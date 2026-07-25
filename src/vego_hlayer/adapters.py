"""Deterministic adapters between legacy M1-M4B-1 artifacts and canonical records."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

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


@dataclass(frozen=True)
class AdapterResult:
    """Canonical view plus an exact, non-mutating legacy round trip."""

    stage: str
    records: tuple[dict[str, Any], ...]
    _legacy_payload: Any

    def to_legacy(self) -> Any:
        return copy.deepcopy(self._legacy_payload)


def _items_and_provenance(stage: str, payload: Any) -> tuple[list[dict], dict]:
    if stage in {"review", "feedback", "resolved", "memory"}:
        if not isinstance(payload, list):
            raise ValidationError(f"{stage} payload must be a list")
        return payload, {"source": f"legacy_{stage}_artifact"}
    if not isinstance(payload, dict):
        raise ValidationError(f"{stage} payload must be an object")
    key = "advice" if stage == "advice" else "comparisons"
    items = payload.get(key)
    if not isinstance(items, list):
        raise ValidationError(f"{stage} payload must contain a {key} list")
    provenance = payload.get("provenance") or {"source": f"legacy_{stage}_artifact"}
    if not isinstance(provenance, dict):
        raise ValidationError(f"{stage} provenance must be an object")
    return items, provenance


def _review_record(item: dict) -> ReviewItem:
    review_id = item.get("review_id", "")
    signature = item.get("review_signature", "")
    ai_decision = item.get("ai_decision") or {}
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
    human_decision = item.get("human_decision") or {}
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
        rationale=str(human_decision.get("rationale") or item.get("notes") or ""),
        confidence=str(human_decision.get("confidence") or ""),
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
    matches = item.get("memory_matches") or []
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
    original = item.get("original_agent4_classification") or {}
    parallel = item.get("memory_informed_classification") or {}
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
            feedback = item.get("human_feedback")
            record = _feedback_record(feedback) if feedback else _review_record(item)
        elif stage == "memory":
            record = _memory_record(item)
        elif stage == "advice":
            record = _advice_record(item, provenance)
        else:
            record = _comparison_record(item, provenance)
        records.append(record.to_dict())
    return AdapterResult(stage=stage, records=tuple(records), _legacy_payload=legacy)
