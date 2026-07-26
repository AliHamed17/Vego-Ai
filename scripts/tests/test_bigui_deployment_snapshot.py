from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_builder():
    path = ROOT / "scripts" / "build_bigui_deployment_snapshot.py"
    spec = importlib.util.spec_from_file_location(
        "build_bigui_deployment_snapshot_test", path
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_equal_count_without_matching_hash_is_stale() -> None:
    builder = load_builder()
    candidate_hash = "a" * 64

    assert (
        builder.determine_live_status(
            {
                "reachable": True,
                "experimentCount": 41,
                "catalogSha256": None,
            },
            41,
            candidate_hash,
        )
        == "stale"
    )
    assert (
        builder.determine_live_status(
            {
                "reachable": True,
                "experimentCount": 41,
                "catalogSha256": "b" * 64,
            },
            41,
            candidate_hash,
        )
        == "stale"
    )


def test_matching_count_and_hash_is_current() -> None:
    builder = load_builder()
    candidate_hash = "a" * 64

    assert (
        builder.determine_live_status(
            {
                "reachable": True,
                "experimentCount": 41,
                "catalogSha256": candidate_hash,
            },
            41,
            candidate_hash,
        )
        == "current"
    )


def test_unreachable_live_site_stays_unreachable() -> None:
    builder = load_builder()

    assert (
        builder.determine_live_status(
            {
                "reachable": False,
                "experimentCount": 41,
                "catalogSha256": "a" * 64,
            },
            41,
            "a" * 64,
        )
        == "unreachable"
    )
