"""EXP-010: convergence-bound replay over EXP-009 synthetic dialogue traces."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from hlayer_harness import (
    exp005_gate_sentence,
    experiment_output_dir,
    load_exp005_gate,
    output_root,
    write_experiment_manifest,
    write_json,
)

IN = output_root() / "exp009" / "dialogue_traces.json"
OUT = experiment_output_dir("exp010")
CLAIM_BASE = (
    "Assumption-driven synthetic replay of dialogue bounds; not validation against expert mistakes."
)
SYNTHETIC_TAG = "SYNTHETIC_NOT_HUMAN"


def load_traces(path: Path = IN) -> dict:
    if not path.is_file():
        raise ValueError(f"EXP-009 dialogue traces missing: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        value.get("experiment") != "EXP-009"
        or value.get("evidence_classification") != SYNTHETIC_TAG
    ):
        raise ValueError("EXP-010 accepts only tagged EXP-009 synthetic traces")
    if not isinstance(value.get("records"), list) or not value["records"]:
        raise ValueError("EXP-009 dialogue trace file has no records")
    return value


def outcome_for_bound(record: dict, bound: int) -> str:
    history = record.get("dialogue_history") or []
    if not record.get("detected_conflict"):
        return "passed_no_conflict" if not record.get("expected_conflict") else "still_conflicted"
    if bound < 2 or len(history) < 2:
        return "timed_out_parked"
    final = record.get("final_status") or history[-1].get("outcome")
    mapping = {
        "resolved": "resolved",
        "escalated_pending_adjudication": "needs_adjudication",
        "timed_out_parked": "timed_out_parked",
        "still_conflicted": "still_conflicted",
        "passed_no_conflict": "passed_no_conflict",
    }
    return mapping.get(final, "still_conflicted")


def simulate_for_bound(records: list[dict], bound: int) -> dict:
    outcomes = [outcome_for_bound(record, bound) for record in records]
    counts = Counter(outcomes)
    total = len(records)
    return {
        "round_bound": bound,
        "total_synthetic_traces": total,
        "resolved": counts["resolved"],
        "passed_no_conflict": counts["passed_no_conflict"],
        "needs_adjudication": counts["needs_adjudication"],
        "timed_out_parked": counts["timed_out_parked"],
        "still_conflicted": counts["still_conflicted"],
        "resolved_rate": round(counts["resolved"] / total, 3),
        "passed_no_conflict_rate": round(counts["passed_no_conflict"] / total, 3),
        "needs_adjudication_rate": round(counts["needs_adjudication"] / total, 3),
        "timed_out_parked_rate": round(counts["timed_out_parked"] / total, 3),
        "still_conflicted_rate": round(counts["still_conflicted"] / total, 3),
        "baseline_preserved_for_nonresolved": True,
    }


def main() -> int:
    try:
        traces = load_traces()
        gate = load_exp005_gate()
    except (ValueError, OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"EXP-010 input error: {exc}", file=sys.stderr)
        return 2
    claim = f"{CLAIM_BASE} {exp005_gate_sentence(gate)}"
    records = sorted(traces["records"], key=lambda record: record["id"])
    results = [simulate_for_bound(records, bound) for bound in (1, 2, 3, 4)]
    summary = {
        "experiment": "EXP-010 convergence-bound sweep",
        "claim_scope": claim,
        "evidence_classification": SYNTHETIC_TAG,
        "source_fixture_version": traces.get("fixture_version"),
        "source_trace_count": len(records),
        "two_round_status": "pilot candidate; not an approved default",
        "interpretation": "Resolution and adjudication are separate outcomes and are never combined as convergence.",
        "results": results,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    summary_path = OUT / "summary.json"
    write_json(summary_path, summary)
    lines = [
        "# EXP-010 Convergence-Bound Sweep",
        "",
        f"Claim scope: {claim}",
        "",
        f"Input: EXP-009 `{SYNTHETIC_TAG}` dialogue traces, fixture version `{traces.get('fixture_version')}`.",
        "Resolution and pending adjudication remain separate; this report makes no 100% convergence claim.",
        "A two-round bound is a pilot candidate only, not an approved default.",
        "",
        "| B | Resolved | Passed no conflict | Needs adjudication | Timed out/parked | Still conflicted |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        lines.append(
            f"| {result['round_bound']} | {result['resolved']} | {result['passed_no_conflict']} | "
            f"{result['needs_adjudication']} | {result['timed_out_parked']} | {result['still_conflicted']} |"
        )
    summary_md = OUT / "summary.md"
    summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_experiment_manifest(
        OUT,
        experiment_id="EXP-010",
        experiment_version="2.0",
        config_version="exp009-trace-bounds-1.0",
        claim_scope=claim,
        script_path=Path(__file__),
        inputs=[IN],
        outputs=[summary_path, summary_md],
        config={"round_bounds": [1, 2, 3, 4], "two_round_status": "pilot candidate"},
        metric_schema={
            "resolved": "synthetic conflicts corrected within the bound",
            "needs_adjudication": "override/conflict traces awaiting human authority; not resolved",
            "timed_out_parked": "bound exhausted with baseline preserved",
        },
    )
    print(f"EXP-010 done: consumed {len(records)} EXP-009 traces -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
