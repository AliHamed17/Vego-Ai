#!/usr/bin/env python3
"""Build an offline VEGO-AI results dashboard from existing result files.

This module is intentionally read-only with respect to VEGO-AI outputs. It
collects metrics from JSON/JSONL artifacts and writes a static dashboard under a
generated reports directory.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
import sys
import webbrowser
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "1.0.0"
DEFAULT_SETTINGS = ("ucd_ch", "cd_ch", "ucd_pw", "cd_pw")
SETTING_LABELS = {
    "ucd_ch": "Use Case Diagram / Cheers",
    "cd_ch": "Class Diagram / Cheers",
    "ucd_pw": "Use Case Diagram / Parking World",
    "cd_pw": "Class Diagram / Parking World",
}
CLASSIFICATION_ORDER = (
    "Substantial Variability",
    "Occasional Variability",
    "Undetermined",
)
ADVICE_STRENGTH_ORDER = ("strong", "moderate", "weak", "none", "conflicting")
SENSITIVE_PATH_HINTS = (
    "models",
    "analysis",
    "eval_output",
    "human_review_output",
    "pdf",
    "zip",
)


class DashboardError(RuntimeError):
    """Raised when strict dashboard generation cannot continue."""


@dataclass
class HealthLog:
    """Collects source and parsing health without failing normal generation."""

    strict: bool = False
    files_found: list[str] = field(default_factory=list)
    files_missing: list[dict[str, Any]] = field(default_factory=list)
    parse_errors: list[dict[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def found(self, path: Path) -> None:
        item = _display_path(path)
        if item not in self.files_found:
            self.files_found.append(item)

    def missing(self, logical_name: str, candidates: Iterable[Path]) -> None:
        self.files_missing.append(
            {
                "logical_name": logical_name,
                "candidates": [_display_path(path) for path in candidates],
            }
        )

    def parse_error(self, path: Path, message: str) -> None:
        item = {"path": _display_path(path), "error": message}
        self.parse_errors.append(item)
        if self.strict:
            raise DashboardError(f"Could not parse {path}: {message}") from None

    def warn(self, message: str) -> None:
        self.warnings.append(message)
        if self.strict:
            raise DashboardError(message)

    def as_dict(self) -> dict[str, Any]:
        return {
            "strict": self.strict,
            "files_found": sorted(self.files_found),
            "files_missing": self.files_missing,
            "parse_errors": self.parse_errors,
            "warnings": self.warnings,
            "status": "ok" if not self.parse_errors and not self.warnings else "attention_needed",
        }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a static VEGO-AI results dashboard from existing JSON/JSONL outputs.",
    )
    parser.add_argument("--root", default="VEGO-AI", help="VEGO-AI project root.")
    parser.add_argument(
        "--out",
        default="VEGO-AI/reports/results_dashboard",
        help="Directory for generated dashboard files.",
    )
    parser.add_argument(
        "--settings",
        nargs="+",
        default=list(DEFAULT_SETTINGS),
        help="Setting IDs to include, for example: ucd_ch cd_ch ucd_pw cd_pw.",
    )
    parser.add_argument("--eval-dir", help="Directory containing baseline eval outputs.")
    parser.add_argument("--eval-runs-dir", help="Directory containing repeated eval run outputs.")
    parser.add_argument("--output-runs-dir", help="Directory containing framework output runs.")
    parser.add_argument("--human-dir", help="Directory containing human-review outputs.")
    parser.add_argument("--open", action="store_true", help="Open the generated index.html.")
    parser.add_argument("--strict", action="store_true", help="Fail on missing or invalid inputs.")
    parser.add_argument("--json-only", action="store_true", help="Write metrics_snapshot.json only.")
    return parser.parse_args(argv)


def build_dashboard(
    *,
    root: str | Path,
    out_dir: str | Path,
    settings: Iterable[str] = DEFAULT_SETTINGS,
    eval_dir: str | Path | None = None,
    eval_runs_dir: str | Path | None = None,
    output_runs_dir: str | Path | None = None,
    human_dir: str | Path | None = None,
    strict: bool = False,
    json_only: bool = False,
) -> dict[str, Any]:
    """Build the dashboard files and return the metrics snapshot."""

    root_path = Path(root).resolve()
    out_path = Path(out_dir).resolve()
    health = HealthLog(strict=strict)
    requested_settings = list(settings)

    source_dirs = {
        "eval_dir": _resolve_dir(eval_dir, root_path / "eval_output"),
        "eval_runs_dir": _resolve_dir(eval_runs_dir, root_path / "eval_runs"),
        "output_runs_dir": _resolve_dir(output_runs_dir, root_path / "output_runs"),
        "human_dir": _resolve_dir(human_dir, root_path / "human_review_output"),
    }

    before_eval_mtimes = _collect_file_mtimes(source_dirs["eval_dir"])
    before_eval_run_mtimes = _collect_file_mtimes(source_dirs["eval_runs_dir"])
    before_output_run_mtimes = _collect_file_mtimes(source_dirs["output_runs_dir"])

    setting_summaries = {}
    for setting_id in requested_settings:
        setting_summaries[setting_id] = _load_setting(setting_id, source_dirs, health)

    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": _display_path(root_path),
        "inputs": {name: _display_path(path) for name, path in source_dirs.items()},
        "settings_requested": requested_settings,
        "settings": setting_summaries,
        "overview": _build_overview(setting_summaries),
        "health": health.as_dict(),
        "reproducibility": _build_reproducibility(
            root_path,
            before_eval_mtimes,
            before_eval_run_mtimes,
            before_output_run_mtimes,
            source_dirs,
        ),
    }

    out_path.mkdir(parents=True, exist_ok=True)
    snapshot_path = out_path / "metrics_snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")

    if not json_only:
        index_html = render_index(snapshot)
        (out_path / "index.html").write_text(index_html, encoding="utf-8")
        _write_setting_pages(out_path / "settings", snapshot)

    return snapshot


def _resolve_dir(configured: str | Path | None, default: Path) -> Path:
    return Path(configured).resolve() if configured else default.resolve()


def _load_setting(setting_id: str, source_dirs: dict[str, Path], health: HealthLog) -> dict[str, Any]:
    source_roots = {
        "eval_output": source_dirs["eval_dir"] / setting_id,
        "eval_runs": source_dirs["eval_runs_dir"] / setting_id,
        "output_runs": source_dirs["output_runs_dir"] / setting_id,
        "human_review": source_dirs["human_dir"] / setting_id,
    }

    agent_c = _load_agent_c(setting_id, source_roots, health)
    variability = _load_variability(setting_id, source_roots, health)
    human = _load_human_layers(setting_id, source_roots, health)

    return {
        "setting_id": setting_id,
        "label": SETTING_LABELS.get(setting_id, setting_id),
        "sources": {
            name: {"path": _display_path(path), "exists": path.exists()}
            for name, path in source_roots.items()
        },
        "model_performance": agent_c,
        "variability": variability,
        "human_review_queue": human["human_review_queue"],
        "human_feedback": human["human_feedback"],
        "human_judgment_memory": human["human_judgment_memory"],
        "memory_advisory": human["memory_advisory"],
    }


def _load_agent_c(setting_id: str, source_roots: dict[str, Path], health: HealthLog) -> dict[str, Any]:
    eval_candidates = _setting_dirs(source_roots, "eval_output", "eval_runs")
    scores_path = _find_first(
        f"{setting_id}: Agent C all scores",
        [path / "agentC_all_scores.json" for path in eval_candidates],
        health,
    )
    scores_doc = _read_json(scores_path, health) if scores_path else {}
    ranking = _as_list(_get(scores_doc, "ranking", default=[]))
    scores = [_safe_float(_first(row, "score_pct", "score", "overall_score", "total_score")) for row in ranking]
    scores = [score for score in scores if score is not None]

    case_files = _glob_first_existing(eval_candidates, "agentC_case_*.json", health, f"{setting_id}: Agent C case files")
    status_counts: Counter[str] = Counter()
    for case_path in case_files:
        case_doc = _read_json(case_path, health)
        status_counts.update(_count_compliance_statuses(case_doc))

    top_cases = []
    for row in ranking[:5]:
        top_cases.append(
            {
                "case_id": _stringify(_first(row, "case_id", "id", default="")),
                "rank": _get(row, "rank", default=None),
                "score_pct": _safe_float(_first(row, "score_pct", "score", "overall_score")),
                "assessment": _stringify(_first(row, "overall_assessment", "assessment", default="")),
            }
        )

    return {
        "case_count": len(ranking) or _case_count_from_paths(case_files),
        "scored_case_count": len(scores),
        "score_min": _round_or_none(min(scores) if scores else None),
        "score_max": _round_or_none(max(scores) if scores else None),
        "score_mean": _round_or_none(statistics.mean(scores) if scores else None),
        "score_median": _round_or_none(statistics.median(scores) if scores else None),
        "score_stdev": _round_or_none(statistics.pstdev(scores) if len(scores) > 1 else 0 if scores else None),
        "top_cases": top_cases,
        "compliance_status_counts": dict(sorted(status_counts.items())),
        "source_files": [_display_path(path) for path in ([scores_path] if scores_path else []) + case_files],
    }


def _load_variability(setting_id: str, source_roots: dict[str, Path], health: HealthLog) -> dict[str, Any]:
    eval_and_output = _setting_dirs(source_roots, "eval_output", "eval_runs", "output_runs")
    classes_path = _find_first(
        f"{setting_id}: Agent D variability classes",
        _agent_d_candidates(eval_and_output, "agentD_variability_classes", setting_id)
        + [path / "variability_classifications.json" for path in eval_and_output],
        health,
        fallback_glob="*variability*class*.json",
    )
    patterns_path = _find_first(
        f"{setting_id}: Agent D deviation patterns",
        _agent_d_candidates(eval_and_output, "agentD_deviation_patterns", setting_id)
        + [path / "deviation_patterns.json" for path in eval_and_output],
        health,
        fallback_glob="*deviation*pattern*.json",
    )
    classes_doc = _read_json(classes_path, health) if classes_path else {}
    patterns_doc = _read_json(patterns_path, health) if patterns_path else {}

    classifications = _extract_classifications(classes_doc)
    classification_counts = Counter(_stringify(_get(item, "classification", default="Unknown")) for item in classifications)

    guideline_patterns = _as_list(_get(patterns_doc, "recurring_guideline_patterns", default=[]))
    fragment_patterns = _as_list(_get(patterns_doc, "recurring_fragment_patterns", default=[]))
    all_patterns = guideline_patterns + fragment_patterns
    top_patterns = sorted(
        (_pattern_summary(pattern) for pattern in all_patterns),
        key=lambda row: row["strength_value"] or 0,
        reverse=True,
    )[:8]

    return {
        "classification_count": len(classifications),
        "classification_counts": _ordered_counts(classification_counts, CLASSIFICATION_ORDER),
        "pattern_count": len(all_patterns),
        "guideline_pattern_count": len(guideline_patterns),
        "fragment_pattern_count": len(fragment_patterns),
        "top_patterns": top_patterns,
        "source_files": [_display_path(path) for path in (classes_path, patterns_path) if path],
    }


def _load_human_layers(setting_id: str, source_roots: dict[str, Path], health: HealthLog) -> dict[str, Any]:
    human_dirs = _setting_dirs(source_roots, "human_review", "eval_output", "eval_runs", "output_runs")

    queue_items = _read_jsonl_first(
        setting_id,
        "human_review_queue.jsonl",
        human_dirs,
        health,
        "Human Review Queue",
    )
    resolved_items = _read_jsonl_first(
        setting_id,
        "human_review_queue_resolved.jsonl",
        human_dirs,
        health,
        "resolved Human Feedback",
    )
    memory_items = _read_jsonl_first(
        setting_id,
        "human_judgment_memory.jsonl",
        human_dirs,
        health,
        "Human Judgment Memory",
    )
    advice_doc = _read_json_first(
        setting_id,
        ["memory_advice.json", "*memory_advice.json"],
        human_dirs,
        health,
        "Memory Advisory",
    )
    advice_items = _as_list(_get(advice_doc, "advice", default=advice_doc if isinstance(advice_doc, list) else []))

    queue_status_counts = Counter(_stringify(_get(item, "status", default="unknown")) for item in queue_items)
    queue_trigger_counts: Counter[str] = Counter()
    queue_guideline_counts: Counter[str] = Counter()
    strengths = []
    for item in queue_items:
        queue_trigger_counts.update(_as_string_list(_get(item, "trigger_reasons", default=[])))
        guideline = _get(item, "related_guideline_id")
        if guideline:
            queue_guideline_counts[_stringify(guideline)] += 1
        strength = _strength_value(_get(item, "pattern_strength"))
        if strength is not None:
            strengths.append(strength)

    feedback_decisions: Counter[str] = Counter()
    reusable_count = 0
    guideline_update_count = 0
    for item in resolved_items:
        feedback = _get(item, "human_feedback", default={}) or {}
        decision = _get(feedback, "human_decision", "decision_type")
        if decision:
            feedback_decisions[_stringify(decision)] += 1
        if bool(_get(feedback, "reusable", default=False)):
            reusable_count += 1
        if _get(feedback, "guideline_update") is not None:
            guideline_update_count += 1

    memory_decisions: Counter[str] = Counter()
    memory_conflicts: Counter[str] = Counter()
    memory_guidelines: Counter[str] = Counter()
    active_count = 0
    memory_reusable_count = 0
    for item in memory_items:
        decision = _first(item, "decision_type", default=_get(item, "human_decision", "decision_type"))
        if decision:
            memory_decisions[_stringify(decision)] += 1
        memory_conflicts[_stringify(_get(item, "conflict_status", default="unknown"))] += 1
        guideline = _get(item, "related_guideline_id")
        if guideline:
            memory_guidelines[_stringify(guideline)] += 1
        if _stringify(_get(item, "status", default="")).lower() == "active":
            active_count += 1
        if bool(_get(item, "reuse_scope", "applies_to_future_models", default=False)):
            memory_reusable_count += 1

    strength_counts = Counter(_stringify(_get(item, "advice_strength", default="unknown")) for item in advice_items)
    changed_count = sum(1 for item in advice_items if bool(_get(item, "ai_classification_changed", default=False)))
    matched_count = sum(1 for item in advice_items if _as_list(_get(item, "memory_matches", default=[])))
    conflicting_count = sum(1 for item in advice_items if bool(_get(item, "has_conflicting_memory", default=False)))
    mode_counts = Counter(_stringify(_get(item, "advice_mode", default="unknown")) for item in advice_items)

    return {
        "human_review_queue": {
            "queue_count": len(queue_items),
            "pending_count": sum(1 for item in queue_items if _stringify(_get(item, "status", default="")).lower() == "pending"),
            "resolved_count": sum(1 for item in queue_items if _stringify(_get(item, "status", default="")).lower() == "resolved"),
            "status_counts": dict(sorted(queue_status_counts.items())),
            "trigger_counts": dict(sorted(queue_trigger_counts.items())),
            "guideline_counts": dict(queue_guideline_counts.most_common()),
            "average_pattern_strength": _round_or_none(statistics.mean(strengths) if strengths else None),
        },
        "human_feedback": {
            "resolved_feedback_count": len(resolved_items),
            "decision_counts": dict(feedback_decisions.most_common()),
            "reusable_count": reusable_count,
            "guideline_update_count": guideline_update_count,
        },
        "human_judgment_memory": {
            "memory_count": len(memory_items),
            "active_count": active_count,
            "decision_counts": dict(memory_decisions.most_common()),
            "conflict_status_counts": dict(memory_conflicts.most_common()),
            "guideline_counts": dict(memory_guidelines.most_common()),
            "reusable_count": memory_reusable_count,
        },
        "memory_advisory": {
            "advice_count": len(advice_items),
            "strength_counts": _ordered_counts(strength_counts, ADVICE_STRENGTH_ORDER),
            "matched_advice_count": matched_count,
            "conflicting_advice_count": conflicting_count,
            "ai_classification_changed_count": changed_count,
            "mode_counts": dict(mode_counts.most_common()),
            "advisory_only_boundary_ok": changed_count == 0,
        },
    }


def _build_overview(settings: dict[str, dict[str, Any]]) -> dict[str, Any]:
    score_means = [
        _get(summary, "model_performance", "score_mean")
        for summary in settings.values()
        if _get(summary, "model_performance", "score_mean") is not None
    ]
    return {
        "settings_count": len(settings),
        "case_count": sum(_get(summary, "model_performance", "case_count", default=0) or 0 for summary in settings.values()),
        "average_score_mean": _round_or_none(statistics.mean(score_means) if score_means else None),
        "variability_classification_count": sum(
            _get(summary, "variability", "classification_count", default=0) or 0 for summary in settings.values()
        ),
        "variability_pattern_count": sum(
            _get(summary, "variability", "pattern_count", default=0) or 0 for summary in settings.values()
        ),
        "human_review_queue_count": sum(
            _get(summary, "human_review_queue", "queue_count", default=0) or 0 for summary in settings.values()
        ),
        "resolved_feedback_count": sum(
            _get(summary, "human_feedback", "resolved_feedback_count", default=0) or 0 for summary in settings.values()
        ),
        "judgment_memory_count": sum(
            _get(summary, "human_judgment_memory", "memory_count", default=0) or 0 for summary in settings.values()
        ),
        "memory_advice_count": sum(
            _get(summary, "memory_advisory", "advice_count", default=0) or 0 for summary in settings.values()
        ),
        "ai_classification_changed_count": sum(
            _get(summary, "memory_advisory", "ai_classification_changed_count", default=0) or 0
            for summary in settings.values()
        ),
    }


def _build_reproducibility(
    root: Path,
    before_eval_mtimes: dict[str, float],
    before_eval_run_mtimes: dict[str, float],
    before_output_run_mtimes: dict[str, float],
    source_dirs: dict[str, Path],
) -> dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "git_commit": _git_value(root.parent, ["rev-parse", "--short", "HEAD"]),
        "git_branch": _git_value(root.parent, ["branch", "--show-current"]),
        "baseline_eval_outputs_modified": before_eval_mtimes != _collect_file_mtimes(source_dirs["eval_dir"]),
        "eval_runs_modified": before_eval_run_mtimes != _collect_file_mtimes(source_dirs["eval_runs_dir"]),
        "output_runs_modified": before_output_run_mtimes != _collect_file_mtimes(source_dirs["output_runs_dir"]),
        "offline_static_generation": True,
        "ai_behavior_changed_by_dashboard": False,
    }


def render_index(snapshot: dict[str, Any]) -> str:
    body = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "<head>",
        "<meta charset=\"utf-8\">",
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        "<title>VEGO-AI Results Dashboard</title>",
        _style_block(),
        "</head>",
        "<body>",
        "<main>",
        "<header class=\"hero\">",
        "<p class=\"eyebrow\">Offline research metrics</p>",
        "<h1>VEGO-AI Results Dashboard</h1>",
        f"<p>Generated {escape(snapshot['generated_at'])}. Static HTML and JSON only; no LLM calls, API calls, or classification changes.</p>",
        "</header>",
        _render_overview(snapshot),
        _render_setting_comparison(snapshot),
        _render_model_performance(snapshot),
        _render_variability_patterns(snapshot),
        _render_human_review_queue(snapshot),
        _render_human_feedback(snapshot),
        _render_human_judgment_memory(snapshot),
        _render_memory_advisory(snapshot),
        _render_health(snapshot),
        "</main>",
        "</body>",
        "</html>",
    ]
    return "\n".join(body)


def render_setting_page(snapshot: dict[str, Any], setting_id: str, setting: dict[str, Any]) -> str:
    scoped_snapshot = dict(snapshot)
    scoped_snapshot["settings"] = {setting_id: setting}
    scoped_snapshot["overview"] = _build_overview(scoped_snapshot["settings"])
    return render_index(scoped_snapshot).replace(
        "<h1>VEGO-AI Results Dashboard</h1>",
        f"<h1>{escape(setting['label'])}</h1>",
    )


def _write_setting_pages(settings_dir: Path, snapshot: dict[str, Any]) -> None:
    settings_dir.mkdir(parents=True, exist_ok=True)
    for setting_id, setting in snapshot["settings"].items():
        (settings_dir / f"{setting_id}.html").write_text(
            render_setting_page(snapshot, setting_id, setting),
            encoding="utf-8",
        )


def _render_overview(snapshot: dict[str, Any]) -> str:
    overview = snapshot["overview"]
    cards = [
        ("Settings", overview["settings_count"]),
        ("Cases", overview["case_count"]),
        ("Avg. score", _fmt_percent(overview["average_score_mean"])),
        ("Patterns", overview["variability_pattern_count"]),
        ("Review items", overview["human_review_queue_count"]),
        ("Reusable memories", overview["judgment_memory_count"]),
        ("M4A changed AI labels", overview["ai_classification_changed_count"]),
    ]
    return "<section><h2>Overview KPI Cards</h2><div class=\"kpis\">" + "".join(
        f"<article class=\"kpi\"><span>{escape(label)}</span><strong>{escape(str(value))}</strong></article>"
        for label, value in cards
    ) + "</div></section>"


def _render_setting_comparison(snapshot: dict[str, Any]) -> str:
    rows = []
    for setting_id, setting in snapshot["settings"].items():
        rows.append(
            [
                _setting_link(setting_id, setting),
                _get(setting, "model_performance", "case_count", default=0),
                _fmt_percent(_get(setting, "model_performance", "score_mean")),
                _get(setting, "variability", "pattern_count", default=0),
                _get(setting, "human_review_queue", "queue_count", default=0),
                _get(setting, "human_judgment_memory", "memory_count", default=0),
                _get(setting, "memory_advisory", "advice_count", default=0),
            ]
        )
    return "<section><h2>Setting Comparison</h2>" + _table(
        ["Setting", "Cases", "Mean score", "Patterns", "Review queue", "Memories", "Advice"],
        rows,
    ) + "</section>"


def _render_model_performance(snapshot: dict[str, Any]) -> str:
    parts = ["<section><h2>Model Performance</h2>"]
    for setting_id, setting in snapshot["settings"].items():
        perf = setting["model_performance"]
        parts.append(f"<article><h3>{escape(setting['label'])}</h3>")
        parts.append(
            _table(
                ["Metric", "Value"],
                [
                    ["Case count", perf["case_count"]],
                    ["Score range", f"{_fmt_percent(perf['score_min'])} to {_fmt_percent(perf['score_max'])}"],
                    ["Mean / median", f"{_fmt_percent(perf['score_mean'])} / {_fmt_percent(perf['score_median'])}"],
                    ["Std. dev.", _fmt_percent(perf["score_stdev"])],
                ],
            )
        )
        parts.append(_counts_block("Compliance status counts", perf["compliance_status_counts"]))
        if perf["top_cases"]:
            rows = [
                [case["rank"], case["case_id"], _fmt_percent(case["score_pct"]), case["assessment"][:120]]
                for case in perf["top_cases"]
            ]
            parts.append(_table(["Rank", "Case", "Score", "Assessment"], rows))
        parts.append("</article>")
    parts.append("</section>")
    return "\n".join(parts)


def _render_variability_patterns(snapshot: dict[str, Any]) -> str:
    parts = ["<section><h2>Variability Patterns</h2>"]
    for setting_id, setting in snapshot["settings"].items():
        variability = setting["variability"]
        parts.append(f"<article><h3>{escape(setting['label'])}</h3>")
        parts.append(_counts_block("Classification counts", variability["classification_counts"]))
        rows = [
            [
                pattern["pattern_id"],
                pattern["kind"],
                pattern["guideline_id"] or "",
                pattern["strength_display"] or "",
                pattern["affected_case_count"],
                pattern["description"][:140],
            ]
            for pattern in variability["top_patterns"]
        ]
        parts.append(_table(["Pattern", "Kind", "Guideline", "Strength", "Cases", "Description"], rows))
        parts.append("</article>")
    parts.append("</section>")
    return "\n".join(parts)


def _render_human_review_queue(snapshot: dict[str, Any]) -> str:
    rows = []
    for setting_id, setting in snapshot["settings"].items():
        queue = setting["human_review_queue"]
        rows.append(
            [
                _setting_link(setting_id, setting),
                queue["queue_count"],
                queue["pending_count"],
                queue["resolved_count"],
                _fmt_percent(queue["average_pattern_strength"], scale=100),
                ", ".join(f"{k}: {v}" for k, v in queue["trigger_counts"].items()),
            ]
        )
    return "<section><h2>Human Review Queue</h2>" + _table(
        ["Setting", "Items", "Pending", "Resolved", "Avg. pattern strength", "Triggers"],
        rows,
    ) + "</section>"


def _render_human_feedback(snapshot: dict[str, Any]) -> str:
    parts = ["<section><h2>Human Feedback</h2>"]
    for setting_id, setting in snapshot["settings"].items():
        feedback = setting["human_feedback"]
        parts.append(f"<article><h3>{escape(setting['label'])}</h3>")
        parts.append(
            _table(
                ["Metric", "Value"],
                [
                    ["Resolved feedback", feedback["resolved_feedback_count"]],
                    ["Reusable feedback", feedback["reusable_count"]],
                    ["Guideline updates proposed", feedback["guideline_update_count"]],
                ],
            )
        )
        parts.append(_counts_block("Human decision counts", feedback["decision_counts"]))
        parts.append("</article>")
    parts.append("</section>")
    return "\n".join(parts)


def _render_human_judgment_memory(snapshot: dict[str, Any]) -> str:
    parts = ["<section><h2>Human Judgment Memory</h2>"]
    for setting_id, setting in snapshot["settings"].items():
        memory = setting["human_judgment_memory"]
        parts.append(f"<article><h3>{escape(setting['label'])}</h3>")
        parts.append(
            _table(
                ["Metric", "Value"],
                [
                    ["Memory entries", memory["memory_count"]],
                    ["Active entries", memory["active_count"]],
                    ["Reusable for future models", memory["reusable_count"]],
                ],
            )
        )
        parts.append(_counts_block("Decision counts", memory["decision_counts"]))
        parts.append(_counts_block("Conflict status counts", memory["conflict_status_counts"]))
        parts.append("</article>")
    parts.append("</section>")
    return "\n".join(parts)


def _render_memory_advisory(snapshot: dict[str, Any]) -> str:
    rows = []
    for setting_id, setting in snapshot["settings"].items():
        advice = setting["memory_advisory"]
        rows.append(
            [
                _setting_link(setting_id, setting),
                advice["advice_count"],
                advice["matched_advice_count"],
                advice["conflicting_advice_count"],
                advice["ai_classification_changed_count"],
                "yes" if advice["advisory_only_boundary_ok"] else "no",
                ", ".join(f"{k}: {v}" for k, v in advice["strength_counts"].items()),
            ]
        )
    return "<section><h2>Memory Advisory</h2><p class=\"note\">M4A is advisory-only. This dashboard counts advice and verifies that it did not change AI classifications.</p>" + _table(
        ["Setting", "Advice", "Matched", "Conflicting", "AI label changes", "Boundary OK", "Strengths"],
        rows,
    ) + "</section>"


def _render_health(snapshot: dict[str, Any]) -> str:
    health = snapshot["health"]
    reproducibility = snapshot["reproducibility"]
    rows = [
        ["Health status", health["status"]],
        ["Files found", len(health["files_found"])],
        ["Missing source groups", len(health["files_missing"])],
        ["Parse errors", len(health["parse_errors"])],
        ["Git commit", reproducibility["git_commit"] or "unknown"],
        ["Git branch", reproducibility["git_branch"] or "unknown"],
        ["Baseline eval outputs modified", reproducibility["baseline_eval_outputs_modified"]],
        ["AI behavior changed by dashboard", reproducibility["ai_behavior_changed_by_dashboard"]],
    ]
    parts = ["<section><h2>Health and Reproducibility</h2>", _table(["Check", "Value"], rows)]
    if health["parse_errors"]:
        parts.append("<h3>Parse Errors</h3>")
        parts.append(_table(["Path", "Error"], [[item["path"], item["error"]] for item in health["parse_errors"]]))
    if health["files_missing"]:
        parts.append("<h3>Missing Optional Inputs</h3>")
        parts.append(
            _table(
                ["Logical source", "Candidate count"],
                [[item["logical_name"], len(item["candidates"])] for item in health["files_missing"]],
            )
        )
    parts.append("</section>")
    return "\n".join(parts)


def _style_block() -> str:
    return """<style>
