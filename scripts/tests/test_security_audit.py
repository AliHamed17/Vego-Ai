from __future__ import annotations

import importlib.util
import re
import subprocess
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "security_audit.py"


def load_module():
    spec = importlib.util.spec_from_file_location("security_audit", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_archive_member_contents_are_scanned_for_secrets(tmp_path: Path) -> None:
    module = load_module()
    module.ROOT = tmp_path
    archive_path = tmp_path / "artifact.docx"
    key = "sk" + "-proj-" + "abcdefghijklmnopqrstuvwxyz1234567890"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("word/document.xml", f"<w:t>{key}</w:t>")
    findings = module._zip_findings(archive_path)
    assert any("openai_key in archive member word/document.xml" in item for item in findings)


def test_archive_limits_fail_closed(tmp_path: Path) -> None:
    module = load_module()
    module.ROOT = tmp_path
    module.MAX_ARCHIVE_MEMBER_BYTES = 4
    archive_path = tmp_path / "artifact.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("large.txt", "12345")
    findings = module._zip_findings(archive_path)
    assert any("archive member exceeds 4 bytes" in item for item in findings)


def test_encrypted_pkcs8_private_keys_are_detected_in_content_and_history() -> None:
    module = load_module()
    encrypted_header = b"-----BEGIN ENCRYPTED " + b"PRIVATE KEY-----"
    assert "private_key" in module._secret_labels(encrypted_header)
    assert re.search(
        module.HISTORY_SCAN_EXPRESSION,
        encrypted_header.decode("ascii"),
    )


def test_history_scan_uses_a_git_compatible_expression(tmp_path: Path) -> None:
    module = load_module()
    module.ROOT = tmp_path

    def git(*args: str) -> None:
        subprocess.run(
            ["git", *args],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    git("init", "-b", "main")
    git("config", "user.name", "Fixture")
    git("config", "user.email", "fixture@example.invalid")
    (tmp_path / "record.txt").write_text("safe\n", encoding="utf-8")
    git("add", "record.txt")
    git("commit", "-m", "safe")
    secret = "sk" + "-proj-" + "abcdefghijklmnopqrstuvwxyz1234567890"
    (tmp_path / "record.txt").write_text(secret + "\n", encoding="utf-8")
    git("commit", "-am", "fixture secret")

    result = module.inspect(include_history=True)
    assert result["history_findings"]
    assert any("record.txt" in finding for finding in result["history_findings"])


def test_history_scan_command_failure_is_release_blocking(monkeypatch) -> None:
    module = load_module()
    monkeypatch.setattr(module, "_candidate_files", lambda: [])

    def fail_git(*_args: str) -> str:
        raise subprocess.CalledProcessError(128, ["git", "log"])

    monkeypatch.setattr(module, "_git", fail_git)
    with pytest.raises(subprocess.CalledProcessError):
        module.inspect(include_history=True)
