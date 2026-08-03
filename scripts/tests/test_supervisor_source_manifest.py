from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/build_supervisor_source_manifest.py"
SPEC = importlib.util.spec_from_file_location("build_supervisor_source_manifest", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_reference_normalization_separates_annotation_and_fragment() -> None:
    assert MODULE.normalize_reference(
        "docs/research/phd-proposal/master-traceability-register.md "
        "(R-15, R-16)#section"
    ) == (
        "docs/research/phd-proposal/master-traceability-register.md",
        "section",
    )


def _build_payload_or_skip() -> dict[str, object]:
    try:
        return MODULE.build_payload()
    except ValueError as error:
        pytest.skip(
            "a [Sources]-referenced artifact is gitignored and only present on "
            f"the machine that generated it: {error}"
        )


def test_current_deck_sources_resolve_and_are_hash_bound() -> None:
    payload = _build_payload_or_skip()
    sources = payload["sources"]

    assert payload["schema_version"] == "IrisSupervisorSourceManifest-v1"
    assert payload["presentation"]["slide_count"] == 21
    assert payload["presentation"]["source_note_sections"] == 21
    assert payload["unique_source_path_count"] == len(sources)
    assert len(sources) >= 20
    assert all(source["slides"] for source in sources)
    assert all(
        (source["kind"] == "file" and MODULE.valid_sha256(source["sha256"]))
        or (
            source["kind"] == "directory"
            and MODULE.valid_sha256(source["aggregate_sha256"])
            and source["member_count"] == len(source["members"])
        )
        for source in sources
    )


def test_tracked_manifest_is_byte_reproducible() -> None:
    payload = _build_payload_or_skip()
    assert MODULE.DEFAULT_OUTPUT.read_text(encoding="utf-8") == MODULE.render(payload)
