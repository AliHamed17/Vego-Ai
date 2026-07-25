from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest
from docx import Document

ROOT = Path(__file__).resolve().parents[2]
BUILDER_PATH = ROOT / "scripts/build_thesis_evidence_package.py"
SNAPSHOT_PATH = (
    ROOT / "docs/research/thesis-evidence/thesis-evidence-snapshot-v1.json"
)
SCHEMA_DIR = ROOT / "schemas"
MANIFEST_PATH = (
    ROOT / "docs/research/thesis-evidence/THESIS_REVIEW_PACKAGE_MANIFEST.json"
)
THESIS_DOCX_PATH = (
    ROOT
    / "thesis/output/VEGO-AI-MSc-Thesis-Evidence-Ready-Draft-2026-07-25.docx"
)


def load_builder():
    spec = importlib.util.spec_from_file_location("build_thesis_evidence_package", BUILDER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def validate(schema: dict, instance: dict) -> None:
    jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    ).validate(instance)


def test_snapshot_has_fixed_baseline_and_experiment_ladders() -> None:
    data = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    assert [item["id"] for item in data["baselines"]] == [
        "B0",
        "B1",
        "B2",
        "B3",
        "B4",
        "B5",
    ]
    assert [item["id"] for item in data["experiments"]] == [
        f"EXP-{number:03d}" for number in range(19, 28)
    ]
    assert [item["id"] for item in data["runtimeHardening"]["modes"]] == [
        "legacy",
        "unified",
        "parity",
    ]
    assert data["runtimeHardening"]["defaultMode"] == "legacy"
    assert [
        item["id"]
        for item in data["runtimeHardening"]["modelBoundary"]["protocols"]
    ] == ["EXP-028", "EXP-029"]
    assert (
        data["runtimeHardening"]["parityEvidence"]["classificationChangeCount"]
        == 0
    )
    assert all(item["behaviorChanged"] is False for item in data["baselines"])


def test_zero_label_gate_keeps_all_accuracy_fields_null() -> None:
    data = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    assert data["labelGate"]["generalizationSafeLabels"] == 0
    assert data["labelGate"]["accuracyStatus"] == "NOT YET COMPUTABLE"
    current = data["metrics"]["currentResults"]
    assert current["status"] == "NOT YET COMPUTABLE"
    assert current["originalAccuracy"] is None
    assert current["candidateAccuracy"] is None
    assert current["originalMacroF1"] is None
    assert current["candidateMacroF1"] is None
    assert current["netCorrection"] is None
    assert current["pairedPValue"] is None


def test_snapshot_validates_against_document_schema() -> None:
    validate(
        load_schema("thesis-evidence-snapshot-v1.schema.json"),
        json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8")),
    )


def test_portable_review_manifest_validates_without_personal_paths() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    validate(
        load_schema("thesis-review-package-manifest-v1.schema.json"),
        manifest,
    )
    serialized = json.dumps(manifest)
    assert "C:\\\\" not in serialized
    assert "featureCodeImplemented" not in manifest
    assert manifest["runtimeFeatureCodeImplemented"] is False
    assert manifest["researchInfrastructureImplemented"] is True


def test_builder_is_byte_deterministic_without_timestamp_refresh() -> None:
    builder = load_builder()
    first = builder.build_snapshot(False)
    second = builder.build_snapshot(False)
    assert json.dumps(first, ensure_ascii=False, sort_keys=True) == json.dumps(
        second, ensure_ascii=False, sort_keys=True
    )


def test_canonical_source_hash_normalizes_checkout_line_endings(
    tmp_path: Path,
) -> None:
    builder = load_builder()
    lf = tmp_path / "lf.ps1"
    crlf = tmp_path / "crlf.ps1"
    lf.write_bytes(b"Write-Output 'ok'\n")
    crlf.write_bytes(b"Write-Output 'ok'\r\n")
    assert builder.sha256_portable_text_file(
        lf
    ) == builder.sha256_portable_text_file(crlf)


