"""Compatibility bridge to the canonical VEGO-AI H-layer runtime.

The bridge keeps the historical standalone CLIs working without requiring an
editable package install. It performs no work at import time.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

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


def _resolved_destination(path: str | Path) -> Path:
    target = Path(path)
    if not target.is_absolute():
        target = Path.cwd() / target
    return target.resolve(strict=False)


def _destinations_collide(output_path: str | Path, manifest_path: str | Path) -> bool:
    output = _resolved_destination(output_path)
    manifest = _resolved_destination(manifest_path)
    if output == manifest:
        return True
    try:
        return output.exists() and manifest.exists() and output.samefile(manifest)
    except OSError:
        return False


def publish_stage_output(
    stage: str,
    payload: Any,
    *,
    output_path: str | Path,
    writer: Callable[[Any, str | Path], Any],
    architecture_mode: str = "legacy",
    architecture_manifest: str | Path | None = None,
) -> ArchitectureExecution:
    """Validate, publish the artifact, then publish its manifest.

    The output and manifest must be distinct files. A writer failure is allowed
    to propagate and cannot leave behind a manifest that claims publication
    succeeded.
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
    writer(execution.output, output_path)
    if architecture_manifest is not None:
        write_manifest(execution.manifest, architecture_manifest)
    return execution


__all__ = [
    "ARCHITECTURE_MODES",
    "ArchitectureExecution",
    "add_architecture_arguments",
    "apply_stage_architecture",
    "publish_stage_output",
]
