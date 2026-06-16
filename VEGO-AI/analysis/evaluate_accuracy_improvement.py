#!/usr/bin/env python3
"""Prepare and evaluate leakage-aware accuracy-improvement evidence.

This script is intentionally read-only with respect to VEGO-AI baseline outputs.
It consumes EXP-002 labeling rows plus existing M4A/M4B-1 artifacts and writes
generated EXP-003 reports under reports/generated/exp003 by default.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOWED_LABELS = {
    "Substantial Variability",
    "Occasional Variability",
    "Undetermined / Needs Review",
}

LABEL_FIELDS = (
    "expert_label",
    "expert_rationale",
    "reviewer_id",
    "review_date",
    "confidence",
    "notes",
)

ERROR_ANALYSIS_COLUMNS = (
    "setting",
    "pattern_id",
    "original_classification",
    "expert_label",
    "original_correct",
    "original_confidence",
    "related_guideline_id",
    "pattern_description",
    "affected_cases",
    "memory_advice_strength",
    "memory_informed_classification",
    "memory_informed_differs_from_original",
    "requires_human_review_after_memory",
    "evaluation_leakage_status",
    "error_type",
)

COMPARISON_COLUMNS = (
    "setting",
    "pattern_id",
    "expert_label",
    "prediction",
    "correct",
    "evaluation_leakage_status",
    "generalization_safe_candidate",
)

PAIRED_COLUMNS = (
    "setting",
    "pattern_id",
    "expert_label",
    "original_classification",
    "memory_informed_classification",
    "original_correct",
    "memory_informed_correct",
    "memory_informed_differs_from_original",
    "requires_human_review_after_memory",
    "evaluation_leakage_status",
)

BLIND_REMOVE_COLUMNS = {
    "original_agent4_classification",
    "original_confidence",
    "original_justification",
    "memory_informed_classification",
    "memory_informed_differs_from_original",
    "memory_advice_summary",
    "memory_match_ids",
    "existing_expert_label",
    "existing_expert_label_source",
    "existing_reviewer_id",
}


class EvaluationError(RuntimeError):
    """Raised when evaluation inputs are invalid."""


@dataclass(frozen=True)
class MetricSet:
    rows: int
    accuracy: float | None
    macro_f1: float | None
    confusion_matrix: dict[str, dict[str, int]]
    per_class: list[dict[str, Any]]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise EvaluationError(f"Input CSV not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def markdown_cell(value: Any) -> str:
    return str(value if value is not None else "").replace("\n", " ").replace("|", "\\|")


def write_markdown_table(path: Path, title: str, rows: list[dict[str, Any]], columns: list[str] | tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", ""]
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join("---" for _ in columns) + " |")
    for row in rows:
        lines.append("| " + " | ".join(markdown_cell(row.get(column, "")) for column in columns) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def normalize_label(value: str) -> str:
    label = (value or "").strip()
    if label == "Undetermined":
        return "Undetermined / Needs Review"
    return label


def has_independent_label(row: dict[str, str]) -> bool:
    return normalize_label(row.get("expert_label", "")) in ALLOWED_LABELS


def is_generalization_safe(row: dict[str, str]) -> bool:
    return (
        has_independent_label(row)
        and truthy(row.get("generalization_safe_candidate", ""))
        and row.get("evaluation_leakage_status", "") != "same_pattern_memory_used"
    )


def priority_score(row: dict[str, str]) -> tuple[int, str]:
    score = 0
    reasons: list[str] = []

    if truthy(row.get("generalization_safe_candidate", "")):
        score += 1000
        reasons.append("generalization-safe candidate")
    if truthy(row.get("requires_human_review_after_memory", "")):
        score += 300
        reasons.append("requires review after memory")
    if row.get("memory_advice_strength", "") in {"strong", "moderate"}:
        score += 200
        reasons.append(f"{row.get('memory_advice_strength')} memory advice")
    if truthy(row.get("flag_for_guidelines_update", "")):
        score += 120
        reasons.append("guideline-update candidate")
    if row.get("original_confidence", "").lower() in {"low", "medium"}:
        score += 100
        reasons.append("low/medium original confidence")

    try:
        score += int(row.get("sampling_priority_score", "") or 0)
    except ValueError:
        pass

    if row.get("sampling_reasons"):
        reasons.append(row["sampling_reasons"])

    return score, "; ".join(dict.fromkeys(reasons))


def enrich_label_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    enriched: list[dict[str, str]] = []
    scored: list[tuple[int, int, dict[str, str]]] = []
    for index, row in enumerate(rows):
        score, reasons = priority_score(row)
        item = dict(row)
        item.setdefault("review_date", "")
        item.setdefault("confidence", "")
        item.setdefault("notes", "")
        item["exp003_priority_score"] = str(score)
        item["exp003_priority_reasons"] = reasons
        scored.append((score, index, item))

    for rank, (_, _, row) in enumerate(sorted(scored, key=lambda item: (-item[0], item[1])), start=1):
        row["exp003_priority_rank"] = str(rank)
        enriched.append(row)
    return enriched


def make_blind_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[str]]:
    fieldnames = [field for field in rows[0].keys() if field not in BLIND_REMOVE_COLUMNS] if rows else []
    for required in LABEL_FIELDS:
        if required not in fieldnames:
            fieldnames.append(required)
    return [{field: row.get(field, "") for field in fieldnames} for row in rows], fieldnames


def classify_error(row: dict[str, str]) -> str:
    original = row.get("original_agent4_classification", "")
    expert = normalize_label(row.get("expert_label", ""))

    if not expert:
        return ""
    if expert == "Undetermined / Needs Review":
        return "ambiguous_requires_review"
    if original == expert:
        return "no_error"
    if truthy(row.get("flag_for_guidelines_update", "")):
        return "guideline_update_missed"
    if original == "Occasional Variability" and expert == "Substantial Variability":
        if "alternative" in row.get("pattern_kind", "").lower():
            return "missed_valid_alternative"
        return "false_occasional"
    if original == "Substantial Variability" and expert == "Occasional Variability":
        if "mistake" in row.get("pattern_kind", "").lower():
            return "missed_misconception"
        return "false_substantial"
    return "ambiguous_requires_review"


def build_error_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        if not has_independent_label(row):
            continue
        expert = normalize_label(row.get("expert_label", ""))
        original = row.get("original_agent4_classification", "")
        output.append(
            {
                "setting": row.get("setting", ""),
                "pattern_id": row.get("pattern_id", ""),
                "original_classification": original,
                "expert_label": expert,
                "original_correct": str(original == expert),
                "original_confidence": row.get("original_confidence", ""),
                "related_guideline_id": row.get("related_guideline_id", ""),
                "pattern_description": row.get("pattern_description", ""),
                "affected_cases": row.get("affected_cases", ""),
                "memory_advice_strength": row.get("memory_advice_strength", ""),
                "memory_informed_classification": row.get("memory_informed_classification", ""),
                "memory_informed_differs_from_original": row.get("memory_informed_differs_from_original", ""),
                "requires_human_review_after_memory": row.get("requires_human_review_after_memory", ""),
                "evaluation_leakage_status": row.get("evaluation_leakage_status", ""),
                "error_type": classify_error(row),
            }
        )
    return output


def comparison_rows(rows: list[dict[str, str]], prediction_field: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        if not has_independent_label(row):
            continue
        expert = normalize_label(row.get("expert_label", ""))
        prediction = row.get(prediction_field, "")
        output.append(
            {
                "setting": row.get("setting", ""),
                "pattern_id": row.get("pattern_id", ""),
                "expert_label": expert,
                "prediction": prediction,
                "correct": str(prediction == expert),
                "evaluation_leakage_status": row.get("evaluation_leakage_status", ""),
                "generalization_safe_candidate": row.get("generalization_safe_candidate", ""),
            }
        )
    return output


def paired_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        if not has_independent_label(row):
            continue
        expert = normalize_label(row.get("expert_label", ""))
        original = row.get("original_agent4_classification", "")
        memory = row.get("memory_informed_classification", "")
        output.append(
            {
                "setting": row.get("setting", ""),
                "pattern_id": row.get("pattern_id", ""),
                "expert_label": expert,
                "original_classification": original,
                "memory_informed_classification": memory,
                "original_correct": str(original == expert),
                "memory_informed_correct": str(memory == expert),
                "memory_informed_differs_from_original": row.get("memory_informed_differs_from_original", ""),
                "requires_human_review_after_memory": row.get("requires_human_review_after_memory", ""),
                "evaluation_leakage_status": row.get("evaluation_leakage_status", ""),
            }
        )
    return output


def metric_set(rows: list[dict[str, str]], prediction_field: str) -> MetricSet:
    labeled = [row for row in rows if has_independent_label(row)]
    labels = sorted({normalize_label(row.get("expert_label", "")) for row in labeled} | {row.get(prediction_field, "") for row in labeled})
    labels = [label for label in labels if label]
    matrix = {gold: {pred: 0 for pred in labels} for gold in labels}

    correct = 0
    for row in labeled:
        gold = normalize_label(row.get("expert_label", ""))
        pred = row.get(prediction_field, "")
        if gold not in matrix:
            matrix[gold] = {label: 0 for label in labels}
        if pred not in matrix[gold]:
            matrix[gold][pred] = 0
        matrix[gold][pred] += 1
        correct += int(gold == pred)

    per_class = []
    for label in labels:
        tp = sum(1 for row in labeled if normalize_label(row.get("expert_label", "")) == label and row.get(prediction_field, "") == label)
        fp = sum(1 for row in labeled if normalize_label(row.get("expert_label", "")) != label and row.get(prediction_field, "") == label)
        fn = sum(1 for row in labeled if normalize_label(row.get("expert_label", "")) == label and row.get(prediction_field, "") != label)
        precision = None if tp + fp == 0 else tp / (tp + fp)
        recall = None if tp + fn == 0 else tp / (tp + fn)
        f1 = None if precision is None or recall is None or precision + recall == 0 else 2 * precision * recall / (precision + recall)
        per_class.append(
            {
                "label": label,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }
        )

    f1_values = [item["f1"] for item in per_class if item["f1"] is not None]
    return MetricSet(
        rows=len(labeled),
        accuracy=None if not labeled else correct / len(labeled),
        macro_f1=None if not f1_values else sum(f1_values) / len(f1_values),
        confusion_matrix=matrix,
        per_class=per_class,
    )


def metric_dict(rows: list[dict[str, str]]) -> dict[str, Any]:
    all_labeled = [row for row in rows if has_independent_label(row)]
    safe_labeled = [row for row in rows if is_generalization_safe(row)]
    no_same_pattern = [row for row in all_labeled if row.get("evaluation_leakage_status", "") != "same_pattern_memory_used"]

    def pack(label_rows: list[dict[str, str]]) -> dict[str, Any]:
        original = metric_set(label_rows, "original_agent4_classification")
        memory = metric_set(label_rows, "memory_informed_classification")
        return {
            "rows": original.rows,
            "original_accuracy": original.accuracy,
            "memory_informed_accuracy": memory.accuracy,
            "original_macro_f1": original.macro_f1,
            "memory_informed_macro_f1": memory.macro_f1,
            "original_confusion_matrix": original.confusion_matrix,
            "memory_informed_confusion_matrix": memory.confusion_matrix,
            "original_per_class": original.per_class,
            "memory_informed_per_class": memory.per_class,
        }

    paired = paired_rows(rows)
    return {
        "all_labeled": pack(all_labeled),
        "excluding_same_pattern": pack(no_same_pattern),
        "generalization_safe": pack(safe_labeled),
        "paired": {
            "original_wrong_memory_correct": sum(1 for row in paired if row["original_correct"] == "False" and row["memory_informed_correct"] == "True"),
            "original_correct_memory_wrong": sum(1 for row in paired if row["original_correct"] == "True" and row["memory_informed_correct"] == "False"),
            "both_correct": sum(1 for row in paired if row["original_correct"] == "True" and row["memory_informed_correct"] == "True"),
            "both_wrong": sum(1 for row in paired if row["original_correct"] == "False" and row["memory_informed_correct"] == "False"),
            "changed_and_correct": sum(1 for row in paired if truthy(row["memory_informed_differs_from_original"]) and row["memory_informed_correct"] == "True"),
            "changed_and_wrong": sum(1 for row in paired if truthy(row["memory_informed_differs_from_original"]) and row["memory_informed_correct"] == "False"),
            "unchanged": sum(1 for row in paired if not truthy(row["memory_informed_differs_from_original"])),
        },
    }


def simple_bar_svg(title: str, counts: dict[str, int]) -> str:
    width = 900
    height = 360
    margin = 70
    items = sorted(counts.items())
    max_value = max([value for _, value in items], default=1)
    slot = (width - margin * 2) / max(len(items), 1)
    bars = []
    for index, (label, value) in enumerate(items):
        bar_width = slot * 0.56
        bar_height = 190 * value / max_value
        x = margin + index * slot + slot * 0.22
        y = 280 - bar_height
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" rx="5" fill="#0B7285"/>'
            f'<text x="{x + bar_width / 2:.1f}" y="{y - 10:.1f}" text-anchor="middle" class="value">{value}</text>'
            f'<text x="{x + bar_width / 2:.1f}" y="318" text-anchor="middle" class="label">{label}</text>'
        )
    return "\n".join(
        [
            '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="360" viewBox="0 0 900 360">',
            "<style>.title{font:700 28px Arial;fill:#0F172A}.label{font:400 15px Arial;fill:#334155}.value{font:700 17px Arial;fill:#0F172A}</style>",
            '<rect width="900" height="360" fill="#F8FAFC"/>',
            f'<text x="70" y="50" class="title">{title}</text>',
            *bars,
            "</svg>",
        ]
    )


def write_labeling_instructions(path: Path, safe_count: int, row_count: int) -> None:
    text = f"""# EXP-003 Labeling Instructions

