"""Compatibility bridge to the canonical VEGO-AI H-layer runtime.

The bridge keeps the historical standalone CLIs working without requiring an
editable package install. It performs no work at import time.
"""

from __future__ import annotations

import argparse
import os
import stat
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any
from uuid import uuid4

_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from vego_hlayer.contracts import ValidationError  # noqa: E402
from vego_hlayer.runtime import (  # noqa: E402
    ARCHITECTURE_MODES,
    ArchitectureExecution,
    apply_architecture_mode,
    write_manifest,
)


def add_architecture_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--architecture-mode",
        choices=sorted(ARCHITECTURE_MODES),
        default="legacy",
        help="legacy (default), unified contract validation, or fail-closed parity",
    )
    parser.add_argument(
        "--architecture-manifest",
        default=None,
        help="Optional ArchitectureRunManifest JSON path; never use eval_output.",
    )


def apply_stage_architecture(
    stage: str,
    payload: Any,
    *,
    architecture_mode: str = "legacy",
    architecture_manifest: str | Path | None = None,
) -> ArchitectureExecution:
    if architecture_manifest is not None:
        raise ValidationError(
            "architecture manifests must be published after their artifact; "
            "use publish_stage_output"
        )
    return apply_architecture_mode(
        stage,
        payload,
        architecture_mode=architecture_mode,
    )


def _is_link_or_reparse_point(path: Path) -> bool:
    try:
        metadata = os.lstat(path)
    except FileNotFoundError:
        return False
    if stat.S_ISLNK(metadata.st_mode):
        return True
    attributes = getattr(metadata, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(reparse_flag and attributes & reparse_flag)


def _reject_lexical_link_components(path: Path, label: str) -> None:
    """Reject links before resolution so aliases cannot disappear from checks."""

    absolute = path if path.is_absolute() else Path.cwd() / path
    cursor = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        if part in {"", "."}:
            continue
        if part == "..":
            cursor = cursor.parent
            continue
        cursor /= part
        if _is_link_or_reparse_point(cursor):
            raise ValidationError(
                f"{label} paths cannot contain symbolic links or reparse points"
            )


def _resolved_destination(path: str | Path, label: str) -> Path:
    target = Path(path)
    _reject_lexical_link_components(target, label)
    if not target.is_absolute():
        target = Path.cwd() / target
    return target.resolve(strict=False)


def _destinations_collide(output_path: str | Path, manifest_path: str | Path) -> bool:
    output = _resolved_destination(output_path, "artifact output")
    manifest = _resolved_destination(manifest_path, "architecture manifest")
    if output == manifest:
        return True
    try:
        return output.exists() and manifest.exists() and output.samefile(manifest)
    except OSError:
        return False


def _transaction_path(target: Path, role: str, token: str) -> Path:
    return target.with_name(f".{target.name}.{os.getpid()}.{token}.{role}")


def _validate_transaction_destination(target: Path, label: str) -> None:
    _reject_lexical_link_components(target, label)
    if _is_link_or_reparse_point(target):
        raise ValidationError(f"{label} cannot be a symbolic link or reparse point")
    if target.exists() and not target.is_file():
        raise ValidationError(f"{label} must be a regular file")


def _publish_artifact_manifest_pair(
    staged_output: Path,
    output: Path,
    staged_manifest: Path,
    manifest: Path,
    *,
    token: str,
) -> None:
    """Replace an artifact and manifest together with fail-closed rollback.

    The old manifest is moved away from its official path before the artifact
    changes. A process interruption can therefore leave a missing manifest,
    but never a new artifact beside an old success-looking manifest.
    """

    output_backup = _transaction_path(output, "output-backup", token)
    manifest_backup = _transaction_path(manifest, "manifest-backup", token)
    for destination, label in (
        (output, "artifact output"),
        (manifest, "architecture manifest"),
        (output_backup, "artifact transaction backup"),
        (manifest_backup, "manifest transaction backup"),
    ):
        _validate_transaction_destination(destination, label)
    if output_backup.exists() or manifest_backup.exists():
        raise ValidationError("refusing to reuse an existing publication backup")

    old_output_moved = False
    old_manifest_moved = False
    new_output_published = False
    new_manifest_published = False
    try:
        if manifest.exists():
            manifest.replace(manifest_backup)
            old_manifest_moved = True
        if output.exists():
            output.replace(output_backup)
            old_output_moved = True
        staged_output.replace(output)
        new_output_published = True
        staged_manifest.replace(manifest)
        new_manifest_published = True
    except BaseException:
        if new_manifest_published and manifest.is_file():
            manifest.unlink()
        if new_output_published and output.is_file():
            output.unlink()
        if old_output_moved and output_backup.is_file():
            output_backup.replace(output)
        if old_manifest_moved and manifest_backup.is_file():
            manifest_backup.replace(manifest)
        raise
    else:
        if output_backup.is_file():
            output_backup.unlink()
        if manifest_backup.is_file():
            manifest_backup.unlink()


def publish_stage_output(
    stage: str,
    payload: Any,
    *,
    output_path: str | Path,
    writer: Callable[[Any, str | Path], Any],
    architecture_mode: str = "legacy",
    architecture_manifest: str | Path | None = None,
) -> ArchitectureExecution:
    """Validate and transactionally publish an artifact/manifest pair.

    The output and manifest must be distinct files. A writer failure is allowed
    to propagate. When a manifest is requested, both files are staged before
    replacement and rollback restores the previous pair on a handled failure.
    """
    if architecture_manifest is not None and _destinations_collide(
        output_path,
        architecture_manifest,
    ):
        raise ValidationError(
            "artifact output and architecture manifest must use different paths"
        )
    execution = apply_stage_architecture(
        stage,
        payload,
        architecture_mode=architecture_mode,
    )
    if architecture_manifest is None:
        output = _resolved_destination(output_path, "artifact output")
        _validate_transaction_destination(output, "artifact output")
        writer(execution.output, output)
        return execution

    output = _resolved_destination(output_path, "artifact output")
    manifest = _resolved_destination(
        architecture_manifest,
        "architecture manifest",
    )
    _validate_transaction_destination(output, "artifact output")
    _validate_transaction_destination(manifest, "architecture manifest")
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    token = uuid4().hex
    staged_output = _transaction_path(output, "output-stage", token)
    staged_manifest = _transaction_path(manifest, "manifest-stage", token)
    try:
        writer(execution.output, staged_output)
        if not staged_output.is_file() or staged_output.is_symlink():
            raise ValidationError("artifact writer did not produce a regular staged file")
        write_manifest(execution.manifest, staged_manifest)
        _publish_artifact_manifest_pair(
            staged_output,
            output,
            staged_manifest,
            manifest,
            token=token,
        )
    finally:
        if staged_output.is_file() or staged_output.is_symlink():
            staged_output.unlink()
        if staged_manifest.is_file() or staged_manifest.is_symlink():
            staged_manifest.unlink()
    return execution


def require_cli_parity_success(execution: ArchitectureExecution) -> None:
    """Exit nonzero after fail-closed publication when parity detects drift."""

    if execution.manifest.parity_status != "mismatch":
        return
    print(
        "ERROR: unified/legacy parity mismatch; legacy output was preserved",
        file=sys.stderr,
    )
    raise SystemExit(1)


__all__ = [
    "ARCHITECTURE_MODES",
    "ArchitectureExecution",
    "add_architecture_arguments",
    "apply_stage_architecture",
    "publish_stage_output",
    "require_cli_parity_success",
]
