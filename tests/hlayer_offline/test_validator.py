from __future__ import annotations

import json

import pytest
from hlayer_offline.common import _decision_snapshot, write_experiment_bundle
from hlayer_offline.validator import validate


def test_isolated_validator_passes_and_preserves_protected_tree() -> None:
    result = validate()
    assert result["passed"] is True
    assert result["checks"]["all_eight_contracts_cataloged"]
    assert result["checks"]["e15_always_parked"]
    assert result["checks"]["protected_runtime_tree_unchanged"]


def test_bundle_promotion_is_transactional_and_normalized_manifest_is_stable(tmp_path) -> None:
    source = tmp_path / "input.json"
    source.write_text('{"fixture":true}\n', encoding="utf-8")
    output = tmp_path / "exp-test"

    def write_bundle():
        return write_experiment_bundle(
            experiment_id="EXP-TEST",
            experiment_version="1.0",
            config_version="fixture-1.0",
            output_dir=output,
            input_files=(source,),
            payloads={"summary.json": {"passed": True, "value": 1}},
            metric_schema={"value": "count"},
            parameters={"mode": "fixture"},
        )

    first = write_bundle()
    (output / "stale-from-old-run.txt").write_text("stale", encoding="utf-8")
    second = write_bundle()
    assert first.run_id == second.run_id
    assert first.normalized_manifest_sha256 == second.normalized_manifest_sha256
    assert not (output / "stale-from-old-run.txt").exists()
    persisted = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert persisted["decision_snapshot_status"] in {"recorded_snapshot", "offline_fallback"}


def test_failed_acceptance_cannot_replace_existing_bundle(tmp_path) -> None:
    source = tmp_path / "input.json"
    source.write_text("{}\n", encoding="utf-8")
    output = tmp_path / "existing"
    output.mkdir()
    (output / "sentinel.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="acceptance did not pass"):
        write_experiment_bundle(
            experiment_id="EXP-FAIL",
            experiment_version="1.0",
            config_version="fixture-1.0",
            output_dir=output,
            input_files=(source,),
            payloads={"summary.json": {"passed": False}},
            metric_schema={"passed": "boolean"},
            parameters={},
        )
    assert (output / "sentinel.txt").read_text(encoding="utf-8") == "keep"


def test_missing_decision_snapshot_uses_explicit_stable_offline_fallback(tmp_path) -> None:
    first = _decision_snapshot(tmp_path / "absent.json")
    second = _decision_snapshot(tmp_path / "absent.json")
    assert first == second
    assert first["status"] == "offline_fallback"
    assert first["source"] == "embedded:all-unresolved-decisions-deferred"
    assert first["program_mode"] == "offline_only"
    assert first["offline_only"] is True
    assert first["live_shadow_authorized"] is False
