from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load(name: str, path: Path):  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MERGE = load("build_iris_zoom_adjudicated_ledger", ROOT / "scripts/build_iris_zoom_adjudicated_ledger.py")
VALIDATOR = load("validate_iris_requirements_closure_adjudication", ROOT / "scripts/validate_iris_requirements_closure.py")


def review_rows(reviewer: str, preliminary: list[dict[str, str]]) -> list[dict[str, str]]:
    gap_sha256, gap_count = MERGE.read_timeline_requirements()
    rows = []
    for source in preliminary:
        rows.append(
            {
                "Record_ID": source["Segment_ID"],
                "Record_Type": "Segment",
                "Reviewer_ID": reviewer,
                "Review_Date": "2026-08-02",
                "Reviewed_HE": source["Machine_HE"],
                "Reviewed_EN": source["Machine_EN"],
                "Speaker": "Unresolved",
                "Speaker_Confidence": "Unknown",
                "Speaker_Basis": "Independent audiovisual review",
                "Content_Class": "Context",
                "Control_IDs": source["Control_IDs"],
                "External_Claim_IDs": "",
                "Review_Notes": "Reviewed independently",
            }
        )
    rows.append(
        {
            key: value
            for key, value in zip(
                MERGE.REVIEW_FIELDS,
                (
                    MERGE.TIMELINE_ID,
                    "Full-media",
                    reviewer,
                    "2026-08-02",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    (
                        "Full 46:26.283 audiovisual timeline reviewed. "
                        "Complete_Start_to_End_Review=Yes "
                        f"Media_SHA256={MERGE.VIDEO_SHA256} "
                        f"Gap_Register_SHA256={gap_sha256} "
                        f"Uncovered_Intervals_Reviewed={gap_count}/{gap_count} "
                        "Gap_Classifications=Complete"
                    ),
                ),
                strict=True,
            )
        }
    )
    return rows


def test_tracked_review_templates_are_header_only_and_pending() -> None:
    assert MERGE.read_csv(MERGE.REVIEWER_A, MERGE.REVIEW_FIELDS) == []
    assert MERGE.read_csv(MERGE.REVIEWER_B, MERGE.REVIEW_FIELDS) == []
    assert MERGE.read_csv(MERGE.ADJUDICATION, MERGE.ADJUDICATION_FIELDS) == []
    with pytest.raises(MERGE.PendingReviews):
        MERGE.expected_outputs()
    assert not MERGE.DEFAULT_CSV.exists()
    assert not MERGE.DEFAULT_JSON.exists()


def test_consensus_reviews_merge_without_mutating_preliminary_source() -> None:
    preliminary = MERGE.read_preliminary()[:2]
    rows, timeline = MERGE.build_rows(
        preliminary,
        review_rows("reviewer-a", preliminary),
        review_rows("reviewer-b", preliminary),
        [],
    )

    assert len(rows) == 2
    assert all(row["Review_Status"] == "Adjudicated" for row in rows)
    assert all(row["Adjudication"] == "Independent reviewer consensus" for row in rows)
    assert timeline["disagreement_count"] == "0"


def test_validator_uses_separate_pending_adjudication_and_companion_status() -> None:
    assert len(VALIDATOR.companion_status_rows()) == 44
    assert VALIDATOR.RUNNERS["IRIS-EXP-05"]().passed_for_mode("structure")
    assert not VALIDATOR.RUNNERS["IRIS-EXP-05"]().passed_for_mode("readiness")
    exp06 = VALIDATOR.RUNNERS["IRIS-EXP-06"]()
    assert exp06.passed_for_mode("structure")
    assert not exp06.passed_for_mode("readiness")
    assert any(
        item.name == "deterministic human-review merge interface is valid"
        for item in exp06.checks
    )
