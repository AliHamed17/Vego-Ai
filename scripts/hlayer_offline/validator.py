"""Read-only validation suite for the isolated H-layer contracts and experiments."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any, Callable

from .common import REPO_ROOT
from .contracts import (
    CONTRACT_SCHEMA_VERSION,
    MemoryRecord,
    ObservationRecord,
    ValidationError,
    contract_catalog,
)
from .exp013 import evaluate as evaluate_013
from .exp014 import evaluate as evaluate_014
from .exp015 import evaluate as evaluate_015
from .exp016 import evaluate as evaluate_016
from .exp017 import evaluate as evaluate_017
from .exp018 import evaluate as evaluate_018
from .state_machine import ReviewState, ReviewStateMachine, route_observation


def _tree_digest(paths: tuple[Path, ...]) -> str:
    digest = sha256()
    for root in paths:
        if not root.exists():
            continue
        for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
            digest.update(path.relative_to(REPO_ROOT).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


def validate() -> dict[str, Any]:
    checks: dict[str, bool] = {}
    details: dict[str, Any] = {}
    protected = (
        REPO_ROOT / "VEGO-AI" / "framework",
        REPO_ROOT / "VEGO-AI" / "eval",
        REPO_ROOT / "VEGO-AI" / "schemas",
    )
    before = _tree_digest(protected)

    catalog = contract_catalog()
    checks["contract_catalog_version"] = catalog["schema_version"] == CONTRACT_SCHEMA_VERSION
    checks["all_eight_contracts_cataloged"] = len(catalog["contracts"]) == 8

    missing_lineage_blocked = False
    try:
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
    except ValidationError:
        missing_lineage_blocked = True
    checks["captured_event_requires_lineage"] = missing_lineage_blocked

    e15 = ObservationRecord(
        observation_id="OBS-e15-validator",
        event_type="E15",
        run_id="validator",
        setting_id="fixture",
        producer="validator",
        channel="evaluation",
        sequence=1,
        capture_status="reconstructed",
        source_artifact="validator-fixture",
        source_sha256="0" * 64,
        payload={},
    )
    e15_triage = route_observation(e15, severity=3, trigger_codes=("evaluation_signal",))
    checks["e15_always_parked"] = (
        e15_triage.outcome == "park" and e15_triage.budget_state == "evaluation_only"
    )

    machine = ReviewStateMachine()
    machine.transition(ReviewState.PROMOTED)
    machine.transition(ReviewState.PENDING_REVIEW)
    timeout = machine.timeout()
    checks["timeout_parks_without_side_effects"] = (
        timeout["state"] == "timed_out_parked"
        and timeout["baseline_preserved"]
        and not timeout["trusted_memory_written"]
        and not timeout["correction_applied"]
    )
    illegal_transition_blocked = False
    try:
        ReviewStateMachine().transition(ReviewState.APPROVED)
    except ValidationError:
        illegal_transition_blocked = True
    checks["illegal_state_transition_blocked"] = illegal_transition_blocked

    unresolved_memory_blocked = False
    try:
        MemoryRecord(
            memory_id="MEM-invalid",
            verification_id="VERIFY-invalid",
            source_outcome="needs_adjudication",
            validity_scope={"fixture": "invalid"},
            conflicts=("unresolved",),
            provenance={"source": "fixture"},
            leakage_classification="unknown",
        )
    except ValidationError:
        unresolved_memory_blocked = True
    checks["unresolved_input_blocked_from_memory"] = unresolved_memory_blocked

    evaluators: tuple[tuple[str, Callable[[], dict[str, Any]]], ...] = (
        ("EXP-013", evaluate_013),
        ("EXP-014", evaluate_014),
        ("EXP-015", evaluate_015),
        ("EXP-016", evaluate_016),
        ("EXP-017", evaluate_017),
        ("EXP-018", evaluate_018),
    )
    experiment_results = {name: evaluator()["summary"] for name, evaluator in evaluators}
    for name, summary in experiment_results.items():
        checks[f"{name.lower()}_acceptance"] = bool(summary["passed"])
    checks["replay_is_three_run_deterministic"] = experiment_results["EXP-014"]["acceptance"][
        "three_runs_identical"
    ]
    checks["bundle_keys_are_isolated"] = experiment_results["EXP-015"]["acceptance"][
        "no_cross_subject_bundle_collisions"
    ]
    checks["authority_cases_have_no_writes"] = (
        experiment_results["EXP-016"]["trusted_memory_writes"] == 0
        and experiment_results["EXP-016"]["correction_applications"] == 0
    )
    checks["synthetic_verification_does_not_contaminate_memory"] = (
        experiment_results["EXP-017"]["trusted_memory_writes"] == 0
    )
    checks["correction_dry_run_hashes_match"] = (
        experiment_results["EXP-018"]["source_sha256_before"]
        == experiment_results["EXP-018"]["source_sha256_after"]
    )

    after = _tree_digest(protected)
    checks["protected_runtime_tree_unchanged"] = before == after
    details["protected_tree_sha256_before"] = before
    details["protected_tree_sha256_after"] = after
    details["experiment_acceptance"] = {
        name: summary["acceptance"] for name, summary in experiment_results.items()
    }
    return {
        "validator": "hlayer-offline-contracts-1.0",
        "checks": checks,
        "details": details,
        "passed": all(checks.values()),
    }
