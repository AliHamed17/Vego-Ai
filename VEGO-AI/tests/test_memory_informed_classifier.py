"""
Minimal tests for the Memory-Informed Classifier (Milestone 4B-1, deterministic).

Runs with no third-party dependency:
    python tests/test_memory_informed_classifier.py
Also discoverable by pytest:
    pytest tests/test_memory_informed_classifier.py

Most important properties proven: the baseline is NEVER changed, the original
classification is preserved verbatim, and only "strong disagreement" yields a
parallel differing classification (flagged for human review).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "framework"))

import memory_informed_classifier as mic  # noqa: E402

SCHEMA = ROOT / "schemas" / "memory_informed_comparison.schema.json"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _entry(pid="P5", classification="Substantial Variability", confidence="Medium",
           rhr=False, flag=False):
    return {"pattern_id": pid, "classification": classification, "confidence": confidence,
            "requires_human_review": rhr, "flag_for_guidelines_update": flag,
            "evidence": "G12 -- x", "justification": "j"}


def _classes(entries):
    return {"domain_identifier": "cheers", "variability_classifications": entries}


def _match(memory_id="HJM-ucd_ch-P5", decision_type="valid_alternative",
           classification="Substantial Variability"):
    return {"memory_id": memory_id,
            "human_decision": {"decision_type": decision_type,
                               "classification": classification, "rationale": "r"}}


def _advice(pid="P5", strength="strong", matches=None, conflict=False, summary="s"):
    return {"advice": [{"pattern_id": pid, "advice_strength": strength,
                        "advice_summary": summary, "memory_matches": matches or [],
                        "has_conflicting_memory": conflict}]}


def _mem(memory_id="HJM-ucd_ch-P5", source_setting="ucd_ch", source_pattern="P5",
         confidence="High"):
    return {"memory_id": memory_id, "confidence": confidence,
            "provenance": {"source_setting": source_setting, "source_pattern_id": source_pattern}}


def _one(vc, adv, mem, setting="ucd_ch"):
    return mic.build_comparison_items(vc, adv, mem, setting)[0]


# ---------------------------------------------------------------------------
# Policy table
# ---------------------------------------------------------------------------

def test_no_memory_keeps_original():
    it = _one(_classes([_entry()]), _advice(strength="none", matches=[]), [])
    assert it["rule_applied"] == "no_memory_keep_original"
    assert it["memory_informed_differs_from_original"] is False
    assert it["memory_informed_classification"]["source"] == "original_agent4"
    assert it["requires_human_review_after_memory"] is False
    assert it["evaluation_leakage_status"] == "none"


def test_weak_keeps_original():
    it = _one(_classes([_entry()]), _advice(strength="weak", matches=[_match()]),
              [_mem()])
    assert it["rule_applied"] == "weak_keep_original"
    assert it["memory_informed_differs_from_original"] is False


def test_moderate_agreement_keeps_original_no_review():
    it = _one(_classes([_entry(classification="Substantial Variability")]),
              _advice(strength="moderate", matches=[_match(classification="Substantial Variability")]),
              [_mem()])
    assert it["rule_applied"] == "moderate_agreement_keep_original"
    assert it["requires_human_review_after_memory"] is False


def test_moderate_disagreement_requires_review_no_change():
    it = _one(_classes([_entry(classification="Substantial Variability")]),
              _advice(strength="moderate", matches=[_match(classification="Occasional Variability")]),
              [_mem()])
    assert it["rule_applied"] == "moderate_disagreement_keep_original_require_review"
    assert it["memory_informed_differs_from_original"] is False
    assert it["requires_human_review_after_memory"] is True
    assert it["memory_informed_classification"]["source"] == "original_agent4"


def test_strong_agreement_keeps_original():
    it = _one(_classes([_entry(classification="Substantial Variability")]),
              _advice(strength="strong", matches=[_match(classification="Substantial Variability")]),
              [_mem()])
    assert it["rule_applied"] == "strong_agreement_keep_original"
    assert it["memory_informed_differs_from_original"] is False
    assert it["requires_human_review_after_memory"] is False


def test_strong_disagreement_proposes_parallel_alternative():
    it = _one(_classes([_entry(classification="Substantial Variability")]),
              _advice(strength="strong", matches=[_match(classification="Occasional Variability")]),
              [_mem(confidence="High")])
    assert it["rule_applied"] == "strong_disagreement_propose_memory_supported_alternative"
    assert it["memory_informed_differs_from_original"] is True
    assert it["memory_informed_classification"]["source"] == "human_memory"
    assert it["memory_informed_classification"]["classification"] == "Occasional Variability"
    assert it["memory_informed_classification"]["confidence"] == "High"
    assert it["requires_human_review_after_memory"] is True
    # baseline original is untouched
    assert it["original_agent4_classification"]["classification"] == "Substantial Variability"
    assert it["ai_behavior_changed_in_baseline"] is False


def test_conflicting_requires_review_no_change():
    matches = [_match(memory_id="HJM-ucd_ch-P5", classification="Substantial Variability"),
               _match(memory_id="HJM-ucd_ch-P8", classification="Occasional Variability")]
    it = _one(_classes([_entry()]),
              _advice(strength="conflicting", matches=matches, conflict=True),
              [_mem("HJM-ucd_ch-P5"), _mem("HJM-ucd_ch-P8", source_pattern="P8")])
    assert it["rule_applied"] == "conflicting_keep_original_require_review"
    assert it["memory_informed_differs_from_original"] is False
    assert it["requires_human_review_after_memory"] is True


def test_ambiguous_requires_review():
    it = _one(_classes([_entry()]),
              _advice(strength="strong",
                      matches=[_match(decision_type="ambiguous", classification="Substantial Variability")]),
              [_mem()])
    assert it["rule_applied"] == "ambiguous_keep_original_require_review"
    assert it["requires_human_review_after_memory"] is True


def test_guideline_update_no_class_flags_review():
    it = _one(_classes([_entry()]),
              _advice(strength="strong",
                      matches=[_match(decision_type="needs_guideline_update", classification=None)]),
              [_mem()])
    assert it["rule_applied"] == "guideline_update_keep_original_flag_review"
    assert it["memory_informed_differs_from_original"] is False
    assert it["requires_human_review_after_memory"] is True


# ---------------------------------------------------------------------------
# Baseline-never-changed invariant (across all patterns)
# ---------------------------------------------------------------------------

def test_baseline_never_changed_and_original_preserved():
    vc = _classes([_entry("P5", classification="Substantial Variability"),
                   _entry("P6", classification="Occasional Variability")])
    adv = {"advice": [
        {"pattern_id": "P5", "advice_strength": "strong",
         "memory_matches": [_match(classification="Occasional Variability")], "has_conflicting_memory": False},
        {"pattern_id": "P6", "advice_strength": "none", "memory_matches": [], "has_conflicting_memory": False},
    ]}
    items = mic.build_comparison_items(vc, adv, [_mem()], "ucd_ch")
    assert all(it["ai_behavior_changed_in_baseline"] is False for it in items)
    by_pid = {it["pattern_id"]: it for it in items}
    assert by_pid["P5"]["original_agent4_classification"]["classification"] == "Substantial Variability"
    assert by_pid["P6"]["original_agent4_classification"]["classification"] == "Occasional Variability"


# ---------------------------------------------------------------------------
# Evaluation-leakage status
# ---------------------------------------------------------------------------

def test_leakage_same_pattern():
    it = _one(_classes([_entry("P5")]),
              _advice("P5", "strong", [_match(memory_id="HJM-ucd_ch-P5", classification="Occasional Variability")]),
              [_mem("HJM-ucd_ch-P5", source_setting="ucd_ch", source_pattern="P5")])
    assert it["evaluation_leakage_status"] == "same_pattern_memory_used"


def test_leakage_same_setting():
    it = _one(_classes([_entry("P5")]),
              _advice("P5", "strong", [_match(memory_id="HJM-ucd_ch-P8", classification="Occasional Variability")]),
              [_mem("HJM-ucd_ch-P8", source_setting="ucd_ch", source_pattern="P8")])
    assert it["evaluation_leakage_status"] == "same_setting_memory_used"


def test_leakage_cross_setting():
    it = _one(_classes([_entry("P5")]),
              _advice("P5", "strong", [_match(memory_id="HJM-cd_ch-P5", classification="Occasional Variability")]),
              [_mem("HJM-cd_ch-P5", source_setting="cd_ch", source_pattern="P5")])
    assert it["evaluation_leakage_status"] == "cross_setting_memory_used"


# ---------------------------------------------------------------------------
# Provenance / trace fields
# ---------------------------------------------------------------------------

def test_policy_version_and_decision_trace_present():
    it = _one(_classes([_entry()]), _advice(strength="strong", matches=[_match()]), [_mem()])
    assert it["policy_version"] == "memory-informed-classifier-v1"
    assert it["mode"] == "experimental"
    assert "baseline_output_not_modified" in it["decision_trace"]
    assert any(t.startswith("rule=") for t in it["decision_trace"])


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def test_report_validates_against_schema():
    from jsonschema import Draft7Validator
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    vc = _classes([_entry("P5", classification="Substantial Variability"),
                   _entry("P1", classification="Occasional Variability")])
    adv = {"advice": [
        {"pattern_id": "P5", "advice_strength": "strong",
         "memory_matches": [_match(classification="Occasional Variability")], "has_conflicting_memory": False},
        {"pattern_id": "P1", "advice_strength": "none", "memory_matches": [], "has_conflicting_memory": False},
    ]}
    items = mic.build_comparison_items(vc, adv, [_mem()], "ucd_ch")
    prov = {"source_variability_classes": "vc.json", "source_memory_advice": "adv.json",
            "source_memory": "mem.jsonl"}
    report = mic.generate_report(items, "ucd_ch", prov)
    Draft7Validator(schema).validate(report)


def test_schema_rejects_missing_nested_memory_advice_fields():
    from jsonschema import Draft7Validator
    from jsonschema.exceptions import ValidationError

    from vego_hlayer.contracts import ValidationError as ContractValidationError

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    item = _one(_classes([_entry()]), _advice(strength="none", matches=[]), [])
    item["memory_advice"].pop("advice_strength")
    prov = {
        "source_variability_classes": "vc.json",
        "source_memory_advice": "adv.json",
        "source_memory": "mem.jsonl",
    }
    try:
        report = mic.generate_report([item], "ucd_ch", prov)
        Draft7Validator(schema).validate(report)
    except (ValidationError, ContractValidationError):
        return
    raise AssertionError("schema accepted memory_advice without advice_strength")


def test_schema_rejects_missing_nested_parallel_classification_fields():
    from jsonschema import Draft7Validator
    from jsonschema.exceptions import ValidationError

    from vego_hlayer.contracts import ValidationError as ContractValidationError

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    item = _one(_classes([_entry()]), _advice(strength="none", matches=[]), [])
    item["memory_informed_classification"].pop("source")
    prov = {
        "source_variability_classes": "vc.json",
        "source_memory_advice": "adv.json",
        "source_memory": "mem.jsonl",
    }
    try:
        report = mic.generate_report([item], "ucd_ch", prov)
        Draft7Validator(schema).validate(report)
    except (ValidationError, ContractValidationError):
        return
    raise AssertionError("schema accepted a parallel classification without source")


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
