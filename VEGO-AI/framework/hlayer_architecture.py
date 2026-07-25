"""Compatibility bridge to the canonical VEGO-AI H-layer runtime.

The bridge keeps the historical standalone CLIs working without requiring an
editable package install. It performs no work at import time.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from vego_hlayer.runtime import (  # noqa: E402
    ARCHITECTURE_MODES,
    ArchitectureExecution,
    apply_architecture_mode,
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
    return apply_architecture_mode(
        stage,
        payload,
        architecture_mode=architecture_mode,
        manifest_path=architecture_manifest,
    )


__all__ = [
    "ARCHITECTURE_MODES",
    "ArchitectureExecution",
    "add_architecture_arguments",
    "apply_stage_architecture",
]
