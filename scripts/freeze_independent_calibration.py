#!/usr/bin/env python3
"""Record the required human instruction freeze after reviewer calibration."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = ROOT / "reports/generated/independent_evidence_v1"
AUTOMATED_TOKENS = ("chatgpt", "codex", "synthetic", "automated", "llm", "bot")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected an object: {path}")
    return value


def freeze(
    *,
    pair_report_path: Path,
    output_path: Path,
    disposition: str,
    reviewed_by: str,
    review_date: str,
    rationale: str,
    clarifications: list[str],
) -> dict[str, Any]:
    report = load_json(pair_report_path)
    if report.get("schemaVersion") != "IndependentCalibrationPairReport-v1":
        raise ValueError("unexpected calibration pair-report schema")
    if report.get("status") != "HUMAN_INSTRUCTION_FREEZE_REQUIRED":
        raise ValueError("calibration pair report is not ready for human freeze")
    if report.get("calibrationRowsExcludedFromPerformance") is not True:
        raise ValueError("calibration rows must remain excluded from performance")
    if len(report.get("reviewerReturns", [])) != 2:
        raise ValueError("two calibration return hashes are required")
    if any(
        token in reviewed_by.strip().casefold() for token in AUTOMATED_TOKENS
    ):
        raise ValueError("instruction freeze must be recorded by a human")
    if len(reviewed_by.strip()) < 3:
        raise ValueError("reviewed-by pseudonym or role is required")
    try:
        date.fromisoformat(review_date)
    except ValueError as exc:
        raise ValueError("review date must use YYYY-MM-DD") from exc
    if len(rationale.strip()) < 3:
        raise ValueError("human freeze rationale is required")
    if disposition == "clarified" and not any(item.strip() for item in clarifications):
        raise ValueError("clarified instructions require at least one clarification")
    if disposition == "unchanged" and any(item.strip() for item in clarifications):
        raise ValueError("unchanged instructions cannot include clarifications")

    result = {
        "schemaVersion": "IndependentCalibrationInstructionFreeze-v1",
        "status": "FROZEN_BY_HUMAN",
        "pairReportSha256": sha256_file(pair_report_path),
        "instructionDisposition": disposition,
        "clarifications": [
            item.strip() for item in clarifications if item.strip()
        ],
        "reviewedBy": reviewed_by.strip(),
        "reviewDate": review_date,
        "rationale": rationale.strip(),
        "reviewerReturnSha256": [
            item["sha256"] for item in report["reviewerReturns"]
        ],
        "evaluationReleaseAuthorized": True,
        "calibrationRowsExcludedFromPerformance": True,
        "claimBoundary": (
            "This human record freezes reviewer instructions and authorizes "
            "evaluation-package release. It is not a gold label or performance result."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pair-report",
        type=Path,
        default=DEFAULT_PACKAGE / "validation/calibration/calibration_pair_report.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_PACKAGE
        / "validation/calibration/calibration_instruction_freeze.json",
    )
    parser.add_argument(
        "--disposition",
        choices=("unchanged", "clarified"),
        required=True,
    )
    parser.add_argument("--reviewed-by", required=True)
    parser.add_argument("--review-date", required=True)
    parser.add_argument("--rationale", required=True)
    parser.add_argument("--clarification", action="append", default=[])
    args = parser.parse_args()
    try:
        result = freeze(
            pair_report_path=args.pair_report,
            output_path=args.output,
            disposition=args.disposition,
            reviewed_by=args.reviewed_by,
            review_date=args.review_date,
            rationale=args.rationale,
            clarifications=args.clarification,
        )
        print(
            "Calibration instruction freeze: PASS "
            f"({result['instructionDisposition']}; evaluation release authorized)"
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Calibration instruction freeze: FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
