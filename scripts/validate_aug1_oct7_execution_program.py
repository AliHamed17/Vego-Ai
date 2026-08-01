#!/usr/bin/env python3
"""Validate the Aug 1-Oct 7 VEGO-AI execution control board.

The validator is deliberately read-only and fail-closed. Structure mode proves
only that the control graph is well formed. Readiness additionally requires the
configured delivery package, hashes, access evidence, and human gates. Closure
requires every work package to have an approved final disposition plus the
specified supervisor, route, approval, receipt, and certificate evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BOARD = ROOT / "docs/research/phd-proposal/aug1-oct7-execution-control-board.json"

MODES = ("structure", "readiness", "closure")
SCHEMA_VERSION = "VegoExecutionControlBoard-v1"
TIMEZONE_NAME = "Asia/Jerusalem"
EXPECTED_OFFSET = timedelta(hours=3)

WORK_PACKAGE_ID = re.compile(r"^WP-\d{3}$")
ROLE_ID = re.compile(r"^[A-Z][A-Z0-9_]*$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")

WORK_PACKAGE_STATUSES = {
    "planned",
    "in_progress",
    "partial",
    "evidence_ready",
    "acceptance_check_passed",
    "blocked",
    "accepted",
    "accepted_ongoing",
    "accepted_after_correction",
    "superseded_approved",
    "not_applicable_approved",
}
FINAL_STATUSES = {
    "accepted",
    "accepted_ongoing",
    "accepted_after_correction",
    "superseded_approved",
    "not_applicable_approved",
}
READY_STATUSES = FINAL_STATUSES | {"evidence_ready", "acceptance_check_passed"}
BLOCKING_STATUSES = WORK_PACKAGE_STATUSES - FINAL_STATUSES
ACCEPTANCE_STATES = {"pending", "passed", "failed", "not_applicable_approved"}
GATE_KINDS = {"internal", "human", "external"}
GATE_STATES = {"pending", "satisfied", "failed", "not_applicable_approved"}
EVIDENCE_STATES = {"pending", "present_unverified", "verified", "rejected"}
ROLE_KINDS = {"internal_human", "human_gate", "external_gate", "tool"}
DEPENDENCY_TYPES = {"hard", "conditional", "status_snapshot"}
EXPECTED_CONTROL_IDS = (
    tuple(f"R-{index:02d}" for index in range(1, 20))
    + tuple(f"A-{index:02d}" for index in range(1, 16))
    + tuple(f"Q-{index:02d}" for index in range(1, 11))
)
EXPECTED_ASSURANCE_EXPERIMENT_IDS = tuple(f"IRIS-EXP-{index:02d}" for index in range(1, 11))
EXPECTED_CANONICAL_EXPERIMENT_IDS = (
    "EXP-005",
    *tuple(f"EXP-{index:03d}" for index in range(19, 28)),
)


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str


def issue(issues: list[Issue], code: str, path: str, message: str) -> None:
    issues.append(Issue(code=code, path=path, message=message))


def load_board(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("board root must be a JSON object")
    return payload


def parse_timestamp(
    value: Any, path: str, issues: list[Issue], *, require_program_offset: bool = True
) -> datetime | None:
    if not isinstance(value, str) or not value:
        issue(issues, "timestamp.missing", path, "timestamp must be a non-empty string")
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        issue(issues, "timestamp.invalid", path, f"invalid ISO-8601 timestamp: {value!r}")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        issue(issues, "timestamp.naive", path, "timestamp must include an explicit offset")
        return None
    if require_program_offset and parsed.utcoffset() != EXPECTED_OFFSET:
        issue(
            issues,
            "timestamp.offset",
            path,
            "program timestamps must use the Asia/Jerusalem +03:00 offset for this window",
        )
    return parsed


def safe_locator(locator: Any) -> bool:
    if not isinstance(locator, str) or not locator.strip():
        return False
    path = Path(locator)
    return not path.is_absolute() and ".." not in path.parts


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _has_cycle(dependencies: dict[str, list[str]]) -> list[str] | None:
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        if node in visiting:
            start = stack.index(node)
            return stack[start:] + [node]
        if node in visited:
            return None
        visiting.add(node)
        stack.append(node)
        for dependency in dependencies.get(node, []):
            cycle = visit(dependency)
            if cycle:
                return cycle
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for candidate in dependencies:
        cycle = visit(candidate)
        if cycle:
            return cycle
    return None


def validate_structure(board: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    required_top = {
        "schemaVersion",
        "programId",
        "title",
        "baselineAt",
        "timezone",
        "window",
        "claimBoundary",
        "completionPolicy",
        "roles",
        "coverageRequirements",
        "coverageMap",
        "modeRequirements",
        "dependencyTypes",
        "gateEvidenceBindings",
        "workPackages",
    }
    for key in sorted(required_top - board.keys()):
        issue(issues, "board.required", key, "required top-level field is missing")

    if board.get("schemaVersion") != SCHEMA_VERSION:
        issue(
            issues,
            "board.schema_version",
            "schemaVersion",
            f"expected {SCHEMA_VERSION!r}",
        )
    if board.get("timezone") != TIMEZONE_NAME:
        issue(
            issues,
            "board.timezone",
            "timezone",
            f"expected {TIMEZONE_NAME!r}",
        )
    if not isinstance(board.get("programId"), str) or not board.get("programId"):
        issue(issues, "board.program_id", "programId", "programId must be non-empty")
    if not isinstance(board.get("claimBoundary"), str) or not board.get("claimBoundary"):
        issue(issues, "board.claim_boundary", "claimBoundary", "claimBoundary is required")

    baseline = parse_timestamp(board.get("baselineAt"), "baselineAt", issues)
    window = board.get("window")
    if not isinstance(window, dict):
        issue(issues, "board.window", "window", "window must be an object")
        window = {}
    start = parse_timestamp(window.get("startAt"), "window.startAt", issues)
    end = parse_timestamp(window.get("endAt"), "window.endAt", issues)
    if start and end and start >= end:
        issue(issues, "board.window_order", "window", "startAt must precede endAt")
    if baseline and start and baseline != start:
        issue(
            issues,
            "board.baseline",
            "baselineAt",
            "baselineAt must equal the controlled window start",
        )

    completion = board.get("completionPolicy")
    if not isinstance(completion, dict):
        issue(
            issues,
            "completion.policy",
            "completionPolicy",
            "completionPolicy must be an object",
        )
        completion = {}
    if completion.get("silenceIsAcceptance") is not False:
        issue(
            issues,
            "completion.silence",
            "completionPolicy.silenceIsAcceptance",
            "silence must never count as acceptance",
        )
    if completion.get("denominatorIsDynamic") is not True:
        issue(
            issues,
            "completion.denominator",
            "completionPolicy.denominatorIsDynamic",
            "newly discovered controls must expand the denominator",
        )
    if set(_as_list(completion.get("finalStatuses"))) != FINAL_STATUSES:
        issue(
            issues,
            "completion.final_statuses",
            "completionPolicy.finalStatuses",
            "finalStatuses must exactly match the approved final dispositions",
        )
    if set(_as_list(completion.get("blockingStatuses"))) != BLOCKING_STATUSES:
        issue(
            issues,
            "completion.blocking_statuses",
            "completionPolicy.blockingStatuses",
            "blockingStatuses must exactly cover every non-final state",
        )
    fallback = completion.get("medicalFallback")
    if not isinstance(fallback, dict):
        issue(
            issues,
            "completion.medical_fallback",
            "completionPolicy.medicalFallback",
            "medicalFallback must be an object",
        )
    else:
        parse_timestamp(
            fallback.get("checkpointAt"),
            "completionPolicy.medicalFallback.checkpointAt",
            issues,
        )
        if fallback.get("requiredGateCount") != 6:
            issue(
                issues,
                "completion.medical_gate_count",
                "completionPolicy.medicalFallback.requiredGateCount",
                "medical readiness requires exactly six gates",
            )

    roles = board.get("roles")
    if not isinstance(roles, list) or not roles:
        issue(issues, "roles.required", "roles", "at least one role is required")
        roles = []
    role_ids: set[str] = set()
    for index, role in enumerate(roles):
        path = f"roles[{index}]"
        if not isinstance(role, dict):
            issue(issues, "role.object", path, "role must be an object")
            continue
        role_id = role.get("id")
        if not isinstance(role_id, str) or not ROLE_ID.fullmatch(role_id):
            issue(issues, "role.id", f"{path}.id", "invalid role ID")
        elif role_id in role_ids:
            issue(issues, "role.duplicate", f"{path}.id", f"duplicate role ID {role_id}")
        else:
            role_ids.add(role_id)
        if role.get("kind") not in ROLE_KINDS:
            issue(issues, "role.kind", f"{path}.kind", "invalid role kind")
        if not isinstance(role.get("filled"), bool):
            issue(issues, "role.filled", f"{path}.filled", "filled must be boolean")
        name = role.get("name")
        if role.get("filled") is True and (not isinstance(name, str) or not name.strip()):
            issue(issues, "role.name", f"{path}.name", "filled roles require a name")
        if role.get("filled") is False and name is not None:
            issue(
                issues,
                "role.unfilled_name",
                f"{path}.name",
                "unfilled roles must not fabricate a name",
            )

    packages = board.get("workPackages")
    if not isinstance(packages, list) or not packages:
        issue(
            issues,
            "work_packages.required",
            "workPackages",
            "at least one work package is required",
        )
        packages = []

    package_ids: set[str] = set()
    package_due: dict[str, datetime] = {}
    package_statuses: dict[str, str] = {}
    dependencies: dict[str, list[str]] = {}
    package_evidence_kinds: dict[str, set[str]] = {}
    gate_package: dict[str, str] = {}
    all_evidence_ids: set[str] = set()
    all_deliverable_ids: set[str] = set()
    all_acceptance_ids: set[str] = set()
    all_gate_ids: set[str] = set()

    for index, package in enumerate(packages):
        path = f"workPackages[{index}]"
        if not isinstance(package, dict):
            issue(issues, "work_package.object", path, "work package must be an object")
            continue
        required_fields = {
            "id",
            "title",
            "phase",
            "ownerRoles",
            "dueAt",
            "dependsOn",
            "status",
            "deliverables",
            "acceptanceChecks",
            "evidence",
            "gates",
        }
        for key in sorted(required_fields - package.keys()):
            issue(issues, "work_package.required", f"{path}.{key}", "required field missing")

        package_id = package.get("id")
        if not isinstance(package_id, str) or not WORK_PACKAGE_ID.fullmatch(package_id):
            issue(issues, "work_package.id", f"{path}.id", "invalid work package ID")
            package_id = f"<invalid-{index}>"
        elif package_id in package_ids:
            issue(
                issues,
                "work_package.duplicate",
                f"{path}.id",
                f"duplicate work package ID {package_id}",
            )
        else:
            package_ids.add(package_id)

        if not isinstance(package.get("title"), str) or not package.get("title"):
            issue(issues, "work_package.title", f"{path}.title", "title is required")
        if not isinstance(package.get("phase"), str) or not package.get("phase"):
            issue(issues, "work_package.phase", f"{path}.phase", "phase is required")
        if package.get("status") not in WORK_PACKAGE_STATUSES:
            issue(issues, "work_package.status", f"{path}.status", "invalid status")
        else:
            package_statuses[package_id] = package["status"]

        due = parse_timestamp(package.get("dueAt"), f"{path}.dueAt", issues)
        if due:
            package_due[package_id] = due
            if start and due < start:
                issue(
                    issues, "work_package.before_window", f"{path}.dueAt", "dueAt precedes window"
                )
            if end and due > end:
                issue(issues, "work_package.after_window", f"{path}.dueAt", "dueAt exceeds window")

        owners = package.get("ownerRoles")
        if not isinstance(owners, list) or not owners:
            issue(issues, "work_package.owners", f"{path}.ownerRoles", "owners are required")
            owners = []
        for owner in owners:
            if owner not in role_ids:
                issue(
                    issues,
                    "work_package.owner_unknown",
                    f"{path}.ownerRoles",
                    f"unknown role {owner!r}",
                )

        deps = package.get("dependsOn")
        if not isinstance(deps, list) or any(not isinstance(dep, str) for dep in deps):
            issue(
                issues,
                "work_package.dependencies",
                f"{path}.dependsOn",
                "dependsOn must be a string list",
            )
            deps = []
        if len(deps) != len(set(deps)):
            issue(
                issues,
                "work_package.dependency_duplicate",
                f"{path}.dependsOn",
                "duplicate dependency",
            )
        if package_id in deps:
            issue(
                issues,
                "work_package.self_dependency",
                f"{path}.dependsOn",
                "work package cannot depend on itself",
            )
        dependencies[package_id] = deps

        evidence_rows = package.get("evidence")
        if not isinstance(evidence_rows, list):
            issue(issues, "evidence.list", f"{path}.evidence", "evidence must be a list")
            evidence_rows = []
        local_evidence_ids: set[str] = set()
        evidence_by_id: dict[str, dict[str, Any]] = {}
        local_evidence_kinds: set[str] = set()
        for ev_index, evidence in enumerate(evidence_rows):
            ev_path = f"{path}.evidence[{ev_index}]"
            if not isinstance(evidence, dict):
                issue(issues, "evidence.object", ev_path, "evidence must be an object")
                continue
            evidence_id = evidence.get("id")
            if not isinstance(evidence_id, str) or not evidence_id:
                issue(issues, "evidence.id", f"{ev_path}.id", "evidence ID is required")
                continue
            if evidence_id in all_evidence_ids:
                issue(
                    issues,
                    "evidence.duplicate",
                    f"{ev_path}.id",
                    f"duplicate evidence ID {evidence_id}",
                )
            all_evidence_ids.add(evidence_id)
            local_evidence_ids.add(evidence_id)
            evidence_by_id[evidence_id] = evidence
            if not isinstance(evidence.get("kind"), str) or not evidence.get("kind"):
                issue(issues, "evidence.kind", f"{ev_path}.kind", "kind is required")
            else:
                local_evidence_kinds.add(evidence["kind"])
            if not safe_locator(evidence.get("locator")):
                issue(
                    issues,
                    "evidence.locator",
                    f"{ev_path}.locator",
                    "locator must be a safe repository-relative path",
                )
            if evidence.get("state") not in EVIDENCE_STATES:
                issue(issues, "evidence.state", f"{ev_path}.state", "invalid evidence state")
            evidence_hash = evidence.get("sha256")
            if evidence_hash is not None and (
                not isinstance(evidence_hash, str) or not SHA256.fullmatch(evidence_hash)
            ):
                issue(issues, "evidence.sha256", f"{ev_path}.sha256", "invalid SHA-256")
            if evidence.get("state") == "verified":
                if not isinstance(evidence_hash, str) or not SHA256.fullmatch(evidence_hash):
                    issue(
                        issues,
                        "evidence.verified_hash",
                        f"{ev_path}.sha256",
                        "verified evidence requires a SHA-256",
                    )
                parse_timestamp(
                    evidence.get("verifiedAt"),
                    f"{ev_path}.verifiedAt",
                    issues,
                    require_program_offset=False,
                )
                if evidence.get("verifiedByRole") not in role_ids:
                    issue(
                        issues,
                        "evidence.verified_by",
                        f"{ev_path}.verifiedByRole",
                        "verified evidence requires a known verifier role",
                    )
            else:
                if (
                    evidence.get("verifiedAt") is not None
                    or evidence.get("verifiedByRole") is not None
                ):
                    issue(
                        issues,
                        "evidence.false_verification",
                        ev_path,
                        "non-verified evidence cannot carry verification metadata",
                    )
            approved_by = evidence.get("approvedByRoles", [])
            if not isinstance(approved_by, list) or any(
                not isinstance(role_id, str) for role_id in approved_by
            ):
                issue(
                    issues,
                    "evidence.approved_by",
                    f"{ev_path}.approvedByRoles",
                    "approvedByRoles must be a role-ID list",
                )
                approved_by = []
            if len(approved_by) != len(set(approved_by)):
                issue(
                    issues,
                    "evidence.approver_duplicate",
                    f"{ev_path}.approvedByRoles",
                    "approvedByRoles must not contain duplicates",
                )
            for approver in approved_by:
                if approver not in role_ids:
                    issue(
                        issues,
                        "evidence.approver_unknown",
                        f"{ev_path}.approvedByRoles",
                        f"unknown approver role {approver!r}",
                    )
                    continue
                role = next((row for row in roles if row.get("id") == approver), None)
                if role and role.get("filled") is not True:
                    issue(
                        issues,
                        "evidence.approver_unfilled",
                        f"{ev_path}.approvedByRoles",
                        f"unfilled role {approver!r} cannot approve evidence",
                    )
            if approved_by and evidence.get("state") != "verified":
                issue(
                    issues,
                    "evidence.approval_without_verification",
                    f"{ev_path}.approvedByRoles",
                    "only verified evidence can carry approvals",
                )

        package_evidence_kinds[package_id] = local_evidence_kinds

        deliverables = package.get("deliverables")
        if not isinstance(deliverables, list) or not deliverables:
            issue(
                issues,
                "deliverable.required",
                f"{path}.deliverables",
                "at least one deliverable is required",
            )
            deliverables = []
        for del_index, deliverable in enumerate(deliverables):
            del_path = f"{path}.deliverables[{del_index}]"
            if not isinstance(deliverable, dict):
                issue(issues, "deliverable.object", del_path, "deliverable must be an object")
                continue
            deliverable_id = deliverable.get("id")
            if not isinstance(deliverable_id, str) or not deliverable_id:
                issue(issues, "deliverable.id", f"{del_path}.id", "deliverable ID is required")
            elif deliverable_id in all_deliverable_ids:
                issue(
                    issues,
                    "deliverable.duplicate",
                    f"{del_path}.id",
                    f"duplicate deliverable ID {deliverable_id}",
                )
            else:
                all_deliverable_ids.add(deliverable_id)
            if not safe_locator(deliverable.get("locator")):
                issue(
                    issues,
                    "deliverable.locator",
                    f"{del_path}.locator",
                    "locator must be a safe repository-relative path",
                )
            if not isinstance(deliverable.get("evidenceRequired"), bool):
                issue(
                    issues,
                    "deliverable.evidence_required",
                    f"{del_path}.evidenceRequired",
                    "evidenceRequired must be boolean",
                )
            evidence_ids = deliverable.get("evidenceIds")
            if not isinstance(evidence_ids, list):
                issue(
                    issues,
                    "deliverable.evidence_ids",
                    f"{del_path}.evidenceIds",
                    "evidenceIds must be a list",
                )
                evidence_ids = []
            for evidence_id in evidence_ids:
                if evidence_id not in local_evidence_ids:
                    issue(
                        issues,
                        "deliverable.evidence_unknown",
                        f"{del_path}.evidenceIds",
                        f"unknown local evidence ID {evidence_id!r}",
                    )
            if deliverable.get("evidenceRequired") is True and not evidence_ids:
                issue(
                    issues,
                    "deliverable.evidence_missing",
                    f"{del_path}.evidenceIds",
                    "required deliverable must name expected evidence",
                )

        checks = package.get("acceptanceChecks")
        if not isinstance(checks, list) or not checks:
            issue(
                issues,
                "acceptance.required",
                f"{path}.acceptanceChecks",
                "at least one acceptance check is required",
            )
            checks = []
        for check_index, check in enumerate(checks):
            check_path = f"{path}.acceptanceChecks[{check_index}]"
            if not isinstance(check, dict):
                issue(issues, "acceptance.object", check_path, "acceptance check must be an object")
                continue
            check_id = check.get("id")
            if not isinstance(check_id, str) or not check_id:
                issue(issues, "acceptance.id", f"{check_path}.id", "acceptance ID is required")
            elif check_id in all_acceptance_ids:
                issue(
                    issues,
                    "acceptance.duplicate",
                    f"{check_path}.id",
                    f"duplicate acceptance ID {check_id}",
                )
            else:
                all_acceptance_ids.add(check_id)
            if check.get("state") not in ACCEPTANCE_STATES:
                issue(issues, "acceptance.state", f"{check_path}.state", "invalid state")
            check_evidence = check.get("evidenceIds")
            if not isinstance(check_evidence, list):
                issue(
                    issues,
                    "acceptance.evidence_ids",
                    f"{check_path}.evidenceIds",
                    "evidenceIds must be a list",
                )
                check_evidence = []
            for evidence_id in check_evidence:
                if evidence_id not in local_evidence_ids:
                    issue(
                        issues,
                        "acceptance.evidence_unknown",
                        f"{check_path}.evidenceIds",
                        f"unknown local evidence ID {evidence_id!r}",
                    )
            if check.get("state") in {"passed", "not_applicable_approved"} and not check_evidence:
                issue(
                    issues,
                    "acceptance.unsupported",
                    check_path,
                    "passed or approved-not-applicable checks require evidence",
                )

        gates = package.get("gates")
        if not isinstance(gates, list) or not gates:
            issue(issues, "gate.required", f"{path}.gates", "at least one gate is required")
            gates = []
        for gate_index, gate in enumerate(gates):
            gate_path = f"{path}.gates[{gate_index}]"
            if not isinstance(gate, dict):
                issue(issues, "gate.object", gate_path, "gate must be an object")
                continue
            gate_id = gate.get("id")
            if not isinstance(gate_id, str) or not gate_id:
                issue(issues, "gate.id", f"{gate_path}.id", "gate ID is required")
            elif gate_id in all_gate_ids:
                issue(issues, "gate.duplicate", f"{gate_path}.id", f"duplicate gate ID {gate_id}")
            else:
                all_gate_ids.add(gate_id)
                gate_package[gate_id] = package_id
            if gate.get("kind") not in GATE_KINDS:
                issue(issues, "gate.kind", f"{gate_path}.kind", "invalid gate kind")
            if gate.get("state") not in GATE_STATES:
                issue(issues, "gate.state", f"{gate_path}.state", "invalid gate state")
            if gate.get("ownerRole") not in role_ids:
                issue(issues, "gate.owner", f"{gate_path}.ownerRole", "unknown gate owner role")
            gate_evidence = gate.get("evidenceIds")
            if not isinstance(gate_evidence, list):
                issue(
                    issues,
                    "gate.evidence_ids",
                    f"{gate_path}.evidenceIds",
                    "evidenceIds must be a list",
                )
                gate_evidence = []
            for evidence_id in gate_evidence:
                if evidence_id not in local_evidence_ids:
                    issue(
                        issues,
                        "gate.evidence_unknown",
                        f"{gate_path}.evidenceIds",
                        f"unknown local evidence ID {evidence_id!r}",
                    )
            if gate.get("state") in {"satisfied", "not_applicable_approved"} and not gate_evidence:
                issue(
                    issues,
                    "gate.unsupported",
                    gate_path,
                    "satisfied or approved-not-applicable gates require evidence",
                )
            if gate.get("state") in {"satisfied", "not_applicable_approved"}:
                owner_role = next(
                    (role for role in roles if role.get("id") == gate.get("ownerRole")),
                    None,
                )
                if owner_role and owner_role.get("filled") is not True:
                    issue(
                        issues,
                        "gate.unfilled_owner",
                        gate_path,
                        "a satisfied gate cannot be owned by an unfilled role",
                    )

        if package.get("status") in FINAL_STATUSES:
            if any(
                check.get("state") not in {"passed", "not_applicable_approved"} for check in checks
            ):
                issue(
                    issues,
                    "work_package.false_final",
                    f"{path}.status",
                    "final status requires every acceptance check to be passed or approved not applicable",
                )
            if any(
                gate.get("state") not in {"satisfied", "not_applicable_approved"} for gate in gates
            ):
                issue(
                    issues,
                    "work_package.false_final_gate",
                    f"{path}.status",
                    "final status requires every gate to be satisfied or approved not applicable",
                )
        if package.get("status") in READY_STATUSES:
            for deliverable in deliverables:
                if deliverable.get("evidenceRequired") is not True:
                    continue
                for evidence_id in deliverable.get("evidenceIds", []):
                    evidence = evidence_by_id.get(evidence_id, {})
                    if evidence.get("state") != "verified":
                        issue(
                            issues,
                            "work_package.false_ready",
                            f"{path}.status",
                            "ready or final status requires verified deliverable evidence",
                        )
                        break

    for package_id, deps in dependencies.items():
        for dependency in deps:
            if dependency not in package_ids:
                issue(
                    issues,
                    "work_package.dependency_unknown",
                    f"workPackages.{package_id}.dependsOn",
                    f"unknown dependency {dependency}",
                )
            elif package_id in package_due and dependency in package_due:
                if package_due[dependency] > package_due[package_id]:
                    issue(
                        issues,
                        "work_package.dependency_due_order",
                        f"workPackages.{package_id}.dueAt",
                        f"dependency {dependency} is due after {package_id}",
                    )
    cycle = _has_cycle(dependencies)
    if cycle:
        issue(
            issues,
            "work_package.dependency_cycle",
            "workPackages",
            "dependency cycle: " + " -> ".join(cycle),
        )

    coverage_requirements = board.get("coverageRequirements")
    if not isinstance(coverage_requirements, dict):
        issue(
            issues,
            "coverage.requirements",
            "coverageRequirements",
            "coverageRequirements must be an object",
        )
        coverage_requirements = {}
    expected_coverage = {
        "controlIds": EXPECTED_CONTROL_IDS,
        "assuranceExperimentIds": EXPECTED_ASSURANCE_EXPERIMENT_IDS,
        "canonicalExperimentIds": EXPECTED_CANONICAL_EXPERIMENT_IDS,
    }
    for field, expected_ids in expected_coverage.items():
        actual_ids = coverage_requirements.get(field)
        if not isinstance(actual_ids, list) or tuple(actual_ids) != expected_ids:
            issue(
                issues,
                "coverage.denominator",
                f"coverageRequirements.{field}",
                f"expected exact ordered denominator {list(expected_ids)!r}",
            )

    coverage_map = board.get("coverageMap")
    if not isinstance(coverage_map, dict):
        issue(issues, "coverage.map", "coverageMap", "coverageMap must be an object")
        coverage_map = {}
    coverage_sections = {
        "controls": EXPECTED_CONTROL_IDS,
        "assuranceExperiments": EXPECTED_ASSURANCE_EXPERIMENT_IDS,
        "canonicalExperiments": EXPECTED_CANONICAL_EXPERIMENT_IDS,
    }
    for section, expected_ids in coverage_sections.items():
        mapping = coverage_map.get(section)
        if not isinstance(mapping, dict):
            issue(
                issues,
                "coverage.section",
                f"coverageMap.{section}",
                "coverage section must be an object",
            )
            continue
        if set(mapping) != set(expected_ids):
            missing = sorted(set(expected_ids) - set(mapping))
            extra = sorted(set(mapping) - set(expected_ids))
            issue(
                issues,
                "coverage.exact",
                f"coverageMap.{section}",
                f"coverage keys differ; missing={missing}, extra={extra}",
            )
        for source_id, mapped_packages in mapping.items():
            source_path = f"coverageMap.{section}.{source_id}"
            if not isinstance(mapped_packages, list) or not mapped_packages:
                issue(
                    issues,
                    "coverage.unmapped",
                    source_path,
                    "every source ID must map to at least one work package",
                )
                continue
            if len(mapped_packages) != len(set(mapped_packages)):
                issue(
                    issues,
                    "coverage.duplicate_package",
                    source_path,
                    "mapped work packages must be unique",
                )
            for package_id in mapped_packages:
                if package_id not in package_ids:
                    issue(
                        issues,
                        "coverage.unknown_package",
                        source_path,
                        f"unknown mapped work package {package_id!r}",
                    )

    dependency_types = board.get("dependencyTypes")
    if not isinstance(dependency_types, dict):
        issue(
            issues,
            "dependency_types.object",
            "dependencyTypes",
            "dependencyTypes must be an object",
        )
        dependency_types = {}
    expected_edges = {
        f"{package_id}<-{dependency}"
        for package_id, package_dependencies in dependencies.items()
        for dependency in package_dependencies
    }
    if set(dependency_types) != expected_edges:
        missing = sorted(expected_edges - set(dependency_types))
        extra = sorted(set(dependency_types) - expected_edges)
        issue(
            issues,
            "dependency_types.exact",
            "dependencyTypes",
            f"dependency bindings differ; missing={missing}, extra={extra}",
        )
    for edge, dependency_type in dependency_types.items():
        if dependency_type not in DEPENDENCY_TYPES:
            issue(
                issues,
                "dependency_types.value",
                f"dependencyTypes.{edge}",
                f"invalid dependency type {dependency_type!r}",
            )

    gate_bindings = board.get("gateEvidenceBindings")
    if not isinstance(gate_bindings, dict):
        issue(
            issues,
            "gate_binding.object",
            "gateEvidenceBindings",
            "gateEvidenceBindings must be an object",
        )
        gate_bindings = {}
    if set(gate_bindings) != all_gate_ids:
        missing = sorted(all_gate_ids - set(gate_bindings))
        extra = sorted(set(gate_bindings) - all_gate_ids)
        issue(
            issues,
            "gate_binding.exact",
            "gateEvidenceBindings",
            f"gate bindings differ; missing={missing}, extra={extra}",
        )
    for gate_id, binding in gate_bindings.items():
        binding_path = f"gateEvidenceBindings.{gate_id}"
        if not isinstance(binding, dict):
            issue(issues, "gate_binding.value", binding_path, "binding must be an object")
            continue
        required_kinds = binding.get("requiredEvidenceKinds")
        required_approvers = binding.get("requiredApproverRoles")
        if not isinstance(required_kinds, list) or not required_kinds:
            issue(
                issues,
                "gate_binding.evidence_kinds",
                f"{binding_path}.requiredEvidenceKinds",
                "at least one required evidence kind is required",
            )
            required_kinds = []
        if len(required_kinds) != len(set(required_kinds)):
            issue(
                issues,
                "gate_binding.evidence_duplicate",
                f"{binding_path}.requiredEvidenceKinds",
                "required evidence kinds must be unique",
            )
        package_id = gate_package.get(gate_id)
        available_kinds = package_evidence_kinds.get(package_id or "", set())
        for evidence_kind in required_kinds:
            if evidence_kind not in available_kinds:
                issue(
                    issues,
                    "gate_binding.evidence_unavailable",
                    f"{binding_path}.requiredEvidenceKinds",
                    f"evidence kind {evidence_kind!r} is unavailable in {package_id}",
                )
        if not isinstance(required_approvers, list) or not required_approvers:
            issue(
                issues,
                "gate_binding.approvers",
                f"{binding_path}.requiredApproverRoles",
                "at least one required approver role is required",
            )
            required_approvers = []
        if len(required_approvers) != len(set(required_approvers)):
            issue(
                issues,
                "gate_binding.approver_duplicate",
                f"{binding_path}.requiredApproverRoles",
                "required approver roles must be unique",
            )
        for approver in required_approvers:
            if approver not in role_ids:
                issue(
                    issues,
                    "gate_binding.approver_unknown",
                    f"{binding_path}.requiredApproverRoles",
                    f"unknown approver role {approver!r}",
                )

    modes = board.get("modeRequirements")
    if not isinstance(modes, dict):
        issue(
            issues,
            "mode_requirements.object",
            "modeRequirements",
            "modeRequirements must be an object",
        )
        modes = {}
    readiness_ids = modes.get("readinessWorkPackageIds")
    closure_ids = modes.get("closureWorkPackageIds")
    evidence_kinds = modes.get("requiredClosureEvidenceKinds")
    if not isinstance(readiness_ids, list) or not readiness_ids:
        issue(
            issues,
            "mode_requirements.readiness",
            "modeRequirements.readinessWorkPackageIds",
            "readiness package IDs are required",
        )
        readiness_ids = []
    if not isinstance(closure_ids, list) or not closure_ids:
        issue(
            issues,
            "mode_requirements.closure",
            "modeRequirements.closureWorkPackageIds",
            "closure package IDs are required",
        )
        closure_ids = []
    for mode_name, ids in (("readiness", readiness_ids), ("closure", closure_ids)):
        if len(ids) != len(set(ids)):
            issue(
                issues,
                "mode_requirements.duplicate",
                f"modeRequirements.{mode_name}WorkPackageIds",
                "work package IDs must be unique",
            )
        for package_id in ids:
            if package_id not in package_ids:
                issue(
                    issues,
                    "mode_requirements.unknown",
                    f"modeRequirements.{mode_name}WorkPackageIds",
                    f"unknown work package {package_id!r}",
                )
    if set(closure_ids) != package_ids:
        issue(
            issues,
            "mode_requirements.denominator",
            "modeRequirements.closureWorkPackageIds",
            "closure denominator must contain every current work package exactly once",
        )
    if not isinstance(evidence_kinds, list) or not evidence_kinds:
        issue(
            issues,
            "mode_requirements.evidence_kinds",
            "modeRequirements.requiredClosureEvidenceKinds",
            "required closure evidence kinds are missing",
        )

    return issues


def _packages_by_id(board: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        package["id"]: package
        for package in board.get("workPackages", [])
        if isinstance(package, dict) and isinstance(package.get("id"), str)
    }


def _verified_evidence_issue(evidence: dict[str, Any], root: Path, path: str) -> Issue | None:
    if evidence.get("state") != "verified":
        return Issue("evidence.not_verified", path, "evidence is not verified")
    locator = evidence.get("locator")
    if not safe_locator(locator):
        return Issue("evidence.locator", path, "evidence locator is invalid")
    evidence_path = root / locator
    if not evidence_path.is_file():
        return Issue("evidence.file_missing", path, f"evidence file is missing: {locator}")
    expected = evidence.get("sha256")
    if not isinstance(expected, str) or not SHA256.fullmatch(expected):
        return Issue("evidence.hash_missing", path, "verified evidence has no valid SHA-256")
    actual = sha256(evidence_path)
    if actual != expected:
        return Issue(
            "evidence.hash_mismatch",
            path,
            f"expected {expected}, found {actual}",
        )
    if not evidence.get("verifiedAt") or not evidence.get("verifiedByRole"):
        return Issue(
            "evidence.verification_metadata",
            path,
            "verified evidence requires verifiedAt and verifiedByRole",
        )
    return None


def _referenced_evidence_ids(package: dict[str, Any]) -> set[str]:
    referenced: set[str] = set()
    for collection in ("deliverables", "acceptanceChecks", "gates"):
        for row in package.get(collection, []):
            if not isinstance(row, dict):
                continue
            referenced.update(
                evidence_id
                for evidence_id in row.get("evidenceIds", [])
                if isinstance(evidence_id, str)
            )
    return referenced


def _verified_referenced_evidence(package: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    package_id = package.get("id", "<unknown>")
    referenced = _referenced_evidence_ids(package)
    verified: list[dict[str, Any]] = []
    for evidence in package.get("evidence", []):
        if not isinstance(evidence, dict) or evidence.get("id") not in referenced:
            continue
        evidence_id = evidence.get("id", "<unknown>")
        if (
            _verified_evidence_issue(
                evidence,
                root,
                f"workPackages.{package_id}.evidence.{evidence_id}",
            )
            is None
        ):
            verified.append(evidence)
    return verified


def _has_explicit_blocked_outcome(package: dict[str, Any], root: Path) -> bool:
    if package.get("status") != "blocked":
        return False
    failed_evidence_ids: set[str] = set()
    for collection in ("acceptanceChecks", "gates"):
        for row in package.get(collection, []):
            if isinstance(row, dict) and row.get("state") == "failed":
                failed_evidence_ids.update(
                    evidence_id
                    for evidence_id in row.get("evidenceIds", [])
                    if isinstance(evidence_id, str)
                )
    return any(
        evidence.get("id") in failed_evidence_ids
        for evidence in _verified_referenced_evidence(package, root)
    )


def _validate_package_dependencies(
    package: dict[str, Any],
    board: dict[str, Any],
    root: Path,
    *,
    require_final: bool,
) -> list[Issue]:
    issues: list[Issue] = []
    packages = _packages_by_id(board)
    dependency_types = board.get("dependencyTypes", {})
    package_id = package.get("id", "<unknown>")
    for dependency_id in package.get("dependsOn", []):
        dependency = packages.get(dependency_id)
        if dependency is None:
            continue
        path = f"workPackages.{package_id}.dependsOn.{dependency_id}"
        dependency_status = dependency.get("status")
        if require_final:
            if dependency_status not in FINAL_STATUSES:
                issue(
                    issues,
                    "dependency.not_final",
                    path,
                    f"closure requires dependency {dependency_id} to be final; found {dependency_status!r}",
                )
            continue

        dependency_type = dependency_types.get(f"{package_id}<-{dependency_id}")
        if dependency_type == "hard":
            if dependency_status not in READY_STATUSES:
                issue(
                    issues,
                    "dependency.hard_not_ready",
                    path,
                    f"hard dependency {dependency_id} is not evidence-ready; found {dependency_status!r}",
                )
        elif dependency_type == "conditional":
            if dependency_status not in READY_STATUSES and not _has_explicit_blocked_outcome(
                dependency, root
            ):
                issue(
                    issues,
                    "dependency.conditional_unresolved",
                    path,
                    f"conditional dependency {dependency_id} has neither a ready result nor an evidenced blocked outcome",
                )
        elif dependency_type == "status_snapshot":
            if dependency_status not in READY_STATUSES and not _verified_referenced_evidence(
                dependency, root
            ):
                issue(
                    issues,
                    "dependency.snapshot_missing",
                    path,
                    f"status-snapshot dependency {dependency_id} has no verified referenced status evidence",
                )
    return issues


def _validate_package_gate(
    package: dict[str, Any],
    board: dict[str, Any],
    root: Path,
    *,
    require_final: bool,
) -> list[Issue]:
    issues: list[Issue] = []
    package_id = package.get("id", "<unknown>")
    path = f"workPackages.{package_id}"
    status = package.get("status")
    if require_final:
        if status not in FINAL_STATUSES:
            issue(
                issues,
                "closure.status",
                f"{path}.status",
                f"closure requires an approved final status, found {status!r}",
            )
    elif status not in READY_STATUSES:
        issue(
            issues,
            "readiness.status",
            f"{path}.status",
            f"readiness requires an evidence-ready or final status, found {status!r}",
        )

    evidence_by_id = {
        row.get("id"): row
        for row in package.get("evidence", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    verified_cache: dict[str, Issue | None] = {}

    def require_evidence(evidence_id: str, evidence_path: str) -> dict[str, Any] | None:
        evidence = evidence_by_id.get(evidence_id)
        if evidence is None:
            issue(
                issues,
                "evidence.reference_missing",
                evidence_path,
                f"evidence ID {evidence_id!r} is missing",
            )
            return None
        if evidence_id not in verified_cache:
            verified_cache[evidence_id] = _verified_evidence_issue(
                evidence, root, f"{path}.evidence.{evidence_id}"
            )
        evidence_issue = verified_cache[evidence_id]
        if evidence_issue and evidence_issue not in issues:
            issues.append(evidence_issue)
        if evidence_issue:
            return None
        return evidence

    disposition_only = status in {"superseded_approved", "not_applicable_approved"}
    if not disposition_only:
        for deliverable in package.get("deliverables", []):
            if deliverable.get("evidenceRequired") is not True:
                continue
            evidence_ids = deliverable.get("evidenceIds", [])
            if not evidence_ids:
                issue(
                    issues,
                    "deliverable.no_evidence",
                    f"{path}.deliverables.{deliverable.get('id')}",
                    "required deliverable has no evidence IDs",
                )
            for evidence_id in evidence_ids:
                require_evidence(
                    evidence_id,
                    f"{path}.deliverables.{deliverable.get('id')}.evidenceIds",
                )

    for check in package.get("acceptanceChecks", []):
        check_state = check.get("state")
        if check_state not in {"passed", "not_applicable_approved"}:
            issue(
                issues,
                "acceptance.pending",
                f"{path}.acceptanceChecks.{check.get('id')}",
                f"acceptance is not closed: {check_state!r}",
            )
        verified_rows = []
        for evidence_id in check.get("evidenceIds", []):
            evidence = require_evidence(
                evidence_id,
                f"{path}.acceptanceChecks.{check.get('id')}.evidenceIds",
            )
            if evidence is not None:
                verified_rows.append(evidence)
        if check_state in {"passed", "not_applicable_approved"}:
            owner_roles = set(package.get("ownerRoles", []))
            approver_roles = {
                approver
                for evidence in verified_rows
                for approver in evidence.get("approvedByRoles", [])
            }
            if not owner_roles.intersection(approver_roles):
                issue(
                    issues,
                    "acceptance.approver_missing",
                    f"{path}.acceptanceChecks.{check.get('id')}.evidenceIds",
                    "closed acceptance requires verified evidence approved by at least one accountable package owner",
                )
            if check_state == "not_applicable_approved" and not any(
                evidence.get("kind") == "approved_disposition" for evidence in verified_rows
            ):
                issue(
                    issues,
                    "acceptance.disposition_evidence",
                    f"{path}.acceptanceChecks.{check.get('id')}.evidenceIds",
                    "approved-not-applicable acceptance requires approved_disposition evidence",
                )

    for gate in package.get("gates", []):
        gate_state = gate.get("state")
        if gate_state not in {"satisfied", "not_applicable_approved"}:
            issue(
                issues,
                f"{gate.get('kind', 'unknown')}_gate.pending",
                f"{path}.gates.{gate.get('id')}",
                f"gate is not closed: {gate_state!r}",
            )
        verified_rows = []
        for evidence_id in gate.get("evidenceIds", []):
            evidence = require_evidence(
                evidence_id,
                f"{path}.gates.{gate.get('id')}.evidenceIds",
            )
            if evidence is not None:
                verified_rows.append(evidence)
        if gate_state in {"satisfied", "not_applicable_approved"}:
            gate_id = gate.get("id")
            binding = board.get("gateEvidenceBindings", {}).get(gate_id, {})
            required_kinds = (
                {"approved_disposition"}
                if gate_state == "not_applicable_approved"
                else set(binding.get("requiredEvidenceKinds", []))
            )
            verified_kinds = {evidence.get("kind") for evidence in verified_rows}
            for missing_kind in sorted(required_kinds - verified_kinds):
                issue(
                    issues,
                    "gate.evidence_kind_missing",
                    f"{path}.gates.{gate_id}.evidenceIds",
                    f"closed gate lacks verified referenced evidence kind {missing_kind!r}",
                )
            required_approvers = set(binding.get("requiredApproverRoles", []))
            evidence_approvers = {
                approver
                for evidence in verified_rows
                for approver in evidence.get("approvedByRoles", [])
            }
            for missing_approver in sorted(required_approvers - evidence_approvers):
                issue(
                    issues,
                    "gate.approver_missing",
                    f"{path}.gates.{gate_id}.evidenceIds",
                    f"closed gate lacks verified evidence approved by {missing_approver}",
                )

    return issues


def validate_readiness(
    board: dict[str, Any], root: Path, as_of: datetime | None = None
) -> list[Issue]:
    issues: list[Issue] = []
    packages = _packages_by_id(board)
    readiness_ids = board.get("modeRequirements", {}).get("readinessWorkPackageIds", [])
    for package_id in readiness_ids:
        package = packages.get(package_id)
        if package:
            issues.extend(_validate_package_gate(package, board, root, require_final=False))
            issues.extend(_validate_package_dependencies(package, board, root, require_final=False))

    if as_of is not None:
        for package_id, package in packages.items():
            due_issues: list[Issue] = []
            due = parse_timestamp(
                package.get("dueAt"),
                f"workPackages.{package_id}.dueAt",
                due_issues,
                require_program_offset=False,
            )
            if due and due <= as_of and package.get("status") in BLOCKING_STATUSES:
                issue(
                    issues,
                    "schedule.overdue",
                    f"workPackages.{package_id}.status",
                    f"work package was due at {package.get('dueAt')} and remains {package.get('status')}",
                )
    return issues


def validate_closure(board: dict[str, Any], root: Path) -> list[Issue]:
    issues: list[Issue] = []
    packages = _packages_by_id(board)
    closure_ids = board.get("modeRequirements", {}).get("closureWorkPackageIds", [])
    for package_id in closure_ids:
        package = packages.get(package_id)
        if package:
            issues.extend(_validate_package_gate(package, board, root, require_final=True))
            issues.extend(_validate_package_dependencies(package, board, root, require_final=True))

    verified_kinds = {
        evidence.get("kind")
        for package in packages.values()
        for evidence in _verified_referenced_evidence(package, root)
    }
    required_kinds = set(board.get("modeRequirements", {}).get("requiredClosureEvidenceKinds", []))
    for missing_kind in sorted(required_kinds - verified_kinds):
        issue(
            issues,
            "closure.evidence_kind",
            "modeRequirements.requiredClosureEvidenceKinds",
            f"no verified closure evidence exists for kind {missing_kind!r}",
        )
    return issues


def validate(
    board: dict[str, Any], mode: str, root: Path = ROOT, as_of: datetime | None = None
) -> list[Issue]:
    issues = validate_structure(board)
    if issues or mode == "structure":
        return issues
    if mode == "readiness":
        return issues + validate_readiness(board, root, as_of=as_of)
    if mode == "closure":
        return issues + validate_readiness(board, root, as_of=as_of) + validate_closure(board, root)
    raise ValueError(f"unknown mode: {mode}")


def report_payload(
    board_path: Path,
    board: dict[str, Any],
    mode: str,
    issues: list[Issue],
    as_of: datetime | None,
) -> dict[str, Any]:
    packages = board.get("workPackages", [])
    statuses: dict[str, int] = {}
    for package in packages:
        if not isinstance(package, dict):
            continue
        status = str(package.get("status", "<missing>"))
        statuses[status] = statuses.get(status, 0) + 1
    return {
        "schemaVersion": "VegoExecutionControlValidation-v1",
        "board": str(board_path),
        "programId": board.get("programId"),
        "mode": mode,
        "asOf": as_of.isoformat() if as_of else None,
        "passed": not issues,
        "workPackageCount": len(packages),
        "statusCounts": statuses,
        "issueCount": len(issues),
        "issues": [asdict(item) for item in issues],
        "evidenceBoundary": (
            "A passing structure result proves control-board conformance only. "
            "Readiness and closure require real, hash-verified human and external evidence."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, default=DEFAULT_BOARD)
    parser.add_argument("--mode", choices=MODES, default="structure")
    parser.add_argument(
        "--as-of",
        help="Optional aware ISO-8601 time for overdue checks; omitted means no overdue check.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        board = load_board(args.board)
        as_of_issues: list[Issue] = []
        as_of = (
            parse_timestamp(
                args.as_of,
                "--as-of",
                as_of_issues,
                require_program_offset=False,
            )
            if args.as_of
            else None
        )
        issues = as_of_issues or validate(board, args.mode, root=ROOT, as_of=as_of)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        payload = {
            "schemaVersion": "VegoExecutionControlValidation-v1",
            "board": str(args.board),
            "mode": args.mode,
            "passed": False,
            "issueCount": 1,
            "issues": [
                {
                    "code": "board.load_error",
                    "path": str(args.board),
                    "message": str(exc),
                }
            ],
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"FAIL [{args.mode}] {args.board}: {exc}")
        return 2

    payload = report_payload(args.board, board, args.mode, issues, as_of)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        verdict = "PASS" if not issues else "FAIL"
        print(
            f"{verdict} [{args.mode}] {payload['programId']} "
            f"({payload['workPackageCount']} work packages, {len(issues)} issues)"
        )
        for item in issues:
            print(f"- {item.code} @ {item.path}: {item.message}")
        print(payload["evidenceBoundary"])
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