:root { color-scheme: light; --ink: #17202a; --muted: #566573; --line: #d6dbdf; --bg: #f7f9fb; --accent: #0f766e; --soft: #e8f5f3; }
* { box-sizing: border-box; }
body { margin: 0; font-family: Arial, Helvetica, sans-serif; background: var(--bg); color: var(--ink); line-height: 1.5; }
main { max-width: 1180px; margin: 0 auto; padding: 28px; }
.hero { padding: 28px 0 18px; border-bottom: 1px solid var(--line); }
.eyebrow { margin: 0 0 8px; color: var(--accent); font-weight: 700; text-transform: uppercase; font-size: 12px; letter-spacing: 0; }
h1 { margin: 0 0 10px; font-size: 34px; }
h2 { margin: 34px 0 14px; font-size: 24px; }
h3 { margin: 24px 0 10px; font-size: 18px; }
section { padding: 10px 0; }
article { border-top: 1px solid var(--line); padding-top: 10px; }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }
.kpi { background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 14px; min-height: 86px; }
.kpi span { display: block; color: var(--muted); font-size: 13px; }
.kpi strong { display: block; margin-top: 8px; font-size: 26px; }
table { width: 100%; border-collapse: collapse; margin: 10px 0 18px; background: #fff; border: 1px solid var(--line); }
th, td { text-align: left; padding: 9px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { background: var(--soft); font-size: 13px; }
td { font-size: 13px; }
.counts { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 8px; margin: 8px 0 16px; }
.count { background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 10px; }
.bar { height: 7px; background: var(--soft); border-radius: 999px; overflow: hidden; margin-top: 7px; }
.bar span { display: block; height: 100%; background: var(--accent); }
.note { color: var(--muted); }
a { color: #0b5cad; }
@media (max-width: 720px) { main { padding: 16px; } h1 { font-size: 28px; } table { display: block; overflow-x: auto; } }
</style>"""


def _table(headers: list[Any], rows: list[list[Any]]) -> str:
    if not rows:
        return "<p class=\"note\">No data found for this section.</p>"
    head = "".join(f"<th>{escape(str(header))}</th>" for header in headers)
    body = []
    for row in rows:
        cells = []
        for value in row:
            text = str(value)
            if text.startswith("<a "):
                cells.append(f"<td>{text}</td>")
            else:
                cells.append(f"<td>{escape(text)}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def _counts_block(title: str, counts: dict[str, int]) -> str:
    if not counts:
        return f"<h4>{escape(title)}</h4><p class=\"note\">No counts available.</p>"
    max_count = max(counts.values()) if counts else 1
    items = []
    for label, count in counts.items():
        width = 0 if max_count == 0 else max(4, int((count / max_count) * 100))
        items.append(
            f"<div class=\"count\"><strong>{escape(str(count))}</strong><br>{escape(str(label))}"
            f"<div class=\"bar\"><span style=\"width:{width}%\"></span></div></div>"
        )
    return f"<h4>{escape(title)}</h4><div class=\"counts\">{''.join(items)}</div>"


def _setting_link(setting_id: str, setting: dict[str, Any]) -> str:
    return f"<a href=\"settings/{escape(setting_id)}.html\">{escape(setting['label'])}</a>"


def _setting_dirs(source_roots: dict[str, Path], *names: str) -> list[Path]:
    return [source_roots[name] for name in names if name in source_roots]


def _agent_d_candidates(dirs: list[Path], stem: str, setting_id: str) -> list[Path]:
    names = [
        f"{stem}.json",
        f"{stem}_{setting_id}.json",
        f"{stem}__{setting_id}.json",
    ]
    return [directory / name for directory in dirs for name in names]


def _find_first(
    logical_name: str,
    candidates: list[Path],
    health: HealthLog,
    *,
    fallback_glob: str | None = None,
) -> Path | None:
    for path in candidates:
        if path.exists():
            health.found(path)
            return path
    if fallback_glob:
        for directory in _unique_parent_dirs(candidates):
            if directory.exists():
                matches = sorted(directory.glob(fallback_glob))
                if matches:
                    health.found(matches[0])
                    return matches[0]
    health.missing(logical_name, candidates)
    if health.strict:
        raise DashboardError(f"Missing required source group: {logical_name}")
    return None


def _glob_first_existing(dirs: list[Path], pattern: str, health: HealthLog, logical_name: str) -> list[Path]:
    for directory in dirs:
        if directory.exists():
            matches = sorted(directory.glob(pattern))
            if matches:
                for path in matches:
                    health.found(path)
                return matches
    health.missing(logical_name, [directory / pattern for directory in dirs])
    return []


def _read_json_first(
    setting_id: str,
    names_or_patterns: list[str],
    dirs: list[Path],
    health: HealthLog,
    logical_layer: str,
) -> Any:
    exact_candidates = [directory / name for directory in dirs for name in names_or_patterns if "*" not in name]
    glob_candidates = []
    for pattern in [item for item in names_or_patterns if "*" in item]:
        for directory in dirs:
            if directory.exists():
                glob_candidates.extend(sorted(directory.glob(pattern)))
            else:
                glob_candidates.append(directory / pattern)
    first = _find_first(f"{setting_id}: {logical_layer}", exact_candidates + glob_candidates, health)
    if first:
        return _read_json(first, health)
    return {}


def _read_jsonl_first(
    setting_id: str,
    filename: str,
    dirs: list[Path],
    health: HealthLog,
    logical_layer: str,
) -> list[dict[str, Any]]:
    path = _find_first(
        f"{setting_id}: {logical_layer}",
        [directory / filename for directory in dirs],
        health,
    )
    return _read_jsonl(path, health) if path else []


def _read_json(path: Path, health: HealthLog) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # JSONDecodeError, UnicodeDecodeError, OSError
        health.parse_error(path, str(exc))
        return {}


def _read_jsonl(path: Path, health: HealthLog) -> list[dict[str, Any]]:
    items = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception as exc:
        health.parse_error(path, str(exc))
        return items
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except Exception as exc:
            health.parse_error(path, f"line {line_number}: {exc}")
            continue
        if isinstance(value, dict):
            items.append(value)
        else:
            health.parse_error(path, f"line {line_number}: expected object, got {type(value).__name__}")
    return items


def _extract_classifications(doc: Any) -> list[dict[str, Any]]:
    if isinstance(doc, list):
        return [item for item in doc if isinstance(item, dict)]
    if not isinstance(doc, dict):
        return []
    for key in ("variability_classifications", "classifications", "items", "patterns"):
        value = doc.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _pattern_summary(pattern: dict[str, Any]) -> dict[str, Any]:
    affected_cases = _as_list(_get(pattern, "affected_cases", default=[]))
    strength = _first(pattern, "pattern_strength", "strength")
    kind = "guideline" if _get(pattern, "guideline_id") else "fragment"
    return {
        "pattern_id": _stringify(_get(pattern, "pattern_id", default="")),
        "kind": kind,
        "guideline_id": _stringify(_get(pattern, "guideline_id", default="")),
        "description": _stringify(_first(pattern, "description", "target_fragment", default="")),
        "affected_case_count": len(affected_cases),
        "strength_display": _strength_display(strength),
        "strength_value": _strength_value(strength),
    }


def _count_compliance_statuses(doc: Any) -> Counter[str]:
    counts: Counter[str] = Counter()

    def walk(value: Any, key: str = "") -> None:
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                walk(child_value, child_key)
        elif isinstance(value, list):
            for child in value:
                walk(child, key)
        elif isinstance(value, str) and key in {"compliance_status", "status", "label", "fragment_label"}:
            normalized = _normalize_status(value)
            if normalized:
                counts[normalized] += 1

    walk(doc)
    return counts


def _normalize_status(value: str) -> str | None:
    lowered = value.strip().lower().replace("_", "-")
    if "partially-satisfied" in lowered or "partial" in lowered:
        return "Partially-Satisfied"
    if "not-satisfied" in lowered or "not satisfied" in lowered or "unsatisfied" in lowered:
        return "Not-Satisfied"
    if lowered in {"satisfied", "fully-satisfied", "pass", "passed"}:
        return "Satisfied"
    if lowered in {"alternative", "language mistake", "domain mistake", "missing"}:
        return value.strip()
    return None


def _get(value: Any, *keys: str, default: Any = None) -> Any:
    current = value
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def _first(value: Any, *keys: str, default: Any = None) -> Any:
    if not isinstance(value, dict):
        return default
    for key in keys:
        if key in value:
            return value[key]
    return default


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_string_list(value: Any) -> list[str]:
    return [_stringify(item) for item in _as_list(value)]


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value) if math.isfinite(float(value)) else None
    if isinstance(value, str):
        cleaned = value.strip().replace("%", "")
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _strength_value(value: Any) -> float | None:
    if isinstance(value, dict):
        if value.get("value") is not None:
            return _safe_float(value.get("value"))
        if value.get("percentage") is not None:
            numeric = _safe_float(value.get("percentage"))
            return numeric / 100 if numeric and numeric > 1 else numeric
    numeric = _safe_float(value)
    if numeric is None:
        return None
    return numeric / 100 if numeric > 1 else numeric


def _strength_display(value: Any) -> str | None:
    if isinstance(value, dict):
        if value.get("display"):
            return _stringify(value["display"])
        if value.get("percentage"):
            return _stringify(value["percentage"])
        if value.get("value") is not None:
            return _fmt_percent(_strength_value(value), scale=100)
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return _fmt_percent(_strength_value(value), scale=100)
    return None


def _round_or_none(value: float | int | None) -> float | None:
    return round(float(value), 3) if value is not None else None


def _fmt_percent(value: Any, *, scale: int = 1) -> str:
    numeric = _safe_float(value)
    if numeric is None:
        return "n/a"
    numeric *= scale
    return f"{numeric:.1f}%"


def _case_count_from_paths(paths: list[Path]) -> int:
    return len(paths)


def _ordered_counts(counts: Counter[str], order: Iterable[str]) -> dict[str, int]:
    ordered: dict[str, int] = {}
    for key in order:
        if key in counts:
            ordered[key] = counts[key]
    for key, value in counts.most_common():
        if key not in ordered:
            ordered[key] = value
    return ordered


def _collect_file_mtimes(directory: Path) -> dict[str, float]:
    if not directory.exists():
        return {}
    return {
        _display_path(path): path.stat().st_mtime
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def _git_value(cwd: Path, args: list[str]) -> str | None:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return None
    value = proc.stdout.strip()
    return value or None


def _unique_parent_dirs(paths: list[Path]) -> list[Path]:
    seen = set()
    dirs = []
    for path in paths:
        parent = path.parent
        if parent not in seen:
            seen.add(parent)
            dirs.append(parent)
    return dirs


def _display_path(path: Path) -> str:
    try:
        return path.resolve().as_posix()
    except OSError:
        return path.as_posix()


def _stringify(value: Any) -> str:
    return "" if value is None else str(value)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        build_dashboard(
            root=args.root,
            out_dir=args.out,
            settings=args.settings,
            eval_dir=args.eval_dir,
            eval_runs_dir=args.eval_runs_dir,
            output_runs_dir=args.output_runs_dir,
            human_dir=args.human_dir,
            strict=args.strict,
            json_only=args.json_only,
        )
    except DashboardError as exc:
        print(f"dashboard error: {exc}", file=sys.stderr)
        return 2
    index_path = Path(args.out) / "index.html"
    if args.open and index_path.exists():
        webbrowser.open(index_path.resolve().as_uri())
    print(f"dashboard written to {Path(args.out).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