Purpose: collect independent expert labels before any accuracy-improvement claim.

## Files

- `expert_labeling_sheet_full.csv`: full context; includes original VEGO-AI / Agent 4 classification.
- `expert_labeling_sheet_blind.csv`: reduced-bias context; hides original and memory-informed classifications.

## Required Labels

Allowed `expert_label` values:

- `Substantial Variability`
- `Occasional Variability`
- `Undetermined / Needs Review`

Required fields to fill:

- `expert_label`
- `expert_rationale`
- `reviewer_id`
- `review_date`
- `confidence`
- `notes` when needed

## Labeling Rule

Judge the pattern from the pattern description, affected cases, related guideline, and domain context. Do not copy Agent 4 output. Do not use same-pattern Human Judgment Memory as generalization evidence.

## Priority

This package contains {row_count} rows. {safe_count} rows are currently marked as generalization-safe candidates. Label at least 20 generalization-safe rows before reporting accuracy as more than pilot evidence; preferred target is 30-50 labels across audited runs.

## Stop Gate

If fewer than 20 generalization-safe expert labels are filled, report only pilot evidence. If 0 safe labels are filled, report: "Accuracy improvement cannot be evaluated yet."
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_summary(rows: list[dict[str, str]], error_rows: list[dict[str, Any]], metrics: dict[str, Any]) -> dict[str, Any]:
    labeled = [row for row in rows if has_independent_label(row)]
    safe = [row for row in rows if is_generalization_safe(row)]
    differs_count = sum(1 for row in rows if truthy(row.get("memory_informed_differs_from_original", "")))
    review_after_memory = sum(1 for row in rows if truthy(row.get("requires_human_review_after_memory", "")))

    if len(safe) == 0:
        claim_status = "Accuracy improvement cannot be evaluated yet."
    elif len(safe) < 20:
        claim_status = "Pilot evidence only; fewer than 20 generalization-safe expert labels."
    else:
        claim_status = "Generalization-safe accuracy evaluation available."

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "experiment_id": "EXP-003",
        "purpose": "Accuracy improvement evaluation after independent expert labels",
        "row_count": len(rows),
        "independent_labeled_count": len(labeled),
        "generalization_safe_labeled_count": len(safe),
        "generalization_safe_candidate_count": sum(1 for row in rows if truthy(row.get("generalization_safe_candidate", ""))),
        "memory_informed_differs_from_original_count": differs_count,
        "requires_human_review_after_memory_count": review_after_memory,
        "error_type_distribution": dict(Counter(row["error_type"] for row in error_rows if row.get("error_type"))),
        "errors_by_setting": dict(Counter(row["setting"] for row in error_rows if row.get("error_type") and row["error_type"] != "no_error")),
        "errors_by_confidence": dict(Counter(row["original_confidence"] for row in error_rows if row.get("error_type") and row["error_type"] != "no_error")),
        "errors_by_advice_strength": dict(Counter(row["memory_advice_strength"] for row in error_rows if row.get("error_type") and row["error_type"] != "no_error")),
        "metrics": metrics,
        "strict_gate": {
            "minimum_safe_labels_for_non_pilot": 20,
            "status": claim_status,
            "accuracy_improvement_claim_allowed": len(safe) >= 20,
            "automatic_accuracy_delta_possible": differs_count > 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp002-sheet", default="reports/generated/exp002/expert_labeling_sheet.csv")
    parser.add_argument("--output-dir", default="reports/generated/exp003")
    args = parser.parse_args()

    sheet_path = Path(args.exp002_sheet)
    output_dir = Path(args.output_dir)

    source_rows = read_csv(sheet_path)
    enriched_rows = enrich_label_rows(source_rows)
    full_fields = list(enriched_rows[0].keys()) if enriched_rows else []
    blind_rows, blind_fields = make_blind_rows(enriched_rows)

    safe_candidates = sum(1 for row in enriched_rows if truthy(row.get("generalization_safe_candidate", "")))
    write_csv(output_dir / "expert_labeling_sheet_full.csv", enriched_rows, full_fields)
    write_csv(output_dir / "expert_labeling_sheet_blind.csv", blind_rows, blind_fields)
    write_labeling_instructions(output_dir / "labeling_instructions.md", safe_candidates, len(enriched_rows))

    error_rows = build_error_rows(enriched_rows)
    original_rows = comparison_rows(enriched_rows, "original_agent4_classification")
    memory_rows = comparison_rows(enriched_rows, "memory_informed_classification")
    paired = paired_rows(enriched_rows)
    metrics = metric_dict(enriched_rows)
    summary = build_summary(enriched_rows, error_rows, metrics)

    write_csv(output_dir / "error_analysis.csv", error_rows, ERROR_ANALYSIS_COLUMNS)
    write_markdown_table(output_dir / "error_analysis.md", "EXP-003 Error Analysis", error_rows, ERROR_ANALYSIS_COLUMNS)
    write_csv(output_dir / "original_vs_expert.csv", original_rows, COMPARISON_COLUMNS)
    write_csv(output_dir / "memory_informed_vs_expert.csv", memory_rows, COMPARISON_COLUMNS)
    write_csv(output_dir / "paired_comparison.csv", paired, PAIRED_COLUMNS)
    write_json(output_dir / "error_summary.json", summary)
    write_json(output_dir / "accuracy_summary.json", summary)

    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    (figures_dir / "label_coverage.svg").write_text(
        simple_bar_svg(
            "EXP-003 Label Coverage",
            {
                "rows": len(enriched_rows),
                "safe candidates": safe_candidates,
                "labeled": summary["independent_labeled_count"],
                "safe labeled": summary["generalization_safe_labeled_count"],
            },
        ),
        encoding="utf-8",
    )
    (figures_dir / "memory_advice_strength.svg").write_text(
        simple_bar_svg("Memory Advice Strength", dict(Counter(row.get("memory_advice_strength", "unknown") for row in enriched_rows))),
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
