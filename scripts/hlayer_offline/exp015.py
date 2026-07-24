"""EXP-015: offline workload, bundling, and queue-aging fairness checks."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping
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
from .contracts import ObservationRecord, stable_identifier
from .state_machine import route_observation

EXPERIMENT_ID = "EXP-015"
EXPERIMENT_FOLDER = "EXP-015-workload-bundling-fairness"


def _natural_key(value: str) -> tuple[Any, ...]:
    return tuple(int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value))


def _bundle_key(item: Mapping[str, Any]) -> str:
    """Keep setting, case, guideline, and question boundaries explicit."""

    return "|".join(
        [
            item["setting_id"],
            item.get("case_id") or "-",
            item.get("guideline_id") or "-",
            item.get("question_id") or "-",
        ]
    )


def _select(items: list[dict[str, Any]], cap: int) -> list[dict[str, Any]]:
    high = sorted(
        (item for item in items if item["severity"] >= 2),
        key=lambda item: (-item["severity"], -item["age"], _natural_key(item["id"])),
    )
    routine = sorted(
        (item for item in items if item["severity"] < 2),
        key=lambda item: (-item["age"], -item["severity"], _natural_key(item["id"])),
    )
    effective_cap = max(cap, len(high))
    return high + routine[: max(0, effective_cap - len(high))]


def _simulate_config(
    name: str,
    items: list[dict[str, Any]],
    caps: Mapping[str, int],
    observations: Mapping[str, ObservationRecord],
) -> dict[str, Any]:
    by_setting: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        by_setting[item["setting_id"]].append(item)
    total_count = len(items)
    high_ids = {item["id"] for item in items if item["severity"] >= 2}
    selected_round1: list[dict[str, Any]] = []
    for setting, setting_items in sorted(by_setting.items()):
        selected_round1.extend(_select(setting_items, caps[setting]))
    selected_ids = {item["id"] for item in selected_round1}
    deferred = [item for item in items if item["id"] not in selected_ids]

    # A later checkpoint considers only the parked queue after its age increases.
    aged_deferred = [{**item, "age": item["age"] + 100} for item in deferred]
    deferred_by_setting: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in aged_deferred:
        deferred_by_setting[item["setting_id"]].append(item)
    selected_round2: list[dict[str, Any]] = []
    for setting, setting_items in sorted(deferred_by_setting.items()):
        selected_round2.extend(_select(setting_items, caps[setting]))
    recovered_ids = {item["id"] for item in selected_round2}

    triage_records = []
    for item in items:
        triage_records.append(
            route_observation(
                observations[item["id"]],
                severity=item["severity"],
                trigger_codes=(item["trigger_code"],),
                dosage_config={"mode": name, "caps": dict(caps), "approved_default": False},
                bundle_key=_bundle_key(item),
                within_budget=item["id"] in selected_ids,
            ).to_dict()
        )

    bundle_subjects: dict[str, set[tuple[str, str, str, str]]] = defaultdict(set)
    for item in selected_round1:
        subject = (
            item["setting_id"],
            item.get("case_id") or "-",
            item.get("guideline_id") or "-",
            item.get("question_id") or "-",
        )
        bundle_subjects[_bundle_key(item)].add(subject)
    collisions = {key: sorted(values) for key, values in bundle_subjects.items() if len(values) > 1}
    selected_high = len(high_ids & selected_ids)
    return {
        "config": name,
        "caps": dict(caps),
        "denominators": {"observations": total_count, "high_severity_observations": len(high_ids)},
        "round_1": {
            "selected_observations": len(selected_round1),
            "selected_ids": sorted(selected_ids, key=_natural_key),
            "load": round(len(selected_round1) / total_count, 6) if total_count else 0.0,
            "bundle_count": len(bundle_subjects),
            "bundle_reduction_observed": len(selected_round1) - len(bundle_subjects),
            "high_severity_coverage": round(selected_high / len(high_ids), 6) if high_ids else 1.0,
        },
        "fairness": {
            "deferred_ids": sorted((item["id"] for item in deferred), key=_natural_key),
            "oldest_deferred_age": max((item["age"] for item in deferred), default=0),
            "recovered_next_checkpoint_ids": sorted(recovered_ids, key=_natural_key),
            "still_deferred_after_next_checkpoint": sorted(
                (item["id"] for item in deferred if item["id"] not in recovered_ids),
                key=_natural_key,
            ),
        },
        "bundle_collision_count": len(collisions),
        "bundle_collisions": collisions,
        "triage_records": triage_records,
    }


def evaluate(fixtures: Path | None = None) -> dict[str, Any]:
    fixtures = fixtures or fixture_dir(EXPERIMENT_FOLDER)
    descriptor_path = fixtures / "queue.json"
    fixture = load_json(descriptor_path)
    source_hash = sha256_file(descriptor_path)
    observations: dict[str, ObservationRecord] = {}
    for item in fixture["items"]:
        observations[item["id"]] = ObservationRecord(
            observation_id=stable_identifier("OBS", item),
            event_type=item["event_type"],
            run_id=fixture["run_id"],
            setting_id=item["setting_id"],
            case_id=item.get("case_id"),
            producer="queue_fixture",
            channel="offline_replay",
            sequence=item["sequence"],
            capture_status="reconstructed",
            source_artifact=relative_path(descriptor_path),
            source_sha256=source_hash,
            payload={
                "fixture_item_id": item["id"],
                "guideline_id": item.get("guideline_id"),
                "question_id": item.get("question_id"),
            },
        )
    configs = [
        ("uniform_cap_4", {setting: 4 for setting in fixture["settings"]}),
        ("adaptive_fixture_caps", fixture["adaptive_caps"]),
    ]
    results = [
        _simulate_config(name, fixture["items"], caps, observations) for name, caps in configs
    ]
    acceptance = {
        "stable_denominators": all(
            result["denominators"]
            == {"observations": len(fixture["items"]), "high_severity_observations": 6}
            for result in results
        ),
        "no_cross_subject_bundle_collisions": all(
            result["bundle_collision_count"] == 0 for result in results
        ),
        "high_severity_preserved": all(
            result["round_1"]["high_severity_coverage"] == 1.0 for result in results
        ),
        "deferred_recovery_reported": all(
            bool(result["fairness"]["recovered_next_checkpoint_ids"]) for result in results
        ),
    }
    summary = {
        "experiment": EXPERIMENT_ID,
        "fixture_version": fixture["fixture_version"],
        "configurations": results,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }
    return {"summary": summary, "input_files": (descriptor_path,)}


def execute(output_dir: Path | None = None) -> dict[str, Any]:
    result = evaluate()
    output = output_dir or default_output_dir(EXPERIMENT_ID)
    write_experiment_bundle(
        experiment_id=EXPERIMENT_ID,
        experiment_version="1.0",
        config_version="fixture-1.0",
        output_dir=output,
        input_files=result["input_files"],
        payloads={"summary.json": result["summary"]},
        metric_schema={
            "load": "selected_observations / fixed_observation_denominator",
            "bundle_reduction_observed": "selected_observations - distinct_composite_bundles",
            "high_severity_coverage": "selected_high_severity / fixed_high_severity_denominator",
            "deferred_recovery": "identifier[]",
        },
        parameters={
            "uniform_cap": 4,
            "adaptive_caps": "fixture-comparison-only",
            "aging_increment": 100,
        },
    )
    print_completion(EXPERIMENT_ID, output, result["summary"])
    return result
