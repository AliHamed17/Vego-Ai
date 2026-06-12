"""
Minimal tests for the Memory Advisory Layer (Milestone 4A).

Runs with no third-party dependency:
    python tests/test_memory_advisor.py
Also discoverable by pytest:
    pytest tests/test_memory_advisor.py

The most important property proven here: M4A NEVER changes an AI classification.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "framework"))

import memory_advisor as ma  # noqa: E402

ADVICE_SCHEMA = ROOT / "schemas" / "memory_advice.schema.json"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _mem(memory_id="HJM-ucd_ch-P5", sig="858650979a1195fb", gid="G12",
         fragment="Marketing employees' ability to update wine information.",
         classification="Substantial Variability", conflict="none"):
    return {
        "memory_id": memory_id, "memory_signature": sig,
        "domain": "cheers", "diagram_type": "UCD", "related_guideline_id": gid,
        "target_fragment": fragment, "human_classification": classification,
        "human_decision": {"decision_type": "needs_guideline_update", "rationale": "r"},
        "rationale": "r", "reuse_scope": {"domain": "cheers", "diagram_type": "UCD"},
        "conflict_status": conflict, "conflicting_memory_ids": [],
    }


def _classes(entries):
    return {"domain_identifier": "cheers", "variability_classifications": entries}


def _entry(pid="P5", classification="Substantial Variability", confidence="Medium",
           rhr=True, flag=False, evidence='G12 -- "Only employees in the marketing department..."'):
    return {"pattern_id": pid, "classification": classification, "confidence": confidence,
            "requires_human_review": rhr, "flag_for_guidelines_update": flag,
            "evidence": evidence, "justification": "j"}


def _patterns(frag):
    return {"recurring_guideline_patterns": [],
            "recurring_fragment_patterns": [{"pattern_id": pid, "description": d}
                                            for pid, d in frag.items()]}


P5_DESC = "Marketing employees' ability to update wine information is presented as an alternative."
P1_DESC = "The guideline for distinguishing wines by manufacturer and catalog number is often not satisfied."


# ---------------------------------------------------------------------------
# Advisory-only invariants
# ---------------------------------------------------------------------------

def test_one_advice_item_per_pattern():
    vc = _classes([_entry("P5"), _entry("P1", evidence="G20 -- x")])
    items = ma.build_advice_items(vc, _patterns({"P5": P5_DESC, "P1": P1_DESC}), [_mem()], "ucd_ch")
    assert [i["pattern_id"] for i in items] == ["P5", "P1"]


def test_ai_classification_never_changed():
    vc = _classes([_entry("P5", classification="Substantial Variability", confidence="Medium")])
    items = ma.build_advice_items(vc, _patterns({"P5": P5_DESC}), [_mem()], "ucd_ch")
    it = items[0]
    assert it["ai_classification_changed"] is False
    assert it["advice_mode"] == "advisory_only"
    # original is copied through unchanged
    assert it["original_ai_classification"]["classification"] == "Substantial Variability"
    assert it["original_ai_classification"]["confidence"] == "Medium"
    assert it["original_ai_classification"]["requires_human_review"] is True


def test_report_never_flags_a_change():
    vc = _classes([_entry("P5"), _entry("P6", evidence="Domain Description -- x")])
    items = ma.build_advice_items(vc, _patterns({"P5": P5_DESC, "P6": "Customer as actor"}),
                                  [_mem()], "ucd_ch")
    assert all(i["ai_classification_changed"] is False for i in items)


# ---------------------------------------------------------------------------
# Strength / relevance
# ---------------------------------------------------------------------------

def test_strong_advice_on_full_match():
    vc = _classes([_entry("P5")])
    items = ma.build_advice_items(vc, _patterns({"P5": P5_DESC}), [_mem()], "ucd_ch")
    it = items[0]
    assert it["advice_strength"] == "strong"
    assert len(it["memory_matches"]) == 1
    reasons = it["memory_matches"][0]["match_reasons"]
    assert "same related guideline G12" in reasons
    assert any(r.startswith("keyword match:") for r in reasons)


def test_none_when_no_relevant_memory():
    # pattern guideline G20 + no keyword overlap with the (G12) memory
    vc = _classes([_entry("P1", evidence="G20 -- x")])
    items = ma.build_advice_items(vc, _patterns({"P1": P1_DESC}), [_mem()], "ucd_ch")
    it = items[0]
    assert it["advice_strength"] == "none"
    assert it["memory_matches"] == []
    assert it["advice_summary"].startswith("No relevant")


def test_empty_memory_all_none():
    vc = _classes([_entry("P5"), _entry("P1", evidence="G20 -- x")])
    items = ma.build_advice_items(vc, _patterns({"P5": P5_DESC, "P1": P1_DESC}), [], "ucd_ch")
    assert all(i["advice_strength"] == "none" for i in items)


def test_missing_memory_file_loads_as_empty(tmp_path):
    missing = tmp_path / "missing-memory.jsonl"
    assert ma.load_memory_or_empty(missing) == []


def test_missing_memory_file_cli_writes_none_advice(tmp_path):
    patterns = tmp_path / "patterns.json"
    classes = tmp_path / "classes.json"
    out = tmp_path / "memory_advice.json"
    patterns.write_text(json.dumps(_patterns({"P5": P5_DESC})), encoding="utf-8")
    classes.write_text(json.dumps(_classes([_entry("P5")])), encoding="utf-8")
    ma.main([
        "--patterns", str(patterns),
        "--classes", str(classes),
        "--memory", str(tmp_path / "missing-memory.jsonl"),
        "--out", str(out),
        "--setting", "ucd_ch",
    ])
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["advice"][0]["advice_strength"] == "none"
    assert report["advice"][0]["ai_classification_changed"] is False


# ---------------------------------------------------------------------------
# Conflict surfacing (never auto-resolved)
# ---------------------------------------------------------------------------

def test_conflicting_memory_surfaced():
    a = _mem(memory_id="HJM-ucd_ch-P5", sig="aaaaaaaaaaaaaaa1",
             classification="Substantial Variability", conflict="needs_adjudication")
    b = _mem(memory_id="HJM-ucd_ch-P8", sig="aaaaaaaaaaaaaaa2",
             classification="Occasional Variability", conflict="needs_adjudication")
    vc = _classes([_entry("P5")])
    items = ma.build_advice_items(vc, _patterns({"P5": P5_DESC}), [a, b], "ucd_ch")
    it = items[0]
    assert it["advice_strength"] == "conflicting"
    assert it["has_conflicting_memory"] is True
    assert it["conflict_note"]
    assert all(mm.get("match_warning") == "conflicting_human_judgments"
               for mm in it["memory_matches"])


# ---------------------------------------------------------------------------
# Keyword extraction (deterministic)
# ---------------------------------------------------------------------------

def test_keywords_deterministic():
    kws = ma._keywords_from("The inclusion of 'Gefen System' and Marketing data.")
    assert "Gefen System" in kws
    assert "Marketing" in kws
    assert "The" not in kws  # stopword


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def test_report_validates_against_schema():
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        print("    (skipped: jsonschema not installed)")
        return
    schema = json.loads(ADVICE_SCHEMA.read_text(encoding="utf-8"))
    vc = _classes([_entry("P5"), _entry("P1", evidence="G20 -- x")])
    prov = {"source_memory_file": "m.jsonl",
            "source_agent4_files": {"deviation_patterns": "dp.json", "variability_classes": "vc.json"}}
    items = ma.build_advice_items(vc, _patterns({"P5": P5_DESC, "P1": P1_DESC}),
                                  [_mem()], "ucd_ch", provenance=prov)
    report = ma.generate_report(items, "ucd_ch", prov)
    Draft7Validator(schema).validate(report)


def test_default_provenance_is_schema_valid():
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        print("    (skipped: jsonschema not installed)")
        return
    schema = json.loads(ADVICE_SCHEMA.read_text(encoding="utf-8"))
    vc = _classes([{"pattern_id": "P9"}])
    items = ma.build_advice_items(vc, _patterns({"P9": "Unknown fragment"}), [], "ucd_ch")
    report = ma.generate_report(items, "ucd_ch", items[0]["provenance"])
    Draft7Validator(schema).validate(report)


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
