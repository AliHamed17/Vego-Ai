from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_fixture(path: Path) -> None:
    fields = [
        "setting",
        "pattern_id",
        "pattern_description",
        "affected_cases",
        "related_guideline_id",
        "original_agent4_classification",
        "memory_informed_classification",
        "requires_human_review",
        "requires_human_review_after_memory",
        "evaluation_leakage_status",
        "generalization_safe_candidate",
    ]
    rows: list[dict[str, str]] = []
    for setting in ("cd_ch", "cd_pw", "ucd_ch", "ucd_pw"):
        for index in range(1, 7):
            label = (
                "Substantial Variability"
                if index % 2
                else "Occasional Variability"
            )
            rows.append(
                {
                    "setting": setting,
                    "pattern_id": f"P{index}",
                    "pattern_description": f"Neutral fixture {setting} {index}",
                    "affected_cases": str(1000 + index),
                    "related_guideline_id": f"G{index}",
                    "original_agent4_classification": label,
                    "memory_informed_classification": label,
                    "requires_human_review": "True" if index <= 3 else "False",
                    "requires_human_review_after_memory": (
                        "True" if index == 1 else "False"
                    ),
                    "evaluation_leakage_status": "none",
                    "generalization_safe_candidate": "True",
                }
            )
    for index in range(1, 4):
        rows.append(
            {
                "setting": "cd_ch",
                "pattern_id": f"C{index}",
                "pattern_description": f"Calibration fixture {index}",
                "affected_cases": str(2000 + index),
                "related_guideline_id": f"GC{index}",
                "original_agent4_classification": "Substantial Variability",
                "memory_informed_classification": "Substantial Variability",
                "requires_human_review": "True",
                "requires_human_review_after_memory": "True",
                "evaluation_leakage_status": "same_pattern_memory_used",
                "generalization_safe_candidate": "False",
            }
        )
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def review_return(
    *,
    manifest: dict,
    slot: str,
    reviewer_id: str,
    disagree_first_two: bool = False,
) -> dict:
    records = []
    for index in range(1, 25):
        label = (
            "Substantial Variability"
            if index % 2
            else "Occasional Variability"
        )
        if disagree_first_two and index <= 2:
            label = (
                "Occasional Variability"
                if label == "Substantial Variability"
                else "Substantial Variability"
            )
        records.append(
            {
                "anonymousItemId": f"ITEM-{index:02d}",
                "expertLabel": label,
                "expertRationale": "Human fixture rationale",
                "confidence": "High",
                "reviewRequirement": (
                    "Human review required"
                    if index <= 8
                    else "Automatic handling acceptable"
                ),
                "routingRationale": "Human routing fixture rationale",
                "reviewPriority": "High" if index <= 4 else "Medium",
                "reviewDate": "2026-07-26",
                "activeSeconds": float(20 + index),
                "notes": "",
            }
        )
    return {
        "schemaVersion": "IndependentReviewReturn-v1",
        "packageVersion": manifest["packageVersion"],
        "reviewerSlot": slot,
        "reviewerId": reviewer_id,
        "sourceSheetSha256": manifest["source"]["sha256"],
        "completedAt": "2026-07-26T12:00:00Z",
        "records": records,
    }


def build_fixture(tmp_path: Path):
    builder = load_script("build_independent_evidence_package.py")
    source = tmp_path / "source.csv"
    output = tmp_path / "package"
    source_fixture(source)
    manifest = builder.build(source, output)
    return builder, source, output, manifest


def test_blind_package_is_deterministic_separated_and_empty(tmp_path: Path) -> None:
    builder, source, output, first = build_fixture(tmp_path)
    second = builder.build(source, output)
    assert first == second
    assert second["counts"] == {
        "candidateRows": 24,
        "calibrationRows": 3,
        "developmentRows": 16,
        "sealedHoldoutRows": 8,
        "reviewerCount": 2,
        "suppliedLabels": 0,
    }
    assert builder.check(source, output) == second
    reviewer_1 = list(csv.DictReader((output / "reviewer_1_evaluation.csv").open()))
    reviewer_2 = list(csv.DictReader((output / "reviewer_2_evaluation.csv").open()))
    assert [row["anonymous_item_id"] for row in reviewer_1] != [
        row["anonymous_item_id"] for row in reviewer_2
    ]
    for row in [*reviewer_1, *reviewer_2]:
        assert all(row[field] == "" for field in builder.REVIEW_FIELDS)
    private = (output / "private/item_mapping_PRIVATE.csv").read_text()
    assert "sealed_holdout" in private
    for reviewer_file in output.glob("reviewer_*"):
        if reviewer_file.is_file():
            text = reviewer_file.read_text(encoding="utf-8")
            assert "original_agent4_classification" not in text
            assert "memory_informed_classification" not in text


def test_pair_validation_computes_agreement_before_adjudication(
    tmp_path: Path,
) -> None:
    _builder, _source, package, manifest = build_fixture(tmp_path)
    validator = load_script("validate_independent_evidence_returns.py")
    left_path = tmp_path / "reviewer_1.json"
    right_path = tmp_path / "reviewer_2.json"
    left_path.write_text(
        json.dumps(
            review_return(
                manifest=manifest,
                slot="reviewer_1",
                reviewer_id="expert_one",
            )
        )
    )
    right_path.write_text(
        json.dumps(
            review_return(
                manifest=manifest,
                slot="reviewer_2",
                reviewer_id="expert_two",
                disagree_first_two=True,
            )
        )
    )
    result = validator.validate_pair(
        package,
        left_path,
        right_path,
        tmp_path / "validation",
    )
    assert result["agreement"]["itemCount"] == 24
    assert result["agreement"]["agreementCount"] == 22
    assert result["agreement"]["disagreementCount"] == 2
    assert result["gate"]["status"] == "ADJUDICATION_REQUIRED"
    workbook = list(
        csv.DictReader(
            (tmp_path / "validation/adjudication_workbook.csv").open(
                encoding="utf-8"
            )
        )
    )
    assert len(workbook) == 24
    assert all(row["adjudicated_label"] == "" for row in workbook)


