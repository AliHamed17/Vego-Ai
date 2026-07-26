#!/usr/bin/env python3
"""Validate two independent EXP-020 reviewer returns without changing them.

The command refuses automated/synthetic reviewer identities, validates all 24
blind items, computes agreement before adjudication, and creates a local
adjudication workbook. It never creates gold labels.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = ROOT / "reports/generated/independent_evidence_v1"
DEFAULT_OUTPUT = ROOT / "reports/generated/independent_evidence_v1/validation"
SCHEMA = ROOT / "schemas/independent-review-return-v1.schema.json"
LABELS = [
    "Substantial Variability",
    "Occasional Variability",
    "Undetermined / Needs Review",
]
AUTOMATED_REVIEWER_TOKENS = {
    "ai",
    "chatgpt",
    "claude",
    "codex",
    "gpt",
    "llm",
    "openai",
    "synthetic",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def automated_reviewer_id(value: str) -> bool:
    normalized = "".join(character.lower() if character.isalnum() else " " for character in value)
    words = set(normalized.split())
    return bool(words & AUTOMATED_REVIEWER_TOKENS)


def validate_return(
    path: Path,
    *,
    expected_slot: str,
    expected_source_hash: str,
) -> tuple[dict[str, Any], str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    ).validate(payload)
    if payload["reviewerSlot"] != expected_slot:
        raise ValueError(
            f"{path.name}: expected {expected_slot}, found {payload['reviewerSlot']}"
        )
    if payload["sourceSheetSha256"] != expected_source_hash:
        raise ValueError(f"{path.name}: source sheet hash does not match the package")
    if automated_reviewer_id(payload["reviewerId"]):
        raise ValueError(f"{path.name}: automated or synthetic reviewer ID is forbidden")
    identifiers = [record["anonymousItemId"] for record in payload["records"]]
    expected = {f"ITEM-{index:02d}" for index in range(1, 25)}
    if len(set(identifiers)) != len(identifiers):
        raise ValueError(f"{path.name}: duplicate anonymous item ID")
    if set(identifiers) != expected:
        missing = sorted(expected - set(identifiers))
        unexpected = sorted(set(identifiers) - expected)
        raise ValueError(
            f"{path.name}: item set mismatch; missing={missing}, unexpected={unexpected}"
        )
    return payload, sha256_file(path)


def cohen_kappa(labels_1: list[str], labels_2: list[str]) -> tuple[float, float | None]:
    return cohen_kappa_for_vocabulary(labels_1, labels_2, LABELS)


def cohen_kappa_for_vocabulary(
    labels_1: list[str],
    labels_2: list[str],
    vocabulary: list[str],
) -> tuple[float, float | None]:
    if len(labels_1) != len(labels_2) or not labels_1:
        raise ValueError("agreement requires two equally sized non-empty label lists")
    total = len(labels_1)
    observed = (
        sum(left == right for left, right in zip(labels_1, labels_2, strict=True))
        / total
    )
    counts_1 = Counter(labels_1)
    counts_2 = Counter(labels_2)
    expected = sum(
        (counts_1[label] / total) * (counts_2[label] / total)
        for label in vocabulary
    )
    if expected == 1:
        return observed, None
    return observed, (observed - expected) / (1 - expected)


def build_gate(package_manifest: dict[str, Any], state: str) -> dict[str, Any]:
    return {
        "schemaVersion": "IndependentEvidenceGate-v1",
        "status": state,
        "candidateRows": package_manifest["counts"]["candidateRows"],
        "reviewerCountRequired": 2,
        "reviewerReturnsValidated": state in {"ADJUDICATION_REQUIRED", "AGREEMENT_COMPLETE"},
        "adjudicationComplete": False,
        "goldLabelsFrozen": False,
        "safeGoldLabelCount": 0,
        "accuracyMetricsComputable": False,
        "macroF1Computable": False,
        "generalizationClaimAllowed": False,
        "humanEffortClaimAllowed": False,
        "paperSuperiorityClaimAllowed": False,
        "nextAction": (
            "Obtain two independent human evaluation returns."
            if state == "HUMAN_INPUT_REQUIRED"
            else "Adjudicate disagreements and freeze the gold-label file."
        ),
        "claimBoundary": (
            "Reviewer-package or agreement readiness is not classification evidence. "
            "All empirical performance fields remain null until human adjudication."
        ),
    }


def readiness(package: Path, output: Path | None) -> dict[str, Any]:
    manifest_path = package / "package_manifest.json"
    if not manifest_path.is_file():
        raise ValueError(f"package manifest is missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    gate = build_gate(manifest, "HUMAN_INPUT_REQUIRED")
    if output is not None:
        write_json(output / "evidence_gate.json", gate)
    return gate


def validate_pair(
    package: Path,
    reviewer_1_path: Path,
    reviewer_2_path: Path,
    output: Path,
) -> dict[str, Any]:
    manifest = json.loads((package / "package_manifest.json").read_text(encoding="utf-8"))
    source_hash = manifest["source"]["sha256"]
    reviewer_1, reviewer_1_hash = validate_return(
        reviewer_1_path,
        expected_slot="reviewer_1",
        expected_source_hash=source_hash,
    )
    reviewer_2, reviewer_2_hash = validate_return(
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
    item_ids = sorted(records_1)
    labels_1 = [records_1[item_id]["expertLabel"] for item_id in item_ids]
    labels_2 = [records_2[item_id]["expertLabel"] for item_id in item_ids]
    observed, kappa = cohen_kappa(labels_1, labels_2)
    routing_1 = [records_1[item_id]["reviewRequirement"] for item_id in item_ids]
    routing_2 = [records_2[item_id]["reviewRequirement"] for item_id in item_ids]
    routing_observed, routing_kappa = cohen_kappa_for_vocabulary(
        routing_1,
        routing_2,
        [
            "Human review required",
            "Automatic handling acceptable",
            "Insufficient context",
        ],
    )
    disagreements = [
        item_id
        for item_id in item_ids
        if records_1[item_id]["expertLabel"] != records_2[item_id]["expertLabel"]
    ]
    seconds_1 = [float(records_1[item_id]["activeSeconds"]) for item_id in item_ids]
    seconds_2 = [float(records_2[item_id]["activeSeconds"]) for item_id in item_ids]
    agreement = {
        "schemaVersion": "IndependentReviewerAgreement-v1",
        "packageVersion": manifest["packageVersion"],
        "sourceSheetSha256": source_hash,
        "reviewerReturns": {
            "reviewer_1": {
                "reviewerId": reviewer_1["reviewerId"],
                "sha256": reviewer_1_hash,
                "completedAt": reviewer_1["completedAt"],
            },
            "reviewer_2": {
                "reviewerId": reviewer_2["reviewerId"],
                "sha256": reviewer_2_hash,
                "completedAt": reviewer_2["completedAt"],
            },
        },
        "itemCount": len(item_ids),
        "agreementCount": len(item_ids) - len(disagreements),
        "disagreementCount": len(disagreements),
        "observedAgreement": round(observed, 6),
        "cohenKappa": None if kappa is None else round(kappa, 6),
        "routingObservedAgreement": round(routing_observed, 6),
        "routingCohenKappa": (
            None if routing_kappa is None else round(routing_kappa, 6)
        ),
        "disagreementItemIds": disagreements,
        "labelDistributions": {
            "reviewer_1": dict(Counter(labels_1)),
            "reviewer_2": dict(Counter(labels_2)),
        },
        "routingDistributions": {
            "reviewer_1": dict(Counter(routing_1)),
            "reviewer_2": dict(Counter(routing_2)),
        },
        "effort": {
            "reviewer_1": {
                "totalSeconds": round(sum(seconds_1), 3),
                "medianSecondsPerItem": round(statistics.median(seconds_1), 3),
                "meanSecondsPerItem": round(statistics.fmean(seconds_1), 3),
            },
            "reviewer_2": {
                "totalSeconds": round(sum(seconds_2), 3),
                "medianSecondsPerItem": round(statistics.median(seconds_2), 3),
                "meanSecondsPerItem": round(statistics.fmean(seconds_2), 3),
            },
        },
        "claimBoundary": (
            "Agreement and annotation time describe this reviewer pair and this "
            "24-item set. They are not classification accuracy or effort reduction."
        ),
    }
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "reviewer_agreement.json", agreement)

    fields = [
        "anonymous_item_id",
        "reviewer_1_label",
        "reviewer_1_rationale",
        "reviewer_1_confidence",
        "reviewer_1_review_requirement",
        "reviewer_1_routing_rationale",
        "reviewer_1_review_priority",
        "reviewer_2_label",
        "reviewer_2_rationale",
        "reviewer_2_confidence",
        "reviewer_2_review_requirement",
        "reviewer_2_routing_rationale",
        "reviewer_2_review_priority",
        "agreement_status",
        "adjudicated_label",
        "adjudicated_rationale",
        "adjudicated_review_requirement",
        "adjudicated_routing_rationale",
        "adjudicated_review_priority",
        "adjudicator_id",
        "adjudication_date",
        "notes",
    ]
    with (output / "adjudication_workbook.csv").open(
        "w",
        encoding="utf-8",
        newline="",
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for item_id in item_ids:
            left, right = records_1[item_id], records_2[item_id]
            writer.writerow(
                {
                    "anonymous_item_id": item_id,
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
                    "agreement_status": (
                        "agree"
                        if left["expertLabel"] == right["expertLabel"]
                        else "disagree"
                    ),
                }
            )
    gate_state = "AGREEMENT_COMPLETE" if not disagreements else "ADJUDICATION_REQUIRED"
    gate = build_gate(manifest, gate_state)
    gate["reviewerAgreement"] = {
        "observedAgreement": agreement["observedAgreement"],
        "cohenKappa": agreement["cohenKappa"],
        "routingObservedAgreement": agreement["routingObservedAgreement"],
        "routingCohenKappa": agreement["routingCohenKappa"],
        "disagreementCount": agreement["disagreementCount"],
    }
    write_json(output / "evidence_gate.json", gate)
    return {"agreement": agreement, "gate": gate}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--reviewer-1", type=Path)
    parser.add_argument("--reviewer-2", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check-gate",
        action="store_true",
        help="Report the current no-label gate without accepting reviewer evidence.",
    )
    args = parser.parse_args()
    try:
        if args.check_gate:
            result = readiness(args.package, args.output)
        else:
            if args.reviewer_1 is None or args.reviewer_2 is None:
                raise ValueError("--reviewer-1 and --reviewer-2 are both required")
            result = validate_pair(
                args.package,
                args.reviewer_1,
                args.reviewer_2,
                args.output,
            )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, json.JSONDecodeError, jsonschema.ValidationError) as exc:
        print(f"Independent return validation: FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
