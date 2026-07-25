from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import run_hlayer_architecture as architecture_cli

ROOT = Path(__file__).resolve().parents[2]


def test_parity_cli_publishes_legacy_shape_and_manifest(tmp_path: Path) -> None:
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
