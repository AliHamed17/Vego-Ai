"""
Minimal tests for the Human Review Queue (Milestone 1.1).

Runs with no third-party dependency:
    python tests/test_human_review_queue.py
Also discoverable by pytest:
    pytest tests/test_human_review_queue.py

Schema-validation tests are skipped automatically if `jsonschema` is absent.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "framework"))

import hlayer_architecture as architecture_bridge  # noqa: E402
import human_review_queue as hrq  # noqa: E402
import selective_intervention_policy as sip  # noqa: E402

SCHEMA_PATH = ROOT / "schemas" / "human_review_item.schema.json"


# ---------------------------------------------------------------------------
# Test fixtures (synthetic Agent 4 outputs mirroring the real shape)
# ---------------------------------------------------------------------------

def _vc(entries):
    return {"domain_identifier": "cheers", "variability_classifications": entries}


def _dp():
    return {
        "recurring_guideline_patterns": [
            {"pattern_id": "P1", "guideline_id": "G20", "description": "g-pattern",
             "affected_cases": ["a", "b"], "pattern_strength": "20.0%"},
        ],
        "recurring_fragment_patterns": [
            {"pattern_id": "P4", "description": "f-pattern",
             "affected_cases": ["a"], "pattern_strength": "22.5%"},
        ],
    }


# ---------------------------------------------------------------------------
# Selective Intervention Policy
# ---------------------------------------------------------------------------

def test_policy_high_no_flag_skips():
    need, reasons = sip.should_request_human_review(
        {"classification": "Occasional Variability", "confidence": "High",
         "flag_for_guidelines_update": False, "requires_human_review": False})
    assert need is False and reasons == []


def test_policy_medium_triggers_and_strict_suppresses():
    entry = {"classification": "Occasional Variability", "confidence": "Medium",
             "flag_for_guidelines_update": False, "requires_human_review": False}
    need, reasons = sip.should_request_human_review(entry, include_medium=True)
    assert need is True and "medium_confidence" in reasons
    need2, reasons2 = sip.should_request_human_review(entry, include_medium=False)
    assert need2 is False and reasons2 == []


def test_policy_low_triggers():
    need, reasons = sip.should_request_human_review(
        {"classification": "Occasional Variability", "confidence": "Low",
         "flag_for_guidelines_update": False, "requires_human_review": False})
    assert need is True and "low_confidence" in reasons


def test_policy_undetermined_triggers():
    need, reasons = sip.should_request_human_review(
        {"classification": "Undetermined", "confidence": "High",
         "flag_for_guidelines_update": False, "requires_human_review": False})
    assert need is True and "undetermined_classification" in reasons


def test_policy_guideline_update_triggers():
    need, reasons = sip.should_request_human_review(
        {"classification": "Substantial Variability", "confidence": "High",
         "flag_for_guidelines_update": True, "requires_human_review": False})
    assert need is True and "guideline_update_proposed" in reasons


def test_policy_explicit_request_triggers():
    need, reasons = sip.should_request_human_review(
        {"classification": "Undetermined", "confidence": "Low",
         "flag_for_guidelines_update": True, "requires_human_review": True})
    # all four triggers fire
    assert need is True
    assert set(reasons) == {
        "agent_requested_human_review", "undetermined_classification",
        "low_confidence", "guideline_update_proposed"}


# ---------------------------------------------------------------------------
# pattern_strength normalisation
# ---------------------------------------------------------------------------

def test_strength_object_string():
    assert hrq.strength_object("22.5%") == {"value": 0.225, "display": "22.5%"}


def test_strength_object_dict():
    out = hrq.strength_object({"count": 9, "total": 40, "percentage": "22.5%"})
    assert out["display"] == "22.5%" and abs(out["value"] - 0.225) < 1e-9


def test_strength_object_none():
    assert hrq.strength_object(None) == {"value": None, "display": None}


# ---------------------------------------------------------------------------
# guideline resolution transparency
# ---------------------------------------------------------------------------

def test_resolve_guideline_from_pattern():
    out = hrq.resolve_guideline({"guideline_id": "G20"}, "irrelevant")
    assert out["related_guideline_id"] == "G20"
    assert out["related_guideline_resolution"]["method"] == "from_pattern"


def test_resolve_guideline_from_evidence():
    out = hrq.resolve_guideline({}, 'G16 -- "At the start of each month..."')
    assert out["related_guideline_id"] == "G16"
    assert out["related_guideline_resolution"]["method"] == "parsed_from_evidence"
    assert out["related_guideline_resolution"]["candidate_guidelines"] == ["G16"]


def test_resolve_guideline_none():
    out = hrq.resolve_guideline({}, "Domain Description -- no guideline here")
    assert out["related_guideline_id"] is None
    assert out["related_guideline_resolution"]["method"] == "none"
    assert out["related_guideline_resolution"]["candidate_guidelines"] == []


# ---------------------------------------------------------------------------
# review_signature stability
# ---------------------------------------------------------------------------

def test_review_signature_is_16_hex():
    sig = hrq.review_signature(
        setting_id="ucd_ch", pattern_description="x",
        related_guideline_id="G16", affected_cases=["a"],
        classification="Substantial Variability")
    assert len(sig) == 16 and all(c in "0123456789abcdef" for c in sig)


def test_review_signature_stable_under_reorder_and_dups():
    a = hrq.review_signature(
        setting_id="ucd_ch", pattern_description="x", related_guideline_id="G16",
        affected_cases=["68092", "68162", "68106"], classification="Substantial Variability")
    b = hrq.review_signature(
        setting_id="ucd_ch", pattern_description="x", related_guideline_id="G16",
        affected_cases=["68106", "68092", "68162", "68092"],  # reordered + duplicate
        classification="Substantial Variability")
    assert a == b


def test_review_signature_changes_with_classification():
    base = dict(setting_id="ucd_ch", pattern_description="x",
                related_guideline_id="G16", affected_cases=["a"])
    s1 = hrq.review_signature(classification="Substantial Variability", **base)
    s2 = hrq.review_signature(classification="Occasional Variability", **base)
    assert s1 != s2


# ---------------------------------------------------------------------------
# Build / counts / empty
# ---------------------------------------------------------------------------

def test_build_counts_and_fields():
    vc = _vc([
        {"pattern_id": "P1", "classification": "Occasional Variability",
         "confidence": "Medium", "evidence": "G20 -- x",
         "flag_for_guidelines_update": False, "requires_human_review": False},
        {"pattern_id": "P4", "classification": "Substantial Variability",
         "confidence": "High", "evidence": "G16 -- x",
         "flag_for_guidelines_update": True, "requires_human_review": False},
        {"pattern_id": "P9", "classification": "Occasional Variability",
         "confidence": "High", "evidence": "no guideline",
         "flag_for_guidelines_update": False, "requires_human_review": False},
    ])
    items = hrq.build_review_items(vc, _dp(), "ucd_ch", include_medium=True)
    ids = [it["pattern_id"] for it in items]
    assert ids == ["P1", "P4"]            # P9 (High, no flag) excluded
    p1 = items[0]
    assert p1["review_id"] == "HRQ-ucd_ch-P1"
    assert p1["source_pattern_id"] == "P1"
    assert len(p1["review_signature"]) == 16
    assert p1["signature_fields"] == hrq.SIGNATURE_FIELDS
    assert p1["provenance"]["policy_version"] == sip.POLICY_VERSION
    assert p1["provenance"]["source_setting"] == "ucd_ch"
    assert p1["pattern_kind"] == "guideline"
    assert p1["pattern_strength"]["display"] == "20.0%"
    assert items[1]["pattern_kind"] == "fragment"


def test_build_empty_when_all_high_no_flag():
    vc = _vc([
        {"pattern_id": "P1", "classification": "Occasional Variability",
         "confidence": "High", "evidence": "G1 -- x",
         "flag_for_guidelines_update": False, "requires_human_review": False},
    ])
    items = hrq.build_review_items(vc, _dp(), "cd_pw", include_medium=True)
    assert items == []


# ---------------------------------------------------------------------------
# Idempotency / dedup
# ---------------------------------------------------------------------------

def test_write_queue_idempotent_and_dedups(monkeypatch):
    vc = _vc([
        {"pattern_id": "P4", "classification": "Substantial Variability",
         "confidence": "High", "evidence": "G16 -- x",
         "flag_for_guidelines_update": True, "requires_human_review": False},
    ])
    items = hrq.build_review_items(vc, _dp(), "ucd_ch")
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "q.jsonl"
        n1 = hrq.write_queue(items, path)
        lines1 = path.read_text(encoding="utf-8").strip().splitlines()
        n2 = hrq.write_queue(items, path)          # run twice
        lines2 = path.read_text(encoding="utf-8").strip().splitlines()
        assert n1 == n2 == 1
        assert len(lines1) == len(lines2) == 1     # no accumulation
        # explicit duplicate input must still collapse to one
        n3 = hrq.write_queue(items + items, path)
        assert n3 == 1

        manifest = Path(d) / "architecture-run.json"
        called = False

        def should_not_write(_payload, _path):
            nonlocal called
            called = True

        try:
            hrq.publish_stage_output(
                "review",
                items,
                output_path=path,
                writer=should_not_write,
                architecture_manifest=path,
            )
        except ValueError as exc:
            assert "different paths" in str(exc)
        else:
            raise AssertionError("output/manifest collision must fail closed")
        assert called is False

        def fail_writer(_payload, _path):
            raise OSError("fixture writer failure")

        try:
            hrq.publish_stage_output(
                "review",
                items,
                output_path=path,
                writer=fail_writer,
                architecture_manifest=manifest,
            )
        except OSError as exc:
            assert "fixture writer failure" in str(exc)
        else:
            raise AssertionError("writer failure must propagate")
        assert not manifest.exists()

        execution = hrq.publish_stage_output(
            "review",
            items,
            output_path=path,
            writer=hrq.write_queue,
            architecture_mode="parity",
            architecture_manifest=manifest,
        )
        assert execution.output == items
        assert path.exists()
        assert json.loads(manifest.read_text(encoding="utf-8"))[
            "parity_status"
        ] == "match"
        first_manifest = json.loads(manifest.read_text(encoding="utf-8"))
        first_artifact_bytes = path.read_bytes()
        first_manifest_bytes = manifest.read_bytes()
        changed_items = json.loads(json.dumps(items))
        changed_items[0]["ai_decision"]["justification"] = "Updated fixture rationale."
        with monkeypatch.context() as scoped:
            def fail_manifest(_manifest, _path):
                raise OSError("fixture manifest failure")

            scoped.setattr(architecture_bridge, "write_manifest", fail_manifest)
            try:
                hrq.publish_stage_output(
                    "review",
                    changed_items,
                    output_path=path,
                    writer=hrq.write_queue,
                    architecture_mode="parity",
                    architecture_manifest=manifest,
                )
            except OSError as exc:
                assert "fixture manifest failure" in str(exc)
            else:
                raise AssertionError("manifest failure must propagate")
        assert path.read_bytes() == first_artifact_bytes
        assert manifest.read_bytes() == first_manifest_bytes

        hrq.publish_stage_output(
            "review",
            changed_items,
            output_path=path,
            writer=hrq.write_queue,
            architecture_mode="parity",
            architecture_manifest=manifest,
        )
        second_manifest = json.loads(manifest.read_text(encoding="utf-8"))
        persisted_item = json.loads(path.read_text(encoding="utf-8").strip())
        assert persisted_item["ai_decision"]["justification"] == (
            "Updated fixture rationale."
        )
        assert second_manifest["input_sha256"] != first_manifest["input_sha256"]
        assert second_manifest["published_output_sha256"] != (
            first_manifest["published_output_sha256"]
        )


def test_publication_rejects_symlinked_output_before_resolution():
    vc = _vc([
        {
            "pattern_id": "P4",
            "classification": "Substantial Variability",
            "confidence": "High",
            "evidence": "G16 -- x",
            "flag_for_guidelines_update": True,
            "requires_human_review": False,
        },
    ])
    items = hrq.build_review_items(vc, _dp(), "ucd_ch")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        actual = root / "actual.jsonl"
        actual.write_text("preserve\n", encoding="utf-8")
        alias = root / "alias.jsonl"
        try:
            alias.symlink_to(actual)
        except OSError:
            return
        try:
            hrq.publish_stage_output(
                "review",
                items,
                output_path=alias,
                writer=hrq.write_queue,
            )
        except ValueError as exc:
            assert "symbolic links or reparse points" in str(exc)
        else:
            raise AssertionError("symlinked output must fail before publication")
        assert actual.read_text(encoding="utf-8") == "preserve\n"


def test_compatibility_cli_reports_parity_mismatch_as_failure():
    mismatch = SimpleNamespace(
        manifest=SimpleNamespace(parity_status="mismatch"),
    )
    try:
        architecture_bridge.require_cli_parity_success(mismatch)
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("a parity mismatch must produce a nonzero CLI exit")

    matching = SimpleNamespace(
        manifest=SimpleNamespace(parity_status="match"),
    )
    assert architecture_bridge.require_cli_parity_success(matching) is None


# ---------------------------------------------------------------------------
# Schema validation (skipped if jsonschema not installed)
# ---------------------------------------------------------------------------

def test_built_items_validate_against_schema():
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        print("    (skipped: jsonschema not installed)")
        return
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema)
    vc = _vc([
        {"pattern_id": "P4", "classification": "Substantial Variability",
         "confidence": "High", "evidence": "G16 -- x",
         "flag_for_guidelines_update": True, "requires_human_review": False},
        {"pattern_id": "P6", "classification": "Occasional Variability",
         "confidence": "Medium", "evidence": "Domain Description -- x",
         "flag_for_guidelines_update": False, "requires_human_review": False},
    ])
    for item in hrq.build_review_items(vc, _dp(), "ucd_ch"):
        validator.validate(item)


# ---------------------------------------------------------------------------
# Manual runner (no pytest required)
# ---------------------------------------------------------------------------

def _run_all() -> int:
    funcs = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in funcs:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {fn.__name__}: {exc!r}")
    print(f"\n{len(funcs) - failed}/{len(funcs)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run_all())
