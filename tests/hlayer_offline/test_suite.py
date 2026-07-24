from __future__ import annotations

import json

import pytest
from hlayer_offline.common import (
    DECISION_IDS,
    EXPECTED_AUTHORIZED_TOUCHES,
    _decision_snapshot,
    canonical_json,
    sha256_bytes,
)
from hlayer_offline.suite import SuiteError, execute_suite, validate_suite_stage


def _rehash_snapshot(payload: dict) -> None:
    payload.pop("snapshot_sha256", None)
    payload["snapshot_sha256"] = sha256_bytes((canonical_json(payload) + "\n").encode("utf-8"))


def _live_snapshot() -> dict:
    decisions = []
    for decision_id in DECISION_IDS:
        gated = decision_id in {"M-02", "M-03", "M-04", "M-05"}
        decisions.append(
            {
                "id": decision_id,
                "decision_complete": gated,
                "accepted": gated,
                "effective_outcome": "Accepted" if gated else "Deferred",
            }
        )
    payload = {
        "schema_version": "1.0",
        "decision_ids": list(DECISION_IDS),
        "decisions": decisions,
        "program_mode": "live_shadow_authorized",
        "offline_only": False,
        "live_shadow_authorized": True,
        "authorization_blockers": [],
        "implementation_gate": {"offline_only": False},
        "authorization_record": {
            "allowed_touch_outcome": "Accepted",
            "implementation_outcome": "Accepted",
            "allowed_touches": sorted(EXPECTED_AUTHORIZED_TOUCHES),
            "approver": "supervisor-fixture",
            "approved_at": "2026-07-15T12:00:00+00:00",
        },
    }
    _rehash_snapshot(payload)
    return payload


def test_combined_suite_is_atomic_hash_valid_and_stable(tmp_path) -> None:
    output = tmp_path / "hlayer_conformance"
    first = execute_suite(output)
    (output / "stale.txt").write_text("stale", encoding="utf-8")
    second = execute_suite(output)

    assert first["run_id"] == second["run_id"]
    assert first["normalized_suite_sha256"] == second["normalized_suite_sha256"]
    assert [child["experiment_id"] for child in second["experiments"]] == [
        "EXP-013",
        "EXP-014",
        "EXP-015",
        "EXP-016",
        "EXP-017",
        "EXP-018",
    ]
    assert not (output / "stale.txt").exists()
    decision = _decision_snapshot()
    assert second["decision_snapshot_sha256"] == decision["sha256"]
    assert second["decision_snapshot_status"] == decision["status"]
    assert second["decision_snapshot_program_mode"] == decision["program_mode"]
    assert second["decision_snapshot_offline_only"] is decision["offline_only"]
    assert second["live_shadow_authorized"] is decision["live_shadow_authorized"]
    assert validate_suite_stage(
        output,
        ["EXP-013", "EXP-014", "EXP-015", "EXP-016", "EXP-017", "EXP-018"],
        decision,
    )["passed"]

    with (output / "exp018" / "proposal.diff").open("a", encoding="utf-8") as handle:
        handle.write("tampered\n")
    with pytest.raises(SuiteError, match="output hash mismatch"):
        validate_suite_stage(
            output,
            ["EXP-013", "EXP-014", "EXP-015", "EXP-016", "EXP-017", "EXP-018"],
            decision,
        )


def test_combined_suite_fails_fast_and_preserves_previous_bundle(tmp_path) -> None:
    output = tmp_path / "existing"
    output.mkdir()
    sentinel = output / "sentinel.json"
    sentinel.write_text(json.dumps({"keep": True}), encoding="utf-8")
    calls: list[str] = []

    def failing_runner(_output):
        calls.append("first")
        return {"summary": {"passed": False}}

    def should_not_run(_output):
        calls.append("second")
        return {"summary": {"passed": True}}

    with pytest.raises(SuiteError, match="failed acceptance"):
        execute_suite(
            output,
            runners=(("EXP-013", failing_runner), ("EXP-014", should_not_run)),
        )
    assert calls == ["first"]
    assert json.loads(sentinel.read_text(encoding="utf-8")) == {"keep": True}


def test_rehashed_broadened_authorization_can_never_report_live(tmp_path, monkeypatch) -> None:
    snapshot_path = tmp_path / "decision_snapshot.json"
    payload = _live_snapshot()
    snapshot_path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setenv("HLAYER_DECISION_SNAPSHOT", str(snapshot_path))
    assert _decision_snapshot()["live_shadow_authorized"] is True

    payload["authorization_record"]["allowed_touches"].append("VEGO-AI/framework/extra.py")
    _rehash_snapshot(payload)
    snapshot_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="authorization flags are inconsistent"):
        _decision_snapshot()

    payload.update(
        {
            "program_mode": "offline_only",
            "offline_only": True,
            "live_shadow_authorized": False,
            "implementation_gate": {"offline_only": True},
        }
    )
    _rehash_snapshot(payload)
    snapshot_path.write_text(json.dumps(payload), encoding="utf-8")
    decision = _decision_snapshot()
    assert decision["offline_only"] is True
    assert decision["live_shadow_authorized"] is False

    manifest = execute_suite(tmp_path / "broadened-suite")
    assert manifest["decision_snapshot_offline_only"] is True
    assert manifest["live_shadow_authorized"] is False


def test_rehashed_snapshot_still_requires_exact_ordered_m01_through_m06(tmp_path) -> None:
    payload = _live_snapshot()
    payload["decisions"] = list(reversed(payload["decisions"]))
    _rehash_snapshot(payload)
    path = tmp_path / "reordered.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="ordered M-01 through M-06"):
        _decision_snapshot(path)
