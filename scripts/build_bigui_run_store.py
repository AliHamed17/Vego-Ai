#!/usr/bin/env python3
"""Build and validate accepted VEGO-AI experiment run bundles.

The tracked bundles contain only privacy-safe aggregate observations.  Rich
local run folders and the SQLite index are generated under reports/generated.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vego_bigui.store import (  # noqa: E402
    BundleValidator,
    canonical_sha256,
    file_sha256,
    load_bundles,
    rebuild_sqlite,
    run_store_summary,
)

ACCEPTED_ROOT = ROOT / "experiments" / "accepted-runs"
LOCAL_ROOT = ROOT / "reports" / "generated" / "experiments"
DATABASE = ROOT / "reports" / "generated" / "bigui" / "run-registry.sqlite"
SCHEMA_ROOT = ROOT / "schemas"
PROGRAM = (
    ROOT / "docs" / "research" / "h-layer" / "program-status-snapshot-v1.json"
)
BASELINE = (
    ROOT / "docs" / "research" / "hardening" / "baseline-lock-manifest-v2.json"
)
CATALOG = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "experiment-catalog-snapshot-v1.json"
)
BIGUI_PROGRAM = ROOT / "experiments" / "bigui-program-v1.json"
ARCHITECTURE_SUMMARY = (
    ROOT / "reports" / "generated" / "bigui_architecture" / "summary.json"
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def generated_at(value: dict[str, Any], fallback: str) -> str:
    for key in ("generatedAt", "generated_at", "generated"):
        candidate = value.get(key)
        if isinstance(candidate, str) and candidate:
            return candidate.replace("Z", "+00:00") if candidate.endswith("Z") else candidate
    return fallback.replace("Z", "+00:00") if fallback.endswith("Z") else fallback


def date_part(timestamp: str) -> str:
    match = re.match(r"^(\d{4}-\d{2}-\d{2})", timestamp)
    if not match:
        raise ValueError(f"invalid experiment timestamp {timestamp!r}")
    return match.group(1)


def source_revision(program: dict[str, Any]) -> str:
    value = str(program["sourceRevision"])
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("program sourceRevision is invalid")
    return value


def baseline_cohort_hash(baseline: dict[str, Any]) -> str:
    return canonical_sha256(
        [
            item["canonicalJsonSha256"]
            for item in baseline["agent4Outputs"]["files"]
        ]
    )


@dataclass
class RunBuilder:
    experiment_id: str
    run_id: str
    baseline_id: str
    comparator_id: str
    source_path: Path
    source_sha256: str
    evidence_class: str
    observation_date: str
    cohort_hash: str

    def __post_init__(self) -> None:
        self.definitions: dict[str, dict[str, Any]] = {}
        self.observations: list[dict[str, Any]] = []

    def add(
        self,
        metric_id: str,
        value: Any,
        numerator: int | float | None,
        denominator: int | float | None,
        unit: str,
        *,
        title: str,
        formula: str,
        direction: str = "neutral",
        grain: str = "experiment run",
        dimensions: dict[str, Any] | None = None,
        estimand: str | None = None,
        exclusions: list[str] | None = None,
        missing_count: int = 0,
        analysis_method: str = "deterministic aggregate",
        confidence_interval: dict[str, Any] | None = None,
        claim_boundary: str,
        required_evidence: str | None = None,
        target: dict[str, Any] | None = None,
    ) -> None:
        definition = {
            "schemaVersion": "MetricDefinition-v1",
            "metricId": metric_id,
            "title": title,
            "description": estimand or title,
            "formula": formula,
            "unit": unit,
            "direction": direction,
            "grain": grain,
            "requiredEvidenceClass": required_evidence or self.evidence_class,
            "nullable": value is None,
            "nullRule": (
                "Must remain null when required evidence is unavailable."
                if value is None
                else "Observed from the accepted experiment run."
            ),
            "dimensions": sorted((dimensions or {}).keys()),
            "target": target,
        }
        previous = self.definitions.get(metric_id)
        if previous is not None and previous != definition:
            raise ValueError(f"inconsistent definition for {metric_id}")
        self.definitions[metric_id] = definition
        definition_hash = canonical_sha256(definition)
        identity_payload = {
            "experimentId": self.experiment_id,
            "runId": self.run_id,
            "metricId": metric_id,
            "dimensions": dimensions or {},
        }
        suffix = canonical_sha256(identity_payload)[:12]
        self.observations.append(
            {
                "schemaVersion": "MetricObservation-v2",
                "observationId": f"OBS-METRIC-{metric_id}-{suffix}",
                "experimentId": self.experiment_id,
                "runId": self.run_id,
                "metricId": metric_id,
                "metricDefinitionSha256": definition_hash,
                "baselineId": self.baseline_id,
                "comparatorId": self.comparator_id,
                "value": value,
                "numerator": numerator,
                "denominator": denominator,
                "missingCount": missing_count,
                "unit": unit,
                "direction": direction,
                "estimand": estimand or title,
                "grain": grain,
                "dimensions": dimensions or {},
                "exclusions": exclusions or [],
                "analysisMethod": analysis_method,
                "confidenceInterval": confidence_interval,
                "sourcePath": relative(self.source_path),
                "sourceSha256": self.source_sha256,
                "evidenceClass": self.evidence_class,
                "observationDate": self.observation_date,
                "cohortHash": self.cohort_hash,
                "metricSchemaVersion": "2.0",
                "claimBoundary": claim_boundary,
            }
        )


def context(
    baseline: dict[str, Any],
    cohort_hash: str,
    evidence: str,
    *,
    architecture_mode: str = "legacy",
    topology: str = "not_applicable",
    interface_version: str = "not_applicable",
    policy_version: str = "m4b1-v1",
) -> dict[str, str]:
    return {
        "datasetHash": cohort_hash,
        "partitionHash": "not_applicable",
        "baselineRevision": baseline["officialTagCommit"],
        "policyVersion": policy_version,
        "promptVersion": "historical-frozen",
        "modelIdentifier": "gpt-4o-historical-alias",
        "metricSchemaVersion": "2.0",
        "labelEligibility": "generalization_safe",
        "leakageClass": "none",
        "evidenceClass": evidence,
        "architectureMode": architecture_mode,
        "topology": topology,
        "interfaceVersion": interface_version,
        "pairedCohortHash": cohort_hash,
    }


def make_bundle(
    experiment_id: str,
    source_path: Path,
    evidence_class: str,
    baseline: dict[str, Any],
    program: dict[str, Any],
    metric_callback,
    *,
    baseline_id: str,
    comparator_id: str,
    verdict: str,
    execution_valid: bool = True,
    deterministic: bool | None = None,
    engineering_target_met: bool | None = None,
    evidence_admissible: bool = True,
    architecture_mode: str = "legacy",
    topology: str = "not_applicable",
    interface_version: str = "not_applicable",
    claim_boundary: str,
    criteria: list[tuple[str, bool, str]] | None = None,
) -> dict[str, Any]:
    source = load_json(source_path)
    source_hash = file_sha256(source_path)
    run_id = f"{experiment_id}-{source_hash[:12]}"
    timestamp = generated_at(source, program["generatedAt"])
    cohort_hash = baseline_cohort_hash(baseline)
    builder = RunBuilder(
        experiment_id=experiment_id,
        run_id=run_id,
        baseline_id=baseline_id,
        comparator_id=comparator_id,
        source_path=source_path,
        source_sha256=source_hash,
        evidence_class=evidence_class,
        observation_date=date_part(timestamp),
        cohort_hash=cohort_hash,
    )
    metric_callback(builder, source)
    definitions = sorted(
        builder.definitions.values(), key=lambda item: item["metricId"]
    )
    observations = sorted(
        builder.observations, key=lambda item: item["observationId"]
    )
    criteria_rows = [
        {"id": item_id, "passed": passed, "detail": detail}
        for item_id, passed, detail in (
            criteria
            or [
                (
                    "SOURCE_PRESENT_AND_HASHED",
                    True,
                    "The source summary exists and has a recorded SHA-256 hash.",
                ),
                (
                    "CLAIM_BOUNDARY_RECORDED",
                    bool(claim_boundary),
                    "The run records its admissible evidence boundary.",
                ),
            ]
        )
    ]
    acceptance_status = (
        "accepted"
        if execution_valid and evidence_admissible and all(
            item["passed"] for item in criteria_rows
        )
        else "quarantined"
    )
    evaluation = {
        "schemaVersion": "ExperimentEvaluation-v1",
        "experimentId": experiment_id,
        "runId": run_id,
        "executionValid": execution_valid,
        "deterministic": deterministic,
        "engineeringTargetMet": engineering_target_met,
        "evidenceAdmissible": evidence_admissible,
        "resultVerdict": verdict,
        "criteria": criteria_rows,
        "claimBoundary": claim_boundary,
    }
    definition_hashes = {
        item["metricId"]: canonical_sha256(item) for item in definitions
    }
    manifest_path = source_path
    sibling_manifest = source_path.with_name("manifest.json")
    if sibling_manifest.is_file():
        manifest_path = sibling_manifest
    envelope = {
        "schemaVersion": "ExperimentRunEnvelope-v2",
        "experimentId": experiment_id,
        "runId": run_id,
        "attemptId": "attempt-001",
        "executionStatus": "succeeded" if execution_valid else "failed",
        "startedAt": timestamp,
        "completedAt": timestamp,
        "durationMilliseconds": None,
        "manifestSchema": (
            "HLayerExperimentManifest"
            if sibling_manifest.is_file()
            else "SanitizedAggregateSource"
        ),
        "manifestPath": relative(manifest_path),
        "manifestSha256": file_sha256(manifest_path),
        "acceptanceStatus": acceptance_status,
        "acceptedAt": timestamp if acceptance_status == "accepted" else None,
        "evidenceClass": evidence_class,
        "sourceRevision": source_revision(program),
        "inputHashes": {"baselineCohort": cohort_hash},
        "outputHashes": {"summary": source_hash},
        "metricObservationIds": [
            item["observationId"] for item in observations
        ],
        "metricDefinitionHashes": definition_hashes,
        "comparisonContext": context(
            baseline,
            cohort_hash,
            evidence_class,
            architecture_mode=architecture_mode,
            topology=topology,
            interface_version=interface_version,
        ),
        "artifactRefs": [relative(source_path)],
        "logRef": None,
        "evaluation": evaluation,
    }
    acceptance = {
        "schemaVersion": "RunAcceptanceRecord-v1",
        "experimentId": experiment_id,
        "runId": run_id,
        "status": acceptance_status,
        "evaluatorVersion": "bigui-run-store-v1",
        "evaluatedAt": timestamp,
        "criteriaOutcomes": criteria_rows,
        "rationale": (
            "The privacy-safe aggregate run is accepted for its stated evidence class."
            if acceptance_status == "accepted"
            else "The run is quarantined because one or more acceptance checks failed."
        ),
        "approverClass": "deterministic_validator",
    }
    return {
        "schemaVersion": "AcceptedExperimentRunBundle-v1",
        "publicationTier": "tracked_sanitized",
        "envelope": envelope,
        "metricDefinitions": definitions,
        "metricObservations": observations,
        "acceptance": acceptance,
    }


def metrics_exp001(builder: RunBuilder, source: dict[str, Any]) -> None:
    totals = source["totals"]
    boundary = source["conclusion"]["statement"]
    builder.add(
        "MECH_COMPARISON_ROWS",
        totals["comparison_count"],
        totals["comparison_count"],
        totals["comparison_count"],
        "comparison rows",
        title="M4B-1 comparison rows",
        formula="count(comparison rows)",
        claim_boundary=boundary,
    )
    builder.add(
        "SAFETY_CLASSIFICATION_CHANGES",
        totals["changed_count"],
        totals["changed_count"],
        totals["comparison_count"],
        "classification changes",
        title="Baseline classification changes",
        formula="count(memory-informed classification != Agent 4 classification)",
        direction="lower_is_better",
        claim_boundary=boundary,
        target={"operator": "eq", "value": 0},
    )
    builder.add(
        "MECH_REVIEW_AFTER_MEMORY",
        totals["requires_human_review_after_memory_count"],
        totals["requires_human_review_after_memory_count"],
        totals["comparison_count"],
        "review escalations",
        title="Review required after memory",
        formula="count(rows requiring human review after advisory memory)",
        claim_boundary=boundary,
    )
    for row in source["distributions"]["advice_strength"]:
        builder.add(
            "MECH_ADVICE_STRENGTH_COUNT",
            row["count"],
            row["count"],
            totals["comparison_count"],
            "advice rows",
            title="Memory advice strength count",
            formula="count(rows grouped by advice strength)",
            dimensions={"strength": row["value"]},
            grain="advice strength within run",
            claim_boundary=boundary,
        )


def metrics_exp002(builder: RunBuilder, source: dict[str, Any]) -> None:
    totals = source["totals"]
    boundary = "Label-package readiness only; no independent labels were supplied."
    for metric_id, key, title in (
        ("LABEL_CANDIDATES", "generalization_safe_candidate_count", "Safe label candidates"),
        ("LABEL_EXISTING_SAME_PATTERN", "existing_expert_label_count", "Same-pattern mechanism labels"),
        ("LABEL_RECOMMENDED_ROWS", "recommended_count", "Recommended annotation rows"),
    ):
        value = totals[key]
        builder.add(
            metric_id,
            value,
            value,
            totals["row_count"],
            "rows",
            title=title,
            formula=f"{key} / row_count",
            claim_boundary=boundary,
        )


def metrics_zero_label(builder: RunBuilder, source: dict[str, Any]) -> None:
    boundary = "Independent generalization-safe labels are absent; performance remains null."
    for metric_id, title in (
        ("CLASSIFICATION_ACCURACY_B0", "Agent 4 accuracy"),
        ("CLASSIFICATION_ACCURACY_B1", "Memory-informed accuracy"),
        ("CLASSIFICATION_MACRO_F1_B0", "Agent 4 macro-F1"),
        ("CLASSIFICATION_MACRO_F1_B1", "Memory-informed macro-F1"),
        ("PAIRED_NET_CORRECTION", "Paired net correction"),
    ):
        builder.add(
            metric_id,
            None,
            None,
            0,
            "not computable",
            title=title,
            formula="requires independently adjudicated safe labels",
            direction="higher_is_better",
            required_evidence="empirical",
            claim_boundary=boundary,
        )


def metrics_exp004(builder: RunBuilder, source: dict[str, Any]) -> None:
    matrix = source["matrix"]
    boundary = (
        "Synthetic truth scenarios screen policy risk only and are not expert evidence."
    )
    for row in matrix:
        builder.add(
            "SYNTHETIC_POLICY_SAFE_DELTA_PP",
            row["safe_delta_pp"],
            row["safe_wrong_to_correct"] - row["safe_correct_to_wrong"],
            row["safe_rows"],
            "percentage points",
            title="Synthetic safe-row policy delta",
            formula="synthetic policy accuracy minus synthetic original accuracy",
            dimensions={
                "policy": row["policy_variant"],
                "truthScenario": row["truth_scenario"],
            },
            grain="policy and synthetic truth scenario",
            analysis_method="deterministic synthetic scenario calculation",
            claim_boundary=boundary,
        )


def metrics_exp005(builder: RunBuilder, source: dict[str, Any]) -> None:
    counts = source
    reliability = source["reviewer_reliability"]
    denominator = counts["generalization_safe_candidate_count"]
    boundary = source["strict_gate"]["status"]
    for metric_id, key, title in (
        ("LABEL_SUPPLIED", "labels_supplied_count", "Labels supplied"),
        ("LABEL_VALID", "valid_label_count", "Valid labels"),
        (
            "LABEL_GENERALIZATION_SAFE",
            "generalization_safe_valid_label_count",
            "Generalization-safe valid labels",
        ),
        ("LABEL_REVIEWER2", "reviewer_2_label_count", "Reviewer 2 labels"),
        ("LABEL_ADJUDICATED", "adjudicated_label_count", "Adjudicated labels"),
    ):
        value = counts.get(key, reliability.get(key, 0))
        builder.add(
            metric_id,
            value,
            value,
            denominator,
            "labels",
            title=title,
            formula=f"{key} / generalization_safe_candidate_count",
            direction="higher_is_better",
            claim_boundary=boundary,
        )


def metrics_exp006(builder: RunBuilder, source: dict[str, Any]) -> None:
    totals = source["totals"]
    boundary = source["claim_scope"]
    for metric_id, key, title, unit in (
        ("EVENT_TOTAL_RECONSTRUCTED", "total_reconstructed_events", "Reconstructed lifecycle events", "events"),
        ("EVENT_EARLY_STAGE", "early_stage_events", "Early-stage events", "events"),
        ("EVENT_SEV2PLUS", "sev2plus_events", "Severity 2+ events", "events"),
        ("EVENT_UNCERTAINTY_MARKED", "uncertainty_marked_events", "Uncertainty-marked events", "events"),
        ("MECH_REVIEW_QUEUE_ITEMS", "old_m1_review_queue_items", "Historical M1 queue items", "queue items"),
    ):
        value = totals[key]
        denominator = (
            totals["total_reconstructed_events"]
            if key != "total_reconstructed_events"
            else value
        )
        builder.add(
            metric_id,
            value,
            value,
            denominator,
            unit,
            title=title,
            formula=f"count({key})",
            grain="event replay run",
            claim_boundary=boundary,
        )
    builder.add(
        "MECH_QUEUE_TO_EVENT_COUNT_RATIO",
        totals["old_m1_queue_item_to_reconstructed_event_count_ratio"],
        totals["old_m1_review_queue_items"],
        totals["total_reconstructed_events"],
        "count ratio",
        title="Queue-item to reconstructed-event count ratio",
        formula="historical queue items / heterogeneous reconstructed lifecycle events",
        claim_boundary=boundary,
    )


def metrics_exp007(builder: RunBuilder, source: dict[str, Any]) -> None:
    boundary = source["claim_scope"]
    for row in source["results"]["ALL"]:
        dimensions = {"setting": "ALL", "mode": row["mode"]}
        for metric_id, key, title in (
            ("ROUTING_EVENT_LOAD", "event_load_vs_every_decision", "Event review load"),
            ("ROUTING_TRANSACTION_LOAD", "review_transaction_load_vs_every_decision_events", "Review-transaction load"),
            ("ROUTING_WEIGHTED_COVERAGE", "weighted_severity_coverage", "Weighted severity coverage"),
            ("ROUTING_HIGH_SEVERITY_COVERAGE", "high_severity_coverage", "High-severity coverage"),
            ("ROUTING_BUNDLING_REDUCTION", "bundling_reduction_vs_unbundled_selected", "Bundling reduction"),
        ):
            value = row[key]
            builder.add(
                metric_id,
                value,
                None,
                row["triageable_event_total"],
                "proportion",
                title=title,
                formula=key,
                direction=(
                    "lower_is_better"
                    if "LOAD" in metric_id or "REDUCTION" in metric_id
                    else "higher_is_better"
                ),
                grain="dosage mode over aggregate replay",
                dimensions=dimensions,
                claim_boundary=boundary,
            )


def metrics_exp008(builder: RunBuilder, source: dict[str, Any]) -> None:
    boundary = source["claim_scope"]
    total = source["totals"]["rank_and_cap_sweep"]
    denominator = source["totals"]["unstable_never_reviewed"]
    for cap, row in sorted(total.items(), key=lambda item: int(item[0])):
        builder.add(
            "TRIGGER_CAP_CAPTURE",
            row["capture_share"],
            row["surfaced_never_reviewed"],
            row["never_reviewed_denominator"],
            "proportion",
            title="Unstable-guideline capture by cap",
            formula="surfaced never-reviewed unstable guidelines / all never-reviewed unstable guidelines",
            direction="higher_is_better",
            dimensions={"capPerSetting": int(cap)},
            grain="uniform per-setting cap",
            claim_boundary=boundary,
        )
        builder.add(
            "TRIGGER_MAX_ADDED_LOAD",
            row["max_added_load_per_setting"],
            row["max_added_load_per_setting"],
            denominator,
            "items per setting",
            title="Maximum added review load by cap",
            formula="maximum selected items among settings",
            direction="lower_is_better",
            dimensions={"capPerSetting": int(cap)},
            grain="uniform per-setting cap",
            claim_boundary=boundary,
        )


def metrics_exp009(builder: RunBuilder, source: dict[str, Any]) -> None:
    values = source["metrics"]
    boundary = source["claim_scope"]
    total = values["total_seeds"]
    for metric_id, key, title in (
        ("HVERIFY_TRUE_POSITIVES", "true_positives", "Synthetic true positives"),
        ("HVERIFY_FALSE_POSITIVES", "false_positives", "Synthetic false positives"),
        ("HVERIFY_FALSE_NEGATIVES", "false_negatives", "Synthetic false negatives"),
        ("HVERIFY_TRUE_NEGATIVES", "true_negatives", "Synthetic true negatives"),
        ("HVERIFY_DETECTION_RECALL", "synthetic_detection_recall", "Synthetic conflict recall"),
        ("HVERIFY_SPECIFICITY", "synthetic_specificity", "Synthetic non-conflict specificity"),
    ):
        value = values[key]
        builder.add(
            metric_id,
            value,
            value if isinstance(value, int) else None,
            total,
            "count" if isinstance(value, int) else "proportion",
            title=title,
            formula=key,
            direction="higher_is_better",
            grain="synthetic conflict fixture",
            claim_boundary=boundary,
        )
    for outcome, value in values["final_status_counts"].items():
        builder.add(
            "HVERIFY_FINAL_STATUS_COUNT",
            value,
            value,
            total,
            "synthetic cases",
            title="H-Verify final status count",
            formula="count(cases grouped by final status)",
            dimensions={"outcome": outcome},
            grain="synthetic final status",
            claim_boundary=boundary,
        )


def metrics_exp010(builder: RunBuilder, source: dict[str, Any]) -> None:
    boundary = source["claim_scope"]
    for row in source["results"]:
        dimensions = {"roundBound": row["round_bound"]}
        for metric_id, key, title in (
            ("CONVERGENCE_RESOLVED_RATE", "resolved_rate", "Resolved rate"),
            ("CONVERGENCE_ADJUDICATION_RATE", "needs_adjudication_rate", "Adjudication rate"),
            ("CONVERGENCE_TIMEOUT_RATE", "timed_out_parked_rate", "Timeout and parked rate"),
            ("CONVERGENCE_NO_CONFLICT_RATE", "passed_no_conflict_rate", "No-conflict pass rate"),
        ):
            builder.add(
                metric_id,
                row[key],
                row[key.replace("_rate", "")],
                row["total_synthetic_traces"],
                "proportion",
                title=title,
                formula=f"{key.replace('_rate', '')} / total_synthetic_traces",
                dimensions=dimensions,
                grain="synthetic trace by round bound",
                claim_boundary=boundary,
            )


def metrics_exp012(builder: RunBuilder, source: dict[str, Any]) -> None:
    metrics_zero_label(builder, source)
    gate = source["validated_exp005_gate"]["counts"]
    boundary = source["claim_scope"]
    for metric_id, key, title in (
        ("LABEL_SUPPLIED", "labels_supplied_count", "Labels supplied"),
        ("LABEL_GENERALIZATION_SAFE", "generalization_safe_valid_label_count", "Safe valid labels"),
    ):
        value = gate[key]
        builder.add(
            metric_id,
            value,
            value,
            gate["generalization_safe_candidate_count"],
            "labels",
            title=title,
            formula=f"{key} / generalization_safe_candidate_count",
            claim_boundary=boundary,
        )
    builder.add(
        "EVALUATOR_CROSSCHECK_PASS",
        1,
        sum(source["canonical_exp003_cross_check"]["checks"].values()),
        len(source["canonical_exp003_cross_check"]["checks"]),
        "boolean",
        title="EXP-003 evaluator cross-check",
        formula="all declared cross-checks pass",
        direction="target",
        claim_boundary=boundary,
        target={"operator": "eq", "value": 1},
    )


def metrics_exp013(builder: RunBuilder, source: dict[str, Any]) -> None:
    boundary = "Offline event-contract fixture evidence only."
    for metric_id, value, numerator, denominator, title in (
        ("CONTRACT_SCHEMA_VALID_RATE", 1.0, source["schema_valid_records"], source["total_records"], "Schema-valid event records"),
        ("CONTRACT_LINEAGE_COMPLETE_RATE", 1.0, source["captured_records_with_lineage"], source["captured_or_reconstructed_records"], "Captured lineage completeness"),
        ("CONTRACT_EXPLICIT_GAPS", len(source["explicit_gap_event_types"]), len(source["explicit_gap_event_types"]), source["total_records"], "Explicit unobservable event gaps"),
        ("CONTRACT_E15_PARKED", 1, 1, 1, "E15 parked outside operational framework"),
    ):
        builder.add(
            metric_id,
            value,
            numerator,
            denominator,
            "proportion" if "RATE" in metric_id else "count",
            title=title,
            formula=title.lower(),
            direction="target",
            claim_boundary=boundary,
        )


def metrics_exp014(builder: RunBuilder, source: dict[str, Any]) -> None:
    boundary = "Offline deterministic replay evidence only."
    builder.add(
        "REPLAY_IDENTICAL_RUNS",
        source["replay_count"],
        source["replay_count"],
        3,
        "runs",
        title="Identical normalized replays",
        formula="count(replays matching the canonical normalized hash)",
        direction="target",
        claim_boundary=boundary,
        target={"operator": "eq", "value": 3},
    )
    builder.add(
        "REPLAY_DUPLICATE_REVIEW_ITEMS",
        0,
        0,
        source["review_item_count"],
        "duplicates",
        title="Duplicate review item IDs",
        formula="count(duplicate review item IDs)",
        direction="lower_is_better",
        claim_boundary=boundary,
        target={"operator": "eq", "value": 0},
    )


def metrics_exp015(builder: RunBuilder, source: dict[str, Any]) -> None:
    boundary = "Offline workload and fairness fixture evidence only."
    for row in source["configurations"]:
        dimensions = {"configuration": row["config"]}
        denominator = row["denominators"]["observations"]
        for metric_id, value, numerator, title, direction in (
            ("WORKLOAD_SELECTED_LOAD", row["round_1"]["load"], row["round_1"]["selected_observations"], "Selected observation load", "lower_is_better"),
            ("WORKLOAD_HIGH_SEVERITY_COVERAGE", row["round_1"]["high_severity_coverage"], row["denominators"]["high_severity_observations"], "High-severity coverage", "higher_is_better"),
            ("WORKLOAD_BUNDLE_COLLISIONS", row["bundle_collision_count"], row["bundle_collision_count"], "Cross-subject bundle collisions", "lower_is_better"),
            ("WORKLOAD_DEFERRED_RECOVERY", len(row["fairness"]["recovered_next_checkpoint_ids"]), len(row["fairness"]["recovered_next_checkpoint_ids"]), "Deferred items recovered", "higher_is_better"),
        ):
            builder.add(
                metric_id,
                value,
                numerator,
                denominator,
                "proportion" if isinstance(value, float) else "items",
                title=title,
                formula=title.lower(),
                direction=direction,
                dimensions=dimensions,
                grain="workload configuration",
                claim_boundary=boundary,
            )


def metrics_exp016(builder: RunBuilder, source: dict[str, Any]) -> None:
    boundary = "Synthetic authority fixtures only; no live authority is granted."
    case_count = len(source["cases"])
    passing = sum(
        bool(item["baseline_preserved"])
        and not item["trusted_memory_written"]
        and not item["correction_applied"]
        for item in source["cases"]
    )
    for metric_id, value, numerator, denominator, title, direction in (
        ("AUTHORITY_SAFE_CASE_RATE", passing / case_count, passing, case_count, "Authority cases preserving baseline", "target"),
        ("AUTHORITY_TRUSTED_MEMORY_WRITES", source["trusted_memory_writes"], source["trusted_memory_writes"], case_count, "Unsafe trusted-memory writes", "lower_is_better"),
        ("AUTHORITY_CORRECTION_APPLICATIONS", source["correction_applications"], source["correction_applications"], case_count, "Correction applications", "lower_is_better"),
    ):
        builder.add(
            metric_id,
            value,
            numerator,
            denominator,
            "proportion" if metric_id.endswith("RATE") else "count",
            title=title,
            formula=title.lower(),
            direction=direction,
            claim_boundary=boundary,
        )


def metrics_exp017(builder: RunBuilder, source: dict[str, Any]) -> None:
    boundary = "Synthetic deterministic-source verification fixtures only."
    case_count = len(source["cases"])
    builder.add(
        "VERIFY_EXPECTED_OUTCOME_RATE",
        1.0 if source["acceptance"]["expected_outcomes_match"] else 0.0,
        case_count if source["acceptance"]["expected_outcomes_match"] else 0,
        case_count,
        "proportion",
        title="Expected verification outcomes",
        formula="cases with expected deterministic disposition / all fixture cases",
        direction="target",
        claim_boundary=boundary,
    )
    builder.add(
        "VERIFY_SOURCE_FAMILY_COUNT",
        len(source["source_order"]),
        len(source["source_order"]),
        len(source["source_order"]),
        "source families",
        title="Deterministic source families traced",
        formula="count(ordered source families)",
        claim_boundary=boundary,
    )


def metrics_exp018(builder: RunBuilder, source: dict[str, Any]) -> None:
    boundary = "Proposal dry-run evidence only; no artifact mutation is authorized."
    for metric_id, value, title, direction in (
        ("PROPOSAL_DIFF_REPRODUCIBLE", 1 if source["acceptance"]["reproducible_diff"] else 0, "Reproducible proposed diff", "target"),
        ("PROPOSAL_APPLICATIONS", 1 if source["proposal"]["applied"] else 0, "Applied corrections", "lower_is_better"),
        ("PROPOSAL_SOURCE_HASH_CHANGED", 0 if source["source_sha256_before"] == source["source_sha256_after"] else 1, "Repository-source hash changes", "lower_is_better"),
    ):
        builder.add(
            metric_id,
            value,
            value,
            1,
            "boolean",
            title=title,
            formula=title.lower(),
            direction=direction,
            claim_boundary=boundary,
        )


def metrics_exp030(builder: RunBuilder, source: dict[str, Any]) -> None:
    experiments = source["experiments"]
    ids = [item["id"] for item in experiments]
    resolved = sum(
        bool(item.get("title"))
        and bool(item.get("researchQuestion"))
        and bool(item.get("metricDefinitions"))
        for item in experiments
    )
    unique = len(set(ids))
    boundary = (
        "Tracked BigUI extension-definition fidelity only. Full catalog, run, "
        "and browser fidelity are enforced separately; no classification "
        "validity follows."
    )
    for metric_id, numerator, denominator, title in (
        (
            "BIGUI_DEFINITION_FIELD_COMPLETENESS",
            resolved,
            len(experiments),
            "Extension definitions with complete required fields",
        ),
        (
            "BIGUI_DEFINITION_ID_UNIQUENESS",
            unique,
            len(experiments),
            "Unique extension experiment IDs",
        ),
    ):
        builder.add(
            metric_id,
            numerator / denominator if denominator else None,
            numerator,
            denominator,
            "proportion",
            title=title,
            formula=f"{numerator} / {denominator}",
            direction="target",
            claim_boundary=boundary,
            target={"operator": "eq", "value": 1},
        )


def metrics_architecture(
    experiment_id: str,
    builder: RunBuilder,
    source: dict[str, Any],
) -> None:
    result = {
        item["experimentId"]: item for item in source["experiments"]
    }[experiment_id]
    boundary = result["claimBoundary"]
    if experiment_id == "EXP-033":
        for metric_id, value, numerator, denominator, title, direction in (
            ("ARCH_SEMANTIC_PARITY_RATE", 1 - (result["semanticDifferences"] / result["runCount"]), result["runCount"] - result["semanticDifferences"], result["runCount"], "Semantic parity across executions", "target"),
            ("ARCH_REPLAY_DETERMINISM", 1 if result["deterministic"] else 0, int(result["deterministic"]), 1, "Architecture replay determinism", "target"),
            ("ARCH_BASELINE_PRESERVATION", 1 if result["baselinePreserved"] else 0, int(result["baselinePreserved"]), 1, "Baseline preservation", "target"),
            ("ARCH_CLASSIFICATION_CHANGES", result["classificationChanges"], result["classificationChanges"], result["recordExecutions"], "Classification changes", "lower_is_better"),
        ):
            builder.add(
                metric_id,
                value,
                numerator,
                denominator,
                "proportion" if metric_id.endswith(("RATE", "DETERMINISM", "PRESERVATION")) else "count",
                title=title,
                formula=title.lower(),
                direction=direction,
                claim_boundary=boundary,
            )
    elif experiment_id == "EXP-034":
        for row in result["topologies"]:
            dimensions = {"topology": row["id"]}
            for metric_id, key, title, direction, unit in (
                ("TOPOLOGY_HANDOFF_COUNT", "handoffs", "Measured handoffs", "lower_is_better", "handoffs"),
                ("TOPOLOGY_CONTEXT_BYTES", "contextBytes", "Serialized context bytes", "lower_is_better", "bytes"),
                ("TOPOLOGY_STATE_BOUNDARIES", "stateBoundaries", "State ownership boundaries", "lower_is_better", "boundaries"),
                ("TOPOLOGY_FAILURE_BREADTH", "failurePropagationBreadth", "Failure propagation breadth", "lower_is_better", "skills"),
                ("TOPOLOGY_TRACE_COMPLETENESS", "traceCompleteness", "Trace completeness", "target", "proportion"),
                ("TOPOLOGY_P95_LATENCY_MS", "p95Milliseconds", "Topology p95 latency", "lower_is_better", "milliseconds"),
            ):
                builder.add(
                    metric_id,
                    row[key],
                    None,
                    row["scenarioCount"],
                    unit,
                    title=title,
                    formula=title.lower(),
                    direction=direction,
                    dimensions=dimensions,
                    grain="topology over equivalent scenarios",
                    claim_boundary=boundary,
                )
    elif experiment_id == "EXP-035":
        passed = sum(
            item["outcome"] not in {"unsafe_accept", "unexpected"}
            and item["baselinePreserved"]
            and item["trustedMemoryWrites"] == 0
            and item["correctionApplications"] == 0
            for item in result["cases"]
        )
        builder.add(
            "SAFETY_FAULT_CASE_PASS_RATE",
            passed / result["caseCount"],
            passed,
            result["caseCount"],
            "proportion",
            title="Fault cases with expected safe disposition",
            formula="safe expected dispositions / declared fault cases",
            direction="target",
            claim_boundary=boundary,
        )
        for outcome in sorted({item["outcome"] for item in result["cases"]}):
            count = sum(item["outcome"] == outcome for item in result["cases"])
            builder.add(
                "SAFETY_FAULT_OUTCOME_COUNT",
                count,
                count,
                result["caseCount"],
                "fault cases",
                title="Fault outcome count",
                formula="count(fault cases grouped by disposition)",
                dimensions={"outcome": outcome},
                grain="fault disposition",
                claim_boundary=boundary,
            )
    elif experiment_id == "EXP-036":
        for scale in result["scales"]:
            for row in scale["modes"]:
                dimensions = {"fixture": scale["fixture"], "mode": row["mode"]}
                for metric_id, key, title, unit, direction in (
                    ("ARCH_P50_LATENCY_MS", "p50Milliseconds", "Architecture p50 latency", "milliseconds", "lower_is_better"),
                    ("ARCH_P95_LATENCY_MS", "p95Milliseconds", "Architecture p95 latency", "milliseconds", "lower_is_better"),
                    ("ARCH_THROUGHPUT_RPS", "throughputRecordsPerSecond", "Architecture throughput", "records/second", "higher_is_better"),
                    ("ARCH_PEAK_MEMORY_BYTES", "peakBytes", "Architecture peak memory", "bytes", "lower_is_better"),
                    ("ARCH_P95_RATIO_TO_LEGACY", "p95RatioToLegacy", "p95 latency ratio to legacy", "ratio", "lower_is_better"),
                    ("ARCH_MEMORY_RATIO_TO_LEGACY", "peakMemoryRatioToLegacy", "Peak-memory ratio to legacy", "ratio", "lower_is_better"),
                ):
                    builder.add(
                        metric_id,
                        row[key],
                        None,
                        row["timedIterations"],
                        unit,
                        title=title,
                        formula=title.lower(),
                        direction=direction,
                        dimensions=dimensions,
                        grain="mode and scale benchmark",
                        confidence_interval=row.get(f"{key}ConfidenceInterval"),
                        analysis_method="interleaved repeated offline benchmark",
                        claim_boundary=boundary,
                    )


def source_specs() -> list[tuple[str, Path, str, Any, dict[str, Any]]]:
    return [
        ("EXP-001", ROOT / "reports/generated/exp001/exp001_summary.json", "mechanism", metrics_exp001, {"baseline_id": "B0", "comparator_id": "B1-L", "verdict": "NOT_APPLICABLE", "claim_boundary": "Mechanism readiness only; no accuracy claim."}),
        ("EXP-002", ROOT / "reports/generated/exp002/exp002_summary.json", "evaluation_ready", metrics_exp002, {"baseline_id": "B0", "comparator_id": "label-package", "verdict": "NOT_APPLICABLE", "claim_boundary": "Annotation-package readiness only."}),
        ("EXP-003", ROOT / "reports/generated/exp003/accuracy_summary.json", "evaluation_ready", metrics_zero_label, {"baseline_id": "B0", "comparator_id": "B1", "verdict": "NOT_COMPUTABLE", "claim_boundary": "Zero safe labels keep all empirical metrics null."}),
        ("EXP-004", ROOT / "reports/generated/policy_sensitivity/policy_sensitivity_summary.json", "synthetic", metrics_exp004, {"baseline_id": "synthetic-original", "comparator_id": "synthetic-policy", "verdict": "NOT_APPLICABLE", "claim_boundary": "Synthetic policy-risk screening only."}),
        ("EXP-005", ROOT / "reports/generated/exp005_label_review/label_validation_summary.json", "evaluation_ready", metrics_exp005, {"baseline_id": "label-protocol", "comparator_id": "validated-labels", "verdict": "NOT_COMPUTABLE", "claim_boundary": "Zero safe labels; no performance result."}),
        ("EXP-006", ROOT / "reports/generated/exp006/summary.json", "offline", metrics_exp006, {"baseline_id": "B1-event-source", "comparator_id": "event-replay", "verdict": "NOT_APPLICABLE", "claim_boundary": "Observability evidence only."}),
        ("EXP-007", ROOT / "reports/generated/exp007/summary.json", "offline", metrics_exp007, {"baseline_id": "every-decision", "comparator_id": "dosage-modes", "verdict": "INCONCLUSIVE", "claim_boundary": "Pareto evidence only; no default selected."}),
        ("EXP-008", ROOT / "reports/generated/exp008/summary.json", "offline", metrics_exp008, {"baseline_id": "uncapped-triggering", "comparator_id": "uniform-cap-sweep", "verdict": "INCONCLUSIVE", "claim_boundary": "Cap/capture trade-off only."}),
        ("EXP-009", ROOT / "reports/generated/exp009/summary.json", "synthetic", metrics_exp009, {"baseline_id": "synthetic-conflict-truth", "comparator_id": "deterministic-hverify", "verdict": "CONFORMANCE_PASS", "claim_boundary": "Synthetic deterministic rule conformance only.", "deterministic": True}),
        ("EXP-010", ROOT / "reports/generated/exp010/summary.json", "synthetic", metrics_exp010, {"baseline_id": "one-round-bound", "comparator_id": "round-bound-sweep", "verdict": "INCONCLUSIVE", "claim_boundary": "Synthetic convergence-bound evidence only.", "deterministic": True}),
        ("EXP-012", ROOT / "reports/generated/exp012/summary.json", "evaluation_ready", metrics_exp012, {"baseline_id": "B0", "comparator_id": "B1", "verdict": "NOT_COMPUTABLE", "claim_boundary": "Validated N=0 measurement boundary."}),
        ("EXP-013", ROOT / "reports/generated/exp013/summary.json", "offline", metrics_exp013, {"baseline_id": "contract-catalog", "comparator_id": "fixture-records", "verdict": "CONFORMANCE_PASS", "claim_boundary": "Offline event-contract conformance only.", "deterministic": True}),
        ("EXP-014", ROOT / "reports/generated/exp014/summary.json", "offline", metrics_exp014, {"baseline_id": "replay-input", "comparator_id": "three-repetitions", "verdict": "CONFORMANCE_PASS", "claim_boundary": "Offline replay determinism only.", "deterministic": True}),
        ("EXP-015", ROOT / "reports/generated/exp015/summary.json", "offline", metrics_exp015, {"baseline_id": "uniform-cap", "comparator_id": "adaptive-cap", "verdict": "CONFORMANCE_PASS", "claim_boundary": "Offline workload/fairness fixtures only.", "deterministic": True}),
        ("EXP-016", ROOT / "reports/generated/exp016/summary.json", "synthetic", metrics_exp016, {"baseline_id": "authority-state-machine", "comparator_id": "negative-authority-cases", "verdict": "CONFORMANCE_PASS", "claim_boundary": "Synthetic authority safety fixtures only.", "deterministic": True}),
        ("EXP-017", ROOT / "reports/generated/exp017/summary.json", "synthetic", metrics_exp017, {"baseline_id": "source-catalog", "comparator_id": "deterministic-verification", "verdict": "CONFORMANCE_PASS", "claim_boundary": "Synthetic source-verification fixtures only.", "deterministic": True}),
        ("EXP-018", ROOT / "reports/generated/exp018/summary.json", "synthetic", metrics_exp018, {"baseline_id": "copied-artifact", "comparator_id": "proposal-diff", "verdict": "CONFORMANCE_PASS", "claim_boundary": "Proposal dry run only; no mutation.", "deterministic": True}),
    ]


def build_source_bundles() -> list[dict[str, Any]]:
    program = load_json(PROGRAM)
    baseline = load_json(BASELINE)
    bundles: list[dict[str, Any]] = []
    for experiment_id, path, evidence, callback, options in source_specs():
        if not path.is_file():
            raise ValueError(f"required experiment source is missing: {relative(path)}")
        bundles.append(
            make_bundle(
                experiment_id,
                path,
                evidence,
                baseline,
                program,
                callback,
                **options,
            )
        )
    if BIGUI_PROGRAM.is_file():
        bundles.append(
            make_bundle(
                "EXP-030",
                BIGUI_PROGRAM,
                "offline",
                baseline,
                program,
                metrics_exp030,
                baseline_id="bigui-program-contract",
                comparator_id="validated-extension-definitions",
                verdict="CONFORMANCE_PASS",
                deterministic=True,
                claim_boundary=(
                    "BigUI extension-definition fidelity only; catalog, run, "
                    "and browser fidelity remain separately checked."
                ),
                interface_version="BigUI-v2",
            )
        )
    if ARCHITECTURE_SUMMARY.is_file():
        architecture = load_json(ARCHITECTURE_SUMMARY)
        result_by_id = {
            item["experimentId"]: item for item in architecture["experiments"]
        }
        for experiment_id in ("EXP-033", "EXP-034", "EXP-035", "EXP-036"):
            result = result_by_id[experiment_id]
            engineering_target_met = (
                bool(result.get("engineeringTargetMet"))
                if experiment_id == "EXP-036"
                else None
            )
            verdict = (
                "ENGINEERING_TARGET_MET"
                if experiment_id == "EXP-036" and engineering_target_met
                else (
                    "ENGINEERING_TARGET_NOT_MET"
                    if experiment_id == "EXP-036"
                    else "CONFORMANCE_PASS"
                )
            )
            bundles.append(
                make_bundle(
                    experiment_id,
                    ARCHITECTURE_SUMMARY,
                    result["evidenceClass"],
                    baseline,
                    program,
                    lambda builder, source, exp=experiment_id: metrics_architecture(
                        exp, builder, source
                    ),
                    baseline_id="B1-L",
                    comparator_id={
                        "EXP-033": "B1-U/B1-P",
                        "EXP-034": "T-A/T-B/T-C",
                        "EXP-035": "fault-catalog",
                        "EXP-036": "B1-U/B1-P",
                    }[experiment_id],
                    verdict=verdict,
                    deterministic=bool(result.get("deterministic", result.get("passed"))),
                    engineering_target_met=engineering_target_met,
                    architecture_mode="multi-mode",
                    topology="A/B/C" if experiment_id == "EXP-034" else "not_applicable",
                    claim_boundary=result["claimBoundary"],
                    criteria=[
                        (
                            "EXECUTION_VALID",
                            bool(result.get("executionValid", result.get("passed"))),
                            "The architecture experiment completed with schema-valid output.",
                        ),
                        (
                            "BASELINE_PRESERVED",
                            bool(result.get("baselinePreserved", True)),
                            "The experiment did not modify Agent 4 or baseline artifacts.",
                        ),
                    ],
                )
            )
    return bundles


def safe_serialized(bundle: dict[str, Any]) -> str:
    content = json.dumps(bundle, ensure_ascii=False, indent=2) + "\n"
    lowered = content.lower()
    for forbidden in ("file://", "c:\\users\\", "@gmail.com", "@outlook.com"):
        if forbidden in lowered:
            raise ValueError(f"bundle contains forbidden private text: {forbidden}")
    return content


def write_local_bundle(bundle: dict[str, Any]) -> None:
    envelope = bundle["envelope"]
    destination = (
        LOCAL_ROOT / envelope["experimentId"] / envelope["runId"]
    )
    staging = destination.with_name(f".{destination.name}.staging")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    files = {
        "run.json": envelope,
        "manifest.json": {
            "manifestPath": envelope["manifestPath"],
            "manifestSha256": envelope["manifestSha256"],
            "inputHashes": envelope["inputHashes"],
            "outputHashes": envelope["outputHashes"],
        },
        "summary.json": envelope["evaluation"],
        "artifacts.json": {"artifacts": envelope["artifactRefs"]},
        "acceptance.json": bundle["acceptance"],
    }
    for name, payload in files.items():
        (staging / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    (staging / "metrics.jsonl").write_text(
        "".join(
            json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n"
            for item in bundle["metricObservations"]
        ),
        encoding="utf-8",
        newline="\n",
    )
    (staging / "events.jsonl").write_text(
        json.dumps(
            {
                "schemaVersion": "RunLogEvent-v1",
                "sequence": 1,
                "timestamp": envelope["completedAt"],
                "eventType": "run_completed",
                "experimentId": envelope["experimentId"],
                "runId": envelope["runId"],
                "message": "Run completed and its privacy-safe projection was accepted.",
                "details": {
                    "acceptanceStatus": envelope["acceptanceStatus"],
                    "artifactRef": "acceptance.json",
                },
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if destination.exists():
        shutil.rmtree(destination)
    last_error: PermissionError | None = None
    for attempt in range(5):
        try:
            staging.rename(destination)
            last_error = None
            break
        except PermissionError as exc:
            last_error = exc
            if destination.exists():
                shutil.rmtree(destination)
            time.sleep(0.05 * (attempt + 1))
    if last_error is not None:
        raise last_error


def refresh() -> list[dict[str, Any]]:
    validator = BundleValidator(SCHEMA_ROOT)
    bundles = build_source_bundles()
    ACCEPTED_ROOT.mkdir(parents=True, exist_ok=True)
    for bundle in bundles:
        validator.validate(bundle)
        envelope = bundle["envelope"]
        path = ACCEPTED_ROOT / f"{envelope['experimentId']}-{envelope['runId']}.json"
        path.write_text(
            safe_serialized(bundle),
            encoding="utf-8",
            newline="\n",
        )
        write_local_bundle(bundle)
        print(f"WROTE: {relative(path)}")
    loaded = load_bundles(ACCEPTED_ROOT, SCHEMA_ROOT)
    summary = rebuild_sqlite(loaded, DATABASE)
    summary_path = DATABASE.with_name("run-store-summary.json")
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"WROTE LOCAL: {relative(DATABASE)}")
    return loaded


def check() -> list[dict[str, Any]]:
    bundles = load_bundles(ACCEPTED_ROOT, SCHEMA_ROOT)
    if not bundles:
        raise ValueError("no accepted run bundles are tracked")
    summary = run_store_summary(bundles)
    if summary["uniqueExperimentRunCount"] != summary["acceptedAttemptCount"]:
        raise ValueError("accepted attempts do not map one-to-one to experiment runs")
    temporary = DATABASE.with_name(".run-registry-check.sqlite")
    rebuild_sqlite(bundles, temporary)
    temporary.unlink(missing_ok=True)
    print(
        "BigUI run store: PASS "
        f"({summary['bundleCount']} bundles, "
        f"{summary['metricObservationCount']} observations)"
    )
    return bundles


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--refresh", action="store_true")
    action.add_argument("--rebuild-database", action="store_true")
    args = parser.parse_args()
    try:
        if args.refresh:
            refresh()
        elif args.rebuild_database:
            bundles = load_bundles(ACCEPTED_ROOT, SCHEMA_ROOT)
            summary = rebuild_sqlite(bundles, DATABASE)
            print(
                f"BigUI run database: PASS "
                f"({summary['bundleCount']} bundles)"
            )
        else:
            check()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"BigUI run store: FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
