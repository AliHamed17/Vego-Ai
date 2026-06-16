from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "evaluate_accuracy_improvement.py"


def _write_exp002_sheet(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "setting",
        "pattern_id",
        "pattern_description",
        "affected_cases",
        "related_guideline_id",
        "pattern_strength",
        "pattern_kind",
        "original_agent4_classification",
        "original_confidence",
        "original_justification",
        "requires_human_review",
        "flag_for_guidelines_update",
        "memory_advice_strength",
        "memory_advice_summary",
        "memory_match_ids",
        "memory_informed_classification",
        "memory_informed_differs_from_original",
        "requires_human_review_after_memory",
        "rule_applied",
        "evaluation_leakage_status",
        "generalization_safe_candidate",
        "existing_expert_label",
        "existing_expert_label_source",
        "existing_reviewer_id",
        "expert_label",
        "expert_rationale",
        "reviewer_id",
        "reviewer_confidence",
        "sampling_priority_score",
        "sampling_reasons",
        "source_comparison_file",
    ]
    rows = [
        {
            "setting": "ucd_ch",
            "pattern_id": "P1",
            "pattern_description": "Missing required catalog number.",
            "affected_cases": "A;B",
            "related_guideline_id": "G1",
            "pattern_strength": "20%",
            "pattern_kind": "guideline",
            "original_agent4_classification": "Occasional Variability",
            "original_confidence": "Medium",
            "original_justification": "Original rationale",
            "requires_human_review": "False",
            "flag_for_guidelines_update": "True",
            "memory_advice_strength": "strong",
            "memory_advice_summary": "Advice",
            "memory_match_ids": "HJM-1",
            "memory_informed_classification": "Substantial Variability",
            "memory_informed_differs_from_original": "True",
            "requires_human_review_after_memory": "True",
            "rule_applied": "test_rule",
            "evaluation_leakage_status": "none",
            "generalization_safe_candidate": "True",
            "existing_expert_label": "",
            "existing_expert_label_source": "",
            "existing_reviewer_id": "",
            "expert_label": "Substantial Variability",
            "expert_rationale": "Expert rationale",
            "reviewer_id": "expert_01",
            "reviewer_confidence": "",
            "sampling_priority_score": "100",
            "sampling_reasons": "test",
            "source_comparison_file": "memory_informed_comparison.json",
        }
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_exp003_generates_blind_sheet_and_safe_label_metrics(tmp_path: Path) -> None:
    sheet = tmp_path / "expert_labeling_sheet.csv"
    output = tmp_path / "exp003"
    _write_exp002_sheet(sheet)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--exp002-sheet",
            str(sheet),
            "--output-dir",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    summary = json.loads((output / "accuracy_summary.json").read_text(encoding="utf-8"))
    assert summary["independent_labeled_count"] == 1
    assert summary["generalization_safe_labeled_count"] == 1
    assert summary["strict_gate"]["accuracy_improvement_claim_allowed"] is False
    assert "Pilot evidence" in summary["strict_gate"]["status"]

    blind_header = (output / "expert_labeling_sheet_blind.csv").read_text(encoding="utf-8").splitlines()[0]
    assert "original_agent4_classification" not in blind_header
    assert "memory_informed_classification" not in blind_header
    assert "expert_label" in blind_header
    assert "Substantial Variability" in result.stdout
