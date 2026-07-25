from __future__ import annotations

import json
import os
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
FAKE_GITHUB_REFRESH_TOKEN = "gh" + "r_fixtureabcdefghijklmnopqrstuvwxyz123456"
FAKE_AWS_KEY = "AK" + "IA" + "ABCDEFGHIJKLMNOP"
FAKE_PRIVATE_KEY = (
    "-----BEGIN "
    + "PRIVATE KEY-----\nfixture-private-material\n-----END "
    + "PRIVATE KEY-----"
)
FAKE_ENCRYPTED_PRIVATE_KEY = (
    "-----BEGIN ENCRYPTED "
    + "PRIVATE KEY-----\nfixture-encrypted-private-material\n-----END ENCRYPTED "
    + "PRIVATE KEY-----"
)


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
            "user": f"tokens {FAKE_LONG_TOKEN} {FAKE_AWS_KEY}",
        },
        raw=json.dumps(
            {
                "token": FAKE_GITHUB_TOKEN,
                "refresh": FAKE_GITHUB_REFRESH_TOKEN,
                "pem": FAKE_PRIVATE_KEY,
                "encrypted_pem": FAKE_ENCRYPTED_PRIVATE_KEY,
            }
        ),
        parsed={
            FAKE_LONG_TOKEN: "secret-shaped key",
            "pem": FAKE_PRIVATE_KEY,
        },
        parse_error=None,
        response=_response(),
        attempt=1,
    )
    text = path.read_text(encoding="utf-8")
    assert "REDACTED_SECRET" in text
    assert FAKE_LONG_TOKEN not in text
    assert FAKE_GITHUB_TOKEN not in text
    assert FAKE_GITHUB_REFRESH_TOKEN not in text
    assert FAKE_AWS_KEY not in text
    assert "fixture-private-material" not in text
    assert "fixture-encrypted-private-material" not in text
    entry = json.loads(text)
    assert "[REDACTED_SECRET]" in entry["response_parsed_content"]


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


def test_expired_log_is_removed_and_pending_entry_triggers_rotation(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", FAKE_API_KEY)
    path = tmp_path / "interaction.jsonl"
    path.write_text("expired private content\n", encoding="utf-8")
    os.utime(path, (1, 1))
    client = LLMClient(
        interaction_log=path,
        interaction_log_mode="metadata_only",
        interaction_log_max_bytes=4096,
        interaction_log_retention_days=1,
    )
    client._write_interaction(
        label="agent1/test",
        prompt={"system": "system", "user": "user"},
        raw="{}",
        parsed={},
        parse_error=None,
        response=_response(),
        attempt=1,
    )
    text = path.read_text(encoding="utf-8")
    assert "expired private content" not in text
    assert json.loads(text)["schema_version"] == "model-execution-manifest-v1"

    near_limit = "x" * (client._log_max_bytes - 1)
    path.write_text(near_limit, encoding="utf-8")
    client._write_interaction(
        label="agent1/test",
        prompt={"system": "system", "user": "user"},
        raw="{}",
        parsed={},
        parse_error=None,
        response=_response(),
        attempt=1,
    )
    backup = path.with_suffix(f"{path.suffix}.1")
    assert backup.read_text(encoding="utf-8") == near_limit
    assert path.stat().st_size < client._log_max_bytes
    assert json.loads(path.read_text(encoding="utf-8"))[
        "schema_version"
    ] == "model-execution-manifest-v1"


def test_runtime_config_controls_production_log_policy(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", FAKE_API_KEY)
    policy = tmp_path / "hlayer-runtime.json"
    policy.write_text(
        json.dumps(
            {
                "h_layer": {
                    "interaction_log_mode": "off",
                    "interaction_log": {
                        "retention_days": 7,
                        "max_bytes": 4096,
                        "backups": 2,
                        "redaction_enabled": True,
                        "full_content_local_only": True,
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("VEGO_HLAYER_RUNTIME_CONFIG", str(policy))
    chmod_calls = []
    monkeypatch.setattr(
        Path,
        "chmod",
        lambda path, mode: chmod_calls.append((path, mode)),
    )
    client = LLMClient(interaction_log=tmp_path / "interaction.jsonl")
    assert chmod_calls == []
    assert client._log_mode == "off"
    assert client._log_retention_days == 7
    assert client._log_max_bytes == 4096
    assert client._log_backups == 2
