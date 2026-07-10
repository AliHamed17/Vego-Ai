"""EXP-014: deterministic three-run replay over contract records."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import (
    default_output_dir,
    fixture_dir,
    load_json,
    print_completion,
    relative_path,
    sha256_bytes,
    sha256_file,
    write_experiment_bundle,
)
from .contracts import ObservationRecord, ReviewItem, canonical_json, stable_identifier
from .state_machine import route_observation

EXPERIMENT_ID = "EXP-014"
EXPERIMENT_FOLDER = "EXP-014-replay-determinism"


def _replay_once(descriptor_path: Path, fixture: dict[str, Any]) -> dict[str, Any]:
    source_hash = sha256_file(descriptor_path)
    observations: list[ObservationRecord] = []
    triage_records = []
    reviews: list[ReviewItem] = []
    for event in sorted(
        fixture["events"], key=lambda value: (value["sequence"], value["event_type"])
    ):
        observation = ObservationRecord(
            observation_id=stable_identifier("OBS", event),
            event_type=event["event_type"],
            run_id=fixture["run_id"],
            setting_id=event["setting_id"],
            case_id=event.get("case_id"),
            producer=event["producer"],
            channel=event["channel"],
            sequence=event["sequence"],
            capture_status="reconstructed",
            source_artifact=relative_path(descriptor_path),
            source_sha256=source_hash,
            payload=event["payload"],
        )
        observations.append(observation)
        subject = event["payload"].get("subject", observation.observation_id)
        bundle_key = f"{observation.setting_id}|{observation.case_id or '-'}|{subject}"
        triage = route_observation(
            observation,
            severity=event["severity"],
            trigger_codes=tuple(event.get("trigger_codes", [])),
            dosage_config=fixture["dosage_config"],
            bundle_key=bundle_key,
        )
        triage_records.append(triage)
        if triage.outcome == "promote":
            review_id = stable_identifier(
                "REVIEW", {"triage": triage.triage_id, "bundle": bundle_key}
            )
            reviews.append(
                ReviewItem(
                    review_id=review_id,
                    triage_id=triage.triage_id,
                    evidence_snapshot={"observation": observation.to_dict()},
                    question=f"Review {event['event_type']} for {subject}",
                    risk="high" if event["severity"] >= 3 else "medium",
                    owner_role="course_staff",
                    deduplication_key=bundle_key,
                    due_state="pending",
                    provenance={
                        "source_artifact": relative_path(descriptor_path),
                        "source_sha256": source_hash,
                    },
                )
            )
    normalized = {
        "observations": [record.to_dict() for record in observations],
        "triage": [record.to_dict() for record in triage_records],
        "reviews": [record.to_dict() for record in reviews],
    }
    return {
        "normalized": normalized,
        "hash": sha256_bytes(canonical_json(normalized).encode("utf-8")),
        "review_ids": [review.review_id for review in reviews],
    }


def evaluate(fixtures: Path | None = None) -> dict[str, Any]:
    fixtures = fixtures or fixture_dir(EXPERIMENT_FOLDER)
    descriptor_path = fixtures / "replay.json"
    fixture = load_json(descriptor_path)
    runs = [_replay_once(descriptor_path, fixture) for _ in range(3)]
    normalized_hashes = [run["hash"] for run in runs]
    review_ids = runs[0]["review_ids"]
    acceptance = {
        "three_runs_identical": len(set(normalized_hashes)) == 1,
        "stable_ids_and_ordering": all(
            run["normalized"] == runs[0]["normalized"] for run in runs[1:]
        ),
        "no_duplicate_review_items": len(review_ids) == len(set(review_ids)),
    }
    summary = {
        "experiment": EXPERIMENT_ID,
        "fixture_version": fixture["fixture_version"],
        "replay_count": 3,
        "normalized_hashes": normalized_hashes,
        "review_item_count": len(review_ids),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }
    return {
        "summary": summary,
        "records": runs[0]["normalized"],
        "input_files": (descriptor_path,),
    }


def execute(output_dir: Path | None = None) -> dict[str, Any]:
    result = evaluate()
    output = output_dir or default_output_dir(EXPERIMENT_ID)
    write_experiment_bundle(
        experiment_id=EXPERIMENT_ID,
        experiment_version="1.0",
        config_version="fixture-1.0",
        output_dir=output,
        input_files=result["input_files"],
        payloads={"summary.json": result["summary"], "normalized_records.json": result["records"]},
        metric_schema={
            "replay_count": "count",
            "normalized_hashes": "sha256[]",
            "no_duplicate_review_items": "boolean",
        },
        parameters={"replays": 3, "normalization": "canonical-json-sort-keys"},
    )
    print_completion(EXPERIMENT_ID, output, result["summary"])
    return result
