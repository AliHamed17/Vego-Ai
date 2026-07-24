#!/usr/bin/env python3
"""Validate the thesis evidence snapshot and its hard research gates."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import hashlib
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = (
    ROOT
    / "docs/research/thesis-evidence/thesis-evidence-snapshot-v1.json"
)
PROGRAM_STATUS = ROOT / "docs/research/h-layer/program-status-snapshot-v1.json"
SCHEMA = ROOT / "schemas/thesis-evidence-snapshot-v1.schema.json"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def find_duplicates(values: list[str]) -> list[str]:
    return sorted({value for value in values if values.count(value) > 1})


def validate_json_schema(data: dict[str, Any], errors: list[str]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    for issue in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in issue.absolute_path) or "<root>"
        errors.append(f"schema {location}: {issue.message}")


def validate() -> list[str]:
    errors: list[str] = []
    if not SNAPSHOT.exists():
        return [f"missing snapshot: {SNAPSHOT.relative_to(ROOT)}"]

    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    status = json.loads(PROGRAM_STATUS.read_text(encoding="utf-8"))
    validate_json_schema(data, errors)

    if data.get("schemaVersion") != "ThesisEvidenceSnapshot-v1":
        errors.append("unexpected schemaVersion")
    source_revision = data.get("sourceRevision", "")
    ancestor = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "merge-base",
            "--is-ancestor",
            source_revision,
            "HEAD",
        ],
        check=False,
    )
    if ancestor.returncode != 0:
        errors.append("sourceRevision is not an ancestor of current HEAD")
    current_hashes: dict[str, str] = {}
    for relative_path, recorded_hash in data.get("sourceHashes", {}).items():
        path = ROOT / relative_path
        if not path.is_file():
            errors.append(f"source hash points to missing file: {relative_path}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        current_hashes[relative_path] = digest
        if digest != recorded_hash:
            errors.append(f"source hash drift: {relative_path}")
        committed = subprocess.run(
            [
                "git",
                "-C",
                str(ROOT),
                "show",
                f"{source_revision}:{relative_path}",
            ],
            check=False,
            capture_output=True,
        )
        if committed.returncode != 0:
            errors.append(
                f"source file is missing from sourceRevision: {relative_path}"
            )
        elif hashlib.sha256(committed.stdout).hexdigest() != recorded_hash:
            errors.append(
                f"sourceRevision hash differs: {relative_path}"
            )
    tree_digest = hashlib.sha256()
    for relative_path, digest in sorted(current_hashes.items()):
        tree_digest.update(relative_path.encode("utf-8"))
        tree_digest.update(b"\0")
        tree_digest.update(digest.encode("ascii"))
        tree_digest.update(b"\n")
    if tree_digest.hexdigest() != data.get("sourceTreeHash"):
        errors.append("sourceTreeHash differs from current canonical sources")
    if data.get("canonicalSourcesDirty") is not False:
        errors.append("canonicalSourcesDirty must be false for publication")
    if data["programSnapshot"]["latestAcceptedIteration"] != status[
        "latestAcceptedIteration"
    ]["iteration"]:
        errors.append("latest accepted iteration differs from ProgramStatusSnapshot-v1")
    if data["programSnapshot"]["latestAcceptedRunId"] != status[
        "latestAcceptedIteration"
    ]["runId"]:
        errors.append("latest accepted run ID differs from ProgramStatusSnapshot-v1")

    label_gate = data["labelGate"]
    program_gate = status["exp005Gate"]
    expected_pairs = {
        "candidateRows": "candidateRows",
        "suppliedLabels": "suppliedLabels",
        "validLabels": "validLabels",
        "generalizationSafeLabels": "generalizationSafeValidLabels",
    }
    for thesis_key, program_key in expected_pairs.items():
        if label_gate[thesis_key] != program_gate[program_key]:
            errors.append(
                f"labelGate.{thesis_key} differs from ProgramStatusSnapshot-v1"
            )
    label_counts = [
        label_gate["generalizationSafeLabels"],
        label_gate["validLabels"],
        label_gate["suppliedLabels"],
        label_gate["candidateRows"],
    ]
    if label_counts != sorted(label_counts):
        errors.append(
            "label counts must satisfy safe <= valid <= supplied <= candidate"
        )

    if label_gate["developmentRows"] + label_gate["sealedHoldoutRows"] != label_gate[
        "candidateRows"
    ]:
        errors.append("development plus holdout rows must equal candidate rows")
    if label_gate["externalTarget"] < label_gate["externalMinimum"]:
        errors.append("external target must be at least the external minimum")

    current = data["metrics"]["currentResults"]
    accuracy_fields = [
        "originalAccuracy",
        "candidateAccuracy",
        "originalMacroF1",
        "candidateMacroF1",
        "netCorrection",
        "pairedPValue",
    ]
    if label_gate["generalizationSafeLabels"] == 0:
        if label_gate["accuracyStatus"] != "NOT YET COMPUTABLE":
            errors.append("zero-label gate must say NOT YET COMPUTABLE")
        if current["status"] != "NOT YET COMPUTABLE":
            errors.append("current result status must be NOT YET COMPUTABLE")
        for field in accuracy_fields:
            if current[field] is not None:
                errors.append(f"{field} must be null while safe N=0")

    baseline_ids = [item["id"] for item in data["baselines"]]
    if baseline_ids != [f"B{number}" for number in range(6)]:
        errors.append(f"baseline ladder must be B0-B5 in order, got {baseline_ids}")
    if any(item["behaviorChanged"] for item in data["baselines"]):
        errors.append("no baseline stage may claim a behavior change")
    if data["baselines"][3]["status"] != "Proposal — not approved":
        errors.append("B3 candidate policy must remain Proposal — not approved")

    experiment_ids = [item["id"] for item in data["experiments"]]
    expected_experiments = [f"EXP-{number:03d}" for number in range(19, 28)]
    if experiment_ids != expected_experiments:
        errors.append(
            f"experiment roadmap must be EXP-019 through EXP-027, got {experiment_ids}"
        )
    duplicates = find_duplicates(experiment_ids)
    if duplicates:
        errors.append(f"duplicate experiment IDs: {', '.join(duplicates)}")

    rq_ids = [
        item["id"] for item in data["researchFrame"]["evaluationResearchQuestions"]
    ]
    if rq_ids != ["E-RQ1", "E-RQ2", "E-RQ3"]:
        errors.append("evaluation research questions must be E-RQ1 through E-RQ3")
    hypothesis_ids = [
        item["id"] for item in data["researchFrame"]["hypotheses"]
    ]
    if hypothesis_ids != ["H1", "H2", "H3", "H4"]:
        errors.append("hypotheses must be H1 through H4")

    if data["statisticalProtocol"]["pairedBootstrapReplicates"] != 10000:
        errors.append("paired bootstrap must use 10,000 replicates")
    if data["statisticalProtocol"]["pairedBootstrapSeed"] != 20260721:
        errors.append("paired bootstrap seed must be 20260721")

    source_text = json.dumps(data, ensure_ascii=False).lower()
    prohibited_assertions = [
        r"\baccuracy (?:is|was|has been) improved\b",
        r"\bproven generalization\b",
        r"\bguaranteed accuracy\b",
        r"\breduced human effort at scale\b(?! without)",
        r"\bclinical performance (?:is|was|has been)\b",
    ]
    for pattern in prohibited_assertions:
        if re.search(pattern, source_text):
            errors.append(f"prohibited positive claim matched: {pattern}")

    for chapter in data["chapterTraceability"]:
        path = ROOT / chapter["file"]
        if not path.exists():
            errors.append(f"chapter trace points to missing file: {chapter['file']}")

    protected = status["protectedPathState"]
    if protected["status"] != "PASS" or protected["protectedDiff"]:
        errors.append("protected path state is not PASS/empty")
    if status["decisionState"]["runtimeAuthorization"]:
        errors.append("runtime authorization unexpectedly true")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    args = parser.parse_args()
    errors = validate()
    result = {
        "status": "PASS" if not errors else "FAIL",
        "errorCount": len(errors),
        "errors": errors,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    elif errors:
        print("thesis evidence validation: FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        print("thesis evidence validation: PASS")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
