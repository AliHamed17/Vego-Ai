#!/usr/bin/env python3
"""Validate partial Reviewer A/B CSVs without creating adjudicated evidence.

Exit codes:
    0: both inputs are structurally valid (partial or complete)
    1: at least one input is invalid
    2: inputs are valid but incomplete and --require-complete was requested

This command is read-only. A complete result proves reviewer-file coverage and
schema conformance only; it does not prove reviewer independence, review truth,
adjudication, supervisor acceptance, or full requirements closure.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from build_iris_zoom_adjudicated_ledger import (
    CONFIDENCE_VALUES,
    CONTENT_CLASSES,
    REVIEW_FIELDS,
    REVIEWER_A,
    REVIEWER_B,
    TIMELINE_ID,
)

EXPECTED_SEGMENTS = 1195
SEGMENT_PATTERN = re.compile(r"^S-(\d{4})$")
CONTROL_PATTERN = re.compile(r"^(R|A|Q)-(\d{2,})$")
EXTERNAL_PATTERN = re.compile(r"^EF-(\d{2,})$")
SPEAKER_VALUES = {
    "Iris",
    "Arnon",
    "Ali",
    "Multiple",
    "Unresolved",
    "Non-speech",
}


@dataclass(frozen=True)
class ReviewFinding:
    label: str
    path: Path
    segment_count: int
    timeline_count: int
    reviewer_id: str
    missing_count: int
    errors: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.errors

    @property
    def complete(self) -> bool:
        return self.valid and self.segment_count == EXPECTED_SEGMENTS and self.timeline_count == 1


def parse_list(
    value: str,
    pattern: re.Pattern[str],
    order_key,  # type: ignore[no-untyped-def]
    field: str,
) -> list[str]:
    items = [item.strip() for item in value.split(";") if item.strip()]
    if len(items) != len(set(items)):
        raise ValueError(f"{field} contains duplicate IDs")
    if any(pattern.fullmatch(item) is None for item in items):
        raise ValueError(f"{field} contains an invalid ID")
    if items != sorted(items, key=order_key):
        raise ValueError(f"{field} is not in canonical order")
    return items


def control_order(value: str) -> tuple[int, int]:
    match = CONTROL_PATTERN.fullmatch(value)
    assert match
    return ({"R": 0, "A": 1, "Q": 2}[match.group(1)], int(match.group(2)))


def external_order(value: str) -> int:
    match = EXTERNAL_PATTERN.fullmatch(value)
    assert match
    return int(match.group(1))


def valid_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def read_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    errors: list[str] = []
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != REVIEW_FIELDS:
                return [], ["header does not exactly match the controlled review schema"]
            return list(reader), errors
    except (OSError, UnicodeError, csv.Error) as error:
        return [], [f"cannot read CSV: {error}"]


def validate_review(path: Path, label: str) -> ReviewFinding:
    raw_rows, errors = read_rows(path)
    seen: set[str] = set()
    segment_numbers: list[int] = []
    reviewer_ids: set[str] = set()
    timeline_count = 0

    for line_number, raw in enumerate(raw_rows, start=2):
        row = {key: (value or "").strip() for key, value in raw.items()}
        record_id = row["Record_ID"]
        prefix = f"line {line_number} {record_id or '<blank>'}"
        if not record_id:
            errors.append(f"{prefix}: Record_ID is required")
            continue
        if record_id in seen:
            errors.append(f"{prefix}: duplicate Record_ID")
            continue
        seen.add(record_id)

        reviewer_id = row["Reviewer_ID"]
        if not reviewer_id:
            errors.append(f"{prefix}: Reviewer_ID is required")
        else:
            reviewer_ids.add(reviewer_id)
        if not valid_date(row["Review_Date"]):
            errors.append(f"{prefix}: Review_Date must be a real ISO date")

        if record_id == TIMELINE_ID:
            timeline_count += 1
            if row["Record_Type"] != "Full-media":
                errors.append(f"{prefix}: timeline Record_Type must be Full-media")
            if not row["Review_Notes"]:
                errors.append(f"{prefix}: full-media evidence notes are required")
            continue

        match = SEGMENT_PATTERN.fullmatch(record_id)
        if not match or not 1 <= int(match.group(1)) <= EXPECTED_SEGMENTS:
            errors.append(f"{prefix}: unknown or out-of-range segment ID")
            continue
        segment_numbers.append(int(match.group(1)))
        if row["Record_Type"] != "Segment":
            errors.append(f"{prefix}: Record_Type must be Segment")
        required = (
            "Reviewed_HE",
            "Reviewed_EN",
            "Speaker",
            "Speaker_Confidence",
            "Speaker_Basis",
            "Content_Class",
        )
        for field in required:
            if not row[field]:
                errors.append(f"{prefix}: {field} is required")
        if row["Speaker"] and row["Speaker"] not in SPEAKER_VALUES:
            errors.append(f"{prefix}: Speaker is not an allowed value")
        if row["Speaker_Confidence"] and row["Speaker_Confidence"] not in CONFIDENCE_VALUES:
            errors.append(f"{prefix}: Speaker_Confidence is not allowed")
        if row["Content_Class"] and row["Content_Class"] not in CONTENT_CLASSES:
            errors.append(f"{prefix}: Content_Class is not allowed")
        try:
            parse_list(row["Control_IDs"], CONTROL_PATTERN, control_order, "Control_IDs")
            parse_list(
                row["External_Claim_IDs"],
                EXTERNAL_PATTERN,
                external_order,
                "External_Claim_IDs",
            )
        except ValueError as error:
            errors.append(f"{prefix}: {error}")

    if segment_numbers != sorted(segment_numbers):
        errors.append("segment records are not in ascending Segment_ID order")
    if TIMELINE_ID in seen and raw_rows[-1]["Record_ID"].strip() != TIMELINE_ID:
        errors.append("MEDIA-TIMELINE must be the final record")
    if len(reviewer_ids) > 1:
        errors.append("file contains more than one Reviewer_ID")

    reviewer_id = next(iter(reviewer_ids)) if len(reviewer_ids) == 1 else ""
    return ReviewFinding(
        label=label,
        path=path,
        segment_count=len(set(segment_numbers)),
        timeline_count=timeline_count,
        reviewer_id=reviewer_id,
        missing_count=EXPECTED_SEGMENTS - len(set(segment_numbers)),
        errors=tuple(errors),
    )


def render(finding: ReviewFinding) -> list[str]:
    state = "INVALID" if not finding.valid else "VALID_COMPLETE" if finding.complete else "VALID_PARTIAL"
    lines = [
        f"{finding.label}: {state}",
        f"  path: {finding.path}",
        f"  segments: {finding.segment_count}/{EXPECTED_SEGMENTS}",
        f"  full-media record: {finding.timeline_count}/1",
        f"  reviewer identity: {finding.reviewer_id or 'not yet recorded'}",
        f"  missing segments: {finding.missing_count}",
    ]
    lines.extend(f"  ERROR: {error}" for error in finding.errors)
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-a", type=Path, default=REVIEWER_A)
    parser.add_argument("--reviewer-b", type=Path, default=REVIEWER_B)
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Return 2 when structurally valid inputs are not both complete.",
    )
    args = parser.parse_args()

    findings = (
        validate_review(args.reviewer_a.resolve(), "Reviewer A"),
        validate_review(args.reviewer_b.resolve(), "Reviewer B"),
    )
    errors = [error for finding in findings for error in finding.errors]
    identities = {finding.reviewer_id for finding in findings if finding.reviewer_id}
    recorded_identity_count = sum(bool(finding.reviewer_id) for finding in findings)
    if recorded_identity_count == 2 and len(identities) != 2:
        errors.append("Reviewer A and Reviewer B identities must be distinct")

    for finding in findings:
        print("\n".join(render(finding)))
    if recorded_identity_count == 2 and len(identities) != 2:
        print("CROSS-FILE ERROR: Reviewer identities are not distinct")
    print(
        "Evidence boundary: coverage validation only; no adjudicated truth is emitted."
    )

    if errors:
        return 1
    if args.require_complete and not all(finding.complete for finding in findings):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
