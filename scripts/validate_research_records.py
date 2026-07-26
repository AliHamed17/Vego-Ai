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
    "MetricObservation-v1": ROOT / "schemas/metric-observation-v1.schema.json",
    "ExperimentRunEnvelope-v1": ROOT
    / "schemas/experiment-run-envelope-v1.schema.json",
    "ArchitectureVariant-v1": ROOT
    / "schemas/architecture-variant-v1.schema.json",
    "ComparisonEligibility-v1": ROOT
    / "schemas/comparison-eligibility-v1.schema.json",
    "BigUIStudyRecord-v1": ROOT / "schemas/bigui-study-record-v1.schema.json",
    "ExperimentCatalogSnapshot-v1": ROOT
    / "schemas/experiment-catalog-snapshot-v1.schema.json",
}


def schema_errors(record: dict[str, Any], version: str) -> list[str]:
    schema_path = SCHEMAS[version]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    return [
        (
            ".".join(str(part) for part in issue.absolute_path) or "<root>"
        )
        + f": {issue.message}"
        for issue in sorted(validator.iter_errors(record), key=lambda item: list(item.path))
    ]


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
    elif version == "MetricObservation-v1":
        interval = record["confidenceInterval"]
        if interval is not None and interval["lower"] > interval["upper"]:
            errors.append("confidenceInterval lower cannot exceed upper")
    elif version == "ExperimentRunEnvelope-v1":
        if record["acceptanceStatus"] != "accepted" and record["acceptedAt"] is not None:
            errors.append("only accepted runs may have acceptedAt")
    elif version == "ComparisonEligibility-v1":
        fields = [check["field"] for check in record["checks"]]
        if len(fields) != len(set(fields)):
            errors.append("comparison checks must use each field at most once")
        mismatches = [check for check in record["checks"] if not check["matches"]]
        if record["eligible"] and mismatches:
            errors.append("eligible comparisons cannot contain mismatched checks")
        if not record["eligible"] and not mismatches:
            errors.append("ineligible comparisons must contain a mismatched check")
    elif version == "ExperimentCatalogSnapshot-v1":
        experiment_ids = [item["id"] for item in record["experiments"]]
        expected_ids = [f"EXP-{index:03d}" for index in range(37)]
        if experiment_ids != expected_ids:
            errors.append("experiments must contain EXP-000 through EXP-036 in order")
        metric_ids = [item.get("metricId") for item in record["metricObservations"]]
        if len(metric_ids) != len(set(metric_ids)):
            errors.append("metricObservations must have unique metricId values")
        run_ids = [item.get("runId") for item in record["acceptedRuns"]]
        run_keys = [
            (item.get("experimentId"), item.get("runId"))
            for item in record["acceptedRuns"]
        ]
        if len(run_keys) != len(set(run_keys)):
            errors.append(
                "acceptedRuns must have unique experimentId and runId pairs"
            )
        nested_groups = [
            ("architectureVariants", "ArchitectureVariant-v1"),
            ("metricObservations", "MetricObservation-v1"),
            ("acceptedRuns", "ExperimentRunEnvelope-v1"),
        ]
        for field, nested_version in nested_groups:
            for index, nested_record in enumerate(record[field]):
                for nested_error in schema_errors(nested_record, nested_version):
                    errors.append(f"{field}.{index}: {nested_error}")
                for nested_error in semantic_errors(nested_record):
                    errors.append(f"{field}.{index}: {nested_error}")

        known_metrics = set(metric_ids)
        known_runs = set(run_ids)
        for experiment in record["experiments"]:
            missing_runs = sorted(set(experiment["acceptedRunIds"]) - known_runs)
            if missing_runs:
                errors.append(
                    f"{experiment['id']} references unknown accepted runs: "
                    + ", ".join(missing_runs)
                )
            latest = experiment["latestResult"]
            if latest is not None:
                missing_metrics = sorted(
                    set(latest["metricObservationIds"]) - known_metrics
                )
                if missing_metrics:
                    errors.append(
                        f"{experiment['id']} references unknown metrics: "
                        + ", ".join(missing_metrics)
                    )
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
    errors = schema_errors(record, version)
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
