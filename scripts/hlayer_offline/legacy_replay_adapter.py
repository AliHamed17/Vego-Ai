"""Validated adapter from EXP-006 replay rows to ``ObservationRecord``.

EXP-006 preserves its historical CSV interface for audit compatibility.  This
adapter is the sole boundary into the contract-driven offline flow: it validates
each reconstructed row as an ObservationRecord and makes instrumentation gaps
explicit before EXP-007 performs dosage comparisons.
"""

from __future__ import annotations

import csv
import json
import re
from collections.abc import Iterable
from hashlib import sha256
from pathlib import Path
from typing import Any

from .contracts import ObservationRecord, canonical_json, stable_identifier

EVENT_PREFIX = re.compile(r"^(E(?:[1-9]|1[0-5]))(?:_|$)")


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def event_type_of(legacy_event: str) -> str:
    match = EVENT_PREFIX.match(str(legacy_event or ""))
    if not match:
        raise ValueError(f"legacy event has no E1-E15 prefix: {legacy_event!r}")
    return match.group(1)


def case_id_of(subject_id: str) -> str | None:
    subject = str(subject_id or "")
    return subject.split(":", 1)[1] if subject.startswith("case:") else None


def adapt_reconstructed_row(row: dict[str, Any], *, run_id: str) -> ObservationRecord:
    capture_status = str(row.get("capture_status") or "")
    if capture_status not in {"observed", "reconstructed"}:
        raise ValueError(f"CSV row must be captured/reconstructed, got {capture_status!r}")
    legacy_event = str(row.get("event") or "")
    payload = {
        "legacy_event": legacy_event,
        "stage": str(row.get("stage") or ""),
        "subject_id": str(row.get("subject_id") or ""),
        "severity": int(row.get("severity") or row.get("sev") or 0),
        "uncertainty": int(row.get("uncertainty") or 0),
        "detail": str(row.get("detail") or ""),
    }
    return ObservationRecord(
        observation_id=str(row.get("event_id") or ""),
        event_type=event_type_of(legacy_event),
        run_id=run_id,
        setting_id=str(row.get("setting") or ""),
        case_id=case_id_of(str(row.get("subject_id") or "")),
        producer=str(row.get("producer") or ""),
        channel=str(row.get("channel") or ""),
        sequence=int(row.get("sequence") or 0),
        capture_status=capture_status,
        source_artifact=str(row.get("source_artifact") or ""),
        source_sha256=str(row.get("source_sha256") or ""),
        payload=payload,
    )


def gap_records(summary: dict[str, Any], *, run_id: str) -> list[ObservationRecord]:
    records: list[ObservationRecord] = []
    for setting_summary in summary.get("settings", []):
        setting = str(setting_summary.get("setting") or "")
        next_sequence = int(setting_summary.get("total_reconstructed_events") or 0)
        for gap in setting_summary.get("instrumentation_gaps", []):
            raw_types: Iterable[str]
            if gap.get("event"):
                raw_types = (str(gap["event"]),)
            else:
                raw_types = str(gap.get("events") or "").split("/")
            for raw_type in raw_types:
                event_type = event_type_of(raw_type)
                next_sequence += 1
                identity = {
                    "run_id": run_id,
                    "setting": setting,
                    "event_type": event_type,
                    "gap_reason": gap.get("reason"),
                }
                records.append(
                    ObservationRecord(
                        observation_id=stable_identifier("GAP", identity),
                        event_type=event_type,
                        run_id=run_id,
                        setting_id=setting,
                        producer="baseline_instrumentation_audit",
                        channel="offline_artifact_replay",
                        sequence=next_sequence,
                        capture_status="unobservable",
                        gap_reason=str(gap.get("reason") or "baseline event was not observable"),
                        payload={},
                    )
                )
    return records


def load_contract_boundary(
    events_path: Path, summary_path: Path
) -> tuple[list[ObservationRecord], dict[str, Any]]:
    if not events_path.is_file() or not summary_path.is_file():
        raise ValueError("EXP-006 contract boundary requires events.csv and summary.json")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    run_id = "EXP006-" + sha256_file(summary_path)[:20]
    with events_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    captured = [adapt_reconstructed_row(row, run_id=run_id) for row in rows]
    gaps = gap_records(summary, run_id=run_id)
    records = captured + gaps
    normalized = [record.to_dict() for record in records]
    boundary = {
        "schema_version": "1.0",
        "adapter": "exp006-legacy-csv-to-observation-record",
        "run_id": run_id,
        "captured_records": len(captured),
        "unobservable_gap_records": len(gaps),
        "total_contract_records": len(records),
        "event_types": sorted(
            {record.event_type for record in records}, key=lambda value: int(value[1:])
        ),
        "records_sha256": sha256(canonical_json(normalized).encode("utf-8")).hexdigest(),
        "source_events_sha256": sha256_file(events_path),
        "source_summary_sha256": sha256_file(summary_path),
        "all_records_valid": True,
    }
    return records, boundary


def replay_rows(records: Iterable[ObservationRecord]) -> list[dict[str, Any]]:
    """Return validated captured records in EXP-007's metric input shape."""

    rows: list[dict[str, Any]] = []
    for record in records:
        if record.capture_status == "unobservable":
            continue
        payload = dict(record.payload)
        rows.append(
            {
                "event_id": record.observation_id,
                "schema_version": record.schema_version,
                "setting": record.setting_id,
                "sequence": record.sequence,
                "event": payload["legacy_event"],
                "stage": payload["stage"],
                "producer": record.producer,
                "channel": record.channel,
                "capture_status": record.capture_status,
                "subject_id": payload["subject_id"],
                "uncertainty": payload["uncertainty"],
                "severity": payload["severity"],
                "sev": payload["severity"],
                "detail": payload["detail"],
                "source_artifact": record.source_artifact,
                "source_sha256": record.source_sha256,
            }
        )
    return rows
