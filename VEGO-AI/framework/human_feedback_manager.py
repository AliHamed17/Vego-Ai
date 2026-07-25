"""
human_feedback_manager.py — capture, validate, and attach human feedback.

Milestone 2 of the Human-AI Co-Reasoning extension. Pure Python, no LLM call.

This milestone CAPTURES human judgment about Human Review Queue items and attaches
it to those items, producing a *resolved* queue. It deliberately does NOT change
any AI decision (no Agent 4 re-classification), does not store reusable judgment
(no Human Judgment Memory), and does not touch the visualizer. Those are later
milestones.

Flow
----
    human_review_queue.jsonl  (Milestone 1 output)
            +
    human_feedback.jsonl      (expert decisions)
            |
            v
    load + validate (schema + business rules)
            |
            v
    attach by review_id, verify review_signature
            |
            v
    human_review_queue_resolved.jsonl

Matching rules
--------------
  * Feedback is matched to a review item by review_id.
  * review_signature is verified. A mismatch is NEVER applied silently: the item
    is marked status="signature_mismatch" with a resolution_note, and the feedback
    is reported, not applied.
  * Feedback whose review_id is not in the queue is reported as unmatched.
  * Items with no feedback keep status="pending".

CLI (no API key)
----------------
    python human_feedback_manager.py \
        --queue   ../human_review_output/ucd_ch/human_review_queue.jsonl \
        --feedback ../inputs/human_feedback.example.jsonl \
        --out     ../human_review_output/ucd_ch/human_review_queue_resolved.jsonl
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
from pathlib import Path

try:
    from hlayer_architecture import (
        add_architecture_arguments,
        apply_stage_architecture,
        publish_stage_output,
    )
except ImportError:  # pragma: no cover - package import fallback
    from .hlayer_architecture import (  # type: ignore
        add_architecture_arguments,
        apply_stage_architecture,
        publish_stage_output,
    )

logger = logging.getLogger(__name__)

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
DEFAULT_FEEDBACK_SCHEMA = _REPO / "schemas" / "human_feedback.schema.json"

# Decision types that change/contest the AI verdict and therefore require a
# rationale (a plain approval does not).
RATIONALE_REQUIRED_UNLESS = {"approve_ai_decision"}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def _load_jsonl(path: str | Path) -> list[dict]:
    items: list[dict] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def load_review_queue(path: str | Path) -> list[dict]:
    """Load a human_review_queue.jsonl into a list of review items."""
    return _load_jsonl(path)


def load_feedback(path: str | Path) -> list[dict]:
    """Load a human_feedback.jsonl into a list of feedback objects."""
    return _load_jsonl(path)


# ---------------------------------------------------------------------------
# Validation (schema + business rules)
# ---------------------------------------------------------------------------

def validate_feedback(
    feedback: dict,
    schema_path: str | Path = DEFAULT_FEEDBACK_SCHEMA,
) -> list[str]:
    """
    Validate one feedback object. Returns a list of error strings ([] == valid).

    Layer 1 — structural: mandatory JSON Schema (Draft-07).
    Layer 2 — business rule: any decision that is not a plain approval must carry
              a non-empty rationale.
    """
    errors: list[str] = []

    # Layer 1 — structural
    from jsonschema import Draft7Validator

    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    for e in sorted(
        Draft7Validator(schema).iter_errors(feedback), key=lambda x: list(x.path)
    ):
        loc = "/".join(str(p) for p in e.path) or "(root)"
        errors.append(f"schema: {loc}: {e.message}")

    # Layer 2 — business rule: rationale required for non-approve decisions
    hd = feedback.get("human_decision") or {}
    decision_type = hd.get("decision_type")
    if decision_type and decision_type not in RATIONALE_REQUIRED_UNLESS:
        if not (hd.get("rationale") or "").strip():
            errors.append(
                f"rule: decision_type '{decision_type}' requires a non-empty rationale"
            )

    return errors


# ---------------------------------------------------------------------------
# Attaching
# ---------------------------------------------------------------------------

def _match(review_items: list[dict], feedback_items: list[dict]) -> tuple[list[dict], dict]:
    """Core matcher shared by attach_feedback and report_feedback."""
    items = [copy.deepcopy(it) for it in review_items]
    index = {it.get("review_id"): it for it in items}

    resolved = 0
    mismatched: list[str] = []
    unmatched: list[str] = []

    for fb in feedback_items:
        fid = fb.get("feedback_id", "<no-id>")
        rid = fb.get("review_id")
        item = index.get(rid)
        if item is None:
            unmatched.append(fid)
            logger.warning("Feedback %s: review_id %r not in queue (unmatched).", fid, rid)
            continue
        if fb.get("review_signature") != item.get("review_signature"):
            item["status"] = "signature_mismatch"
            item["resolution_note"] = (
                f"feedback {fid} signature {fb.get('review_signature')!r} != "
                f"item signature {item.get('review_signature')!r}; not applied"
            )
            mismatched.append(fid)
            logger.warning("Feedback %s: signature mismatch on %s; not applied.", fid, rid)
            continue
        item["status"] = "resolved"
        item["feedback_id"] = fb.get("feedback_id")
        item["human_feedback"] = fb
        resolved += 1

    report = {
        "total_items": len(items),
        "resolved": resolved,
        "signature_mismatch": len(mismatched),
        "pending": sum(1 for it in items if it.get("status") == "pending"),
        "unmatched_feedback": unmatched,
        "mismatched_feedback": mismatched,
    }
    return items, report


def attach_feedback(
    review_items: list[dict],
    feedback_items: list[dict],
    *,
    architecture_mode: str = "legacy",
    architecture_manifest: str | Path | None = None,
) -> list[dict]:
    """
    Attach feedback to review items (by review_id, verifying review_signature).

    Returns a new list of items (originals are not mutated). Resolved items get
    status="resolved", feedback_id, and human_feedback. Signature mismatches get
    status="signature_mismatch" and a resolution_note and are NOT applied. Items
    with no feedback keep status="pending".
    """
    items, _ = _match(review_items, feedback_items)
    return apply_stage_architecture(
        "resolved",
        items,
        architecture_mode=architecture_mode,
        architecture_manifest=architecture_manifest,
    ).output


def report_feedback(review_items: list[dict], feedback_items: list[dict]) -> dict:
    """Return match counts and unmatched/mismatched feedback ids (no mutation)."""
    _, report = _match(review_items, feedback_items)
    return report


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

def write_resolved_queue(items: list[dict], path: str | Path) -> int:
    """Write the resolved queue as JSONL. Returns the number of items written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for item in items:
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")
    logger.info("Resolved queue -> %s (%d item(s))", path, len(items))
    return len(items)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Attach validated human feedback to a Human Review Queue (no API key)."
    )
    parser.add_argument("--queue", required=True, help="human_review_queue.jsonl")
    parser.add_argument("--feedback", required=True, help="human_feedback.jsonl")
    parser.add_argument("--out", required=True, help="output human_review_queue_resolved.jsonl")
    parser.add_argument("--schema", default=str(DEFAULT_FEEDBACK_SCHEMA),
                        help="human_feedback.schema.json (default: repo schemas/)")
    add_architecture_arguments(parser)
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

    review_items = load_review_queue(args.queue)
    raw_feedback = load_feedback(args.feedback)

    valid: list[dict] = []
    invalid = 0
    for fb in raw_feedback:
        errs = validate_feedback(fb, args.schema)
        if errs:
            invalid += 1
            print(f"INVALID feedback {fb.get('feedback_id', '<no-id>')}:")
            for e in errs:
                print(f"    - {e}")
        else:
            valid.append(fb)

    items = attach_feedback(
        review_items,
        valid,
    )
    report = report_feedback(review_items, valid)
    execution = publish_stage_output(
        "resolved",
        items,
        output_path=args.out,
        writer=write_resolved_queue,
        architecture_mode=args.architecture_mode,
        architecture_manifest=args.architecture_manifest,
    )
    items = execution.output

    print("\n=== Feedback attachment summary ===")
    print(f"review items     : {report['total_items']}")
    print(f"feedback (valid) : {len(valid)}   (invalid: {invalid})")
    print(f"resolved         : {report['resolved']}")
    print(f"signature_mismatch: {report['signature_mismatch']}  {report['mismatched_feedback']}")
    print(f"unmatched feedback: {len(report['unmatched_feedback'])}  {report['unmatched_feedback']}")
    print(f"still pending     : {report['pending']}")
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
