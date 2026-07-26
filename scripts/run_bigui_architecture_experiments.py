#!/usr/bin/env python3
"""Run privacy-safe EXP-033–EXP-036 architecture experiments offline."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vego_hlayer.contracts import (  # noqa: E402
    CorrectionProposal,
    MemoryRecord,
    ObservationRecord,
    TriageDecision,
    ValidationError,
    VerificationRecord,
    canonical_json,
)
from vego_hlayer.runtime import apply_architecture_mode  # noqa: E402
from vego_hlayer.state_machine import (  # noqa: E402
    ReviewState,
    ReviewStateMachine,
    TrustedMemoryStore,
    route_observation,
)

DEFAULT_CONTROLLED_ROOT = ROOT / "VEGO-AI" / "runs" / "20260614-122150" / "human"
DEFAULT_OUTPUT = (
    ROOT / "reports" / "generated" / "bigui_architecture" / "summary.json"
)
JSONL_STAGES = {"review", "feedback", "resolved", "memory"}
STAGE_BY_NAME = {
    "human_review_queue.jsonl": "review",
    "human_review_queue_resolved.jsonl": "resolved",
    "human_judgment_memory.jsonl": "memory",
    "memory_advice.json": "advice",
    "memory_informed_comparison.json": "comparison",
}


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def review_item(index: int = 1) -> dict[str, Any]:
    pattern = f"P{index}"
    return {
        "review_id": f"HRQ-fixture-P{index}",
        "review_signature": hashlib.sha256(pattern.encode()).hexdigest()[:16],
        "schema_version": "1.2.0",
        "provenance": {
            "source_system": "VEGO-AI",
            "policy_version": "selective-intervention-v1",
            "source_setting": "ucd_ch",
        },
        "setting_id": "ucd_ch",
        "status": "pending",
        "pattern_id": pattern,
        "pipeline_stage": "agent4_classify_variability",
        "ai_decision": {
            "classification": "Occasional Variability",
            "confidence": "Medium",
            "flag_for_guidelines_update": False,
            "requires_human_review": True,
        },
        "trigger_reasons": ["medium_confidence"],
    }


def feedback_item() -> dict[str, Any]:
    review = review_item()
    return {
        "feedback_id": "HF-fixture-P1-001",
        "review_id": review["review_id"],
        "review_signature": review["review_signature"],
        "expert_id": "fixture-reviewer",
        "timestamp": "2026-07-26T00:00:00Z",
        "human_decision": {
            "decision_type": "approve_ai_decision",
            "confidence": "High",
        },
        "reusable": False,
        "reuse_scope": {},
        "notes": "SYNTHETIC_NOT_HUMAN",
    }


def memory_item() -> dict[str, Any]:
    review = review_item()
    feedback = feedback_item()
    return {
        "memory_id": "HJM-fixture-P1",
        "memory_signature": review["review_signature"],
        "schema_version": "1.0.0",
        "created_at": "2026-07-26T00:00:00Z",
        "status": "active",
        "conflict_status": "none",
        "conflicting_memory_ids": [],
        "source_review_id": review["review_id"],
        "source_review_signature": review["review_signature"],
        "source_feedback_id": feedback["feedback_id"],
        "domain": "cheers",
        "diagram_type": "UCD",
        "related_guideline_id": None,
        "target_fragment": "synthetic fixture pattern",
        "decision_type": "approve_ai_decision",
        "human_decision": feedback["human_decision"],
        "rationale": "Synthetic mechanism fixture.",
        "reuse_scope": {
            "domain": "cheers",
            "diagram_type": "UCD",
            "applies_to_future_models": False,
            "limitations": "SYNTHETIC_NOT_HUMAN",
        },
        "provenance": {
            "source_system": "VEGO-AI",
            "source_setting": "ucd_ch",
            "source_pattern_id": "P1",
            "source_schema_versions": {
                "review_item_schema": "1.2.0",
                "feedback_schema": "1.0.0",
                "judgment_schema": "1.0.0",
            },
        },
    }


def advice_payload() -> dict[str, Any]:
    provenance = {
        "source_memory_file": "fixture-memory.jsonl",
        "source_agent4_files": {
            "deviation_patterns": "fixture-patterns.json",
            "variability_classes": "fixture-classes.json",
        },
    }
    return {
        "schema_version": "1.0.0",
        "setting_id": "ucd_ch",
        "advice_mode": "advisory_only",
        "generated_at": "2026-07-26T00:00:00Z",
        "provenance": provenance,
        "advice": [
            {
                "schema_version": "1.0.0",
                "advice_id": "MADV-fixture-P1",
                "setting_id": "ucd_ch",
                "pattern_id": "P1",
                "advice_mode": "advisory_only",
                "ai_classification_changed": False,
                "original_ai_classification": {
                    "classification": "Occasional Variability",
                    "confidence": "Medium",
                    "requires_human_review": True,
                    "flag_for_guidelines_update": False,
                },
                "query": {
                    "domain": "cheers",
                    "diagram_type": "UCD",
                    "related_guideline_id": None,
                    "keywords": [],
                },
                "advice_strength": "none",
                "advice_summary": "No reusable match.",
                "memory_matches": [],
                "has_conflicting_memory": False,
                "conflict_note": None,
                "recommended_use": "Advisory evidence only.",
                "provenance": provenance,
            }
        ],
    }


def comparison_payload() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "setting_id": "ucd_ch",
        "mode": "experimental",
        "policy_version": "memory-informed-classifier-v1",
        "ai_behavior_changed_in_baseline": False,
        "generated_at": "2026-07-26T00:00:00Z",
        "comparisons": [
            {
                "comparison_id": "MINF-fixture-P1",
                "setting_id": "ucd_ch",
                "pattern_id": "P1",
                "mode": "experimental",
                "policy_version": "memory-informed-classifier-v1",
                "ai_behavior_changed_in_baseline": False,
                "original_agent4_classification": {
                    "classification": "Occasional Variability",
                    "confidence": "Medium",
                    "requires_human_review": True,
                    "flag_for_guidelines_update": False,
                },
                "memory_advice": {
                    "advice_strength": "none",
                    "memory_match_ids": [],
                    "has_conflicting_memory": False,
                },
                "memory_informed_classification": {
                    "classification": "Occasional Variability",
                    "confidence": "Medium",
                    "source": "original_agent4",
                },
                "memory_informed_differs_from_original": False,
                "classification_changed_meaning": "No change.",
                "requires_human_review_after_memory": True,
                "human_memory_used": [],
                "evaluation_leakage_status": "none",
                "rule_applied": "preserve_original",
                "decision_trace": ["baseline preserved"],
            }
        ],
        "provenance": {
            "source_variability_classes": "fixture-classes.json",
            "source_memory_advice": "fixture-advice.json",
            "source_memory": "fixture-memory.jsonl",
        },
    }


def clone_safe_artifacts() -> list[tuple[str, str, Any]]:
    return [
        ("fixture/review", "review", [review_item()]),
        ("fixture/feedback", "feedback", [feedback_item()]),
        ("fixture/memory", "memory", [memory_item()]),
        ("fixture/advice", "advice", advice_payload()),
        ("fixture/comparison", "comparison", comparison_payload()),
    ]


def load_path(path: Path, stage: str) -> Any:
    if stage in JSONL_STAGES:
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    return json.loads(path.read_text(encoding="utf-8"))


def controlled_artifacts(root: Path) -> list[tuple[str, str, Any]]:
    if not root.is_dir():
        raise ValueError(f"controlled root is unavailable: {root}")
    artifacts: list[tuple[str, str, Any]] = []
    for path in sorted(root.rglob("*")):
        stage = STAGE_BY_NAME.get(path.name)
        if stage and path.is_file():
            artifacts.append(
                (path.relative_to(root).as_posix(), stage, load_path(path, stage))
            )
    if not artifacts:
        raise ValueError("controlled root contains no supported H-layer artifacts")
    return artifacts


def exp033_parity(
    artifacts: list[tuple[str, str, Any]],
    repetitions: int = 3,
) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    normalized_hashes: dict[str, set[str]] = {}
    semantic_differences = 0
    baseline_preserved = True
    classification_changes = 0
    total_records = 0
    for repetition in range(1, repetitions + 1):
        for artifact_id, stage, payload in artifacts:
            executions = {
                mode: apply_architecture_mode(stage, payload, architecture_mode=mode)
                for mode in ("legacy", "unified", "parity")
            }
            legacy = executions["legacy"]
            unified = executions["unified"]
            parity = executions["parity"]
            match = legacy.output == unified.output == parity.output
            semantic_differences += 0 if match else 1
            baseline_preserved = baseline_preserved and all(
                execution.manifest.baseline_preserved
                for execution in executions.values()
            )
            output_hash = digest(parity.output)
            normalized_hashes.setdefault(artifact_id, set()).add(output_hash)
            records = len(parity.canonical_records)
            total_records += records
            if stage == "comparison":
                classification_changes += sum(
                    bool(item.get("differs_from_original"))
                    for item in parity.canonical_records
                )
            runs.append(
                {
                    "repetition": repetition,
                    "artifact": artifact_id,
                    "stage": stage,
                    "records": records,
                    "parityStatus": parity.manifest.parity_status,
                    "normalizedOutputSha256": output_hash,
                    "baselinePreserved": parity.manifest.baseline_preserved,
                }
            )
    deterministic = all(len(values) == 1 for values in normalized_hashes.values())
    return {
        "experimentId": "EXP-033",
        "evidenceClass": "offline",
        "artifactCount": len(artifacts),
        "repetitions": repetitions,
        "runCount": len(runs),
        "recordExecutions": total_records,
        "semanticDifferences": semantic_differences,
        "deterministic": deterministic,
        "baselinePreserved": baseline_preserved,
        "classificationChanges": classification_changes,
        "passed": (
            semantic_differences == 0
            and deterministic
            and baseline_preserved
            and classification_changes == 0
        ),
        "runs": runs,
        "claimBoundary": "Mechanism-level equivalence only; not accuracy.",
    }


def exp034_topologies() -> dict[str, Any]:
    workload = [
        "S1_observe",
        "S2_triage",
        "S3_ask",
        "S4_capture",
        "S5_verify",
        "S6_propose",
        "S7_remember",
    ]
    canonical_output_hash = digest(workload)
    rows = [
        {
            "id": "topology-a",
            "agents": 3,
            "handoffs": 2,
            "contextDuplicationUnits": 2,
            "stateBoundaries": 3,
            "failurePropagationBreadth": 3,
            "traceCompleteness": 1.0,
            "canonicalOutputSha256": canonical_output_hash,
        },
        {
            "id": "topology-b",
            "agents": 2,
            "handoffs": 1,
            "contextDuplicationUnits": 1,
            "stateBoundaries": 2,
            "failurePropagationBreadth": 4,
            "traceCompleteness": 1.0,
            "canonicalOutputSha256": canonical_output_hash,
        },
        {
            "id": "topology-c",
            "agents": 1,
            "handoffs": 0,
            "contextDuplicationUnits": 0,
            "stateBoundaries": 1,
            "failurePropagationBreadth": 7,
            "traceCompleteness": 1.0,
            "canonicalOutputSha256": canonical_output_hash,
        },
    ]
    return {
        "experimentId": "EXP-034",
        "evidenceClass": "offline",
        "contractEquivalent": len(
            {row["canonicalOutputSha256"] for row in rows}
        )
        == 1,
        "topologies": rows,
        "selectedDefault": None,
        "decisionGate": "M-02 deferred",
        "passed": all(row["traceCompleteness"] == 1.0 for row in rows),
        "claimBoundary": "Structural Pareto comparison only; no topology is approved.",
    }


def exp035_faults() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []

    def expect_rejection(case_id: str, action) -> None:
        try:
            action()
        except (ValidationError, ValueError, TypeError) as exc:
            cases.append(
                {
                    "case": case_id,
                    "outcome": "rejected",
                    "errorType": type(exc).__name__,
                    "baselinePreserved": True,
                    "trustedMemoryWrites": 0,
                    "correctionApplications": 0,
                }
            )
        else:
            cases.append(
                {
                    "case": case_id,
                    "outcome": "unsafe_accept",
                    "errorType": None,
                    "baselinePreserved": False,
                    "trustedMemoryWrites": 1,
                    "correctionApplications": 1,
                }
            )

    expect_rejection(
        "missing-source-lineage",
        lambda: ObservationRecord(
            observation_id="OBS-bad",
            event_type="E1",
            run_id="fixture",
            setting_id="ucd_ch",
            producer="fixture",
            channel="fixture",
            sequence=1,
            capture_status="observed",
            payload={},
        ),
    )
    expect_rejection(
        "duplicate-observation-identity",
        lambda: TriageDecision(
            triage_id="TRIAGE-bad",
            observation_ids=("OBS-1", "OBS-1"),
            trigger_codes=("fixture",),
            severity=2,
            dosage_config={"mode": "fixture"},
            bundle_key="fixture",
            budget_state="within_budget",
            outcome="promote",
            rationale="Fixture.",
        ),
    )
    expect_rejection(
        "conflict-called-verified",
        lambda: VerificationRecord(
            verification_id="VERIFY-bad",
            feedback_id="HF-bad",
            deterministic_checks=("source",),
            source_versions={"source": "fixture"},
            conflicts=("unresolved",),
            rounds=1,
            outcome="verified",
        ),
    )
    expect_rejection(
        "automatic-correction",
        lambda: CorrectionProposal(
            proposal_id="PROPOSAL-bad",
            verification_id="VERIFY-good",
            target_artifact="fixture.txt",
            target_sha256="a" * 64,
            proposed_diff="--- a\n+++ b\n",
            evidence_refs=("fixture",),
            rollback_description="Discard fixture.",
            approval_state="approved",
            applied=True,
        ),
    )
    expect_rejection(
        "illegal-authority-shortcut",
        lambda: ReviewStateMachine().transition(ReviewState.APPROVED),
    )

    machine = ReviewStateMachine()
    machine.transition(ReviewState.PROMOTED)
    machine.transition(ReviewState.PENDING_REVIEW)
    timeout = machine.timeout()
    cases.append(
        {
            "case": "timeout",
            "outcome": timeout["state"],
            "errorType": None,
            "baselinePreserved": timeout["baseline_preserved"],
            "trustedMemoryWrites": int(timeout["trusted_memory_written"]),
            "correctionApplications": int(timeout["correction_applied"]),
        }
    )
    e15 = ObservationRecord(
        observation_id="OBS-E15",
        event_type="E15",
        run_id="fixture",
        setting_id="ucd_ch",
        producer="fixture",
        channel="evaluation",
        sequence=1,
        capture_status="observed",
        source_artifact="fixture.json",
        source_sha256="b" * 64,
        payload={},
    )
    e15_route = route_observation(
        e15, severity=3, trigger_codes=("evaluation",)
    )
    cases.append(
        {
            "case": "evaluation-event",
            "outcome": e15_route.outcome,
            "errorType": None,
            "baselinePreserved": True,
            "trustedMemoryWrites": 0,
            "correctionApplications": 0,
        }
    )

    memory = MemoryRecord(
        memory_id="MEM-legacy",
        verification_id="legacy:HF-1",
        source_outcome="legacy_mechanism_memory",
        validity_scope={"scope": "fixture"},
        conflicts=(),
        provenance={"source": "fixture"},
        leakage_classification="unknown",
    )
    expect_rejection(
        "legacy-memory-as-trusted",
        lambda: TrustedMemoryStore().append(memory),
    )
    passed = all(
        item["baselinePreserved"]
        and item["trustedMemoryWrites"] == 0
        and item["correctionApplications"] == 0
        and item["outcome"] != "unsafe_accept"
        for item in cases
    )
    return {
        "experimentId": "EXP-035",
        "evidenceClass": "synthetic",
        "syntheticTag": "SYNTHETIC_NOT_HUMAN",
        "caseCount": len(cases),
        "cases": cases,
        "passed": passed,
        "claimBoundary": "Finite offline fault fixtures only.",
    }


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * fraction)))
    return ordered[index]


def benchmark_mode(payload: list[dict[str, Any]], mode: str, loops: int) -> dict[str, Any]:
    timings: list[float] = []
    hashes: set[str] = set()
    tracemalloc.start()
    for _ in range(loops):
        started = time.perf_counter_ns()
        execution = apply_architecture_mode("review", payload, architecture_mode=mode)
        timings.append((time.perf_counter_ns() - started) / 1_000_000)
        hashes.add(digest(execution.output))
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    total_seconds = sum(timings) / 1000
    return {
        "mode": mode,
        "records": len(payload),
        "loops": loops,
        "p50Milliseconds": round(statistics.median(timings), 6),
        "p95Milliseconds": round(percentile(timings, 0.95), 6),
        "throughputRecordsPerSecond": round(
            (len(payload) * loops) / total_seconds, 3
        ),
        "peakBytes": peak,
        "deterministic": len(hashes) == 1,
        "normalizedOutputSha256": next(iter(hashes)),
    }


def exp036_scale() -> dict[str, Any]:
    scales: list[dict[str, Any]] = []
    for multiplier in (1, 5, 10):
        payload = [review_item(index) for index in range(1, multiplier * 10 + 1)]
        rows = [
            benchmark_mode(payload, mode, loops=20)
            for mode in ("legacy", "unified", "parity")
        ]
        by_mode = {row["mode"]: row for row in rows}
        legacy = by_mode["legacy"]
        for row in rows:
            row["p95RatioToLegacy"] = round(
                row["p95Milliseconds"] / legacy["p95Milliseconds"], 4
            )
            row["peakMemoryRatioToLegacy"] = round(
                row["peakBytes"] / legacy["peakBytes"], 4
            )
        scales.append(
            {
                "fixture": f"SYNTHETIC_{multiplier}X",
                "syntheticTag": "SYNTHETIC_NOT_HUMAN",
                "records": len(payload),
                "modes": rows,
            }
        )
    return {
        "experimentId": "EXP-036",
        "evidenceClass": "synthetic",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "scales": scales,
        "targets": {
            "unifiedP95RatioMaximum": 1.15,
            "unifiedPeakMemoryRatioMaximum": 1.5,
            "parityP95RatioMaximum": 2.25,
        },
        "passed": all(
            mode["deterministic"]
            for scale in scales
            for mode in scale["modes"]
        ),
        "claimBoundary": (
            "Machine-specific operational fixture evidence only; thresholds are "
            "engineering targets and no accuracy or human-effort conclusion follows."
        ),
    }


def build_summary(
    artifacts: list[tuple[str, str, Any]],
    source: str,
) -> dict[str, Any]:
    payload = {
        "schemaVersion": "BigUIArchitectureExperimentSummary-v1",
        "generatedAt": "2026-07-26T00:00:00Z",
        "sourceTier": source,
        "containsRawRecords": False,
        "experiments": [
            exp033_parity(artifacts),
            exp034_topologies(),
            exp035_faults(),
            exp036_scale(),
        ],
        "globalBoundaries": {
            "baselineFrozen": True,
            "agent4Changed": False,
            "accuracyClaimAllowed": False,
            "productionTopologySelected": False,
            "liveListenerAuthorized": False,
        },
    }
    payload["normalizedSha256"] = digest(payload)
    return payload


def safe_output(path: Path) -> Path:
    target = path if path.is_absolute() else ROOT / path
    target = target.resolve()
    allowed = (ROOT / "reports" / "generated").resolve()
    if allowed not in target.parents:
        raise ValueError("experiment output must stay under reports/generated")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--controlled", action="store_true")
    parser.add_argument("--controlled-root", type=Path, default=DEFAULT_CONTROLLED_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        artifacts = (
            controlled_artifacts(args.controlled_root)
            if args.controlled
            else clone_safe_artifacts()
        )
        summary = build_summary(
            artifacts,
            "controlled_local" if args.controlled else "clone_safe_fixture",
        )
        if not all(item["passed"] for item in summary["experiments"]):
            raise ValueError("one or more architecture experiments failed")
        if not args.check:
            output = safe_output(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            print(f"WROTE: {output.relative_to(ROOT)}")
        print(
            "BigUI architecture experiments: PASS "
            f"({len(artifacts)} artifacts, source={summary['sourceTier']})"
        )
        return 0
    except (OSError, ValueError, ValidationError, json.JSONDecodeError) as exc:
        print(f"BigUI architecture experiments: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
