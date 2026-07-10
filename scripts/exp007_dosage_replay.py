"""EXP-007: deterministic S2 dosage replay with fixed workload denominators."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from hlayer_harness import (
    exp005_gate_sentence,
    experiment_output_dir,
    load_exp005_gate,
    output_root,
    write_experiment_manifest,
    write_json,
)
from hlayer_offline.legacy_replay_adapter import load_contract_boundary, replay_rows

ROOT = output_root()
IN = ROOT / "exp006" / "events.csv"
EXP006_SUMMARY = ROOT / "exp006" / "summary.json"
ADAPTER_PATH = Path(__file__).parent / "hlayer_offline" / "legacy_replay_adapter.py"
OUT = experiment_output_dir("exp007")
FIRST_N = 10
CLAIM_BASE = "Design/mechanism evidence for workload and coverage trade-offs only."
TRIAGEABLE = {
    "E1_template_created",
    "E1_template_revised",
    "E2_question_from_B",
    "E2_question_from_D",
    "E4_guidelines_created",
    "E4_guidelines_refined",
    "E6_inspector_uncertainty",
    "E8_classification",
    "E12_low_certainty_guideline",
    "E13_agent4_signals",
}


def natural_key(value: str) -> tuple:
    return tuple(
        int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)
    )


def case_of(event: dict) -> str | None:
    subject = str(event.get("subject_id", ""))
    if subject.startswith("case:"):
        return subject.split(":", 1)[1]
    if event.get("event") in {"E5_compliance_vector", "E6_inspector_uncertainty"}:
        match = re.match(r"(\d+)", str(event.get("detail", "")))
        return match.group(1) if match else None
    return None


def bundle_key_of(event: dict) -> tuple[str, str]:
    """Return a boundary-safe review transaction key.

    Setting is always part of the key, preventing identical case/pattern IDs
    from being bundled across settings.
    """
    setting = str(event.get("setting", ""))
    subject = str(event.get("subject_id", "")).strip()
    if subject:
        return setting, subject
    detail = str(event.get("detail", ""))
    event_type = str(event.get("event", ""))
    case_id = case_of(event)
    if case_id:
        return setting, f"case:{case_id}"
    if event_type in {"E8_classification", "E13_agent4_signals"}:
        match = re.match(r"^([\w-]+)", detail)
        if match:
            return setting, f"pattern:{match.group(1)}"
    if event_type == "E12_low_certainty_guideline":
        match = re.match(r"^([Gg]\d+)", detail)
        if match:
            return setting, f"guideline:{match.group(1)}"
    if event_type in {"E2_question_from_B", "E2_question_from_D"}:
        return setting, f"question:{detail.split()[0]}"
    if event_type.startswith("E1_"):
        return setting, "template"
    if event_type.startswith("E4_"):
        return setting, "guideline_set"
    return setting, f"{event_type}:{detail}"


def subject_severity(events: Iterable[dict]) -> dict[tuple[str, str], int]:
    values: dict[tuple[str, str], int] = {}
    for event in events:
        key = bundle_key_of(event)
        values[key] = max(values.get(key, 0), int(event.get("sev", event.get("severity", 0)) or 0))
    return values


def metrics(selected: list[dict], triageable: list[dict]) -> dict:
    total_subjects = subject_severity(triageable)
    selected_subjects = subject_severity(selected)
    total_mass = sum(total_subjects.values())
    selected_mass = sum(total_subjects[key] for key in selected_subjects if key in total_subjects)
    high_subjects = {key for key, severity in total_subjects.items() if severity >= 2}
    selected_high = high_subjects.intersection(selected_subjects)

    event_denominator = len(triageable)
    event_load = len(selected) / event_denominator if event_denominator else 0.0
    transaction_count = len(selected_subjects)
    transaction_load = transaction_count / event_denominator if event_denominator else 0.0
    subject_denominator = len(total_subjects)
    subject_load = transaction_count / subject_denominator if subject_denominator else 0.0
    weighted_coverage = selected_mass / total_mass if total_mass else 1.0
    bundling_reduction = 1 - transaction_count / len(selected) if selected else 0.0

    return {
        "routed_event_items": len(selected),
        "routed_items": len(selected),  # compatibility alias; unit is explicit above
        "event_load_vs_every_decision": round(event_load, 3),
        "load_vs_every_decision": round(event_load, 3),
        "review_transactions": transaction_count,
        "review_transaction_load_vs_every_decision_events": round(transaction_load, 3),
        "bundled_load": round(
            transaction_load, 3
        ),  # compatibility alias with corrected fixed denominator
        "unique_subject_load": round(subject_load, 3),
        "bundling_reduction_vs_unbundled_selected": round(bundling_reduction, 3),
        "weighted_severity_coverage": round(weighted_coverage, 3),
        "high_severity_coverage": round(len(selected_high) / len(high_subjects), 3)
        if high_subjects
        else 1.0,
        "efficiency": round(weighted_coverage / event_load, 3) if event_load else 0.0,
        "bundled_efficiency": round(weighted_coverage / transaction_load, 3)
        if transaction_load
        else 0.0,
        "triageable_event_total": event_denominator,
        "triageable_total": event_denominator,
        "triageable_unique_subject_total": subject_denominator,
        "bundled_triageable_total": subject_denominator,
        "severity_mass_total_unique_subject_max": total_mass,
        "severity_mass_total": total_mass,
        "high_severity_subject_total": len(high_subjects),
        "high_severity_total": len(high_subjects),
        "denominators": {
            "event_load": "selected triageable event items / all triageable event items",
            "review_transaction_load": "selected unique setting+subject transactions / all triageable event items",
            "unique_subject_load": "selected unique setting+subject transactions / all unique setting+subject subjects",
            "coverage": "max severity per unique setting+subject; correlated signals are counted once",
        },
    }


def simulate(events: list[dict]) -> list[dict]:
    triageable = [event for event in events if event.get("event") in TRIAGEABLE]
    case_ids = sorted(
        {case for case in (case_of(event) for event in events) if case}, key=natural_key
    )
    first_cases = set(case_ids[:FIRST_N])
    modes = {
        "every_decision": triageable,
        "threshold_sev1": [event for event in triageable if event["sev"] >= 1],
        "threshold_sev2": [event for event in triageable if event["sev"] >= 2],
        "threshold_sev3": [event for event in triageable if event["sev"] >= 3],
        "first_n_then_auto": [
            event for event in triageable if case_of(event) in first_cases or event["sev"] >= 3
        ],
        "silent": [],
    }
    return [{"mode": name, **metrics(selected, triageable)} for name, selected in modes.items()]


def pareto_frontier(rows: list[dict]) -> list[dict]:
    """Return load-minimizing / coverage-maximizing non-dominated modes."""

    frontier: list[dict] = []
    for candidate in rows:
        load = candidate["event_load_vs_every_decision"]
        coverage = candidate["weighted_severity_coverage"]
        dominated = any(
            other is not candidate
            and other["event_load_vs_every_decision"] <= load
            and other["weighted_severity_coverage"] >= coverage
            and (
                other["event_load_vs_every_decision"] < load
                or other["weighted_severity_coverage"] > coverage
            )
            for other in rows
        )
        if not dominated:
            frontier.append(
                {
                    "mode": candidate["mode"],
                    "event_load": load,
                    "review_transaction_load": candidate[
                        "review_transaction_load_vs_every_decision_events"
                    ],
                    "weighted_severity_coverage": coverage,
                    "high_severity_coverage": candidate["high_severity_coverage"],
                }
            )
    return sorted(frontier, key=lambda row: (row["event_load"], row["mode"]))


def main() -> int:
    if not IN.is_file() or not EXP006_SUMMARY.is_file():
        print(f"EXP-006 boundary inputs missing: {IN}, {EXP006_SUMMARY}", file=sys.stderr)
        return 2
    gate = load_exp005_gate()
    claim = f"{CLAIM_BASE} {exp005_gate_sentence(gate)}"
    by_setting: dict[str, list[dict]] = defaultdict(list)
    try:
        contract_records, contract_boundary = load_contract_boundary(IN, EXP006_SUMMARY)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"EXP-006 contract boundary failed: {exc}", file=sys.stderr)
        return 2
    for row in replay_rows(contract_records):
        by_setting[row["setting"]].append(row)
    if not by_setting:
        print("EXP-007 input contains no events", file=sys.stderr)
        return 2
    for setting in by_setting:
        by_setting[setting].sort(
            key=lambda event: (int(event.get("sequence") or 0), event.get("event_id", ""))
        )

    results = {setting: simulate(by_setting[setting]) for setting in sorted(by_setting)}
    all_events = [event for setting in sorted(by_setting) for event in by_setting[setting]]
    results["ALL"] = simulate(all_events)
    pareto = {setting: pareto_frontier(rows) for setting, rows in results.items()}
    all_target_rows = [
        row
        for row in results["ALL"]
        if row["weighted_severity_coverage"] >= 0.8 and row["event_load_vs_every_decision"] <= 0.5
    ]
    summary = {
        "experiment": "EXP-007 S2 dosage-mode replay (v3 fixed denominators)",
        "claim_scope": claim,
        "first_n": FIRST_N,
        "threshold_sev2_status": "replay-based pilot candidate; not an approved default",
        "contract_boundary": contract_boundary,
        "pareto_frontiers": pareto,
        "guardrails": {
            "recommended_pilot_high_severity_coverage_required": 1.0,
            "workload_coverage_target": {"coverage_at_least": 0.8, "event_load_at_most": 0.5},
            "workload_coverage_target_met": bool(all_target_rows),
            "qualifying_modes": [row["mode"] for row in all_target_rows],
            "interpretation": (
                "Report the observed Pareto boundary; do not select or silently tune a default."
            ),
        },
        "results": results,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    summary_path = OUT / "summary.json"
    write_json(summary_path, summary)
    boundary_path = OUT / "contract-boundary.json"
    write_json(boundary_path, contract_boundary)

    lines = [
        "# EXP-007 Dosage-Mode Replay - Summary",
        "",
        f"Claim scope: {claim}",
        "",
        "`threshold_sev2` is a replay-based pilot candidate, not an approved default.",
        "Coverage uses the maximum severity per setting+subject so correlated event signals are not double-counted.",
        "Review-transaction load always uses the same all-triageable-event denominator as event load.",
        "",
    ]
    for setting, rows in results.items():
        lines.extend(
            [
                f"## {setting}",
                "",
                "| Mode | Routed events | Event load | Review transactions | Transaction load | Bundle reduction | Weighted coverage | High-sev coverage |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in rows:
            lines.append(
                f"| {row['mode']} | {row['routed_event_items']} | {row['event_load_vs_every_decision']} | "
                f"{row['review_transactions']} | {row['review_transaction_load_vs_every_decision_events']} | "
                f"{row['bundling_reduction_vs_unbundled_selected']} | {row['weighted_severity_coverage']} | "
                f"{row['high_severity_coverage']} |"
            )
        lines.append("")
        lines.extend(
            [
                "Pareto frontier: "
                + ", ".join(
                    f"{point['mode']} (load={point['event_load']}, coverage={point['weighted_severity_coverage']})"
                    for point in pareto[setting]
                ),
                "",
            ]
        )
    lines.extend(
        [
            "## Guardrail readout",
            "",
            (
                "The aggregate coverage>=0.8 at event-load<=0.5 target is met."
                if all_target_rows
                else "The aggregate coverage>=0.8 at event-load<=0.5 target remains unmet; report the Pareto boundary without selecting a default."
            ),
            "",
        ]
    )
    summary_md = OUT / "summary.md"
    summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_experiment_manifest(
        OUT,
        experiment_id="EXP-007",
        experiment_version="3.0",
        config_version="dosage-fixed-denominators-1.0",
        claim_scope=claim,
        script_path=Path(__file__),
        inputs=[IN, EXP006_SUMMARY, ADAPTER_PATH],
        outputs=[summary_path, summary_md, boundary_path],
        config={"first_n": FIRST_N, "modes": [row["mode"] for row in results["ALL"]]},
        metric_schema={
            "event_load_vs_every_decision": "selected triageable event items / all triageable event items",
            "review_transaction_load_vs_every_decision_events": "unique selected setting+subject transactions / all triageable event items",
            "weighted_severity_coverage": "selected max severity mass / total max severity mass per setting+subject",
            "contract_boundary": "EXP-006 rows validated as ObservationRecord 1.0 before replay",
            "pareto_frontiers": "non-dominated event-load/weighted-coverage points per setting and aggregate",
        },
    )
    candidate = next(row for row in results["ALL"] if row["mode"] == "threshold_sev2")
    print(
        "EXP-007 done: threshold_sev2 "
        f"event_load={candidate['event_load_vs_every_decision']} "
        f"transaction_load={candidate['review_transaction_load_vs_every_decision_events']} -> {OUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
