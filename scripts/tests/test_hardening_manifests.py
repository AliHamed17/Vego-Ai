from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "scripts" / "build_hardening_manifests.py"
OUTPUT = ROOT / "docs" / "research" / "hardening"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_hardening_manifests", BUILDER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(schema_name: str, value: dict) -> None:
    schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(value)


def test_hardening_manifests_validate_and_are_portable() -> None:
    mapping = {
        "baseline-lock-manifest-v2.json": "baseline-lock-manifest-v2.schema.json",
        "security-posture-snapshot-v1.json": ("security-posture-snapshot-v1.schema.json"),
        "release-manifest-v3.json": "release-manifest-v3.schema.json",
        "iteration-015-manifest.json": "hlayer-iteration-manifest-v1.schema.json",
    }
    for file_name, schema_name in mapping.items():
        payload = json.loads((OUTPUT / file_name).read_text(encoding="utf-8"))
        validate(schema_name, payload)
        serialized = json.dumps(payload)
        assert "C:\\\\" not in serialized
        assert "file:///" not in serialized


def test_builder_is_deterministic_with_or_without_controlled_check() -> None:
    builder = load_builder()
    clone_safe = builder.build_all(False)
    assert clone_safe == builder.build_all(False)

    controlled_paths = [
        ROOT / "VEGO-AI" / "eval_output" / setting
        for setting in ("cd_ch", "cd_pw", "ucd_ch", "ucd_pw")
    ]
    if all(path.is_dir() for path in controlled_paths):
        assert clone_safe == builder.build_all(True)
    else:
        with pytest.raises(ValueError, match="controlled Agent 4 output missing"):
            builder.build_all(True)


def test_portable_text_hash_normalizes_checkout_line_endings(tmp_path: Path) -> None:
    builder = load_builder()
    lf = tmp_path / "lf.txt"
    crlf = tmp_path / "crlf.txt"
    lf.write_bytes(b"alpha\nbeta\n")
    crlf.write_bytes(b"alpha\r\nbeta\r\n")
    assert builder.sha256_portable_text_file(lf) == builder.sha256_portable_text_file(
        crlf
    )


def test_baseline_lock_preserves_agent4_and_model_boundary() -> None:
    payload = json.loads((OUTPUT / "baseline-lock-manifest-v2.json").read_text(encoding="utf-8"))
    assert payload["requestedModel"] == "gpt-4o"
    assert payload["servedSnapshotKnown"] is False
    assert len(payload["agent4Outputs"]["files"]) == 4
    assert all(item["matchesOfficialSemantics"] for item in payload["agent4Outputs"]["files"])


def test_sbom_components_are_unique_and_pinned() -> None:
    payload = json.loads((OUTPUT / "sbom.cdx.json").read_text(encoding="utf-8"))
    components = payload["components"]
    identities = [(item["purl"], item["version"]) for item in components]
    assert len(identities) == len(set(identities))
    assert all(item["version"] for item in components)


def test_iteration_15_is_reliability_only() -> None:
    payload = json.loads((OUTPUT / "iteration-015-manifest.json").read_text(encoding="utf-8"))
    assert payload["iteration"] == 15
    assert payload["verdict"] == "NEUTRAL"
    assert payload["guardrails"]["classificationChanges"] == 0
    assert payload["guardrails"]["exp005SafeLabels"] == 0
    assert payload["guardrails"]["accuracyClaimAllowed"] is False
