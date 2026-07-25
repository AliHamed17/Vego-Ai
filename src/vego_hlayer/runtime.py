"""Legacy, unified, and fail-closed parity execution for H-layer artifacts."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from .adapters import adapt_legacy_artifact
from .contracts import ArchitectureRunManifest, ValidationError, canonical_json
from .io_safety import atomic_write_text

ARCHITECTURE_MODES = frozenset({"legacy", "unified", "parity"})
NORMALIZED_KEYS = frozenset({"created_at", "generated_at", "run_id"})


@dataclass(frozen=True)
class ArchitectureExecution:
    output: Any
    canonical_records: tuple[dict[str, Any], ...]
    manifest: ArchitectureRunManifest


def _sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _normalize(item)
            for key, item in sorted(value.items())
            if key not in NORMALIZED_KEYS
        }
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize(item) for item in value]
    return value


def _safe_manifest_path(path: str | Path) -> Path:
    target = Path(path)
    lowered = {part.lower() for part in target.parts}
    if lowered & {"eval_output", ".git"}:
        raise ValidationError("architecture manifests cannot be written into protected outputs")
    if target.is_symlink():
        raise ValidationError("architecture manifests cannot target symbolic links")
    return target


def write_manifest(manifest: ArchitectureRunManifest, path: str | Path) -> None:
    target = _safe_manifest_path(path)
    content = canonical_json(manifest.to_dict()) + "\n"
    if target.exists():
        if target.read_text(encoding="utf-8") == content:
            return
        raise ValidationError("refusing to overwrite a different architecture manifest")
    atomic_write_text(
        target,
        content,
    )


def apply_architecture_mode(
    stage: str,
    legacy_output: Any,
    *,
    architecture_mode: str = "legacy",
    manifest_path: str | Path | None = None,
) -> ArchitectureExecution:
    """Apply canonical validation without allowing a parity mismatch to publish.

    Unified mode is a deterministic legacy-contract adapter in this release.
    It changes the internal representation, not the public artifact semantics.
    """

    if architecture_mode not in ARCHITECTURE_MODES:
        raise ValidationError(
            f"architecture_mode must be one of {sorted(ARCHITECTURE_MODES)}"
        )
    legacy = copy.deepcopy(legacy_output)
    adapted = adapt_legacy_artifact(stage, legacy)
    unified = adapted.to_legacy()
    legacy_hash = _sha256(legacy)
    unified_hash = _sha256(unified)
    normalized_match = _normalize(legacy) == _normalize(unified)

    if architecture_mode == "legacy":
        published = legacy
        parity_status = "not_run"
        failure_state = None
    elif architecture_mode == "unified":
        if not normalized_match:
            raise ValidationError("unified adapter changed public artifact semantics")
        published = unified
        parity_status = "match"
        failure_state = None
    else:
        parity_status = "match" if normalized_match else "mismatch"
        failure_state = None if normalized_match else "normalized_output_mismatch"
        published = legacy

    run_seed = {
        "stage": stage,
        "architecture_mode": architecture_mode,
        "input_sha256": legacy_hash,
        "unified_output_sha256": unified_hash,
    }
    run_id = f"HLAYER-{sha256(canonical_json(run_seed).encode('utf-8')).hexdigest()[:16]}"
    manifest = ArchitectureRunManifest(
        run_id=run_id,
        stage=stage,
        architecture_mode=architecture_mode,
        input_sha256=legacy_hash,
        legacy_output_sha256=legacy_hash,
        unified_output_sha256=unified_hash,
        published_output_sha256=_sha256(published),
        parity_status=parity_status,
        normalization_rules=tuple(sorted(NORMALIZED_KEYS)),
        baseline_preserved=True,
        failure_state=failure_state,
    )
    if manifest_path is not None:
        write_manifest(manifest, manifest_path)
    return ArchitectureExecution(
        output=published,
        canonical_records=adapted.records,
        manifest=manifest,
    )
