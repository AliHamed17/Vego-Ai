"""EXP-017: deterministic-first verification provenance over synthetic sources."""

from __future__ import annotations

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
from .contracts import MemoryRecord, ValidationError, VerificationRecord
from .state_machine import TrustedMemoryStore

EXPERIMENT_ID = "EXP-017"
EXPERIMENT_FOLDER = "EXP-017-verification-provenance"
SOURCE_ORDER = ("baseline", "guideline", "review", "memory")


def _verify_case(fixtures: Path, case: dict[str, Any]) -> tuple[dict[str, Any], tuple[Path, ...]]:
    trace: list[dict[str, Any]] = []
    source_versions: dict[str, str] = {}
    conflicts: list[str] = list(case.get("declared_conflicts", []))
    input_files: list[Path] = []
    for family in SOURCE_ORDER:
        reference = case["sources"][family]
        path = fixtures / reference["path"]
        if not path.is_file():
            status = "missing"
            actual = "MISSING"
            conflicts.append(f"{family}:missing_source")
        else:
            input_files.append(path)
            actual = sha256_file(path)
            expected = (
                actual if reference["expected_sha256"] == "ACTUAL" else reference["expected_sha256"]
            )
            status = "passed" if actual == expected else "hash_mismatch"
            if status != "passed":
                conflicts.append(f"{family}:hash_mismatch")
        source_versions[family] = actual
        trace.append(
            {
                "family": family,
                "source_artifact": relative_path(path),
                "actual_sha256": actual,
                "status": status,
                "synthetic_tag": "SYNTHETIC_NOT_HUMAN",
            }
        )
    outcome = "verified" if not conflicts else "needs_adjudication"
    verification = VerificationRecord(
        verification_id=f"VERIFY-{case['id']}",
        feedback_id=f"FEEDBACK-{case['id']}",
        deterministic_checks=tuple(f"{entry['family']}:{entry['status']}" for entry in trace),
        source_versions=source_versions,
        conflicts=tuple(conflicts),
        rounds=1,
        outcome=outcome,
    )
    return (
        {
            "case_id": case["id"],
            "synthetic_tag": "SYNTHETIC_NOT_HUMAN",
            "trace": trace,
            "verification": verification.to_dict(),
            "semantic_checks_performed": False,
        },
        tuple(input_files),
    )


def evaluate(fixtures: Path | None = None) -> dict[str, Any]:
    fixtures = fixtures or fixture_dir(EXPERIMENT_FOLDER)
    descriptor_path = fixtures / "cases.json"
    fixture = load_json(descriptor_path)
    results: list[dict[str, Any]] = []
    input_files: set[Path] = {descriptor_path}
    for case in fixture["cases"]:
        result, used = _verify_case(fixtures, case)
        results.append(result)
        input_files.update(used)

    memory = TrustedMemoryStore()
    verified_synthetic = next(
        result for result in results if result["verification"]["outcome"] == "verified"
    )
    try:
        synthetic_memory = MemoryRecord(
            memory_id="MEMORY-SYNTHETIC-VALID",
            verification_id=verified_synthetic["verification"]["verification_id"],
            source_outcome="verified",
            validity_scope={"fixture": verified_synthetic["case_id"]},
            conflicts=(),
            provenance={"synthetic_tag": "SYNTHETIC_NOT_HUMAN"},
            leakage_classification="not_applicable",
        )
        memory.append(synthetic_memory)
    except ValidationError as exc:
        synthetic_memory_block = str(exc)
    else:
        synthetic_memory_block = "NOT_BLOCKED"

    expected_outcomes = {case["id"]: case["expected_outcome"] for case in fixture["cases"]}
    actual_outcomes = {result["case_id"]: result["verification"]["outcome"] for result in results}
    missing_case = next(result for result in results if result["case_id"] == "VERIFY-02-MISSING")
    acceptance = {
        "all_source_families_traced_in_order": all(
            [entry["family"] for entry in result["trace"]] == list(SOURCE_ORDER)
            for result in results
        ),
        "deterministic_before_semantic": all(
            not result["semantic_checks_performed"] for result in results
        ),
        "expected_outcomes_match": actual_outcomes == expected_outcomes,
        "missing_source_needs_adjudication": missing_case["verification"]["outcome"]
        == "needs_adjudication",
        "zero_synthetic_memory_contamination": len(memory.records) == 0
        and synthetic_memory_block != "NOT_BLOCKED",
    }
    summary = {
        "experiment": EXPERIMENT_ID,
        "fixture_version": fixture["fixture_version"],
        "synthetic_tag": "SYNTHETIC_NOT_HUMAN",
        "source_order": list(SOURCE_ORDER),
        "cases": results,
        "trusted_memory_writes": len(memory.records),
        "synthetic_memory_block_reason": synthetic_memory_block,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }
    return {"summary": summary, "input_files": tuple(sorted(input_files))}


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
            "source_trace": "ordered baseline/guideline/review/memory status[]",
            "verification_outcome": "verified|needs_adjudication",
            "trusted_memory_writes": "count",
        },
        parameters={"source_order": list(SOURCE_ORDER), "semantic_checks": "not_performed"},
    )
    print_completion(EXPERIMENT_ID, output, result["summary"])
    return result
