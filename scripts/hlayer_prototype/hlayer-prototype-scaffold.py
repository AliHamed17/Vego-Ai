#!/usr/bin/env python3
"""
H-Layer Framework Interactive CLI Prototype Shell (Phase P3)

Loads real compliance warnings and classifications, presents an interactive
review queue, runs live anti-sycophancy check logic against active guidelines
and templates, and logs verified expert judgments.

Usage:
  python scripts/hlayer_prototype/hlayer-prototype-scaffold.py --dry-run
  python scripts/hlayer_prototype/hlayer-prototype-scaffold.py --test-conflict
  python scripts/hlayer_prototype/hlayer-prototype-scaffold.py --mock-session
  python scripts/hlayer_prototype/hlayer-prototype-scaffold.py --interactive
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sys
from collections import defaultdict

# Root Paths
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVAL = os.path.join(REPO, "VEGO-AI", "eval_output")
OUT_DIR = os.path.join(REPO, "reports", "generated")
FEEDBACK_FILE = os.path.join(OUT_DIR, "hlayer_prototype_feedback.json")
ADJUDICATION_LOG = os.path.join(OUT_DIR, "adjudication_log.json")

CLAIM = ("Design/mechanism evidence (observability and dialogue loop validation). "
         "No accuracy, generalization, or clinical claims. EXP-005 remains the accuracy gate.")

SETTINGS = ["cd_ch", "cd_pw", "ucd_ch", "ucd_pw"]


def load_real_events() -> list[dict]:
    """Loads events from EXP-006 events.csv and extracts case information."""
    events_path = os.path.join(REPO, "reports", "generated", "exp006", "events.csv")
    if not os.path.exists(events_path):
        return []

    events = []
    with open(events_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            sev = int(row.get("severity") or 0)
            detail = row.get("detail") or ""
            # Extract case ID if E5/E6 compliance events
            m = re.match(r"^(\d+)", detail)
            case_id = m.group(1) if m else None
            events.append({
                "event_id": f"EV_{idx:03d}",
                "setting": row.get("setting"),
                "event": row.get("event"),
                "stage": row.get("stage"),
                "severity": sev,
                "detail": detail,
                "case_id": case_id
            })
    return events


def bundle_key_of(ev: dict) -> str:
    """Standardizes subject bundling keys (S3 grouping semantics)."""
    event = ev["event"]
    detail = ev.get("detail", "")

    if event in {"E5_compliance_vector", "E6_inspector_uncertainty", "E5_compliance_eval"}:
        m = re.match(r"^(\d+)", detail)
        if m:
            return f"case_{m.group(1)}"
    if event in {"E8_classification", "E13_agent4_signals"}:
        m = re.match(r"^([\w\-]+)", detail)
        if m:
            return f"pattern_{m.group(1)}"
    if event == "E12_low_certainty_guideline":
        m = re.match(r"^([Gg]\d+)", detail)
        if m:
            return f"guideline_{m.group(1)}"
    if event in {"E2_question_from_B", "E2_question_from_D"}:
        m = re.match(r"^([Qq]_[a-zA-Z0-9\_]+)", detail)
        if m:
            return f"question_{m.group(1)}"
    if event in {"E1_template_created", "E1_template_revised"}:
        return "template_advisor"
    if event in {"E4_guidelines_created", "E4_guidelines_refined"}:
        return "domain_guidelines"
    return detail


class VerificationEngine:
    def __init__(self, setting: str):
        self.setting = setting
        self.core_guidelines = set()
        self.load_reference_sources()

    def load_reference_sources(self):
        """Loads guidelines and template files for live verification checks."""
        setting_dir = os.path.join(EVAL, self.setting)
        if not os.path.exists(setting_dir):
            return

        # Load guidelines to find high-severity/low-certainty core rules
        gl_paths = glob.glob(os.path.join(setting_dir, "agentB_best_guidelines*.json"))
        if gl_paths:
            try:
                with open(gl_paths[0], encoding="utf-8") as f:
                    data = json.load(f)
                    for g in data.get("reference_guidelines", []) or []:
                        c = g.get("mapping_certainty")
                        if isinstance(c, (int, float)) and c <= 0.7:  # Core severity criteria
                            self.core_guidelines.add(g.get("id"))
            except Exception:
                pass

    def check(self, feedback: dict) -> str | None:
        """Executes verification rules (Rule-1, Rule-2, Rule-3, and semantic checks)."""
        decision = feedback.get("decision")
        subject = feedback.get("subject", "")
        rationale = feedback.get("rationale", "")
        detail = feedback.get("detail", "")

        # Rule-1: Core guideline disabling conflict
        m_gl = re.match(r"^guideline_([\w\-]+)", subject)
        if m_gl and decision == "Reject" and m_gl.group(1) in self.core_guidelines:
            return f"Rule-1 Warning: Rejecting core guideline '{m_gl.group(1)}' violates domain constraints."

        # Rule-2: Template syntax mismatched braces check
        if subject == "template_advisor" and "{" in detail and not "}" in detail:
            return "Rule-2 Warning: Template revision contains mismatched braces (syntax error)."

        # Rule-3: Stored memory contradictions check
        if os.path.exists(FEEDBACK_FILE):
            try:
                with open(FEEDBACK_FILE, encoding="utf-8") as f:
                    past = json.load(f)
                    for p in past:
                        if p.get("setting") == self.setting and p.get("subject") == subject:
                            if p.get("decision") != decision:
                                return f"Rule-3 Warning: Decision contradicts prior judgment in memory (was {p.get('decision')})."
            except Exception:
                pass

        # Semantic check: negative terms mismatch
        if decision == "Approve" and any(w in rationale.lower() for w in ["not", "violate", "wrong", "fail"]):
            return "Semantic Warning: Rationale contains negative qualifiers but decision is Approve."

        return None


def save_feedback(record: dict, escalated: bool = False):
    """Saves verified rulings to persistent feedback and adjudication stores."""
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1. Stored Feedback Memory (E12)
    past = []
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, encoding="utf-8") as f:
                past = json.load(f)
        except Exception:
            pass
    # Overwrite if exists, otherwise append
    past = [p for p in past if not (p.get("setting") == record["setting"] and p.get("subject") == record["subject"])]
    past.append(record)
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(past, f, indent=2)

    # 2. Adjudication Log (Escalated overrides)
    if escalated:
        adj = []
        if os.path.exists(ADJUDICATION_LOG):
            try:
                with open(ADJUDICATION_LOG, encoding="utf-8") as f:
                    adj = json.load(f)
            except Exception:
                pass
        adj.append(record)
        with open(ADJUDICATION_LOG, "w", encoding="utf-8") as f:
            json.dump(adj, f, indent=2)


def run_bounded_dialogue(engine: VerificationEngine, setting: str, subject: str,
                         is_mock: bool = False, mock_inputs: list = None) -> tuple[str, str, bool]:
    """Runs the 2-round bounded dialogue interface (Iris Directive D10)."""
    input_idx = 0

    def get_input(prompt: str) -> str:
        nonlocal input_idx
        if is_mock:
            val = mock_inputs[input_idx]
            input_idx += 1
            print(f"{prompt}{val}")
            return val
        return input(prompt).strip()

    print(f"\nReviewing subject '{subject}' in setting '{setting}':")
    
    # Dialogue Round 1
    decision = get_input("  Enter decision (Approve/Reject): ")
    detail = ""
    if subject == "template_advisor":
        detail = get_input("  Enter template details (e.g. {construct}): ")
    rationale = get_input("  Enter rationale: ")

    feedback = {
        "setting": setting,
        "subject": subject,
        "decision": decision,
        "detail": detail,
        "rationale": rationale
    }

    conflict_r1 = engine.check(feedback)
    if not conflict_r1:
        print("  >> [S5-Verify] Passed checks.")
        save_feedback(feedback)
        return decision, rationale, False

    # Round 1 question cards
    print(f"\n  [Round 1] S5 Verify caught conflict:\n  >> {conflict_r1}")
    print("  >> S5 Question: This ruling contradicts domain rules. Would you like to revise or proceed?")
    action = get_input("  Do you want to revise your decision? (yes/no): ")

    if action.lower() in {"y", "yes"}:
        # Resubmit revised
        decision = get_input("  Enter revised decision (Approve/Reject): ")
        if subject == "template_advisor":
            detail = get_input("  Enter revised template details: ")
            feedback["detail"] = detail
        rationale = get_input("  Enter revised rationale: ")
        feedback["decision"] = decision
        feedback["rationale"] = rationale
        
        conflict_r2 = engine.check(feedback)
        if not conflict_r2:
            print("  >> [S5-Verify] Passed checks on revision.")
            save_feedback(feedback)
            return decision, rationale, False
        else:
            print(f"  >> [Round 2] Conflict persists:\n  >> {conflict_r2}")

    # Dialogue Round 2 - Final Warn override card
    print("\n  [Round 2] Final Warning: Conflict persists. An override requires validation.")
    override = get_input("  Confirm override? (yes/no): ")
    if override.lower() in {"y", "yes"}:
        override_rationale = get_input("  Provide explicit override rationale: ")
        feedback["override_flag"] = True
        feedback["override_rationale"] = override_rationale
        print("  >> [S5-Verify] Verification escalated to supervisor adjudication log.")
        save_feedback(feedback, escalated=True)
        return decision, rationale, True
    else:
        print("  >> Review aborted. No feedback stored.")
        return "Aborted", "", False


def run_dry_run(events: list):
    """Dry run: Passive S1 events loading and S2 triage dashboard."""
    print("=== H-Layer Dry Run: Triage & Load Analysis ===")
    print(f"Claim scope: {CLAIM}\n")

    triageable = [e for e in events if e["severity"] >= 1]
    bundled_keys = set()
    for e in triageable:
        bundled_keys.add((e["setting"], bundle_key_of(e)))

    total_load = len(triageable)
    bundled_load = len(bundled_keys)

    print(f"Total events in EXP-006 baseline: {len(events)}")
    print(f"Triageable alerts (unbundled every decision): {total_load}")
    print(f"Bundled review tasks (H5 subject-level): {bundled_load}")
    reduction = round((1 - (bundled_load / total_load)) * 100, 2) if total_load else 0
    print(f"Triage workload reduction: {reduction}%")


def run_interactive_shell(events: list):
    """Interactive review menu."""
    print("=== H-Layer Interactive Review Shell (Demo) ===")
    print(f"Claim scope: {CLAIM}")

    triageable = [e for e in events if e["severity"] >= 1]
    
    while True:
        print("\n--- Settings Menu ---")
        for i, s in enumerate(SETTINGS):
            print(f" {i + 1}. {s}")
        print(" 5. Exit")
        choice = input("Select setting number: ").strip()
        if choice == "5" or not choice:
            break
        if choice not in {"1", "2", "3", "4"}:
            print("Invalid choice.")
            continue

        setting = SETTINGS[int(choice) - 1]
        engine = VerificationEngine(setting)

        # Get settings events and bundle them
        set_events = [e for e in triageable if e["setting"] == setting]
        bundled = defaultdict(list)
        for e in set_events:
            sub = bundle_key_of(e)
            bundled[sub].append(e)

        subjects = sorted(bundled.keys())
        while True:
            print(f"\n--- Queue for '{setting}' ({len(subjects)} items) ---")
            for idx, sub in enumerate(subjects):
                events_list = bundled[sub]
                max_sev = max(e["severity"] for e in events_list)
                print(f" {idx + 1}. {sub} [alerts={len(events_list)}, max_sev={max_sev}]")
            print(" b. Back to Settings")
            sub_choice = input("Select item number to review: ").strip()
            if sub_choice.lower() == "b":
                break
            try:
                sub_idx = int(sub_choice) - 1
                if 0 <= sub_idx < len(subjects):
                    run_bounded_dialogue(engine, setting, subjects[sub_idx])
                else:
                    print("Index out of bounds.")
            except ValueError:
                print("Invalid input.")


def run_mock_session(events: list):
    """Automates user keyboard inputs for a mock run validation."""
    print("=== H-Layer Automated Mock Session Verification ===")
    triageable = [e for e in events if e["severity"] >= 1]
    setting = "cd_ch"
    engine = VerificationEngine(setting)

    # 1. Test Seed 1: Core Guideline Conflict overridden
    print("\n--- Test 1: Override Core Guideline Conflict ---")
    mock_inputs_1 = ["Reject", "G4 is unnecessary for this setting", "no", "yes", "Special setting exception override"]
    decision, rationale, escalated = run_bounded_dialogue(
        engine, setting, "guideline_G4", is_mock=True, mock_inputs=mock_inputs_1
    )
    assert decision == "Reject" and escalated, "Test 1 Failed"

    # 2. Test 2: Mismatched braces corrected
    print("\n--- Test 2: Mismatched Template braces corrected ---")
    mock_inputs_2 = ["Approve", "{construct_A", "Updated construct properties", "yes", "Approve", "{construct_A}", "Updated properties"]
    decision, rationale, escalated = run_bounded_dialogue(
        engine, setting, "template_advisor", is_mock=True, mock_inputs=mock_inputs_2
    )
    assert decision == "Approve" and not escalated, "Test 2 Failed"

    print("\n[OK] Automated Mock Session verification passed.")


def main():
    parser = argparse.ArgumentParser(description="H-Layer CLI Prototype Shell")
    parser.add_argument("--dry-run", action="store_true", help="Print passive listening and triage workload dashboard")
    parser.add_argument("--test-conflict", action="store_true", help="Print mock conflict warn logs")
    parser.add_argument("--mock-session", action="store_true", help="Execute automated mock inputs validation")
    parser.add_argument("--interactive", action="store_true", help="Start interactive CLI review queue shell")
    args = parser.parse_args()

    events = load_real_events()
    if not events:
        print("Replay events missing; run exp006_event_replay.py first.", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        run_dry_run(events)
    elif args.test_conflict:
        # Predefined mock conflict print
        engine = VerificationEngine("cd_ch")
        print("\n--- Sycophancy Mismatch warning example ---")
        feedback = {"decision": "Approve", "subject": "case_68059", "rationale": "This does not apply"}
        warn = engine.check(feedback)
        print(f"Warning: {warn}")
    elif args.mock_session:
        run_mock_session(events)
    elif args.interactive:
        run_interactive_shell(events)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
