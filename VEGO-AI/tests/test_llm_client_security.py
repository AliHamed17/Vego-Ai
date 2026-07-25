from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "framework"))

from llm_client import LLMClient  # noqa: E402

# Assembled from fragments so no key-shaped literal is stored in a tracked file
# (scripts/check_repository_privacy.py scans for those). The runtime value is a
# realistic-length fake token, which is what the redaction test needs.
FAKE_API_KEY = "sk" + "-proj-fixture-not-a-real-key"
FAKE_LONG_TOKEN = "sk" + "-proj-" + "fixtureabcdefghijklmnopqrstuvwxyz123456"
FAKE_GITHUB_TOKEN = "gh" + "o_fixtureabcdefghijklmnopqrstuvwxyz123456"


def _response():
    return SimpleNamespace(
        model="gpt-4o-2024-11-20",
        system_fingerprint="fp_fixture",
        usage=SimpleNamespace(
            prompt_tokens=10,
            completion_tokens=4,
            total_tokens=14,
        ),
    )


def test_plaintext_api_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        LLMClient(api_key=FAKE_API_KEY)


def test_metadata_only_log_contains_hashes_not_content(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", FAKE_API_KEY)
    path = tmp_path / "interaction.jsonl"
    client = LLMClient(interaction_log=path, interaction_log_mode="metadata_only")
    client._write_interaction(
        label="agent1/test",
        prompt={"system": "private system", "user": "private user"},
        raw='{"ok":true}',
        parsed={"ok": True},
        parse_error=None,
        response=_response(),
        attempt=1,
    )
    entry = json.loads(path.read_text(encoding="utf-8"))
    assert entry["requested_model"] == "gpt-4o"
    assert entry["returned_model"] == "gpt-4o-2024-11-20"
    assert entry["sdk_version"] == "1.109.1"
    assert entry["retry_count"] == 0
    assert entry["response_parsed"] is True
    assert "prompt_system" not in entry
    assert "prompt_user" not in entry
    assert "response_raw" not in entry
    assert "private system" not in path.read_text(encoding="utf-8")
    schema = json.loads(
        (
            ROOT.parent / "schemas" / "model-execution-manifest-v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    Draft202012Validator(schema).validate(entry)


def test_full_content_log_requires_opt_in_and_redacts_secrets(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", FAKE_API_KEY)
    path = tmp_path / "interaction.jsonl"
    client = LLMClient(interaction_log=path, interaction_log_mode="full_content")
    client._write_interaction(
        label="agent1/test",
        prompt={
            "system": "system",
            "user": f"token {FAKE_LONG_TOKEN}",
        },
        raw=json.dumps({"token": FAKE_GITHUB_TOKEN}),
        parsed={"ok": True},
        parse_error=None,
        response=_response(),
        attempt=1,
    )
    text = path.read_text(encoding="utf-8")
    assert "REDACTED_SECRET" in text
    assert FAKE_LONG_TOKEN not in text
    assert FAKE_GITHUB_TOKEN not in text


def test_off_mode_writes_nothing(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", FAKE_API_KEY)
    path = tmp_path / "interaction.jsonl"
    client = LLMClient(interaction_log=path, interaction_log_mode="off")
    client._write_interaction(
        label="agent1/test",
        prompt={"system": "system", "user": "user"},
        raw="{}",
        parsed={},
        parse_error=None,
        response=_response(),
        attempt=1,
    )
    assert not path.exists()


def test_interaction_log_rejects_network_path(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", FAKE_API_KEY)
    with pytest.raises(ValueError, match="local storage"):
        LLMClient(interaction_log=Path("//server/share/interaction.jsonl"))


def test_interaction_log_retention_is_bounded(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", FAKE_API_KEY)
    with pytest.raises(ValueError, match="between 1 and 365"):
        LLMClient(
            interaction_log=tmp_path / "interaction.jsonl",
            interaction_log_retention_days=0,
        )
