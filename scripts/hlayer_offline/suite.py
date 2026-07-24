"""Transactional combined conformance suite for EXP-013 through EXP-018."""

from __future__ import annotations

import io
import json
import shutil
import tempfile
from collections.abc import Callable, Mapping, Sequence
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .common import (
    CLAIM_SCOPE,
    REPO_ROOT,
    _decision_snapshot,
    _promote_directory,
    _write_staged,
    canonical_json,
    load_json,
    normalized_manifest_payload,
    normalized_manifest_sha256,
    sha256_bytes,
    sha256_file,
)
from .contracts import stable_identifier
from .exp013 import execute as execute_013
from .exp014 import execute as execute_014
from .exp015 import execute as execute_015
from .exp016 import execute as execute_016
from .exp017 import execute as execute_017
from .exp018 import execute as execute_018

SUITE_ID = "HLAYER-CONFORMANCE"
SUITE_VERSION = "1.0"
DEFAULT_OUTPUT = REPO_ROOT / "reports" / "generated" / "hlayer_conformance"
Runner = Callable[[Path], dict[str, Any]]
DEFAULT_RUNNERS: tuple[tuple[str, Runner], ...] = (
    ("EXP-013", execute_013),
    ("EXP-014", execute_014),
    ("EXP-015", execute_015),
    ("EXP-016", execute_016),
    ("EXP-017", execute_017),
    ("EXP-018", execute_018),
)


class SuiteError(RuntimeError):
    """Raised before promotion when any child bundle fails validation."""


