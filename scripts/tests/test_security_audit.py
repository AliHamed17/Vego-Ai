from __future__ import annotations

import importlib.util
import io
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

    inner_bytes = io.BytesIO()
    github_key = "github" + "_pat_" + "sample_abcdefghijklmnopqrstuvwxyz1234567890"
    with zipfile.ZipFile(inner_bytes, "w") as inner:
        inner.writestr("token.txt", github_key)
    nested_path = tmp_path / "nested.zip"
    with zipfile.ZipFile(nested_path, "w") as outer:
        outer.writestr("inner.zip", inner_bytes.getvalue())
    nested_findings = module._zip_findings(nested_path)
    assert any(
        "nested.zip!inner.zip" in item
        and "github_token in archive member token.txt" in item
        for item in nested_findings
    )


def test_archive_limits_fail_closed(tmp_path: Path) -> None:
    module = load_module()
    module.ROOT = tmp_path
    module.MAX_ARCHIVE_MEMBER_BYTES = 4
    archive_path = tmp_path / "artifact.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("large.txt", "12345")
    findings = module._zip_findings(archive_path)
    assert any("archive member exceeds 4 bytes" in item for item in findings)

    module.MAX_ARCHIVE_MEMBER_BYTES = 25 * 1024 * 1024
    module.MAX_ARCHIVE_NESTING_DEPTH = 0
    inner_bytes = io.BytesIO()
    with zipfile.ZipFile(inner_bytes, "w") as inner:
        inner.writestr("record.txt", "safe")
    nested_path = tmp_path / "bounded.zip"
    with zipfile.ZipFile(nested_path, "w") as outer:
        outer.writestr("inner.zip", inner_bytes.getvalue())
    nested_findings = module._zip_findings(nested_path)
    assert any("archive nesting exceeds 0" in item for item in nested_findings)


def test_disguised_archives_are_scanned_by_magic_in_current_and_history(
    tmp_path: Path,
) -> None:
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
    secret = "AKIA" + "ABCDEFGHIJKLMNOP"
    disguised = tmp_path / "payload.bin"
    with zipfile.ZipFile(
        disguised,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        archive.writestr("secret.txt", secret)

    current = module.inspect(include_history=False)
    assert current["status"] == "FAIL"
    assert any(
        "payload.bin" in finding
        and "aws_access_key in archive member secret.txt" in finding
        for finding in current["binary_findings"]
    )

    git("add", "payload.bin")
    git("commit", "-m", "disguised archive fixture")
    disguised.unlink()
    git("add", "-u")
    git("commit", "-m", "remove disguised archive fixture")
    historical = module.inspect(include_history=True)
    assert any(
        "payload.bin" in finding
        and "aws_access_key in archive member secret.txt" in finding
        for finding in historical["history_findings"]
    )


def test_preamble_zip_is_scanned_in_current_tree_and_history(tmp_path: Path) -> None:
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
    archive_bytes = io.BytesIO()
    secret = "AKIA" + "ABCDEFGHIJKLMNOP"
    with zipfile.ZipFile(archive_bytes, "w") as archive:
        archive.writestr("secret.txt", secret)
    disguised = tmp_path / "launcher.bin"
    disguised.write_bytes(b"MZ launcher preamble" + archive_bytes.getvalue())

    current = module.inspect(include_history=False)
    assert any(
        "launcher.bin" in finding
        and "aws_access_key in archive member secret.txt" in finding
        for finding in current["binary_findings"]
    )

    git("add", "launcher.bin")
    git("commit", "-m", "preamble archive")
    disguised.unlink()
    git("add", "-u")
    git("commit", "-m", "remove preamble archive")
    historical = module.inspect(include_history=True)
    assert any(
        "launcher.bin" in finding
        and "aws_access_key in archive member secret.txt" in finding
        for finding in historical["history_findings"]
    )


def test_encrypted_pkcs8_private_keys_are_detected_in_content_and_history() -> None:
    module = load_module()
    encrypted_header = b"-----BEGIN ENCRYPTED " + b"PRIVATE KEY-----"
    fine_grained_token = (
        b"github" + b"_pat_" + b"sample_abcdefghijklmnopqrstuvwxyz1234567890"
    )
    assert "private_key" in module._secret_labels(encrypted_header)
    assert "github_token" in module._secret_labels(fine_grained_token)
    assert re.search(
        module.HISTORY_SCAN_EXPRESSION,
        encrypted_header.decode("ascii"),
    )
    assert re.search(
        module.HISTORY_SCAN_EXPRESSION,
        fine_grained_token.decode("ascii"),
    )


def test_fixture_substring_does_not_exempt_a_credential() -> None:
    module = load_module()
    credential = (
        b"sk"
        b"-proj-"
        b"productionfixtureabcdefghijklmnopqrstuvwxyz123456"
    )
    assert module._secret_labels(credential) == ["openai_key"]


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
    secret = "github" + "_pat_" + "sample_abcdefghijklmnopqrstuvwxyz1234567890"
    (tmp_path / "record.txt").write_text(secret + "\n", encoding="utf-8")
    git("commit", "-am", "fixture secret")
    archive_path = tmp_path / "historical.docx"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("word/document.xml", f"<w:t>{secret}</w:t>")
    git("add", "historical.docx")
    git("commit", "-m", "archive fixture secret")
    git("mv", "historical.docx", "historical.bin")
    git("commit", "-m", "rename archive fixture")
    renamed_archive = tmp_path / "historical.bin"
    renamed_archive.unlink()
    git("add", "-u")
    git("commit", "-m", "remove archive fixture")
    binary_secret = "AKIA" + "ABCDEFGHIJKLMNOP"
    binary_path = tmp_path / "historical.pdf"
    binary_path.write_bytes(b"%PDF-1.7\n\x00" + binary_secret.encode("ascii"))
    git("add", "historical.pdf")
    git("commit", "-m", "binary fixture secret")
    binary_path.unlink()
    git("add", "-u")
    git("commit", "-m", "remove binary fixture")

    result = module.inspect(include_history=True)
    assert result["history_findings"]
    assert any("record.txt" in finding for finding in result["history_findings"])
    assert any(
        "historical.docx" in finding and "archive member" in finding
        for finding in result["history_findings"]
    )
    assert any(
        "historical.pdf" in finding and "aws_access_key" in finding
        for finding in result["history_findings"]
    )


def test_git_path_parsers_preserve_newlines(monkeypatch) -> None:
    module = load_module()
    newline_path = b"secret\nbundle.zip"
    object_id = b"a" * 40
    raw_history = (
        b":100644 100644 "
        + object_id
        + b" "
        + object_id
        + b" M\0"
        + newline_path
        + b"\0"
    )

    def fake_git_bytes(*args: str) -> bytes:
        if args[0] == "ls-files":
            return newline_path + b"\0"
        if args[0] == "log":
            return raw_history
        raise AssertionError(args)

    monkeypatch.setattr(module, "_git_bytes", fake_git_bytes)
    assert module._candidate_files() == ["secret\nbundle.zip"]
    assert module._historical_blob_paths() == {
        object_id.decode("ascii"): {"secret\nbundle.zip"}
    }


def test_history_scan_command_failure_is_release_blocking(monkeypatch) -> None:
    module = load_module()
    monkeypatch.setattr(module, "_candidate_files", lambda: [])

    def fail_history() -> list[str]:
        raise subprocess.CalledProcessError(128, ["git", "log"])

    monkeypatch.setattr(module, "_historical_blob_findings", fail_history)
    with pytest.raises(subprocess.CalledProcessError):
        module.inspect(include_history=True)
