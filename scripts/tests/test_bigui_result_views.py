from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT_VIEWS = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "experiment-result-views-v1.json"
)
CATALOG = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "experiment-catalog-snapshot-v1.json"
)


def load_builder():
    path = ROOT / "scripts" / "build_bigui_result_views.py"
    spec = importlib.util.spec_from_file_location(
        "build_bigui_result_views_test", path
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_result_views_are_deterministic_complete_and_schema_valid() -> None:
    builder = load_builder()
    tracked = json.loads(RESULT_VIEWS.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    assert builder.build_result_views() == tracked
    assert tracked["summary"]["experimentCount"] == 41
    assert tracked["summary"]["currentAcceptedRunCount"] == 26
    assert tracked["summary"]["historicalAcceptedRunCount"] == len(
        catalog["acceptedRunBundles"]
    )
    assert [
        item["experimentId"] for item in tracked["resultViews"]
    ] == [f"EXP-{index:03d}" for index in range(41)]
    assert len(
        {
            spec["visualizationId"]
            for view in tracked["resultViews"]
            for spec in view["visualizationSpecs"]
        }
    ) == sum(
        len(view["visualizationSpecs"]) for view in tracked["resultViews"]
    )


def test_progress_deltas_have_cross_interpreter_precision() -> None:
    builder = load_builder()
    payload = builder.build_result_views()
    deltas = [
        assessment[field]
        for view in payload["resultViews"]
        for assessment in view["progressAssessments"]
        for field in ("absoluteDelta", "relativeDelta")
        if assessment[field] is not None
    ]

    assert deltas
    assert all(value == round(value, 9) for value in deltas)


def test_result_views_do_not_count_null_values_as_measured() -> None:
    payload = json.loads(RESULT_VIEWS.read_text(encoding="utf-8"))
    views = {item["experimentId"]: item for item in payload["resultViews"]}
    exp003 = views["EXP-003"]["measurementState"]
    assert exp003["declaredMetricCount"] == 5
    assert exp003["observedMetricCount"] == 5
    assert exp003["nonNullObservationCount"] == 0
    assert exp003["nonNullMetricCount"] == 0
    assert exp003["status"] == "observed_null"
    assert any(
        spec["chartFamily"] == "empty_state"
        for spec in views["EXP-003"]["visualizationSpecs"]
    )

    exp012 = views["EXP-012"]["measurementState"]
    assert exp012["declaredMetricCount"] == 8
    assert exp012["observedMetricCount"] == 8
    assert exp012["nonNullMetricCount"] == 3
    assert exp012["status"] == "measured_partial"
    assert set(exp012["nullMetricIds"]) == {
        "CLASSIFICATION_ACCURACY_B0",
        "CLASSIFICATION_ACCURACY_B1",
        "CLASSIFICATION_MACRO_F1_B0",
        "CLASSIFICATION_MACRO_F1_B1",
        "PAIRED_NET_CORRECTION",
    }


def test_result_views_keep_paper_and_empirical_lanes_separate() -> None:
    payload = json.loads(RESULT_VIEWS.read_text(encoding="utf-8"))
    assert payload["summary"]["classificationClaimsEligible"] is False
    assert len(payload["paperMetricMappings"]) == 4
    assert not any(
        item["directComparisonEligible"]
        for item in payload["paperMetricMappings"]
    )
    phase_a = next(
        item
        for item in payload["paperMetricMappings"]
        if item["paperPhase"] == "A"
    )
    assert "not variability-classification accuracy" in (
        phase_a["incompatibilityReason"]
    )
    for view in payload["resultViews"]:
        for assessment in view["progressAssessments"]:
            if assessment["comparabilityVerdict"] != "Eligible":
                assert assessment["absoluteDelta"] is None
                assert assessment["relativeDelta"] is None


def test_comparison_mismatch_refuses_a_delta() -> None:
    builder = load_builder()
    left = {field: "same" for field in builder.REQUIRED_COMPARISON_FIELDS}
    right = dict(left)
    right["datasetHash"] = "different"
    mismatches = builder.comparison_mismatches(left, right)
    assert mismatches == [
        {"field": "datasetHash", "left": "same", "right": "different"}
    ]


def test_metric_definition_mismatch_refuses_same_grain_delta() -> None:
    builder = load_builder()
    shared = {
        "metricId": "CATALOG_COMPLETENESS",
        "dimensions": {"scope": "definitions"},
        "value": 1.0,
    }
    left = {**shared, "metricDefinitionSha256": "a" * 64}
    right = {**shared, "metricDefinitionSha256": "b" * 64}

    assert builder.metric_definition_mismatches([left], [right]) == [
        {
            "field": "metricDefinitionSha256",
            "left": "a" * 64,
            "right": "b" * 64,
        }
    ]


def test_assessment_refuses_delta_when_metric_definition_changed() -> None:
    builder = load_builder()
    context = {
        field: "same" for field in builder.REQUIRED_COMPARISON_FIELDS
    }
    base_observation = {
        "metricId": "CATALOG_COMPLETENESS",
        "dimensions": {"scope": "definitions"},
        "value": 1.0,
        "direction": "higher_is_better",
        "confidenceInterval": None,
    }
    left = {
        "envelope": {
            "runId": "left",
            "comparisonContext": context,
        },
        "metricObservations": [
            {**base_observation, "metricDefinitionSha256": "a" * 64}
        ],
    }
    right = {
        "envelope": {
            "runId": "right",
            "comparisonContext": context,
        },
        "metricObservations": [
            {**base_observation, "metricDefinitionSha256": "b" * 64}
        ],
    }

    assessment = builder.assessment_for_metric(
        "EXP-030",
        "CATALOG_COMPLETENESS",
        right,
        left,
        {"engineeringSignals": []},
    )

    assert assessment["comparabilityVerdict"] == "Not directly comparable"
    assert assessment["status"] == "Not directly comparable"
    assert assessment["absoluteDelta"] is None
    assert assessment["relativeDelta"] is None
    assert assessment["mismatches"][0]["field"] == "metricDefinitionSha256"


def test_previous_run_is_selected_by_acceptance_time() -> None:
    builder = load_builder()
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    bundles = [
        item
        for item in catalog["acceptedRunBundles"]
        if item["envelope"]["experimentId"] == "EXP-006"
    ]
    current_run_id = next(
        item["runId"]
        for item in catalog["currentRunIndex"]["currentRuns"]
        if item["experimentId"] == "EXP-006"
    )
    current = next(
        item for item in bundles if item["envelope"]["runId"] == current_run_id
    )
    ordered = sorted(bundles, key=builder.accepted_bundle_sort_key)
    current_index = next(
        index
        for index, item in enumerate(ordered)
        if item["envelope"]["runId"] == current_run_id
    )

    assert current_index > 0
    assert (
        builder.previous_accepted_bundle(bundles, current)["envelope"]["runId"]
        == ordered[current_index - 1]["envelope"]["runId"]
    )


def test_unchanged_progress_is_not_labeled_regressed_when_guardrail_is_missed() -> None:
    builder = load_builder()
    payload = builder.build_result_views()
    exp007 = next(
        item
        for item in payload["resultViews"]
        if item["experimentId"] == "EXP-007"
    )
    unchanged = [
        assessment
        for assessment in exp007["progressAssessments"]
        if assessment["absoluteDelta"] == 0
        and any(
            guardrail["status"] == "missed"
            for guardrail in assessment["guardrails"]
        )
    ]

    assert unchanged
    assert all(item["status"] == "Unchanged" for item in unchanged)
