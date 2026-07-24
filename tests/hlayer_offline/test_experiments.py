from __future__ import annotations

import pytest
from hlayer_offline.exp013 import evaluate as evaluate_013
from hlayer_offline.exp014 import evaluate as evaluate_014
from hlayer_offline.exp015 import evaluate as evaluate_015
from hlayer_offline.exp016 import evaluate as evaluate_016
from hlayer_offline.exp017 import evaluate as evaluate_017
from hlayer_offline.exp018 import evaluate as evaluate_018


@pytest.mark.parametrize(
    "evaluate",
    [evaluate_013, evaluate_014, evaluate_015, evaluate_016, evaluate_017, evaluate_018],
)
def test_experiment_acceptance(evaluate) -> None:
    result = evaluate()
    assert result["summary"]["passed"] is True


def test_exp013_keeps_gaps_explicit_and_e15_out() -> None:
    summary = evaluate_013()["summary"]
    assert {"E3", "E9"}.issubset(summary["explicit_gap_event_types"])
    assert summary["e15_triage"]["outcome"] == "park"
    assert summary["e15_triage"]["budget_state"] == "evaluation_only"


def test_exp014_three_replays_have_one_normalized_hash() -> None:
    summary = evaluate_014()["summary"]
    assert summary["replay_count"] == 3
    assert len(set(summary["normalized_hashes"])) == 1
    assert summary["acceptance"]["no_duplicate_review_items"]


def test_exp015_bundle_isolation_and_deferred_recovery() -> None:
    summary = evaluate_015()["summary"]
    for config in summary["configurations"]:
        assert config["bundle_collision_count"] == 0
        assert config["round_1"]["high_severity_coverage"] == 1.0
        assert config["fairness"]["recovered_next_checkpoint_ids"]


def test_exp016_timeout_rejection_and_unresolved_cases_do_not_write() -> None:
    summary = evaluate_016()["summary"]
    assert summary["baseline_sha256_before"] == summary["baseline_sha256_after"]
    assert summary["trusted_memory_writes"] == 0
    assert summary["correction_applications"] == 0
    timeout = next(case for case in summary["cases"] if case["case_type"] == "timeout")
    assert timeout["state"] == "timed_out_parked"
    unauthorized_rejection = next(case for case in summary["cases"] if case["case_id"] == "AUTH-06")
    assert unauthorized_rejection["case_type"] == "rejection"
    assert unauthorized_rejection["authority"]["allowed"] is False
    assert unauthorized_rejection["state"] == "needs_adjudication"
    assert "proposal" not in unauthorized_rejection
    assert unauthorized_rejection["feedback_crosswalk"]["review_id"].startswith("HRQ-")


def test_exp017_deterministic_source_order_and_synthetic_memory_block() -> None:
    summary = evaluate_017()["summary"]
    assert summary["source_order"] == ["baseline", "guideline", "review", "memory"]
    assert summary["trusted_memory_writes"] == 0
    assert all(not case["semantic_checks_performed"] for case in summary["cases"])


def test_exp018_proposal_is_reproducible_and_source_hash_is_unchanged() -> None:
    result = evaluate_018()
    summary = result["summary"]
    assert summary["source_sha256_before"] == summary["source_sha256_after"]
    assert summary["proposal"]["applied"] is False
    assert summary["proposal"]["approval_state"] == "pending"
    assert result["diff"].startswith("--- a/target.txt\n+++ b/target.txt.proposed-copy\n")
