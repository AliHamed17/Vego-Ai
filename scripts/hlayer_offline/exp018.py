"""EXP-018: correction-proposal dry run against disposable copied data."""

from __future__ import annotations

import difflib
import shutil
import tempfile
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
from .contracts import CorrectionProposal, VerificationRecord, stable_identifier

EXPERIMENT_ID = "EXP-018"
EXPERIMENT_FOLDER = "EXP-018-correction-proposal-dry-run"


def _proposal_diff(target: Path, old_text: str, new_text: str) -> str:
    with tempfile.TemporaryDirectory(prefix="vego-exp018-") as temporary:
        copied = Path(temporary) / target.name
        shutil.copy2(target, copied)
        original = copied.read_text(encoding="utf-8")
        if original.count(old_text) != 1:
            raise ValueError("fixture replacement must match exactly once")
        proposed = original.replace(old_text, new_text, 1)
        copied.write_text(proposed, encoding="utf-8", newline="")
        lines = difflib.unified_diff(
            original.splitlines(),
            proposed.splitlines(),
            fromfile=f"a/{target.name}",
            tofile=f"b/{target.name}.proposed-copy",
            lineterm="",
        )
        return "\n".join(lines) + "\n"


def evaluate(fixtures: Path | None = None) -> dict[str, Any]:
    fixtures = fixtures or fixture_dir(EXPERIMENT_FOLDER)
    descriptor_path = fixtures / "proposal.json"
    descriptor = load_json(descriptor_path)
    target = fixtures / descriptor["target"]
    source_hash_before = sha256_file(target)
    first_diff = _proposal_diff(target, descriptor["replace"]["old"], descriptor["replace"]["new"])
    second_diff = _proposal_diff(target, descriptor["replace"]["old"], descriptor["replace"]["new"])
    source_hash_after = sha256_file(target)

    verification = VerificationRecord(
        verification_id="VERIFY-EXP018-FIXTURE",
        feedback_id="FEEDBACK-EXP018-FIXTURE",
        deterministic_checks=(
            "target_hash_captured",
            "replacement_matches_once",
            "diff_replayed_twice",
        ),
        source_versions={"target": source_hash_before},
        conflicts=(),
        rounds=1,
        outcome="verified",
    )
    proposal = CorrectionProposal(
        proposal_id=stable_identifier(
            "PROPOSAL", {"target": source_hash_before, "diff": first_diff}
        ),
        verification_id=verification.verification_id,
        target_artifact=relative_path(target),
        target_sha256=source_hash_before,
        proposed_diff=first_diff,
        evidence_refs=tuple(descriptor["evidence_refs"]),
        rollback_description=descriptor["rollback_description"],
        approval_state="pending",
        applied=False,
    )
    acceptance = {
        "reproducible_diff": first_diff == second_diff,
        "target_hash_recorded": proposal.target_sha256 == source_hash_before,
        "rollback_description_present": bool(proposal.rollback_description.strip()),
        "zero_repository_source_modification": source_hash_before == source_hash_after,
        "proposal_not_applied": not proposal.applied,
    }
    summary = {
        "experiment": EXPERIMENT_ID,
        "fixture_version": descriptor["fixture_version"],
        "synthetic_tag": "SYNTHETIC_NOT_HUMAN",
        "working_copy_only": True,
        "source_sha256_before": source_hash_before,
        "source_sha256_after": source_hash_after,
        "verification": verification.to_dict(),
        "proposal": proposal.to_dict(),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }
    return {
        "summary": summary,
        "diff": first_diff,
        "input_files": (descriptor_path, target),
    }


def execute(output_dir: Path | None = None) -> dict[str, Any]:
    result = evaluate()
    output = output_dir or default_output_dir(EXPERIMENT_ID)
    write_experiment_bundle(
        experiment_id=EXPERIMENT_ID,
        experiment_version="1.0",
        config_version="fixture-1.0",
        output_dir=output,
        input_files=result["input_files"],
        payloads={"summary.json": result["summary"], "proposal.diff": result["diff"]},
        metric_schema={
            "source_sha256_before": "sha256",
            "source_sha256_after": "sha256",
            "reproducible_diff": "boolean",
            "proposal_applied": "constant false",
        },
        parameters={"target_mode": "temporary-copy", "approval_state": "pending"},
    )
    print_completion(EXPERIMENT_ID, output, result["summary"])
    return result
