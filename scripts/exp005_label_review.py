#!/usr/bin/env python3
"""Build and validate the EXP-005 real-label accuracy gate package.

EXP-005 does not change VEGO-AI behavior. It packages the current EXP-003
labeling rows for expert review, validates filled labels, and evaluates
candidate policy variants against real labels only when those labels exist.
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


ALLOWED_LABELS = {
    "Substantial Variability",
    "Occasional Variability",
    "Undetermined / Needs Review",
}

CHANGE_LABELS = {
    "Substantial Variability",
    "Occasional Variability",
}

LABEL_FIELDS = (
    "expert_label",
    "expert_rationale",
    "reviewer_id",
    "review_date",
    "confidence",
    "notes",
)

COPY_LABEL_FIELDS = (
    "expert_label",
    "expert_rationale",
    "reviewer_id",
    "review_date",
    "confidence",
    "reviewer_confidence",
    "notes",
)

BLIND_FIELDS = (
    "review_row_id",
    "exp005_priority_rank",
    "review_priority",
    "setting",
    "pattern_id",
    "pattern_description",
    "affected_cases",
    "related_guideline_id",
    "pattern_strength",
    "pattern_kind",
    "requires_human_review",
    "flag_for_guidelines_update",
    "expert_label",
    "expert_rationale",
    "reviewer_id",
    "review_date",
    "confidence",
    "notes",
)

FULL_EXTRA_FIELDS = (
    "review_row_id",
    "review_priority",
    "exp005_priority_score",
    "exp005_priority_rank",
    "exp005_priority_group",
    "exp005_priority_reasons",
    "safe_memory_disagreement",
    "memory_suggestion_available",
    "memory_suggested_label",
    "memory_decision_type",
)

POLICIES = (
    "current_v1",
    "escalation_only",
    "strong_safe_low_medium",
    "moderate_strong_safe_low_medium",
    "moderate_strong_safe_any_conf",
    "moderate_strong_safe_any_decision",
    "any_memory_safe_no_guideline_update",
    "any_memory_safe_any_decision",
)


class Exp005Error(RuntimeError):
    """Raised when EXP-005 inputs are invalid."""


def truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def normalize_label(value: str) -> str:
    label = (value or "").strip()
    if label == "Undetermined":
        return "Undetermined / Needs Review"
    return label


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise Exp005Error(f"CSV not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str] | tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def markdown_cell(value: Any) -> str:
    return str(value if value is not None else "").replace("\n", " ").replace("|", "\\|")


def key_for(row: dict[str, str]) -> tuple[str, str]:
    return row.get("setting", ""), row.get("pattern_id", "")


def merge_filled_labels(base_rows: list[dict[str, str]], filled_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    filled_by_key = {key_for(row): row for row in filled_rows}
    merged: list[dict[str, str]] = []
    for row in base_rows:
        item = dict(row)
        filled = filled_by_key.get(key_for(row))
        if filled:
            for field in COPY_LABEL_FIELDS:
                if field in filled:
                    item[field] = filled.get(field, "")
            if not item.get("confidence") and filled.get("reviewer_confidence"):
                item["confidence"] = filled.get("reviewer_confidence", "")
        merged.append(item)
    return merged


def suggested_label(row: dict[str, str]) -> str:
    match = re.search(
        r"classified .*? as (Substantial Variability|Occasional Variability|Undetermined / Needs Review)",
        row.get("memory_advice_summary", ""),
    )
    return match.group(1) if match else ""


def memory_decision_type(row: dict[str, str]) -> str:
    match = re.search(r"judgment \(([^)]+)\)", row.get("memory_advice_summary", ""))
    return match.group(1) if match else ""


def is_safe_candidate(row: dict[str, str]) -> bool:
    return truthy(row.get("generalization_safe_candidate", "")) and row.get("evaluation_leakage_status") != "same_pattern_memory_used"


def has_valid_label(row: dict[str, str]) -> bool:
    return normalize_label(row.get("expert_label", "")) in ALLOWED_LABELS and not validation_errors(row)


def validation_errors(row: dict[str, str]) -> list[str]:
    errors: list[str] = []
    label = normalize_label(row.get("expert_label", ""))
    if not label:
        return errors
    if label not in ALLOWED_LABELS:
        errors.append("invalid expert_label")
    if not row.get("expert_rationale", "").strip():
        errors.append("missing expert_rationale")
    if not row.get("reviewer_id", "").strip():
        errors.append("missing reviewer_id")
    if not row.get("review_date", "").strip():
        errors.append("missing review_date")
    if not (row.get("confidence", "").strip() or row.get("reviewer_confidence", "").strip()):
        errors.append("missing confidence")
    return errors


def priority_for(row: dict[str, str]) -> tuple[int, str, list[str]]:
    score = 0
    reasons: list[str] = []
    safe = is_safe_candidate(row)
    suggestion = suggested_label(row)
    disagreement = safe and suggestion in CHANGE_LABELS and suggestion != row.get("original_agent4_classification", "")

    if safe:
        score += 1000
        reasons.append("generalization-safe candidate")
    if disagreement:
        score += 500
        reasons.append("safe memory disagreement")
    if truthy(row.get("requires_human_review_after_memory", "")):
        score += 450
        reasons.append("requires human review after memory")
    if row.get("memory_advice_strength") == "strong":
        score += 300
        reasons.append("strong memory advice")
    elif row.get("memory_advice_strength") == "moderate":
        score += 250
        reasons.append("moderate memory advice")
    elif row.get("memory_advice_strength") == "weak":
        score += 80
        reasons.append("weak memory advice")
    if truthy(row.get("flag_for_guidelines_update", "")):
        score += 150
        reasons.append("guideline-update candidate")
    if row.get("original_confidence", "").lower() in {"low", "medium"}:
        score += 120
        reasons.append("low/medium original confidence")
    if row.get("evaluation_leakage_status") == "same_pattern_memory_used":
        score -= 400
        reasons.append("same-pattern mechanism row")

    try:
        score += int(row.get("sampling_priority_score", "") or 0)
    except ValueError:
        pass

    if disagreement or truthy(row.get("requires_human_review_after_memory", "")):
        group = "G1: label first - safe memory disagreement/review"
    elif safe and row.get("memory_advice_strength") in {"strong", "moderate"}:
        group = "G2: label early - safe moderate/strong advice"
    elif safe and (truthy(row.get("flag_for_guidelines_update", "")) or row.get("original_confidence", "").lower() in {"low", "medium"}):
        group = "G3: label early - safe guideline/confidence case"
    elif safe:
        group = "G4: safe baseline coverage"
    else:
        group = "G5: mechanism-only or non-safe row"

    return score, group, list(dict.fromkeys(reasons))


def enrich_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    scored: list[tuple[int, int, dict[str, str]]] = []
    for index, row in enumerate(rows):
        item = dict(row)
        for field in LABEL_FIELDS:
            item.setdefault(field, "")
        suggestion = suggested_label(item)
        decision_type = memory_decision_type(item)
        safe_disagreement = is_safe_candidate(item) and suggestion in CHANGE_LABELS and suggestion != item.get("original_agent4_classification", "")
        score, group, reasons = priority_for(item)
        item["review_row_id"] = f"{item.get('setting', 'unknown')}::{item.get('pattern_id', 'unknown')}"
        item["review_priority"] = "High" if score >= 1300 else "Medium" if score >= 1000 else "Low"
        item["exp005_priority_score"] = str(score)
        item["exp005_priority_group"] = group
        item["exp005_priority_reasons"] = "; ".join(reasons)
        item["safe_memory_disagreement"] = str(safe_disagreement)
        item["memory_suggestion_available"] = str(suggestion in ALLOWED_LABELS)
        item["memory_suggested_label"] = suggestion
        item["memory_decision_type"] = decision_type
        scored.append((score, index, item))

    enriched: list[dict[str, str]] = []
    for rank, (_, _, row) in enumerate(sorted(scored, key=lambda value: (-value[0], value[1])), start=1):
        row["exp005_priority_rank"] = str(rank)
        enriched.append(row)
    return enriched


def make_blind_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [{field: row.get(field, "") for field in BLIND_FIELDS} for row in rows]


def candidate_prediction(row: dict[str, str], policy: str) -> tuple[str, bool, bool, str]:
    original = row.get("original_agent4_classification", "")
    current = row.get("memory_informed_classification", "") or original
    suggestion = suggested_label(row)
    strength = row.get("memory_advice_strength", "")
    confidence = row.get("original_confidence", "")
    decision_type = memory_decision_type(row)
    safe = is_safe_candidate(row)
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
        return suggestion if changed else original, changed, changed, "flip_strong_safe_low_medium_non_guideline"
    if policy == "moderate_strong_safe_low_medium":
        changed = disagreement and safe and non_guideline and strength in {"moderate", "strong"} and low_medium
        return suggestion if changed else original, changed, changed, "flip_moderate_strong_safe_low_medium_non_guideline"
    if policy == "moderate_strong_safe_any_conf":
        changed = disagreement and safe and non_guideline and strength in {"moderate", "strong"}
        return suggestion if changed else original, changed, changed, "flip_moderate_strong_safe_any_conf_non_guideline"
    if policy == "moderate_strong_safe_any_decision":
        changed = disagreement and safe and strength in {"moderate", "strong"}
        return suggestion if changed else original, changed, changed, "flip_moderate_strong_safe_any_decision"
    if policy == "any_memory_safe_no_guideline_update":
        changed = disagreement and safe and non_guideline
        return suggestion if changed else original, changed, changed, "flip_any_safe_non_guideline"
    if policy == "any_memory_safe_any_decision":
        changed = disagreement and safe
        return suggestion if changed else original, changed, changed, "flip_any_safe_any_decision"
    raise Exp005Error(f"Unknown policy: {policy}")


def evaluate_real_policy_gate(rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    safe_labeled = [
        row
        for row in rows
        if has_valid_label(row)
        and is_safe_candidate(row)
        and normalize_label(row.get("expert_label", "")) in CHANGE_LABELS
    ]
    matrix: list[dict[str, Any]] = []
    predictions: list[dict[str, Any]] = []

    for policy in POLICIES:
        original_correct = 0
        policy_correct = 0
        changed_count = 0
        wrong_to_correct = 0
        correct_to_wrong = 0
        review_count = 0

        for row in safe_labeled:
            expert = normalize_label(row.get("expert_label", ""))
            original = row.get("original_agent4_classification", "")
            prediction, changed, review, rule_note = candidate_prediction(row, policy)
            original_is_correct = original == expert
            policy_is_correct = prediction == expert
            original_correct += int(original_is_correct)
            policy_correct += int(policy_is_correct)
            changed_count += int(changed)
            wrong_to_correct += int(not original_is_correct and policy_is_correct)
            correct_to_wrong += int(original_is_correct and not policy_is_correct)
            review_count += int(review)
            predictions.append(
                {
                    "policy_variant": policy,
                    "setting": row.get("setting", ""),
                    "pattern_id": row.get("pattern_id", ""),
                    "expert_label": expert,
                    "original_classification": original,
                    "policy_classification": prediction,
                    "original_correct": str(original_is_correct),
                    "policy_correct": str(policy_is_correct),
                    "changed": str(changed),
                    "requires_review": str(review),
                    "rule_note": rule_note,
                    "memory_advice_strength": row.get("memory_advice_strength", ""),
                    "memory_suggested_label": suggested_label(row),
                    "evaluation_leakage_status": row.get("evaluation_leakage_status", ""),
                }
            )

        rows_count = len(safe_labeled)
        original_accuracy = None if rows_count == 0 else round(original_correct / rows_count, 4)
        policy_accuracy = None if rows_count == 0 else round(policy_correct / rows_count, 4)
        delta_pp = None if rows_count == 0 else round(((policy_correct - original_correct) / rows_count) * 100, 2)
        matrix.append(
            {
                "policy_variant": policy,
                "safe_decidable_label_count": rows_count,
                "original_accuracy": original_accuracy,
                "policy_accuracy": policy_accuracy,
                "delta_pp": delta_pp,
                "changed_count": changed_count,
                "wrong_to_correct": wrong_to_correct,
                "correct_to_wrong": correct_to_wrong,
                "review_count": review_count,
                "accuracy_claim_allowed": False,
            }
        )

    return matrix, predictions


def summarize_labels(rows: list[dict[str, str]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    supplied = [row for row in rows if normalize_label(row.get("expert_label", ""))]
    invalid: list[dict[str, Any]] = []
    for row in supplied:
        errors = validation_errors(row)
        if errors:
            invalid.append(
                {
                    "setting": row.get("setting", ""),
                    "pattern_id": row.get("pattern_id", ""),
                    "expert_label": row.get("expert_label", ""),
                    "errors": "; ".join(errors),
                }
            )

    valid = [row for row in rows if has_valid_label(row)]
    safe_valid = [row for row in valid if is_safe_candidate(row)]
    safe_decidable = [row for row in safe_valid if normalize_label(row.get("expert_label", "")) in CHANGE_LABELS]
    same_pattern = [row for row in valid if row.get("evaluation_leakage_status") == "same_pattern_memory_used"]

    if len(safe_valid) == 0:
        gate_status = "Accuracy improvement cannot be evaluated yet."
    elif len(safe_valid) < 20:
        gate_status = "Pilot evidence only; fewer than 20 generalization-safe expert labels."
    else:
        gate_status = "Generalization-safe accuracy evaluation available; improvement claim still requires observed positive delta and review."

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "experiment_id": "EXP-005",
        "row_count": len(rows),
        "generalization_safe_candidate_count": sum(1 for row in rows if is_safe_candidate(row)),
        "memory_suggestion_available_count": sum(1 for row in rows if suggested_label(row) in ALLOWED_LABELS),
        "safe_memory_disagreement_count": sum(1 for row in rows if truthy(row.get("safe_memory_disagreement", ""))),
        "requires_human_review_after_memory_count": sum(1 for row in rows if truthy(row.get("requires_human_review_after_memory", ""))),
        "labels_supplied_count": len(supplied),
        "valid_label_count": len(valid),
        "invalid_label_count": len(invalid),
        "generalization_safe_valid_label_count": len(safe_valid),
        "generalization_safe_decidable_label_count": len(safe_decidable),
        "same_pattern_valid_label_count": len(same_pattern),
        "label_distribution": dict(Counter(normalize_label(row.get("expert_label", "")) for row in valid)),
        "priority_group_distribution": dict(Counter(row.get("exp005_priority_group", "") for row in rows)),
        "strict_gate": {
            "minimum_safe_labels_for_non_pilot": 20,
            "preferred_safe_labels": "30-50",
            "status": gate_status,
            "quantitative_evaluation_allowed": len(safe_valid) >= 20,
            "accuracy_improvement_claim_allowed": False,
        },
    }
    return summary, invalid


def write_labeling_instructions(path: Path, row_count: int, safe_count: int) -> None:
    text = f"""# EXP-005 Labeling Instructions

