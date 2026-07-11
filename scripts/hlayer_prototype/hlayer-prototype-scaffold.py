#!/usr/bin/env python3
"""Offline H-layer interactive demonstration shell.

The shell replays existing EXP-006 observations and demonstrates deterministic
review checks.  It is not a runtime listener, an approved feedback-memory
writer, or an empirical evaluation.

Usage:
  python scripts/hlayer_prototype/hlayer-prototype-scaffold.py --dry-run
  python scripts/hlayer_prototype/hlayer-prototype-scaffold.py --test-conflict
  python scripts/hlayer_prototype/hlayer-prototype-scaffold.py \
      --mock-session --output-dir <temp-dir>
  python scripts/hlayer_prototype/hlayer-prototype-scaffold.py --interactive
"""
from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EVAL = REPO / "VEGO-AI" / "eval_output"
DEFAULT_OUTPUT_DIR = REPO / "reports" / "generated" / "hlayer_demo"
FEEDBACK_FILENAME = "feedback_records.json"
ADJUDICATION_FILENAME = "adjudication_candidates.json"

OFFLINE_DEMO_ORIGIN = "OFFLINE_REPLAY_DEMO"
SYNTHETIC_ORIGIN = "SYNTHETIC_NOT_HUMAN"
SEMANTIC_CHECKER_ENABLED = False

CLAIM = (
    "Offline design/mechanism demonstration only. No accuracy, generalization, "
    "or clinical claims. EXP-005 remains the accuracy gate."
)

SETTINGS = ["cd_ch", "cd_pw", "ucd_ch", "ucd_pw"]
DECISIONS = {"approve": "Approve", "reject": "Reject"}
YES_NO = {"y": "yes", "yes": "yes", "n": "no", "no": "no"}


def validate_output_dir(path: Path) -> Path:
    """Resolve the demo output and reject protected repository subtrees."""
    candidate = path.expanduser().resolve()
    forbidden_roots = [(REPO / ".git").resolve(), (REPO / "VEGO-AI").resolve()]
    for forbidden_root in forbidden_roots:
        if candidate == forbidden_root or forbidden_root in candidate.parents:
            raise ValueError(
                f"Demo output directory cannot be inside protected path: {forbidden_root}"
            )
    return candidate


def load_real_events() -> list[dict]:
    """Load offline-replay observations from the current EXP-006 output."""
    events_path = REPO / "reports" / "generated" / "exp006" / "events.csv"
    if not events_path.exists():
        return []

    events = []
    with events_path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for idx, row in enumerate(reader):
            detail = row.get("detail") or ""
            match = re.match(r"^(\d+)", detail)
            events.append(
                {
                    "event_id": row.get("event_id") or f"EV_{idx:03d}",
                    "setting": row.get("setting"),
                    "event": row.get("event"),
                    "stage": row.get("stage"),
                    "severity": int(row.get("severity") or 0),
                    "detail": detail,
                    "case_id": match.group(1) if match else None,
                    "capture_status": row.get("capture_status") or "unknown",
                    "source_artifact": row.get("source_artifact") or "",
                    "source_sha256": row.get("source_sha256") or "",
                }
            )
    return events


def bundle_key_of(event_record: dict) -> str:
    """Return the subject-level bundling key used by the offline demo."""
    event = event_record["event"]
    detail = event_record.get("detail", "")

    if event in {"E5_compliance_vector", "E6_inspector_uncertainty", "E5_compliance_eval"}:
        match = re.match(r"^(\d+)", detail)
        if match:
            return f"case_{match.group(1)}"
    if event in {"E8_classification", "E13_agent4_signals"}:
        match = re.match(r"^([\w\-]+)", detail)
        if match:
            return f"pattern_{match.group(1)}"
    if event == "E12_low_certainty_guideline":
        match = re.match(r"^([Gg]\d+)", detail)
        if match:
            return f"guideline_{match.group(1)}"
    if event in {"E2_question_from_B", "E2_question_from_D"}:
        match = re.match(r"^([Qq]_[a-zA-Z0-9_]+)", detail)
        if match:
            return f"question_{match.group(1)}"
    if event in {"E1_template_created", "E1_template_revised"}:
        return "template_advisor"
    if event in {"E4_guidelines_created", "E4_guidelines_refined"}:
        return "domain_guidelines"
    return detail or "unclassified_subject"


