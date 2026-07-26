from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import jsonschema

from vego_bigui.comparison import comparison_eligibility

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "experiment-catalog-snapshot-v1.json"
)
ARCHITECTURE_PATH = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "architecture-fixture-results-v1.json"
)
HTML_PATH = ROOT / "VEGO-AI-Research-Hub.html"


def load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_catalog_is_complete_deterministic_and_schema_valid() -> None:
    builder = load_script("build_bigui_catalog.py")
    tracked = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    assert builder.build_catalog() == tracked
    schema = json.loads(
        (ROOT / "schemas" / "experiment-catalog-snapshot-v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    ).validate(tracked)
    assert [item["id"] for item in tracked["experiments"]] == [
        f"EXP-{index:03d}" for index in range(41)
    ]
    assert len({item["id"] for item in tracked["experiments"]}) == 41
    current_rows = tracked["currentRunIndex"]["currentRuns"]
    assert len(current_rows) == tracked["runStoreSummary"][
        "experimentsWithAcceptedRuns"
    ]
    assert len({item["experimentId"] for item in current_rows}) == len(
        current_rows
    )


def test_catalog_zero_label_gate_keeps_empirical_metrics_null() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    assert catalog["programState"]["safeLabels"] == 0
    performance = [
        item
        for item in [
            *catalog["metricObservations"],
            *catalog["metricObservationsV2"],
        ]
        if item["metricId"].startswith(("CLASSIFICATION_", "PAIRED_"))
    ]
    assert performance
    assert all(item["value"] is None for item in performance)
    assert all(item["denominator"] == 0 for item in performance)


def test_bigui_exposes_independent_evidence_workflow() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    assert 'id="independent-evidence"' in html
    assert "Blind 24-item review" in html
    assert "Agreement + adjudication" in html
    assert "Only independent humans may supply or adjudicate the labels" in html
    assert "Current phase: calibration." in html
    assert "IE-01–IE-10 accepted" in html
    assert "all 24 evaluation cases remain sealed" in html
    decision_match = re.search(
        r'<script id="independent-evidence-decisions" type="application/json">(.*?)</script>',
        html,
        re.DOTALL,
    )
    assert decision_match
    decisions = json.loads(decision_match.group(1))
    assert decisions["programStage"] == "calibration_ready"
    assert len(decisions["decisions"]) == 10
    assert all(item["outcome"] == "Accepted" for item in decisions["decisions"])


def test_every_metric_and_source_has_publishable_provenance() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    for metric in catalog["metricObservations"]:
        assert metric["sourcePath"]
        assert metric["sourceSha256"]
        assert metric["unit"]
        assert metric["observationDate"]
        assert metric["evidenceClass"]
        assert metric["claimBoundary"]
    for metric in catalog["metricObservationsV2"]:
        assert metric["observationId"]
        assert metric["experimentId"]
        assert metric["runId"]
        assert metric["sourcePath"]
        assert metric["sourceSha256"]
        assert metric["unit"]
        assert metric["observationDate"]
        assert metric["evidenceClass"]
        assert metric["claimBoundary"]
    serialized = json.dumps(catalog)
    assert "file:///" not in serialized
    assert "C:\\\\Users\\\\" not in serialized
    for source in catalog["sources"]:
        path = ROOT / source["path"]
        assert path.is_file()
        assert builder_hash(path) == source["sha256"]


def builder_hash(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_comparison_eligibility_fails_closed() -> None:
    shared = {
        "datasetHash": "a",
        "partitionHash": "b",
        "baselineRevision": "c",
        "policyVersion": "d",
        "promptVersion": "e",
        "modelIdentifier": "f",
        "metricSchemaVersion": "1",
        "labelEligibility": "safe",
        "leakageClass": "none",
        "evidenceClass": "empirical",
    }
    left = {"runId": "left", **shared}
    right = {"runId": "right", **shared}
    assert comparison_eligibility(left, right)["eligible"] is True
    right["evidenceClass"] = "synthetic"
    verdict = comparison_eligibility(left, right)
    assert verdict["eligible"] is False
    assert verdict["status"] == "Not directly comparable"
    right = {"runId": "missing", **shared}
    del right["partitionHash"]
    assert comparison_eligibility(left, right)["eligible"] is False


def test_architecture_fixture_results_are_bounded_and_pass() -> None:
    snapshot_builder = load_script("build_bigui_architecture_snapshot.py")
    tracked = json.loads(ARCHITECTURE_PATH.read_text(encoding="utf-8"))
    assert snapshot_builder.build() == tracked
    assert tracked["containsControlledData"] is False
    assert tracked["containsHumanLabels"] is False
    results = {item["experimentId"]: item for item in tracked["experiments"]}
    assert results["EXP-033"]["passed"] is True
    assert results["EXP-033"]["semanticDifferences"] == 0
    assert results["EXP-034"]["contractEquivalent"] is True
    assert results["EXP-034"]["selectedDefault"] is None
    assert results["EXP-035"]["passed"] is True
    assert results["EXP-036"]["result"] is None


def test_paper_and_current_baselines_are_reconciled_without_accuracy_claim() -> None:
    builder = load_script("build_bigui_catalog.py")
    catalog = builder.build_catalog()
    paper = catalog["paperBaseline"]
    comparison = catalog["baselineComparisonResults"]
    assert paper["evaluationScope"]["caseModelTotal"] == 178
    assert paper["phaseD"]["patternTotal"] == 26
    assert comparison["currentBaseline"]["caseModelTotal"] == 179
    assert comparison["currentBaseline"]["patternTotal"] == 27
    exp037 = next(
        item
        for item in comparison["experiments"]
        if item["experimentId"] == "EXP-037"
    )
    eligibility = next(
        item
        for item in exp037["metrics"]
        if item["metricId"]
        == "PAPER_CURRENT_CLASSIFICATION_COMPARISON_ELIGIBLE"
    )
    assert eligibility["value"] == 0
    assert comparison["currentBaseline"]["safeLabels"] == 0


def test_comparison_scorecard_keeps_empirical_dimensions_null() -> None:
    builder = load_script("build_bigui_catalog.py")
    comparison = builder.build_catalog()["baselineComparisonResults"]
    exp038 = next(
        item
        for item in comparison["experiments"]
        if item["experimentId"] == "EXP-038"
    )
    rows = {
        item["dimension"]: item for item in exp038["details"]["scorecard"]
    }
    assert rows["human_judgment_capabilities"]["current"] == 1.0
    assert rows["semantic_parity"]["current"] == 1.0
    assert rows["classification_accuracy"]["current"] is None
    assert rows["human_effort"]["current"] is None


def test_bigui_html_is_fresh_offline_and_catalog_driven() -> None:
    builder = load_script("build_bigui.py")
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    assert HTML_PATH.read_text(encoding="utf-8") == builder.render(catalog)
    content = HTML_PATH.read_text(encoding="utf-8")
    assert '<script src="http' not in content
    assert '<link href="http' not in content
    assert "EXP-040" in content
    assert "Paper baseline and evidence of progress" in content
    assert "All-experiment evaluation benchmark" in content
    assert "VEGO-AI-Experiment-Benchmark-Report.html" in content
    assert "NOT YET COMPUTABLE" in content
    assert "Accepted run center" in content
    assert "Measured experiments first" in content
    assert "A declared or null placeholder is never counted as a measured result." in content
    assert "Paper baseline laboratory · Phases A–D" in content
    assert "Live deployment is stale" in content
    match = re.search(
        r'<script id="bigui-catalog" type="application/json">(.*?)</script>',
        content,
        re.DOTALL,
    )
    assert match
    embedded = json.loads(match.group(1))
    assert embedded == catalog
    result_match = re.search(
        r'<script id="experiment-result-views" type="application/json">(.*?)</script>',
        content,
        re.DOTALL,
    )
    deployment_match = re.search(
        r'<script id="deployment-snapshot" type="application/json">(.*?)</script>',
        content,
        re.DOTALL,
    )
    assert result_match and deployment_match
    result_views = json.loads(result_match.group(1))
    deployment = json.loads(deployment_match.group(1))
    assert len(result_views["resultViews"]) == 41
    assert result_views["summary"]["classificationClaimsEligible"] is False
    assert deployment["experimentCount"] == 41
    assert deployment["liveObservation"]["status"] == "stale"


def test_status_and_evidence_classes_remain_separate() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in catalog["experiments"]}
    assert by_id["EXP-009"]["evidenceClass"] == "synthetic"
    assert by_id["EXP-020"]["evidenceClass"] == "blocked"
    assert by_id["EXP-033"]["evidenceClass"] == "offline"
    assert by_id["EXP-033"]["status"] == "Offline evidence"
    assert by_id["EXP-031"]["status"] == "Proposal — not approved"
    assert by_id["EXP-032"]["status"] == "Blocked"
    assert by_id["EXP-034"]["latestResult"]["metricObservationIds"]


def test_record_validator_rejects_incomparable_runs_marked_eligible() -> None:
    validator = load_script("validate_research_records.py")
    record = json.loads(
        (
            ROOT
            / "schemas"
            / "examples"
            / "comparison-incomparable.invalid.json"
        ).read_text(encoding="utf-8")
    )
    errors = validator.validate_record(record)
    assert errors
    assert any("mismatched checks" in error for error in errors)