def test_pair_validation_rejects_non_independent_or_automated_reviewers(
    tmp_path: Path,
) -> None:
    _builder, _source, package, manifest = build_fixture(tmp_path)
    validator = load_script("validate_independent_evidence_returns.py")
    left = review_return(
        manifest=manifest,
        slot="reviewer_1",
        reviewer_id="same_reviewer",
    )
    right = review_return(
        manifest=manifest,
        slot="reviewer_2",
        reviewer_id="same_reviewer",
    )
    left_path, right_path = tmp_path / "left.json", tmp_path / "right.json"
    left_path.write_text(json.dumps(left))
    right_path.write_text(json.dumps(right))
    with pytest.raises(ValueError, match="two different"):
        validator.validate_pair(package, left_path, right_path, tmp_path / "out")
    right["reviewerId"] = "ChatGPT reviewer"
    right_path.write_text(json.dumps(right))
    with pytest.raises(ValueError, match="automated or synthetic"):
        validator.validate_pair(package, left_path, right_path, tmp_path / "out")


def test_zero_label_evaluation_is_null_and_holdout_fails_closed(
    tmp_path: Path,
) -> None:
    _builder, _source, package, manifest = build_fixture(tmp_path)
    evaluator = load_script("evaluate_independent_ground_truth.py")
    result = evaluator.null_result(manifest)
    assert result["status"] == "NOT YET COMPUTABLE"
    assert result["baseline"]["accuracy"] is None
    assert result["baseline"]["macroF1"] is None
    assert result["paired"]["netCorrection"] is None

    gold_template = package / "private/gold_labels_template.csv"
    with pytest.raises(ValueError, match="missing adjudication fields"):
        evaluator.evaluate(
            package,
            gold_template,
            stage="sealed_holdout",
            policy_manifest_path=None,
        )


def test_delivery_contains_no_private_mapping_or_labels(tmp_path: Path) -> None:
    _builder, _source, package, _manifest = build_fixture(tmp_path)
    publisher = load_script("publish_independent_evidence_package.py")
    destination = tmp_path / "delivery"
    manifest = publisher.refresh(package, destination)
    assert manifest["suppliedLabels"] == 0
    assert manifest["privateMappingIncluded"] is False
    assert publisher.check(package, destination) == manifest
    paths = {
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file()
    }
    assert not any("private" in path.casefold() for path in paths)
    assert not any("gold" in path.casefold() for path in paths)


def test_explicit_adjudication_freezes_gold_and_enables_development_metrics(
    tmp_path: Path,
) -> None:
    _builder, _source, package, manifest = build_fixture(tmp_path)
    validator = load_script("validate_independent_evidence_returns.py")
    left_payload = review_return(
        manifest=manifest,
        slot="reviewer_1",
        reviewer_id="expert_one",
    )
    right_payload = review_return(
        manifest=manifest,
        slot="reviewer_2",
        reviewer_id="expert_two",
    )
    left_path, right_path = tmp_path / "left.json", tmp_path / "right.json"
    left_path.write_text(json.dumps(left_payload))
    right_path.write_text(json.dumps(right_payload))
    validation = tmp_path / "validation"
    validator.validate_pair(package, left_path, right_path, validation)
    workbook_path = validation / "adjudication_workbook.csv"
    workbook = list(csv.DictReader(workbook_path.open(encoding="utf-8")))
    fields = list(workbook[0])
    for row in workbook:
        row.update(
            {
                "adjudicated_label": row["reviewer_1_label"],
                "adjudicated_rationale": "Explicit human fixture adjudication",
                "adjudicated_review_requirement": row[
                    "reviewer_1_review_requirement"
                ],
                "adjudicated_routing_rationale": (
                    "Explicit human routing fixture adjudication"
                ),
                "adjudicated_review_priority": row["reviewer_1_review_priority"],
                "adjudicator_id": "human_adjudicator",
                "adjudication_date": "2026-07-26",
            }
        )
    with workbook_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(workbook)

    freezer = load_script("freeze_independent_gold_labels.py")
    gold_dir = tmp_path / "gold"
    freeze_manifest = freezer.freeze(
        package=package,
        reviewer_1_path=left_path,
        reviewer_2_path=right_path,
        adjudication_path=workbook_path,
        output=gold_dir,
    )
    assert freeze_manifest["goldLabelCount"] == 24

    evaluator = load_script("evaluate_independent_ground_truth.py")
    result = evaluator.evaluate(
        package,
        gold_dir / "gold_labels.csv",
        stage="development",
        policy_manifest_path=None,
    )
    assert result["evaluatedRows"] == 16
    assert result["baseline"]["accuracy"] == result["currentComparator"]["accuracy"]
    assert result["currentComparator"]["classificationChanges"] == 0
    assert result["paired"]["netCorrection"] == 0
    assert result["routing"]["baseline"]["n"] == 16
