#!/usr/bin/env python3
"""Freeze explicit human adjudication as the EXP-020 gold-label set.

The script revalidates both immutable reviewer returns, verifies that the
adjudication workbook has not altered either review, and writes gold labels
only from completed human adjudication fields.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import validate_independent_evidence_returns as return_validator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = ROOT / "reports/generated/independent_evidence_v1"
DEFAULT_OUTPUT = DEFAULT_PACKAGE / "gold"
LABELS = {
    "Substantial Variability",
    "Occasional Variability",
    "Undetermined / Needs Review",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def freeze(
    *,
    package: Path,
    reviewer_1_path: Path,
    reviewer_2_path: Path,
    adjudication_path: Path,
    output: Path,
    replace: bool = False,
) -> dict[str, Any]:
    if output.exists() and any(output.iterdir()) and not replace:
        raise ValueError(f"gold output already exists; use a new path or explicit --replace: {output}")
    manifest = json.loads((package / "package_manifest.json").read_text(encoding="utf-8"))
    source_hash = manifest["source"]["sha256"]
    reviewer_1, reviewer_1_hash = return_validator.validate_return(
        reviewer_1_path,
        expected_slot="reviewer_1",
        expected_source_hash=source_hash,
    )
    reviewer_2, reviewer_2_hash = return_validator.validate_return(
        reviewer_2_path,
        expected_slot="reviewer_2",
        expected_source_hash=source_hash,
    )
    if reviewer_1["reviewerId"].casefold() == reviewer_2["reviewerId"].casefold():
        raise ValueError("reviewer IDs must identify two different human reviewers")
    records_1 = {
        record["anonymousItemId"]: record for record in reviewer_1["records"]
    }
    records_2 = {
        record["anonymousItemId"]: record for record in reviewer_2["records"]
    }
    adjudication = read_csv(adjudication_path)
    expected_ids = set(records_1)
    ids = [row.get("anonymous_item_id", "") for row in adjudication]
    if len(adjudication) != 24 or len(set(ids)) != 24 or set(ids) != expected_ids:
        raise ValueError("adjudication workbook must contain each of the 24 items exactly once")

    gold_rows: list[dict[str, str]] = []
    adjudicators: set[str] = set()
    for row in sorted(adjudication, key=lambda item: item["anonymous_item_id"]):
        item_id = row["anonymous_item_id"]
        left, right = records_1[item_id], records_2[item_id]
        protected_pairs = {
            "reviewer_1_label": left["expertLabel"],
            "reviewer_1_rationale": left["expertRationale"],
            "reviewer_1_confidence": left["confidence"],
            "reviewer_1_review_requirement": left["reviewRequirement"],
            "reviewer_1_routing_rationale": left["routingRationale"],
            "reviewer_1_review_priority": left["reviewPriority"],
            "reviewer_2_label": right["expertLabel"],
            "reviewer_2_rationale": right["expertRationale"],
            "reviewer_2_confidence": right["confidence"],
            "reviewer_2_review_requirement": right["reviewRequirement"],
            "reviewer_2_routing_rationale": right["routingRationale"],
            "reviewer_2_review_priority": right["reviewPriority"],
        }
        for field, expected in protected_pairs.items():
            if row.get(field, "") != expected:
                raise ValueError(f"{item_id}: adjudication workbook changed immutable {field}")
        required = (
            "adjudicated_label",
            "adjudicated_rationale",
            "adjudicated_review_requirement",
            "adjudicated_routing_rationale",
            "adjudicated_review_priority",
            "adjudicator_id",
            "adjudication_date",
        )
        missing = [field for field in required if not row.get(field, "").strip()]
        if missing:
            raise ValueError(f"{item_id}: missing human adjudication fields {missing}")
        if row["adjudicated_label"] not in LABELS:
            raise ValueError(f"{item_id}: invalid adjudicated label")
        if row["adjudicated_review_requirement"] not in {
            "Human review required",
            "Automatic handling acceptable",
            "Insufficient context",
        }:
            raise ValueError(f"{item_id}: invalid adjudicated review requirement")
        if row["adjudicated_review_priority"] not in {"Low", "Medium", "High"}:
            raise ValueError(f"{item_id}: invalid adjudicated review priority")
        if return_validator.automated_reviewer_id(row["adjudicator_id"]):
            raise ValueError(f"{item_id}: automated or synthetic adjudicator forbidden")
        adjudicators.add(row["adjudicator_id"])
        gold_rows.append(
            {
                "anonymous_item_id": item_id,
                "gold_label": row["adjudicated_label"],
                "gold_rationale": row["adjudicated_rationale"].strip(),
                "gold_review_requirement": row[
                    "adjudicated_review_requirement"
                ].strip(),
                "gold_routing_rationale": row[
                    "adjudicated_routing_rationale"
                ].strip(),
                "gold_review_priority": row["adjudicated_review_priority"].strip(),
                "adjudicator_id": row["adjudicator_id"].strip(),
                "adjudication_date": row["adjudication_date"].strip(),
                "reviewer_1_return_sha256": reviewer_1_hash,
                "reviewer_2_return_sha256": reviewer_2_hash,
            }
        )

    if replace and output.exists():
        for path in output.iterdir():
            if path.is_file():
                path.unlink()
    output.mkdir(parents=True, exist_ok=True)
    gold_path = output / "gold_labels.csv"
    fields = [
        "anonymous_item_id",
        "gold_label",
        "gold_rationale",
        "gold_review_requirement",
        "gold_routing_rationale",
        "gold_review_priority",
        "adjudicator_id",
        "adjudication_date",
        "reviewer_1_return_sha256",
        "reviewer_2_return_sha256",
    ]
    write_csv(gold_path, gold_rows, fields)
    freeze_manifest = {
        "schemaVersion": "IndependentGoldFreeze-v1",
        "packageManifestSha256": sha256_file(package / "package_manifest.json"),
        "sourceSheetSha256": source_hash,
        "reviewerReturns": {
            "reviewer_1": {
                "reviewerId": reviewer_1["reviewerId"],
                "sha256": reviewer_1_hash,
            },
            "reviewer_2": {
                "reviewerId": reviewer_2["reviewerId"],
                "sha256": reviewer_2_hash,
            },
        },
        "adjudicationWorkbookSha256": sha256_file(adjudication_path),
        "adjudicatorIds": sorted(adjudicators),
        "goldLabelCount": len(gold_rows),
        "goldLabelsSha256": sha256_file(gold_path),
        "immutableRawReturns": True,
        "generalizationSafeCandidateCount": 24,
        "accuracyReportingEligibility": "eligible_with_small_sample_limitations",
        "claimBoundary": (
            "A frozen gold set enables measurement; it does not itself establish "
            "positive accuracy, macro-F1, generalization, effort, or superiority."
        ),
    }
    write_json(output / "gold_freeze_manifest.json", freeze_manifest)
    return freeze_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--reviewer-1", type=Path, required=True)
    parser.add_argument("--reviewer-2", type=Path, required=True)
    parser.add_argument("--adjudication", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    try:
        result = freeze(
            package=args.package,
            reviewer_1_path=args.reviewer_1,
            reviewer_2_path=args.reviewer_2,
            adjudication_path=args.adjudication,
            output=args.output,
            replace=args.replace,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Independent gold freeze: FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
