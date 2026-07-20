#!/usr/bin/env python3
"""Build the unified H-layer program overview.

Joins, strictly read-only, the artifacts that already exist into one
machine-readable JSON, one human-readable Markdown page, and one
chart-ready metric-trajectory CSV:

- replay-suite manifest (EXP-006..010, 012) - ``hlayer_suite_manifest.json``
- conformance-suite manifest (EXP-013..018) - ``hlayer_conformance/manifest.json``
- program validation - ``hlayer_program_validation/latest.json``
- validated EXP-005 gate (revalidated through the canonical harness helper)
- supervisor decision snapshot (through the canonical harness helper)
- accepted iteration history - ``hlayer_iterations/iter_*/`` summaries
  (drift-tolerant across the metric-schema versions of iterations 001-013)

The overview NEVER creates evidence: it carries the claim boundary of its
sources and reports gate states verbatim. Outputs land in
``reports/generated/hlayer_program_overview/`` (git-ignored).
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from typing import Any

from hlayer_harness import (
    HarnessError,
    decision_snapshot,
    exp005_gate_sentence,
    experiment_output_dir,
    generated_at,
    load_exp005_gate,
    output_root,
    read_json,
    write_json,
)

OUT = experiment_output_dir("hlayer_program_overview")
CLAIM = (
    "Program status overview only: joins existing offline mechanism/conformance artifacts. "
    "It creates no evidence and authorizes no accuracy, generalization, or clinical claim."
)

# Metric names drifted across iteration schemas; map every known alias to one
# canonical trajectory column. Missing values stay blank, never guessed.
TRAJECTORY_METRICS: dict[str, tuple[str, ...]] = {
    "event_load": ("event_load_vs_every_decision", "load_vs_every_decision"),
    "weighted_coverage": ("weighted_severity_coverage",),
    "high_severity_coverage": ("high_severity_coverage",),
    "efficiency": ("efficiency",),
    "bundled_load": ("bundled_load",),
    "bundled_efficiency": ("bundled_efficiency",),
}
TRAJECTORY_MODES = ("every_decision", "threshold_sev1", "threshold_sev2", "threshold_sev3",
                    "first_n_then_auto", "threshold", "silent")


def optional_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = read_json(path)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def iteration_dirs(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(
        (p for p in root.iterdir() if p.is_dir() and re.fullmatch(r"iter_\d{3}", p.name)),
        key=lambda p: p.name,
    )


def mode_rows(exp007_summary: dict[str, Any]) -> list[dict[str, Any]]:
    results = exp007_summary.get("results")
    if isinstance(results, dict):
        rows = results.get("ALL")
        if isinstance(rows, list):
            return [r for r in rows if isinstance(r, dict)]
        for value in results.values():  # oldest schema: no ALL key
            if isinstance(value, list):
                return [r for r in value if isinstance(r, dict)]
    return []


def first_present(row: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    for name in aliases:
        if name in row and row[name] is not None:
            return row[name]
    return None


def trajectory_rows(iterations_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for it_dir in iteration_dirs(iterations_root):
        summary = optional_json(it_dir / "exp007-summary.json")
        if summary is None:
            continue
        manifest = optional_json(it_dir / "iteration_manifest.json") or {}
        for mode_row in mode_rows(summary):
            mode = str(mode_row.get("mode") or "")
            if mode not in TRAJECTORY_MODES:
                continue
            record: dict[str, Any] = {
                "iteration": it_dir.name,
                "verdict": manifest.get("verdict") or "",
                "mode": mode,
            }
            for column, aliases in TRAJECTORY_METRICS.items():
                value = first_present(mode_row, aliases)
                record[column] = value if isinstance(value, (int, float)) else ""
            rows.append(record)
    return rows


def iteration_records(iterations_root: Path) -> list[dict[str, Any]]:
    records = []
    for it_dir in iteration_dirs(iterations_root):
        manifest = optional_json(it_dir / "iteration_manifest.json")
        records.append(
            {
                "iteration": it_dir.name,
                "has_manifest": manifest is not None,
                "iteration_kind": (manifest or {}).get("iteration_kind"),
                "verdict": (manifest or {}).get("verdict"),
                "hypothesis": (manifest or {}).get("hypothesis"),
                "run_id": (manifest or {}).get("run_id"),
            }
        )
    return records


def suite_section(root: Path) -> dict[str, Any]:
    manifest = optional_json(root / "hlayer_suite_manifest.json")
    if manifest is None:
        return {"present": False}
    return {
        "present": True,
        "run_id": manifest.get("run_id"),
        "generated_at": manifest.get("generated_at"),
        "experiments": [e.get("experiment") for e in manifest.get("experiments", [])
                        if isinstance(e, dict)],
        "normalized_sha256": manifest.get("normalized_sha256"),
        "claim_boundary": manifest.get("claim_boundary"),
    }


def conformance_section(root: Path) -> dict[str, Any]:
    manifest = optional_json(root / "hlayer_conformance" / "manifest.json")
    if manifest is None:
        return {"present": False}
    return {
        "present": True,
        "passed": manifest.get("passed"),
        "run_id": manifest.get("run_id"),
        "suite_version": manifest.get("suite_version"),
        "experiments": [e.get("experiment_id") or e.get("experiment")
                        for e in manifest.get("experiments", []) if isinstance(e, dict)],
        "live_shadow_authorized": manifest.get("live_shadow_authorized"),
        "program_mode": manifest.get("decision_snapshot_program_mode"),
    }


def validation_section(root: Path) -> dict[str, Any]:
    latest = optional_json(root / "hlayer_program_validation" / "latest.json")
    if latest is None:
        return {"present": False}
    return {
        "present": True,
        "status": latest.get("status"),
        "checks_passed": latest.get("checks_passed"),
        "failures": latest.get("failures"),
    }


def fmt(value: Any) -> str:
    return "-" if value in (None, "") else str(value)


def build_markdown(overview: dict[str, Any], trajectories: list[dict[str, Any]]) -> str:
    suite = overview["replay_suite"]
    conf = overview["conformance_suite"]
    val = overview["program_validation"]
    gate = overview["exp005_gate"]
    decisions = overview["decision_snapshot"]
    iterations = overview["iterations"]

    lines = [
        "# H-Layer Program Overview",
        "",
        f"Generated: {overview['generated_at']} (regenerate: `python scripts/build_hlayer_program_overview.py`)",
        "",
        f"Claim scope: {CLAIM}",
        "",
        f"**Gate state:** {overview['gate_sentence']}",
        "",
        "## Program At A Glance",
        "",
        "| Area | State |",
        "| --- | --- |",
        f"| Replay suite (EXP-006..010, 012) | {'run ' + fmt(suite.get('run_id')) if suite.get('present') else 'MISSING'} |",
        f"| Conformance suite (EXP-013..018) | {('PASS' if conf.get('passed') else 'FAIL') if conf.get('present') else 'MISSING'} (run {fmt(conf.get('run_id'))}) |",
        f"| Program validation | {fmt(val.get('status')) if val.get('present') else 'MISSING'} ({fmt(val.get('checks_passed'))} checks) |",
        f"| Accepted iterations | {len(iterations)} ({fmt(iterations[-1]['iteration']) if iterations else '-'} latest) |",
        f"| EXP-005 validated safe labels | {fmt(gate.get('counts', {}).get('generalization_safe_valid_label_count'))} |",
        f"| Program mode | {fmt(conf.get('program_mode')) if conf.get('present') else fmt(decisions.get('status'))} |",
        f"| Live shadow authorized | {fmt(conf.get('live_shadow_authorized'))} |",
        "",
        "## Iterations",
        "",
        "| Iteration | Kind | Verdict |",
        "| --- | --- | --- |",
    ]
    for record in iterations:
        lines.append(
            f"| {record['iteration']} | {fmt(record.get('iteration_kind'))} | {fmt(record.get('verdict'))} |"
        )

    lines += [
        "",
        "## Metric Trajectories (threshold_sev2, pooled ALL)",
        "",
        "| Iteration | Event load | Weighted coverage | High-sev coverage | Efficiency | Bundled load | Bundled efficiency |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in trajectories:
        if row["mode"] != "threshold_sev2":
            continue
        lines.append(
            "| {iteration} | {event_load} | {weighted_coverage} | {high_severity_coverage} | "
            "{efficiency} | {bundled_load} | {bundled_efficiency} |".format(
                **{k: fmt(v) for k, v in row.items()}
            )
        )
    lines += [
        "",
        "Full per-mode trajectories: `metric_trajectories.csv` in this directory.",
        "",
        "## Sources",
        "",
        "- `reports/generated/hlayer_suite_manifest.json` (replay suite)",
        "- `reports/generated/hlayer_conformance/manifest.json` (conformance suite)",
        "- `reports/generated/hlayer_program_validation/latest.json` (program validator)",
        "- `reports/generated/hlayer_iterations/iter_*/` (accepted iterations)",
        "- validated EXP-005 gate + supervisor decision snapshot via `hlayer_harness`",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    root = output_root()
    try:
        gate = load_exp005_gate()
        decisions = decision_snapshot()
    except HarnessError as exc:
        print(f"program overview error: {exc}", file=sys.stderr)
        return 2

    iterations_root = root / "hlayer_iterations"
    trajectories = trajectory_rows(iterations_root)
    overview = {
        "schema_version": "1.0",
        "generated_at": generated_at(),
        "claim_scope": CLAIM,
        "gate_sentence": exp005_gate_sentence(gate),
        "replay_suite": suite_section(root),
        "conformance_suite": conformance_section(root),
        "program_validation": validation_section(root),
        "exp005_gate": {"counts": gate.get("counts"), "snapshot_sha256": gate.get("snapshot_sha256")},
        "decision_snapshot": {
            "present": decisions.get("present"),
            "status": decisions.get("status"),
            "offline_only": decisions.get("offline_only"),
        },
        "iterations": iteration_records(iterations_root),
        "trajectory_rows": len(trajectories),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / "program_overview.json", overview)
    columns = ["iteration", "verdict", "mode", *TRAJECTORY_METRICS.keys()]
    with (OUT / "metric_trajectories.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(trajectories)
    (OUT / "program_overview.md").write_text(build_markdown(overview, trajectories), encoding="utf-8")

    print(
        f"program overview: {len(overview['iterations'])} iterations, "
        f"{overview['trajectory_rows']} trajectory rows, "
        f"replay={'ok' if overview['replay_suite'].get('present') else 'missing'}, "
        f"conformance={'PASS' if overview['conformance_suite'].get('passed') else 'see file'} -> {OUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
