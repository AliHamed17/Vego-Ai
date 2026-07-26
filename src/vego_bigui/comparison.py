"""Fail-closed run comparison rules used by the BigUI and experiment harness."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

COMPARISON_FIELDS = (
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


def comparison_eligibility(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
) -> dict[str, Any]:
    """Return an explicit comparison verdict for two normalized runs.

    A missing value is not a wildcard. Two runs are directly comparable only
    when every required field exists and matches. Synthetic and empirical runs
    therefore cannot enter the same delta or trend series.
    """

    left_id = str(left.get("runId") or left.get("run_id") or "")
    right_id = str(right.get("runId") or right.get("run_id") or "")
    if not left_id or not right_id:
        raise ValueError("both comparison records require a runId")

    checks: list[dict[str, Any]] = []
    reasons: list[str] = []
    for field in COMPARISON_FIELDS:
        left_value = left.get(field)
        right_value = right.get(field)
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
        "status": (
            "Directly comparable" if eligible else "Not directly comparable"
        ),
        "checks": checks,
        "reasons": reasons,
    }
