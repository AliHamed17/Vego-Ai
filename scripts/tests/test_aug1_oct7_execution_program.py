from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/validate_aug1_oct7_execution_program.py"
BOARD = ROOT / "docs/research/phd-proposal/aug1-oct7-execution-control-board.json"
SPEC = importlib.util.spec_from_file_location("validate_aug1_oct7_execution_program", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def canonical_board() -> dict[str, object]:
    return json.loads(BOARD.read_text(encoding="utf-8"))


def complete_board(tmp_path: Path) -> dict[str, object]:
    evidence_file = tmp_path / "evidence" / "complete.txt"
    evidence_file.parent.mkdir(parents=True)
    evidence_file.write_text("verified evidence\n", encoding="utf-8")
    digest = hashlib.sha256(evidence_file.read_bytes()).hexdigest()
    final_statuses = sorted(MODULE.FINAL_STATUSES)
    blocking_statuses = sorted(MODULE.BLOCKING_STATUSES)
    return {
        "schemaVersion": MODULE.SCHEMA_VERSION,
        "programId": "TEST-PROGRAM",
        "title": "Complete synthetic control board",
        "baselineAt": "2026-08-01T00:00:00+03:00",
        "timezone": MODULE.TIMEZONE_NAME,
        "window": {
            "startAt": "2026-08-01T00:00:00+03:00",
            "endAt": "2026-10-07T23:59:00+03:00",
        },
        "claimBoundary": "Synthetic validator fixture only.",
        "completionPolicy": {
            "silenceIsAcceptance": False,
            "denominatorIsDynamic": True,
            "finalStatuses": final_statuses,
            "blockingStatuses": blocking_statuses,
            "medicalFallback": {
                "checkpointAt": "2026-08-26T23:59:00+03:00",
                "requiredGateCount": 6,
                "rule": "Test fallback rule.",
            },
        },
        "roles": [
            {
                "id": "ALI",
                "title": "Test owner",
                "kind": "internal_human",
                "filled": True,
                "name": "Ali",
            }
        ],
        "coverageRequirements": {
            "controlIds": list(MODULE.EXPECTED_CONTROL_IDS),
            "assuranceExperimentIds": list(MODULE.EXPECTED_ASSURANCE_EXPERIMENT_IDS),
            "canonicalExperimentIds": list(MODULE.EXPECTED_CANONICAL_EXPERIMENT_IDS),
        },
        "coverageMap": {
            "controls": {source_id: ["WP-001"] for source_id in MODULE.EXPECTED_CONTROL_IDS},
            "assuranceExperiments": {
                source_id: ["WP-001"] for source_id in MODULE.EXPECTED_ASSURANCE_EXPERIMENT_IDS
            },
            "canonicalExperiments": {
                source_id: ["WP-001"] for source_id in MODULE.EXPECTED_CANONICAL_EXPERIMENT_IDS
            },
        },
        "dependencyTypes": {},
        "gateEvidenceBindings": {
            "GATE-WP001-01": {
                "requiredEvidenceKinds": ["test_evidence"],
                "requiredApproverRoles": ["ALI"],
            }
        },
        "modeRequirements": {
            "readinessWorkPackageIds": ["WP-001"],
            "closureWorkPackageIds": ["WP-001"],
            "requiredClosureEvidenceKinds": ["test_evidence"],
        },
        "workPackages": [
            {
                "id": "WP-001",
                "title": "Complete test work package",
                "phase": "Test",
                "ownerRoles": ["ALI"],
                "dueAt": "2026-08-02T12:00:00+03:00",
                "dependsOn": [],
                "status": "accepted",
                "deliverables": [
                    {
                        "id": "DEL-WP001-01",
                        "description": "Verified file",
                        "locator": "evidence/complete.txt",
                        "evidenceRequired": True,
                        "evidenceIds": ["EV-WP001-01"],
                    }
                ],
                "acceptanceChecks": [
                    {
                        "id": "AC-WP001-01",
                        "description": "Evidence accepted",
                        "state": "passed",
                        "evidenceIds": ["EV-WP001-01"],
                    }
                ],
                "evidence": [
                    {
                        "id": "EV-WP001-01",
                        "kind": "test_evidence",
                        "locator": "evidence/complete.txt",
                        "state": "verified",
                        "sha256": digest,
                        "verifiedAt": "2026-08-02T11:00:00+03:00",
                        "verifiedByRole": "ALI",
                        "approvedByRoles": ["ALI"],
                    }
                ],
                "gates": [
                    {
                        "id": "GATE-WP001-01",
                        "kind": "internal",
                        "description": "Evidence accepted",
                        "ownerRole": "ALI",
                        "state": "satisfied",
                        "evidenceIds": ["EV-WP001-01"],
                    }
                ],
            }
        ],
    }


def test_canonical_board_passes_structure_only() -> None:
    board = canonical_board()

    assert MODULE.validate(board, "structure") == []
    assert len(board["workPackages"]) == 29
    assert set(board["modeRequirements"]["closureWorkPackageIds"]) == {
        package["id"] for package in board["workPackages"]
    }
    assert tuple(board["coverageRequirements"]["controlIds"]) == MODULE.EXPECTED_CONTROL_IDS
    assert set(board["coverageMap"]["assuranceExperiments"]) == set(
        MODULE.EXPECTED_ASSURANCE_EXPERIMENT_IDS
    )
    assert set(board["coverageMap"]["canonicalExperiments"]) == set(
        MODULE.EXPECTED_CANONICAL_EXPERIMENT_IDS
    )


def test_canonical_board_fails_closed_for_readiness_and_closure() -> None:
    board = canonical_board()

    readiness = MODULE.validate(board, "readiness")
    closure = MODULE.validate(board, "closure")

    assert readiness
    assert closure
    assert "human_gate.pending" in {item.code for item in readiness}
    assert "external_gate.pending" in {item.code for item in readiness}
    assert "closure.evidence_kind" in {item.code for item in closure}
    assert any("authorized_submission_receipt" in item.message for item in closure)


def test_structure_rejects_unknown_dependency_and_cycle() -> None:
    board = canonical_board()
    second = board["workPackages"][1]
    first = board["workPackages"][0]
    first["dependsOn"] = [second["id"]]
    second["dependsOn"] = [first["id"], "WP-999"]

    issues = MODULE.validate(board, "structure")
    codes = {item.code for item in issues}

    assert "work_package.dependency_unknown" in codes
    assert "work_package.dependency_cycle" in codes
    assert "work_package.dependency_due_order" in codes


def test_structure_rejects_false_final_human_gate() -> None:
    board = canonical_board()
    package = board["workPackages"][1]
    package["status"] = "accepted"

    issues = MODULE.validate(board, "structure")
    codes = {item.code for item in issues}

    assert "work_package.false_final" in codes
    assert "work_package.false_final_gate" in codes
    assert "work_package.false_ready" in codes


def test_structure_rejects_missing_exact_control_coverage() -> None:
    board = canonical_board()
    del board["coverageMap"]["controls"]["R-19"]

    issues = MODULE.validate(board, "structure")

    assert "coverage.exact" in {item.code for item in issues}


def test_fully_evidenced_fixture_passes_all_modes(tmp_path: Path) -> None:
    board = complete_board(tmp_path)

    assert MODULE.validate(board, "structure", root=tmp_path) == []
    assert MODULE.validate(board, "readiness", root=tmp_path) == []
    assert MODULE.validate(board, "closure", root=tmp_path) == []


def test_readiness_rejects_hash_mismatch(tmp_path: Path) -> None:
    board = complete_board(tmp_path)
    board["workPackages"][0]["evidence"][0]["sha256"] = "0" * 64

    issues = MODULE.validate(board, "readiness", root=tmp_path)

    assert "evidence.hash_mismatch" in {item.code for item in issues}


def test_readiness_requires_accountable_evidence_approval(tmp_path: Path) -> None:
    board = complete_board(tmp_path)
    board["workPackages"][0]["evidence"][0]["approvedByRoles"] = []

    assert MODULE.validate(board, "structure", root=tmp_path) == []
    issues = MODULE.validate(board, "readiness", root=tmp_path)
    codes = {item.code for item in issues}

    assert "acceptance.approver_missing" in codes
    assert "gate.approver_missing" in codes


def test_closure_ignores_unreferenced_verified_evidence(tmp_path: Path) -> None:
    board = complete_board(tmp_path)
    package = board["workPackages"][0]
    orphan = dict(package["evidence"][0])
    orphan["id"] = "EV-WP001-ORPHAN"
    orphan["kind"] = "orphan_closure_kind"
    package["evidence"].append(orphan)
    board["modeRequirements"]["requiredClosureEvidenceKinds"].append("orphan_closure_kind")

    assert MODULE.validate(board, "structure", root=tmp_path) == []
    issues = MODULE.validate(board, "closure", root=tmp_path)

    assert any(
        item.code == "closure.evidence_kind" and "orphan_closure_kind" in item.message
        for item in issues
    )


def _add_blocked_dependency(board: dict[str, object], dependency_type: str) -> None:
    package = board["workPackages"][0]
    predecessor = json.loads(
        json.dumps(package).replace("WP-001", "WP-002").replace("WP001", "WP002")
    )
    predecessor["status"] = "blocked"
    predecessor["dueAt"] = "2026-08-01T12:00:00+03:00"
    predecessor["acceptanceChecks"][0]["state"] = "failed"
    predecessor["gates"][0]["state"] = "failed"
    package["dependsOn"] = ["WP-002"]
    board["workPackages"].append(predecessor)
    board["modeRequirements"]["closureWorkPackageIds"].append("WP-002")
    board["dependencyTypes"] = {"WP-001<-WP-002": dependency_type}
    board["gateEvidenceBindings"]["GATE-WP002-01"] = {
        "requiredEvidenceKinds": ["test_evidence"],
        "requiredApproverRoles": ["ALI"],
    }


def test_readiness_enforces_hard_dependency_despite_blocked_evidence(
    tmp_path: Path,
) -> None:
    board = complete_board(tmp_path)
    _add_blocked_dependency(board, "hard")

    assert MODULE.validate(board, "structure", root=tmp_path) == []
    issues = MODULE.validate(board, "readiness", root=tmp_path)

    assert "dependency.hard_not_ready" in {item.code for item in issues}


def test_readiness_allows_documented_status_snapshot_or_conditional_block(
    tmp_path: Path,
) -> None:
    board = complete_board(tmp_path)
    _add_blocked_dependency(board, "status_snapshot")

    assert MODULE.validate(board, "readiness", root=tmp_path) == []
    board["dependencyTypes"]["WP-001<-WP-002"] = "conditional"
    assert MODULE.validate(board, "readiness", root=tmp_path) == []


def test_readiness_rejects_pending_human_gate_even_with_verified_file(
    tmp_path: Path,
) -> None:
    board = complete_board(tmp_path)
    package = board["workPackages"][0]
    package["status"] = "evidence_ready"
    package["gates"][0]["kind"] = "human"
    package["gates"][0]["state"] = "pending"
    package["gates"][0]["evidenceIds"] = []

    assert MODULE.validate(board, "structure", root=tmp_path) == []
    issues = MODULE.validate(board, "readiness", root=tmp_path)

    assert "human_gate.pending" in {item.code for item in issues}


def test_overdue_check_is_explicit_and_optional(tmp_path: Path) -> None:
    board = complete_board(tmp_path)
    package = board["workPackages"][0]
    package["status"] = "partial"
    package["acceptanceChecks"][0]["state"] = "pending"
    package["acceptanceChecks"][0]["evidenceIds"] = []
    package["gates"][0]["state"] = "pending"
    package["gates"][0]["evidenceIds"] = []

    issues = MODULE.validate(
        board,
        "readiness",
        root=tmp_path,
        as_of=datetime.fromisoformat("2026-08-03T00:00:00+03:00"),
    )

    assert "schedule.overdue" in {item.code for item in issues}
