#!/usr/bin/env python3
"""Build the machine-only July 29 Zoom disposition ledger.

The generated ledger is a deterministic review input, not a human-reviewed
transcript.  It copies the aligned machine text, expands only segment locators
already present in the July 29 requirement/action/question registers, and
leaves all uncited content and speaker attribution for human review.

Examples:
    python scripts/build_iris_zoom_disposition_ledger.py
    python scripts/build_iris_zoom_disposition_ledger.py --check
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEETING_DIR = ROOT / "docs/research/meetings"
SOURCE = MEETING_DIR / "2026-07-29-iris-supervisor-asr.he-en.machine.jsonl"
REQUIREMENTS = MEETING_DIR / "2026-07-29-iris-requirements-register.md"
ACTIONS = MEETING_DIR / "2026-07-29-iris-supervisor-action-register.md"
DEFAULT_CSV = MEETING_DIR / "2026-07-29-iris-zoom-preliminary-disposition.csv"
DEFAULT_JSON = MEETING_DIR / "2026-07-29-iris-zoom-preliminary-disposition.json"

EXPECTED_SEGMENTS = 1195
MEDIA_DURATION_SECONDS = 46 * 60 + 26.283
SCHEMA_VERSION = "IrisZoomPreliminaryDisposition-v1"

CONTROL_ORDER = {
    **{f"R-{index:02d}": index for index in range(1, 20)},
    **{f"A-{index:02d}": 100 + index for index in range(1, 16)},
    **{f"Q-{index:02d}": 200 + index for index in range(1, 11)},
}

FIELDNAMES = (
    "Segment_ID",
    "Start",
    "End",
    "Speaker",
    "Speaker_Confidence",
    "Speaker_Basis",
    "Machine_HE",
    "Reviewed_HE",
    "Machine_EN",
    "Reviewed_EN",
    "Content_Class",
    "Preliminary_Disposition",
    "Control_IDs",
    "External_Claim_IDs",
    "Reviewer_A",
    "Reviewer_B",
    "Disagreement",
    "Adjudication",
    "Review_Status",
    "Evidence_Link",
)

SEGMENT_RANGE = re.compile(
    r"\[S-(\d{4})\]\([^)]*\)"
    r"(?:\s*[\u2013\u2014-]\s*\[S-(\d{4})\]\([^)]*\))?"
)
CONTROL_ROW = re.compile(r"^\|\s*((?:R|A|Q)-\d{2})\s*\|")


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_machine_segments(path: Path = SOURCE) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSON on {relative(path)}:{line_number}") from error
            rows.append(row)

    ids = [row.get("id") for row in rows]
    expected = list(range(1, EXPECTED_SEGMENTS + 1))
    if ids != expected:
        raise ValueError(
            f"expected contiguous segment IDs 1..{EXPECTED_SEGMENTS}; "
            f"found {len(rows)} rows"
        )

    required = (
        "start",
        "end",
        "start_hms",
        "end_hms",
        "text_he_asr",
        "text_en_machine_translation",
    )
    for row in rows:
        missing = [field for field in required if field not in row]
        if missing:
            raise ValueError(f"segment {row['id']} missing fields: {', '.join(missing)}")
    return rows


def expand_segment_locators(text: str) -> set[int]:
    segments: set[int] = set()
    for match in SEGMENT_RANGE.finditer(text):
        first = int(match.group(1))
        last = int(match.group(2) or match.group(1))
        if first > last:
            raise ValueError(f"descending segment locator S-{first:04d}–S-{last:04d}")
        if first < 1 or last > EXPECTED_SEGMENTS:
            raise ValueError(f"out-of-range locator S-{first:04d}–S-{last:04d}")
        segments.update(range(first, last + 1))
    return segments


def read_control_segments(paths: Iterable[Path] = (REQUIREMENTS, ACTIONS)) -> dict[int, list[str]]:
    mapping: dict[int, set[str]] = defaultdict(set)
    seen_controls: set[str] = set()
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            match = CONTROL_ROW.match(line)
            if not match:
                continue
            control_id = match.group(1)
            if control_id not in CONTROL_ORDER:
                raise ValueError(f"unexpected control ID {control_id} in {relative(path)}")
            seen_controls.add(control_id)
            segments = expand_segment_locators(line)
            if not segments:
                raise ValueError(f"{control_id} has no segment locator in {relative(path)}")
            for segment in segments:
                mapping[segment].add(control_id)

    missing = sorted(set(CONTROL_ORDER) - seen_controls, key=CONTROL_ORDER.__getitem__)
    if missing:
        raise ValueError("missing control rows: " + ", ".join(missing))
    return {
        segment: sorted(control_ids, key=CONTROL_ORDER.__getitem__)
        for segment, control_ids in mapping.items()
    }


def content_class(control_ids: list[str]) -> str:
    if any(control.startswith("R-") for control in control_ids):
        return "Requirement"
    if any(control.startswith("A-") for control in control_ids):
        return "Action"
    if any(control.startswith("Q-") for control in control_ids):
        return "Open question"
    # Context is deliberately a placeholder.  It is not a human finding that
    # the segment is non-substantive; Review_Status keeps that boundary clear.
    return "Context"


def build_rows(
    source_rows: list[dict[str, object]] | None = None,
    control_segments: dict[int, list[str]] | None = None,
) -> list[dict[str, str]]:
    source_rows = source_rows if source_rows is not None else read_machine_segments()
    control_segments = (
        control_segments if control_segments is not None else read_control_segments()
    )
    ledger: list[dict[str, str]] = []
    for source_row in source_rows:
        segment_number = int(source_row["id"])
        segment_id = f"S-{segment_number:04d}"
        controls = control_segments.get(segment_number, [])
        is_opening_iris = segment_number <= 6
        ledger.append(
            {
                "Segment_ID": segment_id,
                "Start": str(source_row["start_hms"]),
                "End": str(source_row["end_hms"]),
                "Speaker": "Iris" if is_opening_iris else "Unresolved",
                "Speaker_Confidence": "High" if is_opening_iris else "Unknown",
                "Speaker_Basis": (
                    "Opening visual review documented in provenance manifest"
                    if is_opening_iris
                    else "No automatic diarization; human audiovisual review required"
                ),
                "Machine_HE": str(source_row["text_he_asr"]),
                "Reviewed_HE": "",
                "Machine_EN": str(source_row["text_en_machine_translation"]),
                "Reviewed_EN": "",
                "Content_Class": content_class(controls),
                "Preliminary_Disposition": (
                    "Control-linked" if controls else "Human-review-needed"
                ),
                "Control_IDs": "; ".join(controls),
                "External_Claim_IDs": "",
                "Reviewer_A": "",
                "Reviewer_B": "",
                "Disagreement": "",
                "Adjudication": "",
                "Review_Status": "Machine-only; human review needed",
                "Evidence_Link": (
                    "./2026-07-29-iris-supervisor-bilingual-transcript.he-en.md"
                    f"#s-{segment_number:04d}"
                ),
            }
        )
    return ledger


def render_csv(rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def build_payload(rows: list[dict[str, str]]) -> dict[str, object]:
    source_rows = read_machine_segments()
    cited = sum(bool(row["Control_IDs"]) for row in rows)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": relative(Path(__file__).resolve()),
        "evidence_boundary": (
            "Machine-only preliminary ledger. No bilingual review, full speaker "
            "diarization, adjudication, supervisor acceptance, or external-fact "
            "verification is claimed."
        ),
        "classification_policy": (
            "Only source-register locators create control links. Uncited segments "
            "remain Context placeholders with Human-review-needed disposition."
        ),
        "human_review_completed": False,
        "sources": [
            {
                "path": relative(path),
                "sha256": sha256(path),
            }
            for path in (SOURCE, REQUIREMENTS, ACTIONS)
        ],
        "coverage": {
            "segment_count": len(rows),
            "control_linked_segments": cited,
            "human_review_needed_segments": len(rows),
            "first_segment_start": source_rows[0]["start_hms"],
            "last_segment_end": source_rows[-1]["end_hms"],
            "media_duration": "00:46:26.283",
            "untranscribed_lead_seconds": float(source_rows[0]["start"]),
            "untranscribed_tail_seconds": round(
                MEDIA_DURATION_SECONDS - float(source_rows[-1]["end"]), 3
            ),
            "timeline_review_status": (
                "Machine segment coverage recorded; full-media human review pending"
            ),
        },
        "rows": rows,
    }


def render_json(rows: list[dict[str, str]]) -> str:
    return json.dumps(build_payload(rows), ensure_ascii=False, indent=2) + "\n"


def write_or_check(path: Path, expected: str, check: bool) -> bool:
    if check:
        return path.exists() and path.read_text(encoding="utf-8") == expected
    path.write_text(expected, encoding="utf-8", newline="")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify tracked outputs are byte-for-byte reproducible without writing.",
    )
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args()

    rows = build_rows()
    outputs = {
        args.csv.resolve(): render_csv(rows),
        args.json.resolve(): render_json(rows),
    }
    results = {
        path: write_or_check(path, expected, args.check)
        for path, expected in outputs.items()
    }
    action = "verified" if args.check else "wrote"
    for path, matched in results.items():
        state = action if matched else "STALE_OR_MISSING"
        print(f"{state}: {path} ({len(rows)} segments)")
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
