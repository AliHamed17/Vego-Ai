#!/usr/bin/env python3
"""Build the tracked candidate DeploymentSnapshot-v1 for BigUI."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
BIGUI = ROOT / "docs" / "research" / "bigui"
CATALOG = BIGUI / "experiment-catalog-snapshot-v1.json"
RESULT_VIEWS = BIGUI / "experiment-result-views-v1.json"
LIVE_OBSERVATION = BIGUI / "live-deployment-observation-v1.json"
OUTPUT = BIGUI / "deployment-snapshot-v1.json"
SCHEMA = ROOT / "schemas" / "deployment-snapshot-v1.schema.json"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path.relative_to(ROOT)}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def determine_live_status(
    live: dict[str, Any],
    candidate_experiment_count: int,
    candidate_catalog_sha256: str,
) -> str:
    if not live["reachable"]:
        return "unreachable"
    if (
        live["experimentCount"] == candidate_experiment_count
        and live.get("catalogSha256") == candidate_catalog_sha256
    ):
        return "current"
    return "stale"


def build_snapshot() -> dict[str, Any]:
    catalog = load_json(CATALOG)
    result_views = load_json(RESULT_VIEWS)
    live = load_json(LIVE_OBSERVATION)
    if live.get("schemaVersion") != "LiveDeploymentObservation-v1":
        raise ValueError("unexpected live deployment observation schema")
    catalog_sha256 = sha256(CATALOG)
    live_status = determine_live_status(
        live,
        len(catalog["experiments"]),
        catalog_sha256,
    )
    snapshot = {
        "schemaVersion": "DeploymentSnapshot-v1",
        "apiVersion": "v1",
        "publicationState": "candidate",
        "mainBranchRevision": None,
        "catalogSha256": catalog_sha256,
        "resultViewsSha256": sha256(RESULT_VIEWS),
        "deploymentPackageSha256": None,
        "experimentCount": len(catalog["experiments"]),
        "currentAcceptedRunCount": result_views["summary"][
            "currentAcceptedRunCount"
        ],
        "historicalAcceptedRunCount": result_views["summary"][
            "historicalAcceptedRunCount"
        ],
        "metricObservationCount": catalog["runStoreSummary"][
            "metricObservationCount"
        ],
        "acceptedIteration": catalog["programState"][
            "latestAcceptedIteration"
        ],
        "generatedAt": result_views["generatedAt"],
        "deployedAt": None,
        "targetUrl": live["targetUrl"],
        "liveObservation": {
            "observedAt": live["observedAt"],
            "iteration": live["iteration"],
            "experimentCount": live["experimentCount"],
            "catalogSha256": live["catalogSha256"],
            "status": live_status,
            "detail": live["detail"],
        },
        "claimBoundary": (
            "This tracked snapshot describes a deployable candidate. It is not "
            "proof that the production URL was updated. Empirical claims remain "
            "blocked at zero independent safe labels."
        ),
    }
    jsonschema.Draft202012Validator(
        load_json(SCHEMA),
        format_checker=jsonschema.FormatChecker(),
    ).validate(snapshot)
    if snapshot["experimentCount"] != 41:
        raise ValueError("deployment snapshot must publish EXP-000 through EXP-040")
    if snapshot["liveObservation"]["status"] == "current":
        if (
            snapshot["liveObservation"]["catalogSha256"]
            != snapshot["catalogSha256"]
        ):
            raise ValueError("a current live observation must match the catalog hash")
    return snapshot


def write_or_check(payload: dict[str, Any], check: bool) -> None:
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else None
    if current == content:
        return
    if check:
        raise ValueError(f"stale generated output: {OUTPUT.relative_to(ROOT)}")
    OUTPUT.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    try:
        payload = build_snapshot()
        write_or_check(payload, args.check)
        live = payload["liveObservation"]
        print(
            "BigUI deployment snapshot: PASS "
            f"(candidate {payload['experimentCount']} experiments; "
            f"live {live['experimentCount']} / {live['status']})"
        )
        return 0
    except Exception as exc:
        print(f"BigUI deployment snapshot: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
