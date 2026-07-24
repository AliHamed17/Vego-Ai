"""EXP-013: event-contract fidelity and explicit provenance gaps."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import (
    default_output_dir,
    fixture_dir,
    load_json,
    print_completion,
    relative_path,
    sha256_file,
    write_experiment_bundle,
)
from .contracts import ObservationRecord, contract_catalog, stable_identifier
from .state_machine import route_observation

EXPERIMENT_ID = "EXP-013"
EXPERIMENT_FOLDER = "EXP-013-event-contract-fidelity"


def evaluate(fixtures: Path | None = None) -> dict[str, Any]:
    fixtures = fixtures or fixture_dir(EXPERIMENT_FOLDER)
    descriptor_path = fixtures / "events.json"
    descriptors = load_json(descriptor_path)
    records: list[ObservationRecord] = []
    for descriptor in descriptors["events"]:
        source = fixtures / descriptor["source"] if descriptor.get("source") else None
        identity = {key: value for key, value in descriptor.items() if key != "source"}
        records.append(
            ObservationRecord(
                observation_id=stable_identifier("OBS", identity),
                event_type=descriptor["event_type"],
                run_id=descriptors["run_id"],
                setting_id=descriptor["setting_id"],
                case_id=descriptor.get("case_id"),
                producer=descriptor["producer"],
                channel=descriptor["channel"],
                sequence=descriptor["sequence"],
                capture_status=descriptor["capture_status"],
                source_artifact=relative_path(source) if source else None,
                source_sha256=sha256_file(source) if source else None,
                gap_reason=descriptor.get("gap_reason"),
                payload=descriptor.get("payload", {}),
            )
        )

    captured = [record for record in records if record.capture_status != "unobservable"]
    lineage_complete = [
        record for record in captured if record.source_artifact and record.source_sha256
    ]
    gaps = [record for record in records if record.capture_status == "unobservable"]
    e15 = next(record for record in records if record.event_type == "E15")
    e15_triage = route_observation(e15, severity=3, trigger_codes=("evaluation_signal",))
    explicit_gap_types = sorted(record.event_type for record in gaps)
    acceptance = {
        "all_records_schema_valid": len(records) == len(descriptors["events"]),
        "captured_lineage_complete": len(lineage_complete) == len(captured),
        "e3_and_e9_gaps_explicit": {"E3", "E9"}.issubset(explicit_gap_types),
        "e15_parked_evaluation_only": (
            e15_triage.outcome == "park" and e15_triage.budget_state == "evaluation_only"
        ),
    }
    summary = {
        "experiment": EXPERIMENT_ID,
        "fixture_version": descriptors["fixture_version"],
        "total_records": len(records),
        "schema_valid_records": len(records),
        "captured_or_reconstructed_records": len(captured),
        "captured_records_with_lineage": len(lineage_complete),
        "explicit_gap_event_types": explicit_gap_types,
        "e15_triage": e15_triage.to_dict(),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }
    return {
        "summary": summary,
        "records": [record.to_dict() for record in records],
        "catalog": contract_catalog(),
        "input_files": tuple(
            [descriptor_path]
            + sorted(
                path for path in fixtures.rglob("*") if path.is_file() and path != descriptor_path
            )
        ),
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
        payloads={
            "summary.json": result["summary"],
            "records.json": result["records"],
            "contract_catalog.json": result["catalog"],
        },
        metric_schema={
            "schema_valid_records": "count",
            "captured_records_with_lineage": "count",
            "explicit_gap_event_types": "event_type[]",
            "e15_parked_evaluation_only": "boolean",
        },
        parameters={"event_scope": "E1-E15", "e15_route": "evaluation_only"},
    )
    print_completion(EXPERIMENT_ID, output, result["summary"])
    return result
