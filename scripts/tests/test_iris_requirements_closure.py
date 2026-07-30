from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/validate_iris_requirements_closure.py"
SPEC = importlib.util.spec_from_file_location(
    "validate_iris_requirements_closure", SCRIPT
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_control_set_is_exact_and_contiguous() -> None:
    expected = (
        tuple(f"R-{index:02d}" for index in range(1, 20))
        + tuple(f"A-{index:02d}" for index in range(1, 16))
        + tuple(f"Q-{index:02d}" for index in range(1, 11))
    )
    assert MODULE.EXPECTED_IDS == expected
    assert len(MODULE.EXPECTED_IDS) == 44


def test_all_structural_checks_pass_without_promoting_human_gates() -> None:
    results = [MODULE.RUNNERS[experiment]() for experiment in MODULE.EXPERIMENTS]

    assert all(result.passed for result in results)
    assert [result.state for result in results] == [
        "PASS",
        "READY_PENDING_HUMAN_RUN",
        "PASS",
        "READY_PENDING_NEXT_MEETING",
    ]


def test_audited_readiness_distribution_is_preserved() -> None:
    assert MODULE.EXPECTED_STATUS_COUNTS == {
        "Verified complete": 2,
        "Implemented awaiting human acceptance": 6,
        "Partial": 22,
        "Open": 5,
        "Blocked": 9,
    }
