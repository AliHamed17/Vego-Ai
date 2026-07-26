#!/usr/bin/env python3
"""Shared reproducibility helpers for the offline H-layer experiments.

The helpers deliberately know nothing about VEGO-AI runtime behavior.  They
only resolve generated-output locations, validate the existing EXP-005 gate,
hash inputs/outputs, and write deterministic metadata for an offline run.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import uuid
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA_VERSION = "1.0"
ALLOWED_LABELS = {
    "Substantial Variability",
    "Occasional Variability",
    "Undetermined / Needs Review",
}
SAFE_LEAKAGE_ALLOWLIST = frozenset({"none", "cross_setting_memory_used"})
DECISION_IDS = tuple(f"M-{number:02d}" for number in range(1, 7))
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
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_EXPERIMENT_OUTPUTS = {
    "exp006": frozenset({"events.csv", "summary.json", "summary.md"}),
    "exp007": frozenset({"contract-boundary.json", "summary.json", "summary.md"}),
    "exp008": frozenset({"unstable_guidelines.csv", "summary.json", "summary.md"}),
    "exp009": frozenset({"dialogue_traces.json", "summary.json", "summary.md"}),
    "exp010": frozenset({"summary.json", "summary.md"}),
    "exp012": frozenset({"summary.json", "summary.md"}),
}


class HarnessError(RuntimeError):
    """Raised when a run cannot satisfy the reproducibility contract."""


def output_root() -> Path:
    return Path(os.environ.get("HLAYER_OUTPUT_ROOT", REPO / "reports" / "generated")).resolve()


def source_generated_root() -> Path:
    return Path(
        os.environ.get("HLAYER_SOURCE_GENERATED_ROOT", REPO / "reports" / "generated")
    ).resolve()


def experiment_output_dir(name: str) -> Path:
    return output_root() / name


def generated_at() -> str:
    return os.environ.get("HLAYER_GENERATED_AT") or datetime.now(timezone.utc).isoformat()


def run_id() -> str:
    value = os.environ.get("HLAYER_RUN_ID")
    if value:
        return value
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"hlayer-{stamp}-{os.getpid()}"


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def read_json(path: Path) -> Any:
    """Read UTF-8 JSON, accepting the BOM emitted by Windows PowerShell 5."""
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def normalized_manifest_digest(value: dict[str, Any]) -> str:
    """Digest a manifest while excluding only run-time identity timestamps.

    Suite manifests additionally exclude each child manifest file's raw hash,
    because that raw file contains the excluded volatile fields; the child's
    own normalized digest remains part of the suite digest.
    """
    normalized = copy.deepcopy(value)
    normalized.pop("run_id", None)
    normalized.pop("generated_at", None)
    normalized.pop("normalized_sha256", None)
    for item in normalized.get("experiments", []) or []:
        if isinstance(item, dict):
            item.pop("manifest", None)
    return stable_digest(normalized)


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        relative_output = resolved.relative_to(output_root())
        return (Path("reports") / "generated" / relative_output).as_posix()
    except ValueError:
        pass
    try:
        return resolved.relative_to(REPO).as_posix()
    except ValueError:
        return str(resolved)


def file_record(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise HarnessError(f"Required file not found: {path}")
    return {
        "path": display_path(path),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def file_records(paths: Iterable[Path]) -> list[dict[str, Any]]:
    unique = {path.resolve() for path in paths}
    return [file_record(path) for path in sorted(unique, key=lambda item: str(item).lower())]


def truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"true", "1", "yes", "y"}


def normalize_label(value: str) -> str:
    label = (value or "").strip()
    return "Undetermined / Needs Review" if label == "Undetermined" else label


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise HarnessError(f"Required CSV not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def exp005_dir() -> Path:
    return Path(
        os.environ.get("HLAYER_EXP005_DIR", source_generated_root() / "exp005_label_review")
    ).resolve()


def load_exp005_gate() -> dict[str, Any]:
    """Validate the EXP-005 summary against its full review sheet.

    Validation is delegated to the canonical EXP-005 validation functions so
    future reviewer/rationale rules cannot silently drift in this harness.
    """
    gate_dir = exp005_dir()
    summary_path = gate_dir / "label_validation_summary.json"
    rows_path = gate_dir / "exp005_label_review_full.csv"
    if not summary_path.is_file() or not rows_path.is_file():
        raise HarnessError(
            f"EXP-005 validated interface is incomplete; expected {summary_path} and {rows_path}"
        )
    try:
        summary = read_json(summary_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise HarnessError(f"Invalid EXP-005 validation summary: {exc}") from exc
    if summary.get("experiment_id") != "EXP-005":
        raise HarnessError("EXP-005 validation summary has the wrong experiment_id")

    rows = read_csv(rows_path)
    try:
        from exp005_label_review import summarize_labels  # type: ignore

        recomputed, _ = summarize_labels(rows)
    except Exception as exc:  # canonical validator errors must block the run
        raise HarnessError(f"Could not revalidate EXP-005 rows: {exc}") from exc

    checked_fields = (
        "row_count",
        "labels_supplied_count",
        "valid_label_count",
        "invalid_label_count",
        "generalization_safe_candidate_count",
        "generalization_safe_valid_label_count",
        "same_pattern_valid_label_count",
    )
    mismatches = {
        key: {"summary": summary.get(key), "recomputed": recomputed.get(key)}
        for key in checked_fields
        if summary.get(key) != recomputed.get(key)
    }
    if mismatches:
        raise HarnessError(f"EXP-005 validation summary is stale or inconsistent: {mismatches}")
    for section in ("strict_gate", "reviewer_reliability"):
        if summary.get(section) != recomputed.get(section):
            raise HarnessError(
                f"EXP-005 {section} is stale or inconsistent: "
                f"summary={summary.get(section)!r}, recomputed={recomputed.get(section)!r}"
            )

    gate = {
        "validated": True,
        "source": file_record(summary_path),
        "review_rows": file_record(rows_path),
        "counts": {key: summary.get(key) for key in checked_fields},
        "strict_gate": summary.get("strict_gate", {}),
        "reviewer_reliability": summary.get("reviewer_reliability", {}),
        "claim_boundary": (
            "No accuracy, generalization, or clinical-performance claim is authorized by this snapshot."
        ),
    }
    gate["snapshot_sha256"] = stable_digest(gate)
    return gate


def exp005_gate_sentence(gate: dict[str, Any]) -> str:
    count = int(gate.get("counts", {}).get("generalization_safe_valid_label_count") or 0)
    if count == 0:
        return "EXP-005 has 0 validated generalization-safe expert labels; downstream evaluation remains parked."
    if count < 20:
        return f"EXP-005 has {count} validated generalization-safe expert labels; results remain pilot-only."
    return (
        f"EXP-005 has {count} validated generalization-safe expert labels; quantitative evaluation is "
        "available, but no improvement claim is implied."
    )


def validate_decision_snapshot_data(data: dict[str, Any]) -> bool:
    """Validate integrity and derive the conservative offline-only state."""
    if data.get("schema_version") != "1.0":
        raise HarnessError("H-layer decision snapshot must use schema_version 1.0")
    if data.get("decision_ids") != list(DECISION_IDS):
        raise HarnessError(f"H-layer decision snapshot must list exactly {list(DECISION_IDS)}")
    decisions = data.get("decisions")
    if not isinstance(decisions, list) or len(decisions) != len(DECISION_IDS):
        raise HarnessError("H-layer decision snapshot must contain exactly six decision records")
    record_ids = [record.get("id") for record in decisions if isinstance(record, dict)]
    if len(record_ids) != len(decisions) or record_ids != list(DECISION_IDS):
        raise HarnessError("H-layer decision records must be unique and ordered M-01 through M-06")

    declared_hash = str(data.get("snapshot_sha256") or "").lower()
    if not SHA256_PATTERN.fullmatch(declared_hash):
        raise HarnessError("H-layer decision snapshot has no valid snapshot_sha256")
    payload = copy.deepcopy(data)
    payload.pop("snapshot_sha256", None)
    recomputed_hash = stable_digest(payload)
    if declared_hash != recomputed_hash:
        raise HarnessError(
            f"H-layer decision snapshot hash mismatch: declared {declared_hash}, recomputed {recomputed_hash}"
        )

    by_id = {record["id"]: record for record in decisions}
    complete = all(
        by_id[decision_id].get("decision_complete") is True
        for decision_id in ("M-02", "M-03", "M-04", "M-05")
    )
    m05 = by_id["M-05"]
    m05_accepted = m05.get("accepted") is True and m05.get("effective_outcome") in ACCEPTED_OUTCOMES
    authorization = data.get("authorization_record")
    authorization_valid = (
        isinstance(authorization, dict)
        and authorization.get("allowed_touch_outcome") in ACCEPTED_OUTCOMES
        and authorization.get("implementation_outcome") in ACCEPTED_OUTCOMES
        and isinstance(authorization.get("allowed_touches"), list)
        and len(authorization.get("allowed_touches")) == len(EXPECTED_AUTHORIZED_TOUCHES)
        and all(isinstance(item, str) for item in authorization.get("allowed_touches"))
        and set(authorization.get("allowed_touches")) == set(EXPECTED_AUTHORIZED_TOUCHES)
        and bool(str(authorization.get("approver") or "").strip())
        and bool(str(authorization.get("approved_at") or "").strip())
    )
    blockers = data.get("authorization_blockers")
    no_blockers = isinstance(blockers, list) and not blockers
    derived_live = complete and m05_accepted and authorization_valid and no_blockers
    derived_offline = not derived_live

    reported_offline = data.get("offline_only")
    reported_live = data.get("live_shadow_authorized")
    gate = data.get("implementation_gate")
    if not isinstance(reported_offline, bool) or not isinstance(reported_live, bool):
        raise HarnessError("H-layer decision snapshot authorization flags must be booleans")
    if not isinstance(gate, dict) or not isinstance(gate.get("offline_only"), bool):
        raise HarnessError("H-layer decision snapshot implementation gate is missing offline_only")
    expected_mode = "live_shadow_authorized" if derived_live else "offline_only"
    if (
        reported_offline != derived_offline
        or reported_live != derived_live
        or gate["offline_only"] != derived_offline
        or data.get("program_mode") != expected_mode
    ):
        raise HarnessError(
            "H-layer decision snapshot authorization flags are inconsistent with decision and authorization records"
        )
    return derived_offline


def decision_snapshot() -> dict[str, Any]:
    configured = os.environ.get("HLAYER_DECISION_SNAPSHOT")
    candidates = [Path(configured)] if configured else []
    candidates.extend(
        [
            source_generated_root() / "h_layer_decisions" / "decision_snapshot.json",
            source_generated_root() / "hlayer_decisions" / "decision_snapshot.json",
            source_generated_root() / "h_layer_decision_snapshot.json",
        ]
    )
    path = next(
        (candidate.resolve() for candidate in candidates if candidate and candidate.is_file()), None
    )
    if path is None:
        return {
            "present": False,
            "status": "missing",
            "offline_only": True,
            "reason": "No generated supervisor decision snapshot was found; no defaults were inferred.",
        }
    try:
        data = read_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        raise HarnessError(f"Invalid H-layer decision snapshot: {exc}") from exc

    if not isinstance(data, dict):
        raise HarnessError("H-layer decision snapshot root must be a JSON object")
    offline = validate_decision_snapshot_data(data)
    statuses = data.get("decision_statuses") or data.get("decisions") or {}
    return {
        "present": True,
        "source": file_record(path),
        "status": data.get("status") or data.get("snapshot_status") or "recorded",
        "offline_only": offline,
        "decision_statuses": statuses,
    }


def validate_child_manifest(
    root: Path, name: str, path: Path, data: dict[str, Any], expected_run_id: str | None
) -> str:
    if name not in REQUIRED_EXPERIMENT_OUTPUTS:
        raise HarnessError(f"Unsupported H-layer experiment directory in suite: {name}")
    if data.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise HarnessError(f"{name} manifest has unsupported schema_version")
    expected_id = f"EXP-{name[3:]}"
    if data.get("experiment_id") != expected_id:
        raise HarnessError(
            f"{name} manifest experiment_id {data.get('experiment_id')!r} != {expected_id}"
        )
    if expected_run_id and data.get("run_id") != expected_run_id:
        raise HarnessError(
            f"Stale manifest in {name}: run_id {data.get('run_id')} != {expected_run_id}"
        )

    declared_normalized = str(data.get("normalized_sha256") or "").lower()
    if not SHA256_PATTERN.fullmatch(declared_normalized):
        raise HarnessError(f"{name} manifest has no valid normalized_sha256")
    recomputed_normalized = normalized_manifest_digest(data)
    if declared_normalized != recomputed_normalized:
        raise HarnessError(
            f"{name} normalized manifest mismatch: declared {declared_normalized}, recomputed {recomputed_normalized}"
        )

    outputs = data.get("outputs")
    if not isinstance(outputs, list):
        raise HarnessError(f"{name} manifest outputs must be a list")
    child_dir = (root / name).resolve()
    logical_prefix = Path("reports") / "generated" / name
    declared_names: set[str] = set()
    for record in outputs:
        if not isinstance(record, dict):
            raise HarnessError(f"{name} manifest has a non-object output record")
        logical = Path(str(record.get("path") or ""))
        try:
            relative = logical.relative_to(logical_prefix)
        except ValueError as exc:
            raise HarnessError(
                f"{name} output path escapes its logical directory: {logical}"
            ) from exc
        if not relative.parts or ".." in relative.parts:
            raise HarnessError(f"{name} output path is invalid: {logical}")
        actual = (child_dir / relative).resolve()
        try:
            actual.relative_to(child_dir)
        except ValueError as exc:
            raise HarnessError(
                f"{name} output resolves outside its child directory: {logical}"
            ) from exc
        relative_name = relative.as_posix()
        if relative_name in declared_names:
            raise HarnessError(f"{name} manifest declares output twice: {relative_name}")
        declared_names.add(relative_name)
        if not actual.is_file():
            raise HarnessError(f"{name} declared output does not exist: {actual}")
        declared_hash = str(record.get("sha256") or "").lower()
        declared_bytes = record.get("bytes")
        if not SHA256_PATTERN.fullmatch(declared_hash) or not isinstance(declared_bytes, int):
            raise HarnessError(f"{name} output record lacks valid sha256/bytes: {relative_name}")
        if sha256_file(actual) != declared_hash or actual.stat().st_size != declared_bytes:
            raise HarnessError(f"{name} declared output hash/size does not match: {relative_name}")
    if declared_names != set(REQUIRED_EXPERIMENT_OUTPUTS[name]):
        raise HarnessError(
            f"{name} output set is partial or unexpected: {sorted(declared_names)}; "
            f"expected {sorted(REQUIRED_EXPERIMENT_OUTPUTS[name])}"
        )
    return declared_normalized


def git_snapshot() -> dict[str, Any]:
    def run_git(*args: str) -> str:
        proc = subprocess.run(
            ["git", *args],
            cwd=REPO,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        return proc.stdout.strip() if proc.returncode == 0 else ""

    status = run_git("status", "--porcelain=v1", "--untracked-files=all")
    return {
        "commit": run_git("rev-parse", "HEAD") or None,
        "branch": run_git("branch", "--show-current") or None,
        "dirty": bool(status),
        "status_sha256": hashlib.sha256(status.encode("utf-8")).hexdigest(),
    }


def write_experiment_manifest(
    output_dir: Path,
    *,
    experiment_id: str,
    experiment_version: str,
    config_version: str,
    claim_scope: str,
    script_path: Path,
    inputs: Iterable[Path],
    outputs: Iterable[Path],
    config: dict[str, Any],
    metric_schema: dict[str, Any],
) -> dict[str, Any]:
    gate = load_exp005_gate()
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "run_id": run_id(),
        "experiment_id": experiment_id,
        "experiment_version": experiment_version,
        "config_version": config_version,
        "generated_at": generated_at(),
        "claim_scope": claim_scope,
        "claim_boundary": exp005_gate_sentence(gate),
        "script": file_record(script_path),
        "runtime": {
            "python": sys.version.split()[0],
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "git": git_snapshot(),
        "decision_snapshot": decision_snapshot(),
        "exp005_gate": gate,
        "config": config,
        "metric_schema": metric_schema,
        "inputs": file_records(inputs),
        "outputs": file_records(outputs),
    }
    manifest["normalized_sha256"] = normalized_manifest_digest(manifest)
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def write_suite_manifest(root: Path, experiments: list[str], destination: Path) -> dict[str, Any]:
    expected_experiments = list(REQUIRED_EXPERIMENT_OUTPUTS)
    if experiments != expected_experiments:
        raise HarnessError(
            f"H-layer suite must contain exactly {expected_experiments} in canonical order; got {experiments}"
        )
    manifests: list[dict[str, Any]] = []
    expected_run_id = os.environ.get("HLAYER_RUN_ID")
    for name in experiments:
        path = root / name / "manifest.json"
        if not path.is_file():
            raise HarnessError(f"Missing experiment manifest: {path}")
        try:
            data = read_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            raise HarnessError(f"Invalid experiment manifest {path}: {exc}") from exc
        if not isinstance(data, dict):
            raise HarnessError(f"Experiment manifest root must be an object: {path}")
        normalized_sha256 = validate_child_manifest(root, name, path, data, expected_run_id)
        manifests.append(
            {
                "experiment": name,
                "manifest": file_record(path),
                "normalized_sha256": normalized_sha256,
            }
        )

    gate = load_exp005_gate()
    value = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "run_id": run_id(),
        "generated_at": generated_at(),
        "claim_scope": "Offline mechanism and architecture-conformance evidence only.",
        "claim_boundary": exp005_gate_sentence(gate),
        "git": git_snapshot(),
        "decision_snapshot": decision_snapshot(),
        "exp005_gate": gate,
        "experiments": manifests,
    }
    value["normalized_sha256"] = normalized_manifest_digest(value)
    write_json(destination, value)
    return value


def replace_with_retry(source: Path, destination: Path, attempts: int = 5) -> None:
    """Retry transient Windows file locks without weakening atomic rename semantics."""
    for attempt in range(1, attempts + 1):
        try:
            os.replace(source, destination)
            return
        except PermissionError:
            if attempt == attempts:
                raise
            time.sleep(0.05 * attempt)


def atomic_promote(
    stage_root: Path,
    target_root: Path,
    directories: Iterable[str],
    files: Iterable[str],
) -> None:
    """Promote a complete staged output set with rollback on any rename failure.

    The stage and target must share a filesystem so every individual rename is
    atomic.  Multi-path promotion is protected by moving all existing targets
    to a transaction backup first and restoring them if any later move fails.
    """
    stage_root = stage_root.resolve()
    target_root = target_root.resolve()
    directory_names = list(dict.fromkeys(directories))
    file_names = list(dict.fromkeys(files))
    names = directory_names + file_names
    for name in names:
        source = stage_root / name
        expected = source.is_dir() if name in directory_names else source.is_file()
        if not expected:
            raise HarnessError(f"Staged output is missing or has the wrong type: {source}")

    target_root.mkdir(parents=True, exist_ok=True)
    if stage_root.stat().st_dev != target_root.stat().st_dev:
        raise HarnessError("Atomic promotion requires stage and target on the same filesystem")

    transaction = target_root / f".hlayer-promote-{uuid.uuid4().hex}"
    backup = transaction / "backup"
    incoming = transaction / "incoming"
    backup.mkdir(parents=True)
    incoming.mkdir(parents=True)
    moved_old: list[str] = []
    moved_new: list[str] = []
    try:
        # First move the already-validated staged set under the target parent.
        for name in names:
            replace_with_retry(stage_root / name, incoming / name)
        for name in names:
            target = target_root / name
            if target.exists():
                replace_with_retry(target, backup / name)
                moved_old.append(name)
        for name in names:
            replace_with_retry(incoming / name, target_root / name)
            moved_new.append(name)
    except Exception as exc:
        # Remove newly promoted paths, then restore every prior path.  A failed
        # rollback is surfaced with both errors instead of being hidden.
        rollback_errors: list[str] = []
        for name in reversed(moved_new):
            path = target_root / name
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                elif path.exists():
                    path.unlink()
            except Exception as rollback_exc:  # pragma: no cover - catastrophic filesystem failure
                rollback_errors.append(f"remove {name}: {rollback_exc}")
        for name in reversed(moved_old):
            try:
                replace_with_retry(backup / name, target_root / name)
            except Exception as rollback_exc:  # pragma: no cover
                rollback_errors.append(f"restore {name}: {rollback_exc}")
        detail = f"; rollback errors: {rollback_errors}" if rollback_errors else ""
        raise HarnessError(f"Atomic promotion failed and was rolled back: {exc}{detail}") from exc
    finally:
        shutil.rmtree(transaction, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    gate_parser = sub.add_parser("snapshot-gate")
    gate_parser.add_argument("--output", required=True, type=Path)
    suite_parser = sub.add_parser("suite-manifest")
    suite_parser.add_argument("--output-root", required=True, type=Path)
    suite_parser.add_argument("--output", required=True, type=Path)
    suite_parser.add_argument("--experiments", nargs="+", required=True)
    promote_parser = sub.add_parser("promote")
    promote_parser.add_argument("--stage-root", required=True, type=Path)
    promote_parser.add_argument("--target-root", required=True, type=Path)
    promote_parser.add_argument("--directories", nargs="+", required=True)
    promote_parser.add_argument("--files", nargs="+", required=True)
    normalize_parser = sub.add_parser("normalize-manifest")
    normalize_parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()

    try:
        if args.command == "snapshot-gate":
            write_json(args.output, load_exp005_gate())
        elif args.command == "suite-manifest":
            write_suite_manifest(
                args.output_root.resolve(), args.experiments, args.output.resolve()
            )
        elif args.command == "promote":
            atomic_promote(args.stage_root, args.target_root, args.directories, args.files)
        elif args.command == "normalize-manifest":
            path = args.input.resolve()
            value = read_json(path)
            value["normalized_sha256"] = normalized_manifest_digest(value)
            write_json(path, value)
    except HarnessError as exc:
        print(f"H-layer harness error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
