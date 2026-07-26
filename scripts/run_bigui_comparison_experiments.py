#!/usr/bin/env python3
"""Run EXP-037–EXP-040 baseline and comparison experiments.

The tracked output is a privacy-safe, deterministic projection.  The original
paper PDF remains ignored and local; ``--paper-pdf`` verifies its recorded hash
without making the PDF a clone-safe dependency.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vego_bigui.store import canonical_sha256, load_bundles  # noqa: E402

PAPER = (
    ROOT / "docs" / "research" / "bigui" / "paper-baseline-snapshot-v1.json"
)
THESIS = (
    ROOT
    / "docs"
    / "research"
    / "thesis-evidence"
    / "thesis-evidence-snapshot-v1.json"
)
ARCHITECTURE = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "architecture-fixture-results-v1.json"
)
ACCEPTED_RUNS = ROOT / "experiments" / "accepted-runs"
CURRENT_RUN_INDEX = ROOT / "experiments" / "current-run-index-v1.json"
SCHEMAS = ROOT / "schemas"
OUTPUT = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "baseline-comparison-results-v1.json"
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metric(
    metric_id: str,
    value: Any,
    numerator: int | float | None,
    denominator: int | float | None,
    unit: str,
    *,
    direction: str = "neutral",
    evidence_class: str,
    claim_boundary: str,
    dimensions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "metricId": metric_id,
        "value": value,
        "numerator": numerator,
        "denominator": denominator,
        "unit": unit,
        "direction": direction,
        "evidenceClass": evidence_class,
        "dimensions": dimensions or {},
        "claimBoundary": claim_boundary,
    }


def latest_bundle(
    bundles: list[dict[str, Any]],
    experiment_id: str,
    current_run_index: dict[str, Any],
) -> dict[str, Any]:
    current_run_id = next(
        (
            item["runId"]
            for item in current_run_index["currentRuns"]
            if item["experimentId"] == experiment_id
        ),
        None,
    )
    candidates = [
        item
        for item in bundles
        if item["envelope"]["experimentId"] == experiment_id
        and item["envelope"]["acceptanceStatus"] == "accepted"
        and item["envelope"]["runId"] == current_run_id
    ]
    if len(candidates) != 1:
        raise ValueError(
            f"current run index did not resolve exactly one {experiment_id} bundle"
        )
    return candidates[0]


def observation_index(bundle: dict[str, Any]) -> dict[tuple[str, str], Any]:
    result: dict[tuple[str, str], Any] = {}
    for observation in bundle["metricObservations"]:
        dimensions = json.dumps(
            observation["dimensions"],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        result[(observation["metricId"], dimensions)] = observation
    return result


def dimensional_rows(
    bundle: dict[str, Any],
    metric_id: str,
    dimension: str,
) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for observation in bundle["metricObservations"]:
        if observation["metricId"] != metric_id:
            continue
        key = observation["dimensions"].get(dimension)
        if key is not None:
            rows[str(key)] = observation
    return rows


def build() -> dict[str, Any]:
    paper = load_json(PAPER)
    thesis = load_json(THESIS)
    architecture = load_json(ARCHITECTURE)
    jsonschema.Draft202012Validator(
        load_json(SCHEMAS / "paper-baseline-snapshot-v1.schema.json"),
        format_checker=jsonschema.FormatChecker(),
    ).validate(paper)
    bundles = load_bundles(ACCEPTED_RUNS, SCHEMAS)
    current_run_index = load_json(CURRENT_RUN_INDEX)
    dependency_experiments = {
        "EXP-007",
        "EXP-033",
        "EXP-034",
        "EXP-035",
        "EXP-036",
    }

    current = {
        "caseModelTotal": thesis["evidence"]["studentModels"]["value"],
        "patternTotal": thesis["evidence"]["agent4Patterns"]["value"],
        "substantialTotal": thesis["evidence"]["substantialPatterns"]["value"],
        "occasionalTotal": thesis["evidence"]["occasionalPatterns"]["value"],
        "undeterminedTotal": thesis["evidence"]["undeterminedPatterns"]["value"],
        "comparisonRows": thesis["evidence"]["comparisonRows"]["value"],
        "classificationChanges": thesis["evidence"]["memoryInformedChanges"]["value"],
        "safeLabels": thesis["labelGate"]["generalizationSafeLabels"],
    }
    capabilities = paper["humanJudgmentCapabilities"]
    paper_capabilities = sum(item["paperBaseline"] for item in capabilities)
    current_capabilities = sum(item["currentExtension"] for item in capabilities)

    paper_boundary = (
        "Paper counts are historical version markers. They do not share an "
        "independent classification ground truth with the current H-layer."
    )
    capability_boundary = (
        "Implemented capability coverage demonstrates architectural extension, "
        "not classification accuracy or human-effort improvement."
    )
    exp037_metrics = [
        metric(
            "PAPER_CASE_MODEL_COUNT",
            paper["evaluationScope"]["caseModelTotal"],
            paper["evaluationScope"]["caseModelTotal"],
            paper["evaluationScope"]["caseModelTotal"],
            "case models",
            evidence_class="historical",
            claim_boundary=paper_boundary,
        ),
        metric(
            "CURRENT_CASE_MODEL_COUNT",
            current["caseModelTotal"],
            current["caseModelTotal"],
            current["caseModelTotal"],
            "case models",
            evidence_class="mechanism",
            claim_boundary=paper_boundary,
        ),
        metric(
            "PAPER_PATTERN_COUNT",
            paper["phaseD"]["patternTotal"],
            paper["phaseD"]["patternTotal"],
            paper["phaseD"]["patternTotal"],
            "patterns",
            evidence_class="historical",
            claim_boundary=paper_boundary,
        ),
        metric(
            "CURRENT_PATTERN_COUNT",
            current["patternTotal"],
            current["patternTotal"],
            current["patternTotal"],
            "patterns",
            evidence_class="mechanism",
            claim_boundary=paper_boundary,
        ),
        metric(
            "PAPER_HUMAN_JUDGMENT_CAPABILITY_COVERAGE",
            paper_capabilities / len(capabilities),
            paper_capabilities,
            len(capabilities),
            "proportion",
            direction="higher_is_better",
            evidence_class="historical",
            claim_boundary=capability_boundary,
        ),
        metric(
            "CURRENT_HUMAN_JUDGMENT_CAPABILITY_COVERAGE",
            current_capabilities / len(capabilities),
            current_capabilities,
            len(capabilities),
            "proportion",
            direction="higher_is_better",
            evidence_class="mechanism",
            claim_boundary=capability_boundary,
        ),
        metric(
            "PAPER_CURRENT_CLASSIFICATION_COMPARISON_ELIGIBLE",
            0,
            0,
            1,
            "boolean",
            direction="target",
            evidence_class="offline",
            claim_boundary=(
                "Current classification accuracy remains null at safe N=0; "
                "the paper's qualitative author assessment is not a compatible "
                "independent benchmark."
            ),
        ),
    ]

    exp033 = latest_bundle(bundles, "EXP-033", current_run_index)
    exp035 = latest_bundle(bundles, "EXP-035", current_run_index)
    exp033_index = observation_index(exp033)
    exp035_index = observation_index(exp035)
    empty_dimensions = "{}"

    def accepted_value(
        index: dict[tuple[str, str], Any],
        metric_id: str,
    ) -> Any:
        try:
            return index[(metric_id, empty_dimensions)]["value"]
        except KeyError as exc:
            raise ValueError(f"accepted metric is missing: {metric_id}") from exc

    scorecard = [
        {
            "dimension": "human_judgment_capabilities",
            "paperBaseline": paper_capabilities / len(capabilities),
            "current": current_capabilities / len(capabilities),
            "status": "demonstrated",
            "evidence": "EXP-037",
            "interpretation": "Seven explicit H-layer capabilities were added.",
        },
        {
            "dimension": "semantic_parity",
            "paperBaseline": None,
            "current": accepted_value(
                exp033_index, "ARCH_SEMANTIC_PARITY_RATE"
            ),
            "status": "demonstrated",
            "evidence": "EXP-033",
            "interpretation": "Legacy and unified outputs match on the accepted parity cohort.",
        },
        {
            "dimension": "deterministic_replay",
            "paperBaseline": None,
            "current": accepted_value(
                exp033_index, "ARCH_REPLAY_DETERMINISM"
            ),
            "status": "demonstrated",
            "evidence": "EXP-033",
            "interpretation": "The accepted parity run reproduced the same normalized outputs.",
        },
        {
            "dimension": "fault_authority_safety",
            "paperBaseline": None,
            "current": accepted_value(
                exp035_index, "SAFETY_FAULT_CASE_PASS_RATE"
            ),
            "status": "demonstrated",
            "evidence": "EXP-035",
            "interpretation": "All bounded fault fixtures preserved authority and baseline behavior.",
        },
        {
            "dimension": "classification_accuracy",
            "paperBaseline": None,
            "current": None,
            "status": "not_yet_measurable",
            "evidence": "EXP-005/EXP-012",
            "interpretation": "Independent safe labels: 0/24.",
        },
        {
            "dimension": "human_effort",
            "paperBaseline": None,
            "current": None,
            "status": "not_yet_measurable",
            "evidence": "EXP-026",
            "interpretation": "Queue counts are not time or effort evidence.",
        },
    ]
    demonstrated = sum(item["status"] == "demonstrated" for item in scorecard)
    exp038_metrics = [
        metric(
            "ARCHITECTURE_SCORECARD_DEMONSTRATED_DIMENSIONS",
            demonstrated,
            demonstrated,
            len(scorecard),
            "dimensions",
            evidence_class="offline",
            claim_boundary=(
                "Dimensions remain separate; no arbitrary weighted global "
                "improvement score is calculated."
            ),
        ),
        metric(
            "ARCHITECTURE_SCORECARD_UNMEASURED_DIMENSIONS",
            len(scorecard) - demonstrated,
            len(scorecard) - demonstrated,
            len(scorecard),
            "dimensions",
            evidence_class="offline",
            claim_boundary=(
                "Classification and effort remain visibly unmeasured."
            ),
        ),
    ]

    exp007 = latest_bundle(bundles, "EXP-007", current_run_index)
    exp034 = latest_bundle(bundles, "EXP-034", current_run_index)
    exp036 = latest_bundle(bundles, "EXP-036", current_run_index)
    routing_load = dimensional_rows(exp007, "ROUTING_EVENT_LOAD", "mode")
    routing_coverage = dimensional_rows(
        exp007, "ROUTING_WEIGHTED_COVERAGE", "mode"
    )
    routing_high = dimensional_rows(
        exp007, "ROUTING_HIGH_SEVERITY_COVERAGE", "mode"
    )

    routing_pairs = []
    for left, right in (
        ("threshold_sev3", "threshold_sev2"),
        ("threshold_sev2", "threshold_sev1"),
    ):
        routing_pairs.append(
            {
                "family": "routing",
                "left": left,
                "right": right,
                "directlyComparable": True,
                "deltas": {
                    "weightedCoverage": (
                        routing_coverage[right]["value"]
                        - routing_coverage[left]["value"]
                    ),
                    "eventLoad": (
                        routing_load[right]["value"]
                        - routing_load[left]["value"]
                    ),
                    "highSeverityCoverage": (
                        routing_high[right]["value"]
                        - routing_high[left]["value"]
                    ),
                },
                "interpretation": (
                    "Higher-severity coverage is purchased with additional "
                    "review load; this is a Pareto trade-off, not a global win."
                ),
            }
        )

    topology_metrics = {
        metric_id: dimensional_rows(exp034, metric_id, "topology")
        for metric_id in (
            "TOPOLOGY_HANDOFF_COUNT",
            "TOPOLOGY_CONTEXT_BYTES",
            "TOPOLOGY_STATE_BOUNDARIES",
            "TOPOLOGY_FAILURE_BREADTH",
            "TOPOLOGY_TRACE_COMPLETENESS",
        )
    }
    topology_pairs = []
    for left, right in (
        ("topology-a", "topology-b"),
        ("topology-b", "topology-c"),
        ("topology-a", "topology-c"),
    ):
        deltas = {
            metric_id: rows[right]["value"] - rows[left]["value"]
            for metric_id, rows in topology_metrics.items()
        }
        topology_pairs.append(
            {
                "family": "topology",
                "left": left,
                "right": right,
                "directlyComparable": True,
                "deltas": deltas,
                "interpretation": (
                    "Fewer handoffs and state boundaries increase the breadth "
                    "affected by a single-agent failure; M-02 remains deferred."
                ),
            }
        )

    latency_rows = dimensional_rows(
        exp036, "ARCH_P95_RATIO_TO_LEGACY", "mode"
    )
    runtime_pairs = []
    for mode in ("unified", "parity"):
        values = [
            observation["value"]
            for observation in exp036["metricObservations"]
            if observation["metricId"] == "ARCH_P95_RATIO_TO_LEGACY"
            and observation["dimensions"].get("mode") == mode
        ]
        runtime_pairs.append(
            {
                "family": "runtime_mode",
                "left": "legacy",
                "right": mode,
                "directlyComparable": True,
                "deltas": {
                    "meanP95RatioToLegacy": round(
                        sum(values) / len(values), 6
                    ),
                    "maxP95RatioToLegacy": round(max(values), 6),
                },
                "interpretation": (
                    "Machine-specific operational ratio only; it does not "
                    "measure classification validity."
                ),
            }
        )
    del latency_rows

    refused = [
        {
            "family": "classification_validity",
            "left": "paper-author-qualitative-RQ4",
            "right": "current-H-layer",
            "directlyComparable": False,
            "reasons": [
                "The paper RQ4 assessment is qualitative author judgment.",
                "The current safe independent-label denominator is zero.",
                "The compared architecture stages and metric definitions differ.",
            ],
        }
    ]
    comparison_groups = routing_pairs + topology_pairs + runtime_pairs
    exp039_metrics = [
        metric(
            "DIRECT_COMPARISON_GROUPS",
            len(comparison_groups),
            len(comparison_groups),
            len(comparison_groups) + len(refused),
            "comparison groups",
            direction="higher_is_better",
            evidence_class="offline",
            claim_boundary=(
                "Eligibility means the treatment comparison is well-formed; "
                "it does not imply a positive result."
            ),
        ),
        metric(
            "INCOMPATIBLE_COMPARISONS_SUPPRESSED",
            len(refused),
            len(refused),
            len(comparison_groups) + len(refused),
            "comparison groups",
            direction="target",
            evidence_class="offline",
            claim_boundary=(
                "Incompatible paper-to-current accuracy deltas are refused."
            ),
        ),
    ]

    traceability = thesis["researchFrame"]["traceability"]
    hypotheses = thesis["researchFrame"]["hypotheses"]
    supported_hypotheses = sum(
        item["status"] == "Confirmed outcome" for item in hypotheses
    )
    safe_claims = thesis["claimGates"]["safeNow"]
    empirical_claims = (
        thesis["claimGates"]["conditionalAfterLabels"]
        + thesis["claimGates"]["formalImprovement"]
    )
    exp040_metrics = [
        metric(
            "THESIS_SAFE_CURRENT_CLAIMS",
            len(safe_claims),
            len(safe_claims),
            len(safe_claims),
            "claims",
            evidence_class="mechanism",
            claim_boundary=(
                "These claims are limited to mechanism readiness, compatibility, "
                "traceability, and baseline protection."
            ),
        ),
        metric(
            "THESIS_EMPIRICAL_IMPROVEMENT_CLAIMS_READY",
            0,
            0,
            len(empirical_claims),
            "claims",
            direction="higher_is_better",
            evidence_class="offline",
            claim_boundary=(
                "Independent labels, a frozen policy, and external replication "
                "remain required."
            ),
        ),
        metric(
            "THESIS_HYPOTHESES_CONFIRMED",
            supported_hypotheses,
            supported_hypotheses,
            len(hypotheses),
            "hypotheses",
            direction="higher_is_better",
            evidence_class="offline",
            claim_boundary=(
                "No empirical thesis hypothesis is confirmed at safe N=0."
            ),
        ),
        metric(
            "THESIS_TRACEABILITY_RECORDS",
            len(traceability),
            len(traceability),
            len(traceability),
            "records",
            evidence_class="offline",
            claim_boundary=(
                "Traceability completeness is not hypothesis confirmation."
            ),
        ),
    ]

    experiments = [
        {
            "experimentId": "EXP-037",
            "evidenceClass": "offline",
            "executionValid": True,
            "passed": True,
            "metrics": exp037_metrics,
            "details": {
                "paperPhaseA": paper["phaseA"],
                "paperPhaseB": paper["phaseB"],
                "paperPhaseC": paper["phaseC"],
                "paperPhaseD": paper["phaseD"],
                "capabilities": capabilities,
                "countReconciliation": {
                    "caseModels": {
                        "paper": paper["evaluationScope"]["caseModelTotal"],
                        "current": current["caseModelTotal"],
                        "delta": (
                            current["caseModelTotal"]
                            - paper["evaluationScope"]["caseModelTotal"]
                        ),
                        "qualityInterpretation": "not_applicable",
                    },
                    "patterns": {
                        "paper": paper["phaseD"]["patternTotal"],
                        "current": current["patternTotal"],
                        "delta": (
                            current["patternTotal"]
                            - paper["phaseD"]["patternTotal"]
                        ),
                        "qualityInterpretation": "not_applicable",
                    },
                },
            },
            "claimBoundary": paper["comparisonBoundary"],
        },
        {
            "experimentId": "EXP-038",
            "evidenceClass": "offline",
            "executionValid": True,
            "passed": True,
            "metrics": exp038_metrics,
            "details": {"scorecard": scorecard},
            "claimBoundary": (
                "Capability and reliability extension is demonstrated on the "
                "accepted cohorts; classification and effort value remain null."
            ),
        },
        {
            "experimentId": "EXP-039",
            "evidenceClass": "offline",
            "executionValid": True,
            "passed": True,
            "metrics": exp039_metrics,
            "details": {
                "eligibleComparisons": comparison_groups,
                "refusedComparisons": refused,
            },
            "claimBoundary": (
                "Every 'better' statement is metric-specific and accompanied "
                "by its countervailing trade-off and evidence boundary."
            ),
        },
        {
            "experimentId": "EXP-040",
            "evidenceClass": "offline",
            "executionValid": True,
            "passed": True,
            "metrics": exp040_metrics,
            "details": {
                "traceability": traceability,
                "hypotheses": hypotheses,
                "safeClaims": safe_claims,
                "conditionalClaims": empirical_claims,
            },
            "claimBoundary": (
                "Claim readiness is a provenance audit; it cannot replace the "
                "missing independent observations."
            ),
        },
    ]

    payload: dict[str, Any] = {
        "schemaVersion": "BaselineComparisonResults-v1",
        "generatedAt": max(
            paper["generatedAt"],
            thesis["generatedAt"],
            architecture["generatedAt"],
        ),
        "paperBaseline": {
            "sourceSha256": paper["source"]["sha256"],
            "caseModels": paper["evaluationScope"]["caseModelTotal"],
            "patterns": paper["phaseD"]["patternTotal"],
            "substantial": paper["phaseD"]["substantialTotal"],
            "occasional": paper["phaseD"]["occasionalTotal"],
            "rq4Assessment": paper["phaseD"]["assessmentMethod"],
        },
        "currentBaseline": current,
        "comparisonLanes": [
            {
                "id": "CAPABILITY",
                "title": "Human-judgment architecture capability",
                "status": "demonstrated",
                "directlyComparable": True,
                "explanation": (
                    "The paper lacks the seven explicit H-layer capabilities; "
                    "the current implementation exposes and tests them."
                ),
            },
            {
                "id": "RELIABILITY",
                "title": "Parity, replay, and authority safety",
                "status": "demonstrated",
                "directlyComparable": False,
                "explanation": (
                    "These are new architecture properties with accepted "
                    "mechanism evidence, not paper accuracy metrics."
                ),
            },
            {
                "id": "COUNTS",
                "title": "Paper and repository version counts",
                "status": "contextual_only",
                "directlyComparable": False,
                "explanation": (
                    "The paper draft reports 178 models and 26 patterns; the "
                    "current locked snapshot reports 179 and 27. A larger count "
                    "does not mean higher quality."
                ),
            },
            {
                "id": "CLASSIFICATION_VALIDITY",
                "title": "Classification accuracy and macro-F1",
                "status": "not_yet_measurable",
                "directlyComparable": False,
                "explanation": (
                    "The current independent safe-label denominator is zero."
                ),
            },
            {
                "id": "HUMAN_EFFORT",
                "title": "Human effort and review-time value",
                "status": "not_yet_measurable",
                "directlyComparable": False,
                "explanation": (
                    "A controlled participant study has not been run."
                ),
            },
        ],
        "experiments": experiments,
        "sources": {
            PAPER.relative_to(ROOT).as_posix(): file_sha256(PAPER),
            THESIS.relative_to(ROOT).as_posix(): file_sha256(THESIS),
            ARCHITECTURE.relative_to(ROOT).as_posix(): file_sha256(ARCHITECTURE),
            "experiments/current-run-index-v1.json#comparison-dependencies": (
                canonical_sha256(
                    [
                        item
                        for item in current_run_index["currentRuns"]
                        if item["experimentId"] in dependency_experiments
                    ]
                )
            ),
            "experiments/accepted-runs": canonical_sha256(
                sorted(
                    {
                        item["_bundlePath"]: item["_bundleSha256"]
                        for item in bundles
                        if item["envelope"]["experimentId"]
                        in dependency_experiments
                    }.items()
                )
            ),
        },
        "claimBoundary": (
            "The current proof baseline is multidimensional: capability and "
            "mechanism reliability are demonstrated; classification accuracy, "
            "generalization, and effort improvement remain unmeasured."
        ),
        "normalizedSha256": "",
    }
    normalized = dict(payload)
    normalized["normalizedSha256"] = ""
    payload["normalizedSha256"] = canonical_sha256(normalized)
    jsonschema.Draft202012Validator(
        load_json(SCHEMAS / "baseline-comparison-results-v1.schema.json"),
        format_checker=jsonschema.FormatChecker(),
    ).validate(payload)
    return payload


def serialized(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--refresh", action="store_true")
    parser.add_argument(
        "--paper-pdf",
        type=Path,
        help="Optional controlled local PDF whose SHA-256 must match the snapshot.",
    )
    args = parser.parse_args()
    try:
        if args.paper_pdf:
            paper = load_json(PAPER)
            if file_sha256(args.paper_pdf) != paper["source"]["sha256"]:
                raise ValueError("controlled paper PDF hash does not match snapshot")
            print("Paper PDF hash: PASS")
        content = serialized(build())
        if args.check:
            if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
                raise ValueError(
                    f"{OUTPUT.relative_to(ROOT)} is stale; run with --refresh"
                )
            print("EXP-037–EXP-040 comparison experiments: PASS")
        else:
            OUTPUT.write_text(content, encoding="utf-8", newline="\n")
            print(f"WROTE: {OUTPUT.relative_to(ROOT)}")
    except (OSError, ValueError, json.JSONDecodeError, jsonschema.ValidationError) as exc:
        print(f"EXP-037–EXP-040 comparison experiments: FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
