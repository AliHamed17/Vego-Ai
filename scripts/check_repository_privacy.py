#!/usr/bin/env python3
"""Fail when Git-tracked files contain private meeting artifacts or likely secrets."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PATH_PATTERNS = [
    re.compile(r"video1832857678", re.IGNORECASE),
    re.compile(r"(?:^|/)(?:raw[-_]?asr|meeting[-_]?recordings?)(?:/|$)", re.IGNORECASE),
    re.compile(r"exp[-_]?005.*(?:filled|gold|expert[-_]?labels?)", re.IGNORECASE),
    re.compile(r"(?:^|/)\.env$", re.IGNORECASE),
    re.compile(r"\.local\.json$", re.IGNORECASE),
]
ALLOWED_PATHS = {".env.example"}
SECRET_PATTERNS = [
    re.compile(r"\bghp_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
    re.compile(r"\bsk-proj-[A-Za-z0-9_-]{30,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
MAX_TEXT_BYTES = 2_000_000


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "-c", "-o", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / item.decode("utf-8", errors="surrogateescape") for item in result.stdout.split(b"\0") if item]


def main() -> int:
    failures: list[str] = []
    for path in tracked_files():
        relative = path.relative_to(ROOT).as_posix()
        lowered = relative.lower()
        if lowered in ALLOWED_PATHS:
            continue
        if any(pattern.search(lowered) for pattern in PRIVATE_PATH_PATTERNS):
            failures.append(f"tracked private/local artifact: {relative}")
            continue
        try:
            if path.stat().st_size > MAX_TEXT_BYTES:
                continue
            data = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(data):
                failures.append(f"likely secret in tracked text: {relative} ({pattern.pattern})")
                break
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("repository privacy scan: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
