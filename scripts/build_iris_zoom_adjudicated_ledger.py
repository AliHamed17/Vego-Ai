#!/usr/bin/env python3
"""Deterministically merge independent July 29 Zoom human reviews.

The immutable preliminary CSV/JSON remain machine-only source artifacts.  This
script reads separate Reviewer A, Reviewer B, and adjudication CSVs.  It emits
an adjudicated CSV/JSON only when both reviewers cover every segment and the
full media timeline, reviewer identities are distinct, and every disagreement
has a completed third-person adjudication.

With the tracked header-only templates, ``--check`` succeeds as a valid pending
interface while the default build exits 2 and writes no adjudicated ledger.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEETING_DIR = ROOT / "docs/research/meetings"
PRELIMINARY_JSON = MEETING_DIR / "2026-07-29-iris-zoom-preliminary-disposition.json"
REVIEWER_A = MEETING_DIR / "2026-07-29-iris-zoom-reviewer-a.csv"
REVIEWER_B = MEETING_DIR / "2026-07-29-iris-zoom-reviewer-b.csv"
ADJUDICATION = MEETING_DIR / "2026-07-29-iris-zoom-adjudication.csv"
DEFAULT_CSV = MEETING_DIR / "2026-07-29-iris-zoom-adjudicated-ledger.csv"
DEFAULT_JSON = MEETING_DIR / "2026-07-29-iris-zoom-adjudicated-ledger.json"

SCHEMA_VERSION = "IrisZoomAdjudicatedLedger-v1"
TIMELINE_ID = "MEDIA-TIMELINE"
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CONTROL_PATTERN = re.compile(r"^(?:R|A|Q)-\d{2,}$")
EXTERNAL_PATTERN = re.compile(r"^EF-\d{2,}$")

REVIEW_FIELDS = (
    "Record_ID",
    "Record_Type",
    "Reviewer_ID",
    "Review_Date",
    "Reviewed_HE",
    "Reviewed_EN",
    "Speaker",
    "Speaker_Confidence",
    "Speaker_Basis",
    "Content_Class",
    "Control_IDs",
    "External_Claim_IDs",
    "Review_Notes",
)
ADJUDICATION_FIELDS = (
    "Segment_ID",
    "Adjudicator_ID",
    "Adjudication_Date",
    "Final_HE",
    "Final_EN",
    "Final_Speaker",
    "Final_Speaker_Confidence",
    "Final_Speaker_Basis",
    "Final_Content_Class",
    "Final_Control_IDs",
    "Final_External_Claim_IDs",
    "Adjudication_Rationale",
    "Decision_Status",
)
OUTPUT_FIELDS = (
    "Segment_ID",
    "Start",
    "End",
    "Machine_HE",
    "Reviewed_HE",
    "Machine_EN",
    "Reviewed_EN",
    "Speaker",
    "Speaker_Confidence",
    "Speaker_Basis",
    "Content_Class",
    "Control_IDs",
    "External_Claim_IDs",
    "Reviewer_A",
    "Reviewer_B",
    "Reviewer_A_Date",
    "Reviewer_B_Date",
    "Disagreement",
    "Adjudicator",
    "Adjudication_Date",
    "Adjudication",
    "Review_Status",
    "Evidence_Link",
)
CONTENT_CLASSES = {
    "Requirement",
    "Action",
    "Decision",
    "Open question",
    "Risk or dependency",
    "External factual claim",
    "Rationale or clarification",
    "Context",
    "Housekeeping",
    "Noise or non-speech",
}
CONFIDENCE_VALUES = {"High", "Medium", "Low", "Unknown"}
CONSENSUS_FIELDS = (
    "Reviewed_HE",
    "Reviewed_EN",
    "Speaker",
    "Speaker_Confidence",
    "Speaker_Basis",
    "Content_Class",
    "Control_IDs",
    "External_Claim_IDs",
)


@dataclass(frozen=True)
class PendingReviews(Exception):
    detail: str

    def __str__(self) -> str:
        return self.detail


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_csv(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(
                f"{relative(path)} header mismatch; expected {','.join(fields)}"
            )
        return list(reader)


def read_preliminary(path: Path = PRELIMINARY_JSON) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    if not isinstance(rows, list) or not rows:
        raise ValueError("preliminary ledger has no rows")
    expected = [f"S-{index:04d}" for index in range(1, len(rows) + 1)]
    if [row.get("Segment_ID") for row in rows] != expected:
        raise ValueError("preliminary ledger IDs are not contiguous")
    return rows


def split_ids(value: str, pattern: re.Pattern[str], field: str) -> list[str]:
    values = [item.strip() for item in value.split(";") if item.strip()]
    invalid = [item for item in values if not pattern.fullmatch(item)]
    if invalid:
        raise ValueError(f"invalid {field}: {', '.join(invalid)}")
    return values


def validate_review(
    rows: list[dict[str, str]],
    preliminary_ids: set[str],
    label: str,
) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    by_id: dict[str, dict[str, str]] = {}
    for row in rows:
        record_id = row["Record_ID"].strip()
        if not record_id or record_id in by_id:
            raise ValueError(f"{label} has blank or duplicate Record_ID {record_id!r}")
        by_id[record_id] = {key: value.strip() for key, value in row.items()}

    expected_ids = preliminary_ids | {TIMELINE_ID}
    extra = sorted(set(by_id) - expected_ids)
    if extra:
        raise ValueError(f"{label} has unknown records: {', '.join(extra)}")
    missing = sorted(expected_ids - set(by_id))
    if missing:
        raise PendingReviews(f"{label} missing {len(missing)}/{len(expected_ids)} records")

    reviewer_ids = {row["Reviewer_ID"] for row in by_id.values()}
    review_dates = {row["Review_Date"] for row in by_id.values()}
    if len(reviewer_ids) != 1 or "" in reviewer_ids:
        raise ValueError(f"{label} must use one non-empty Reviewer_ID")
    if not review_dates or any(not DATE_PATTERN.fullmatch(value) for value in review_dates):
        raise ValueError(f"{label} contains an invalid Review_Date")

    timeline = by_id[TIMELINE_ID]
    if timeline["Record_Type"] != "Full-media" or not timeline["Review_Notes"]:
        raise ValueError(f"{label} MEDIA-TIMELINE needs Full-media type and evidence notes")

    segment_rows = {key: value for key, value in by_id.items() if key != TIMELINE_ID}
    for segment_id, row in segment_rows.items():
        if row["Record_Type"] != "Segment":
            raise ValueError(f"{label} {segment_id} must have Record_Type Segment")
        required = (
            "Reviewed_HE",
            "Reviewed_EN",
            "Speaker",
            "Speaker_Confidence",
            "Speaker_Basis",
            "Content_Class",
        )
        missing_fields = [field for field in required if not row[field]]
        if missing_fields:
            raise ValueError(
                f"{label} {segment_id} missing: {', '.join(missing_fields)}"
            )
        if row["Speaker_Confidence"] not in CONFIDENCE_VALUES:
            raise ValueError(f"{label} {segment_id} invalid speaker confidence")
        if row["Content_Class"] not in CONTENT_CLASSES:
            raise ValueError(f"{label} {segment_id} invalid content class")
        split_ids(row["Control_IDs"], CONTROL_PATTERN, "Control_IDs")
        split_ids(row["External_Claim_IDs"], EXTERNAL_PATTERN, "External_Claim_IDs")
    return segment_rows, timeline


def validate_adjudications(
    rows: list[dict[str, str]],
    disagreement_ids: set[str],
    reviewer_ids: set[str],
) -> dict[str, dict[str, str]]:
    by_id: dict[str, dict[str, str]] = {}
    for raw in rows:
        row = {key: value.strip() for key, value in raw.items()}
        segment_id = row["Segment_ID"]
        if not segment_id or segment_id in by_id:
            raise ValueError("adjudication has blank or duplicate Segment_ID")
        by_id[segment_id] = row
    extra = sorted(set(by_id) - disagreement_ids)
    if extra:
        raise ValueError("adjudication contains non-disagreement rows: " + ", ".join(extra))
    missing = sorted(disagreement_ids - set(by_id))
    if missing:
        raise PendingReviews(f"adjudication missing {len(missing)} disagreement rows")
    adjudicator_ids = {row["Adjudicator_ID"] for row in by_id.values()}
    if disagreement_ids and (
        len(adjudicator_ids) != 1
        or "" in adjudicator_ids
        or bool(adjudicator_ids & reviewer_ids)
    ):
        raise ValueError("adjudicator must be one non-empty third-person identity")
    for segment_id, row in by_id.items():
        required = (
            "Adjudication_Date",
            "Final_HE",
            "Final_EN",
            "Final_Speaker",
            "Final_Speaker_Confidence",
            "Final_Speaker_Basis",
            "Final_Content_Class",
            "Adjudication_Rationale",
        )
        missing_fields = [field for field in required if not row[field]]
        if missing_fields or row["Decision_Status"] != "Adjudicated":
            raise ValueError(f"adjudication {segment_id} is incomplete")
        if not DATE_PATTERN.fullmatch(row["Adjudication_Date"]):
            raise ValueError(f"adjudication {segment_id} has invalid date")
        if row["Final_Speaker_Confidence"] not in CONFIDENCE_VALUES:
            raise ValueError(f"adjudication {segment_id} invalid speaker confidence")
        if row["Final_Content_Class"] not in CONTENT_CLASSES:
            raise ValueError(f"adjudication {segment_id} invalid content class")
        split_ids(row["Final_Control_IDs"], CONTROL_PATTERN, "Final_Control_IDs")
        split_ids(
            row["Final_External_Claim_IDs"],
            EXTERNAL_PATTERN,
            "Final_External_Claim_IDs",
        )
    return by_id


def build_rows(
    preliminary: list[dict[str, str]],
    reviewer_a_rows: list[dict[str, str]],
    reviewer_b_rows: list[dict[str, str]],
    adjudication_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, str]]:
    preliminary_ids = {row["Segment_ID"] for row in preliminary}
    reviewer_a, timeline_a = validate_review(reviewer_a_rows, preliminary_ids, "Reviewer A")
    reviewer_b, timeline_b = validate_review(reviewer_b_rows, preliminary_ids, "Reviewer B")
    reviewer_ids = {
        next(iter({row["Reviewer_ID"] for row in reviewer_a.values()})),
        next(iter({row["Reviewer_ID"] for row in reviewer_b.values()})),
    }
    if len(reviewer_ids) != 2:
        raise ValueError("Reviewer A and Reviewer B identities must be distinct")

    disagreement_ids = {
        segment_id
        for segment_id in preliminary_ids
        if any(
            reviewer_a[segment_id][field] != reviewer_b[segment_id][field]
            for field in CONSENSUS_FIELDS
        )
    }
    adjudications = validate_adjudications(
        adjudication_rows, disagreement_ids, reviewer_ids
    )
    output: list[dict[str, str]] = []
    for source in preliminary:
        segment_id = source["Segment_ID"]
        a_row = reviewer_a[segment_id]
        b_row = reviewer_b[segment_id]
        adjudicated = adjudications.get(segment_id)
        if adjudicated:
            final = {
                "Reviewed_HE": adjudicated["Final_HE"],
                "Reviewed_EN": adjudicated["Final_EN"],
                "Speaker": adjudicated["Final_Speaker"],
                "Speaker_Confidence": adjudicated["Final_Speaker_Confidence"],
                "Speaker_Basis": adjudicated["Final_Speaker_Basis"],
                "Content_Class": adjudicated["Final_Content_Class"],
                "Control_IDs": adjudicated["Final_Control_IDs"],
                "External_Claim_IDs": adjudicated["Final_External_Claim_IDs"],
            }
        else:
            final = {field: a_row[field] for field in CONSENSUS_FIELDS}
        output.append(
            {
                "Segment_ID": segment_id,
                "Start": source["Start"],
                "End": source["End"],
                "Machine_HE": source["Machine_HE"],
                "Reviewed_HE": final["Reviewed_HE"],
                "Machine_EN": source["Machine_EN"],
                "Reviewed_EN": final["Reviewed_EN"],
                "Speaker": final["Speaker"],
                "Speaker_Confidence": final["Speaker_Confidence"],
                "Speaker_Basis": final["Speaker_Basis"],
                "Content_Class": final["Content_Class"],
                "Control_IDs": final["Control_IDs"],
                "External_Claim_IDs": final["External_Claim_IDs"],
                "Reviewer_A": a_row["Reviewer_ID"],
                "Reviewer_B": b_row["Reviewer_ID"],
                "Reviewer_A_Date": a_row["Review_Date"],
                "Reviewer_B_Date": b_row["Review_Date"],
                "Disagreement": "Yes" if adjudicated else "No",
                "Adjudicator": adjudicated["Adjudicator_ID"] if adjudicated else "",
                "Adjudication_Date": (
                    adjudicated["Adjudication_Date"] if adjudicated else ""
                ),
                "Adjudication": (
                    adjudicated["Adjudication_Rationale"]
                    if adjudicated
                    else "Independent reviewer consensus"
                ),
                "Review_Status": "Adjudicated",
                "Evidence_Link": source["Evidence_Link"],
            }
        )
    timeline = {
        "reviewer_a_evidence": timeline_a["Review_Notes"],
        "reviewer_b_evidence": timeline_b["Review_Notes"],
        "reviewer_a_date": timeline_a["Review_Date"],
        "reviewer_b_date": timeline_b["Review_Date"],
        "disagreement_count": str(len(disagreement_ids)),
        "adjudicated_count": str(len(adjudications)),
    }
    return output, timeline


def render_csv(rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def render_json(rows: list[dict[str, str]], timeline: dict[str, str]) -> str:
    sources = (PRELIMINARY_JSON, REVIEWER_A, REVIEWER_B, ADJUDICATION)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_by": relative(Path(__file__).resolve()),
        "human_review_completed": True,
        "evidence_boundary": (
            "Deterministic merge of two complete independent reviews and all "
            "required third-person adjudications; supervisor acceptance remains separate."
        ),
        "sources": [
            {"path": relative(path), "sha256": sha256(path)} for path in sources
        ],
        "coverage": {
            "segment_count": len(rows),
            "timeline_review_status": "Human full-media review complete",
            "unreviewed_media_seconds": 0,
            **timeline,
        },
        "rows": rows,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def expected_outputs() -> tuple[str, str]:
    preliminary = read_preliminary()
    reviewer_a = read_csv(REVIEWER_A, REVIEW_FIELDS)
    reviewer_b = read_csv(REVIEWER_B, REVIEW_FIELDS)
    adjudication = read_csv(ADJUDICATION, ADJUDICATION_FIELDS)
    rows, timeline = build_rows(preliminary, reviewer_a, reviewer_b, adjudication)
    return render_csv(rows), render_json(rows, timeline)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args()
    try:
        csv_text, json_text = expected_outputs()
    except PendingReviews as error:
        outputs_absent = not args.csv.exists() and not args.json.exists()
        print(f"PENDING: {error}; adjudicated outputs absent={outputs_absent}")
        return 0 if args.check and outputs_absent else 2
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1

    expected = ((args.csv, csv_text), (args.json, json_text))
    if args.check:
        matches = all(
            path.exists() and path.read_text(encoding="utf-8") == content
            for path, content in expected
        )
        print(f"{'verified' if matches else 'STALE_OR_MISSING'}: adjudicated ledger")
        return 0 if matches else 1
    for path, content in expected:
        path.write_text(content, encoding="utf-8", newline="")
        print(f"wrote: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
