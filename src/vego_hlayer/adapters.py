"""Deterministic adapters between legacy M1-M4B-1 artifacts and canonical records."""

from __future__ import annotations

import copy
import json
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import jsonschema

from .contracts import (
    AdviceRecord,
    ComparisonRecord,
    FeedbackRecord,
    MemoryRecord,
    ReviewItem,
    ValidationError,
    stable_identifier,
)

STAGES = frozenset(
    {"review", "feedback", "resolved", "memory", "advice", "comparison"}
)
ENVELOPE_FIELDS = {
    "advice": frozenset(
        {
            "schema_version",
            "setting_id",
            "advice_mode",
            "generated_at",
            "provenance",
            "advice",
        }
    ),
    "comparison": frozenset(
        {
            "schema_version",
            "setting_id",
            "mode",
            "policy_version",
            "ai_behavior_changed_in_baseline",
            "generated_at",
            "provenance",
            "comparisons",
        }
    ),
}
REPO_ROOT = Path(__file__).resolve().parents[2]
LEGACY_SCHEMA_FILES = {
    "review": "human_review_item.schema.json",
    "feedback": "human_feedback.schema.json",
    "resolved": "human_review_item.schema.json",
    "memory": "human_judgment.schema.json",
    "advice": "memory_advice.schema.json",
    "comparison": "memory_informed_comparison.schema.json",
}


@dataclass(frozen=True)
class AdapterResult:
    """Canonical view plus a deterministic, non-mutating legacy round trip."""

    stage: str
    records: tuple[dict[str, Any], ...]
    _legacy_payload: Any

    def to_legacy(self) -> Any:
        return serialize_canonical_artifact(
            self.stage,
            self.records,
            self._legacy_payload,
        )


def _serialize_review(record: dict[str, Any]) -> dict[str, Any]:
    """Rebuild a review item from the canonical evidence snapshot and identity."""

    snapshot = record.get("evidence_snapshot")
    if not isinstance(snapshot, dict):
        raise ValidationError("ReviewItem evidence_snapshot must be an object")
    item = copy.deepcopy(snapshot)
    item["review_id"] = record.get("review_id")
    item["review_signature"] = record.get("deduplication_key")
    return item


