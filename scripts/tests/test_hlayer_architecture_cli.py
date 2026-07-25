from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_hlayer_architecture as architecture_cli  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def test_parity_cli_publishes_legacy_shape_and_manifest(
    tmp_path: Path,
    monkeypatch,
) -> None:
    payload = [
        {
            "review_id": "HRQ-ucd_ch-P1",
            "review_signature": "0123456789abcdef",
            "status": "pending",
            "pattern_id": "P1",
            "provenance": {"source": "fixture"},
            "ai_decision": {
                "classification": "Occasional Variability",
                "confidence": "Medium",
            },
        }
    ]
    source = tmp_path / "review.jsonl"
    source.write_text(
        "".join(json.dumps(item) + "\n" for item in payload),
        encoding="utf-8",
    )
    output = tmp_path / "published.jsonl"
    manifest = tmp_path / "manifest.json"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_hlayer_architecture.py"),
            "--stage",
            "review",
            "--input",
            str(source),
            "--output",
            str(output),
            "--manifest",
            str(manifest),
            "--mode",
            "parity",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()] == payload
    record = json.loads(manifest.read_text(encoding="utf-8"))
    assert record["parity_status"] == "match"
    assert record["baseline_preserved"] is True

    failed_output = tmp_path / "failed-output.jsonl"
    failed_manifest = tmp_path / "failed-manifest.json"
    with monkeypatch.context() as scoped:
        def fail_manifest(_manifest, _path):
            raise OSError("fixture manifest staging failure")

        scoped.setattr(architecture_cli, "write_manifest", fail_manifest)
        exit_code = architecture_cli.main(
            [
                "--stage",
                "review",
                "--input",
                str(source),
                "--output",
                str(failed_output),
                "--manifest",
                str(failed_manifest),
                "--mode",
                "parity",
            ]
        )
    assert exit_code == 2
    assert not failed_output.exists()
    assert not failed_manifest.exists()

    failed_output = tmp_path / "replace-failed-output.jsonl"
    failed_manifest = tmp_path / "replace-failed-manifest.json"
    real_replace = architecture_cli.os.replace
    publication_replacements = 0

    def fail_second_publication(source_path, destination_path):
        nonlocal publication_replacements
        if Path(destination_path) in {failed_output, failed_manifest}:
            publication_replacements += 1
            if publication_replacements == 2:
                raise OSError("fixture manifest publication failure")
        return real_replace(source_path, destination_path)

    with monkeypatch.context() as scoped:
        scoped.setattr(architecture_cli.os, "replace", fail_second_publication)
        exit_code = architecture_cli.main(
            [
                "--stage",
                "review",
                "--input",
                str(source),
                "--output",
                str(failed_output),
                "--manifest",
                str(failed_manifest),
                "--mode",
                "parity",
            ]
        )
    assert exit_code == 2
    assert not failed_output.exists()
    assert not failed_manifest.exists()


def test_cli_rejects_shared_output_and_manifest_before_publishing(tmp_path: Path) -> None:
    payload = [
        {
            "review_id": "HRQ-ucd_ch-P1",
            "review_signature": "0123456789abcdef",
            "status": "pending",
            "pattern_id": "P1",
            "provenance": {"source": "fixture"},
            "ai_decision": {
                "classification": "Occasional Variability",
                "confidence": "Medium",
            },
        }
    ]
    source = tmp_path / "review.jsonl"
    source.write_text(json.dumps(payload[0]) + "\n", encoding="utf-8")
    shared = tmp_path / "shared.json"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_hlayer_architecture.py"),
            "--stage",
            "review",
            "--input",
            str(source),
            "--output",
            str(shared),
            "--manifest",
            str(shared),
            "--mode",
            "parity",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert result.returncode == 2
    assert "must use different paths" in result.stderr
    assert not shared.exists()


def test_comparison_cli_reports_nested_shape_errors_without_traceback(
    tmp_path: Path,
) -> None:
    payload = {
        "comparisons": [
            {
                "comparison_id": "CMP-ucd_ch-P1",
                "setting_id": "ucd_ch",
                "pattern_id": "P1",
                "original_agent4_classification": "Occasional Variability",
                "memory_informed_classification": {
                    "classification": "Occasional Variability",
                    "source": "original_agent4",
                },
                "memory_informed_differs_from_original": False,
                "requires_human_review_after_memory": False,
                "human_memory_used": [],
                "evaluation_leakage_status": "none",
                "rule_applied": "preserve_original",
                "decision_trace": ["baseline preserved"],
                "mode": "experimental",
                "ai_behavior_changed_in_baseline": False,
            }
        ],
        "provenance": {"source": "fixture"},
    }
    source = tmp_path / "comparison.json"
    source.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "published.json"
    manifest = tmp_path / "manifest.json"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_hlayer_architecture.py"),
            "--stage",
            "comparison",
            "--input",
            str(source),
            "--output",
            str(output),
            "--manifest",
            str(manifest),
            "--mode",
            "unified",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert result.returncode == 2
    assert (
        "original_agent4_classification must be an object"
        in result.stderr
    )
    assert "Traceback" not in result.stderr
    assert not output.exists()
    assert not manifest.exists()


def test_parity_cli_path_preserves_legacy_when_adapter_drifts(monkeypatch) -> None:
    payload = [
        {
            "review_id": "HRQ-ucd_ch-P1",
            "review_signature": "0123456789abcdef",
            "status": "pending",
            "pattern_id": "P1",
            "provenance": {"source": "fixture"},
            "ai_decision": {
                "classification": "Occasional Variability",
                "confidence": "Medium",
            },
        }
    ]

    @dataclass(frozen=True)
    class ChangedAdapter:
        records: tuple[dict, ...] = ()

        def to_legacy(self):
            changed = json.loads(json.dumps(payload))
            changed[0]["status"] = "resolved"
            return changed

    monkeypatch.setattr(
        "vego_hlayer.runtime.adapt_legacy_artifact",
        lambda stage, value: ChangedAdapter(),
    )
    execution = architecture_cli._execute_isolated("review", payload, "parity")
    assert execution.manifest.parity_status == "mismatch"
    assert execution.output == payload
    assert execution.legacy_output == payload
    assert execution.unified_output != payload
