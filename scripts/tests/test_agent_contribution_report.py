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


def test_report_builds_clone_safe_with_full_contract(tmp_path, monkeypatch) -> None:
    out = tmp_path / "agent_contribution"
    monkeypatch.setattr(MODULE, "OUT", out)
    assert MODULE.main() == 0

    report = json.loads((out / "agent_contribution.json").read_text(encoding="utf-8"))
    components = report["components"]
    assert len(components) >= 8
    ids = {c["id"] for c in components}
    # the paper's four agents and the human-judgment mechanism must always be covered
    assert {"A1", "A2", "A3", "A4", "M1-M3", "M4A/M4B-1"} <= ids
    for comp in components:
        assert comp["purpose"] and comp["delivers"]
        assert comp["verdict"], comp["id"]
        assert comp["why"], comp["id"]
        assert comp["verdict_would_change_if"], comp["id"]
        for sig in comp["measured_signals"]:
            assert sig["source"], f"{comp['id']} signal without source: {sig['name']}"
    # verdicts must never smuggle an accuracy claim while the gate is closed
    assert "no accuracy" in report["claim_scope"].lower()
    counts = report["overall"]["component_verdict_counts"]
    assert sum(counts.values()) == len(components)

    markdown = (out / "agent_contribution.md").read_text(encoding="utf-8")
    assert "The Owner's Question, Answered" in markdown
    assert "Verdict changes if:" in markdown


def test_in_range_is_honest_about_below_floor_values() -> None:
    msg = MODULE.in_range([0.5, 0.9], (0.7, 0.88))
    assert "below the paper range" in msg
    msg_ok = MODULE.in_range([0.8, 0.95], (0.7, 0.88))
    assert "within/above" in msg_ok
    assert MODULE.in_range([], (0.1, 0.2)) == "no measured values"
