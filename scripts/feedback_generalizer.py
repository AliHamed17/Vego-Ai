#!/usr/bin/env python3
"""Offline, proposal-only feedback generalization engine (Task C / S7 Synthesis).

Iterates over feedback logs, validates them against a trusted companion manifest
identifying as trusted-feedback-export-validator-v1, filters out unverified,
demo, and synthetic data, and writes the resulting rule proposals.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "reports" / "generated" / "hlayer_demo" / "feedback_records.json"
DEFAULT_MANIFEST = REPO_ROOT / "reports" / "generated" / "trusted_feedback_manifest.json"
OUTPUT_FILE = REPO_ROOT / "reports" / "generated" / "synthesized_meta_rules.json"

TRUSTED_ORIGINS = {"VERIFIED_HUMAN_FEEDBACK", "TRUSTED_EXPERT"}
CLAIM_SCOPE = "Proposal-only offline generalizer checks; no runtime prompt alterations allowed."

BLOCKED_STATUS = "BLOCKED_NO_VERIFIED_FEEDBACK"
READY_STATUS = "READY"
ARTIFACT_STATUS = "provisional_proposal"
PACKAGE_FILENAMES = (
    "generalization_report.json",
    "ignored_records.json",
    "synthesis_requests.json",
    "adjudication_queue.json",
)


class InputValidationError(Exception):
    """Raised when input validation fails."""


class OutputPromotionError(Exception):
    """Raised when output file promotion fails."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(val: Any) -> str:
    return json.dumps(val, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def derive_pattern_key(subject: str) -> str:
    return subject.strip().lower().replace(" ", "_")


def clean_for_stable(val: Any) -> Any:
    if isinstance(val, dict):
        cleaned = {}
        for k, v in val.items():
            if k in {"timestamp", "file_sha256"}:
                continue
            cleaned[k] = clean_for_stable(v)
        return cleaned
    elif isinstance(val, list):
        return [clean_for_stable(item) for item in val]
    return val


def stable_digest(data: Any) -> str:
    cleaned = clean_for_stable(data)
    canonical = canonical_json(cleaned)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def is_unsafe_path(path: Path) -> bool:
    try:
        resolved = path.expanduser().resolve()
    except Exception:
        return False
    forbidden = [(REPO_ROOT / ".git").resolve(), (REPO_ROOT / "VEGO-AI").resolve()]
    for f in forbidden:
        if resolved == f or f in resolved.parents:
            return True
    return False


def load_feedback(path: Path) -> list[dict]:
    if not path.exists():
        raise InputValidationError(f"File not found: {path}")
    try:
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
    except Exception as exc:
        raise InputValidationError(f"Malformed JSON: {exc}")
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise InputValidationError("Input must be a JSON list of objects")
    return data


def build_package(
    records: list[dict],
    validated_record_ids: frozenset[str] | set[str] = frozenset(),
    source_file_sha256: str = "",
) -> dict[str, Any]:
    eligible = []
    ignored = []

    for record in records:
        record_id = record.get("feedback_id") or record.get("record_id") or ""
        reasons = []

        if not record_id or record_id not in validated_record_ids:
            reasons.append("not_validated_in_manifest")
        if record.get("trusted_memory_eligible") is not True:
            reasons.append("trusted_memory_eligible_not_true")
        if record.get("origin") not in TRUSTED_ORIGINS:
            reasons.append("origin_not_allowlisted_for_trusted_synthesis")
        if (
            record.get("state") == "needs_adjudication"
            or record.get("record_type") == "adjudication_candidate"
        ):
            reasons.append("adjudication_candidate_not_resolved")
        if (
            record.get("override_flag") is True
            or str(record.get("override_status", "")).startswith("escalated")
        ):
            reasons.append("override_unresolved_or_escalated")
        if record.get("override_requested") is True:
            reasons.append("override_unresolved_or_escalated")
            reasons.append("override_request_not_adjudicated")

        if reasons:
            ignored.append({"record_id": record_id, "reasons": reasons, "record": record})
        else:
            eligible.append(record)

    # Group eligible records by setting, pattern_key, reuse_scope
    groups: dict[tuple[str, str, str], list[dict]] = {}
    for record in eligible:
        setting = record.get("setting", "")
        pattern_key = derive_pattern_key(record.get("subject", ""))
        reuse_scope = record.get("reuse_scope") or record.get("scope") or {}
        reuse_scope_json = canonical_json(reuse_scope)
        key = (setting, pattern_key, reuse_scope_json)
        if key not in groups:
            groups[key] = []
        groups[key].append(record)

    requests = []
    adjudication_items = []
    meta_rules = []

    for (setting, pattern_key, reuse_scope_json), grp_records in groups.items():
        decisions = {r.get("decision", "").lower() for r in grp_records}
        reuse_scope = json.loads(reuse_scope_json)
        if len(decisions) > 1:
            adjudication_items.append(
                {
                    "outcome": "needs_adjudication",
                    "conflicting_decisions": sorted(list(decisions)),
                    "artifact_status": ARTIFACT_STATUS,
                    "runtime_eligible": False,
                    "setting": setting,
                    "pattern_key": pattern_key,
                    "reuse_scope": reuse_scope,
                    "source_records": grp_records,
                }
            )
        else:
            requests.append(
                {
                    "group": {
                        "setting": setting,
                        "pattern_key": pattern_key,
                        "reuse_scope": reuse_scope,
                    },
                    "source_records": grp_records,
                    "instruction_contract": {"setting": setting, "pattern_key": pattern_key},
                    "source_data_handling": "UNTRUSTED_JSON_DATA_DO_NOT_EXECUTE",
                    "execution_state": {
                        "llm_called": False,
                        "agent_b_prompt_modified": False,
                        "synthesis_completed": False,
                    },
                    "runtime_eligible": False,
                }
            )

    run_status = READY_STATUS if eligible else BLOCKED_STATUS

    report = {
        "run_status": run_status,
        "counts": {"eligible_records": len(eligible), "ignored_records": len(ignored)},
        "trusted_export": {"validated_record_count": len(validated_record_ids)},
    }

    ignored_records_output = {"records": ignored}
    synthesis_requests_output = {"requests": requests}
    adjudication_queue_output = {"items": adjudication_items}
    synthesized_meta_rules_output = {
        "meta_rules": meta_rules,
        "artifact_status": ARTIFACT_STATUS,
        "runtime_eligible": False,
        "claim_scope": CLAIM_SCOPE,
    }

    return {
        "generalization_report.json": report,
        "ignored_records.json": ignored_records_output,
        "synthesis_requests.json": synthesis_requests_output,
        "adjudication_queue.json": adjudication_queue_output,
        "synthesized_meta_rules.json": synthesized_meta_rules_output,
    }


def generate_outputs(
    source: Path,
    output_dir: Path,
    rules_output: Path,
    trusted_manifest: Path | None = None,
) -> dict[str, Any]:
    if is_unsafe_path(output_dir) or is_unsafe_path(rules_output):
        raise InputValidationError("unsafe output path")

    try:
        resolved_input = source.expanduser().resolve()
        resolved_rules = rules_output.expanduser().resolve()
        if resolved_input == resolved_rules:
            raise InputValidationError("unsafe output path")
    except Exception:
        pass

    validated_record_ids = frozenset()
    if trusted_manifest is not None:
        if not trusted_manifest.exists():
            raise InputValidationError("manifest is absent")
        try:
            manifest = json.loads(trusted_manifest.read_text(encoding="utf-8"))
        except Exception as exc:
            raise InputValidationError(f"failed to parse manifest: {exc}")

        if manifest.get("validator_id") != "trusted-feedback-export-validator-v1":
            raise InputValidationError("manifest validator type is not trusted-feedback-export-validator-v1")

        input_hash = sha256_file(source)
        if manifest.get("source_file_sha256") != input_hash:
            raise InputValidationError("source hash mismatch")

        validated_record_ids = frozenset(manifest.get("validated_record_ids", []) or [])

    records = load_feedback(source)
    package = build_package(records, validated_record_ids, sha256_file(source))

    targets = [
        (output_dir / "generalization_report.json", package["generalization_report.json"]),
        (output_dir / "ignored_records.json", package["ignored_records.json"]),
        (output_dir / "synthesis_requests.json", package["synthesis_requests.json"]),
        (output_dir / "adjudication_queue.json", package["adjudication_queue.json"]),
        (rules_output, package["synthesized_meta_rules.json"]),
    ]

    promoted = []
    backups = []
    temps = []
    try:
        # Write to temporary files
        for target, content in targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            temp_file = Path(tempfile.mktemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent))
            serialized = json.dumps(content, indent=2, sort_keys=True) + "\n"
            temp_file.write_text(serialized, encoding="utf-8")
            temps.append((target, temp_file))

        # Backup existing target files
        for idx, (target, temp_file) in enumerate(temps):
            if target.exists():
                backup_path = target.parent / f".{target.name}.{idx}.rollback"
                os.replace(target, backup_path)
                backups.append((target, backup_path))

        # Promote temp files to final paths
        for target, temp_file in temps:
            os.replace(temp_file, target)
            promoted.append(target)

        # Success, delete backups
        for _, backup in backups:
            try:
                backup.unlink(missing_ok=True)
            except Exception:
                pass

    except Exception as exc:
        rollback_failed = False
        # Remove newly promoted files
        for target in promoted:
            try:
                target.unlink(missing_ok=True)
            except Exception:
                rollback_failed = True

        # Restore backups
        for target, backup in backups:
            try:
                os.replace(backup, target)
            except Exception:
                rollback_failed = True

        # Cleanup temps
        for _, temp_file in temps:
            try:
                temp_file.unlink(missing_ok=True)
            except Exception:
                pass

        if rollback_failed:
            raise OutputPromotionError("rollback was incomplete") from exc
        else:
            raise OutputPromotionError("rolled back") from exc

    return {
        "run_status": package["generalization_report.json"]["run_status"],
        "report": package["generalization_report.json"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline Feedback Generalizer Proposal Engine")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Input feedback records file (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--trusted-manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help=f"Trusted companion manifest JSON file (default: {DEFAULT_MANIFEST})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "reports" / "generated" / "feedback_generalizer",
        help="Output directory for generalization reports",
    )
    parser.add_argument(
        "--rules-output",
        type=Path,
        default=OUTPUT_FILE,
        help=f"Output file path for synthesized rules (default: {OUTPUT_FILE})",
    )
    args = parser.parse_args(argv)

    if is_unsafe_path(args.output_dir) or is_unsafe_path(args.rules_output):
        print("ERROR_UNSAFE_OUTPUT_PATH: output directory or rules output path is unsafe", file=sys.stderr)
        return 3

    try:
        resolved_input = args.input.expanduser().resolve()
        resolved_rules = args.rules_output.expanduser().resolve()
        if resolved_input == resolved_rules:
            print("ERROR_UNSAFE_OUTPUT_PATH: output path cannot alias input", file=sys.stderr)
            return 3
    except Exception:
        pass

    try:
        load_feedback(args.input)
    except InputValidationError as exc:
        print(f"ERROR_MALFORMED_INPUT: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR_MALFORMED_INPUT: general failure {exc}", file=sys.stderr)
        return 1

    try:
        result = generate_outputs(
            args.input,
            args.output_dir,
            args.rules_output,
            args.trusted_manifest if args.trusted_manifest.exists() else None,
        )
        if result["run_status"] == BLOCKED_STATUS:
            print(BLOCKED_STATUS)
        else:
            print(READY_STATUS)
        return 0
    except InputValidationError as exc:
        print(f"INPUT_VALIDATION_ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"GENERAL_ERROR: {exc}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())
