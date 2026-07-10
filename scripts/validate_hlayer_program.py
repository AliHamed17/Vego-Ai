#!/usr/bin/env python3
"""Validate the complete offline H-layer program through one read interface.

This validator bridges the historical replay-suite manifest and the versioned
contract/conformance manifest without changing either runtime API.  It verifies
their canonical hashes, the EXP-006 -> EXP-007 ObservationRecord boundary,
decision/EXP-005 gates, the latest accepted iteration, protected paths, and the
retired prototype marker.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import hlayer_harness as harness  # noqa: E402
from build_hlayer_decision_snapshot import build_snapshot  # noqa: E402
from check_hlayer_protected_paths import check_boundary  # noqa: E402
from hlayer_offline.common import _decision_snapshot as conformance_decision_snapshot  # noqa: E402
from hlayer_offline.suite import DEFAULT_RUNNERS, validate_suite_stage  # noqa: E402


class ProgramValidationError(RuntimeError):
    """Raised when a required program surface is missing or inconsistent."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProgramValidationError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProgramValidationError(f"JSON root must be an object: {path}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProgramValidationError(message)


def validate_decision_gate() -> dict[str, Any]:
    register = REPO / "docs/research/meetings/2026-07-15-supervisor-decision-register.md"
    snapshot_path = REPO / "reports/generated/h_layer_decisions/decision_snapshot.json"
    expected = build_snapshot(register)
    actual = load_json(snapshot_path)
    require(actual == expected, "generated decision snapshot is stale")
    offline = harness.validate_decision_snapshot_data(actual)
    require(offline is True, "current unapproved decision state must remain offline-only")
    return {
        "snapshot_sha256": actual["snapshot_sha256"],
        "source_register_sha256": actual["source_register_sha256"],
        "snapshot_status": actual["snapshot_status"],
        "offline_only": offline,
    }


def validate_replay_suite() -> dict[str, Any]:
    root = REPO / "reports/generated"
    suite_path = root / "hlayer_suite_manifest.json"
    suite = load_json(suite_path)
    expected_names = list(harness.REQUIRED_EXPERIMENT_OUTPUTS)
    require(
        suite.get("schema_version") == harness.MANIFEST_SCHEMA_VERSION,
        "replay suite schema mismatch",
    )
    require(
        [item.get("experiment") for item in suite.get("experiments", [])] == expected_names,
        "replay suite membership/order mismatch",
    )
    declared_suite_digest = suite.get("normalized_sha256")
    require(
        isinstance(declared_suite_digest, str)
        and declared_suite_digest == harness.normalized_manifest_digest(suite),
        "replay suite normalized digest mismatch",
    )
    child_digests: dict[str, str] = {}
    for item in suite["experiments"]:
        name = item["experiment"]
        manifest_path = root / name / "manifest.json"
        manifest = load_json(manifest_path)
        digest = harness.validate_child_manifest(
            root, name, manifest_path, manifest, suite.get("run_id")
        )
        require(item.get("normalized_sha256") == digest, f"{name} suite digest record mismatch")
        require(
            item.get("manifest") == harness.file_record(manifest_path),
            f"{name} suite manifest-file record mismatch",
        )
        child_digests[name] = digest
    require(
        suite.get("decision_snapshot") == harness.decision_snapshot(),
        "replay suite decision snapshot is stale",
    )
    gate = harness.load_exp005_gate()
    require(suite.get("exp005_gate") == gate, "replay suite EXP-005 gate is stale")
    return {
        "run_id": suite["run_id"],
        "normalized_sha256": declared_suite_digest,
        "experiments": child_digests,
        "exp005_safe_labels": gate["counts"]["generalization_safe_valid_label_count"],
        "offline_only": suite["decision_snapshot"]["offline_only"],
    }


def validate_contract_boundary() -> dict[str, Any]:
    summary = load_json(REPO / "reports/generated/exp007/summary.json")
    boundary = load_json(REPO / "reports/generated/exp007/contract-boundary.json")
    require(summary.get("contract_boundary") == boundary, "EXP-007 contract-boundary copy mismatch")
    require(
        boundary.get("all_records_valid") is True,
        "EXP-006 rows did not validate as ObservationRecord",
    )
    require(boundary.get("captured_records") == 481, "EXP-006 captured record count drift")
    require(
        boundary.get("unobservable_gap_records") == 20, "EXP-006 explicit gap record count drift"
    )
    require(
        boundary.get("event_types") == [f"E{i}" for i in range(1, 15)],
        "framework event scope must be E1-E14",
    )
    return boundary


