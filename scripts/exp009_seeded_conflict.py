"""EXP-009: deterministic H-Verify seeded-conflict rule tests.

All fixture cases are explicitly synthetic and test rule behavior only. An
override is escalated for human adjudication; it is never approved here.
"""

from __future__ import annotations

import copy
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
    stable_digest,
    write_experiment_manifest,
    write_json,
)

OUT = experiment_output_dir("exp009")
FIXTURE = REPO / "scripts" / "tests" / "fixtures" / "exp009_seeds.v1.json"
CLAIM_BASE = "Assumption-driven synthetic rule tests for deterministic H-Verify behavior only."
CORE_GUIDELINES = frozenset({"G5", "G18"})
MEMORY_STORE = {("cd_ch", "pattern_cd_ch-P5"): "Reject"}
SYNTHETIC_TAG = "SYNTHETIC_NOT_HUMAN"


def load_fixture(path: Path = FIXTURE) -> dict:
    if not path.is_file():
        raise ValueError(f"Synthetic fixture not found: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("evidence_classification") != SYNTHETIC_TAG:
        raise ValueError("EXP-009 fixture must be tagged SYNTHETIC_NOT_HUMAN")
    seeds = value.get("seeds")
    if not isinstance(seeds, list) or not seeds:
        raise ValueError("EXP-009 fixture has no seeds")
    ids = [seed.get("id") for seed in seeds]
    if len(ids) != len(set(ids)) or any(not seed_id for seed_id in ids):
        raise ValueError("EXP-009 fixture IDs must be unique and nonblank")
    return value


def verify_feedback(feedback: dict) -> list[str]:
    """Return all deterministic conflicts, in rule order."""
    findings: list[str] = []
    decision = str(feedback.get("decision") or "").strip()
    rationale = str(feedback.get("rationale") or "").strip()
    guideline = str(feedback.get("guideline_id") or "").strip()
    detail = str(feedback.get("detail") or "")
    template_detail = str(feedback.get("template_detail") or "")
    setting = str(feedback.get("setting") or "")
    if decision not in {"Approve", "Reject", "Modify"} or not rationale:
        findings.append("R0_REQUIRED_FIELDS")
    if decision == "Reject" and guideline in CORE_GUIDELINES:
        findings.append("R1_CORE_GUIDELINE")
    if template_detail.count("{") != template_detail.count("}"):
        findings.append("R2_TEMPLATE_SYNTAX")
    pattern_match = re.match(r"^(pattern_[\w-]+)", detail)
    if pattern_match:
        prior = MEMORY_STORE.get((setting, pattern_match.group(1)))
        if prior and prior != decision:
            findings.append("R3_MEMORY_DIVERGENCE")
    negative_rationale = re.search(
        r"\b(does not conform|noncompliant|violates|incorrect|must be rejected)\b",
        rationale,
        re.IGNORECASE,
    )
    if decision == "Approve" and negative_rationale:
        findings.append("R4_DECISION_RATIONALE")
    return findings


def run_simulation(fixture: dict) -> list[dict]:
    records: list[dict] = []
    for seed in sorted(fixture["seeds"], key=lambda item: item["id"]):
        feedback = {
            key: seed.get(key)
            for key in (
                "setting",
                "decision",
                "guideline_id",
                "detail",
                "template_detail",
                "rationale",
            )
        }
        initial_findings = verify_feedback(feedback)
        trace = [
            {
                "round": 1,
                "feedback": feedback,
                "verification_findings": initial_findings,
                "outcome": "conflict_detected" if initial_findings else "passed_no_conflict",
            }
        ]
        final_status = "passed_no_conflict"
        if initial_findings:
            round_two = seed.get("round_2") or {"action": "no_response"}
            action = round_two.get("action")
            if action == "correct":
                corrected = copy.deepcopy(feedback)
                corrected.update(
                    {key: value for key, value in round_two.items() if key != "action"}
                )
                findings = verify_feedback(corrected)
                final_status = "resolved" if not findings else "still_conflicted"
                trace.append(
                    {
                        "round": 2,
                        "action": "corrected_feedback",
                        "feedback": corrected,
                        "verification_findings": findings,
                        "outcome": final_status,
                    }
                )
            elif action == "override":
                final_status = "escalated_pending_adjudication"
                trace.append(
                    {
                        "round": 2,
                        "action": "override_request",
                        "override_rationale": round_two.get("override_rationale", ""),
                        "verification_findings": initial_findings,
                        "outcome": final_status,
                        "authority": "human adjudication required; no approval recorded",
                    }
                )
            else:
                final_status = "timed_out_parked"
                trace.append(
                    {
                        "round": 2,
                        "action": "no_response",
                        "verification_findings": initial_findings,
                        "outcome": final_status,
                        "baseline_preserved": True,
                    }
                )
        records.append(
            {
                "id": seed["id"],
                "description": seed["description"],
                "fixture_version": fixture["fixture_version"],
                "evidence_classification": SYNTHETIC_TAG,
                "expected_conflict": bool(seed["expected_conflict"]),
                "expected_rule": seed.get("expected_rule"),
                "detected_conflict": bool(initial_findings),
                "detected_rules": initial_findings,
                "dialogue_history": trace,
                "final_status": final_status,
                "trusted_memory_write": False,
                "correction_applied": False,
            }
        )
    return records


def metric_summary(records: list[dict]) -> dict:
    true_positive = sum(item["expected_conflict"] and item["detected_conflict"] for item in records)
    false_positive = sum(
        not item["expected_conflict"] and item["detected_conflict"] for item in records
    )
    false_negative = sum(
        item["expected_conflict"] and not item["detected_conflict"] for item in records
    )
    true_negative = sum(
        not item["expected_conflict"] and not item["detected_conflict"] for item in records
    )
    expected_rules = Counter(
        item.get("expected_rule") for item in records if item.get("expected_rule")
    )
    caught_rules = Counter(
        item["expected_rule"]
        for item in records
        if item.get("expected_rule") and item["expected_rule"] in item["detected_rules"]
    )
    return {
        "total_seeds": len(records),
        "synthetic_conflict_cases": sum(item["expected_conflict"] for item in records),
        "synthetic_non_conflict_cases": sum(not item["expected_conflict"] for item in records),
        "true_positives": true_positive,
        "false_positives": false_positive,
        "false_negatives": false_negative,
        "true_negatives": true_negative,
        "synthetic_detection_recall": round(true_positive / (true_positive + false_negative), 3)
        if true_positive + false_negative
        else 1.0,
        "synthetic_specificity": round(true_negative / (true_negative + false_positive), 3)
        if true_negative + false_positive
        else 1.0,
        "per_rule_fixture_coverage": {
            rule: {"expected": count, "detected": caught_rules[rule]}
            for rule, count in sorted(expected_rules.items())
        },
        "final_status_counts": dict(
            sorted(Counter(item["final_status"] for item in records).items())
        ),
    }


def main() -> int:
    try:
        fixture = load_fixture()
        gate = load_exp005_gate()
    except (ValueError, OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"EXP-009 input error: {exc}", file=sys.stderr)
        return 2
    claim = f"{CLAIM_BASE} {exp005_gate_sentence(gate)}"
    memory_view = sorted(
        (setting, pattern, decision) for (setting, pattern), decision in MEMORY_STORE.items()
    )
    memory_before = stable_digest(memory_view)
    records = run_simulation(fixture)
    memory_after = stable_digest(
        sorted(
            (setting, pattern, decision) for (setting, pattern), decision in MEMORY_STORE.items()
        )
    )
    if memory_before != memory_after:
        print("EXP-009 safety failure: synthetic memory store changed", file=sys.stderr)
        return 3

    OUT.mkdir(parents=True, exist_ok=True)
    traces_path = OUT / "dialogue_traces.json"
    write_json(
        traces_path,
        {
            "experiment": "EXP-009",
            "fixture_version": fixture["fixture_version"],
            "evidence_classification": SYNTHETIC_TAG,
            "records": records,
        },
    )
    summary = {
        "experiment": "EXP-009 H-Verify seeded-conflict dry run",
        "claim_scope": claim,
        "fixture_version": fixture["fixture_version"],
        "evidence_classification": SYNTHETIC_TAG,
        "memory_store_sha256_before": memory_before,
        "memory_store_sha256_after": memory_after,
        "metrics": metric_summary(records),
        "results": records,
    }
    summary_path = OUT / "summary.json"
    write_json(summary_path, summary)
    lines = [
        "# EXP-009 Seeded Conflict Rule Tests",
        "",
        f"Claim scope: {claim}",
        "",
        f"Evidence classification: `{SYNTHETIC_TAG}`; fixture version `{fixture['fixture_version']}`.",
        "Overrides are escalated pending human adjudication and are never approved by this experiment.",
        "",
        "| ID | Expected conflict | Detected rules | Final status |",
        "| --- | :---: | --- | --- |",
    ]
    for record in records:
        lines.append(
            f"| {record['id']} | {record['expected_conflict']} | {', '.join(record['detected_rules']) or 'none'} | "
            f"{record['final_status']} |"
        )
    metrics = summary["metrics"]
    lines.extend(
        [
            "",
            "## Synthetic rule-test confusion counts",
            "",
            f"- True positives: {metrics['true_positives']}",
            f"- False positives: {metrics['false_positives']}",
            f"- False negatives: {metrics['false_negatives']}",
            f"- True negatives: {metrics['true_negatives']}",
        ]
    )
    summary_md = OUT / "summary.md"
    summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_experiment_manifest(
        OUT,
        experiment_id="EXP-009",
        experiment_version="2.0",
        config_version=f"synthetic-fixture-{fixture['fixture_version']}",
        claim_scope=claim,
        script_path=Path(__file__),
        inputs=[FIXTURE],
        outputs=[traces_path, summary_path, summary_md],
        config={
            "fixture_version": fixture["fixture_version"],
            "evidence_classification": SYNTHETIC_TAG,
            "override_behavior": "escalated_pending_adjudication",
        },
        metric_schema={
            "true_positives": "synthetic expected-conflict seeds with one or more deterministic findings",
            "false_positives": "synthetic non-conflict seeds with a deterministic finding",
            "final_status_counts": "separate resolved/escalated/timed-out/still-conflicted states",
        },
    )
    print(f"EXP-009 done: TP={metrics['true_positives']} FP={metrics['false_positives']} -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
