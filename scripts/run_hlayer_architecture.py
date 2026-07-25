"""Validate or parity-check M1-M4B-1 artifacts through canonical contracts."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vego_hlayer.adapters import STAGES  # noqa: E402
from vego_hlayer.contracts import ValidationError  # noqa: E402
from vego_hlayer.io_safety import (  # noqa: E402
    DEFAULT_MAX_RECORDS,
    atomic_write_text,
    validate_input_file,
    validate_output_file,
)
from vego_hlayer.runtime import (  # noqa: E402
    ARCHITECTURE_MODES,
    apply_architecture_mode,
    write_manifest,
)

JSONL_STAGES = frozenset({"review", "feedback", "resolved", "memory"})


def _load(path: Path, stage: str) -> Any:
    path = validate_input_file(path)
    if stage in JSONL_STAGES:
        records: list[dict] = []
        with path.open(encoding="utf-8") as handle:
            for number, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"{path}:{number}: JSONL record must be an object")
                records.append(value)
                if len(records) > DEFAULT_MAX_RECORDS:
                    raise ValueError(
                        f"{path}: record count exceeds {DEFAULT_MAX_RECORDS}"
                    )
        return records
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSON artifact must be an object")
    return value


def _safe_output(path: Path) -> Path:
    return validate_output_file(path, repo_root=ROOT)


def _write(path: Path, stage: str, value: Any) -> None:
    target = _safe_output(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if stage in JSONL_STAGES:
        content = "".join(
            json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
            for record in value
        )
        atomic_write_text(target, content)
        return
    atomic_write_text(
        target,
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )


def _transaction_path(target: Path, role: str, token: str) -> Path:
    return target.with_name(f".{target.name}.{os.getpid()}.{token}.{role}")


def _reserve_publication_path(path: Path) -> None:
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise ValidationError(
            f"publication target appeared during transaction: {path}"
        ) from exc
    else:
        os.close(descriptor)


def _publish_artifact_and_manifest(
    *,
    output: Path,
    stage: str,
    value: Any,
    manifest: Path,
    execution,
) -> None:
    """Stage and publish a new artifact/manifest pair or leave neither."""

    token = uuid4().hex
    staged_output = _transaction_path(output, "output-stage", token)
    staged_manifest = _transaction_path(manifest, "manifest-stage", token)
    output_reserved = False
    manifest_reserved = False
    output_published = False
    manifest_published = False
    try:
        _write(staged_output, stage, value)
        write_manifest(execution.manifest, staged_manifest)
        _reserve_publication_path(output)
        output_reserved = True
        _reserve_publication_path(manifest)
        manifest_reserved = True
        os.replace(staged_output, output)
        output_published = True
        output_reserved = False
        os.replace(staged_manifest, manifest)
        manifest_published = True
        manifest_reserved = False
    except BaseException:
        if manifest_published and manifest.is_file():
            manifest.unlink()
        elif manifest_reserved and manifest.is_file():
            manifest.unlink()
        if output_published and output.is_file():
            output.unlink()
        elif output_reserved and output.is_file():
            output.unlink()
        raise
    finally:
        for staged in (staged_output, staged_manifest):
            if staged.exists() or staged.is_symlink():
                staged.unlink()


def _config_mode(path: Path) -> str:
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("H-layer runtime config must be an object")
    h_layer = config.get("h_layer")
    if h_layer is None:
        h_layer = {}
    if not isinstance(h_layer, dict):
        raise ValueError("h_layer config must be an object")
    mode = h_layer.get("architecture_mode", "legacy")
    if mode not in ARCHITECTURE_MODES:
        raise ValueError(f"invalid architecture_mode {mode!r}")
    if h_layer.get("contract_version") != "1.0":
        raise ValueError("only H-layer contract_version 1.0 is supported")
    if h_layer.get("interaction_log_mode") not in {
        "off",
        "metadata_only",
        "full_content",
    }:
        raise ValueError("invalid interaction_log_mode")
    return mode


def _execute_isolated(
    stage: str,
    payload: Any,
    mode: str,
):
    if mode != "parity":
        return apply_architecture_mode(
            stage,
            payload,
            architecture_mode=mode,
        )
    # Run parity first because it is the operation that owns fail-closed
    # publication. Calling unified mode independently would raise on the
    # semantic drift that parity is specifically required to report.
    execution = apply_architecture_mode(
        stage,
        payload,
        architecture_mode="parity",
    )
    suffix = ".jsonl" if stage in JSONL_STAGES else ".json"
    with tempfile.TemporaryDirectory(prefix="vego-hlayer-parity-") as temporary:
        isolation_root = Path(temporary)
        _write(
            isolation_root / "legacy" / f"artifact{suffix}",
            stage,
            execution.legacy_output,
        )
        _write(
            isolation_root / "unified" / f"artifact{suffix}",
            stage,
            execution.unified_output,
        )
        # Temporary outputs disappear after their isolated serialization check.
        return execution


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run legacy/unified/parity H-layer artifact validation."
    )
    parser.add_argument("--stage", required=True, choices=sorted(STAGES))
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "hlayer-runtime.json",
    )
    parser.add_argument("--mode", choices=sorted(ARCHITECTURE_MODES), default=None)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        mode = args.mode or _config_mode(args.config)
        payload = _load(args.input, args.stage)
        safe_manifest = _safe_output(args.manifest)
        safe_output = _safe_output(args.output)
        if safe_manifest == safe_output:
            raise ValidationError("output and manifest must use different paths")
        execution = _execute_isolated(
            args.stage,
            payload,
            mode,
        )
        _publish_artifact_and_manifest(
            output=safe_output,
            stage=args.stage,
            value=execution.output,
            manifest=safe_manifest,
            execution=execution,
        )
    except (OSError, ValueError, ValidationError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "stage": args.stage,
                "mode": mode,
                "parity_status": execution.manifest.parity_status,
                "baseline_preserved": execution.manifest.baseline_preserved,
                "records": len(execution.canonical_records),
                "output": str(args.output),
                "manifest": str(args.manifest),
            },
            ensure_ascii=False,
        )
    )
    return 0 if execution.manifest.parity_status != "mismatch" else 1


if __name__ == "__main__":
    raise SystemExit(main())
