from __future__ import annotations

import copy
import sqlite3
from pathlib import Path

import pytest

from vego_bigui.comparison import comparison_eligibility
from vego_bigui.store import (
    BundleValidationError,
    BundleValidator,
    load_bundles,
    rebuild_sqlite,
    run_store_summary,
)

ROOT = Path(__file__).resolve().parents[2]
ACCEPTED = ROOT / "experiments" / "accepted-runs"
SCHEMAS = ROOT / "schemas"


def test_accepted_run_store_is_complete_and_rebuildable(tmp_path: Path) -> None:
    bundles = load_bundles(ACCEPTED, SCHEMAS)
    summary = run_store_summary(bundles)
    assert summary["bundleCount"] >= 22
    assert summary["experimentsWithAcceptedRuns"] >= 22
    assert summary["metricObservationCount"] >= 240
    assert "EXP-005" in summary["experimentIds"]
    assert "EXP-036" in summary["experimentIds"]

    database = tmp_path / "run-registry.sqlite"
    rebuilt = rebuild_sqlite(bundles, database)
    assert rebuilt == summary
    with sqlite3.connect(database) as connection:
        run_count = connection.execute("SELECT COUNT(*) FROM run").fetchone()[0]
        observation_count = connection.execute(
            "SELECT COUNT(*) FROM metric_observation"
        ).fetchone()[0]
    assert run_count == summary["bundleCount"]
    assert observation_count == summary["metricObservationCount"]


def test_zero_label_bundle_rejects_non_null_accuracy() -> None:
    bundles = load_bundles(ACCEPTED, SCHEMAS)
    source = next(
        item for item in bundles if item["envelope"]["experimentId"] == "EXP-012"
    )
    invalid = copy.deepcopy(source)
    invalid.pop("_bundlePath", None)
    invalid.pop("_bundleSha256", None)
    observation = next(
        item
        for item in invalid["metricObservations"]
        if item["metricId"].startswith("CLASSIFICATION_")
    )
    observation["value"] = 0.9
    with pytest.raises(BundleValidationError):
        BundleValidator(SCHEMAS).validate(invalid)


def test_v2_comparison_requires_invariants_and_shared_metric_definition() -> None:
    shared = {
        "datasetHash": "a" * 64,
        "partitionHash": "not_applicable",
        "baselineRevision": "baseline",
        "policyVersion": "policy",
        "promptVersion": "prompt",
        "modelIdentifier": "model",
        "metricSchemaVersion": "2.0",
        "labelEligibility": "not_applicable",
        "leakageClass": "none",
        "evidenceClass": "offline",
        "pairedCohortHash": "b" * 64,
    }
    left = {
        "runId": "left",
        "comparisonContext": {**shared, "architectureMode": "legacy"},
        "metricDefinitionHashes": {"PARITY": "c" * 64},
    }
    right = {
        "runId": "right",
        "comparisonContext": {**shared, "architectureMode": "unified"},
        "metricDefinitionHashes": {"PARITY": "c" * 64},
    }
    spec = {
        "comparisonFamily": "architecture_mode",
        "treatmentField": "architectureMode",
        "allowedDifferences": ["architectureMode"],
        "invariantFields": [
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
        ],
        "unitOfAnalysis": "artifact",
        "requiresPairedCohort": True,
    }
    verdict = comparison_eligibility(left, right, spec=spec)
    assert verdict["eligible"] is True
    assert verdict["sharedMetricIds"] == ["PARITY"]

    right["comparisonContext"]["datasetHash"] = "d" * 64
    assert comparison_eligibility(left, right, spec=spec)["eligible"] is False