def test_gold_label_schema_rejects_synthetic_reviewer() -> None:
    schema = load_schema("gold-label-record-v2.schema.json")
    record = {
        "schemaVersion": "GoldLabelRecord-v2",
        "recordType": "raw_review",
        "recordId": "GLR-A01",
        "anonymousItemId": "A01",
        "partition": "development",
        "reviewerId": "SYNTHETIC_NOT_HUMAN",
        "reviewerRole": "reviewer_1",
        "expertLabel": "Substantial Variability",
        "expertRationale": "Human rationale would be required.",
        "confidence": "Medium",
        "reviewDate": "2026-07-24",
        "leakageClass": "none",
        "generalizationSafe": True,
        "sourceSheetSha256": "a" * 64,
        "annotationProtocolVersion": "1.0",
        "adjudicationStatus": "not_required",
        "immutable": True,
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(schema, record)


def test_gold_label_schema_rejects_same_pattern_as_safe() -> None:
    schema = load_schema("gold-label-record-v2.schema.json")
    record = {
        "schemaVersion": "GoldLabelRecord-v2",
        "recordType": "raw_review",
        "recordId": "GLR-CAL01",
        "anonymousItemId": "CAL01",
        "partition": "calibration",
        "reviewerId": "reviewer-1",
        "reviewerRole": "reviewer_1",
        "expertLabel": "Occasional Variability",
        "expertRationale": "Independent calibration rationale.",
        "confidence": "High",
        "reviewDate": "2026-07-24",
        "leakageClass": "same_pattern_memory_used",
        "generalizationSafe": True,
        "sourceSheetSha256": "b" * 64,
        "annotationProtocolVersion": "1.0",
        "adjudicationStatus": "not_required",
        "immutable": True,
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(schema, record)


def test_evaluation_manifest_forces_null_metrics_at_safe_n_zero() -> None:
    schema = load_schema("evaluation-run-manifest-v2.schema.json")
    manifest = {
        "schemaVersion": "EvaluationRunManifest-v2",
        "runId": "exp020-zero-label-check",
        "experimentId": "EXP-020",
        "generatedAt": "2026-07-24T00:00:00+03:00",
        "sourceRevision": "c" * 40,
        "workingTreeState": "clean",
        "runClass": "development",
        "baselineHashes": {"agent4": "d" * 64},
        "inputHashes": {"labels": "e" * 64},
        "outputHashes": {},
        "labelStats": {
            "candidateRows": 24,
            "suppliedLabels": 0,
            "validLabels": 0,
            "generalizationSafeLabels": 0,
            "reviewerCount": 0,
            "adjudicatedRows": 0,
        },
        "partition": {
            "role": "none",
            "manifestSha256": None,
            "sealedBeforePolicyFreeze": False,
        },
        "policy": {
            "policyId": "memory-informed-classifier-v1",
            "policySha256": None,
            "status": "Implemented baseline comparator",
        },
        "randomization": {
            "annotationSeed": 20260721,
            "partitionSeed": 20260721,
            "bootstrapSeed": 20260721,
            "bootstrapReplicates": 10000,
        },
        "metrics": {
            "status": "NOT YET COMPUTABLE",
            "originalAccuracy": None,
            "candidateAccuracy": None,
            "originalMacroF1": None,
            "candidateMacroF1": None,
            "netCorrection": None,
            "pairedPValue": None,
        },
        "claimScope": "Gate validation only; no empirical performance result.",
        "protectedRuntimeChanged": False,
    }
    validate(schema, manifest)
    manifest["metrics"]["originalAccuracy"] = 1.0
    with pytest.raises(jsonschema.ValidationError):
        validate(schema, manifest)


def test_policy_schema_forbids_mutation_and_unapproved_statuses() -> None:
    schema = load_schema("policy-candidate-record-v1.schema.json")
    record = {
        "schemaVersion": "PolicyCandidateRecord-v1",
        "policyId": "PC-DEV-001",
        "policyVersion": "0.1",
        "status": "Proposal — not approved",
        "createdAt": "2026-07-24T00:00:00+03:00",
        "developmentPartitionSha256": "f" * 64,
        "labelSetSha256": "1" * 64,
        "deterministicRules": [
            {
                "ruleId": "R1",
                "condition": "Strong, conflict-free, safe advice and low baseline confidence",
                "parallelProposal": "Propose the memory-supported class for human approval",
                "fallback": "Preserve baseline and request or park human review",
            }
        ],
        "evidenceThresholds": {
            "minimumDevelopmentErrors": 3,
            "minimumSettingsRepresented": 2,
            "conflictFreeRequired": True,
            "generalizationSafeRequired": True,
        },
        "allowedOutput": "parallel_proposal_only",
        "baselineMutationAllowed": False,
        "protectedRuntimeChangeAllowed": False,
        "runtimeEffect": "none",
        "safetyBehavior": {
            "onMissingEvidence": "Preserve baseline and park or request human review",
            "onConflict": "Preserve baseline and request human adjudication",
            "onTimeout": "Preserve baseline and park the item",
        },
        "supervisorApproval": {
            "required": True,
            "outcome": "Not recorded",
            "recordId": None,
        },
        "claimBoundary": "Development proposal only.",
    }
    validate(schema, record)
    record["baselineMutationAllowed"] = True
    with pytest.raises(jsonschema.ValidationError):
        validate(schema, record)


def test_schema_examples_validate_and_unsafe_fixture_is_rejected() -> None:
    validator_path = ROOT / "scripts/validate_research_records.py"
    spec = importlib.util.spec_from_file_location(
        "validate_research_records", validator_path
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    examples = SCHEMA_DIR / "examples"
    for path in sorted(examples.glob("*.valid.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        assert module.validate_record(record) == [], path.name
    unsafe = json.loads(
        (examples / "policy-baseline-mutation.invalid.json").read_text(
            encoding="utf-8"
        )
    )
    assert module.validate_record(unsafe)


def test_evaluation_semantics_reject_invalid_count_order() -> None:
    validator_path = ROOT / "scripts/validate_research_records.py"
    spec = importlib.util.spec_from_file_location(
        "validate_research_records_counts", validator_path
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    record = json.loads(
        (
            SCHEMA_DIR / "examples/evaluation-pilot.valid.json"
        ).read_text(encoding="utf-8")
    )
    record["labelStats"]["generalizationSafeLabels"] = 13
    assert any(
        "generalizationSafeLabels" in error
        for error in module.validate_record(record)
    )


def test_policy_semantics_reject_duplicate_rule_ids() -> None:
    validator_path = ROOT / "scripts/validate_research_records.py"
    spec = importlib.util.spec_from_file_location(
        "validate_research_records_policy", validator_path
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    record = json.loads(
        (SCHEMA_DIR / "examples/policy-frozen.valid.json").read_text(
            encoding="utf-8"
        )
    )
    record["deterministicRules"].append(dict(record["deterministicRules"][0]))
    assert "deterministicRules must have unique ruleId values" in module.validate_record(
        record
    )


def test_registry_contains_each_new_experiment_once() -> None:
    registry = (ROOT / "experiments/registry.md").read_text(encoding="utf-8")
    for number in range(19, 30):
        assert registry.count(f"| EXP-{number:03d} |") == 1


def test_chapter_transitions_use_page_break_before_without_blank_break_paragraphs() -> None:
    document = Document(THESIS_DOCX_PATH)
    chapter_headings = [
        paragraph
        for paragraph in document.paragraphs
        if paragraph.style.name == "Heading 1"
        and paragraph.text.startswith("Chapter ")
    ]
    assert len(chapter_headings) == 11
    assert all(
        heading.paragraph_format.page_break_before is True
        for heading in chapter_headings
    )
