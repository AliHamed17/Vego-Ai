from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SPEC = importlib.util.spec_from_file_location(
    "build_agent_contribution_report", SCRIPTS / "build_agent_contribution_report.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

EXPECTED_IDS = {"A1", "A2", "A3", "A4", "M1-M3", "M4A/M4B-1"}


def build_report(tmp_path, monkeypatch) -> dict:
    out = tmp_path / "agent_contribution"
    monkeypatch.setattr(MODULE, "OUT", out)
    assert MODULE.main() == 0
    return json.loads((out / "agent_contribution.json").read_text(encoding="utf-8"))


def test_report_builds_with_full_contract(tmp_path, monkeypatch) -> None:
    report = build_report(tmp_path, monkeypatch)
    components = report["components"]
    assert len(components) >= 8
    ids = {c["id"] for c in components}
    # the paper's four agents and the human-judgment mechanism must always be covered
    assert EXPECTED_IDS <= ids
    for comp in components:
        assert comp["purpose"] and comp["delivers"]
        assert comp["verdict"], comp["id"]
        assert comp["category"] in MODULE.CATEGORIES, comp["id"]
        assert comp["why"], comp["id"]
        assert comp["verdict_would_change_if"], comp["id"]
        for sig in comp["measured_signals"]:
            assert sig["source"], f"{comp['id']} signal without source: {sig['name']}"
    # verdicts must never smuggle an accuracy claim while the gate is closed
    assert "no accuracy" in report["claim_scope"].lower()
    # counts must be derived from the explicit per-component category, not string prefixes
    counts = report["overall"]["component_verdict_counts"]
    assert counts["contributing"] == sum(1 for c in components if c["category"] == "contributing")
    assert counts["partial"] == sum(1 for c in components if c["category"] == "partial")
    assert counts["not_yet_measurable_quality"] == sum(
        1 for c in components if c["category"] == "not_yet_measurable"
    )

    out = tmp_path / "agent_contribution"
    markdown = (out / "agent_contribution.md").read_text(encoding="utf-8")
    assert "The Owner's Question, Answered" in markdown
    assert "Verdict changes if:" in markdown


def test_in_range_is_honest_about_below_floor_values() -> None:
    msg = MODULE.in_range([0.5, 0.9], (0.7, 0.88))
    assert "below the paper range" in msg
    msg_ok = MODULE.in_range([0.8, 0.95], (0.7, 0.88))
    assert "within/above" in msg_ok
    assert MODULE.in_range([], (0.1, 0.2)) == "no measured values"


def test_fresh_clone_emits_no_fabricated_signals(tmp_path, monkeypatch) -> None:
    """With every generated/eval input absent, the report must not invent data."""
    empty_eval = tmp_path / "eval_output"
    empty_run = tmp_path / "run_human"
    empty_generated = tmp_path / "generated"
    for d in (empty_eval, empty_run, empty_generated):
        d.mkdir()
    monkeypatch.setattr(MODULE, "EVAL", empty_eval)
    monkeypatch.setattr(MODULE, "RUN_HUMAN", empty_run)
    monkeypatch.setattr(MODULE, "output_root", lambda: empty_generated)
    monkeypatch.setattr(
        MODULE, "load_exp005_gate",
        lambda: (_ for _ in ()).throw(RuntimeError("gate inputs absent")),
    )
    report = build_report(tmp_path, monkeypatch)

    components = {c["id"]: c for c in report["components"]}
    assert EXPECTED_IDS <= set(components)
    # every measured signal must cite a source that is NOT one of the missing
    # generated/eval artifacts - only static references (paper) may remain
    for comp in report["components"]:
        for sig in comp["measured_signals"]:
            src = sig["source"]
            assert not src.startswith("reports/generated/"), (comp["id"], sig["name"])
            assert not src.startswith("VEGO-AI/eval_output"), (comp["id"], sig["name"])
            assert not src.startswith("VEGO-AI/runs"), (comp["id"], sig["name"])
    # no component may claim a positive verdict without data
    for comp in report["components"]:
        assert comp["category"] == "not_yet_measurable", comp["id"]
    # the headline answer must say the question is not answerable here
    assert "NOT ANSWERABLE FROM THIS CHECKOUT" in report["overall"]["answer"]
