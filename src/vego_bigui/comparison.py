"""Fail-closed run comparison rules used by the BigUI and experiment harness.

Version two comparisons declare what is intentionally changing instead of
requiring every context field to match.  This allows legitimate architecture,
topology, model, policy, and interface comparisons while still refusing
cross-cohort or cross-metric deltas.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

LEGACY_COMPARISON_FIELDS = (
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

COMPARISON_FIELDS = LEGACY_COMPARISON_FIELDS


def _run_id(record: Mapping[str, Any]) -> str:
    value = record.get("runId") or record.get("run_id")
    if not value:
        raise ValueError("both comparison records require a runId")
    return str(value)


def _context(record: Mapping[str, Any]) -> Mapping[str, Any]:
    value = record.get("comparisonContext")
    if isinstance(value, Mapping):
        return value
    return record


def _metric_hashes(record: Mapping[str, Any]) -> Mapping[str, Any]:
    value = record.get("metricDefinitionHashes")
    return value if isinstance(value, Mapping) else {}


def _legacy_comparison(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
) -> dict[str, Any]:
    """Preserve the original all-fields-equal contract for older callers."""

    left_id = _run_id(left)
    right_id = _run_id(right)
    left_context = _context(left)
    right_context = _context(right)
    checks: list[dict[str, Any]] = []
    reasons: list[str] = []
    for field in LEGACY_COMPARISON_FIELDS:
        left_value = left_context.get(field)
        right_value = right_context.get(field)
        matches = (
            left_value is not None
            and right_value is not None
            and left_value == right_value
        )
        checks.append(
            {
                "field": field,
                "left": None if left_value is None else str(left_value),
                "right": None if right_value is None else str(right_value),
                "matches": matches,
            }
        )
        if not matches:
            if left_value is None or right_value is None:
                reasons.append(f"{field} is missing for at least one run")
            else:
                reasons.append(f"{field} differs")
    eligible = not reasons
    return {
        "schemaVersion": "ComparisonEligibility-v1",
        "leftRunId": left_id,
        "rightRunId": right_id,
        "eligible": eligible,
        "status": "Directly comparable" if eligible else "Not directly comparable",
        "checks": checks,
        "reasons": reasons,
    }


def _comparison_v2(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    spec: Mapping[str, Any],
) -> dict[str, Any]:
    left_id = _run_id(left)
    right_id = _run_id(right)
    left_context = _context(left)
    right_context = _context(right)
    treatment_field = str(spec.get("treatmentField") or "")
    comparison_family = str(spec.get("comparisonFamily") or "")
    invariant_fields = tuple(str(item) for item in spec.get("invariantFields", ()))
    allowed_differences = {
        str(item) for item in spec.get("allowedDifferences", ())
    }
    unit = str(spec.get("unitOfAnalysis") or "")
    requires_paired = bool(spec.get("requiresPairedCohort"))
    if (
        not treatment_field
        or not comparison_family
        or not invariant_fields
        or not unit
    ):
        raise ValueError("comparison v2 requires a complete comparison specification")
    if treatment_field not in allowed_differences:
        raise ValueError("treatmentField must be listed in allowedDifferences")

    checks: list[dict[str, Any]] = []
    reasons: list[str] = []
    for field in invariant_fields:
        left_value = left_context.get(field)
        right_value = right_context.get(field)
        matches = (
            left_value is not None
            and right_value is not None
            and left_value == right_value
        )
        checks.append(
            {
                "field": field,
                "left": left_value,
                "right": right_value,
                "role": "invariant",
                "matches": matches,
            }
        )
        if not matches:
            reasons.append(
                f"{field} is missing or differs, but it is an invariant"
            )

    left_treatment = left_context.get(treatment_field)
    right_treatment = right_context.get(treatment_field)
    treatment_present = (
        left_treatment is not None and right_treatment is not None
    )
    checks.append(
        {
            "field": treatment_field,
            "left": left_treatment,
            "right": right_treatment,
            "role": "treatment",
            "matches": treatment_present,
        }
    )
    if not treatment_present:
        reasons.append(f"treatment field {treatment_field} is missing")

    if requires_paired:
        left_pair = left_context.get("pairedCohortHash")
        right_pair = right_context.get("pairedCohortHash")
        pair_matches = (
            left_pair is not None
            and right_pair is not None
            and left_pair == right_pair
        )
        checks.append(
            {
                "field": "pairedCohortHash",
                "left": left_pair,
                "right": right_pair,
                "role": "paired_cohort",
                "matches": pair_matches,
            }
        )
        if not pair_matches:
            reasons.append("paired cohort hash is missing or differs")

    left_metrics = _metric_hashes(left)
    right_metrics = _metric_hashes(right)
    shared_metrics = sorted(
        metric_id
        for metric_id in set(left_metrics) & set(right_metrics)
        if left_metrics[metric_id] == right_metrics[metric_id]
    )
    checks.append(
        {
            "field": "metricDefinitionHashes",
            "left": sorted(left_metrics),
            "right": sorted(right_metrics),
            "role": "metric",
            "matches": bool(shared_metrics),
        }
    )
    if not shared_metrics:
        reasons.append("no shared metric has the same definition hash")

    eligible = not reasons
    normalized_spec = {
        "comparisonFamily": comparison_family,
        "treatmentField": treatment_field,
        "allowedDifferences": sorted(allowed_differences),
        "invariantFields": list(invariant_fields),
        "unitOfAnalysis": unit,
        "requiresPairedCohort": requires_paired,
    }
    return {
        "schemaVersion": "ComparisonEligibility-v2",
        "leftRunId": left_id,
        "rightRunId": right_id,
        "spec": normalized_spec,
        "eligible": eligible,
        "status": "Directly comparable" if eligible else "Not directly comparable",
        "checks": checks,
        "sharedMetricIds": shared_metrics,
        "reasons": reasons,
    }


def comparison_eligibility(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    *,
    spec: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return an explicit comparison verdict for two normalized runs.

    V2 callers provide a comparison specification describing the treatment and
    invariants.  Older callers without a specification keep the original
    all-fields-equal behavior for compatibility.
    """

    if spec is None:
        candidate = left.get("comparisonSpec") or right.get("comparisonSpec")
        spec = candidate if isinstance(candidate, Mapping) else None
    if spec is None:
        return _legacy_comparison(left, right)
    return _comparison_v2(left, right, spec)
