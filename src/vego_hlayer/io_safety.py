"""Filesystem safety helpers for the additive unified H-layer CLI.

The historical M1-M4B-1 commands keep their public paths.  The new unified
entry point uses these stricter guards so untrusted paths cannot target the
baseline, Git metadata, symlinks, or unexpectedly large inputs.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from .contracts import ValidationError

DEFAULT_MAX_INPUT_BYTES = 25 * 1024 * 1024
DEFAULT_MAX_RECORDS = 100_000
FORBIDDEN_PARTS = frozenset({"eval_output", ".git"})


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def validate_input_file(
    path: str | Path,
    *,
    max_bytes: int = DEFAULT_MAX_INPUT_BYTES,
) -> Path:
    """Return a resolved regular input file or fail safely."""

    candidate = Path(path)
    if candidate.is_symlink():
        raise ValidationError("symbolic-link inputs are not accepted")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise ValidationError(f"input file is unavailable: {candidate}") from exc
    if not resolved.is_file():
        raise ValidationError("input must be a regular file")
    if resolved.stat().st_size > max_bytes:
        raise ValidationError(f"input exceeds the {max_bytes}-byte limit")
    return resolved


def validate_output_file(
    path: str | Path,
    *,
    repo_root: str | Path,
    allowed_roots: tuple[str | Path, ...] | None = None,
    allow_existing_identical: bool = False,
) -> Path:
    """Validate a new output path against allowlisted roots and protected areas."""

    root = Path(repo_root).resolve(strict=True)
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve(strict=False)
    lowered = {part.lower() for part in resolved.parts}
    if lowered & FORBIDDEN_PARTS:
        raise ValidationError("refusing to write into eval_output or .git")

    roots = allowed_roots or (
        root / "reports" / "generated",
        root / "artifacts",
        root / "VEGO-AI" / "runs",
        Path(tempfile.gettempdir()),
    )
    resolved_roots = tuple(Path(item).resolve(strict=False) for item in roots)
    if not any(_within(resolved, allowed) for allowed in resolved_roots):
        raise ValidationError("output path is outside the approved output roots")

    cursor = resolved.parent
    while cursor != cursor.parent:
        if cursor.exists() and cursor.is_symlink():
            raise ValidationError("symbolic-link output parents are not accepted")
        if cursor == root or any(cursor == item for item in resolved_roots):
            break
        cursor = cursor.parent
    if resolved.exists():
        if resolved.is_symlink() or not resolved.is_file():
            raise ValidationError("existing output is not a regular file")
        if not allow_existing_identical:
            raise ValidationError("refusing to overwrite an existing output")
    return resolved


def atomic_write_text(path: Path, content: str) -> None:
    """Create a text artifact atomically without following a target symlink."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.exists():
        raise ValidationError("temporary output already exists")
    try:
        temporary.write_text(content, encoding="utf-8", newline="\n")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
