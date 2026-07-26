#!/usr/bin/env python3
"""Validate two independent calibration returns without creating gold labels."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = ROOT / "reports/generated/independent_evidence_v1"
SCHEMA = ROOT / "schemas/independent-calibration-return-v1.schema.json"
AUTOMATED_TOKENS = ("chatgpt", "codex", "synthetic", "automated", "llm", "bot")
EXPECTED_IDS = {f"CAL-{index:02d}" for index in range(1, 4)}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected an object: {path}")
    return value


def validate_return(
    payload: dict[str, Any],
    *,
    slot: str,
    package_manifest: dict[str, Any],
) -> None:
    schema = load_json(SCHEMA)
    jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    ).validate(payload)
    if payload["reviewerSlot"] != slot:
        raise ValueError(f"{slot} return declares {payload['reviewerSlot']}")
    if payload["packageVersion"] != package_manifest["packageVersion"]:
        raise ValueError(f"{slot} package version does not match")
    if payload["sourceSheetSha256"] != package_manifest["source"]["sha256"]:
        raise ValueError(f"{slot} source sheet hash does not match")
    reviewer = payload["reviewerId"].strip().casefold()
    if any(token in reviewer for token in AUTOMATED_TOKENS):
        raise ValueError(f"{slot} reviewer ID appears automated or synthetic")
    ids = [record["anonymousItemId"] for record in payload["records"]]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{slot} contains duplicate calibration IDs")
    if set(ids) != EXPECTED_IDS:
        raise ValueError(f"{slot} must contain CAL-01 through CAL-03")


def agreement(left: list[str], right: list[str]) -> dict[str, Any]:
    if len(left) != len(right) or not left:
        raise ValueError("agreement inputs must have the same nonzero length")
    observed_count = sum(a == b for a, b in zip(left, right, strict=True))
    n = len(left)
    observed = observed_count / n
    left_counts = Counter(left)
    right_counts = Counter(right)
    labels = set(left_counts) | set(right_counts)
    expected = sum(
        (left_counts[label] / n) * (right_counts[label] / n) for label in labels
    )
    kappa = None if math.isclose(1.0 - expected, 0.0) else (
        observed - expected
    ) / (1.0 - expected)
    return {
        "itemCount": n,
        "agreementCount": observed_count,
        "disagreementCount": n - observed_count,
        "observedAgreement": round(observed, 6),
        "cohenKappa": None if kappa is None else round(kappa, 6),
    }


def validate_pair(
    package: Path,
    reviewer_1_path: Path,
    reviewer_2_path: Path,
    output: Path,
) -> dict[str, Any]:
    manifest = load_json(package / "package_manifest.json")
    if manifest.get("governance", {}).get("programStage") != "calibration_ready":
        raise ValueError("independent-evidence decisions are not calibration-ready")
    left = load_json(reviewer_1_path)
    right = load_json(reviewer_2_path)
    validate_return(left, slot="reviewer_1", package_manifest=manifest)
    validate_return(right, slot="reviewer_2", package_manifest=manifest)
    if left["reviewerId"].strip().casefold() == right["reviewerId"].strip().casefold():
        raise ValueError("calibration requires two different human reviewers")

    left_rows = {record["anonymousItemId"]: record for record in left["records"]}
    right_rows = {record["anonymousItemId"]: record for record in right["records"]}
    ordered_ids = sorted(EXPECTED_IDS)
    classification = agreement(
        [left_rows[item]["expertLabel"] for item in ordered_ids],
        [right_rows[item]["expertLabel"] for item in ordered_ids],
    )
    routing = agreement(
        [left_rows[item]["reviewRequirement"] for item in ordered_ids],
        [right_rows[item]["reviewRequirement"] for item in ordered_ids],
    )
    discrepancies = [
        {
            "anonymousItemId": item,
            "classificationDiffers": (
                left_rows[item]["expertLabel"] != right_rows[item]["expertLabel"]
            ),
            "routingDiffers": (
                left_rows[item]["reviewRequirement"]
                != right_rows[item]["reviewRequirement"]
            ),
            "priorityDiffers": (
                left_rows[item]["reviewPriority"]
                != right_rows[item]["reviewPriority"]
            ),
        }
        for item in ordered_ids
        if (
            left_rows[item]["expertLabel"] != right_rows[item]["expertLabel"]
            or left_rows[item]["reviewRequirement"]
            != right_rows[item]["reviewRequirement"]
            or left_rows[item]["reviewPriority"]
            != right_rows[item]["reviewPriority"]
        )
    ]
    active_seconds = {
        "reviewer_1": round(
            sum(float(record["activeSeconds"]) for record in left["records"]), 3
        ),
        "reviewer_2": round(
            sum(float(record["activeSeconds"]) for record in right["records"]), 3
        ),
    }
    report = {
        "schemaVersion": "IndependentCalibrationPairReport-v1",
        "status": "HUMAN_INSTRUCTION_FREEZE_REQUIRED",
        "packageVersion": manifest["packageVersion"],
        "decisionRegisterSha256": manifest["governance"][
            "decisionRegisterSha256"
        ],
        "reviewerReturns": [
            {
                "reviewerSlot": "reviewer_1",
                "reviewerId": left["reviewerId"],
                "sha256": sha256_file(reviewer_1_path),
            },
            {
                "reviewerSlot": "reviewer_2",
                "reviewerId": right["reviewerId"],
                "sha256": sha256_file(reviewer_2_path),
            },
        ],
        "classificationAgreement": classification,
        "routingAgreement": routing,
        "activeSeconds": active_seconds,
        "discrepancies": discrepancies,
        "calibrationRowsExcludedFromPerformance": True,
        "evaluationReleaseAuthorized": False,
        "claimBoundary": (
            "Calibration measures instruction comprehension only. It creates no "
            "gold label, accuracy, macro-F1, generalization, or routing-policy result."
        ),
    }
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / "calibration_pair_report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    freeze_template = {
        "schemaVersion": "IndependentCalibrationInstructionFreeze-v1",
        "status": "PENDING_HUMAN_FREEZE",
        "pairReportSha256": sha256_file(report_path),
        "instructionDisposition": None,
        "clarifications": [],
        "reviewedBy": None,
        "reviewDate": None,
        "rationale": None,
        "reviewerReturnSha256": [
            item["sha256"] for item in report["reviewerReturns"]
        ],
        "evaluationReleaseAuthorized": False,
    }
    (output / "calibration_instruction_freeze.template.json").write_text(
        json.dumps(freeze_template, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report


def gate(package: Path) -> dict[str, Any]:
    manifest = load_json(package / "package_manifest.json")
    governance = manifest.get("governance", {})
    if governance.get("programStage") != "calibration_ready":
        raise ValueError("supervisor approval is not complete")
    return {
        "status": "CALIBRATION_INPUT_REQUIRED",
        "programStage": governance["programStage"],
        "requiredHumanReviewers": 2,
        "receivedCalibrationReturns": 0,
        "evaluationReleaseAuthorized": False,
        "suppliedLabels": manifest["counts"]["suppliedLabels"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--reviewer-1", type=Path)
    parser.add_argument("--reviewer-2", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_PACKAGE / "validation/calibration",
    )
    parser.add_argument("--check-gate", action="store_true")
    args = parser.parse_args()
    try:
        if args.check_gate:
            print(json.dumps(gate(args.package), indent=2))
        else:
            if not args.reviewer_1 or not args.reviewer_2:
                parser.error("--reviewer-1 and --reviewer-2 are required")
            report = validate_pair(
                args.package,
                args.reviewer_1,
                args.reviewer_2,
                args.output,
            )
            print(
                "Independent calibration: PASS "
                f"({report['classificationAgreement']['agreementCount']}/3 "
                "classification agreement; human instruction freeze required)"
            )
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        jsonschema.ValidationError,
    ) as exc:
        print(f"Independent calibration: FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
