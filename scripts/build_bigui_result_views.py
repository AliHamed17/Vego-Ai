#!/usr/bin/env python3
"""Build evidence-honest experiment result views for the VEGO-AI BigUI."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import jsonschema
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
BIGUI = ROOT / "docs" / "research" / "bigui"
CATALOG_PATH = BIGUI / "experiment-catalog-snapshot-v1.json"
BENCHMARK_PATH = BIGUI / "experiment-benchmark-snapshot-v1.json"
PAPER_PATH = BIGUI / "paper-baseline-snapshot-v1.json"
OUTPUT_PATH = BIGUI / "experiment-result-views-v1.json"

REQUIRED_COMPARISON_FIELDS = (
    "datasetHash",
    "partitionHash",
    "baselineRevision",
    "policyVersion",
    "promptVersion",
    "modelIdentifier",
    "metricSchemaVersion",
    "labelEligibility",
    "leakageClass",
    "evidenceClass",
)
EMPIRICAL_PREFIXES = ("CLASSIFICATION_", "PAIRED_")

VISUAL_FAMILY = {
    0: "matrix",
    1: "funnel",
    2: "funnel",
    3: "empty_state",
    4: "heatmap",
    5: "funnel",
    6: "bar",
    7: "dot",
    8: "dot",
    9: "matrix",
    10: "grouped_bar",
    11: "empty_state",
    12: "funnel",
    13: "funnel",
    14: "timeline",
    15: "small_multiples",
    16: "matrix",
    17: "matrix",
    18: "timeline",
    19: "funnel",
    20: "matrix",
    21: "bar",
    22: "small_multiples",
    23: "dot",
    24: "matrix",
    25: "dot",
    26: "small_multiples",
    27: "small_multiples",
    28: "timeline",
    29: "dot",
    30: "matrix",
    31: "bar",
    32: "grouped_bar",
    33: "matrix",
    34: "small_multiples",
    35: "heatmap",
    36: "grouped_bar",
    37: "grouped_bar",
    38: "small_multiples",
    39: "matrix",
    40: "heatmap",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path.relative_to(ROOT)}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_id(prefix: str, value: Any, length: int) -> str:
    encoded = json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return f"{prefix}{hashlib.sha256(encoded).hexdigest()[:length]}"


def validator(schema_name: str) -> jsonschema.Draft202012Validator:
    schema = load_json(SCHEMAS / schema_name)
    registry = Registry()
    for path in SCHEMAS.glob("*.schema.json"):
        candidate = load_json(path)
        if candidate.get("$id"):
            registry = registry.with_resource(
                candidate["$id"], Resource.from_contents(candidate)
            )
    return jsonschema.Draft202012Validator(
        schema,
        registry=registry,
        format_checker=jsonschema.FormatChecker(),
    )


def observation_key(observation: dict[str, Any]) -> tuple[str, str]:
    dimensions = json.dumps(
        observation.get("dimensions") or {},
        sort_keys=True,
        separators=(",", ":"),
    )
    return observation["metricId"], dimensions


def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def comparison_mismatches(
    left: dict[str, Any], right: dict[str, Any]
) -> list[dict[str, Any]]:
    mismatches: list[dict[str, Any]] = []
    for field in REQUIRED_COMPARISON_FIELDS:
        left_value = left.get(field)
        right_value = right.get(field)
        if left_value is None or right_value is None or left_value != right_value:
            mismatches.append(
                {"field": field, "left": left_value, "right": right_value}
            )
    return mismatches


def metric_target_status(
    evaluation: dict[str, Any], metric_id: str
) -> tuple[str | None, list[dict[str, str]]]:
    signals = [
        item
        for item in evaluation.get("engineeringSignals", [])
        if item["metricId"] == metric_id
    ]
    assessed = [item for item in signals if item["status"] in {"met", "missed"}]
    guardrails = [
        {
            "id": f"{metric_id}:{index + 1}",
            "status": item["status"],
            "detail": (
                f"{item.get('target') or 'descriptive target'}; "
                f"dimensions={json.dumps(item.get('dimensions') or {}, sort_keys=True)}"
            ),
        }
        for index, item in enumerate(assessed)
    ]
    statuses = {item["status"] for item in assessed}
    if statuses == {"met"}:
        return "Target met", guardrails
    if "missed" in statuses and "met" in statuses:
        return "Mixed", guardrails
    if statuses == {"missed"}:
        return "Regressed", guardrails
    return None, guardrails


def assessment_for_metric(
    experiment_id: str,
    metric_id: str,
    current_bundle: dict[str, Any] | None,
    previous_bundle: dict[str, Any] | None,
    evaluation: dict[str, Any],
) -> dict[str, Any]:
    payload_seed = {
        "experimentId": experiment_id,
        "metricId": metric_id,
        "left": (
            previous_bundle["envelope"]["runId"] if previous_bundle else None
        ),
        "right": current_bundle["envelope"]["runId"] if current_bundle else None,
    }
    base = {
        "schemaVersion": "ProgressAssessment-v1",
        "assessmentId": stable_id("PA-", payload_seed, 16).upper(),
        "experimentId": experiment_id,
        "metricId": metric_id,
        "comparisonFamily": "none",
        "leftRunId": (
            previous_bundle["envelope"]["runId"] if previous_bundle else None
        ),
        "rightRunId": (
            current_bundle["envelope"]["runId"] if current_bundle else None
        ),
        "comparabilityVerdict": "Not measured",
        "mismatches": [],
        "absoluteDelta": None,
        "relativeDelta": None,
        "confidenceInterval": None,
        "guardrails": [],
        "status": "Not measured",
        "explanation": "No accepted non-null observation is available.",
    }
    if current_bundle is None:
        return base

    current_observations = [
        item
        for item in current_bundle["metricObservations"]
        if item["metricId"] == metric_id
    ]
    current_numeric = [
        item for item in current_observations if finite_number(item.get("value"))
    ]
    target_status, guardrails = metric_target_status(evaluation, metric_id)
    base["guardrails"] = guardrails
    if not current_numeric:
        base["explanation"] = (
            "The metric is declared and observed, but its accepted value is null."
            if current_observations
            else "The accepted run contains no observation for this declared metric."
        )
        return base

    if previous_bundle is None:
        base["comparisonFamily"] = "guardrail"
        base["comparabilityVerdict"] = "Eligible"
        if target_status is not None:
            base["status"] = target_status
            base["explanation"] = (
                "The current accepted run was assessed against its declared "
                "engineering guardrail; no prior comparable run is required."
            )
        else:
            base["status"] = "Not measured"
            base["comparabilityVerdict"] = "Not measured"
            base["explanation"] = (
                "A non-null current result exists, but no prior comparable run "
                "or explicit guardrail is available for a progress delta."
            )
        return base

    base["comparisonFamily"] = "historical_run"
    left_context = previous_bundle["envelope"]["comparisonContext"]
    right_context = current_bundle["envelope"]["comparisonContext"]
    mismatches = comparison_mismatches(left_context, right_context)
    if mismatches:
        base["comparabilityVerdict"] = "Not directly comparable"
        base["mismatches"] = mismatches
        base["status"] = "Not directly comparable"
        base["explanation"] = (
            "The runs differ on one or more required comparison fields; no "
            "delta is calculated."
        )
        return base

    previous_index = {
        observation_key(item): item
        for item in previous_bundle["metricObservations"]
        if item["metricId"] == metric_id and finite_number(item.get("value"))
    }
    pairs = [
        (previous_index[observation_key(item)], item)
        for item in current_numeric
        if observation_key(item) in previous_index
    ]
    if not pairs:
        base["explanation"] = (
            "The run contexts match, but no non-null observations share the "
            "same metric grain and dimensions."
        )
        return base

    left_mean = sum(float(left["value"]) for left, _ in pairs) / len(pairs)
    right_mean = sum(float(right["value"]) for _, right in pairs) / len(pairs)
    delta = right_mean - left_mean
    relative = delta / abs(left_mean) if left_mean else None
    direction = current_numeric[0].get("direction")
    if target_status in {"Target met", "Mixed", "Regressed"}:
        status = target_status
    elif math.isclose(delta, 0.0, abs_tol=1e-12):
        status = "Unchanged"
    elif direction == "lower_is_better":
        status = "Improved" if delta < 0 else "Regressed"
    elif direction == "higher_is_better":
        status = "Improved" if delta > 0 else "Regressed"
    else:
        status = "Mixed"
    intervals = [
        item.get("confidenceInterval")
        for item in current_numeric
        if item.get("confidenceInterval") is not None
    ]
    base.update(
        {
            "comparabilityVerdict": "Eligible",
            "absoluteDelta": delta,
            "relativeDelta": relative,
            "confidenceInterval": intervals[0] if len(intervals) == 1 else None,
            "status": status,
            "explanation": (
                f"Compared {len(pairs)} matched observation grain(s) from the "
                "two accepted runs. A progress label is not an accuracy claim."
            ),
        }
    )
    return base


def paper_mappings(paper: dict[str, Any]) -> list[dict[str, Any]]:
    source = {
        "path": "Variability_MAS4MODELS2026_Mar28_IRB2איריס (1).pdf",
        "sha256": paper["source"]["sha256"],
    }
    common_boundary = (
        "Paper phases remain separate measurement lanes. Direct H-layer "
        "classification comparison requires the same independently adjudicated cohort."
    )
    rows = [
        (
            "A",
            "RQ1",
            "Language Advisor precision, recall, F1, and run agreement",
            f"{paper['evaluationScope']['caseModelTotal']} models; three runs per setting",
            paper["phaseA"]["page"],
            None,
            "Phase A evaluates language-template stability, not variability-classification accuracy.",
        ),
        (
            "B",
            "RQ2",
            "Domain Advisor guideline-quality scores",
            "Four education settings",
            paper["phaseB"]["page"],
            None,
            "Phase B guideline scores use a different construct, cohort, and metric grain.",
        ),
        (
            "C",
            "RQ3",
            "Model Inspector compliance vectors and uncovered audits",
            f"{paper['phaseC']['expertSampleSize']} expert-reviewed models",
            paper["phaseC"]["page"],
            None,
            "Phase C audits model compliance and cannot benchmark H-layer classification.",
        ),
        (
            "D",
            "RQ4",
            "Qualitative variability pattern classification",
            (
                f"{paper['phaseD']['patternTotal']} patterns across "
                f"{paper['evaluationScope']['caseModelTotal']} models"
            ),
            paper["phaseD"]["page"],
            "Paper-aligned frozen Agent 4 B0 counts",
            "Phase D has qualitative author assessment and no independent quantitative classification benchmark.",
        ),
    ]
    return [
        {
            "schemaVersion": "PaperMetricMapping-v1",
            "mappingId": f"PAPER-MAP-{phase}",
            "paperPhase": phase,
            "paperResearchQuestion": rq,
            "paperMetric": metric,
            "paperCohort": cohort,
            "extractionSource": {**source, "page": page},
            "currentEquivalent": equivalent,
            "directComparisonEligible": False,
            "incompatibilityReason": reason,
            "claimBoundary": common_boundary,
        }
        for phase, rq, metric, cohort, page, equivalent, reason in rows
    ]


def source_rows(
    observations: list[dict[str, Any]],
    artifact_links: list[str],
) -> list[dict[str, str]]:
    rows = {
        (item["sourcePath"], item["sourceSha256"])
        for item in observations
        if item.get("sourcePath") and item.get("sourceSha256")
    }
    if not rows:
        for raw_path in artifact_links:
            path = ROOT / raw_path
            if path.is_file():
                rows.add((raw_path.replace("\\", "/"), sha256(path)))
    return [
        {"path": path, "sha256": digest}
        for path, digest in sorted(rows)
    ]


def visualization_specs(
    experiment: dict[str, Any],
    observations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    experiment_id = experiment["id"]
    number = int(experiment_id[-3:])
    non_null_by_metric: dict[str, list[dict[str, Any]]] = defaultdict(list)
    observed_by_metric: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for observation in observations:
        observed_by_metric[observation["metricId"]].append(observation)
        if finite_number(observation.get("value")):
            non_null_by_metric[observation["metricId"]].append(observation)

    specs: list[dict[str, Any]] = []
    preferred_family = VISUAL_FAMILY[number]
    for metric_id in experiment["metricDefinitions"]:
        metric_observations = non_null_by_metric.get(metric_id, [])
        if not metric_observations:
            continue
        family = preferred_family
        if family == "empty_state":
            family = "metric_card"
        if len(metric_observations) == 1 and family not in {"matrix", "funnel", "timeline"}:
            family = "metric_card"
        denominators = {
            item.get("denominator")
            for item in metric_observations
            if item.get("denominator") is not None
        }
        denominator: int | float | str | None
        if len(denominators) == 1:
            denominator = next(iter(denominators))
        elif denominators:
            denominator = "varies by plotted observation"
        else:
            denominator = None
        sources = source_rows(metric_observations, [])
        dates = sorted(
            {
                item["observationDate"]
                for item in metric_observations
                if item.get("observationDate")
            }
        )
        dimensions = sorted(
            {
                key
                for item in metric_observations
                for key in (item.get("dimensions") or {})
            }
        )
        spec_seed = {
            "experimentId": experiment_id,
            "metricId": metric_id,
            "observationIds": [
                item["observationId"] for item in metric_observations
            ],
        }
        specs.append(
            {
                "schemaVersion": "VisualizationSpec-v1",
                "visualizationId": stable_id(
                    f"VIS-{experiment_id}-", spec_seed, 12
                ).upper(),
                "experimentId": experiment_id,
                "title": metric_id.replace("_", " ").title(),
                "analyticalQuestion": (
                    f"What does the latest accepted {metric_id} evidence show "
                    f"for {experiment_id}?"
                ),
                "chartFamily": family,
                "metricIds": [metric_id],
                "observationIds": [
                    item["observationId"] for item in metric_observations
                ],
                "fieldBindings": {
                    "x": f"dimensions.{dimensions[0]}" if dimensions else "metricId",
                    "y": "value",
                    **(
                        {"group": f"dimensions.{dimensions[1]}"}
                        if len(dimensions) > 1
                        else {}
                    ),
                },
                "denominator": denominator,
                "cohort": metric_observations[0].get("cohortHash") or "not recorded",
                "sources": sources,
                "observationDate": dates[-1] if dates else None,
                "evidenceClass": metric_observations[0]["evidenceClass"],
                "comparisonBasis": (
                    "Latest accepted run; dimensions are shown separately and "
                    "different metric units are never combined."
                ),
                "claimBoundary": experiment["claimBoundary"],
                "emptyState": None,
                "accessibleDescription": (
                    f"{family.replace('_', ' ').title()} for {metric_id} with "
                    f"{len(metric_observations)} non-null observation(s). "
                    f"Denominator: {denominator if denominator is not None else 'not applicable'}."
                ),
            }
        )

    null_metrics = sorted(
        metric_id
        for metric_id in experiment["metricDefinitions"]
        if observed_by_metric.get(metric_id) and not non_null_by_metric.get(metric_id)
    )
    if null_metrics:
        seed = {"experimentId": experiment_id, "nullMetrics": null_metrics}
        specs.append(
            {
                "schemaVersion": "VisualizationSpec-v1",
                "visualizationId": stable_id(
                    f"VIS-{experiment_id}-", seed, 12
                ).upper(),
                "experimentId": experiment_id,
                "title": "Metrics awaiting admissible evidence",
                "analyticalQuestion": "Which declared results are still not computable?",
                "chartFamily": "empty_state",
                "metricIds": null_metrics,
                "observationIds": [],
                "fieldBindings": {},
                "denominator": 0,
                "cohort": "No eligible independent cohort",
                "sources": source_rows(
                    [
                        item
                        for metric_id in null_metrics
                        for item in observed_by_metric[metric_id]
                    ],
                    [],
                ),
                "observationDate": None,
                "evidenceClass": experiment["evidenceClass"],
                "comparisonBasis": "No delta is permitted while accepted values are null.",
                "claimBoundary": experiment["claimBoundary"],
                "emptyState": (
                    "Not computable from the current evidence: "
                    + ", ".join(null_metrics)
                    + "."
                ),
                "accessibleDescription": (
                    "Empty result panel. The listed metrics are declared and "
                    "observed as null, so no zero value or improvement is shown."
                ),
            }
        )

    if not specs:
        seed = {"experimentId": experiment_id, "empty": True}
        specs.append(
            {
                "schemaVersion": "VisualizationSpec-v1",
                "visualizationId": stable_id(
                    f"VIS-{experiment_id}-", seed, 12
                ).upper(),
                "experimentId": experiment_id,
                "title": "No accepted measured result",
                "analyticalQuestion": "What evidence is currently available?",
                "chartFamily": "empty_state",
                "metricIds": list(experiment["metricDefinitions"]),
                "observationIds": [],
                "fieldBindings": {},
                "denominator": None,
                "cohort": "No accepted measured cohort",
                "sources": source_rows([], experiment["artifactLinks"]),
                "observationDate": None,
                "evidenceClass": experiment["evidenceClass"],
                "comparisonBasis": "Protocol or gate state only.",
                "claimBoundary": experiment["claimBoundary"],
                "emptyState": (
                    "This experiment has no accepted non-null result. "
                    f"Current status: {experiment['status']}."
                ),
                "accessibleDescription": (
                    "Empty result panel explaining that no measured result is "
                    "available and no value has been invented."
                ),
            }
        )
    return specs


def measurement_state(
    experiment: dict[str, Any],
    observations: list[dict[str, Any]],
    assessments: list[dict[str, Any]],
    safe_labels: int,
) -> dict[str, Any]:
    declared = set(experiment["metricDefinitions"])
    observed = {
        item["metricId"] for item in observations if item["metricId"] in declared
    }
    non_null_observations = [
        item
        for item in observations
        if item["metricId"] in declared and item.get("value") is not None
    ]
    non_null = {item["metricId"] for item in non_null_observations}
    null_metric_ids = sorted(observed - non_null)
    if not declared:
        status = "no_metrics_declared"
    elif not observations:
        status = "protocol_only"
    elif not non_null:
        status = "observed_null"
    elif non_null != declared:
        status = "measured_partial"
    else:
        status = "measured_complete"
    comparable = {
        item["metricId"]
        for item in assessments
        if item["comparabilityVerdict"] == "Eligible"
        and item["status"] not in {"Not measured", "Not eligible"}
    }
    claim_eligible = {
        metric_id
        for metric_id in non_null
        if not metric_id.startswith(EMPIRICAL_PREFIXES) or safe_labels >= 20
    }
    return {
        "declaredMetricCount": len(declared),
        "observedMetricCount": len(observed),
        "nonNullObservationCount": len(non_null_observations),
        "nonNullMetricCount": len(non_null),
        "nullMetricIds": null_metric_ids,
        "comparisonEligibleMetricCount": len(comparable),
        "claimEligibleMetricCount": len(claim_eligible),
        "status": status,
    }


def progress_status(
    assessments: list[dict[str, Any]], eligibility: str
) -> str:
    statuses = {item["status"] for item in assessments}
    if "Regressed" in statuses and statuses & {"Improved", "Target met"}:
        return "Mixed"
    if "Regressed" in statuses:
        return "Regressed"
    if "Mixed" in statuses:
        return "Mixed"
    if "Improved" in statuses:
        return "Improved"
    if statuses and statuses <= {"Target met"}:
        return "Target met"
    if "Target met" in statuses:
        return "Target met"
    if "Unchanged" in statuses:
        return "Unchanged"
    if "Not directly comparable" in statuses:
        return "Not directly comparable"
    if eligibility not in {"eligible_now", "parked"}:
        return "Not eligible"
    return "Not measured"


def build_result_views() -> dict[str, Any]:
    catalog = load_json(CATALOG_PATH)
    benchmark = load_json(BENCHMARK_PATH)
    paper = load_json(PAPER_PATH)
    evaluation_index = {
        item["experimentId"]: item for item in benchmark["evaluationRecords"]
    }
    coverage_index = {
        item["experimentId"]: item for item in benchmark["metricCoverage"]
    }
    bundles_by_experiment: dict[str, list[dict[str, Any]]] = defaultdict(list)
    bundle_index: dict[tuple[str, str], dict[str, Any]] = {}
    for bundle in catalog["acceptedRunBundles"]:
        experiment_id = bundle["envelope"]["experimentId"]
        bundles_by_experiment[experiment_id].append(bundle)
        bundle_index[(experiment_id, bundle["envelope"]["runId"])] = bundle
    current_ids = {
        item["experimentId"]: item["runId"]
        for item in catalog["currentRunIndex"]["currentRuns"]
    }
    mappings = paper_mappings(paper)
    result_views: list[dict[str, Any]] = []
    safe_labels = catalog["programState"]["safeLabels"]

    for experiment in catalog["experiments"]:
        experiment_id = experiment["id"]
        bundles = bundles_by_experiment[experiment_id]
        current_bundle = (
            bundle_index[(experiment_id, current_ids[experiment_id])]
            if experiment_id in current_ids
            else None
        )
        previous_bundle = None
        if current_bundle is not None:
            previous_candidates = [
                bundle
                for bundle in bundles
                if bundle["envelope"]["runId"]
                != current_bundle["envelope"]["runId"]
            ]
            if previous_candidates:
                previous_bundle = previous_candidates[-1]
        observations = (
            current_bundle["metricObservations"] if current_bundle else []
        )
        evaluation = evaluation_index[experiment_id]
        assessments = [
            assessment_for_metric(
                experiment_id,
                metric_id,
                current_bundle,
                previous_bundle,
                evaluation,
            )
            for metric_id in experiment["metricDefinitions"]
        ]
        measure = measurement_state(
            experiment, observations, assessments, safe_labels
        )
        status = progress_status(assessments, evaluation["eligibility"])
        paper_alignment = (
            mappings
            if experiment_id == "EXP-037"
            else (
                [mappings[-1]]
                if experiment_id
                in {
                    "EXP-003",
                    "EXP-005",
                    "EXP-012",
                    "EXP-020",
                    "EXP-021",
                    "EXP-023",
                    "EXP-024",
                    "EXP-025",
                    "EXP-029",
                }
                else []
            )
        )
        current_run = None
        if current_bundle is not None:
            envelope = current_bundle["envelope"]
            current_run = {
                "runId": envelope["runId"],
                "acceptedAt": envelope.get("acceptedAt"),
                "executionStatus": envelope["executionStatus"],
                "evidenceClass": envelope["evidenceClass"],
                "manifestPath": envelope["manifestPath"],
                "manifestSha256": envelope["manifestSha256"],
                "comparisonContext": envelope["comparisonContext"],
                "resultVerdict": envelope["evaluation"]["resultVerdict"],
            }
        what_happened = (
            experiment.get("latestResult", {}).get("summary")
            if current_bundle is not None
            else (
                "No accepted execution exists. The experiment remains a "
                f"{experiment['status'].lower()} study."
            )
        )
        target_outcome = (
            f"Benchmark verdict {evaluation['verdict']}; "
            f"measurement state {measure['status']}."
        )
        result_views.append(
            {
                "schemaVersion": "ExperimentResultView-v1",
                "experimentId": experiment_id,
                "title": experiment["title"],
                "plainLanguagePurpose": experiment["researchQuestion"],
                "baseline": experiment["baseline"],
                "comparator": experiment["comparator"],
                "cohort": {
                    "datasetHash": (
                        current_bundle["envelope"]["comparisonContext"].get(
                            "datasetHash"
                        )
                        if current_bundle
                        else experiment.get("datasetHash")
                    ),
                    "partitionHash": (
                        current_bundle["envelope"]["comparisonContext"].get(
                            "partitionHash"
                        )
                        if current_bundle
                        else experiment.get("partitionHash")
                    ),
                    "description": (
                        "Latest accepted run cohort; see source and comparison "
                        "context hashes."
                        if current_bundle
                        else "No accepted run cohort."
                    ),
                },
                "treatment": (
                    ", ".join(experiment["architectureTargets"])
                    or "Protocol-only research treatment"
                ),
                "status": experiment["status"],
                "evidenceClass": experiment["evidenceClass"],
                "currentRun": current_run,
                "historicalRuns": [
                    {
                        "runId": bundle["envelope"]["runId"],
                        "acceptedAt": bundle["envelope"].get("acceptedAt"),
                        "evidenceClass": bundle["envelope"]["evidenceClass"],
                        "current": (
                            current_bundle is not None
                            and bundle["envelope"]["runId"]
                            == current_bundle["envelope"]["runId"]
                        ),
                    }
                    for bundle in bundles
                ],
                "measurementState": measure,
                "evaluationDimensions": evaluation["dimensions"],
                "progressAssessments": assessments,
                "visualizationSpecs": visualization_specs(
                    experiment, observations
                ),
                "paperAlignment": paper_alignment,
                "conclusion": {
                    "whatWasTested": experiment["researchQuestion"],
                    "whatHappened": what_happened,
                    "targetOutcome": target_outcome,
                    "progressStatus": status,
                    "cannotInfer": experiment["claimBoundary"],
                },
                "sources": source_rows(
                    observations, experiment["artifactLinks"]
                ),
                "limitations": experiment["validityThreats"],
                "nextAction": experiment["nextAction"],
                "claimBoundary": experiment["claimBoundary"],
            }
        )

    result = {
        "schemaVersion": "ExperimentResultViewCollection-v1",
        "generatedAt": benchmark["generatedAt"],
        "publicationTier": (
            "controlled_local"
            if catalog["publicationTier"] == "controlled_local"
            else "tracked_shareable"
        ),
        "catalogSha256": sha256(CATALOG_PATH),
        "benchmarkSha256": sha256(BENCHMARK_PATH),
        "resultViews": result_views,
        "paperMetricMappings": mappings,
        "summary": {
            "experimentCount": len(result_views),
            "currentAcceptedRunCount": len(current_ids),
            "historicalAcceptedRunCount": len(catalog["acceptedRunBundles"]),
            "declaredMetricCount": sum(
                item["measurementState"]["declaredMetricCount"]
                for item in result_views
            ),
            "observedMetricCount": sum(
                item["measurementState"]["observedMetricCount"]
                for item in result_views
            ),
            "nonNullMetricCount": sum(
                item["measurementState"]["nonNullMetricCount"]
                for item in result_views
            ),
            "observedNullExperimentCount": sum(
                item["measurementState"]["status"] == "observed_null"
                for item in result_views
            ),
            "classificationClaimsEligible": safe_labels >= 20,
        },
        "claimBoundary": (
            "Engineering progress and empirical value remain separate. At "
            f"{safe_labels}/24 safe labels, classification accuracy, macro-F1, "
            "generalization, human-effort reduction, and superiority remain unproven."
        ),
    }
    validate(result, coverage_index)
    return result


def validate(
    collection: dict[str, Any],
    benchmark_coverage: dict[str, dict[str, Any]],
) -> None:
    validators = {
        "progress": validator("progress-assessment-v1.schema.json"),
        "visual": validator("visualization-spec-v1.schema.json"),
        "paper": validator("paper-metric-mapping-v1.schema.json"),
        "view": validator("experiment-result-view-v1.schema.json"),
        "collection": validator(
            "experiment-result-view-collection-v1.schema.json"
        ),
    }
    for mapping in collection["paperMetricMappings"]:
        validators["paper"].validate(mapping)
    ids: list[str] = []
    visualization_ids: list[str] = []
    for view in collection["resultViews"]:
        validators["view"].validate(view)
        ids.append(view["experimentId"])
        for assessment in view["progressAssessments"]:
            validators["progress"].validate(assessment)
        for spec in view["visualizationSpecs"]:
            validators["visual"].validate(spec)
            visualization_ids.append(spec["visualizationId"])
        coverage = benchmark_coverage[view["experimentId"]]
        if (
            view["measurementState"]["nonNullMetricCount"]
            != coverage["nonNullMetricCount"]
        ):
            raise ValueError(
                f"{view['experimentId']} result-view coverage disagrees with benchmark"
            )
    validators["collection"].validate(collection)
    expected = [f"EXP-{index:03d}" for index in range(41)]
    if ids != expected:
        raise ValueError("result views must contain EXP-000 through EXP-040 in order")
    if len(visualization_ids) != len(set(visualization_ids)):
        raise ValueError("visualization IDs must be unique")
    if collection["summary"]["classificationClaimsEligible"]:
        raise ValueError(
            "classification claims cannot be eligible while safe labels remain zero"
        )
    for view in collection["resultViews"]:
        empirical = {
            metric_id
            for metric_id in view["measurementState"]["nullMetricIds"]
            if metric_id.startswith(EMPIRICAL_PREFIXES)
        }
        if empirical and not any(
            spec["chartFamily"] == "empty_state"
            and empirical.intersection(spec["metricIds"])
            for spec in view["visualizationSpecs"]
        ):
            raise ValueError(
                f"{view['experimentId']} lacks an honest empirical empty state"
            )


def write_or_check(path: Path, payload: dict[str, Any], check: bool) -> None:
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    current = path.read_text(encoding="utf-8") if path.is_file() else None
    if current == content:
        return
    if check:
        raise ValueError(f"stale generated output: {path.relative_to(ROOT)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    try:
        payload = build_result_views()
        write_or_check(OUTPUT_PATH, payload, args.check)
        summary = payload["summary"]
        print(
            "BigUI result views: PASS "
            f"({summary['experimentCount']} experiments; "
            f"{summary['currentAcceptedRunCount']} current accepted runs; "
            f"{summary['historicalAcceptedRunCount']} historical bundles; "
            f"{summary['nonNullMetricCount']} non-null metric families)"
        )
        return 0
    except Exception as exc:
        print(f"BigUI result views: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
