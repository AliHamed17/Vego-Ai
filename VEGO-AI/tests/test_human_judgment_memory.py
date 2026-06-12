"""
Minimal tests for the Human Judgment Memory (Milestone 3).

Runs with no third-party dependency:
    python tests/test_human_judgment_memory.py
Also discoverable by pytest:
    pytest tests/test_human_judgment_memory.py

Schema-validation assertions degrade gracefully if `jsonschema` is absent.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "framework"))

import human_judgment_memory as hjm  # noqa: E402

JUDGMENT_SCHEMA = ROOT / "schemas" / "human_judgment.schema.json"


# ---------------------------------------------------------------------------
# Fixtures: a resolved review item (M2 output shape)
# ---------------------------------------------------------------------------

def _resolved(
    *,
    review_id="HRQ-ucd_ch-P5",
    pattern_id="P5",
    sig="858650979a1195fb",
    status="resolved",
    reusable=True,
    rationale="Marketing dept update is an explicit domain responsibility.",
    decision_type="needs_guideline_update",
    classification="Substantial Variability",
    related_guideline_id="G12",
    target_fragment="Marketing employees' ability to update wine information.",
    feedback_id="HF-ucd_ch-P5-001",
    with_feedback=True,
):
    item = {
        "review_id": review_id,
        "review_signature": sig,
        "schema_version": "1.2.0",
        "setting_id": "ucd_ch",
        "pattern_id": pattern_id,
        "source_pattern_id": pattern_id,
        "domain": "cheers",
        "diagram_type": "UCD",
        "related_guideline_id": related_guideline_id,
        "target_fragment": target_fragment,
        "ai_decision": {"classification": "Occasional Variability", "confidence": "Medium",
                        "flag_for_guidelines_update": False, "requires_human_review": False},
        "trigger_reasons": ["medium_confidence"],
        "status": status,
        "feedback_id": feedback_id if (with_feedback and status == "resolved") else None,
    }
    if with_feedback:
        hd = {"decision_type": decision_type, "confidence": "High"}
        if classification is not None:
            hd["corrected_classification"] = classification
        if rationale is not None:
            hd["rationale"] = rationale
        item["human_feedback"] = {
            "feedback_id": feedback_id,
            "review_id": review_id,
            "review_signature": sig,
            "expert_id": "expert_01",
            "timestamp": "2026-06-11T12:00:00Z",
            "human_decision": hd,
            "reusable": reusable,
            "reuse_scope": {"domain": "cheers", "diagram_type": "UCD",
                            "applies_to_future_models": True, "limitations": ""},
            "guideline_update": {"action": "add_alternative",
                                 "proposed_text": "Marketing Dept as alt actor.",
                                 "requires_second_expert": False},
        }
    return item


# ---------------------------------------------------------------------------
# Ingestion guardrails
# ---------------------------------------------------------------------------

def test_reusable_resolved_becomes_memory():
    memory, report = hjm.ingest_judgments([_resolved()])
    assert report["ingested"] == 1 and len(memory) == 1
    m = memory[0]
    assert m["memory_id"] == "HJM-ucd_ch-P5"
    assert m["source_feedback_id"] == "HF-ucd_ch-P5-001"
    assert m["human_classification"] == "Substantial Variability"


def test_non_reusable_skipped():
    memory, report = hjm.ingest_judgments([_resolved(reusable=False)])
    assert memory == []
    assert report["skipped_by_reason"].get("skipped_non_reusable") == 1


def test_signature_mismatch_skipped():
    memory, report = hjm.ingest_judgments([_resolved(status="signature_mismatch")])
    assert memory == []
    assert report["skipped_by_reason"].get("signature_mismatch") == 1


def test_pending_skipped():
    memory, report = hjm.ingest_judgments([_resolved(status="pending", with_feedback=False)])
    assert memory == []
    assert report["skipped_by_reason"].get("not_resolved") == 1


def test_missing_rationale_skipped():
    memory, report = hjm.ingest_judgments([_resolved(rationale="")])
    assert memory == []
    assert report["skipped_by_reason"].get("missing_rationale") == 1


def test_provenance_recorded():
    memory, _ = hjm.ingest_judgments([_resolved()])
    prov = memory[0]["provenance"]
    assert prov["source_setting"] == "ucd_ch"
    assert prov["source_pattern_id"] == "P5"
    assert prov["source_schema_versions"]["review_item_schema"] == "1.2.0"
    assert prov["source_schema_versions"]["judgment_schema"] == hjm.JUDGMENT_SCHEMA_VERSION


# ---------------------------------------------------------------------------
# memory_signature stability
# ---------------------------------------------------------------------------

def test_memory_signature_is_16_hex_and_stable():
    m1 = hjm.build_memory_item(_resolved())
    m2 = hjm.build_memory_item(_resolved())
    assert len(m1["memory_signature"]) == 16
    assert all(c in "0123456789abcdef" for c in m1["memory_signature"])
    assert m1["memory_signature"] == m2["memory_signature"]  # deterministic


def test_memory_signature_changes_with_classification():
    a = hjm.build_memory_item(_resolved(classification="Substantial Variability"))
    b = hjm.build_memory_item(_resolved(classification="Occasional Variability"))
    assert a["memory_signature"] != b["memory_signature"]


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def test_memory_validates_against_schema():
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        print("    (skipped: jsonschema not installed)")
        return
    schema = json.loads(JUDGMENT_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema)
    memory, _ = hjm.ingest_judgments([_resolved(), _resolved(review_id="HRQ-ucd_ch-P4",
                                                             pattern_id="P4", sig="e7276994de70f031",
                                                             related_guideline_id="G16",
                                                             feedback_id="HF-ucd_ch-P4-001")])
    for m in memory:
        validator.validate(m)


# ---------------------------------------------------------------------------
# Retrieval — explainable match_reasons
# ---------------------------------------------------------------------------

def test_search_returns_explainable_match_reasons():
    memory, _ = hjm.ingest_judgments([_resolved()])
    hits = hjm.search_memory(memory, domain="cheers", diagram_type="UCD",
                             related_guideline_id="G12", keywords="Marketing")
    assert len(hits) == 1
    reasons = hits[0]["match_reasons"]
    assert "same domain" in reasons
    assert "same diagram type" in reasons
    assert "same related guideline G12" in reasons
    assert any(r.startswith("keyword match: Marketing") for r in reasons)
    assert hits[0]["match_score"] == len(reasons)


def test_search_excludes_non_matches():
    memory, _ = hjm.ingest_judgments([_resolved()])
    assert hjm.search_memory(memory, related_guideline_id="G99") == []


def test_search_no_filter_returns_all():
    memory, _ = hjm.ingest_judgments([_resolved()])
    assert len(hjm.search_memory(memory)) == 1


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_conflict_detection_flags_disagreement():
    # same domain/diagram/guideline/fragment, different human_classification,
    # but distinct (setting, pattern) so the memory_ids differ.
    a = _resolved(review_id="HRQ-ucd_ch-P5", pattern_id="P5", sig="858650979a1195fb",
                  classification="Substantial Variability", feedback_id="HF-a")
    b = _resolved(review_id="HRQ-ucd_ch-P8", pattern_id="P8", sig="0000000000000001",
                  classification="Occasional Variability", feedback_id="HF-b")
    memory, report = hjm.ingest_judgments([a, b])
    assert report["conflicts"] == 2
    for m in memory:
        assert m["conflict_status"] == "needs_adjudication"
        assert m["conflicting_memory_ids"] == [
            mm["memory_id"] for mm in memory if mm["memory_id"] != m["memory_id"]
        ]
    hits = hjm.search_memory(memory, domain="cheers")
    assert all(h.get("match_warning") == "conflicting_human_judgments" for h in hits)


def test_no_conflict_when_agree():
    a = _resolved(review_id="HRQ-ucd_ch-P5", pattern_id="P5", sig="858650979a1195fb",
                  classification="Substantial Variability", feedback_id="HF-a")
    b = _resolved(review_id="HRQ-ucd_ch-P8", pattern_id="P8", sig="0000000000000002",
                  classification="Substantial Variability", feedback_id="HF-b")
    memory, report = hjm.ingest_judgments([a, b])
    assert report["conflicts"] == 0
    assert all(m["conflict_status"] == "none" for m in memory)


# ---------------------------------------------------------------------------
# Round-trip / dedup
# ---------------------------------------------------------------------------

def test_write_load_roundtrip_and_dedup():
    memory, _ = hjm.ingest_judgments([_resolved()])
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "mem.jsonl"
        n1 = hjm.write_memory(memory + memory, path)   # duplicate input
        assert n1 == 1                                  # deduped by memory_id
        loaded = hjm.load_memory(path)
        assert loaded[0]["memory_id"] == "HJM-ucd_ch-P5"


# ---------------------------------------------------------------------------
# Manual runner
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
