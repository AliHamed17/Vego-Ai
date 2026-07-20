from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SCRIPT = SCRIPTS / "build_hlayer_program_overview.py"
SPEC = importlib.util.spec_from_file_location("build_hlayer_program_overview", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def fixture_root(tmp_path: Path) -> Path:
    root = tmp_path / "generated"
    # Old-schema iteration (iter_001): no manifest, legacy metric names, no ALL key.
    write_json(
        root / "hlayer_iterations" / "iter_001" / "exp007-summary.json",
        {
            "results": {
                "ucd_ch": [
                    {
                        "mode": "threshold_sev2",
                        "load_vs_every_decision": 0.8,
                        "weighted_severity_coverage": 0.95,
                        "high_severity_coverage": 1.0,
                        "efficiency": 1.19,
                    }
                ]
            }
        },
    )
    # New-schema iteration (iter_002): manifest + ALL pooled rows + bundled metrics.
    write_json(
        root / "hlayer_iterations" / "iter_002" / "exp007-summary.json",
        {
            "results": {
                "ALL": [
                    {
                        "mode": "threshold_sev2",
                        "event_load_vs_every_decision": 0.799,
                        "weighted_severity_coverage": 0.96,
                        "high_severity_coverage": 1.0,
                        "efficiency": 1.202,
                        "bundled_load": 0.7,
                        "bundled_efficiency": 1.37,
                    },
                    {"mode": "silent", "event_load_vs_every_decision": 0.0},
                ]
            }
        },
    )
    write_json(
        root / "hlayer_iterations" / "iter_002" / "iteration_manifest.json",
        {"iteration": 2, "iteration_kind": "reliability_only", "verdict": "NEUTRAL", "run_id": "r2"},
    )
    # Non-iteration directory must be ignored.
    (root / "hlayer_iterations" / "quarantine_iter_001_x").mkdir(parents=True)
    write_json(
        root / "hlayer_suite_manifest.json",
        {
            "run_id": "suite-run",
            "generated_at": "t",
            "experiments": [{"experiment": "exp006"}, {"experiment": "exp007"}],
            "normalized_sha256": "abc",
            "claim_boundary": "gate sentence",
        },
    )
    write_json(
        root / "hlayer_conformance" / "manifest.json",
        {
            "passed": True,
            "run_id": "conf-run",
            "suite_version": "1.0",
            "experiments": [{"experiment_id": "EXP-013"}],
            "live_shadow_authorized": False,
            "decision_snapshot_program_mode": "offline_only",
        },
    )
    write_json(
        root / "hlayer_program_validation" / "latest.json",
        {"status": "PASS", "checks_passed": 8, "failures": []},
    )
    return root


def run_main(tmp_path: Path, monkeypatch) -> Path:
    root = fixture_root(tmp_path)
    monkeypatch.setattr(MODULE, "output_root", lambda: root)
    monkeypatch.setattr(MODULE, "OUT", root / "hlayer_program_overview")
    monkeypatch.setattr(
        MODULE,
        "load_exp005_gate",
        lambda: {
            "counts": {"generalization_safe_valid_label_count": 0},
            "snapshot_sha256": "0" * 64,
        },
    )
    monkeypatch.setattr(
        MODULE,
        "decision_snapshot",
        lambda: {"present": True, "status": "recorded", "offline_only": True},
    )
    assert MODULE.main() == 0
    return root / "hlayer_program_overview"


def test_overview_joins_all_sections(tmp_path, monkeypatch) -> None:
    out = run_main(tmp_path, monkeypatch)
    overview = json.loads((out / "program_overview.json").read_text(encoding="utf-8"))
    assert overview["replay_suite"]["present"] is True
    assert overview["conformance_suite"]["passed"] is True
    assert overview["program_validation"]["status"] == "PASS"
    assert [record["iteration"] for record in overview["iterations"]] == ["iter_001", "iter_002"]
    assert overview["iterations"][0]["has_manifest"] is False
    assert overview["iterations"][1]["verdict"] == "NEUTRAL"
    assert "no accuracy" in overview["claim_scope"].lower()


def test_trajectory_alias_mapping_and_csv(tmp_path, monkeypatch) -> None:
    out = run_main(tmp_path, monkeypatch)
    with (out / "metric_trajectories.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    by_iter = {
        (row["iteration"], row["mode"]): row
        for row in rows
    }
    old = by_iter[("iter_001", "threshold_sev2")]
    # Legacy alias load_vs_every_decision must land in the canonical event_load column.
    assert old["event_load"] == "0.8"
    assert old["bundled_load"] == ""  # absent in old schema stays blank, never guessed
    new = by_iter[("iter_002", "threshold_sev2")]
    assert new["event_load"] == "0.799"
    assert new["bundled_efficiency"] == "1.37"
    assert new["verdict"] == "NEUTRAL"


def test_markdown_carries_gate_and_boundary(tmp_path, monkeypatch) -> None:
    out = run_main(tmp_path, monkeypatch)
    text = (out / "program_overview.md").read_text(encoding="utf-8")
    assert "EXP-005 has 0 validated generalization-safe expert labels" in text
    assert "creates no evidence" in text
    assert "| iter_002 | reliability_only | NEUTRAL |" in text


def test_missing_sections_reported_not_fatal(tmp_path, monkeypatch) -> None:
    root = tmp_path / "generated"
    (root / "hlayer_iterations").mkdir(parents=True)
    monkeypatch.setattr(MODULE, "output_root", lambda: root)
    monkeypatch.setattr(MODULE, "OUT", root / "hlayer_program_overview")
    monkeypatch.setattr(
        MODULE,
        "load_exp005_gate",
        lambda: {"counts": {"generalization_safe_valid_label_count": 0}, "snapshot_sha256": "0" * 64},
    )
    monkeypatch.setattr(
        MODULE, "decision_snapshot", lambda: {"present": False, "status": "missing", "offline_only": True}
    )
    assert MODULE.main() == 0
    overview = json.loads(
        (root / "hlayer_program_overview" / "program_overview.json").read_text(encoding="utf-8")
    )
    assert overview["replay_suite"] == {"present": False}
    assert overview["conformance_suite"] == {"present": False}
    assert overview["iterations"] == []