def _serialize_feedback(
    template: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    """Overlay every represented feedback field from the canonical record."""

    item = copy.deepcopy(template)
    item["feedback_id"] = record.get("feedback_id")
    item["review_id"] = record.get("review_id")
    item["review_signature"] = record.get("review_signature")
    item["expert_id"] = record.get("expert_id")
    item["timestamp"] = record.get("timestamp")
    item["human_decision"] = copy.deepcopy(record.get("human_decision") or {})
    if "reusable" in item:
        item["reusable"] = bool(record.get("reusable", False))
    if "reuse_scope" in item:
        item["reuse_scope"] = copy.deepcopy(record.get("reuse_scope") or {})
    if "notes" in item:
        item["notes"] = record.get("notes", "")
    return item


def _serialize_memory(
    template: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    item = copy.deepcopy(template)
    item["memory_id"] = record.get("memory_id")
    verification_id = str(record.get("verification_id") or "")
    if "source_feedback_id" in item and not verification_id.startswith("legacy:"):
        item["source_feedback_id"] = verification_id
    if "reuse_scope" in item:
        item["reuse_scope"] = copy.deepcopy(record.get("validity_scope") or {})
    if "conflicting_memory_ids" in item:
        item["conflicting_memory_ids"] = list(record.get("conflicts") or [])
    if "provenance" in item:
        item["provenance"] = copy.deepcopy(record.get("provenance") or {})
    return item


def _serialize_advice(
    template: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    item = copy.deepcopy(template)
    mapped = {
        "setting_id": record.get("setting_id"),
        "pattern_id": record.get("pattern_id"),
        "advice_strength": record.get("advice_strength"),
        "has_conflicting_memory": bool(record.get("has_conflicting_memory", False)),
        "advice_mode": record.get("advice_mode"),
        "ai_classification_changed": bool(
            record.get("ai_classification_changed", False)
        ),
    }
    for key, value in mapped.items():
        if key in item:
            item[key] = value
    matches = _record_list(item, "memory_matches")
    memory_ids = list(record.get("memory_match_ids") or [])
    if len(matches) != len(memory_ids):
        raise ValidationError("AdviceRecord memory match count changed during serialization")
    for match, memory_id in zip(matches, memory_ids, strict=True):
        if not isinstance(match, dict):
            raise ValidationError("legacy advice memory matches must be objects")
        match["memory_id"] = memory_id
    return item


def _serialize_comparison(
    template: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    item = copy.deepcopy(template)
    mapped = {
        "comparison_id": record.get("comparison_id"),
        "setting_id": record.get("setting_id"),
        "pattern_id": record.get("pattern_id"),
        "memory_informed_differs_from_original": bool(
            record.get("differs_from_original", False)
        ),
        "requires_human_review_after_memory": bool(
            record.get("requires_human_review", False)
        ),
        "human_memory_used": list(record.get("memory_match_ids") or []),
        "evaluation_leakage_status": record.get("leakage_status"),
        "rule_applied": record.get("rule_applied"),
        "decision_trace": list(record.get("decision_trace") or []),
        "mode": record.get("mode"),
        "ai_behavior_changed_in_baseline": bool(
            record.get("ai_behavior_changed_in_baseline", False)
        ),
    }
    for key, value in mapped.items():
        if key in item:
            item[key] = value
    original = item.get("original_agent4_classification")
    if isinstance(original, dict) and "classification" in original:
        original["classification"] = record.get("original_classification")
    parallel = item.get("memory_informed_classification")
    if isinstance(parallel, dict):
        if "classification" in parallel:
            parallel["classification"] = record.get("parallel_classification")
        if "source" in parallel:
            parallel["source"] = record.get("parallel_source")
    return item


def serialize_canonical_artifact(
    stage: str,
    records: tuple[dict[str, Any], ...],
    legacy_template: Any,
) -> Any:
    """Serialize canonical records back to the public legacy artifact shape.

    Unrepresented legacy fields are retained as a shape template, while every
    field represented by a canonical contract is written back from that
    contract. A mapping or serializer defect therefore changes the unified
    output and is caught by parity instead of being hidden by an untouched copy.
    """

    templates, _ = _items_and_provenance(stage, legacy_template)
    if len(templates) != len(records):
        raise ValidationError("canonical record count differs from the legacy artifact")
    serialized: list[dict[str, Any]] = []
    for template, record in zip(templates, records, strict=True):
        if not isinstance(template, dict):
            raise ValidationError(f"{stage} records must be objects")
        contract = record.get("contract")
        if stage == "review" or (stage == "resolved" and contract == "ReviewItem"):
            item = _serialize_review(record)
        elif stage == "feedback":
            item = _serialize_feedback(template, record)
        elif stage == "resolved" and contract == "FeedbackRecord":
            item = copy.deepcopy(template)
            feedback_template = item.get("human_feedback")
            if not isinstance(feedback_template, dict):
                raise ValidationError("resolved feedback template is missing")
            item["human_feedback"] = _serialize_feedback(feedback_template, record)
            item["feedback_id"] = record.get("feedback_id")
            item["review_id"] = record.get("review_id")
            item["review_signature"] = record.get("review_signature")
        elif stage == "memory":
            item = _serialize_memory(template, record)
        elif stage == "advice":
            item = _serialize_advice(template, record)
        elif stage == "comparison":
            item = _serialize_comparison(template, record)
        else:
            raise ValidationError(f"unsupported canonical record for {stage}: {contract!r}")
        serialized.append(item)

    if stage in {"review", "feedback", "resolved", "memory"}:
        return serialized
    envelope = copy.deepcopy(legacy_template)
    key = "advice" if stage == "advice" else "comparisons"
    envelope[key] = serialized
    if "provenance" in envelope and records:
        envelope["provenance"] = copy.deepcopy(records[0].get("provenance") or {})
    return envelope


def _require_exact_fields(
    value: Mapping[str, Any],
    required: frozenset[str],
    context: str,
) -> None:
    missing = sorted(required - set(value))
    if missing:
        raise ValidationError(
            f"{context} missing required fields: {', '.join(missing)}"
        )
    unexpected = sorted(set(value) - required)
    if unexpected:
        raise ValidationError(
            f"{context} has unexpected fields: {', '.join(unexpected)}"
        )


def _require_nonempty_text(value: Mapping[str, Any], key: str, context: str) -> None:
    if not isinstance(value.get(key), str) or not value[key]:
        raise ValidationError(f"{context} {key} must be a non-empty string")


@cache
def _legacy_validator(stage: str) -> jsonschema.Draft7Validator:
    schema_name = LEGACY_SCHEMA_FILES[stage]
    schema_path = REPO_ROOT / "VEGO-AI" / "schemas" / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return jsonschema.Draft7Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )


def _validate_schema_instance(
    stage: str,
    value: Any,
    *,
    context: str,
) -> None:
    errors = sorted(
        _legacy_validator(stage).iter_errors(value),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if not errors:
        return
    error = errors[0]
    location = ".".join(str(part) for part in error.absolute_path)
    suffix = f" at {location}" if location else ""
    raise ValidationError(
        f"{context} violates {LEGACY_SCHEMA_FILES[stage]}{suffix}: {error.message}"
    )


def _validate_legacy_artifact(stage: str, payload: Any) -> None:
    """Validate complete public legacy records before canonical adaptation."""

    if stage in {"advice", "comparison"}:
        _validate_schema_instance(stage, payload, context=f"{stage} payload")
        return
    if not isinstance(payload, list):
        raise ValidationError(f"{stage} payload must be a list")
    for index, item in enumerate(payload):
        schema_stage = "review" if stage == "resolved" else stage
        _validate_schema_instance(
            schema_stage,
            item,
            context=f"{stage} record {index}",
        )
        if stage == "resolved" and isinstance(item, Mapping):
            feedback = item.get("human_feedback")
            if feedback is not None:
                _validate_schema_instance(
                    "feedback",
                    feedback,
                    context=f"resolved record {index} human_feedback",
                )


def _validate_envelope(stage: str, payload: dict[str, Any]) -> dict[str, Any]:
    fields = ENVELOPE_FIELDS[stage]
    _require_exact_fields(payload, fields, f"{stage} envelope")
    for key in ("schema_version", "setting_id", "generated_at"):
        _require_nonempty_text(payload, key, f"{stage} envelope")

    provenance = payload["provenance"]
    if not isinstance(provenance, Mapping):
        raise ValidationError(f"{stage} provenance must be an object")
    if stage == "advice":
        if payload["advice_mode"] != "advisory_only":
            raise ValidationError("advice envelope must remain advisory_only")
        provenance_fields = frozenset(
            {"source_memory_file", "source_agent4_files"}
        )
        _require_exact_fields(
            provenance,
            provenance_fields,
            "advice provenance",
        )
        _require_nonempty_text(
            provenance,
            "source_memory_file",
            "advice provenance",
        )
        source_agent4 = provenance["source_agent4_files"]
        if not isinstance(source_agent4, Mapping):
            raise ValidationError(
                "advice provenance source_agent4_files must be an object"
            )
        _require_exact_fields(
            source_agent4,
            frozenset({"deviation_patterns", "variability_classes"}),
            "advice provenance source_agent4_files",
        )
        for key, value in source_agent4.items():
            if value is not None and not isinstance(value, str):
                raise ValidationError(
                    "advice provenance source_agent4_files "
                    f"{key} must be a string or null"
                )
    else:
        if payload["mode"] != "experimental":
            raise ValidationError("comparison envelope mode must be experimental")
        _require_nonempty_text(
            payload,
            "policy_version",
            "comparison envelope",
        )
        if payload["ai_behavior_changed_in_baseline"] is not False:
            raise ValidationError(
                "comparison envelope cannot change baseline AI behavior"
            )
        provenance_fields = frozenset(
            {
                "source_variability_classes",
                "source_memory_advice",
                "source_memory",
            }
        )
        _require_exact_fields(
            provenance,
            provenance_fields,
            "comparison provenance",
        )
        for key, value in provenance.items():
            if value is not None and not isinstance(value, str):
                raise ValidationError(
                    f"comparison provenance {key} must be a string or null"
                )
    return dict(provenance)


def _items_and_provenance(stage: str, payload: Any) -> tuple[list[dict], dict]:
    if stage in {"review", "feedback", "resolved", "memory"}:
        if not isinstance(payload, list):
            raise ValidationError(f"{stage} payload must be a list")
        return payload, {"source": f"legacy_{stage}_artifact"}
    if not isinstance(payload, dict):
        raise ValidationError(f"{stage} payload must be an object")
    provenance = _validate_envelope(stage, payload)
    key = "advice" if stage == "advice" else "comparisons"
    items = payload.get(key)
    if not isinstance(items, list):
        raise ValidationError(f"{stage} payload must contain a {key} list")
    return items, provenance


def _record_mapping(item: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    if key not in item:
        return {}
    value = item[key]
    if not isinstance(value, Mapping):
        raise ValidationError(f"{key} must be an object")
    return value


def _record_list(item: Mapping[str, Any], key: str) -> list[Any]:
    if key not in item:
        return []
    value = item[key]
    if not isinstance(value, list):
        raise ValidationError(f"{key} must be an array")
    return value


def _review_record(item: dict) -> ReviewItem:
    review_id = item.get("review_id", "")
    signature = item.get("review_signature", "")
    ai_decision = _record_mapping(item, "ai_decision")
    confidence = str(ai_decision.get("confidence") or "").lower()
    risk = "high" if confidence == "low" else "medium"
    status = item.get("status")
    due_state = "pending" if status in {"pending", "resolved"} else "parked"
    return ReviewItem(
        review_id=review_id,
        triage_id=stable_identifier("TRIAGE", {"review_id": review_id}),
        evidence_snapshot=copy.deepcopy(item),
        question=f"Review Agent 4 classification for {item.get('pattern_id', 'pattern')}",
        risk=risk,
        owner_role="human_reviewer",
        deduplication_key=signature,
        due_state=due_state,
        provenance=copy.deepcopy(
            item.get("provenance") or {"source": "legacy_review_item"}
        ),
    )


def _feedback_record(item: dict) -> FeedbackRecord:
    human_decision = _record_mapping(item, "human_decision")
    return FeedbackRecord(
        feedback_id=item.get("feedback_id", ""),
        review_id=item.get("review_id", ""),
        review_signature=item.get("review_signature", ""),
        expert_id=item.get("expert_id", ""),
        timestamp=item.get("timestamp", ""),
        human_decision=copy.deepcopy(human_decision),
        reusable=bool(item.get("reusable", False)),
        reuse_scope=copy.deepcopy(item.get("reuse_scope") or {}),
        evidence_refs=(item.get("review_id", ""),),
        rationale=str(human_decision.get("rationale") or ""),
        confidence=str(human_decision.get("confidence") or ""),
        notes=str(item.get("notes") or ""),
    )


def _memory_record(item: dict) -> MemoryRecord:
    scope = copy.deepcopy(item.get("reuse_scope") or {})
    if not scope:
        scope = {
            "domain": item.get("domain") or "unknown",
            "diagram_type": item.get("diagram_type") or "unknown",
        }
    conflicts = tuple(item.get("conflicting_memory_ids") or ())
    return MemoryRecord(
        memory_id=item.get("memory_id", ""),
        verification_id=str(
            item.get("source_feedback_id") or f"legacy:{item.get('memory_id', '')}"
        ),
        source_outcome="legacy_mechanism_memory",
        validity_scope=scope,
        conflicts=conflicts,
        provenance=copy.deepcopy(
            item.get("provenance") or {"source": "legacy_memory_artifact"}
        ),
        leakage_classification="unknown",
    )


def _advice_record(item: dict, provenance: dict) -> AdviceRecord:
    pattern_id = item.get("pattern_id", "")
    setting_id = item.get("setting_id", "")
    matches = _record_list(item, "memory_matches")
    memory_ids = tuple(
        match.get("memory_id", "")
        for match in matches
        if isinstance(match, dict) and match.get("memory_id")
    )
    return AdviceRecord(
        advice_id=stable_identifier(
            "ADV",
            {"setting_id": setting_id, "pattern_id": pattern_id, "matches": memory_ids},
        ),
        setting_id=setting_id,
        pattern_id=pattern_id,
        advice_strength=item.get("advice_strength", "none"),
        memory_match_ids=memory_ids,
        has_conflicting_memory=bool(item.get("has_conflicting_memory", False)),
        provenance=copy.deepcopy(provenance),
        advice_mode=item.get("advice_mode", "advisory_only"),
        ai_classification_changed=bool(item.get("ai_classification_changed", False)),
    )


def _comparison_record(item: dict, provenance: dict) -> ComparisonRecord:
    original = item.get("original_agent4_classification")
    parallel = item.get("memory_informed_classification")
    if not isinstance(original, Mapping):
        raise ValidationError(
            "original_agent4_classification must be an object"
        )
    if not isinstance(parallel, Mapping):
        raise ValidationError(
            "memory_informed_classification must be an object"
        )
    return ComparisonRecord(
        comparison_id=item.get("comparison_id", ""),
        setting_id=item.get("setting_id", ""),
        pattern_id=item.get("pattern_id", ""),
        original_classification=original.get("classification"),
        parallel_classification=parallel.get("classification"),
        parallel_source=parallel.get("source", ""),
        differs_from_original=bool(
            item.get("memory_informed_differs_from_original", False)
        ),
        requires_human_review=bool(
            item.get("requires_human_review_after_memory", False)
        ),
        memory_match_ids=tuple(item.get("human_memory_used") or ()),
        leakage_status=item.get("evaluation_leakage_status", "unknown"),
        rule_applied=item.get("rule_applied", ""),
        decision_trace=tuple(item.get("decision_trace") or ()),
        provenance=copy.deepcopy(provenance),
        mode=item.get("mode", "experimental"),
        ai_behavior_changed_in_baseline=bool(
            item.get("ai_behavior_changed_in_baseline", False)
        ),
    )


def adapt_legacy_artifact(stage: str, payload: Any) -> AdapterResult:
    """Validate a legacy artifact and expose canonical contract records."""

    if stage not in STAGES:
        raise ValidationError(f"unsupported legacy stage {stage!r}")
    legacy = copy.deepcopy(payload)
    _validate_legacy_artifact(stage, legacy)
    items, provenance = _items_and_provenance(stage, legacy)
    records: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            raise ValidationError(f"{stage} records must be objects")
        if stage == "review":
            record = _review_record(item)
        elif stage == "feedback":
            record = _feedback_record(item)
        elif stage == "resolved":
            if "human_feedback" in item:
                feedback = item["human_feedback"]
                if not isinstance(feedback, Mapping):
                    raise ValidationError(
                        "resolved human_feedback must be an object"
                    )
                record = _feedback_record(feedback)
            else:
                record = _review_record(item)
        elif stage == "memory":
            record = _memory_record(item)
        elif stage == "advice":
            record = _advice_record(item, provenance)
        else:
            record = _comparison_record(item, provenance)
        records.append(record.to_dict())
    return AdapterResult(stage=stage, records=tuple(records), _legacy_payload=legacy)
