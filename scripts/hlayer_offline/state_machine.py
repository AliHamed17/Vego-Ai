"""Safety-preserving offline H-layer review state machine."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .contracts import (
    MemoryRecord,
    ObservationRecord,
    TriageDecision,
    ValidationError,
    stable_identifier,
)


class ReviewState(str, Enum):
    OBSERVED = "observed"
    PROMOTED = "promoted"
    PARKED = "parked"
    PENDING_REVIEW = "pending_review"
    FEEDBACK_RECEIVED = "feedback_received"
    TIMED_OUT_PARKED = "timed_out_parked"
    VERIFIED = "verified"
    REVISED = "revised"
    NEEDS_ADJUDICATION = "needs_adjudication"
    PENDING_CORRECTION_APPROVAL = "pending_correction_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"


ALLOWED_TRANSITIONS: Mapping[ReviewState, frozenset[ReviewState]] = {
    ReviewState.OBSERVED: frozenset({ReviewState.PROMOTED, ReviewState.PARKED}),
    ReviewState.PROMOTED: frozenset({ReviewState.PENDING_REVIEW}),
    ReviewState.PENDING_REVIEW: frozenset(
        {ReviewState.FEEDBACK_RECEIVED, ReviewState.TIMED_OUT_PARKED}
    ),
    ReviewState.FEEDBACK_RECEIVED: frozenset(
        {ReviewState.VERIFIED, ReviewState.REVISED, ReviewState.NEEDS_ADJUDICATION}
    ),
    ReviewState.REVISED: frozenset({ReviewState.PENDING_REVIEW}),
    ReviewState.VERIFIED: frozenset({ReviewState.PENDING_CORRECTION_APPROVAL}),
    ReviewState.PENDING_CORRECTION_APPROVAL: frozenset(
        {ReviewState.APPROVED, ReviewState.REJECTED, ReviewState.DEFERRED}
    ),
    ReviewState.PARKED: frozenset(),
    ReviewState.TIMED_OUT_PARKED: frozenset(),
    ReviewState.NEEDS_ADJUDICATION: frozenset(),
    ReviewState.APPROVED: frozenset(),
    ReviewState.REJECTED: frozenset(),
    ReviewState.DEFERRED: frozenset(),
}


@dataclass
class ReviewStateMachine:
    state: ReviewState = ReviewState.OBSERVED

    def __post_init__(self) -> None:
        self.history: list[str] = [self.state.value]

    def transition(self, target: ReviewState | str) -> ReviewState:
        target_state = ReviewState(target)
        if target_state not in ALLOWED_TRANSITIONS[self.state]:
            raise ValidationError(
                f"illegal state transition {self.state.value} -> {target_state.value}"
            )
        self.state = target_state
        self.history.append(target_state.value)
        return self.state

    def timeout(self) -> dict[str, Any]:
        self.transition(ReviewState.TIMED_OUT_PARKED)
        return {
            "state": self.state.value,
            "baseline_preserved": True,
            "correction_applied": False,
            "trusted_memory_written": False,
        }


def route_observation(
    observation: ObservationRecord,
    *,
    severity: int,
    trigger_codes: Iterable[str] = (),
    dosage_config: Mapping[str, Any] | None = None,
    bundle_key: str | None = None,
    within_budget: bool = True,
) -> TriageDecision:
    """Route a record without treating any configurable proposal as a default.

    E15 is always parked in the evaluation-only track. Other events are promoted
    only when an explicit trigger is supplied and budget is available.
    """

    triggers = tuple(sorted(set(trigger_codes)))
    config = dict(dosage_config or {"mode": "explicit_fixture"})
    bundle = (
        bundle_key
        or f"{observation.setting_id}|{observation.case_id or observation.observation_id}"
    )
    if observation.event_type == "E15":
        outcome = "park"
        budget_state = "evaluation_only"
        rationale = (
            "E15 belongs to the parked evaluation track and cannot create a framework action."
        )
    elif observation.capture_status == "unobservable":
        outcome = "park"
        budget_state = "deferred"
        rationale = "The event remains an explicit instrumentation gap; no evidence was fabricated."
    elif not within_budget:
        outcome = "park"
        budget_state = "deferred"
        rationale = (
            "The explicit fixture budget is exhausted; the item remains parked "
            "for a later checkpoint."
        )
    elif triggers:
        outcome = "promote"
        budget_state = "within_budget"
        rationale = "An explicit fixture trigger promoted the observation for offline review."
    else:
        outcome = "park"
        budget_state = "within_budget"
        rationale = "No explicit trigger was supplied; no routing default was inferred."
    triage_id = stable_identifier(
        "TRIAGE",
        {
            "observation_ids": [observation.observation_id],
            "triggers": triggers,
            "severity": severity,
            "config": config,
            "bundle": bundle,
            "outcome": outcome,
        },
    )
    return TriageDecision(
        triage_id=triage_id,
        observation_ids=(observation.observation_id,),
        trigger_codes=triggers,
        severity=severity,
        dosage_config=config,
        bundle_key=bundle,
        budget_state=budget_state,
        outcome=outcome,
        rationale=rationale,
    )


class TrustedMemoryStore:
    """In-memory test double that refuses synthetic or unresolved records."""

    def __init__(self) -> None:
        self._records: list[MemoryRecord] = []

    def append(self, record: MemoryRecord) -> None:
        if record.provenance.get("synthetic_tag") == "SYNTHETIC_NOT_HUMAN":
            raise ValidationError("synthetic fixtures cannot enter trusted memory")
        self._records.append(record)

    @property
    def records(self) -> tuple[MemoryRecord, ...]:
        return tuple(self._records)
