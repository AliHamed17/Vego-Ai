#!/usr/bin/env python3
"""Verify legacy/unified parity against the local 27-row controlled artifact set."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vego_hlayer.runtime import apply_architecture_mode  # noqa: E402

SETTINGS = frozenset({"cd_ch", "cd_pw", "ucd_ch", "ucd_pw"})
FILE_STAGES = {
    "human_review_queue.jsonl": "review",
    "human_review_queue_resolved.jsonl": "resolved",
    "human_judgment_memory.jsonl": "memory",
    "memory_advice.json": "advice",
    "memory_informed_comparison.json": "comparison",
}


def load(path: Path, stage: str) -> Any:
    if stage in {"review", "resolved", "memory"}:
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    return json.loads(path.read_text(encoding="utf-8"))


def find_complete_run() -> Path:
    groups: dict[Path, set[str]] = defaultdict(set)
    for path in (ROOT / "VEGO-AI" / "runs").glob(
        "*/human/*/memory_informed_comparison.json"
    ):
        groups[path.parents[1]].add(path.parent.name)
    complete = sorted(root for root, settings in groups.items() if settings == SETTINGS)
    if not complete:
        raise ValueError("no controlled H-layer run contains all four settings")
    return complete[-1]


def verify() -> dict[str, Any]:
    run_root = find_complete_run()
    artifacts: list[dict[str, Any]] = []
    comparison_rows = 0
    review_items = 0
    memory_records = 0
    classification_changes = 0
    for setting in sorted(SETTINGS):
        setting_root = run_root / setting
        for file_name, stage in FILE_STAGES.items():
            path = setting_root / file_name
            if not path.is_file():
                if stage in {"resolved", "memory"} and setting != "ucd_ch":
                    continue
                raise ValueError(f"controlled artifact is missing: {setting}/{file_name}")
            payload = load(path, stage)
            execution = apply_architecture_mode(
                stage,
                payload,
                architecture_mode="parity",
            )
            if execution.manifest.parity_status != "match":
                raise ValueError(f"parity mismatch: {setting}/{file_name}")
            count = len(execution.canonical_records)
            if stage == "comparison":
                comparison_rows += count
                for row in payload["comparisons"]:
                    classification_changes += int(
                        bool(row.get("memory_informed_differs_from_original"))
                    )
                    if row.get("ai_behavior_changed_in_baseline") is not False:
                        raise ValueError(
                            f"baseline behavior flag violated: {setting}/{file_name}"
                        )
            elif stage == "review":
                review_items += count
            elif stage == "memory":
                memory_records += count
            artifacts.append(
                {
                    "setting": setting,
                    "stage": stage,
                    "records": count,
                    "legacySha256": execution.manifest.legacy_output_sha256,
                    "unifiedSha256": execution.manifest.unified_output_sha256,
                    "parity": execution.manifest.parity_status,
                }
            )
    if comparison_rows != 27:
        raise ValueError(f"expected 27 comparison rows, got {comparison_rows}")
    if review_items != 11:
        raise ValueError(f"expected 11 review items, got {review_items}")
    if memory_records != 3:
        raise ValueError(f"expected 3 legacy memory records, got {memory_records}")
    if classification_changes != 0:
        raise ValueError(
            f"expected zero classification changes, got {classification_changes}"
        )
    return {
        "schemaVersion": "ControlledParityReport-v1",
        "controlledRunId": run_root.parent.name,
        "settings": sorted(SETTINGS),
        "artifactCount": len(artifacts),
        "reviewItems": review_items,
        "memoryRecords": memory_records,
        "comparisonRows": comparison_rows,
        "classificationChanges": classification_changes,
        "baselinePreserved": True,
        "parityStatus": "PASS",
        "claimBoundary": (
            "Mechanism parity and baseline preservation only; no accuracy or "
            "generalization result."
        ),
        "artifacts": artifacts,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = verify()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"controlled parity: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(
            "controlled parity: PASS "
            f"({result['comparisonRows']} rows, "
            f"{result['classificationChanges']} classification changes)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