def _source_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def validate_child_bundle(
    child_dir: Path,
    expected_experiment_id: str,
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    manifest_path = child_dir / "manifest.json"
    summary_path = child_dir / "summary.json"
    if not manifest_path.is_file() or not summary_path.is_file():
        raise SuiteError(
            f"{expected_experiment_id} bundle is missing manifest.json or summary.json"
        )
    manifest = load_json(manifest_path)
    summary = load_json(summary_path)
    if summary.get("passed") is not True:
        raise SuiteError(f"{expected_experiment_id} acceptance is not true")
    if manifest.get("experiment_id") != expected_experiment_id:
        raise SuiteError(f"{expected_experiment_id} manifest identity mismatch")
    if manifest.get("decision_snapshot_sha256") != decision["sha256"]:
        raise SuiteError(f"{expected_experiment_id} used a different decision snapshot")
    if manifest.get("decision_snapshot_status") != decision["status"]:
        raise SuiteError(f"{expected_experiment_id} decision snapshot status mismatch")

    calculated_normalized = normalized_manifest_sha256(manifest)
    if manifest.get("normalized_manifest_sha256") != calculated_normalized:
        raise SuiteError(f"{expected_experiment_id} normalized manifest hash mismatch")
    expected_run_id = stable_identifier(
        expected_experiment_id,
        normalized_manifest_payload(manifest),
        length=20,
    )
    if manifest.get("run_id") != expected_run_id:
        raise SuiteError(f"{expected_experiment_id} stable run ID mismatch")

    output_hashes = manifest.get("output_hashes")
    if not isinstance(output_hashes, dict) or not output_hashes:
        raise SuiteError(f"{expected_experiment_id} has no output hashes")
    actual_output_names = {
        path.relative_to(child_dir).as_posix()
        for path in child_dir.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    }
    if actual_output_names != set(output_hashes):
        raise SuiteError(f"{expected_experiment_id} output set does not match its manifest")
    for name, expected_hash in sorted(output_hashes.items()):
        path = child_dir / name
        if not path.is_file() or sha256_file(path) != expected_hash:
            raise SuiteError(f"{expected_experiment_id} output hash mismatch: {name}")

    input_hashes = manifest.get("input_hashes")
    if not isinstance(input_hashes, dict) or not input_hashes:
        raise SuiteError(f"{expected_experiment_id} has no input hashes")
    for name, expected_hash in sorted(input_hashes.items()):
        path = _source_path(name)
        if not path.is_file() or sha256_file(path) != expected_hash:
            raise SuiteError(f"{expected_experiment_id} input hash mismatch: {name}")

    return {
        "experiment_id": expected_experiment_id,
        "run_id": manifest["run_id"],
        "normalized_manifest_sha256": calculated_normalized,
        "manifest_file_sha256": sha256_file(manifest_path),
        "output_hashes": dict(sorted(output_hashes.items())),
        "acceptance": True,
    }


def _normalized_suite_payload(manifest: Mapping[str, Any]) -> dict[str, Any]:
    stable_experiments = [
        {
            "experiment_id": child["experiment_id"],
            "run_id": child["run_id"],
            "normalized_manifest_sha256": child["normalized_manifest_sha256"],
            "output_hashes": child["output_hashes"],
            "acceptance": child["acceptance"],
        }
        for child in manifest["experiments"]
    ]
    return {
        "schema_version": manifest["schema_version"],
        "suite_id": manifest["suite_id"],
        "suite_version": manifest["suite_version"],
        "claim_scope": manifest["claim_scope"],
        "decision_snapshot_sha256": manifest["decision_snapshot_sha256"],
        "decision_snapshot_status": manifest["decision_snapshot_status"],
        "decision_snapshot_program_mode": manifest["decision_snapshot_program_mode"],
        "decision_snapshot_offline_only": manifest["decision_snapshot_offline_only"],
        "live_shadow_authorized": manifest["live_shadow_authorized"],
        "suite_source_sha256": manifest["suite_source_sha256"],
        "experiments": stable_experiments,
        "passed": manifest["passed"],
    }


def normalized_suite_sha256(manifest: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_json(_normalized_suite_payload(manifest)).encode("utf-8"))


def validate_suite_stage(
    stage: Path,
    expected_ids: Sequence[str],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    manifest_path = stage / "manifest.json"
    if not manifest_path.is_file():
        raise SuiteError("combined suite manifest is missing")
    manifest = load_json(manifest_path)
    if manifest.get("passed") is not True:
        raise SuiteError("combined suite acceptance is not true")
    if manifest.get("decision_snapshot_sha256") != decision["sha256"]:
        raise SuiteError("combined suite decision snapshot mismatch")
    if manifest.get("decision_snapshot_program_mode") != decision["program_mode"]:
        raise SuiteError("combined suite decision program mode mismatch")
    if manifest.get("decision_snapshot_offline_only") is not decision["offline_only"]:
        raise SuiteError("combined suite decision offline-only status mismatch")
    if manifest.get("live_shadow_authorized") is not decision["live_shadow_authorized"]:
        raise SuiteError("combined suite live-authorization status mismatch")
    actual_ids = [child.get("experiment_id") for child in manifest.get("experiments", [])]
    if actual_ids != list(expected_ids):
        raise SuiteError("combined suite experiment order or membership mismatch")
    validated = [
        validate_child_bundle(
            stage / experiment_id.lower().replace("-", ""), experiment_id, decision
        )
        for experiment_id in expected_ids
    ]
    for recorded, actual in zip(manifest["experiments"], validated, strict=True):
        if recorded != actual:
            raise SuiteError(f"combined suite child record mismatch: {actual['experiment_id']}")
    calculated = normalized_suite_sha256(manifest)
    if manifest.get("normalized_suite_sha256") != calculated:
        raise SuiteError("combined suite normalized hash mismatch")
    expected_run_id = stable_identifier(SUITE_ID, _normalized_suite_payload(manifest), length=20)
    if manifest.get("run_id") != expected_run_id:
        raise SuiteError("combined suite stable run ID mismatch")
    return manifest


def execute_suite(
    output_dir: Path | None = None,
    *,
    runners: Sequence[tuple[str, Runner]] = DEFAULT_RUNNERS,
) -> dict[str, Any]:
    """Rerun, validate, and atomically promote the complete conformance suite."""

    output = (output_dir or DEFAULT_OUTPUT).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output.name}.stage-", dir=output.parent))
    started = datetime.now(timezone.utc)
    expected_ids = [experiment_id for experiment_id, _ in runners]
    try:
        for experiment_id, runner in runners:
            child_dir = stage / experiment_id.lower().replace("-", "")
            # Child CLIs normally emit human-readable completion lines. Keep the
            # combined-suite CLI machine-readable by containing those messages.
            with redirect_stdout(io.StringIO()):
                result = runner(child_dir)
            if not isinstance(result, dict) or result.get("summary", {}).get("passed") is not True:
                raise SuiteError(
                    f"{experiment_id} failed acceptance; suite stopped before promotion"
                )

        decision = _decision_snapshot()
        child_records = [
            validate_child_bundle(
                stage / experiment_id.lower().replace("-", ""), experiment_id, decision
            )
            for experiment_id in expected_ids
        ]
        completed = datetime.now(timezone.utc)
        manifest: dict[str, Any] = {
            "schema_version": "1.0",
            "suite_id": SUITE_ID,
            "suite_version": SUITE_VERSION,
            "claim_scope": CLAIM_SCOPE,
            "decision_snapshot_sha256": decision["sha256"],
            "decision_snapshot_status": decision["status"],
            "decision_snapshot_source": decision["source"],
            "decision_snapshot_program_mode": decision["program_mode"],
            "decision_snapshot_offline_only": decision["offline_only"],
            "live_shadow_authorized": decision["live_shadow_authorized"],
            "suite_source_sha256": sha256_file(Path(__file__).resolve()),
            "started_at": started.isoformat(),
            "completed_at": completed.isoformat(),
            "experiments": child_records,
            "passed": True,
        }
        manifest["normalized_suite_sha256"] = normalized_suite_sha256(manifest)
        manifest["run_id"] = stable_identifier(
            SUITE_ID,
            _normalized_suite_payload(manifest),
            length=20,
        )
        _write_staged(
            stage / "manifest.json",
            (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
                "utf-8"
            ),
        )
        validated_manifest = validate_suite_stage(stage, expected_ids, decision)
        _promote_directory(stage, output)
        return validated_manifest
    finally:
        if stage.exists():
            shutil.rmtree(stage)
