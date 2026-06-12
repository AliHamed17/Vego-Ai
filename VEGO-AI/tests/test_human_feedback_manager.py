"""
Minimal tests for the Human Feedback Manager (Milestone 2).

Runs with no third-party dependency:
    python tests/test_human_feedback_manager.py
Also discoverable by pytest:
    pytest tests/test_human_feedback_manager.py

Schema-validation assertions degrade gracefully if `jsonschema` is absent.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "framework"))

import human_feedback_manager as hfm  # noqa: E402

FEEDBACK_SCHEMA = ROOT / "schemas" / "human_feedback.schema.json"
ITEM_SCHEMA = ROOT / "schemas" / "human_review_item.schema.json"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _item(review_id="HRQ-ucd_ch-P4", sig="e7276994de70f031", status="pending"):
    return {
        "review_id": review_id,
        "review_signature": sig,
        "signature_fields": ["source_setting", "pattern_description",
                             "related_guideline_id", "affected_cases", "classification"],
        "schema_version": "1.2.0",
        "provenance": {"source_system": "VEGO-AI", "policy_version": "human-review-policy-v1",
                       "source_setting": "ucd_ch"},
        "setting_id": "ucd_ch",
        "pattern_id": "P4",
        "source_pattern_id": "P4",
        "pipeline_stage": "agent4_classify_variability",
        "ai_decision": {"classification": "Substantial Variability", "confidence": "High",
                        "flag_for_guidelines_update": True, "requires_human_review": False},
        "trigger_reasons": ["guideline_update_proposed"],
        "status": status,
        "feedback_id": None,
    }


def _feedback(review_id="HRQ-ucd_ch-P4", sig="e7276994de70f031",
              decision_type="valid_alternative", rationale="because it is valid",
              fid="HF-1"):
    hd = {"decision_type": decision_type, "confidence": "High"}
    if rationale is not None:
        hd["rationale"] = rationale
    return {
        "feedback_id": fid,
        "review_id": review_id,
        "review_signature": sig,
        "expert_id": "expert_01",
        "timestamp": "2026-06-11T12:00:00Z",
        "human_decision": hd,
    }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_valid_feedback_passes():
    assert hfm.validate_feedback(_feedback(), FEEDBACK_SCHEMA) == []


def test_missing_required_field_fails():
    fb = _feedback()
    del fb["expert_id"]
    errors = hfm.validate_feedback(fb, FEEDBACK_SCHEMA)
    assert errors and any("expert_id" in e for e in errors)


def test_meaningful_change_requires_rationale():
    fb = _feedback(decision_type="reject_ai_decision", rationale=None)
    errors = hfm.validate_feedback(fb, FEEDBACK_SCHEMA)
    assert any("rationale" in e for e in errors)


def test_plain_approve_allows_empty_rationale():
    fb = _feedback(decision_type="approve_ai_decision", rationale=None)
    # structural-only: no rationale required for a plain approval
    assert hfm.validate_feedback(fb, FEEDBACK_SCHEMA) == []


# ---------------------------------------------------------------------------
# Attaching
# ---------------------------------------------------------------------------

def test_attach_by_id_and_matching_signature():
    items = hfm.attach_feedback([_item()], [_feedback(fid="HF-9")])
    it = items[0]
    assert it["status"] == "resolved"
    assert it["feedback_id"] == "HF-9"
    assert it["human_feedback"]["human_decision"]["decision_type"] == "valid_alternative"


def test_signature_mismatch_not_applied():
    items = hfm.attach_feedback([_item()], [_feedback(sig="0000000000000000")])
    it = items[0]
    assert it["status"] == "signature_mismatch"
    assert it.get("feedback_id") is None
    assert "human_feedback" not in it
    assert "resolution_note" in it


def test_unmatched_feedback_reported():
    report = hfm.report_feedback([_item()], [_feedback(review_id="HRQ-ucd_ch-P99", fid="HF-x")])
    assert "HF-x" in report["unmatched_feedback"]
    assert report["resolved"] == 0


def test_unresolved_items_remain_pending():
    items = hfm.attach_feedback([_item(), _item(review_id="HRQ-ucd_ch-P5", sig="858650979a1195fb")],
                                [_feedback(fid="HF-only-P4")])
    by_id = {it["review_id"]: it for it in items}
    assert by_id["HRQ-ucd_ch-P4"]["status"] == "resolved"
    assert by_id["HRQ-ucd_ch-P5"]["status"] == "pending"


def test_attach_does_not_mutate_input():
    original = _item()
    hfm.attach_feedback([original], [_feedback()])
    assert original["status"] == "pending"  # original untouched


# ---------------------------------------------------------------------------
# Resolved output validates against the (extended) review-item schema
# ---------------------------------------------------------------------------

def test_resolved_items_validate_against_item_schema():
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        print("    (skipped: jsonschema not installed)")
        return
    schema = json.loads(ITEM_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema)
    items = hfm.attach_feedback(
        [_item(), _item(review_id="HRQ-ucd_ch-P5", sig="858650979a1195fb")],
        [_feedback(fid="HF-a"), _feedback(review_id="HRQ-ucd_ch-P5", sig="bad", fid="HF-b")],
    )
    for it in items:
        validator.validate(it)


# ---------------------------------------------------------------------------
# Round-trip via files
# ---------------------------------------------------------------------------

def test_load_and_write_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        qp, fp, op = Path(d) / "q.jsonl", Path(d) / "f.jsonl", Path(d) / "out.jsonl"
        qp.write_text(json.dumps(_item()) + "\n", encoding="utf-8")
        fp.write_text(json.dumps(_feedback(fid="HF-rt")) + "\n", encoding="utf-8")
        items = hfm.attach_feedback(hfm.load_review_queue(qp), hfm.load_feedback(fp))
        n = hfm.write_resolved_queue(items, op)
        assert n == 1
        written = hfm.load_review_queue(op)
        assert written[0]["status"] == "resolved"
        assert written[0]["feedback_id"] == "HF-rt"


# ---------------------------------------------------------------------------
# Manual runner (no pytest required)
# ---------------------------------------------------------------------------

def _run_all() -> int:
    funcs = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in funcs:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {fn.__name__}: {exc!r}")
    print(f"\n{len(funcs) - failed}/{len(funcs)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run_all())
