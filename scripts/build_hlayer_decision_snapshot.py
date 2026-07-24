#!/usr/bin/env python3
"""Build a deterministic H-layer decision and implementation-gate snapshot.

The supervisor register is the source of truth.  This script never edits it and
never interprets silence, placeholders, or free-form text as approval.  A live
shadow listener requires all of the following:

* an accepted M-05 outcome;
* an explicit approval of the allowed-touch list; and
* a separate explicit implementation authorization.

The latter two approvals must be supplied in a JSON authorization record.  In
its absence, the snapshot is intentionally ``offline_only``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

DECISION_IDS = tuple(f"M-{number:02d}" for number in range(1, 7))
ACCEPTED_OUTCOMES = {"Accepted", "Accepted with changes"}
RECORDED_OUTCOMES = ACCEPTED_OUTCOMES | {"Rejected", "Deferred"}
PLACEHOLDER_OUTCOMES = {"", "not yet recorded", "not recorded", "pending", "tbd"}
PLACEHOLDER_VALUE_PREFIXES = (
    "to be recorded",
    "not yet recorded",
    "not recorded",
    "pending",
    "tbd",
)
EXPECTED_TOUCHES = (
    "VEGO-AI/framework/orchestrator.py",
    "VEGO-AI/framework/qa_registry.py",
    "VEGO-AI/framework/h_layer_shadow_writer.py",
    "VEGO-AI/schemas/observation_record.schema.json",
    "VEGO-AI/tests/test_h_layer_shadow_writer.py",
)
REPO_ROOT = Path(__file__).resolve().parents[1]


class SnapshotError(RuntimeError):
    """Raised when a source file cannot be parsed safely."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def strip_markdown(value: str) -> str:
    value = value.strip()
    if value.endswith("."):
        value = value[:-1].rstrip()
    if len(value) >= 2 and value[0] == value[-1] == "`":
        value = value[1:-1]
    return value.strip()


def normalize_outcome(raw: str) -> tuple[str, str]:
    cleaned = strip_markdown(raw)
    lowered = cleaned.casefold()
    if lowered in PLACEHOLDER_OUTCOMES:
        return "Deferred", "placeholder_or_blank"
    for outcome in RECORDED_OUTCOMES:
        if lowered == outcome.casefold():
            return outcome, "explicit"
    return "Deferred", "ambiguous_unrecognized"


def has_recorded_value(raw: str) -> bool:
    cleaned = strip_markdown(raw)
    return bool(cleaned) and not cleaned.casefold().startswith(PLACEHOLDER_VALUE_PREFIXES)


def parse_register(text: str) -> dict[str, dict[str, str]]:
    headings = list(re.finditer(r"^##\s+(M-0[1-6])\s+-\s+(.+?)\s*$", text, re.MULTILINE))
    found: dict[str, dict[str, str]] = {}
    for index, match in enumerate(headings):
        decision_id = match.group(1)
        start = match.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        fields: dict[str, str] = {"title": match.group(2).strip()}
        for line in text[start:end].splitlines():
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            field = cells[0]
            value = "|".join(cells[1:]).strip()
            if field.casefold() in {"field", "---"} or set(field) == {"-"}:
                continue
            fields[field.casefold()] = value
        found[decision_id] = fields

    missing = [decision_id for decision_id in DECISION_IDS if decision_id not in found]
    if missing:
        raise SnapshotError(f"decision register is missing: {', '.join(missing)}")
    extras = sorted(set(found) - set(DECISION_IDS))
    if extras:
        raise SnapshotError(f"decision register has unexpected IDs: {', '.join(extras)}")
    return found


def read_authorization(path: Path | None) -> tuple[dict[str, Any] | None, list[str]]:
    reasons: list[str] = []
    if path is None:
        return None, ["separate implementation authorization record is absent"]
    if not path.is_file():
        return None, [f"authorization record does not exist: {path}"]
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"authorization record is unreadable: {exc}"]
    if not isinstance(record, dict):
        return None, ["authorization record must be a JSON object"]

    required_scalars = ("authorization_id", "approved_at", "approver")
    for key in required_scalars:
        if not isinstance(record.get(key), str) or not record[key].strip():
            reasons.append(f"authorization record is missing nonblank {key}")
    if record.get("scope") != "h_layer_shadow_listener":
        reasons.append("authorization scope is not h_layer_shadow_listener")
    if record.get("allowed_touch_outcome") not in sorted(ACCEPTED_OUTCOMES):
        reasons.append("allowed-touch list is not explicitly accepted")
    if record.get("implementation_outcome") not in sorted(ACCEPTED_OUTCOMES):
        reasons.append("implementation is not separately and explicitly accepted")
    touches = record.get("allowed_touches")
    if not isinstance(touches, list) or not all(isinstance(item, str) for item in touches):
        reasons.append("allowed_touches must be a list of repository-relative paths")
    elif len(touches) != len(EXPECTED_TOUCHES) or set(touches) != set(EXPECTED_TOUCHES):
        reasons.append("allowed_touches does not exactly match the phase-one proposal")
    return record, reasons


