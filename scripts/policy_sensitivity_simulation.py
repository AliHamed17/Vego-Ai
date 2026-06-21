#!/usr/bin/env python3
"""Run synthetic policy-sensitivity checks for M4B-1 style variants.

This is not a production classifier and does not modify VEGO-AI outputs. It
uses EXP-003 rows to test whether the evaluation pipeline can detect deltas
under synthetic labels and candidate parallel-comparison policies.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LABELS = {"Substantial Variability", "Occasional Variability", "Undetermined / Needs Review"}
CHANGE_LABELS = {"Substantial Variability", "Occasional Variability"}


def truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def safe_row(row: dict[str, str]) -> bool:
    return truthy(row.get("generalization_safe_candidate", "")) and row.get("evaluation_leakage_status") != "same_pattern_memory_used"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def suggested_label(row: dict[str, str]) -> str:
    match = re.search(
        r"classified .*? as (Substantial Variability|Occasional Variability|Undetermined / Needs Review)",
        row.get("memory_advice_summary", ""),
    )
    return match.group(1) if match else ""


def memory_decision_type(row: dict[str, str]) -> str:
    match = re.search(r"judgment \(([^)]+)\)", row.get("memory_advice_summary", ""))
    return match.group(1) if match else ""


def synthetic_truth(row: dict[str, str], scenario: str) -> str:
    original = row.get("original_agent4_classification", "")
    suggestion = suggested_label(row)
    strength = row.get("memory_advice_strength", "")
    decision_type = memory_decision_type(row)

    if scenario == "original_truth":
        return original
    if scenario == "moderate_strong_memory_truth":
        return suggestion if suggestion in LABELS and strength in {"moderate", "strong"} else original
    if scenario == "all_memory_truth":
        return suggestion if suggestion in LABELS else original
    if scenario == "non_guideline_memory_truth":
        return suggestion if suggestion in LABELS and decision_type != "needs_guideline_update" else original
    raise ValueError(f"Unknown truth scenario: {scenario}")


def candidate_prediction(row: dict[str, str], policy: str) -> tuple[str, bool, bool, str]:
    """Return prediction, changed, requires_review, rule_note."""
    original = row.get("original_agent4_classification", "")
    current = row.get("memory_informed_classification", "") or original
    suggestion = suggested_label(row)
    strength = row.get("memory_advice_strength", "")
    confidence = row.get("original_confidence", "")
    decision_type = memory_decision_type(row)
    safe = safe_row(row)
    disagreement = suggestion in CHANGE_LABELS and suggestion != original
    low_medium = confidence in {"Low", "Medium"}
    non_guideline = decision_type != "needs_guideline_update"

    if policy == "current_v1":
        return current, current != original, truthy(row.get("requires_human_review_after_memory", "")), "existing_m4b1_v1"
    if policy == "escalation_only":
        review = disagreement and safe and strength in {"moderate", "strong"}
        return original, False, review, "escalate_safe_moderate_or_strong_disagreement"
    if policy == "strong_safe_low_medium":
        changed = disagreement and safe and non_guideline and strength == "strong" and low_medium
        return (suggestion if changed else original), changed, changed, "flip_strong_safe_low_medium_non_guideline"
    if policy == "moderate_strong_safe_low_medium":
        changed = disagreement and safe and non_guideline and strength in {"moderate", "strong"} and low_medium
        return (suggestion if changed else original), changed, changed, "flip_moderate_strong_safe_low_medium_non_guideline"
    if policy == "moderate_strong_safe_any_conf":
        changed = disagreement and safe and non_guideline and strength in {"moderate", "strong"}
        return (suggestion if changed else original), changed, changed, "flip_moderate_strong_safe_any_conf_non_guideline"
    if policy == "moderate_strong_safe_any_decision":
        changed = disagreement and safe and strength in {"moderate", "strong"}
        return (suggestion if changed else original), changed, changed, "flip_moderate_strong_safe_any_decision"
    if policy == "any_memory_safe_no_guideline_update":
        changed = disagreement and safe and non_guideline
        return (suggestion if changed else original), changed, changed, "flip_any_safe_non_guideline"
    if policy == "any_memory_safe_any_decision":
        changed = disagreement and safe
        return (suggestion if changed else original), changed, changed, "flip_any_safe_any_decision"
    raise ValueError(f"Unknown policy: {policy}")


def pct(value: float | None) -> float | None:
    return None if value is None else round(value * 100, 2)


def evaluate(rows: list[dict[str, str]], truth_scenario: str, policy: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    detail: list[dict[str, Any]] = []
    for row in rows:
        truth = synthetic_truth(row, truth_scenario)
        original = row.get("original_agent4_classification", "")
        prediction, changed, review, rule_note = candidate_prediction(row, policy)
        item = {
            "truth_scenario": truth_scenario,
            "policy_variant": policy,
            "setting": row.get("setting", ""),
            "pattern_id": row.get("pattern_id", ""),
            "synthetic_label": truth,
            "original_classification": original,
            "policy_classification": prediction,
            "original_correct": original == truth,
            "policy_correct": prediction == truth,
            "changed": changed,
            "requires_review": review,
            "memory_advice_strength": row.get("memory_advice_strength", ""),
            "memory_decision_type": memory_decision_type(row),
            "suggested_label": suggested_label(row),
            "original_confidence": row.get("original_confidence", ""),
            "evaluation_leakage_status": row.get("evaluation_leakage_status", ""),
            "generalization_safe": safe_row(row),
            "rule_note": rule_note,
        }
        detail.append(item)

    safe = [row for row in detail if row["generalization_safe"]]

    def pack(subset: list[dict[str, Any]]) -> dict[str, Any]:
        if not subset:
            return {
                "rows": 0,
                "original_accuracy": None,
                "policy_accuracy": None,
                "delta_pp": None,
                "changed_count": 0,
                "wrong_to_correct": 0,
                "correct_to_wrong": 0,
                "review_count": 0,
            }
        original_correct = sum(1 for row in subset if row["original_correct"])
        policy_correct = sum(1 for row in subset if row["policy_correct"])
        return {
            "rows": len(subset),
            "original_accuracy": pct(original_correct / len(subset)),
            "policy_accuracy": pct(policy_correct / len(subset)),
            "delta_pp": round(((policy_correct - original_correct) / len(subset)) * 100, 2),
            "changed_count": sum(1 for row in subset if row["changed"]),
            "wrong_to_correct": sum(1 for row in subset if not row["original_correct"] and row["policy_correct"]),
            "correct_to_wrong": sum(1 for row in subset if row["original_correct"] and not row["policy_correct"]),
            "review_count": sum(1 for row in subset if row["requires_review"]),
        }

    summary = {
        "truth_scenario": truth_scenario,
        "policy_variant": policy,
        "all_rows": pack(detail),
        "generalization_safe_rows": pack(safe),
        "real_accuracy_claim_allowed": False,
    }
    return summary, detail


def markdown_table(rows: list[dict[str, Any]]) -> str:
    columns = [
        "truth_scenario",
        "policy_variant",
        "safe_rows",
        "safe_original_accuracy",
        "safe_policy_accuracy",
        "safe_delta_pp",
        "safe_changed_count",
        "safe_wrong_to_correct",
        "safe_correct_to_wrong",
        "real_claim",
    ]
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        safe = row["generalization_safe_rows"]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['truth_scenario']}`",
                    f"`{row['policy_variant']}`",
                    str(safe["rows"]),
                    "" if safe["original_accuracy"] is None else f"{safe['original_accuracy']}%",
                    "" if safe["policy_accuracy"] is None else f"{safe['policy_accuracy']}%",
                    "" if safe["delta_pp"] is None else f"{safe['delta_pp']:+.2f}",
                    str(safe["changed_count"]),
                    str(safe["wrong_to_correct"]),
                    str(safe["correct_to_wrong"]),
                    "No",
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def build_report(summaries: list[dict[str, Any]], output_dir: Path) -> str:
    best_by_truth: dict[str, list[dict[str, Any]]] = {}
    for summary in summaries:
        best_by_truth.setdefault(summary["truth_scenario"], []).append(summary)

    lines = [
        "# M4B-1 Policy Sensitivity Experiment",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Strict Boundary",
        "",
        "This is an experimental policy-sensitivity harness. It does not modify Agent 4, M4B-1, M4B-2, baseline outputs, or `VEGO-AI/eval_output/`.",
        "",
        "All labels in this run are synthetic. These results are not expert evidence and must not be reported as accuracy improvement.",
        "",
        "## Summary Matrix",
        "",
        markdown_table(summaries),
        "",
        "## Interpretation",
        "",
        "The current `current_v1` policy remains the real implemented behavior and produces no classification changes. Candidate variants are useful for deciding which rules to discuss after real EXP-003 labels exist.",
        "",
        "If a policy improves only under `all_memory_truth`, it is an upper-bound stress test. If it harms under `original_truth`, it carries false-change risk. No policy should be implemented until real generalization-safe expert labels validate it.",
        "",
        "## Next Action",
        "",
        "Collect at least 20 generalization-safe EXP-003 expert labels, preferably 30-50. Then rerun this harness with real labels or convert a candidate into a reviewed M4B-1.1 design.",
        "",
        "## Generated Files",
        "",
        f"- `{display_path(output_dir / 'policy_sensitivity_summary.json')}`",
        f"- `{display_path(output_dir / 'policy_sensitivity_matrix.csv')}`",
        f"- `{display_path(output_dir / 'policy_sensitivity_predictions.csv')}`",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-sheet", default="reports/generated/exp003/expert_labeling_sheet_full.csv")
    parser.add_argument("--output-dir", default="reports/generated/policy_sensitivity")
    parser.add_argument("--artifact-copy", default="artifacts/POLICY_SENSITIVITY_EXPERIMENT_REPORT.md")
    args = parser.parse_args()

    input_sheet = Path(args.input_sheet)
    output_dir = Path(args.output_dir)
    artifact_copy = Path(args.artifact_copy)
    rows = read_csv(input_sheet)

    truth_scenarios = [
        "original_truth",
        "moderate_strong_memory_truth",
        "all_memory_truth",
        "non_guideline_memory_truth",
    ]
    policies = [
        "current_v1",
        "escalation_only",
        "strong_safe_low_medium",
        "moderate_strong_safe_low_medium",
        "moderate_strong_safe_any_conf",
        "moderate_strong_safe_any_decision",
        "any_memory_safe_no_guideline_update",
        "any_memory_safe_any_decision",
    ]

    summaries: list[dict[str, Any]] = []
    predictions: list[dict[str, Any]] = []
    for truth_scenario in truth_scenarios:
        for policy in policies:
            summary, detail = evaluate(rows, truth_scenario, policy)
            summaries.append(summary)
            predictions.extend(detail)

    matrix_rows = []
    for summary in summaries:
        safe = summary["generalization_safe_rows"]
        all_rows = summary["all_rows"]
        matrix_rows.append(
            {
                "truth_scenario": summary["truth_scenario"],
                "policy_variant": summary["policy_variant"],
                "safe_rows": safe["rows"],
                "safe_original_accuracy": safe["original_accuracy"],
                "safe_policy_accuracy": safe["policy_accuracy"],
                "safe_delta_pp": safe["delta_pp"],
                "safe_changed_count": safe["changed_count"],
                "safe_wrong_to_correct": safe["wrong_to_correct"],
                "safe_correct_to_wrong": safe["correct_to_wrong"],
                "safe_review_count": safe["review_count"],
                "all_rows": all_rows["rows"],
                "all_original_accuracy": all_rows["original_accuracy"],
                "all_policy_accuracy": all_rows["policy_accuracy"],
                "all_delta_pp": all_rows["delta_pp"],
                "real_accuracy_claim_allowed": False,
            }
        )

    write_csv(
        output_dir / "policy_sensitivity_matrix.csv",
        matrix_rows,
        list(matrix_rows[0].keys()),
    )
    write_csv(
        output_dir / "policy_sensitivity_predictions.csv",
        predictions,
        list(predictions[0].keys()),
    )

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": input_sheet.as_posix(),
        "warning": "Synthetic policy-sensitivity results are not expert evidence and do not prove accuracy improvement.",
        "real_accuracy_claim_allowed": False,
        "truth_scenarios": truth_scenarios,
        "policy_variants": policies,
        "matrix": matrix_rows,
        "memory_advice_strength_distribution": dict(Counter(row.get("memory_advice_strength", "") for row in rows)),
        "candidate_rows": {
            "total": len(rows),
            "generalization_safe": sum(1 for row in rows if safe_row(row)),
            "memory_suggestion_available": sum(1 for row in rows if suggested_label(row) in LABELS),
            "safe_memory_disagreement": sum(
                1
                for row in rows
                if safe_row(row)
                and suggested_label(row) in CHANGE_LABELS
                and suggested_label(row) != row.get("original_agent4_classification", "")
            ),
        },
    }
    write_json(output_dir / "policy_sensitivity_summary.json", summary)

    report = build_report(summaries, output_dir)
    report_path = output_dir / "POLICY_SENSITIVITY_EXPERIMENT_REPORT.md"
    report_path.write_text(report, encoding="utf-8")
    artifact_copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(report_path, artifact_copy)

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
