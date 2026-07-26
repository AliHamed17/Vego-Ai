#!/usr/bin/env python3
"""Publish a staged, reviewer-safe copy of the independent evidence package."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "reports/generated/independent_evidence_v1"
DEFAULT_DESTINATION = (
    Path.home()
    / "Claude/Projects/vego-ai/Independent-Evidence-2026-07-26"
)
SCHEMA = ROOT / "schemas/independent-evidence-delivery-v1.schema.json"
DELIVERY_DATE = "2026-07-26"
FILES = [
    (
        "docs/research/independent-evidence/README.md",
        "00-Supervisor/EXECUTION_PROTOCOL.md",
        "supervisors",
        "now",
    ),
    (
        "docs/research/independent-evidence/MEASUREMENT_CONTRACT.md",
        "00-Supervisor/MEASUREMENT_CONTRACT.md",
        "supervisors",
        "now",
    ),
    (
        "docs/research/independent-evidence/SUPERVISOR_DECISIONS_REQUIRED.md",
        "00-Supervisor/SUPERVISOR_DECISIONS_REQUIRED.md",
        "supervisors",
        "now",
    ),
    (
        "SUPERVISOR_APPROVAL_CHECKLIST.md",
        "00-Supervisor/SUPERVISOR_APPROVAL_CHECKLIST.md",
        "supervisors",
        "now",
    ),
    (
        "REVIEWER_INSTRUCTIONS.md",
        "Reviewer-1-Calibration/REVIEWER_INSTRUCTIONS.md",
        "reviewer_1",
        "after_supervisor_approval",
    ),
    (
        "reviewer_1_calibration.html",
        "Reviewer-1-Calibration/reviewer_1_calibration.html",
        "reviewer_1",
        "after_supervisor_approval",
    ),
    (
        "REVIEWER_INSTRUCTIONS.md",
        "Reviewer-1-Evaluation-Release-After-Calibration/REVIEWER_INSTRUCTIONS.md",
        "reviewer_1",
        "after_calibration",
    ),
    (
        "reviewer_1_evaluation.html",
        "Reviewer-1-Evaluation-Release-After-Calibration/reviewer_1_evaluation.html",
        "reviewer_1",
        "after_calibration",
    ),
    (
        "REVIEWER_INSTRUCTIONS.md",
        "Reviewer-2-Calibration/REVIEWER_INSTRUCTIONS.md",
        "reviewer_2",
        "after_supervisor_approval",
    ),
    (
        "reviewer_2_calibration.html",
        "Reviewer-2-Calibration/reviewer_2_calibration.html",
        "reviewer_2",
        "after_supervisor_approval",
    ),
    (
        "REVIEWER_INSTRUCTIONS.md",
        "Reviewer-2-Evaluation-Release-After-Calibration/REVIEWER_INSTRUCTIONS.md",
        "reviewer_2",
        "after_calibration",
    ),
    (
        "reviewer_2_evaluation.html",
        "Reviewer-2-Evaluation-Release-After-Calibration/reviewer_2_evaluation.html",
        "reviewer_2",
        "after_calibration",
    ),
]
README = """# Start Here — Independent Evidence

This delivery contains zero expert labels.

1. Supervisors complete `00-Supervisor/`.
2. Release each calibration folder to its named reviewer.
3. Preserve calibration returns and freeze clarified instructions.
4. Only then release the matching evaluation folder.
5. Keep the two reviewers independent.

The private item mapping, Agent 4 labels, memory results, leakage fields, and
16/8 partition are deliberately absent. Accuracy and macro-F1 remain null
until two human returns are adjudicated.
"""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_path(source: Path, relative: str) -> Path:
    candidate = Path(relative)
    return ROOT / candidate if relative.startswith("docs/") else source / candidate


def manifest_for(source: Path, destination: Path) -> dict[str, Any]:
    records = []
    for _source_relative, destination_relative, audience, release_stage in FILES:
        target = destination / destination_relative
        records.append(
            {
                "path": destination_relative,
                "sha256": sha256_file(target),
                "audience": audience,
                "releaseStage": release_stage,
            }
        )
    records.append(
        {
            "path": "README-FIRST.md",
            "sha256": sha256_file(destination / "README-FIRST.md"),
            "audience": "package_owner",
            "releaseStage": "now",
        }
    )
    return {
        "schemaVersion": "IndependentEvidenceDelivery-v1",
        "deliveryDate": DELIVERY_DATE,
        "sourcePackageSha256": sha256_file(source / "package_manifest.json"),
        "files": sorted(records, key=lambda item: item["path"]),
        "privateMappingIncluded": False,
        "suppliedLabels": 0,
        "claimBoundary": (
            "Reviewer-package delivery creates no expert result and permits no "
            "accuracy, generalization, effort, paper-superiority, topology, or "
            "routing-superiority claim."
        ),
    }


def refresh(source: Path, destination: Path) -> dict[str, Any]:
    destination.mkdir(parents=True, exist_ok=True)
    for source_relative, destination_relative, _audience, _release_stage in FILES:
        origin = source_path(source, source_relative)
        if not origin.is_file():
            raise ValueError(f"delivery source is missing: {origin}")
        target = destination / destination_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origin, target)
    (destination / "README-FIRST.md").write_text(
        README,
        encoding="utf-8",
        newline="\n",
    )
    manifest = manifest_for(source, destination)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    ).validate(manifest)
    (destination / "DELIVERY_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def check(source: Path, destination: Path) -> dict[str, Any]:
    manifest_path = destination / "DELIVERY_MANIFEST.json"
    if not manifest_path.is_file():
        raise ValueError("DELIVERY_MANIFEST.json is missing")
    actual = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = manifest_for(source, destination)
    if actual != expected:
        raise ValueError("delivery manifest is stale")
    expected_paths = {item["path"] for item in actual["files"]} | {
        "DELIVERY_MANIFEST.json"
    }
    actual_paths = {
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file()
    }
    if actual_paths != expected_paths:
        raise ValueError(
            f"unexpected delivery paths: {sorted(actual_paths ^ expected_paths)}"
        )
    forbidden = [
        "original_agent4_classification",
        "memory_informed_classification",
        "evaluation_leakage_status",
        "sealed_holdout",
    ]
    for item in actual["files"]:
        path = destination / item["path"]
        if sha256_file(path) != item["sha256"]:
            raise ValueError(f"delivery hash mismatch: {item['path']}")
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                raise ValueError(f"delivery exposes private token {token}: {item['path']}")
    return actual


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--refresh", action="store_true")
    action.add_argument("--check", action="store_true")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    args = parser.parse_args()
    try:
        manifest = (
            refresh(args.source, args.destination)
            if args.refresh
            else check(args.source, args.destination)
        )
        print(
            "Independent evidence delivery: PASS "
            f"({len(manifest['files'])} shareable files, 0 labels, no private mapping)"
        )
    except (OSError, ValueError, json.JSONDecodeError, jsonschema.ValidationError) as exc:
        print(f"Independent evidence delivery: FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