class DemoOutputStore:
    """Append-only, demo-only records kept separate from trusted memory."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.feedback_file = output_dir / FEEDBACK_FILENAME
        self.adjudication_file = output_dir / ADJUDICATION_FILENAME

    @staticmethod
    def _assert_safe_existing_file(path: Path) -> None:
        if path.is_symlink():
            raise RuntimeError(f"Refusing linked demo output file: {path}")
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            return
        reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        file_attributes = getattr(metadata, "st_file_attributes", 0)
        if reparse_flag and file_attributes & reparse_flag:
            raise RuntimeError(f"Refusing reparse-point demo output file: {path}")
        if not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError(f"Refusing non-regular demo output file: {path}")
        if metadata.st_nlink != 1:
            raise RuntimeError(f"Refusing multi-link demo output file: {path}")

    @staticmethod
    def _load_records(path: Path) -> list[dict]:
        DemoOutputStore._assert_safe_existing_file(path)
        if not path.exists():
            return []
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"Refusing to overwrite unreadable demo data at {path}: {exc}"
            ) from exc
        if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
            raise RuntimeError(f"Refusing to overwrite non-list demo data at {path}")
        return value

    @staticmethod
    def _write_record(path: Path, record: dict) -> None:
        records = DemoOutputStore._load_records(path)
        if not any(item.get("record_id") == record["record_id"] for item in records):
            records.append(record)
        path.parent.mkdir(parents=True, exist_ok=True)
        serialized = (json.dumps(records, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=f".{path.name}.",
                suffix=".tmp",
                dir=path.parent,
                delete=False,
            ) as handle:
                handle.write(serialized)
                handle.flush()
                os.fsync(handle.fileno())
                temporary = Path(handle.name)
            DemoOutputStore._assert_safe_existing_file(path)
            os.replace(temporary, path)
            temporary = None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def feedback_records(self) -> list[dict]:
        return self._load_records(self.feedback_file)

    def save_feedback_record(self, record: dict) -> None:
        if record.get("state") == "needs_adjudication" or record.get("override_requested"):
            raise ValueError("Unadjudicated overrides cannot enter ordinary demo feedback records")
        self._write_record(self.feedback_file, record)

    def save_adjudication_candidate(self, record: dict) -> None:
        if record.get("state") != "needs_adjudication":
            raise ValueError("Adjudication candidates must use the needs_adjudication state")
        self._write_record(self.adjudication_file, record)


class VerificationEngine:
    """Deterministic-only checks for the offline demonstration."""

    def __init__(self, setting: str, output_store: DemoOutputStore):
        self.setting = setting
        self.output_store = output_store
        self.provisional_low_certainty_guidelines: set[str] = set()
        self.load_reference_sources()

    def load_reference_sources(self) -> None:
        """Load guideline metadata used by the provisional demo heuristic."""
        setting_dir = EVAL / self.setting
        if not setting_dir.exists():
            return

        guideline_paths = sorted(glob.glob(str(setting_dir / "agentB_best_guidelines*.json")))
        if not guideline_paths:
            return
        try:
            data = json.loads(Path(guideline_paths[0]).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        for guideline in data.get("reference_guidelines", []) or []:
            certainty = guideline.get("mapping_certainty")
            guideline_id = guideline.get("id")
            if (
                isinstance(certainty, (int, float))
                and certainty <= 0.7
                and isinstance(guideline_id, str)
            ):
                self.provisional_low_certainty_guidelines.add(guideline_id)

    def check(self, feedback: dict) -> str | None:
        """Run deterministic syntax, provenance-heuristic, and history checks."""
        decision = feedback.get("decision")
        subject = feedback.get("subject", "")
        detail = feedback.get("detail", "")

        guideline_match = re.match(r"^guideline_([\w\-]+)", subject)
        if (
            guideline_match
            and decision == "Reject"
            and guideline_match.group(1) in self.provisional_low_certainty_guidelines
        ):
            return (
                "Provisional-Heuristic Warning: rejecting low-certainty mapped guideline "
                f"'{guideline_match.group(1)}' requires human adjudication before reuse. "
                "This flag is not a core domain constraint."
            )

        if subject == "template_advisor" and "{" in detail and "}" not in detail:
            return "Rule-2 Warning: template revision contains mismatched braces (syntax error)."

        for prior in reversed(self.output_store.feedback_records()):
            if prior.get("setting") == self.setting and prior.get("subject") == subject:
                if prior.get("decision") != decision:
                    return (
                        "Rule-3 Warning: decision contradicts a prior demo feedback record "
                        f"(was {prior.get('decision')})."
                    )
                break

        return None


def _record_id(record: dict) -> str:
    canonical = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "DEMO-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20]


def build_record(
    feedback: dict,
    evidence: list[dict],
    *,
    origin: str,
    state: str,
    verification_outcome: str,
    override_rationale: str = "",
) -> dict:
    """Build an explicitly non-trusted record with source provenance."""
    artifacts = []
    for item in evidence:
        source = item.get("source_artifact") or ""
        digest = item.get("source_sha256") or ""
        if source or digest:
            artifacts.append({"path": source, "sha256": digest})
    record = {
        "schema_version": "1.0",
        "record_type": (
            "adjudication_candidate" if state == "needs_adjudication" else "feedback_record"
        ),
        "state": state,
        "origin": origin,
        "trusted_memory_eligible": False,
        "confirmation_status": "unconfirmed_demo_input",
        "setting": feedback["setting"],
        "subject": feedback["subject"],
        "decision": feedback["decision"],
        "detail": feedback.get("detail", ""),
        "rationale": feedback["rationale"],
        "verification": {
            "method": "deterministic_only",
            "semantic_checker_enabled": SEMANTIC_CHECKER_ENABLED,
            "outcome": verification_outcome,
        },
        "provenance": {
            "source_mode": (
                "synthetic_fixture"
                if origin == SYNTHETIC_ORIGIN
                else "offline_artifact_replay"
            ),
            "source_event_ids": [item.get("event_id") for item in evidence if item.get("event_id")],
            "source_artifacts": artifacts,
            "capture_statuses": sorted(
                {item.get("capture_status") or "unknown" for item in evidence}
            ),
            "claim_scope": CLAIM,
        },
    }
    if state == "needs_adjudication":
        record["override_requested"] = True
        record["override_rationale"] = override_rationale
    record["record_id"] = _record_id(record)
    return record


def print_evidence(evidence: list[dict], *, indent: str = "    ", limit: int | None = None) -> None:
    """Print the replay evidence behind a queue subject."""
    visible = evidence if limit is None else evidence[:limit]
    for item in visible:
        digest = item.get("source_sha256") or "missing"
        print(
            f"{indent}- {item.get('event_id')} | {item.get('event')} | stage={item.get('stage')} "
            f"| sev={item.get('severity')} | capture={item.get('capture_status')}"
        )
        print(f"{indent}  detail: {item.get('detail') or '(none)'}")
        print(
            f"{indent}  source: {item.get('source_artifact') or '(none)'} "
            f"sha256={digest}"
        )
    if limit is not None and len(evidence) > limit:
        print(
            f"{indent}- ... {len(evidence) - limit} more evidence record(s); "
            "select for full details"
        )


def run_bounded_dialogue(
    engine: VerificationEngine,
    output_store: DemoOutputStore,
    setting: str,
    subject: str,
    evidence: list[dict],
    *,
    origin: str = OFFLINE_DEMO_ORIGIN,
    is_mock: bool = False,
    mock_inputs: list[str] | None = None,
) -> tuple[str, str, bool]:
    """Run a two-round, proposal-only review dialogue."""
    input_idx = 0
    mock_values = mock_inputs or []

    def get_input(prompt: str) -> str:
        nonlocal input_idx
        if is_mock:
            if input_idx >= len(mock_values):
                raise RuntimeError(f"Mock input exhausted at prompt: {prompt}")
            value = mock_values[input_idx]
            input_idx += 1
            print(f"{prompt}{value}")
            return value.strip()
        return input(prompt).strip()

    def get_choice(prompt: str, choices: dict[str, str]) -> str:
        while True:
            raw = get_input(prompt)
            selected = choices.get(raw.casefold())
            if selected is not None:
                return selected
            print(f"  >> Invalid choice. Expected one of: {', '.join(sorted(choices))}.")

    def get_required_text(prompt: str) -> str:
        while True:
            value = get_input(prompt)
            if value:
                return value
            print("  >> A non-empty value is required for this demo record.")

    print(f"\nReviewing subject '{subject}' in setting '{setting}':")
    print("  Underlying evidence:")
    print_evidence(evidence, indent="    ")

    decision = get_choice("  Enter decision (Approve/Reject): ", DECISIONS)
    detail = ""
    if subject == "template_advisor":
        detail = get_required_text("  Enter template details (e.g. {construct}): ")
    rationale = get_required_text("  Enter rationale: ")

    feedback = {
        "setting": setting,
        "subject": subject,
        "decision": decision,
        "detail": detail,
        "rationale": rationale,
    }

    conflict_r1 = engine.check(feedback)
    if not conflict_r1:
        print("  >> [S5-Verify] Passed deterministic demo checks.")
        record = build_record(
            feedback,
            evidence,
            origin=origin,
            state="feedback_received",
            verification_outcome="deterministic_checks_passed",
        )
        output_store.save_feedback_record(record)
        return decision, rationale, False

    print(f"\n  [Round 1] S5-Verify caught a conflict:\n  >> {conflict_r1}")
    print("  >> Revise the demo ruling or request escalation; no correction is applied.")
    action = get_choice("  Do you want to revise your decision? (yes/no): ", YES_NO)

    if action == "yes":
        decision = get_choice("  Enter revised decision (Approve/Reject): ", DECISIONS)
        if subject == "template_advisor":
            detail = get_required_text("  Enter revised template details: ")
            feedback["detail"] = detail
        rationale = get_required_text("  Enter revised rationale: ")
        feedback["decision"] = decision
        feedback["rationale"] = rationale

        conflict_r2 = engine.check(feedback)
        if not conflict_r2:
            print("  >> [S5-Verify] Passed deterministic demo checks on revision.")
            record = build_record(
                feedback,
                evidence,
                origin=origin,
                state="feedback_received",
                verification_outcome="deterministic_checks_passed_after_revision",
            )
            output_store.save_feedback_record(record)
            return decision, rationale, False
        print(f"  >> [Round 2] Conflict persists:\n  >> {conflict_r2}")

    print("\n  [Round 2] A persistent conflict can only become an adjudication candidate.")
    override = get_choice("  Request supervisor adjudication? (yes/no): ", YES_NO)
    if override == "yes":
        override_rationale = get_required_text("  Provide explicit escalation rationale: ")
        record = build_record(
            feedback,
            evidence,
            origin=origin,
            state="needs_adjudication",
            verification_outcome="conflict_requires_adjudication",
            override_rationale=override_rationale,
        )
        output_store.save_adjudication_candidate(record)
        print("  >> Candidate written only to the adjudication queue; trusted memory is unchanged.")
        return decision, rationale, True

    print("  >> Review aborted. No demo record stored.")
    return "Aborted", "", False


def run_dry_run(events: list[dict]) -> None:
    """Print passive replay and triage workload counts without writing files."""
    print("=== H-Layer Dry Run: Triage & Load Analysis ===")
    print(f"Claim scope: {CLAIM}\n")

    triageable = [event for event in events if event["severity"] >= 1]
    bundled_keys = {(event["setting"], bundle_key_of(event)) for event in triageable}
    total_load = len(triageable)
    bundled_load = len(bundled_keys)

    print(f"Total events in EXP-006 baseline: {len(events)}")
    print(f"Triageable replay alerts (unbundled): {total_load}")
    print(f"Bundled review tasks (subject-level): {bundled_load}")
    reduction = round((1 - bundled_load / total_load) * 100, 2) if total_load else 0
    print(f"Observed replay bundling reduction: {reduction}%")


def run_interactive_shell(events: list[dict], output_store: DemoOutputStore) -> None:
    """Run the interactive, offline review menu."""
    print("=== H-Layer Interactive Review Shell (Offline Demo) ===")
    print(f"Claim scope: {CLAIM}")
    print(f"Demo outputs: {output_store.output_dir}")
    print("All records are unconfirmed and trusted_memory_eligible=false.")

    triageable = [event for event in events if event["severity"] >= 1]
    while True:
        print("\n--- Settings Menu ---")
        for index, setting_name in enumerate(SETTINGS):
            print(f" {index + 1}. {setting_name}")
        print(" 5. Exit")
        choice = input("Select setting number: ").strip()
        if choice == "5" or not choice:
            break
        if choice not in {"1", "2", "3", "4"}:
            print("Invalid choice.")
            continue

        setting = SETTINGS[int(choice) - 1]
        engine = VerificationEngine(setting, output_store)
        bundled: dict[str, list[dict]] = defaultdict(list)
        for event in triageable:
            if event["setting"] == setting:
                bundled[bundle_key_of(event)].append(event)

        subjects = sorted(bundled)
        while True:
            print(f"\n--- Queue for '{setting}' ({len(subjects)} items) ---")
            for index, subject in enumerate(subjects):
                subject_events = bundled[subject]
                max_severity = max(event["severity"] for event in subject_events)
                print(
                    f" {index + 1}. {subject} "
                    f"[alerts={len(subject_events)}, max_sev={max_severity}]"
                )
                print_evidence(subject_events, indent="      ", limit=2)
            print(" b. Back to Settings")
            sub_choice = input("Select item number to review: ").strip()
            if sub_choice.lower() == "b":
                break
            try:
                sub_index = int(sub_choice) - 1
            except ValueError:
                print("Invalid input.")
                continue
            if not 0 <= sub_index < len(subjects):
                print("Index out of bounds.")
                continue
            subject = subjects[sub_index]
            run_bounded_dialogue(
                engine,
                output_store,
                setting,
                subject,
                bundled[subject],
            )


def _synthetic_evidence(event_id: str, event: str, detail: str) -> list[dict]:
    return [
        {
            "event_id": event_id,
            "event": event,
            "stage": "synthetic_demo",
            "severity": 2,
            "detail": detail,
            "capture_status": SYNTHETIC_ORIGIN,
            "source_artifact": "synthetic_fixture",
            "source_sha256": "",
        }
    ]


def run_mock_session(events: list[dict], output_store: DemoOutputStore) -> None:
    """Execute deterministic synthetic inputs against an isolated output store."""
    if not events:
        raise RuntimeError("EXP-006 replay input is required before running the mock session")
    print("=== H-Layer Automated Mock Session Verification ===")
    print(f"Origin: {SYNTHETIC_ORIGIN}")
    print(f"Output directory: {output_store.output_dir}")
    setting = "cd_ch"
    engine = VerificationEngine(setting, output_store)

    print("\n--- Test 1: Provisional heuristic conflict becomes adjudication candidate ---")
    mock_inputs_1 = [
        "Reject",
        "G4 is unnecessary for this synthetic setting",
        "no",
        "yes",
        "Synthetic exception requires supervisor adjudication",
    ]
    decision, _, escalated = run_bounded_dialogue(
        engine,
        output_store,
        setting,
        "guideline_G4",
        _synthetic_evidence("SYNTHETIC-G4", "E12_low_certainty_guideline", "G4 fixture"),
        origin=SYNTHETIC_ORIGIN,
        is_mock=True,
        mock_inputs=mock_inputs_1,
    )
    assert decision == "Reject" and escalated, "Test 1 failed"

    print("\n--- Test 2: Mismatched braces are corrected ---")
    mock_inputs_2 = [
        "Approve",
        "{construct_A",
        "Synthetic template fixture",
        "yes",
        "Approve",
        "{construct_A}",
        "Corrected synthetic template fixture",
    ]
    decision, _, escalated = run_bounded_dialogue(
        engine,
        output_store,
        setting,
        "template_advisor",
        _synthetic_evidence("SYNTHETIC-TEMPLATE", "E1_template_revised", "brace fixture"),
        origin=SYNTHETIC_ORIGIN,
        is_mock=True,
        mock_inputs=mock_inputs_2,
    )
    assert decision == "Approve" and not escalated, "Test 2 failed"

    feedback_records = output_store.feedback_records()
    adjudication_records = DemoOutputStore._load_records(output_store.adjudication_file)
    assert all(not record["trusted_memory_eligible"] for record in feedback_records)
    assert all(not record["trusted_memory_eligible"] for record in adjudication_records)
    assert not any(record.get("override_requested") for record in feedback_records)
    assert all(record["state"] == "needs_adjudication" for record in adjudication_records)
    print("\n[OK] Automated synthetic mock session verification passed.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true", help="Print replay triage workload")
    modes.add_argument(
        "--test-conflict",
        action="store_true",
        help="Print deterministic conflict example",
    )
    modes.add_argument("--mock-session", action="store_true", help="Run synthetic mock inputs")
    modes.add_argument("--interactive", action="store_true", help="Start the offline review shell")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Isolated demo output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    events = load_real_events()
    if not events:
        print("Replay events missing; run exp006_event_replay.py first.", file=sys.stderr)
        return 1

    try:
        output_dir = validate_output_dir(args.output_dir)
    except ValueError as exc:
        print(f"Output-path safety error: {exc}", file=sys.stderr)
        return 2
    output_store = DemoOutputStore(output_dir)
    if args.dry_run:
        run_dry_run(events)
    elif args.test_conflict:
        engine = VerificationEngine("cd_ch", output_store)
        print("\n--- Deterministic syntax-conflict example ---")
        feedback = {
            "decision": "Approve",
            "subject": "template_advisor",
            "detail": "{construct_A",
            "rationale": "Synthetic syntax fixture",
        }
        print(f"Warning: {engine.check(feedback)}")
    elif args.mock_session:
        run_mock_session(events, output_store)
    elif args.interactive:
        run_interactive_shell(events, output_store)
    else:
        print("No mode selected; no files were written.")
        print("Choose one of --dry-run, --test-conflict, --mock-session, or --interactive.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
