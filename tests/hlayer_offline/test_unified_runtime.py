from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from vego_hlayer.adapters import AdapterResult, adapt_legacy_artifact
from vego_hlayer.contracts import MemoryRecord, ValidationError, contract_catalog
from vego_hlayer.runtime import apply_architecture_mode
from vego_hlayer.state_machine import TrustedMemoryStore


def _review_item() -> dict:
    return {
        "review_id": "HRQ-ucd_ch-P1",
        "review_signature": "0123456789abcdef",
        "status": "pending",
        "pattern_id": "P1",
        "provenance": {"source": "fixture"},
        "ai_decision": {
            "classification": "Occasional Variability",
            "confidence": "Medium",
        },
    }


def test_legacy_unified_and_parity_round_trip_without_semantic_change(tmp_path) -> None:
    payload = [_review_item()]
    legacy = apply_architecture_mode("review", payload, architecture_mode="legacy")
    unified = apply_architecture_mode("review", payload, architecture_mode="unified")
    manifest_path = tmp_path / "manifest.json"
    parity = apply_architecture_mode(
        "review",
        payload,
        architecture_mode="parity",
        manifest_path=manifest_path,
    )
    assert legacy.output == unified.output == parity.output == payload
    assert parity.manifest.parity_status == "match"
    assert parity.manifest.baseline_preserved is True
    persisted = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert persisted["published_output_sha256"] == persisted["legacy_output_sha256"]


def test_architecture_manifest_validates_against_schema() -> None:
    payload = [_review_item()]
    result = apply_architecture_mode("review", payload, architecture_mode="parity")
    repo_root = Path(__file__).resolve().parents[2]
    schema = json.loads(
        (repo_root / "schemas" / "architecture-run-manifest-v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(schema).validate(result.manifest.to_dict())


def test_contract_catalog_has_versioned_architecture_identity() -> None:
    catalog = contract_catalog()
    assert catalog["catalog"] == "ArchitectureContractCatalog-v1"
    assert catalog["schema_version"] == "1.0"
    assert {
        "ObservationRecord",
        "ReviewItem",
        "FeedbackRecord",
        "VerificationRecord",
        "MemoryRecord",
        "AdviceRecord",
        "ComparisonRecord",
        "ArchitectureRunManifest",
    } <= set(catalog["contracts"])


def test_parity_mismatch_fails_closed_to_legacy(monkeypatch) -> None:
    payload = [_review_item()]

    @dataclass(frozen=True)
    class ChangedAdapter:
        records: tuple[dict, ...] = ()

        def to_legacy(self):
            changed = [_review_item()]
            changed[0]["status"] = "resolved"
            return changed

    monkeypatch.setattr(
        "vego_hlayer.runtime.adapt_legacy_artifact",
        lambda stage, value: ChangedAdapter(),
    )
    result = apply_architecture_mode("review", payload, architecture_mode="parity")
    assert result.manifest.parity_status == "mismatch"
    assert result.output == payload
    assert result.manifest.failure_state == "normalized_output_mismatch"

    numeric_payload = [_review_item()]
    numeric_payload[0]["numeric_marker"] = 0

    @dataclass(frozen=True)
    class TypeChangedAdapter:
        records: tuple[dict, ...] = ()

        def to_legacy(self):
            changed = copy.deepcopy(numeric_payload)
            changed[0]["numeric_marker"] = False
            return changed

    monkeypatch.setattr(
        "vego_hlayer.runtime.adapt_legacy_artifact",
        lambda stage, value: TypeChangedAdapter(),
    )
    type_result = apply_architecture_mode(
        "review",
        numeric_payload,
        architecture_mode="parity",
    )
    assert type_result.manifest.parity_status == "mismatch"
    assert type_result.output == numeric_payload
    with pytest.raises(
        ValidationError,
        match="unified adapter changed public artifact semantics",
    ):
        apply_architecture_mode(
            "review",
            numeric_payload,
            architecture_mode="unified",
        )


def test_unified_serializer_rebuilds_mapped_fields_from_canonical_records() -> None:
    payload = [_review_item()]
    adapted = adapt_legacy_artifact("review", payload)
    changed = copy.deepcopy(adapted.records[0])
    changed["deduplication_key"] = "fedcba9876543210"
    rebuilt = AdapterResult(
        stage="review",
        records=(changed,),
        _legacy_payload=payload,
    ).to_legacy()
    assert rebuilt[0]["review_signature"] == "fedcba9876543210"
    assert rebuilt != payload

    for invalid_feedback in ("invalid", [], None, 0):
        malformed = [_review_item()]
        malformed[0]["human_feedback"] = invalid_feedback
        with pytest.raises(
            ValidationError,
            match="resolved human_feedback must be an object",
        ):
            adapt_legacy_artifact("resolved", malformed)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("original_agent4_classification", "Occasional Variability"),
        ("memory_informed_classification", ["Occasional Variability"]),
    ],
)
def test_comparison_adapter_rejects_nonobject_nested_classifications(
    field: str,
    value: object,
) -> None:
    payload = {
        "schema_version": "1.0",
        "setting_id": "ucd_ch",
        "mode": "experimental",
        "policy_version": "memory-informed-classifier-v1",
        "ai_behavior_changed_in_baseline": False,
        "generated_at": "2026-07-25T00:00:00Z",
        "comparisons": [
            {
                "comparison_id": "CMP-ucd_ch-P1",
                "setting_id": "ucd_ch",
                "pattern_id": "P1",
                "original_agent4_classification": {
                    "classification": "Occasional Variability",
                },
                "memory_informed_classification": {
                    "classification": "Occasional Variability",
                    "source": "original_agent4",
                },
                "memory_informed_differs_from_original": False,
                "requires_human_review_after_memory": False,
                "human_memory_used": [],
                "evaluation_leakage_status": "none",
                "rule_applied": "preserve_original",
                "decision_trace": ["baseline preserved"],
                "mode": "experimental",
                "ai_behavior_changed_in_baseline": False,
            }
        ],
        "provenance": {
            "source_variability_classes": "fixture-classes.json",
            "source_memory_advice": "fixture-advice.json",
            "source_memory": "fixture-memory.jsonl",
        },
    }
    payload["comparisons"][0][field] = value
    with pytest.raises(ValidationError, match=rf"{field} must be an object"):
        adapt_legacy_artifact("comparison", payload)


def test_manifest_rejects_a_symlinked_parent(tmp_path: Path) -> None:
    protected = tmp_path / "eval_output"
    protected.mkdir()
    alias = tmp_path / "alias"
    try:
        alias.symlink_to(protected, target_is_directory=True)
    except OSError:
        pytest.skip("symbolic links are unavailable on this host")
    with pytest.raises(ValidationError, match="symbolic links"):
        apply_architecture_mode(
            "review",
            [_review_item()],
            architecture_mode="parity",
            manifest_path=alias / "manifest.json",
        )


def test_legacy_memory_is_valid_advisory_evidence_but_not_trusted_memory() -> None:
    record = MemoryRecord(
        memory_id="HJM-ucd_ch-P1",
        verification_id="legacy:HF-1",
        source_outcome="legacy_mechanism_memory",
        validity_scope={"domain": "cheers"},
        conflicts=(),
        provenance={"source": "fixture"},
        leakage_classification="unknown",
    )
    assert record.trusted is False
    with pytest.raises(ValidationError, match="advisory evidence"):
        TrustedMemoryStore().append(record)
