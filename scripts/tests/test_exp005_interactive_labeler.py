from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/exp005_interactive_labeler.py"
SPEC = importlib.util.spec_from_file_location("exp005_interactive_labeler", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

FIELDNAMES = (
    "review_row_id",
    "exp005_priority_rank",
    "review_priority",
    "setting",
    "pattern_id",
    "pattern_description",
    "affected_cases",
    "related_guideline_id",
    "pattern_strength",
    "pattern_kind",
    "requires_human_review",
    "flag_for_guidelines_update",
    "expert_label",
    "expert_rationale",
    "reviewer_id",
    "review_date",
    "confidence",
    "notes",
)


def write_blind_sheet(path: Path, row_ids: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for i, row_id in enumerate(row_ids):
            writer.writerow(
                {
                    "review_row_id": row_id,
                    "exp005_priority_rank": str(i + 1),
                    "review_priority": "High",
                    "setting": "cd_ch",
                    "pattern_id": f"P{i + 1}",
                    "pattern_description": f"Description for {row_id}",
                    "affected_cases": "1;2;3",
                    "related_guideline_id": "G1",
                    "pattern_strength": "10%",
                    "pattern_kind": "guideline",
                    "requires_human_review": "False",
                    "flag_for_guidelines_update": "False",
                    "expert_label": "",
                    "expert_rationale": "",
                    "reviewer_id": "",
                    "review_date": "",
                    "confidence": "",
                    "notes": "",
                }
            )


def run_with_input(monkeypatch, inputs: list[str], **kwargs) -> int:
    iterator = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda *args: next(iterator))
    monkeypatch.setattr(sys, "argv", ["exp005_interactive_labeler.py"])
    return MODULE.main() if not kwargs else _main_with_args(kwargs)


def _main_with_args(kwargs) -> int:
    args = MODULE.argparse.Namespace(**kwargs)
    parser_parse_args = MODULE.argparse.ArgumentParser.parse_args
    MODULE.argparse.ArgumentParser.parse_args = lambda self, *a, **k: args  # type: ignore[method-assign]
    try:
        return MODULE.main()
    finally:
        MODULE.argparse.ArgumentParser.parse_args = parser_parse_args


def test_labels_all_rows_and_matches_schema(tmp_path: Path, monkeypatch) -> None:
    blind = tmp_path / "blind.csv"
    output = tmp_path / "filled.csv"
    write_blind_sheet(blind, ["a::P1", "a::P2"])

    inputs = [
        "expert_01",  # reviewer id prompt
        "1", "reason one", "h", "",  # row 1: label, rationale, confidence, notes
        "2", "reason two", "m", "note two",  # row 2
    ]
    run_with_input(
        monkeypatch,
        inputs,
        input=blind,
        output=output,
        reviewer_id=None,
    )

    rows = list(csv.DictReader(output.open(encoding="utf-8")))
    assert [r["review_row_id"] for r in rows] == ["a::P1", "a::P2"]
    assert rows[0]["expert_label"] == "Substantial Variability"
    assert rows[0]["expert_rationale"] == "reason one"
    assert rows[0]["reviewer_id"] == "expert_01"
    assert rows[0]["confidence"] == "High"
    assert rows[0]["notes"] == ""
    assert rows[1]["expert_label"] == "Occasional Variability"
    assert rows[1]["confidence"] == "Medium"
    assert rows[1]["notes"] == "note two"
    assert list(rows[0].keys()) == list(FIELDNAMES)


def test_quit_preserves_partial_progress_and_resume_continues(tmp_path: Path, monkeypatch) -> None:
    blind = tmp_path / "blind.csv"
    output = tmp_path / "filled.csv"
    write_blind_sheet(blind, ["a::P1", "a::P2", "a::P3"])

    run_with_input(
        monkeypatch,
        ["expert_02", "1", "first", "h", "", "q"],
        input=blind,
        output=output,
        reviewer_id=None,
    )
    rows = list(csv.DictReader(output.open(encoding="utf-8")))
    assert rows[0]["expert_label"] == "Substantial Variability"
    assert rows[1]["expert_label"] == ""
    assert rows[2]["expert_label"] == ""

    run_with_input(
        monkeypatch,
        ["s", "3", "third", "l", ""],
        input=blind,
        output=output,
        reviewer_id="expert_02",
    )
    rows = list(csv.DictReader(output.open(encoding="utf-8")))
    assert rows[0]["expert_label"] == "Substantial Variability", "resume must not clobber prior labels"
    assert rows[1]["expert_label"] == "", "skip must leave the row unlabeled"
    assert rows[2]["expert_label"] == "Undetermined / Needs Review"
    assert rows[2]["confidence"] == "Low"


def test_no_prompts_when_everything_already_labeled(tmp_path: Path, monkeypatch, capsys) -> None:
    blind = tmp_path / "blind.csv"
    output = tmp_path / "filled.csv"
    write_blind_sheet(blind, ["a::P1"])

    run_with_input(
        monkeypatch,
        ["expert_03", "1", "reason", "h", ""],
        input=blind,
        output=output,
        reviewer_id=None,
    )

    def boom(*_args, **_kwargs):
        raise AssertionError("input() should not be called when nothing remains to label")

    monkeypatch.setattr("builtins.input", boom)
    monkeypatch.setattr(sys, "argv", ["exp005_interactive_labeler.py"])
    _main_with_args({"input": blind, "output": output, "reviewer_id": "expert_03"})
    assert "already labeled" in capsys.readouterr().out
