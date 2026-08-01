from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/build_iris_zoom_disposition_ledger.py"
SPEC = importlib.util.spec_from_file_location("build_iris_zoom_disposition_ledger", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_machine_source_is_exactly_1195_contiguous_segments() -> None:
    rows = MODULE.read_machine_segments()

    assert len(rows) == 1195
    assert [row["id"] for row in rows] == list(range(1, 1196))
    assert rows[0]["start_hms"] == "00:00:01.060"
    assert rows[-1]["end_hms"] == "00:46:25.010"


def test_current_register_locators_reproduce_audited_910_285_split() -> None:
    mapping = MODULE.read_control_segments()

    assert len(mapping) == 910
    assert 1195 - len(mapping) == 285
    observed_controls = {
        control for controls in mapping.values() for control in controls
    }
    assert observed_controls == set(MODULE.CONTROL_ORDER)


def test_preliminary_ledger_never_infers_human_review() -> None:
    rows = MODULE.build_rows()
    linked = [row for row in rows if row["Control_IDs"]]
    unlinked = [row for row in rows if not row["Control_IDs"]]

    assert len(rows) == 1195
    assert len(linked) == 910
    assert len(unlinked) == 285
    assert all(row["Preliminary_Disposition"] == "Control-linked" for row in linked)
    assert all(
        row["Content_Class"] == "Context"
        and row["Preliminary_Disposition"] == "Human-review-needed"
        for row in unlinked
    )
    assert [row["Speaker"] for row in rows[:6]] == ["Iris"] * 6
    assert all(row["Speaker"] == "Unresolved" for row in rows[6:])
    assert all(
        row["Review_Status"] == "Machine-only; human review needed"
        and not row["Reviewed_HE"]
        and not row["Reviewed_EN"]
        and not row["Reviewer_A"]
        and not row["Reviewer_B"]
        and not row["Adjudication"]
        for row in rows
    )


def test_tracked_outputs_are_byte_reproducible() -> None:
    rows = MODULE.build_rows()

    assert MODULE.DEFAULT_CSV.read_text(encoding="utf-8") == MODULE.render_csv(rows)
    assert MODULE.DEFAULT_JSON.read_text(encoding="utf-8") == MODULE.render_json(rows)