def build_snapshot(register_path: Path, authorization_path: Path | None = None) -> dict[str, Any]:
    source_bytes = register_path.read_bytes()
    source_text = source_bytes.decode("utf-8-sig")
    parsed = parse_register(source_text)

    decisions: list[dict[str, Any]] = []
    for decision_id in DECISION_IDS:
        fields = parsed[decision_id]
        raw_outcome = fields.get("outcome", "")
        effective_outcome, interpretation = normalize_outcome(raw_outcome)
        rationale = strip_markdown(fields.get("rationale", ""))
        approver = strip_markdown(fields.get("approver", ""))
        selected_value = strip_markdown(fields.get("selected value", ""))
        decision_date = strip_markdown(fields.get("decision date", ""))
        decision_complete = (
            interpretation == "explicit"
            and has_recorded_value(rationale)
            and has_recorded_value(approver)
            and has_recorded_value(selected_value)
            and has_recorded_value(decision_date)
        )
        decisions.append(
            {
                "id": decision_id,
                "title": fields.get("title", ""),
                "raw_outcome": strip_markdown(raw_outcome),
                "effective_outcome": effective_outcome,
                "outcome_interpretation": interpretation,
                "accepted": effective_outcome in ACCEPTED_OUTCOMES and interpretation == "explicit",
                "decision_complete": decision_complete,
                "selected_value": selected_value if decision_complete else None,
                "decision_date": decision_date if decision_complete else None,
                "rationale": rationale,
                "approver": approver,
                "due_date": strip_markdown(fields.get("due date", "")),
                "confirmation_status": strip_markdown(fields.get("confirmation status", "")),
                "exact_decision_requested": strip_markdown(
                    fields.get("exact decision requested", "")
                ),
            }
        )

    authorization, authorization_reasons = read_authorization(authorization_path)
    by_id = {item["id"]: item for item in decisions}
    m05 = by_id["M-05"]
    blockers: list[str] = []
    for decision_id in ("M-02", "M-03", "M-04", "M-05"):
        if not by_id[decision_id]["decision_complete"]:
            blockers.append(
                f"{decision_id} lacks a complete outcome, selected value, rationale, approver, or decision date"
            )
    if not m05["accepted"]:
        blockers.append("M-05 is not explicitly accepted")
    blockers.extend(authorization_reasons)
    live_authorized = not blockers
    decision_set_complete = all(
        by_id[decision_id]["decision_complete"] for decision_id in ("M-02", "M-03", "M-04", "M-05")
    )

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "source_register": display_path(register_path),
        "source_register_sha256": sha256_bytes(source_bytes),
        "decision_ids": list(DECISION_IDS),
        "decisions": decisions,
        "program_mode": "live_shadow_authorized" if live_authorized else "offline_only",
        "snapshot_status": "complete" if decision_set_complete else "deferred",
        "offline_only": not live_authorized,
        "live_shadow_authorized": live_authorized,
        "authorization_blockers": blockers,
        "implementation_gate": {
            "offline_only": not live_authorized,
            "allowed_touch_and_separate_authorization_required": True,
        },
        "authorization_record": (
            {
                "path": display_path(authorization_path),
                "sha256": sha256_bytes(authorization_path.read_bytes()),
                "authorization_id": authorization.get("authorization_id"),
                "approved_at": authorization.get("approved_at"),
                "approver": authorization.get("approver"),
                "scope": authorization.get("scope"),
                "allowed_touch_outcome": authorization.get("allowed_touch_outcome"),
                "implementation_outcome": authorization.get("implementation_outcome"),
                "allowed_touches": authorization.get("allowed_touches"),
            }
            if authorization is not None and authorization_path is not None
            else None
        ),
        "safety_policy": {
            "blank_or_ambiguous_outcome": "Deferred",
            "unaccepted_values": "comparison_parameters_only",
            "timeout": "preserve_baseline_and_park",
            "correction": "proposal_only_with_explicit_human_approval",
            "trusted_memory": "verified_or_supervisor_adjudicated_only",
        },
    }
    payload["snapshot_sha256"] = sha256_bytes(canonical_json_bytes(payload))
    return payload


def write_if_changed(path: Path, payload: dict[str, Any]) -> bool:
    encoded = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path.is_file() and path.read_text(encoding="utf-8") == encoded:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(encoded, encoding="utf-8", newline="\n")
    return True


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--register",
        type=Path,
        default=Path("docs/research/meetings/2026-07-15-supervisor-decision-register.md"),
        help="Markdown supervisor decision register",
    )
    parser.add_argument(
        "--authorization",
        type=Path,
        help="Optional separate JSON approval record for the allowed-touch list and implementation",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/generated/h_layer_decisions/decision_snapshot.json"),
        help="Deterministic JSON snapshot destination",
    )
    parser.add_argument(
        "--check", action="store_true", help="Fail if the output is absent or stale; do not write"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        snapshot = build_snapshot(args.register, args.authorization)
    except (OSError, UnicodeError, SnapshotError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    expected = json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file():
            print(f"STALE: missing decision snapshot: {args.output}", file=sys.stderr)
            return 1
        if args.output.read_text(encoding="utf-8") != expected:
            print(f"STALE: decision snapshot does not match {args.register}", file=sys.stderr)
            return 1
        print(f"OK: {args.output} matches the register ({snapshot['program_mode']})")
        return 0

    changed = write_if_changed(args.output, snapshot)
    action = "wrote" if changed else "unchanged"
    print(f"{action}: {args.output}")
    print(f"snapshot_sha256: {snapshot['snapshot_sha256']}")
    print(f"program_mode: {snapshot['program_mode']}")
    for blocker in snapshot["authorization_blockers"]:
        print(f"blocker: {blocker}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
