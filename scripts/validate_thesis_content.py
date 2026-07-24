#!/usr/bin/env python3
"""Validate thesis terminology, evidence gates, traceability, and claim language."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from check_thesis_citations import audit as audit_citations


ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "thesis/chapters"
SNAPSHOT = (
    ROOT / "docs/research/thesis-evidence/thesis-evidence-snapshot-v1.json"
)
REGISTRY = ROOT / "experiments/registry.md"


def validate() -> list[str]:
    errors: list[str] = []
    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(CHAPTER_DIR.glob("*.md"))
    )
    prohibited = {
        "unqualified improved accuracy": re.compile(
            r"\b(?:has|have|had|is|was|were)\s+improved accuracy\b", re.I
        ),
        "proven accuracy improvement": re.compile(
            r"\baccuracy improvement\s+(?:is|was|has been)\s+"
            r"(?:proven|demonstrated|established)\b",
            re.I,
        ),
        "guaranteed accuracy": re.compile(r"\bguarante(?:e|ed|es)\s+accuracy\b", re.I),
        "proven generalization": re.compile(r"\bproven generalization\b", re.I),
        "internal URI": re.compile(
            r"file:///|codex-file-citation|oai-mem-citation", re.I
        ),
        "placeholder": re.compile(r"\b(?:TODO|TBD|LOREM IPSUM)\b", re.I),
    }
    for label, pattern in prohibited.items():
        if pattern.search(combined):
            errors.append(f"thesis contains forbidden {label}")

    required_terms = [
        "Agent 4",
        "Human Judgment Memory",
        "advisory",
        "non-destructive",
        "generalization-safe",
        "sealed holdout",
    ]
    for term in required_terms:
        if term.casefold() not in combined.casefold():
            errors.append(f"required thesis term is missing: {term}")

    label_gate = data["labelGate"]
    if label_gate["candidateRows"] != 24:
        errors.append("canonical candidate-row count must remain 24")
    if label_gate["generalizationSafeLabels"] != 0:
        errors.append("no independent generalization-safe label may be inferred")
    if data["evidence"]["memoryInformedChanges"]["value"] != 0:
        errors.append("current comparison must remain at zero classification changes")
    if any(
        value is not None
        for key, value in data["metrics"]["currentResults"].items()
        if key != "status"
    ):
        errors.append("performance metrics must remain null at safe N=0")

    expected_decisions = [f"M-{number:02d}" for number in range(1, 7)]
    decisions = data.get("decisionDependencies", [])
    if [item.get("id") for item in decisions] != expected_decisions:
        errors.append("decision dependency register must contain M-01 through M-06")
    for decision in decisions:
        if decision.get("outcome") != "Deferred":
            errors.append(
                f"{decision.get('id')} must remain Deferred without an explicit outcome"
            )
        if decision.get("confirmationStatus") != "unconfirmed":
            errors.append(
                f"{decision.get('id')} must remain unconfirmed without a signed record"
            )

    expected_research = ["E-RQ1", "E-RQ2", "E-RQ3", "H1", "H2", "H3", "H4"]
    trace = data["researchFrame"].get("traceability", [])
    if [row.get("id") for row in trace] != expected_research:
        errors.append("RQ/hypothesis traceability must cover E-RQ1-E-RQ3 and H1-H4")
    experiment_ids = {item["id"] for item in data["experiments"]}
    decision_ids = {item["id"] for item in decisions}
    chapter_ids = {item["chapter"] for item in data["chapterTraceability"]}
    for row in trace:
        if not set(row["experimentIds"]) <= experiment_ids:
            errors.append(f"{row['id']} has an unknown experiment reference")
        if not set(row["decisionIds"]) <= decision_ids:
            errors.append(f"{row['id']} has an unknown decision reference")
        if not set(row["chapterIds"]) <= chapter_ids:
            errors.append(f"{row['id']} has an unknown chapter reference")
    for baseline in data["baselines"]:
        if baseline["behaviorChanged"]:
            errors.append(f"{baseline['id']} cannot change baseline behavior")
        if not set(baseline["decisionIds"]) <= decision_ids:
            errors.append(f"{baseline['id']} has an unknown decision reference")

    if [item.get("id") for item in data.get("riskGates", [])] != [
        "RISK-LEAKAGE",
        "RISK-SMALL-N",
        "RISK-OVERFIT",
        "RISK-EXTERNAL",
    ]:
        errors.append("risk gates must cover leakage, small-N, overfit, and external validity")

    registry = REGISTRY.read_text(encoding="utf-8")
    trace_experiments = {
        experiment
        for chapter in data["chapterTraceability"]
        for experiment in chapter["experiments"]
    }
    for number in range(19, 28):
        experiment_id = f"EXP-{number:03d}"
        if registry.count(f"| {experiment_id} |") != 1:
            errors.append(f"{experiment_id} must appear exactly once in the registry")
        if experiment_id not in trace_experiments:
            errors.append(f"{experiment_id} is missing from chapter traceability")

    appendix = (CHAPTER_DIR / "appendix-a-supplementary.md").read_text(
        encoding="utf-8"
    )
    if "RQ and hypothesis traceability" not in appendix:
        errors.append("appendix is missing the RQ and hypothesis traceability table")

    citation_result = audit_citations()
    errors.extend(str(error) for error in citation_result["errors"])
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("thesis content validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("thesis content validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
