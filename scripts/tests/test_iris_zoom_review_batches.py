from __future__ import annotations

import csv
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "validate_iris_zoom_review_batches.py"
SPEC = importlib.util.spec_from_file_location("validate_iris_zoom_review_batches", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def row(segment: int, reviewer: str = "reviewer-a") -> dict[str, str]:
    return {
        "Record_ID": f"S-{segment:04d}",
        "Record_Type": "Segment",
        "Reviewer_ID": reviewer,
        "Review_Date": "2026-08-02",
        "Reviewed_HE": "טקסט",
        "Reviewed_EN": "text",
        "Speaker": "Unresolved",
        "Speaker_Confidence": "Unknown",
        "Speaker_Basis": "Independent audiovisual review",
        "Content_Class": "Context",
        "Control_IDs": "R-01; A-01; Q-01",
        "External_Claim_IDs": "EF-01",
        "Review_Notes": "batch review",
    }


def timeline(reviewer: str) -> dict[str, str]:
    result = {field: "" for field in MODULE.REVIEW_FIELDS}
    result.update(
        {
            "Record_ID": MODULE.TIMELINE_ID,
            "Record_Type": "Full-media",
            "Reviewer_ID": reviewer,
            "Review_Date": "2026-08-02",
            "Review_Notes": "Full media and ASR edge gaps reviewed",
        }
    )
    return result


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MODULE.REVIEW_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_controlled_header_only_templates_are_valid_partial() -> None:
    a = MODULE.validate_review(MODULE.REVIEWER_A, "Reviewer A")
    b = MODULE.validate_review(MODULE.REVIEWER_B, "Reviewer B")

    assert a.valid and b.valid
    assert not a.complete and not b.complete
    assert a.segment_count == b.segment_count == 0
    assert a.missing_count == b.missing_count == 1195


def test_partial_priority_batches_validate_without_requiring_contiguous_ids(tmp_path: Path) -> None:
    path = tmp_path / "review.csv"
    write_csv(path, [row(53), row(54), row(891)])

    finding = MODULE.validate_review(path, "Reviewer A")

    assert finding.valid
    assert finding.segment_count == 3
    assert finding.missing_count == 1192


def test_batch_validator_rejects_order_duplicates_and_values(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    bad = row(2)
    bad["Speaker"] = "Likely Iris"
    write_csv(path, [bad, row(1), row(1)])

    finding = MODULE.validate_review(path, "Reviewer A")

    assert not finding.valid
    assert any("allowed value" in error for error in finding.errors)
    assert any("ascending" in error for error in finding.errors)
    assert any("duplicate Record_ID" in error for error in finding.errors)


def test_cli_fails_distinct_identity_and_complete_gates(tmp_path: Path) -> None:
    a_path = tmp_path / "a.csv"
    b_path = tmp_path / "b.csv"
    write_csv(a_path, [row(1, "same-reviewer")])
    write_csv(b_path, [row(1, "same-reviewer")])
    same = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--reviewer-a",
            str(a_path),
            "--reviewer-b",
            str(b_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert same.returncode == 1
    assert "identities are not distinct" in same.stdout

    write_csv(b_path, [row(1, "reviewer-b")])
    incomplete = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--reviewer-a",
            str(a_path),
            "--reviewer-b",
            str(b_path),
            "--require-complete",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert incomplete.returncode == 2
    assert "VALID_PARTIAL" in incomplete.stdout


def test_complete_single_file_requires_all_segments_and_timeline(tmp_path: Path) -> None:
    path = tmp_path / "complete.csv"
    rows = [row(index) for index in range(1, 1196)] + [timeline("reviewer-a")]
    write_csv(path, rows)

    finding = MODULE.validate_review(path, "Reviewer A")

    assert finding.valid and finding.complete
    assert finding.segment_count == 1195
    assert finding.timeline_count == 1
