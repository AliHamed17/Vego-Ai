from __future__ import annotations

import pytest
from hlayer_offline.contracts import (
    CorrectionProposal,
    FeedbackRecord,
    MemoryRecord,
    ObservationRecord,
    ValidationError,
    VerificationRecord,
)
from hlayer_offline.state_machine import ReviewState, ReviewStateMachine, route_observation


def captured_observation(event_type: str = "E1") -> ObservationRecord:
    return ObservationRecord(
        observation_id=f"OBS-{event_type}",
        event_type=event_type,
        run_id="fixture-run",
        setting_id="ucd_ch",
        producer="fixture",
        channel="artifact",
        sequence=1,
        capture_status="observed",
        source_artifact="fixture.json",
        source_sha256="a" * 64,
        payload={},
    )


def test_captured_observation_requires_source_lineage() -> None:
    with pytest.raises(ValidationError, match="source_artifact"):
        ObservationRecord(
            observation_id="OBS-invalid",
            event_type="E1",
            run_id="run",
            setting_id="setting",
            producer="fixture",
            channel="artifact",
            sequence=1,
            capture_status="observed",
            payload={},
        )


def test_unobservable_observation_requires_gap_and_forbids_fabricated_lineage() -> None:
    with pytest.raises(ValidationError, match="must not fabricate"):
        ObservationRecord(
            observation_id="OBS-invalid-gap",
            event_type="E3",
            run_id="run",
            setting_id="setting",
            producer="fixture",
            channel="qa",
            sequence=1,
            capture_status="unobservable",
            source_artifact="invented.json",
            source_sha256="b" * 64,
            gap_reason="not persisted",
            payload={},
        )


def test_e15_is_parked_even_when_triggered() -> None:
    decision = route_observation(
        captured_observation("E15"), severity=3, trigger_codes=("evaluation",)
    )
    assert decision.outcome == "park"
    assert decision.budget_state == "evaluation_only"


def test_state_machine_allows_declared_path_and_blocks_shortcut() -> None:
    machine = ReviewStateMachine()
    machine.transition(ReviewState.PROMOTED)
    machine.transition(ReviewState.PENDING_REVIEW)
    machine.transition(ReviewState.FEEDBACK_RECEIVED)
    machine.transition(ReviewState.VERIFIED)
    machine.transition(ReviewState.PENDING_CORRECTION_APPROVAL)
    machine.transition(ReviewState.APPROVED)
    assert machine.state == ReviewState.APPROVED
    with pytest.raises(ValidationError, match="illegal state transition"):
        ReviewStateMachine().transition(ReviewState.APPROVED)


def test_timeout_preserves_baseline_and_parks() -> None:
    machine = ReviewStateMachine()
    machine.transition(ReviewState.PROMOTED)
    machine.transition(ReviewState.PENDING_REVIEW)
    outcome = machine.timeout()
    assert outcome == {
        "state": "timed_out_parked",
        "baseline_preserved": True,
        "correction_applied": False,
        "trusted_memory_written": False,
    }


def test_feedback_crosswalk_uses_existing_schema_fields() -> None:
    feedback = FeedbackRecord(
        feedback_id="HF-fixture",
        review_id="HRQ-fixture-P1",
        review_signature="0123456789abcdef",
        expert_id="reviewer-fixture",
        timestamp="2026-07-10T00:00:00Z",
        human_decision={"decision_type": "ambiguous", "confidence": "High"},
        reusable=False,
        reuse_scope={},
        evidence_refs=("fixture:one",),
        rationale="Synthetic fixture.",
        confidence="High",
    )
    crosswalk = feedback.to_human_feedback_crosswalk()
    assert crosswalk["feedback_id"] == feedback.feedback_id
    assert crosswalk["review_signature"] == feedback.review_signature
    assert crosswalk["human_decision"] == feedback.human_decision


def test_feedback_review_id_must_match_existing_hrq_pattern() -> None:
    with pytest.raises(ValidationError, match="existing HRQ pattern"):
        FeedbackRecord(
            feedback_id="HF-invalid",
            review_id="REVIEW-not-compatible",
            review_signature="0123456789abcdef",
            expert_id="reviewer-fixture",
            timestamp="2026-07-10T00:00:00Z",
            human_decision={"decision_type": "ambiguous", "confidence": "High"},
            reusable=False,
            reuse_scope={},
            evidence_refs=("fixture:one",),
            rationale="Synthetic fixture.",
            confidence="High",
        )


def test_unresolved_verification_cannot_be_called_verified_or_written_to_memory() -> None:
    with pytest.raises(ValidationError, match="verified records cannot retain conflicts"):
        VerificationRecord(
            verification_id="VERIFY-invalid",
            feedback_id="HF-invalid",
            deterministic_checks=("source:conflict",),
            source_versions={"source": "fixture"},
            conflicts=("unresolved",),
            rounds=1,
            outcome="verified",
        )
    with pytest.raises(ValidationError, match="trusted memory requires"):
        MemoryRecord(
            memory_id="MEM-invalid",
            verification_id="VERIFY-invalid",
            source_outcome="needs_adjudication",
            validity_scope={"case": "fixture"},
            conflicts=("unresolved",),
            provenance={"source": "fixture"},
            leakage_classification="unknown",
        )


def test_offline_correction_proposal_can_never_be_applied() -> None:
    with pytest.raises(ValidationError, match="can never be applied"):
        CorrectionProposal(
            proposal_id="PROPOSAL-invalid",
            verification_id="VERIFY-valid",
            target_artifact="fixture.txt",
            target_sha256="c" * 64,
            proposed_diff="--- a\n+++ b\n",
            evidence_refs=("fixture:evidence",),
            rollback_description="Discard copy.",
            approval_state="approved",
            applied=True,
        )