def validate_conformance_suite() -> dict[str, Any]:
    target = REPO / "reports/generated/hlayer_conformance"
    decision = conformance_decision_snapshot()
    expected_ids = [experiment_id for experiment_id, _ in DEFAULT_RUNNERS]
    manifest = validate_suite_stage(target, expected_ids, decision)
    require(
        manifest.get("live_shadow_authorized") is False,
        "conformance suite cannot be live-authorized now",
    )
    return {
        "run_id": manifest["run_id"],
        "normalized_suite_sha256": manifest["normalized_suite_sha256"],
        "experiments": expected_ids,
        "offline_only": not manifest["live_shadow_authorized"],
    }


def validate_latest_iteration(replay_suite: dict[str, Any]) -> dict[str, Any]:
    iteration_root = REPO / "reports/generated/hlayer_iterations"
    candidates: list[tuple[int, Path]] = []
    for path in iteration_root.glob("iter_[0-9][0-9][0-9]"):
        match = re.fullmatch(r"iter_(\d{3})", path.name)
        if match and (path / "iteration_manifest.json").is_file():
            candidates.append((int(match.group(1)), path))
    require(bool(candidates), "no accepted H-layer iteration manifest exists")
    number, latest = max(candidates)
    manifest = load_json(latest / "iteration_manifest.json")
    require(manifest.get("iteration") == number, "latest iteration number mismatch")
    require(
        manifest.get("run_id") == replay_suite["run_id"],
        "latest iteration does not snapshot current replay suite",
    )
    require(
        manifest.get("component_normalized_sha256", {}).get("suite")
        == replay_suite["normalized_sha256"],
        "latest iteration suite digest mismatch",
    )
    require(
        manifest.get("decision_snapshot", {}).get("offline_only") is True,
        "latest iteration is not offline-only",
    )
    require(
        manifest.get("exp005_gate", {})
        .get("counts", {})
        .get("generalization_safe_valid_label_count")
        == 0,
        "latest iteration EXP-005 gate is not the validated zero-label state",
    )
    for name, expected_hash in manifest.get("outputs_sha256", {}).items():
        path = latest / name
        require(
            path.is_file() and sha256_file(path) == expected_hash,
            f"latest iteration output hash mismatch: {name}",
        )
    return {
        "iteration": number,
        "run_id": manifest["run_id"],
        "kind": manifest.get("iteration_kind"),
        "verdict": manifest.get("verdict"),
        "normalized_sha256": manifest.get("normalized_sha256"),
    }


def validate_retired_prototype() -> dict[str, Any]:
    path = REPO / "scripts/hlayer_prototype/hlayer-prototype-scaffold.py"
    text = path.read_text(encoding="utf-8")
    require(
        "RETIRED" in text and "dummy instability" in text, "prototype retirement notice is missing"
    )
    require(
        "class HLayerPrototype" not in text, "misleading prototype implementation remains runnable"
    )
    return {"path": path.relative_to(REPO).as_posix(), "status": "retired_fail_fast"}


def validate_registry() -> dict[str, Any]:
    text = (REPO / "experiments/registry.md").read_text(encoding="utf-8")
    missing = [f"EXP-{number:03d}" for number in range(6, 19) if f"EXP-{number:03d}" not in text]
    require(not missing, f"experiment registry is missing: {', '.join(missing)}")
    return {"registered": [f"EXP-{number:03d}" for number in range(6, 19)]}


def run_checks() -> dict[str, Any]:
    checks: list[tuple[str, Callable[[], dict[str, Any]]]] = [
        ("decision_gate", validate_decision_gate),
        ("replay_suite", validate_replay_suite),
        ("contract_boundary", validate_contract_boundary),
        ("conformance_suite", validate_conformance_suite),
        ("retired_prototype", validate_retired_prototype),
        ("registry", validate_registry),
    ]
    details: dict[str, Any] = {}
    failures: list[str] = []
    for name, check in checks:
        try:
            details[name] = check()
        except Exception as exc:  # collect all independent acceptance failures
            failures.append(f"{name}: {exc}")
    protected = check_boundary(REPO, REPO / "docs/research/h-layer/phase-0-boundary-record.md")
    details["protected_paths"] = protected
    if protected["status"] != "PASS":
        failures.extend(f"protected_paths: {failure}" for failure in protected["failures"])
    if "replay_suite" in details:
        try:
            details["latest_iteration"] = validate_latest_iteration(details["replay_suite"])
        except Exception as exc:
            failures.append(f"latest_iteration: {exc}")
    return {
        "schema_version": "1.0",
        "validator": "h-layer-program",
        "status": "PASS" if not failures else "FAIL",
        "checks_passed": len(details) - (1 if protected["status"] != "PASS" else 0),
        "failures": failures,
        "details": details,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-report", action="store_true", help="Write ignored latest.json/latest.md reports"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_checks()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if args.write_report:
        out = REPO / "reports/generated/hlayer_program_validation"
        out.mkdir(parents=True, exist_ok=True)
        (out / "latest.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        lines = [
            "# H-Layer Program Validation",
            "",
            f"Status: **{result['status']}**",
            "",
            *[f"- {failure}" for failure in result["failures"]],
        ]
        (out / "latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
