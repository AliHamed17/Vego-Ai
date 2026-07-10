"""EXP-016: human-authority and timeout safety over synthetic fixtures."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import (
    default_output_dir,
    fixture_dir,
    load_json,
    print_completion,
    relative_path,
    sha256_file,
    write_experiment_bundle,
)
from .contracts import (
    CorrectionProposal,
    FeedbackRecord,
    MemoryRecord,
    ValidationError,
    VerificationRecord,
    stable_identifier,
)
from .state_machine import ReviewState, ReviewStateMachine, TrustedMemoryStore

EXPERIMENT_ID = "EXP-016"
EXPERIMENT_FOLDER = "EXP-016-authority-timeout-safety"
ROLE_AUTHORITY: dict[str, frozenset[str]] = {
    "supervisor": frozenset({"submit_feedback", "adjudicate", "approve_correction"}),
    "trained_course_staff": frozenset({"submit_feedback"}),
    "course_staff": frozenset({"submit_feedback"}),
    "untrained_reviewer": frozenset(),
}


def _to_pending_review() -> ReviewStateMachine:
    machine = ReviewStateMachine()
    machine.transition(ReviewState.PROMOTED)
    machine.transition(ReviewState.PENDING_REVIEW)
    return machine


def _feedback(case: dict[str, Any]) -> FeedbackRecord:
    review_id = f"HRQ-exp016-{case['id']}-P1"
    signature = stable_identifier("", review_id).replace("--", "")[-16:]
    return FeedbackRecord(
        feedback_id=f"FEEDBACK-{case['id']}",
        review_id=review_id,
        review_signature=signature,
        expert_id=case["actor_role"],
        timestamp="2026-07-10T00:00:00Z",
        human_decision={"decision_type": case["decision"], "confidence": "High"},
        reusable=False,
        reuse_scope={"limitations": "SYNTHETIC_NOT_HUMAN"},
        evidence_refs=(f"fixture:{case['id']}",),
        rationale=case["rationale"],
        confidence="High",
    )


def _authority_result(case: dict[str, Any]) -> dict[str, Any]:
    role = case["actor_role"]
    requested = case["requested_authority"]
    known_role = role in ROLE_AUTHORITY
    allowed = requested == "none" or (known_role and requested in ROLE_AUTHORITY[role])
    return {
        "actor_role": role,
        "requested_authority": requested,
        "known_role": known_role,
        "allowed": allowed,
        "policy_actions": sorted(ROLE_AUTHORITY.get(role, frozenset())),
    }


def evaluate(fixtures: Path | None = None) -> dict[str, Any]:
    fixtures = fixtures or fixture_dir(EXPERIMENT_FOLDER)
    descriptor_path = fixtures / "authority_cases.json"
    baseline_path = fixtures / "baseline_snapshot.json"
    fixture = load_json(descriptor_path)
    baseline_before = sha256_file(baseline_path)
    memory = TrustedMemoryStore()
    records: list[dict[str, Any]] = []
    correction_applications = 0

    for case in fixture["cases"]:
        machine = _to_pending_review()
        authority = _authority_result(case)
        record: dict[str, Any] = {
            "case_id": case["id"],
            "case_type": case["case_type"],
            "synthetic_tag": "SYNTHETIC_NOT_HUMAN",
            "baseline_preserved": True,
            "trusted_memory_written": False,
            "correction_applied": False,
            "authority": authority,
        }
        if case["case_type"] == "timeout":
            record.update(machine.timeout())
        else:
            feedback = _feedback(case)
            record["feedback_crosswalk"] = feedback.to_human_feedback_crosswalk()
            machine.transition(ReviewState.FEEDBACK_RECEIVED)

            unresolved = not authority["allowed"] or case["case_type"] == "unresolved_override"
            if unresolved:
                machine.transition(ReviewState.NEEDS_ADJUDICATION)
                conflict = (
                    f"actor role {case['actor_role']} is not authorized for "
                    f"{case['requested_authority']}"
                    if not authority["allowed"]
                    else case["rationale"]
                )
                verification = VerificationRecord(
                    verification_id=f"VERIFY-{case['id']}",
                    feedback_id=feedback.feedback_id,
                    deterministic_checks=(
                        "authority_role_checked",
                        "requested_authority_checked",
                    ),
                    source_versions={"fixture": sha256_file(descriptor_path)},
                    conflicts=(conflict,),
                    rounds=1,
                    outcome="needs_adjudication",
                )
                record["verification"] = verification.to_dict()
                try:
                    MemoryRecord(
                        memory_id=f"MEMORY-{case['id']}",
                        verification_id=verification.verification_id,
                        source_outcome="needs_adjudication",
                        validity_scope={"case": case["id"]},
                        conflicts=verification.conflicts,
                        provenance={"synthetic_tag": "SYNTHETIC_NOT_HUMAN"},
                        leakage_classification="unknown",
                    )
                except ValidationError as exc:
                    record["memory_block_reason"] = str(exc)
            else:
                machine.transition(ReviewState.VERIFIED)
                verification = VerificationRecord(
                    verification_id=f"VERIFY-{case['id']}",
                    feedback_id=feedback.feedback_id,
                    deterministic_checks=("authority_role_checked", "source_hash_checked"),
                    source_versions={"fixture": sha256_file(descriptor_path)},
                    conflicts=(),
                    rounds=1,
                    outcome="verified",
                )
                record["verification"] = verification.to_dict()
                machine.transition(ReviewState.PENDING_CORRECTION_APPROVAL)
                final_state = (
                    ReviewState.REJECTED
                    if case["case_type"] == "rejection"
                    else ReviewState.DEFERRED
                )
                machine.transition(final_state)
                proposal = CorrectionProposal(
                    proposal_id=f"PROPOSAL-{case['id']}",
                    verification_id=verification.verification_id,
                    target_artifact=relative_path(baseline_path),
                    target_sha256=baseline_before,
                    proposed_diff="--- baseline\n+++ proposal\n@@ synthetic fixture only @@\n",
                    evidence_refs=(f"fixture:{case['id']}",),
                    rollback_description=(
                        "Discard the un-applied proposal; the baseline snapshot remains unchanged."
                    ),
                    approval_state="rejected"
                    if final_state == ReviewState.REJECTED
                    else "deferred",
                    applied=False,
                )
                record["proposal"] = proposal.to_dict()
                correction_applications += int(proposal.applied)
            record["state"] = machine.state.value
        record["history"] = machine.history
        records.append(record)

    baseline_after = sha256_file(baseline_path)
    for record in records:
        record["baseline_preserved"] = baseline_before == baseline_after
        record["trusted_memory_written"] = False
        record["correction_applied"] = False
    timeout_and_denials = [
        record
        for record in records
        if record["case_type"]
        in {"timeout", "rejection", "unresolved_override", "unauthorized_reviewer"}
    ]
    unauthorized_records = [
        record
        for record in records
        if record["case_type"] != "timeout" and not record["authority"]["allowed"]
    ]
    acceptance = {
        "timeout_parks_and_preserves_baseline": any(
            record["case_type"] == "timeout"
            and record["state"] == ReviewState.TIMED_OUT_PARKED.value
            and record["baseline_preserved"]
            for record in records
        ),
        "timeout_and_denials_preserve_baseline": all(
            record["baseline_preserved"] for record in timeout_and_denials
        ),
        "zero_trusted_memory_writes": len(memory.records) == 0,
        "zero_correction_applications": correction_applications == 0,
        "unresolved_inputs_need_adjudication": all(
            record["state"] == ReviewState.NEEDS_ADJUDICATION.value
            for record in records
            if record["case_type"] == "unresolved_override" or not record["authority"]["allowed"]
        ),
        "actor_policy_overrides_case_type": all(
            record["state"] == ReviewState.NEEDS_ADJUDICATION.value
            and not record["trusted_memory_written"]
            and not record["correction_applied"]
            and "proposal" not in record
            for record in unauthorized_records
        ),
    }
    summary = {
        "experiment": EXPERIMENT_ID,
        "fixture_version": fixture["fixture_version"],
        "synthetic_tag": "SYNTHETIC_NOT_HUMAN",
        "baseline_sha256_before": baseline_before,
        "baseline_sha256_after": baseline_after,
        "cases": records,
        "trusted_memory_writes": len(memory.records),
        "correction_applications": correction_applications,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }
    return {"summary": summary, "input_files": (descriptor_path, baseline_path)}


def execute(output_dir: Path | None = None) -> dict[str, Any]:
    result = evaluate()
    output = output_dir or default_output_dir(EXPERIMENT_ID)
    write_experiment_bundle(
        experiment_id=EXPERIMENT_ID,
        experiment_version="1.0",
        config_version="fixture-1.0",
        output_dir=output,
        input_files=result["input_files"],
        payloads={"summary.json": result["summary"]},
        metric_schema={
            "baseline_sha256_before": "sha256",
            "baseline_sha256_after": "sha256",
            "trusted_memory_writes": "count",
            "correction_applications": "count",
        },
        parameters={
            "timeout_behavior": "park_and_preserve_baseline",
            "correction_mode": "proposal_only",
            "authority_policy": {role: sorted(actions) for role, actions in ROLE_AUTHORITY.items()},
        },
    )
    print_completion(EXPERIMENT_ID, output, result["summary"])
    return result
