#!/usr/bin/env python3
"""Evaluate frozen VEGO-AI comparators against adjudicated independent labels.

At zero labels the command emits an explicit null-valued gate. It never opens
the sealed holdout unless an approved frozen policy manifest is supplied.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = ROOT / "reports/generated/independent_evidence_v1"
DEFAULT_OUTPUT = ROOT / "reports/generated/independent_evidence_v1/evaluation"
LABELS = [
    "Substantial Variability",
    "Occasional Variability",
    "Undetermined / Needs Review",
]
AUTOMATED_REVIEWER_TOKENS = {
    "ai",
    "chatgpt",
    "claude",
    "codex",
    "gpt",
    "llm",
    "openai",
    "synthetic",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def automated_identity(value: str) -> bool:
    normalized = "".join(character.lower() if character.isalnum() else " " for character in value)
    return bool(set(normalized.split()) & AUTOMATED_REVIEWER_TOKENS)


def null_result(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "IndependentGroundTruthEvaluation-v1",
        "status": "NOT YET COMPUTABLE",
        "stage": "gate_only",
        "candidateRows": manifest["counts"]["candidateRows"],
        "safeGoldLabels": 0,
        "reviewerCountRequired": 2,
        "baseline": {
            "id": "B0-original-agent4",
            "accuracy": None,
            "macroF1": None,
            "balancedAccuracy": None,
            "confusionMatrix": None,
        },
        "currentComparator": {
            "id": "B1-current-m4b1",
            "classificationChanges": 0,
            "accuracy": None,
            "macroF1": None,
            "balancedAccuracy": None,
            "confusionMatrix": None,
        },
        "paired": {
            "bothCorrect": None,
            "baselineOnlyCorrect": None,
            "candidateOnlyCorrect": None,
            "bothWrong": None,
            "netCorrection": None,
            "exactMcNemarP": None,
        },
        "generalization": {
            "status": "NOT YET COMPUTABLE",
            "reason": "No adjudicated generalization-safe independent labels exist.",
        },
        "humanEffort": {
            "status": "NOT YET COMPARABLE",
            "reason": "Annotation time alone cannot demonstrate effort reduction.",
        },
        "paperComparison": {
            "status": "NOT DIRECTLY COMPARABLE",
            "reason": (
                "The historical thesis outputs do not provide an independent "
                "expert-labeled comparator using this metric protocol."
            ),
        },
        "topologySelection": {
            "status": "MECHANISM EVIDENCE ONLY",
            "reason": "Ground-truth labels do not by themselves choose H-layer topology.",
        },
        "routingSelection": {
            "status": "NOT YET COMPUTABLE",
            "reason": "Adjudicated review targets are required for routing precision/recall.",
        },
        "claimBoundary": (
            "The review package is ready, but accuracy, macro-F1, unseen-pattern "
            "generalization, effort reduction, paper superiority, topology, and "
            "routing superiority remain unmeasured at safe N=0."
        ),
        "nextAction": (
            "Complete supervisor approval, two independent reviews, agreement "
            "analysis, and adjudication; then rerun development evaluation."
        ),
    }


def validate_gold(
    path: Path,
    mapping: list[dict[str, str]],
) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    rows = read_csv(path)
    expected_ids = {
        row["anonymous_item_id"]
        for row in mapping
        if row["generalization_safe"].lower() == "true"
    }
    if len(rows) != 24:
        raise ValueError(f"gold-label file must contain 24 rows, found {len(rows)}")
    identifiers = [row.get("anonymous_item_id", "") for row in rows]
    if len(set(identifiers)) != len(identifiers) or set(identifiers) != expected_ids:
        raise ValueError("gold-label IDs must match all 24 blind evaluation items exactly")
    return_hashes: dict[str, str] = {}
    for row in rows:
        required = [
            "gold_label",
            "gold_rationale",
            "adjudicator_id",
            "adjudication_date",
            "reviewer_1_return_sha256",
            "reviewer_2_return_sha256",
            "gold_review_requirement",
            "gold_routing_rationale",
            "gold_review_priority",
        ]
        missing = [field for field in required if not row.get(field, "").strip()]
        if missing:
            raise ValueError(
                f"{row['anonymous_item_id']}: missing adjudication fields {missing}"
            )
        if row["gold_label"] not in LABELS:
            raise ValueError(f"{row['anonymous_item_id']}: invalid gold label")
        if automated_identity(row["adjudicator_id"]):
            raise ValueError(f"{row['anonymous_item_id']}: automated adjudicator forbidden")
        for field in ("reviewer_1_return_sha256", "reviewer_2_return_sha256"):
            value = row[field]
            if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
                raise ValueError(f"{row['anonymous_item_id']}: invalid {field}")
            previous = return_hashes.setdefault(field, value)
            if previous != value:
                raise ValueError(f"{field} must be identical on every gold-label row")
    return {row["anonymous_item_id"]: row for row in rows}, return_hashes


def boolean(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def routing_metrics(
    targets: list[bool],
    predictions: list[bool],
    priorities: list[str],
) -> dict[str, Any]:
    if len(targets) != len(predictions) or len(targets) != len(priorities):
        raise ValueError("routing targets, predictions, and priorities must align")
    true_positive = false_positive = false_negative = true_negative = 0
    high_required = high_captured = 0
    for target, prediction, priority in zip(
        targets,
        predictions,
        priorities,
        strict=True,
    ):
        if target and prediction:
            true_positive += 1
        elif prediction:
            false_positive += 1
        elif target:
            false_negative += 1
        else:
            true_negative += 1
        if target and priority == "High":
            high_required += 1
            if prediction:
                high_captured += 1
    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive
        else 0.0
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative
        else 0.0
    )
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "n": len(targets),
        "truePositive": true_positive,
        "falsePositive": false_positive,
        "falseNegative": false_negative,
        "trueNegative": true_negative,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
        "workloadRate": round(sum(predictions) / len(predictions), 6),
        "highPriorityRecall": (
            round(high_captured / high_required, 6) if high_required else None
        ),
        "highPriorityTargetCount": high_required,
    }


def confusion(y_true: list[str], y_pred: list[str]) -> dict[str, dict[str, int]]:
    result = {actual: {predicted: 0 for predicted in LABELS} for actual in LABELS}
    for actual, predicted in zip(y_true, y_pred, strict=True):
        if predicted not in LABELS:
            raise ValueError(f"comparator emitted an invalid label: {predicted}")
        result[actual][predicted] += 1
    return result


def classification_metrics(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    matrix = confusion(y_true, y_pred)
    per_class: dict[str, dict[str, float | int]] = {}
    recalls: list[float] = []
    f1_values: list[float] = []
    for label in LABELS:
        true_positive = matrix[label][label]
        false_positive = sum(matrix[actual][label] for actual in LABELS if actual != label)
        support = sum(matrix[label].values())
        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
        recall = true_positive / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = {
            "support": support,
            "precision": round(precision, 6),
            "recall": round(recall, 6),
            "f1": round(f1, 6),
        }
        recalls.append(recall)
        f1_values.append(f1)
    correct = sum(
        actual == predicted
        for actual, predicted in zip(y_true, y_pred, strict=True)
    )
    return {
        "n": len(y_true),
        "accuracy": round(correct / len(y_true), 6),
        "macroF1": round(sum(f1_values) / len(LABELS), 6),
        "balancedAccuracy": round(sum(recalls) / len(LABELS), 6),
        "perClass": per_class,
        "confusionMatrix": matrix,
        "accuracyWilson95": wilson_interval(correct, len(y_true)),
    }


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> list[float]:
    if total == 0:
        return [0.0, 0.0]
    probability = successes / total
    denominator = 1 + z * z / total
    centre = probability + z * z / (2 * total)
    margin = z * math.sqrt(probability * (1 - probability) / total + z * z / (4 * total * total))
    return [
        round((centre - margin) / denominator, 6),
        round((centre + margin) / denominator, 6),
    ]


def exact_mcnemar(baseline_only: int, candidate_only: int) -> float:
    discordant = baseline_only + candidate_only
    if discordant == 0:
        return 1.0
    smaller = min(baseline_only, candidate_only)
    lower_tail = sum(math.comb(discordant, index) for index in range(smaller + 1))
    return round(min(1.0, 2 * lower_tail / (2**discordant)), 8)


def evaluate(
    package: Path,
    gold_path: Path,
    *,
    stage: str,
    policy_manifest_path: Path | None,
) -> dict[str, Any]:
    mapping_path = package / "private/item_mapping_PRIVATE.csv"
    mapping = read_csv(mapping_path)
    gold, return_hashes = validate_gold(gold_path, mapping)
    if stage == "sealed_holdout":
        if policy_manifest_path is None:
            raise ValueError("sealed holdout requires --policy-manifest")
        policy = json.loads(policy_manifest_path.read_text(encoding="utf-8"))
        if (
            policy.get("status") != "Frozen for one-time holdout evaluation"
            or policy.get("supervisorOutcome") not in {"Accepted", "Accepted with changes"}
            or policy.get("baselineMutationAllowed") is not False
        ):
            raise ValueError("policy manifest is not approved, frozen, and baseline-safe")
    partition = "development" if stage == "development" else "sealed_holdout"
    selected = sorted(
        (row for row in mapping if row["partition"] == partition),
        key=lambda row: row["anonymous_item_id"],
    )
    expected_n = 16 if partition == "development" else 8
    if len(selected) != expected_n:
        raise ValueError(f"{partition} must contain {expected_n} rows")
    true_labels = [gold[row["anonymous_item_id"]]["gold_label"] for row in selected]
    review_targets = [
        gold[row["anonymous_item_id"]]["gold_review_requirement"]
        in {"Human review required", "Insufficient context"}
        for row in selected
    ]
    review_priorities = [
        gold[row["anonymous_item_id"]]["gold_review_priority"] for row in selected
    ]
    baseline_labels = [row["original_agent4_classification"] for row in selected]
    candidate_labels = [row["memory_informed_classification"] for row in selected]
    baseline_routing = [
        boolean(row["baseline_requires_human_review"]) for row in selected
    ]
    candidate_routing = [
        boolean(row["memory_requires_human_review"]) for row in selected
    ]
    baseline = classification_metrics(true_labels, baseline_labels)
    candidate = classification_metrics(true_labels, candidate_labels)
    both_correct = baseline_only = candidate_only = both_wrong = 0
    for actual, original, proposed in zip(
        true_labels,
        baseline_labels,
        candidate_labels,
        strict=True,
    ):
        original_correct = original == actual
        proposed_correct = proposed == actual
        if original_correct and proposed_correct:
            both_correct += 1
        elif original_correct:
            baseline_only += 1
        elif proposed_correct:
            candidate_only += 1
        else:
            both_wrong += 1
    result = {
        "schemaVersion": "IndependentGroundTruthEvaluation-v1",
        "status": "PILOT ONLY" if stage == "sealed_holdout" else "DEVELOPMENT ONLY",
        "stage": stage,
        "packageManifestSha256": sha256_file(package / "package_manifest.json"),
        "goldLabelFileSha256": sha256_file(gold_path),
        "reviewerReturnHashes": return_hashes,
        "evaluatedRows": len(selected),
        "baseline": {"id": "B0-original-agent4", **baseline},
        "currentComparator": {
            "id": "B1-current-m4b1",
            "classificationChanges": sum(
                original != proposed
                for original, proposed in zip(
                    baseline_labels,
                    candidate_labels,
                    strict=True,
                )
            ),
            **candidate,
        },
        "paired": {
            "bothCorrect": both_correct,
            "baselineOnlyCorrect": baseline_only,
            "candidateOnlyCorrect": candidate_only,
            "bothWrong": both_wrong,
            "netCorrection": candidate_only - baseline_only,
            "exactMcNemarP": exact_mcnemar(baseline_only, candidate_only),
        },
        "routing": {
            "targetDefinition": (
                "Human review required OR insufficient neutral context, adjudicated "
                "independently of VEGO-AI routing."
            ),
            "baseline": routing_metrics(
                review_targets,
                baseline_routing,
                review_priorities,
            ),
            "currentComparator": routing_metrics(
                review_targets,
                candidate_routing,
                review_priorities,
            ),
        },
        "generalization": {
            "status": (
                "SEALED PILOT ONLY" if stage == "sealed_holdout" else "NOT TESTED ON HOLDOUT"
            ),
            "reason": (
                "The rows are leakage-safe, but formal unseen-pattern evidence "
                "requires a frozen candidate and external replication."
            ),
        },
        "humanEffort": {
            "status": "NOT YET COMPARABLE",
            "reason": "EXP-026 must compare the same review tasks with and without memory.",
        },
        "paperComparison": {
            "status": "NOT DIRECTLY COMPARABLE",
            "reason": (
                "The historical thesis does not expose independent gold labels "
                "under this protocol. Mechanism counts may be contextualized, "
                "but performance deltas cannot be claimed."
            ),
        },
        "claimBoundary": (
            "Development results may guide one preregistered deterministic proposal "
            "but cannot support a confirmatory improvement claim. The eight-row "
            "holdout is a one-time pilot and never formal proof."
        ),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--gold", type=Path)
    parser.add_argument(
        "--stage",
        choices=["development", "sealed_holdout"],
        default="development",
    )
    parser.add_argument("--policy-manifest", type=Path)
    parser.add_argument("--check-gate", action="store_true")
    args = parser.parse_args()
    try:
        manifest = json.loads(
            (args.package / "package_manifest.json").read_text(encoding="utf-8")
        )
        if args.check_gate or args.gold is None:
            result = null_result(manifest)
        else:
            result = evaluate(
                args.package,
                args.gold,
                stage=args.stage,
                policy_manifest_path=args.policy_manifest,
            )
        write_json(args.output / "independent_ground_truth_evaluation.json", result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Independent ground-truth evaluation: FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
