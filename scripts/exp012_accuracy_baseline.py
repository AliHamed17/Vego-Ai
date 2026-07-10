"""EXP-012: leakage-safe baseline measurement from validated EXP-005 rows.

This script does not read ad-hoc Human Judgment Memory labels. It consumes the
validated EXP-005 full review export plus its validation summary, requires an
explicit safe-candidate flag, and admits only an explicit leakage allowlist.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from hlayer_harness import (
    ALLOWED_LABELS,
    REPO,
    SAFE_LEAKAGE_ALLOWLIST,
    exp005_dir,
    exp005_gate_sentence,
    experiment_output_dir,
    load_exp005_gate,
    normalize_label,
    read_csv,
    truthy,
    write_experiment_manifest,
    write_json,
)

OUT = experiment_output_dir("exp012")
CANONICAL_EVALUATOR = REPO / "VEGO-AI" / "analysis" / "evaluate_accuracy_improvement.py"
MIN_QUANTITATIVE_LABELS = 20
CLAIM_BASE = "Baseline measurement infrastructure only. It does not establish improvement, generalization, or clinical performance."
REQUIRED_FIELDS = {
    "setting",
    "pattern_id",
    "expert_label",
    "original_agent4_classification",
    "memory_informed_classification",
    "generalization_safe_candidate",
    "evaluation_leakage_status",
}


def gate_band(label_count: int) -> dict[str, Any]:
    if label_count == 0:
        return {
            "band": "blocked_zero_labels",
            "quantitative_reporting": False,
            "status": "NOT YET COMPUTABLE - no validated safe expert labels",
        }
    if label_count < MIN_QUANTITATIVE_LABELS:
        return {
            "band": "pilot_only",
            "quantitative_reporting": False,
            "status": f"PILOT ONLY - {label_count} validated safe labels (<{MIN_QUANTITATIVE_LABELS})",
        }
    return {
        "band": "quantitative_baseline_available",
        "quantitative_reporting": True,
        "status": (
            f"QUANTITATIVE BASELINE AVAILABLE - {label_count} validated safe labels; no improvement claim implied"
        ),
    }


def effective_gold(row: dict[str, str]) -> str:
    adjudicated = normalize_label(row.get("adjudicated_label", ""))
    if adjudicated in ALLOWED_LABELS:
        return adjudicated
    return normalize_label(row.get("expert_label", ""))


def validate_interface_rows(rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("EXP-005 full review export has no rows")
    missing = REQUIRED_FIELDS - set(rows[0])
    if missing:
        raise ValueError(f"EXP-005 full review export is missing fields: {sorted(missing)}")


def partition_validated_rows(
    rows: list[dict[str, str]],
) -> tuple[list[dict], list[dict], dict[str, int]]:
    safe: list[dict] = []
    same_pattern: list[dict] = []
    excluded: Counter[str] = Counter()
    try:
        from exp005_label_review import validation_errors  # type: ignore
    except ImportError as exc:
        raise ValueError(f"Canonical EXP-005 validator cannot be imported: {exc}") from exc

    for source in sorted(rows, key=lambda row: (row.get("setting", ""), row.get("pattern_id", ""))):
        label = effective_gold(source)
        # Adjudicated labels can supersede an otherwise valid expert label. The
        # canonical row validation still guards rationale/reviewer requirements.
        if label not in ALLOWED_LABELS or validation_errors(source):
            excluded["unvalidated_or_unlabeled"] += 1
            continue
        leakage = str(source.get("evaluation_leakage_status") or "").strip()
        explicit_safe = truthy(source.get("generalization_safe_candidate"))
        item = dict(source)
        item["expert_label"] = label
        if leakage == "same_pattern_memory_used":
            same_pattern.append(item)
            excluded["same_pattern"] += 1
            continue
        if not explicit_safe:
            excluded["safe_candidate_false_or_blank"] += 1
            continue
        if leakage not in SAFE_LEAKAGE_ALLOWLIST:
            excluded[f"leakage_not_allowlisted:{leakage or 'blank'}"] += 1
            continue
        safe.append(item)
    return safe, same_pattern, dict(sorted(excluded.items()))


def metric_pack(rows: list[dict[str, str]]) -> dict[str, Any]:
    if not rows:
        return {
            "rows": 0,
            "original_accuracy": None,
            "memory_informed_accuracy": None,
            "original_correct": 0,
            "memory_informed_correct": 0,
        }
    original_correct = sum(
        str(row.get("original_agent4_classification", ""))
        == normalize_label(row.get("expert_label", ""))
        for row in rows
    )
    memory_correct = sum(
        str(row.get("memory_informed_classification", ""))
        == normalize_label(row.get("expert_label", ""))
        for row in rows
    )
    return {
        "rows": len(rows),
        "original_accuracy": round(original_correct / len(rows), 4),
        "memory_informed_accuracy": round(memory_correct / len(rows), 4),
        "original_correct": original_correct,
        "memory_informed_correct": memory_correct,
    }


def canonical_cross_check(rows: list[dict[str, str]], local: dict[str, Any]) -> dict[str, Any]:
    if not CANONICAL_EVALUATOR.is_file():
        raise ValueError(f"Canonical EXP-003 evaluator missing: {CANONICAL_EVALUATOR}")
    spec = importlib.util.spec_from_file_location("vego_exp003_canonical", CANONICAL_EVALUATOR)
    if spec is None or spec.loader is None:
        raise ValueError("Could not load canonical EXP-003 evaluator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    canonical = module.metric_dict(rows)["generalization_safe"]

    def equal(left: Any, right: Any) -> bool:
        if left is None or right is None:
            return left is right
        return math.isclose(float(left), float(right), rel_tol=0, abs_tol=0.00005)

    checks = {
        "rows": canonical["rows"] == local["rows"],
        "original_accuracy": equal(canonical["original_accuracy"], local["original_accuracy"]),
        "memory_informed_accuracy": equal(
            canonical["memory_informed_accuracy"], local["memory_informed_accuracy"]
        ),
    }
    if not all(checks.values()):
        raise ValueError(
            f"EXP-012 metric drift from canonical EXP-003 evaluator: checks={checks}, canonical={canonical}, local={local}"
        )
    return {"status": "PASS", "checks": checks, "canonical_metrics": canonical}


def main() -> int:
    try:
        gate = load_exp005_gate()
        gate_dir = exp005_dir()
        full_path = gate_dir / "exp005_label_review_full.csv"
        validation_path = gate_dir / "label_validation_summary.json"
        rows = read_csv(full_path)
        validate_interface_rows(rows)
        safe, same_pattern, excluded = partition_validated_rows(rows)
        safe_metrics = metric_pack(safe)
        cross_check = canonical_cross_check(safe, safe_metrics)
    except (ValueError, OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"EXP-012 input/validation error: {exc}", file=sys.stderr)
        return 2

    claim = f"{CLAIM_BASE} {exp005_gate_sentence(gate)}"
    safe_metrics.update(gate_band(len(safe)))
    same_pattern_metrics = metric_pack(same_pattern)
    same_pattern_metrics["status"] = "EXCLUDED FROM GENERALIZATION-SAFE BASELINE"
    summary = {
        "experiment": "EXP-012 validated EXP-005 baseline interface",
        "claim_scope": claim,
        "min_labels_for_quantitative_reporting": MIN_QUANTITATIVE_LABELS,
        "safe_leakage_allowlist": sorted(SAFE_LEAKAGE_ALLOWLIST),
        "validated_exp005_gate": gate,
        "generalization_safe_baseline": safe_metrics,
        "same_pattern_pilot_baseline": same_pattern_metrics,
        "excluded_row_counts": excluded,
        "canonical_exp003_cross_check": cross_check,
        "rows_detail": [
            {
                "setting": row.get("setting"),
                "pattern_id": row.get("pattern_id"),
                "expert_label": normalize_label(row.get("expert_label", "")),
                "original_classification": row.get("original_agent4_classification"),
                "memory_informed_classification": row.get("memory_informed_classification"),
                "evaluation_leakage_status": row.get("evaluation_leakage_status"),
                "generalization_safe_candidate": row.get("generalization_safe_candidate"),
            }
            for row in safe
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    summary_path = OUT / "summary.json"
    write_json(summary_path, summary)
    lines = [
        "# EXP-012 Validated EXP-005 Baseline Interface",
        "",
        f"Claim scope: {claim}",
        "",
        f"Accepted leakage values: {', '.join(sorted(SAFE_LEAKAGE_ALLOWLIST))}.",
        "Blank, unknown, same-setting, and same-pattern leakage states are excluded from the safe baseline.",
        "",
        "## Generalization-safe baseline",
        "",
        f"- Validated rows: {safe_metrics['rows']}",
        f"- Status: {safe_metrics['status']}",
        f"- Original baseline: {safe_metrics['original_accuracy']}",
        f"- Memory-informed comparison: {safe_metrics['memory_informed_accuracy']}",
        f"- Canonical EXP-003 cross-check: {cross_check['status']}",
        "",
        "## Exclusions",
        "",
    ]
    lines.extend(f"- {reason}: {count}" for reason, count in excluded.items())
    lines.extend(
        [
            "",
            "Same-pattern rows remain isolated as mechanism-only material and never enter the safe baseline.",
        ]
    )
    summary_md = OUT / "summary.md"
    summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_experiment_manifest(
        OUT,
        experiment_id="EXP-012",
        experiment_version="2.0",
        config_version="validated-exp005-interface-1.0",
        claim_scope=claim,
        script_path=Path(__file__),
        inputs=[full_path, validation_path, CANONICAL_EVALUATOR],
        outputs=[summary_path, summary_md],
        config={
            "minimum_quantitative_labels": MIN_QUANTITATIVE_LABELS,
            "safe_leakage_allowlist": sorted(SAFE_LEAKAGE_ALLOWLIST),
            "requires_explicit_safe_candidate": True,
        },
        metric_schema={
            "generalization_safe_baseline": "validated labeled rows with explicit safe flag and allowlisted leakage",
            "gate_bands": "0 blocked; 1-19 pilot-only; >=20 quantitative baseline available without an improvement claim",
        },
    )
    print(f"EXP-012 done: safe N={len(safe)} band={safe_metrics['band']} -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
