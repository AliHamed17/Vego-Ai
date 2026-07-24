"""EXP-006: deterministic, provenance-carrying H-Listen event replay.

The replay reconstructs E1-E14 observations from frozen baseline artifacts. It
does not modify VEGO-AI and does not treat reconstructed event counts as quality
or evaluation evidence.
"""

from __future__ import annotations

import csv
import glob
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

from hlayer_harness import (
    REPO,
    exp005_gate_sentence,
    experiment_output_dir,
    load_exp005_gate,
    sha256_file,
    write_experiment_manifest,
    write_json,
)

EVAL = REPO / "VEGO-AI" / "eval_output"
RUN = REPO / "VEGO-AI" / "runs" / "20260614-122150" / "human"
OUT = experiment_output_dir("exp006")
SETTINGS = ("cd_ch", "cd_pw", "ucd_ch", "ucd_pw")
LOW_CERTAINTY = 0.75
SCHEMA_VERSION = "1.0"

CLAIM_BASE = (
    "Mechanism/observability evidence only. Reconstructed events are heterogeneous lifecycle "
    "observations, not independent quality outcomes."
)

STAGE = {
    "E1_template_created": "early",
    "E1_template_revised": "early",
    "E2_question_from_B": "early",
    "E2_question_from_D": "late",
    "E3_answer_logged": "early",
    "E4_guidelines_created": "early-mid",
    "E4_guidelines_refined": "early-mid",
    "E5_compliance_vector": "mid",
    "E6_inspector_uncertainty": "mid",
    "E7_variability_arrival": "mid-late",
    "E8_classification": "late",
    "E12_low_certainty_guideline": "early-mid",
    "E13_agent4_signals": "mid-late",
}
EARLY = {"early", "early-mid"}
UNCERTAINTY_EVENTS = {
    "E2_question_from_B",
    "E2_question_from_D",
    "E6_inspector_uncertainty",
    "E8_low_confidence",
    "E12_low_certainty_guideline",
    "E13_agent4_signals",
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def natural_key(value: str) -> tuple:
    return tuple(
        int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)
    )


def find_one(setting_dir: Path, pattern: str) -> Path | None:
    hits = sorted(
        (Path(path) for path in glob.glob(str(setting_dir / pattern))),
        key=lambda p: natural_key(p.name),
    )
    return hits[0] if hits else None


def guideline_index(doc: dict) -> dict[str, tuple]:
    return {
        str(item.get("id")): (item.get("description"), item.get("mapping_certainty"))
        for item in doc.get("reference_guidelines", []) or []
    }


def template_signature(doc: dict) -> str:
    value = doc.get("guidelines") if isinstance(doc.get("guidelines"), list) else doc
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def producer_for(event: str) -> str:
    if event.startswith("E1_"):
        return "Agent A"
    if event in {
        "E2_question_from_B",
        "E4_guidelines_created",
        "E4_guidelines_refined",
        "E12_low_certainty_guideline",
    }:
        return "Agent B"
    if event.startswith("E5_") or event.startswith("E6_"):
        return "Agent C"
    return "Agent D"


