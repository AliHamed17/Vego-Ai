from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "experiment-benchmark-snapshot-v1.json"
)
STANDARD = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "experiment-evaluation-standard-v1.json"
)
REPORT_MD = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "EXPERIMENT_BENCHMARK_ANALYTICS_REPORT.md"
)
REPORT_HTML = ROOT / "VEGO-AI-Experiment-Benchmark-Report.html"


def load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_benchmark_is_deterministic_complete_and_schema_valid() -> None:
    builder = load_script("build_experiment_benchmark.py")
    tracked = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert builder.build_snapshot() == tracked
    schema = json.loads(
        (
            ROOT / "schemas" / "experiment-benchmark-snapshot-v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    ).validate(tracked)
    assert [item["experimentId"] for item in tracked["evaluationRecords"]] == [
        f"EXP-{index:03d}" for index in range(41)
    ]
    assert tracked["summary"]["evaluatedExperiments"] == 41
    assert tracked["summary"]["executedExperiments"] == 26
    assert tracked["summary"]["protocolOnlyExperiments"] == 15
    assert len(tracked["resultHighlights"]) >= 8
    assert len(
        {item["experimentId"] for item in tracked["resultHighlights"]}
    ) == len(tracked["resultHighlights"])
    for highlight in tracked["resultHighlights"]:
        assert highlight["metrics"]
        for metric in highlight["metrics"]:
            assert metric["denominator"] is not None
            assert len(metric["sourceSha256"]) == 64
            assert metric["sourcePath"]
            assert metric["observationDate"]
            assert metric["claimBoundary"]
    current_ids = {
        item["experimentId"]: item["runId"]
        for item in json.loads(
            (
                ROOT / "experiments" / "current-run-index-v1.json"
            ).read_text(encoding="utf-8")
        )["currentRuns"]
    }
    catalog = json.loads(
        (
            ROOT
            / "docs"
            / "research"
            / "bigui"
            / "experiment-catalog-snapshot-v1.json"
        ).read_text(encoding="utf-8")
    )
    current_bundle_ids = {
        bundle["envelope"]["experimentId"]: bundle["envelope"]["runId"]
        for bundle in catalog["acceptedRunBundles"]
        if bundle["envelope"]["runId"]
        == current_ids.get(bundle["envelope"]["experimentId"])
    }
    assert current_bundle_ids == current_ids


def test_benchmark_never_converts_missing_empirical_evidence_to_zero() -> None:
    benchmark = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert benchmark["programState"]["safeLabels"] == 0
    assert (
        benchmark["summary"]["experimentsWithEmpiricalClassificationEvidence"]
        == 0
    )
    for record in benchmark["evaluationRecords"]:
        empirical = record["empiricalMetrics"]
        assert empirical["status"] == "NOT_COMPUTABLE"
        assert empirical["accuracy"] is None
        assert empirical["macroF1"] is None
        assert empirical["netCorrection"] is None
        assert empirical["mcnemarP"] is None


def test_benchmark_distinguishes_execution_from_engineering_target() -> None:
    benchmark = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    records = {
        item["experimentId"]: item
        for item in benchmark["evaluationRecords"]
    }
    assert records["EXP-033"]["verdict"] == "MEASURED_PASS"
    assert records["EXP-035"]["verdict"] == "MEASURED_PASS"
    assert records["EXP-036"]["verdict"] == "MEASURED_PASS"
    assert records["EXP-036"]["dimensions"]["execution"]["status"] == "pass"
    assert not any(
        item["status"] == "missed"
        for item in records["EXP-036"]["engineeringSignals"]
    )
    assert benchmark["guardrailSummary"]["historicalMissed"] > (
        benchmark["guardrailSummary"]["missed"]
    )
    assert records["EXP-019"]["verdict"] == "GATED_NOT_RUN"
    assert records["EXP-019"]["executionState"] == "not_executed"
    highlights = {
        item["experimentId"]: item
        for item in benchmark["resultHighlights"]
    }
    parity = {
        item["metricId"]: item for item in highlights["EXP-033"]["metrics"]
    }
    assert parity["ARCH_SEMANTIC_PARITY_RATE"]["value"] == 1.0
    assert parity["ARCH_CLASSIFICATION_CHANGES"]["value"] == 0
    readiness = {
        item["metricId"]: item for item in highlights["EXP-040"]["metrics"]
    }
    assert readiness["THESIS_EMPIRICAL_IMPROVEMENT_CLAIMS_READY"]["value"] == 0


def test_standard_forbids_a_blended_value_score() -> None:
    standard = json.loads(STANDARD.read_text(encoding="utf-8"))
    assert standard["scoringRule"]["globalScoreAllowed"] is False
    assert [item["id"] for item in standard["baselineLadder"]] == [
        "B0",
        "B1",
        "B2",
        "B3",
        "B4",
        "B5",
    ]
    assert {item["id"] for item in standard["dimensions"]} == {
        "protocol",
        "data",
        "execution",
        "reproducibility",
        "safety",
        "comparability",
        "empiricalValidity",
    }


def test_benchmark_reports_are_fresh_offline_and_snapshot_driven() -> None:
    builder = load_script("build_experiment_benchmark.py")
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert REPORT_MD.read_text(encoding="utf-8") == builder.render_markdown(
        snapshot
    )
    content = REPORT_HTML.read_text(encoding="utf-8")
    assert content == builder.render_html(snapshot)
    assert "https://" not in content
    assert "http://" not in content
    assert "0/24 independent safe labels" in content
    assert "Every experiment evaluated" in content
    match = re.search(
        r'<script id="benchmark-data" type="application/json">(.*?)</script>',
        content,
        re.DOTALL,
    )
    assert match
    assert json.loads(match.group(1)) == snapshot
