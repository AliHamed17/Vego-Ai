#!/usr/bin/env python3
"""Fast, resumable terminal tool for real EXP-005 expert labeling.

This does not label anything itself. It presents each blind-sheet pattern to
a human reviewer one at a time, asks for the same fields the expert-labeling
protocol requires (docs/research/expert-labeling-protocol.md), and writes a
filled sheet in the exact schema build-exp005-label-review.ps1's
-FilledLabelsSheet expects. Progress is saved after every row, so the
reviewer can quit (q) and resume later without losing work.

Usage:
    python scripts/exp005_interactive_labeler.py
    python scripts/exp005_interactive_labeler.py --reviewer-id expert_01
    python scripts/exp005_interactive_labeler.py --input <blind.csv> --output <filled.csv>
"""

from __future__ import annotations

import argparse
import csv
import sys
import textwrap
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = (
    ROOT / "reports/generated/exp005_label_review/exp005_label_review_blind.csv"
)
DEFAULT_OUTPUT = (
    ROOT / "reports/generated/exp005_label_review/exp005_label_review_filled.csv"
)

ALLOWED_LABELS = (
    "Substantial Variability",
    "Occasional Variability",
    "Undetermined / Needs Review",
)

CONFIDENCE_SHORTCUTS = {"h": "High", "m": "Medium", "l": "Low"}

LABEL_FIELDS = (
    "expert_label",
    "expert_rationale",
    "reviewer_id",
    "review_date",
    "confidence",
    "notes",
)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    return fieldnames, rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tmp_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    tmp_path.replace(path)


def is_labeled(row: dict[str, str]) -> bool:
    return row.get("expert_label", "").strip() in ALLOWED_LABELS


def wrap(text: str, width: int = 92, indent: str = "    ") -> str:
    if not text:
        return indent + "(none)"
    return textwrap.fill(text, width=width, initial_indent=indent, subsequent_indent=indent)


def print_row(row: dict[str, str], index: int, total: int) -> None:
    cases = [c for c in row.get("affected_cases", "").split(";") if c.strip()]
    print()
    print("=" * 96)
    print(
        f"[{index}/{total}] {row.get('review_row_id', '?')}  "
        f"(priority {row.get('review_priority', '?')}, rank {row.get('exp005_priority_rank', '?')})"
    )
    print("-" * 96)
    print(f"  Setting:            {row.get('setting', '')}")
    print(f"  Pattern kind:       {row.get('pattern_kind', '')}")
    print(f"  Pattern strength:   {row.get('pattern_strength', '')}")
    print(f"  Related guideline:  {row.get('related_guideline_id', '') or '(none)'}")
    print(f"  Affected cases:     {len(cases)} case(s): {', '.join(cases) if len(cases) <= 12 else ', '.join(cases[:12]) + ', ...'}")
    print("  Description:")
    print(wrap(row.get("pattern_description", "")))
    print("=" * 96)


def prompt_label() -> str | None:
    print("  Expert label:")
    for i, label in enumerate(ALLOWED_LABELS, start=1):
        print(f"    {i}) {label}")
    print("    s) Skip this row for now")
    print("    q) Save progress and quit")
    while True:
        choice = input("  Choice [1/2/3/s/q]: ").strip().lower()
        if choice in {"1", "2", "3"}:
            return ALLOWED_LABELS[int(choice) - 1]
        if choice in {"s", "skip"}:
            return None
        if choice in {"q", "quit"}:
            raise KeyboardInterrupt
        print("  Please enter 1, 2, 3, s, or q.")


def prompt_text(label: str, required: bool) -> str:
    while True:
        value = input(f"  {label}: ").strip()
        if value or not required:
            return value
        print(f"  {label} is required.")


def prompt_confidence() -> str:
    while True:
        raw = input("  Confidence [H]igh/[M]edium/[L]ow (or type your own): ").strip()
        if not raw:
            print("  Confidence is required.")
            continue
        return CONFIDENCE_SHORTCUTS.get(raw.lower(), raw)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--reviewer-id", default=None)
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Blind sheet not found: {args.input}")
        print("Run .\\scripts\\build-exp005-label-review.ps1 first.")
        return 1

    input_fieldnames, input_rows = read_csv(args.input)

    if args.output.exists():
        _, output_rows = read_csv(args.output)
        by_id = {row["review_row_id"]: row for row in output_rows}
        rows = [dict(row, **by_id.get(row["review_row_id"], {})) for row in input_rows]
        print(f"Resuming from {args.output} ({sum(1 for r in rows if is_labeled(r))}/{len(rows)} already labeled).")
    else:
        rows = [dict(row) for row in input_rows]

    fieldnames = input_fieldnames

    reviewer_id = args.reviewer_id
    if not reviewer_id:
        reviewer_id = input(
            "Reviewer ID (stable anonymous identifier, e.g. expert_01): "
        ).strip()
    today = datetime.now().strftime("%Y-%m-%d")

    total = len(rows)
    remaining = [(i, r) for i, r in enumerate(rows) if not is_labeled(r)]
    if not remaining:
        print(f"All {total} rows are already labeled in {args.output}.")
        return 0

    print(f"\n{len(remaining)} of {total} rows need labels. Reviewer: {reviewer_id}, date: {today}.")
    print("Bias/leakage reminder: judge only what's shown here; don't infer Agent 4 or")
    print("memory-informed classifications, and use 'Undetermined / Needs Review' for")
    print("anything ambiguous rather than guessing.\n")

    labeled_this_session = 0
    try:
        for index, (row_index, row) in enumerate(remaining, start=1):
            print_row(row, index, len(remaining))
            label = prompt_label()
            if label is None:
                continue
            rationale = prompt_text("Rationale (short reason for the label)", required=True)
            confidence = prompt_confidence()
            notes = prompt_text("Notes (optional caveats, Enter to skip)", required=False)

            row["expert_label"] = label
            row["expert_rationale"] = rationale
            row["reviewer_id"] = reviewer_id
            row["review_date"] = today
            row["confidence"] = confidence
            row["notes"] = notes
            rows[row_index] = row
            labeled_this_session += 1

            write_csv(args.output, fieldnames, rows)
    except KeyboardInterrupt:
        print("\nSaving progress before exiting...")
        write_csv(args.output, fieldnames, rows)

    labeled_total = sum(1 for r in rows if is_labeled(r))
    print(f"\nSaved {labeled_this_session} label(s) this session.")
    print(f"Progress: {labeled_total}/{total} rows labeled -> {args.output}")
    if labeled_total < total:
        print("Rerun this script to continue where you left off.")
    else:
        print("All rows labeled. Rerun with the same --output to review/edit any row.")
    print(
        "\nWhen ready, run:\n"
        f"  .\\scripts\\build-exp005-label-review.ps1 -FilledLabelsSheet \"{args.output}\" -RunDownstream"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