def replay_setting(setting: str) -> tuple[list[dict], dict, set[Path]]:
    setting_dir = EVAL / setting
    events: list[dict] = []
    input_paths: set[Path] = set()
    source_hash_cache: dict[Path, str] = {}

    def add(
        event: str, detail: str, source: Path, *, severity: int = 0, subject_id: str = ""
    ) -> None:
        source = source.resolve()
        input_paths.add(source)
        source_hash = source_hash_cache.setdefault(source, sha256_file(source))
        sequence = len(events) + 1
        identity = {
            "setting": setting,
            "event": event,
            "detail": detail,
            "subject_id": subject_id,
            "source_sha256": source_hash,
            "sequence": sequence,
        }
        event_id = (
            "OBS-"
            + hashlib.sha256(
                json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()[:20]
        )
        events.append(
            {
                "event_id": event_id,
                "schema_version": SCHEMA_VERSION,
                "setting": setting,
                "sequence": sequence,
                "event": event,
                "stage": STAGE.get(event, "n/a"),
                "producer": producer_for(event),
                "channel": "offline_artifact_replay",
                "capture_status": "reconstructed",
                "subject_id": subject_id,
                "uncertainty": int(event in UNCERTAINTY_EVENTS or severity >= 2),
                "severity": severity,
                "detail": detail,
                "source_artifact": source.relative_to(REPO).as_posix(),
                "source_sha256": source_hash,
            }
        )

    template_paths = [find_one(setting_dir, f"agentA_run{i}_template*.json") for i in (1, 2, 3)]
    template_paths.append(find_one(setting_dir, "agentA_best_template*.json"))
    previous_signature = None
    for index, path in enumerate(template_paths):
        if path is None:
            continue
        signature = template_signature(load_json(path))
        if index == 0:
            add("E1_template_created", path.name, path, subject_id="template")
        elif previous_signature is not None and signature != previous_signature:
            add("E1_template_revised", path.name, path, severity=1, subject_id="template")
        previous_signature = signature

    guide_paths = [find_one(setting_dir, f"agentB_run{i}_guidelines*.json") for i in (1, 2, 3)]
    best_guides = find_one(setting_dir, "agentB_best_guidelines*.json")
    guide_paths.append(best_guides)
    previous_index = None
    for index, path in enumerate(guide_paths):
        if path is None:
            continue
        guideline_doc = load_json(path)
        current_index = guideline_index(guideline_doc)
        if index == 0:
            add(
                "E4_guidelines_created",
                f"{path.name} n={len(current_index)}",
                path,
                subject_id="guideline_set",
            )
        elif previous_index is not None:
            added = set(current_index) - set(previous_index)
            removed = set(previous_index) - set(current_index)
            changed = {
                key
                for key in set(current_index) & set(previous_index)
                if current_index[key] != previous_index[key]
            }
            if added or removed or changed:
                add(
                    "E4_guidelines_refined",
                    f"{path.name} +{len(added)} -{len(removed)} ~{len(changed)}",
                    path,
                    severity=1,
                    subject_id="guideline_set",
                )
        previous_index = current_index

    if best_guides is not None:
        guideline_doc = load_json(best_guides)
        for guideline in sorted(
            guideline_doc.get("reference_guidelines", []) or [],
            key=lambda item: natural_key(str(item.get("id", ""))),
        ):
            certainty = guideline.get("mapping_certainty")
            if isinstance(certainty, (int, float)) and certainty <= LOW_CERTAINTY:
                severity = 3 if certainty <= 0.6 else (2 if certainty <= 0.7 else 1)
                guideline_id = str(guideline.get("id"))
                add(
                    "E12_low_certainty_guideline",
                    f"{guideline_id} certainty={certainty}",
                    best_guides,
                    severity=severity,
                    subject_id=f"guideline:{guideline_id}",
                )
        questions = guideline_doc.get("questions_to_language_advisor", []) or []
        for question in sorted(questions, key=lambda item: natural_key(str(item.get("id", "")))):
            question_id = str(question.get("id"))
            add(
                "E2_question_from_B",
                f"{question_id} templates={question.get('related_template_ids')}",
                best_guides,
                severity=2,
                subject_id=f"question:B:{question_id}",
            )

    case_paths = sorted(setting_dir.glob("agentC_case_*.json"), key=lambda p: natural_key(p.name))
    for path in case_paths:
        case_doc = load_json(path)
        case_id = str(case_doc.get("case_id") or path.stem)
        add("E5_compliance_vector", case_id, path, subject_id=f"case:{case_id}")
        uncovered = case_doc.get("uncovered_fragments") or []
        potential = case_doc.get("potential_found") or []
        if uncovered or potential:
            signal_count = len(uncovered) + len(potential)
            severity = 3 if signal_count >= 4 else (2 if signal_count >= 2 else 1)
            add(
                "E6_inspector_uncertainty",
                f"{case_id} uncovered={len(uncovered)} potential={len(potential)}",
                path,
                severity=severity,
                subject_id=f"case:{case_id}",
            )

    deviation_path = find_one(setting_dir, "agentD_deviation_patterns*.json")
    if deviation_path is not None:
        deviation_doc = load_json(deviation_path)
        pattern_count = len(deviation_doc.get("recurring_fragment_patterns") or []) + len(
            deviation_doc.get("recurring_guideline_patterns") or []
        )
        for index in range(pattern_count):
            add(
                "E7_variability_arrival",
                f"pattern_{index}",
                deviation_path,
                subject_id=f"pattern:{index}",
            )

    low_confidence = 0
    classification_path = find_one(setting_dir, "agentD_variability_classes*.json")
    if classification_path is not None:
        classification_doc = load_json(classification_path)
        classifications = classification_doc.get("variability_classifications", []) or []
        for classification in sorted(
            classifications, key=lambda item: natural_key(str(item.get("pattern_id", "")))
        ):
            confidence = str(classification.get("confidence"))
            pattern_id = str(classification.get("pattern_id"))
            flags = []
            if classification.get("requires_human_review"):
                flags.append("requires_human_review")
            if classification.get("flag_for_guidelines_update"):
                flags.append("flag_for_guidelines_update")
            if str(classification.get("classification", "")).lower() == "undetermined":
                flags.append("undetermined")
            confidence_severity = (
                0 if confidence.lower() == "high" else (3 if confidence.lower() == "low" else 2)
            )
            add(
                "E8_classification",
                f"{pattern_id} conf={confidence}",
                classification_path,
                severity=confidence_severity,
                subject_id=f"pattern:{pattern_id}",
            )
            low_confidence += int(bool(confidence_severity))
            for flag in sorted(flags):
                add(
                    "E13_agent4_signals",
                    f"{pattern_id} {flag}",
                    classification_path,
                    severity=3,
                    subject_id=f"pattern:{pattern_id}",
                )
        questions = (classification_doc.get("questions_to_domain_advisor") or []) + (
            classification_doc.get("questions_to_language_advisor") or []
        )
        for question in sorted(questions, key=lambda item: natural_key(str(item.get("id", item)))):
            question_id = str(question.get("id") if isinstance(question, dict) else question)
            add(
                "E2_question_from_D",
                question_id,
                classification_path,
                severity=2,
                subject_id=f"question:D:{question_id}",
            )

    queue_path = RUN / setting / "human_review_queue.jsonl"
    queue_items = 0
    if queue_path.is_file():
        input_paths.add(queue_path.resolve())
        with queue_path.open(encoding="utf-8") as handle:
            queue_items = sum(1 for line in handle if line.strip())

    counts = Counter(event["event"] for event in events)
    early = sum(event["stage"] in EARLY for event in events)
    uncertainty = sum(event["uncertainty"] for event in events)
    severity_mass = sum(event["severity"] for event in events)
    severity_two_plus = sum(event["severity"] >= 2 for event in events)
    event_count = len(events)
    return (
        events,
        {
            "setting": setting,
            "total_reconstructed_events": event_count,
            "total_events": event_count,
            "events_by_type": dict(sorted(counts.items())),
            "early_stage_events": early,
            "early_stage_share": round(early / event_count, 3) if event_count else 0,
            "uncertainty_marked_events": uncertainty,
            "severity_mass": severity_mass,
            "sev2plus_events": severity_two_plus,
            "agent8_low_confidence": low_confidence,
            "old_m1_review_queue_items": queue_items,
            "old_m1_queue_item_to_reconstructed_event_count_ratio": round(
                queue_items / event_count, 3
            )
            if event_count
            else 0,
            "ratio_semantics": "queue items / heterogeneous reconstructed lifecycle events; not a visibility share",
            "instrumentation_gaps": [
                {
                    "event": "E3",
                    "capture_status": "unobservable",
                    "reason": "answers not persisted",
                },
                {"event": "E9", "capture_status": "unobservable", "reason": "requires answer logs"},
                {
                    "events": "E10/E11/E14",
                    "capture_status": "unobservable",
                    "reason": "H-layer lifecycle did not run in baseline",
                },
            ],
        },
        input_paths,
    )


def main() -> int:
    missing = [setting for setting in SETTINGS if not (EVAL / setting).is_dir()]
    if missing:
        print(f"EXP-006 missing required setting directories: {missing}", file=sys.stderr)
        return 2
    gate = load_exp005_gate()
    claim = f"{CLAIM_BASE} {exp005_gate_sentence(gate)}"
    OUT.mkdir(parents=True, exist_ok=True)
    all_events: list[dict] = []
    summaries: list[dict] = []
    inputs: set[Path] = set()
    for setting in SETTINGS:
        events, summary, setting_inputs = replay_setting(setting)
        all_events.extend(events)
        summaries.append(summary)
        inputs.update(setting_inputs)

    events_path = OUT / "events.csv"
    fieldnames = [
        "event_id",
        "schema_version",
        "setting",
        "sequence",
        "event",
        "stage",
        "producer",
        "channel",
        "capture_status",
        "subject_id",
        "uncertainty",
        "severity",
        "detail",
        "source_artifact",
        "source_sha256",
    ]
    with events_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_events)

    totals = {
        "total_reconstructed_events": sum(item["total_reconstructed_events"] for item in summaries),
        "total_events": sum(item["total_events"] for item in summaries),
        "early_stage_events": sum(item["early_stage_events"] for item in summaries),
        "uncertainty_marked_events": sum(item["uncertainty_marked_events"] for item in summaries),
        "severity_mass": sum(item["severity_mass"] for item in summaries),
        "sev2plus_events": sum(item["sev2plus_events"] for item in summaries),
        "old_m1_review_queue_items": sum(item["old_m1_review_queue_items"] for item in summaries),
    }
    totals["early_stage_share"] = (
        round(totals["early_stage_events"] / totals["total_reconstructed_events"], 3)
        if totals["total_reconstructed_events"]
        else 0
    )
    totals["old_m1_queue_item_to_reconstructed_event_count_ratio"] = (
        round(totals["old_m1_review_queue_items"] / totals["total_reconstructed_events"], 3)
        if totals["total_reconstructed_events"]
        else 0
    )
    totals["ratio_semantics"] = (
        "queue items / heterogeneous reconstructed lifecycle events; not a percentage of events seen"
    )

    summary = {
        "experiment": "EXP-006 H-Listen event replay",
        "schema_version": SCHEMA_VERSION,
        "claim_scope": claim,
        "low_certainty_threshold": LOW_CERTAINTY,
        "settings": summaries,
        "totals": totals,
    }
    summary_path = OUT / "summary.json"
    write_json(summary_path, summary)

    lines = [
        "# EXP-006 H-Listen Event Replay - Summary",
        "",
        f"Claim scope: {claim}",
        "",
        "The queue/event value below is a ratio between heterogeneous units, not a visibility or coverage percentage.",
        "",
        "| Setting | Reconstructed events | Early-stage | Early share | Uncertainty-marked | Queue items | Queue-item/event-count ratio |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in summaries:
        lines.append(
            f"| {item['setting']} | {item['total_reconstructed_events']} | {item['early_stage_events']} | "
            f"{item['early_stage_share']} | {item['uncertainty_marked_events']} | "
            f"{item['old_m1_review_queue_items']} | {item['old_m1_queue_item_to_reconstructed_event_count_ratio']} |"
        )
    lines.append(
        f"| TOTAL | {totals['total_reconstructed_events']} | {totals['early_stage_events']} | "
        f"{totals['early_stage_share']} | {totals['uncertainty_marked_events']} | "
        f"{totals['old_m1_review_queue_items']} | {totals['old_m1_queue_item_to_reconstructed_event_count_ratio']} |"
    )
    type_totals = Counter()
    for item in summaries:
        type_totals.update(item["events_by_type"])
    lines.extend(["", "## Events by type", "", "| Event | Count |", "| --- | ---: |"])
    lines.extend(f"| {event} | {count} |" for event, count in sorted(type_totals.items()))
    lines.extend(
        [
            "",
            "## Explicit instrumentation gaps",
            "",
            "- E3: unobservable because answers are not persisted.",
            "- E9: unobservable without answer logs.",
            "- E10/E11/E14: unobservable because no H-layer ran in the baseline.",
        ]
    )
    summary_md = OUT / "summary.md"
    summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    write_experiment_manifest(
        OUT,
        experiment_id="EXP-006",
        experiment_version="3.0",
        config_version="event-replay-contract-1.0",
        claim_scope=claim,
        script_path=Path(__file__),
        inputs=inputs,
        outputs=[events_path, summary_path, summary_md],
        config={
            "settings": list(SETTINGS),
            "low_certainty_threshold": LOW_CERTAINTY,
            "schema_version": SCHEMA_VERSION,
        },
        metric_schema={
            "total_reconstructed_events": "count of heterogeneous reconstructed lifecycle observations",
            "early_stage_share": "early reconstructed events / all reconstructed events",
            "old_m1_queue_item_to_reconstructed_event_count_ratio": "queue items / reconstructed events (heterogeneous ratio)",
        },
    )
    print(
        f"EXP-006 done: {totals['total_reconstructed_events']} reconstructed events; "
        f"queue-item/event-count ratio={totals['old_m1_queue_item_to_reconstructed_event_count_ratio']} -> {OUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