Purpose: collect independent expert labels so VEGO-AI accuracy can be evaluated without same-pattern leakage.

## Which File To Use

- `exp005_label_review_blind.csv`: use this for expert labeling. It hides original Agent 4 and memory-informed classifications.
- `exp005_label_review_full.csv`: use this only for audit after labeling. It includes original and memory context.

## Required Fields

Allowed `expert_label` values:

- `Substantial Variability`
- `Occasional Variability`
- `Undetermined / Needs Review`

Fill these fields for each labeled row:

- `expert_label`
- `expert_rationale`
- `reviewer_id`
- `review_date`
- `confidence`
- `notes` when clarification is needed

## Gate

This package contains {row_count} rows, including {safe_count} generalization-safe candidates.

- `0` safe labels: report `Accuracy improvement cannot be evaluated yet.`
- `1-19` safe labels: report pilot evidence only.
- `20+` safe labels: quantitative evaluation can be reported, with validity threats.
- Preferred target: 30-50 safe labels across audited runs.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_label_first(path: Path, rows: list[dict[str, str]], limit: int) -> None:
    columns = [
        "rank",
        "setting",
        "pattern_id",
        "priority_group",
        "reason",
        "original",
        "memory_advice",
        "memory_suggested",
        "review_after_memory",
    ]
    lines = [
        "# EXP-005 Label These First",
        "",
        "Use this list for supervisor discussion. Use the blind CSV for actual expert labeling.",
        "",
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    selected: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        if len(selected) < limit or truthy(row.get("requires_human_review_after_memory", "")):
            row_id = row.get("review_row_id", "")
            if row_id not in seen:
                selected.append(row)
                seen.add(row_id)

    for row in selected:
        values = [
            row.get("exp005_priority_rank", ""),
            row.get("setting", ""),
            row.get("pattern_id", ""),
            row.get("exp005_priority_group", ""),
            row.get("exp005_priority_reasons", ""),
            row.get("original_agent4_classification", ""),
            row.get("memory_advice_strength", ""),
            row.get("memory_suggested_label", ""),
            row.get("requires_human_review_after_memory", ""),
        ]
        lines.append("| " + " | ".join(markdown_cell(value) for value in values) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_policy_gate_report(
    path: Path,
    label_summary: dict[str, Any],
    real_matrix: list[dict[str, Any]],
    synthetic_matrix_path: Path,
) -> None:
    lines = [
        "# EXP-005 Real Vs Synthetic Policy Gate",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Gate Status",
        "",
        label_summary["strict_gate"]["status"],
        "",
        "Synthetic EXP-004 results remain policy-risk screening only. Real labels are required before any policy refinement.",
        "",
    ]

    if synthetic_matrix_path.exists():
        lines.extend(
            [
                "## Synthetic Reference",
                "",
                f"Existing synthetic matrix found at `{synthetic_matrix_path.as_posix()}`.",
                "",
            ]
        )
    else:
        lines.extend(["## Synthetic Reference", "", "No synthetic matrix was found for comparison.", ""])

    lines.extend(
        [
            "## Real-Label Policy Matrix",
            "",
            "| policy_variant | safe_decidable_label_count | original_accuracy | policy_accuracy | delta_pp | changed_count | wrong_to_correct | correct_to_wrong |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in real_matrix:
        lines.append(
            "| "
            + " | ".join(
                markdown_cell(value)
                for value in [
                    row["policy_variant"],
                    row["safe_decidable_label_count"],
                    row["original_accuracy"],
                    row["policy_accuracy"],
                    row["delta_pp"],
                    row["changed_count"],
                    row["wrong_to_correct"],
                    row["correct_to_wrong"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision Rule",
            "",
            "Do not implement M4B-1.1 or M4B-2 unless the real-label matrix has at least 20 safe labels and shows a justified deterministic improvement without unacceptable changed-and-wrong cases.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_package_report(
    path: Path,
    summary: dict[str, Any],
    invalid_rows: list[dict[str, Any]],
    output_dir: Path,
) -> str:
    lines = [
        "# EXP-005 Label Review Package",
        "",
        f"Generated: {summary['generated_at']}",
        "",
        "## Purpose",
        "",
        "EXP-005 moves VEGO-AI accuracy work from synthetic policy simulation toward real expert-label evidence. It does not modify Agent 4, M4B-1 production behavior, M4B-2, baseline outputs, `VEGO-AI/eval_output`, LLM/API behavior, or embeddings.",
        "",
        "## Current Gate",
        "",
        f"- Status: {summary['strict_gate']['status']}",
        f"- Rows: {summary['row_count']}",
        f"- Generalization-safe candidates: {summary['generalization_safe_candidate_count']}",
        f"- Safe memory disagreements: {summary['safe_memory_disagreement_count']}",
        f"- Requires human review after memory: {summary['requires_human_review_after_memory_count']}",
        f"- Valid labels supplied: {summary['valid_label_count']}",
        f"- Generalization-safe valid labels: {summary['generalization_safe_valid_label_count']}",
        "",
        "## Files",
        "",
        f"- `{(output_dir / 'exp005_label_review_blind.csv').as_posix()}`",
        f"- `{(output_dir / 'exp005_label_review_full.csv').as_posix()}`",
        f"- `{(output_dir / 'label_these_first.md').as_posix()}`",
        f"- `{(output_dir / 'labeling_instructions.md').as_posix()}`",
        f"- `{(output_dir / 'label_validation_summary.json').as_posix()}`",
        f"- `{(output_dir / 'real_vs_synthetic_policy_gate.md').as_posix()}`",
        "",
        "## Interpretation",
        "",
        "If no generalization-safe labels are present, accuracy improvement cannot be evaluated yet. If fewer than 20 safe labels are present, report only pilot evidence. Synthetic EXP-004 policy gains remain counterfactual until EXP-005 labels exist.",
    ]

    if invalid_rows:
        lines.extend(["", "## Invalid Filled Labels", ""])
        lines.append("| setting | pattern_id | expert_label | errors |")
        lines.append("| --- | --- | --- | --- |")
        for row in invalid_rows:
            lines.append(
                "| "
                + " | ".join(markdown_cell(row.get(column, "")) for column in ("setting", "pattern_id", "expert_label", "errors"))
                + " |"
            )

    content = "\n".join(lines) + "\n"
    path.write_text(content, encoding="utf-8")
    return content


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-sheet", default="reports/generated/exp003/expert_labeling_sheet_full.csv")
    parser.add_argument("--filled-label-sheet", default="")
    parser.add_argument("--output-dir", default="reports/generated/exp005_label_review")
    parser.add_argument("--artifact-copy", default="artifacts/EXP005_LABEL_REVIEW_PACKAGE.md")
    parser.add_argument("--synthetic-matrix", default="reports/generated/policy_sensitivity/policy_sensitivity_matrix.csv")
    parser.add_argument("--label-first-limit", type=int, default=12)
    args = parser.parse_args()

    source_sheet = Path(args.source_sheet)
    filled_sheet = Path(args.filled_label_sheet) if args.filled_label_sheet else None
    output_dir = Path(args.output_dir)
    artifact_copy = Path(args.artifact_copy)
    synthetic_matrix = Path(args.synthetic_matrix)

    rows = read_csv(source_sheet)
    if filled_sheet:
        rows = merge_filled_labels(rows, read_csv(filled_sheet))

    enriched = enrich_rows(rows)
    fieldnames = list(dict.fromkeys([*enriched[0].keys(), *FULL_EXTRA_FIELDS])) if enriched else list(FULL_EXTRA_FIELDS)
    blind_rows = make_blind_rows(enriched)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "exp005_label_review_full.csv", enriched, fieldnames)
    write_csv(output_dir / "exp005_label_review_blind.csv", blind_rows, BLIND_FIELDS)
    write_labeling_instructions(
        output_dir / "labeling_instructions.md",
        row_count=len(enriched),
        safe_count=sum(1 for row in enriched if is_safe_candidate(row)),
    )
    write_label_first(output_dir / "label_these_first.md", enriched, args.label_first_limit)

    summary, invalid_rows = summarize_labels(enriched)
    write_json(output_dir / "label_validation_summary.json", summary)
    write_csv(output_dir / "invalid_labels.csv", invalid_rows, ("setting", "pattern_id", "expert_label", "errors"))

    real_matrix, real_predictions = evaluate_real_policy_gate(enriched)
    write_csv(
        output_dir / "real_label_policy_gate.csv",
        real_matrix,
        (
            "policy_variant",
            "safe_decidable_label_count",
            "original_accuracy",
            "policy_accuracy",
            "delta_pp",
            "changed_count",
            "wrong_to_correct",
            "correct_to_wrong",
            "review_count",
            "accuracy_claim_allowed",
        ),
    )
    write_csv(
        output_dir / "real_label_policy_predictions.csv",
        real_predictions,
        (
            "policy_variant",
            "setting",
            "pattern_id",
            "expert_label",
            "original_classification",
            "policy_classification",
            "original_correct",
            "policy_correct",
            "changed",
            "requires_review",
            "rule_note",
            "memory_advice_strength",
            "memory_suggested_label",
            "evaluation_leakage_status",
        ),
    )
    write_policy_gate_report(output_dir / "real_vs_synthetic_policy_gate.md", summary, real_matrix, synthetic_matrix)

    package_report = build_package_report(output_dir / "EXP005_LABEL_REVIEW_PACKAGE.md", summary, invalid_rows, output_dir)
    artifact_copy.parent.mkdir(parents=True, exist_ok=True)
    artifact_copy.write_text(package_report, encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
