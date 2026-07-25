#!/usr/bin/env python3
"""Validate thesis research records against schemas and cross-field invariants."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "GoldLabelRecord-v2": ROOT / "schemas/gold-label-record-v2.schema.json",
    "EvaluationRunManifest-v2": ROOT
    / "schemas/evaluation-run-manifest-v2.schema.json",
    "PolicyCandidateRecord-v1": ROOT
    / "schemas/policy-candidate-record-v1.schema.json",
    "ArchitectureRunManifest": ROOT
    / "schemas/architecture-run-manifest-v1.schema.json",
    "BaselineLockManifest-v2": ROOT
    / "schemas/baseline-lock-manifest-v2.schema.json",
    "model-execution-manifest-v1": ROOT
    / "schemas/model-execution-manifest-v1.schema.json",
    "ReleaseManifest-v3": ROOT / "schemas/release-manifest-v3.schema.json",
    "SecurityPostureSnapshot-v1": ROOT
    / "schemas/security-posture-snapshot-v1.schema.json",
    "HLayerIterationManifest-v1": ROOT
    / "schemas/hlayer-iteration-manifest-v1.schema.json",
}


def semantic_errors(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    version = record.get("schemaVersion")
    if version == "EvaluationRunManifest-v2":
        counts = record["labelStats"]
        ordered = [
            counts["generalizationSafeLabels"],
            counts["validLabels"],
            counts["suppliedLabels"],
            counts["candidateRows"],
        ]
        if ordered != sorted(ordered):
            errors.append(
                "label counts must satisfy generalizationSafeLabels <= "
                "validLabels <= suppliedLabels <= candidateRows"
            )
        if counts["adjudicatedRows"] > counts["validLabels"]:
            errors.append("adjudicatedRows cannot exceed validLabels")
        if counts["validLabels"] > 0 and counts["reviewerCount"] < 2:
            errors.append("valid empirical labels require at least two reviewers")
    elif version == "PolicyCandidateRecord-v1":
        rule_ids = [rule["ruleId"] for rule in record["deterministicRules"]]
        if len(rule_ids) != len(set(rule_ids)):
            errors.append("deterministicRules must have unique ruleId values")
    elif version == "GoldLabelRecord-v2":
        if (
            record["recordType"] == "adjudicated_gold"
            and record["recordId"] in record["rawReviewRecordIds"]
        ):
            errors.append("an adjudicated record cannot reference itself")
    return errors


def validate_record(record: dict[str, Any]) -> list[str]:
    version = (
        record.get("schemaVersion")
        or record.get("contract")
        or record.get("schema_version")
    )
    schema_path = SCHEMAS.get(version)
    if schema_path is None:
        return [f"unsupported schemaVersion: {version!r}"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    errors = [
        (
            ".".join(str(part) for part in issue.absolute_path) or "<root>"
        )
        + f": {issue.message}"
        for issue in sorted(validator.iter_errors(record), key=lambda item: list(item.path))
    ]
    errors.extend(semantic_errors(record))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", nargs="+", type=Path)
    args = parser.parse_args()
    paths: list[Path] = []
    for supplied in args.records:
        if supplied.is_dir():
            paths.extend(
                path
                for path in sorted(supplied.rglob("*.json"))
                if not path.name.endswith(".invalid.json")
            )
        else:
            paths.append(supplied)
    failures: list[str] = []
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"{path}: {exc}")
            continue
        records = payload if isinstance(payload, list) else [payload]
        for index, record in enumerate(records):
            for error in validate_record(record):
                failures.append(f"{path}[{index}]: {error}")
    if failures:
        print("research record validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("research record validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
