#!/usr/bin/env python3
"""Build deterministic, tracked fixture evidence for EXP-033–EXP-035."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_bigui_architecture_experiments.py"
PROGRAM = ROOT / "experiments" / "bigui-program-v1.json"
OUTPUT = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "architecture-fixture-results-v1.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    content = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_runner():
    spec = importlib.util.spec_from_file_location(
        "run_bigui_architecture_experiments", RUNNER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load architecture experiment runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build() -> dict:
    runner = load_runner()
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    experiments = [
        runner.exp033_parity(runner.clone_safe_artifacts()),
        runner.exp034_topologies(),
        runner.exp035_faults(),
        {
            "experimentId": "EXP-036",
            "evidenceClass": "proposal",
            "status": "Offline design",
            "targets": {
                "unifiedP95RatioMaximum": 1.15,
                "unifiedPeakMemoryRatioMaximum": 1.5,
                "parityP95RatioMaximum": 2.25,
            },
            "result": None,
            "claimBoundary": (
                "Machine-specific timing remains local and unaccepted; no "
                "operational or accuracy result is published."
            ),
        },
    ]
    payload = {
        "schemaVersion": "BigUIArchitectureFixtureResults-v1",
        "generatedAt": program["generatedAt"],
        "evidenceClass": "offline_fixture",
        "syntheticTag": "SYNTHETIC_NOT_HUMAN",
        "containsControlledData": False,
        "containsHumanLabels": False,
        "experiments": experiments,
        "sources": {
            RUNNER.relative_to(ROOT).as_posix(): sha256(RUNNER),
            PROGRAM.relative_to(ROOT).as_posix(): sha256(PROGRAM),
            "src/vego_hlayer/contracts.py": sha256(
                ROOT / "src" / "vego_hlayer" / "contracts.py"
            ),
            "src/vego_hlayer/runtime.py": sha256(
                ROOT / "src" / "vego_hlayer" / "runtime.py"
            ),
            "src/vego_hlayer/state_machine.py": sha256(
                ROOT / "src" / "vego_hlayer" / "state_machine.py"
            ),
        },
        "claimBoundary": (
            "Clone-safe mechanism, structural, and fault-fixture evidence only. "
            "No accuracy, generalization, effort, topology-approval, or "
            "production-readiness claim."
        ),
    }
    payload["normalizedSha256"] = digest(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        payload = build()
        content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        if args.check:
            if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
                print(f"STALE: {OUTPUT.relative_to(ROOT)}", file=sys.stderr)
                return 1
            print("BigUI architecture fixture snapshot: PASS")
            return 0
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content, encoding="utf-8", newline="\n")
        print(f"WROTE: {OUTPUT.relative_to(ROOT)}")
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"BigUI architecture fixture snapshot: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
