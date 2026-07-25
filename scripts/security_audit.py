#!/usr/bin/env python3
"""Clone-safe secret, privacy, and tracked-binary safety audit."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SECRET_PATTERNS = {
    "openai_key": re.compile(
        rb"\b(?:sk-proj-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,})\b"
    ),
    "github_token": re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "private_key": re.compile(
        rb"-----BEGIN (?:(?:RSA|EC|OPENSSH|ENCRYPTED) )?PRIVATE KEY-----"
    ),
    "aws_access_key": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
}
HISTORY_SECRET_EXPRESSION = (
    r"sk-proj-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,}|"
    r"gh[pousr]_[A-Za-z0-9]{20,}|"
    r"AKIA[0-9A-Z]{16}|"
    r"BEGIN (?:(?:RSA|EC|OPENSSH|ENCRYPTED) )?PRIVATE KEY"
)
PERSONAL_PATH_RE = re.compile(
    rb"(?:[A-Za-z]:[\\/](?:Users|home)[\\/]|file:///)", re.IGNORECASE
)
CURRENT_SHAREABLE = (
    "docs/research/hardening/",
    "src/vego_hlayer/",
    "schemas/",
    "VEGO-AI-Thesis-Baseline-Progress.html",
    "thesis/output/",
)
MAGIC = {
    ".pdf": (b"%PDF-",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".gif": (b"GIF87a", b"GIF89a"),
    ".zip": (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
    ".docx": (b"PK\x03\x04",),
    ".pptx": (b"PK\x03\x04",),
    ".xlsx": (b"PK\x03\x04",),
}
ZIP_SUFFIXES = frozenset({".zip", ".docx", ".pptx", ".xlsx"})
MAX_ARCHIVE_MEMBERS = 10_000
MAX_ARCHIVE_MEMBER_BYTES = 25 * 1024 * 1024
MAX_ARCHIVE_SCAN_BYTES = 100 * 1024 * 1024
MAX_ARCHIVE_EXPANDED_BYTES = 500 * 1024 * 1024
GIT = shutil.which("git")


def _git(*args: str) -> str:
    if not GIT:
        raise OSError("git executable not found")
    return subprocess.run(  # noqa: S603 - executable and arguments are controlled
        [GIT, *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout


def _candidate_files() -> list[str]:
    return sorted(
        {
            line
            for line in _git(
                "ls-files", "--cached", "--others", "--exclude-standard"
            ).splitlines()
            if line
        }
    )


def _is_text(data: bytes) -> bool:
    return b"\0" not in data[:8192]


def _secret_labels(data: bytes) -> list[str]:
    labels: list[str] = []
    for label, pattern in SECRET_PATTERNS.items():
        matches = [
            match.group(0)
            for match in pattern.finditer(data)
            if b"fixture" not in match.group(0).lower()
        ]
        if matches:
            labels.append(label)
    return labels


def _zip_findings(path: Path) -> list[str]:
    findings: list[str] = []
    relative = path.relative_to(ROOT).as_posix()
    try:
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            if len(members) > MAX_ARCHIVE_MEMBERS:
                return [f"{relative}: archive member count exceeds {MAX_ARCHIVE_MEMBERS}"]
            total = 0
            scanned = 0
            for info in members:
                name = info.filename.replace("\\", "/")
                pure = PurePosixPath(name)
                if pure.is_absolute() or ".." in pure.parts:
                    findings.append(f"{relative}: unsafe archive path: {name}")
                if info.is_dir():
                    continue
                total += info.file_size
                if info.compress_size and info.file_size / info.compress_size > 1000:
                    findings.append(
                        f"{relative}: compression ratio exceeds 1000: {name}"
                    )
                    continue
                if info.file_size > MAX_ARCHIVE_MEMBER_BYTES:
                    findings.append(
                        f"{relative}: archive member exceeds "
                        f"{MAX_ARCHIVE_MEMBER_BYTES} bytes: {name}"
                    )
                    continue
                if scanned + info.file_size > MAX_ARCHIVE_SCAN_BYTES:
                    findings.append(
                        f"{relative}: archive content scan exceeds "
                        f"{MAX_ARCHIVE_SCAN_BYTES} bytes"
                    )
                    break
                data = archive.read(info)
                scanned += len(data)
                for label in _secret_labels(data):
                    findings.append(f"{relative}: {label} in archive member {name}")
                if relative.startswith(CURRENT_SHAREABLE) and PERSONAL_PATH_RE.search(data):
                    findings.append(f"{relative}: personal absolute path in archive member {name}")
            if total > MAX_ARCHIVE_EXPANDED_BYTES:
                findings.append(
                    f"{relative}: archive expands beyond 500 MiB"
                )
    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
        findings.append(f"{relative}: invalid archive: {exc}")
    return findings


def inspect(include_history: bool = False) -> dict[str, Any]:
    secret_findings: list[str] = []
    privacy_findings: list[str] = []
    binary_findings: list[str] = []
    candidates = _candidate_files()
    for relative in candidates:
        path = ROOT / relative
        if not path.is_file():
            continue
        data = path.read_bytes()
        for label in _secret_labels(data):
            secret_findings.append(f"{relative}: {label}")
        if relative.startswith(CURRENT_SHAREABLE) and PERSONAL_PATH_RE.search(data):
            privacy_findings.append(f"{relative}: personal absolute path")
        suffix = path.suffix.lower()
        if suffix == ".mp4":
            if len(data) < 12 or data[4:8] != b"ftyp":
                binary_findings.append(f"{relative}: invalid MP4 signature")
        elif suffix in MAGIC and not any(data.startswith(prefix) for prefix in MAGIC[suffix]):
            binary_findings.append(f"{relative}: extension/magic mismatch")
        if suffix in ZIP_SUFFIXES:
            binary_findings.extend(_zip_findings(path))

    history_findings: list[str] = []
    if include_history:
        if not GIT:
            raise OSError("git executable not found")
        result = subprocess.run(  # noqa: S603 - fixed read-only Git history scan
            [
                GIT,
                "log",
                "--all",
                "--pretty=format:%H",
                "--name-only",
                "-G",
                HISTORY_SECRET_EXPRESSION,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        history_findings = sorted(set(line for line in result.stdout.splitlines() if line))

    failures = secret_findings + privacy_findings + binary_findings + history_findings
    return {
        "audit": "vego-ai-security-audit-v1",
        "files_scanned": len(candidates),
        "secret_findings": secret_findings,
        "privacy_findings": privacy_findings,
        "binary_findings": binary_findings,
        "history_findings": history_findings,
        "status": "PASS" if not failures else "FAIL",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = inspect(include_history=args.history)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"security_audit_status: {result['status']} "
            f"({result['files_scanned']} tracked or candidate files)"
        )
        for category in (
            "secret_findings",
            "privacy_findings",
            "binary_findings",
            "history_findings",
        ):
            for finding in result[category]:
                print(f"FAIL: {finding}", file=sys.stderr)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
