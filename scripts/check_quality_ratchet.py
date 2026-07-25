#!/usr/bin/env python3
"""Apply strict lint/security checks to new hardening code without mass-rewriting legacy files."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STRICT_PATHS = (
    "src/vego_hlayer",
    "scripts/check_dependency_lock.py",
    "scripts/check_hlayer_change_authorization.py",
    "scripts/check_quality_ratchet.py",
    "scripts/build_hardening_manifests.py",
    "scripts/run_hlayer_architecture.py",
    "scripts/security_audit.py",
    "scripts/vego_doctor.py",
    "scripts/verify_hlayer_controlled_parity.py",
    "tests/hlayer_offline/test_unified_runtime.py",
    "VEGO-AI/framework/hlayer_architecture.py",
    "VEGO-AI/framework/llm_client.py",
    "VEGO-AI/tests/test_llm_client_security.py",
)


def main() -> int:
    command = [
        sys.executable,
        "-m",
        "ruff",
        "check",
        "--select",
        "F,B,I,S,UP",
        "--ignore",
        "S101",
        *STRICT_PATHS,
    ]
    # The command is fully assembled from local constants and the current
    # interpreter; no user-controlled shell input is accepted.
    return subprocess.run(command, cwd=ROOT).returncode  # noqa: S603


if __name__ == "__main__":
    raise SystemExit(main())
