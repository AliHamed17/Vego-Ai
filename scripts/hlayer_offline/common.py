"""Shared deterministic I/O and provenance helpers for EXP-013 through EXP-018."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import tempfile
import time
import uuid
from collections.abc import Mapping
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from .contracts import ExperimentRunManifest, canonical_json, stable_identifier

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAIM_SCOPE = "Offline architecture-mechanism evidence only; fixtures are not empirical validation."
DECISION_IDS = tuple(f"M-{number:02d}" for number in range(1, 7))
GATED_DECISION_IDS = ("M-02", "M-03", "M-04", "M-05")
ACCEPTED_OUTCOMES = frozenset({"Accepted", "Accepted with changes"})
EXPECTED_AUTHORIZED_TOUCHES = frozenset(
    {
        "VEGO-AI/framework/orchestrator.py",
        "VEGO-AI/framework/qa_registry.py",
        "VEGO-AI/framework/h_layer_shadow_writer.py",
        "VEGO-AI/schemas/observation_record.schema.json",
        "VEGO-AI/tests/test_h_layer_shadow_writer.py",
    }
)
DECISION_SNAPSHOT_PATH = (
    REPO_ROOT / "reports" / "generated" / "h_layer_decisions" / "decision_snapshot.json"
)
NORMALIZED_MANIFEST_FIELDS = (
    "experiment_id",
    "experiment_version",
    "config_version",
    "decision_snapshot_sha256",
    "decision_snapshot_status",
    "git_revision",
    "git_dirty",
    "input_hashes",
    "output_hashes",
    "metric_schema",
    "claim_scope",
    "parameters",
    "runtime_versions",
    "schema_version",
)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def fixture_dir(experiment_folder: str) -> Path:
    return REPO_ROOT / "experiments" / experiment_folder / "fixtures"


def default_output_dir(experiment_id: str) -> Path:
    return REPO_ROOT / "reports" / "generated" / experiment_id.lower().replace("-", "")


def normalized_manifest_payload(manifest: Mapping[str, Any]) -> dict[str, Any]:
    missing = [field for field in NORMALIZED_MANIFEST_FIELDS if field not in manifest]
    if missing:
        raise ValueError(f"experiment manifest is missing normalized fields: {', '.join(missing)}")
    return {field: manifest[field] for field in NORMALIZED_MANIFEST_FIELDS}


def normalized_manifest_sha256(manifest: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_json(normalized_manifest_payload(manifest)).encode("utf-8"))


def _git_state() -> tuple[str, bool]:
    try:
        revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=REPO_ROOT,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        )
        return revision, dirty
    except (OSError, subprocess.CalledProcessError):
        return "git-unavailable", True


def _decision_snapshot(path: Path | None = None) -> dict[str, Any]:
    """Load a validated generated snapshot or return an explicit offline fallback."""

    if path is None:
        configured = os.environ.get("HLAYER_DECISION_SNAPSHOT")
        path = Path(configured).resolve() if configured else DECISION_SNAPSHOT_PATH
    if not path.is_file():
        fallback = {
            "schema_version": "1.0",
            "status": "offline_fallback",
            "program_mode": "offline_only",
            "offline_only": True,
            "live_shadow_authorized": False,
            "reason": "Generated supervisor decision snapshot is absent; no default is inferred.",
            "decision_ids": list(DECISION_IDS),
            "decisions": [
                {
                    "id": decision_id,
                    "effective_outcome": "Deferred",
                    "accepted": False,
                    "decision_complete": False,
                }
                for decision_id in DECISION_IDS
            ],
            "authorization_blockers": ["generated decision snapshot is absent"],
            "authorization_record": None,
            "implementation_gate": {"offline_only": True},
        }
        return {
            "status": "offline_fallback",
            "source": "embedded:all-unresolved-decisions-deferred",
            "sha256": sha256_bytes((canonical_json(fallback) + "\n").encode("utf-8")),
            "path": None,
            "program_mode": "offline_only",
            "offline_only": True,
            "live_shadow_authorized": False,
        }
    try:
        data = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid decision snapshot {path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != "1.0":
        raise ValueError("decision snapshot must be a schema_version 1.0 JSON object")
    if data.get("decision_ids") != list(DECISION_IDS):
        raise ValueError(f"decision snapshot must list exactly {list(DECISION_IDS)}")
    decisions = data.get("decisions")
    if not isinstance(decisions, list) or len(decisions) != len(DECISION_IDS):
        raise ValueError("decision snapshot must contain exactly six decision records")
    record_ids = [item.get("id") for item in decisions if isinstance(item, dict)]
    if len(record_ids) != len(decisions) or record_ids != list(DECISION_IDS):
        raise ValueError("decision records must be unique and ordered M-01 through M-06")
    supplied_digest = data.get("snapshot_sha256")
    if not isinstance(supplied_digest, str):
        raise ValueError("decision snapshot is missing snapshot_sha256")
    unsigned = dict(data)
    unsigned.pop("snapshot_sha256", None)
    calculated = sha256_bytes((canonical_json(unsigned) + "\n").encode("utf-8"))
    if supplied_digest != calculated:
        raise ValueError("decision snapshot snapshot_sha256 does not match its canonical payload")

    by_id = {item["id"]: item for item in decisions}
    decisions_complete = all(
        by_id[decision_id].get("decision_complete") is True for decision_id in GATED_DECISION_IDS
    )
    m05 = by_id["M-05"]
    m05_accepted = m05.get("accepted") is True and m05.get("effective_outcome") in ACCEPTED_OUTCOMES
    authorization = data.get("authorization_record")
    authorization_valid = (
        isinstance(authorization, dict)
        and authorization.get("allowed_touch_outcome") in ACCEPTED_OUTCOMES
        and authorization.get("implementation_outcome") in ACCEPTED_OUTCOMES
        and isinstance(authorization.get("allowed_touches"), list)
        and len(authorization["allowed_touches"]) == len(EXPECTED_AUTHORIZED_TOUCHES)
        and all(isinstance(item, str) for item in authorization["allowed_touches"])
        and set(authorization["allowed_touches"]) == EXPECTED_AUTHORIZED_TOUCHES
        and bool(str(authorization.get("approver") or "").strip())
        and bool(str(authorization.get("approved_at") or "").strip())
    )
    blockers = data.get("authorization_blockers")
    no_blockers = isinstance(blockers, list) and not blockers
    derived_live = decisions_complete and m05_accepted and authorization_valid and no_blockers
    derived_offline = not derived_live
    reported_offline = data.get("offline_only")
    reported_live = data.get("live_shadow_authorized")
    implementation_gate = data.get("implementation_gate")
    if not isinstance(reported_offline, bool) or not isinstance(reported_live, bool):
        raise ValueError("decision snapshot authorization flags must be booleans")
    if not isinstance(implementation_gate, dict) or not isinstance(
        implementation_gate.get("offline_only"), bool
    ):
        raise ValueError("decision snapshot implementation gate is missing offline_only")
    expected_mode = "live_shadow_authorized" if derived_live else "offline_only"
    if (
        reported_offline != derived_offline
        or reported_live != derived_live
        or implementation_gate["offline_only"] != derived_offline
        or data.get("program_mode") != expected_mode
    ):
        raise ValueError(
            "decision snapshot authorization flags are inconsistent with decision and "
            "authorization records"
        )
    return {
        "status": "recorded_snapshot",
        "source": relative_path(path),
        "sha256": supplied_digest,
        "path": path,
        "program_mode": expected_mode,
        "offline_only": derived_offline,
        "live_shadow_authorized": derived_live,
    }


def _write_staged(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _replace_with_retry(source: Path, target: Path, attempts: int = 6) -> None:
    """Retry transient Windows directory-sharing failures without changing semantics."""

    for attempt in range(attempts):
        try:
            os.replace(source, target)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.02 * (2**attempt))


def _promote_directory(stage: Path, target: Path) -> None:
    """Promote one complete staged bundle, restoring the old bundle on failure."""

    target = target.resolve()
    stage = stage.resolve()
    if stage.parent != target.parent:
        raise ValueError("stage and target must be siblings for transactional promotion")
    if target.exists() and not target.is_dir():
        raise ValueError(f"output target is not a directory: {target}")
    backup = target.parent / f".{target.name}.backup-{uuid.uuid4().hex}"
    moved_old = False
    promoted = False
    try:
        if target.exists():
            _replace_with_retry(target, backup)
            moved_old = True
        _replace_with_retry(stage, target)
        promoted = True
    except Exception:
        if moved_old and backup.exists() and not target.exists():
            _replace_with_retry(backup, target)
        raise
    finally:
        if promoted and backup.exists():
            if backup.parent != target.parent or not backup.name.startswith(
                f".{target.name}.backup-"
            ):
                raise RuntimeError("refusing to clean an unexpected transaction backup")
            shutil.rmtree(backup)


def write_experiment_bundle(
    *,
    experiment_id: str,
    experiment_version: str,
    config_version: str,
    output_dir: Path,
    input_files: tuple[Path, ...],
    payloads: Mapping[str, Any],
    metric_schema: Mapping[str, Any],
    parameters: Mapping[str, Any],
) -> ExperimentRunManifest:
    """Stage, validate, and transactionally promote a complete experiment bundle."""

    started = datetime.now(timezone.utc)
    output_dir = output_dir.resolve()
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.stage-", dir=output_dir.parent))
    output_hashes: dict[str, str] = {}
    try:
        for name, value in sorted(payloads.items()):
            if Path(name).is_absolute() or ".." in Path(name).parts:
                raise ValueError(f"output name must remain inside the bundle: {name}")
            if isinstance(value, bytes):
                encoded = value
            elif isinstance(value, str) and name.endswith((".md", ".txt", ".diff")):
                encoded = value.encode("utf-8")
            else:
                encoded = (
                    json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
                ).encode("utf-8")
            _write_staged(stage / name, encoded)
            output_hashes[name] = sha256_bytes(encoded)

        summary = payloads.get("summary.json")
        if not isinstance(summary, Mapping) or summary.get("passed") is not True:
            raise ValueError(
                "refusing to promote an experiment bundle whose summary acceptance did not pass"
            )

        decision = _decision_snapshot()
        manifest_inputs = set(input_files)
        package = Path(__file__).resolve().parent
        core_sources = {
            package / "common.py",
            package / "contracts.py",
            package / "state_machine.py",
        }
        manifest_inputs.update(core_sources)
        experiment_number = experiment_id.removeprefix("EXP-")
        experiment_module = package / f"exp{experiment_number}.py"
        if experiment_module.is_file():
            manifest_inputs.add(experiment_module)
        missing_sources = sorted(path for path in manifest_inputs if not path.is_file())
        if missing_sources:
            raise ValueError(
                "manifest source inputs are missing: "
                + ", ".join(relative_path(path) for path in missing_sources)
            )
        if decision["path"] is not None:
            manifest_inputs.add(decision["path"])
        input_hashes = {relative_path(path): sha256_file(path) for path in sorted(manifest_inputs)}
        git_revision, git_dirty = _git_state()
        stable_parameters = dict(parameters)
        runtime_versions = {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
        }
        stable_payload = {
            "experiment_id": experiment_id,
            "experiment_version": experiment_version,
            "config_version": config_version,
            "decision_snapshot_sha256": decision["sha256"],
            "decision_snapshot_status": decision["status"],
            "git_revision": git_revision,
            "git_dirty": git_dirty,
            "input_hashes": input_hashes,
            "output_hashes": output_hashes,
            "metric_schema": dict(metric_schema),
            "claim_scope": CLAIM_SCOPE,
            "parameters": stable_parameters,
            "runtime_versions": runtime_versions,
            "schema_version": "1.0",
        }
        normalized_manifest_sha256_value = normalized_manifest_sha256(stable_payload)
        run_id = stable_identifier(experiment_id, stable_payload, length=20)
        completed = datetime.now(timezone.utc)
        manifest = ExperimentRunManifest(
            experiment_id=experiment_id,
            run_id=run_id,
            experiment_version=experiment_version,
            config_version=config_version,
            decision_snapshot_sha256=decision["sha256"],
            decision_snapshot_status=decision["status"],
            decision_snapshot_source=decision["source"],
            git_revision=git_revision,
            git_dirty=git_dirty,
            started_at=started.isoformat(),
            completed_at=completed.isoformat(),
            input_hashes=input_hashes,
            output_hashes=output_hashes,
            metric_schema=dict(metric_schema),
            claim_scope=CLAIM_SCOPE,
            parameters=stable_parameters,
            runtime_versions=runtime_versions,
            normalized_manifest_sha256=normalized_manifest_sha256_value,
        )
        _write_staged(
            stage / "manifest.json",
            (
                json.dumps(manifest.to_dict(), ensure_ascii=False, sort_keys=True, indent=2) + "\n"
            ).encode("utf-8"),
        )
        _promote_directory(stage, output_dir)
        return manifest
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def print_completion(experiment_id: str, output_dir: Path, summary: Mapping[str, Any]) -> None:
    print(f"{experiment_id} complete -> {output_dir}")
    print(canonical_json(summary))
