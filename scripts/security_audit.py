#!/usr/bin/env python3
"""Clone-safe secret, privacy, and tracked-binary safety audit."""

from __future__ import annotations

import argparse
import io
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
    "github_token": re.compile(
        rb"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{40,})\b"
    ),
    "private_key": re.compile(
        rb"-----BEGIN (?:(?:RSA|EC|OPENSSH|ENCRYPTED) )?PRIVATE KEY-----"
    ),
    "aws_access_key": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
}
HISTORY_SCAN_EXPRESSION = (
    r"sk-proj-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,}|"
    r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{40,}|"
    r"AKIA[0-9A-Z]{16}|"
    r"BEGIN ((RSA|EC|OPENSSH|ENCRYPTED) )?PRIVATE KEY"
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
MAX_ARCHIVE_NESTING_DEPTH = 3
MAX_HISTORY_BLOB_BYTES = 100 * 1024 * 1024
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


def _git_bytes(*args: str) -> bytes:
    if not GIT:
        raise OSError("git executable not found")
    return subprocess.run(  # noqa: S603 - executable and arguments are controlled
        [GIT, *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def _git_bytes_with_input(input_data: bytes, *args: str) -> bytes:
    if not GIT:
        raise OSError("git executable not found")
    return subprocess.run(  # noqa: S603 - executable and arguments are controlled
        [GIT, *args],
        cwd=ROOT,
        input=input_data,
        check=True,
        capture_output=True,
    ).stdout


def _decode_git_path(raw: bytes) -> str:
    return raw.decode("utf-8", errors="surrogateescape")


def _nul_paths(raw: bytes) -> list[str]:
    return [
        _decode_git_path(item)
        for item in raw.split(b"\0")
        if item
    ]


def _display_git_path(path: str) -> str:
    """Escape control characters without changing the path used for I/O."""

    return json.dumps(path, ensure_ascii=True)[1:-1]


def _candidate_files() -> list[str]:
    return sorted(
        set(
            _nul_paths(
                _git_bytes(
                    "ls-files",
                    "-z",
                    "--cached",
                    "--others",
                    "--exclude-standard",
                )
            )
        )
    )


def _is_text(data: bytes) -> bool:
    return b"\0" not in data[:8192]


def _secret_labels(data: bytes) -> list[str]:
    labels: list[str] = []
    for label, pattern in SECRET_PATTERNS.items():
        if pattern.search(data):
            labels.append(label)
    return labels


def _is_zip_data(data: bytes) -> bool:
    return any(data.startswith(prefix) for prefix in MAGIC[".zip"])


def _zip_data_findings(
    data: bytes,
    display_path: str,
    *,
    check_personal_paths: bool,
    nesting_depth: int = 0,
) -> list[str]:
    findings: list[str] = []
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = archive.infolist()
            if len(members) > MAX_ARCHIVE_MEMBERS:
                return [
                    f"{display_path}: archive member count exceeds {MAX_ARCHIVE_MEMBERS}"
                ]
            total = 0
            scanned = 0
            for info in members:
                name = info.filename.replace("\\", "/")
                pure = PurePosixPath(name)
                if pure.is_absolute() or ".." in pure.parts:
                    findings.append(f"{display_path}: unsafe archive path: {name}")
                if info.is_dir():
                    continue
                total += info.file_size
                if info.compress_size and info.file_size / info.compress_size > 1000:
                    findings.append(
                        f"{display_path}: compression ratio exceeds 1000: {name}"
                    )
                    continue
                if info.file_size > MAX_ARCHIVE_MEMBER_BYTES:
                    findings.append(
                        f"{display_path}: archive member exceeds "
                        f"{MAX_ARCHIVE_MEMBER_BYTES} bytes: {name}"
                    )
                    continue
                if scanned + info.file_size > MAX_ARCHIVE_SCAN_BYTES:
                    findings.append(
                        f"{display_path}: archive content scan exceeds "
                        f"{MAX_ARCHIVE_SCAN_BYTES} bytes"
                    )
                    break
                member_data = archive.read(info)
                scanned += len(member_data)
                for label in _secret_labels(member_data):
                    findings.append(
                        f"{display_path}: {label} in archive member {name}"
                    )
                if check_personal_paths and PERSONAL_PATH_RE.search(member_data):
                    findings.append(
                        f"{display_path}: personal absolute path in archive member {name}"
                    )
                if _is_zip_data(member_data):
                    nested_display = f"{display_path}!{name}"
                    if nesting_depth >= MAX_ARCHIVE_NESTING_DEPTH:
                        findings.append(
                            f"{nested_display}: archive nesting exceeds "
                            f"{MAX_ARCHIVE_NESTING_DEPTH}"
                        )
                    else:
                        findings.extend(
                            _zip_data_findings(
                                member_data,
                                nested_display,
                                check_personal_paths=check_personal_paths,
                                nesting_depth=nesting_depth + 1,
                            )
                        )
            if total > MAX_ARCHIVE_EXPANDED_BYTES:
                findings.append(
                    f"{display_path}: archive expands beyond 500 MiB"
                )
    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
        findings.append(f"{display_path}: invalid archive: {exc}")
    return findings


def _zip_findings(path: Path) -> list[str]:
    relative = path.relative_to(ROOT).as_posix()
    return _zip_data_findings(
        path.read_bytes(),
        relative,
        check_personal_paths=relative.startswith(CURRENT_SHAREABLE),
    )


def _historical_blob_paths() -> dict[str, set[str]]:
    """Return every reachable changed blob and all of its raw Git paths."""

    blobs: dict[str, set[str]] = {}
    raw_history = _git_bytes(
        "log",
        "--all",
        "--raw",
        "-z",
        "--no-renames",
        "--no-abbrev",
        "--format=",
    )
    fields_and_paths = raw_history.split(b"\0")
    index = 0
    while index < len(fields_and_paths):
        metadata = fields_and_paths[index]
        index += 1
        if not metadata:
            continue
        if not metadata.startswith(b":") or index >= len(fields_and_paths):
            raise OSError("malformed NUL-delimited Git raw history")
        relative_raw = fields_and_paths[index]
        index += 1
        if not relative_raw:
            raise OSError("Git raw history contains an empty path")
        relative = _decode_git_path(relative_raw)
        fields = metadata[1:].split()
        if len(fields) < 5:
            raise OSError("malformed Git raw-history metadata")
        for object_id in fields[2:4]:
            if object_id and object_id.strip(b"0"):
                blobs.setdefault(object_id.decode("ascii"), set()).add(relative)
    return blobs


def _historical_blob_sizes(object_ids: list[str]) -> dict[str, int]:
    if not object_ids:
        return {}
    query = "".join(f"{object_id}\n" for object_id in object_ids).encode("ascii")
    output = _git_bytes_with_input(
        query,
        "cat-file",
        "--batch-check=%(objectname) %(objecttype) %(objectsize)",
    )
    sizes: dict[str, int] = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) != 3:
            raise OSError("malformed Git cat-file batch-check response")
        object_id, object_type, size_raw = fields
        if object_type != b"blob":
            continue
        try:
            sizes[object_id.decode("ascii")] = int(size_raw)
        except ValueError as exc:
            raise OSError("invalid Git cat-file object size") from exc
    return sizes


def _historical_blob_data(object_ids: list[str]) -> dict[str, bytes]:
    if not object_ids:
        return {}
    query = "".join(f"{object_id}\n" for object_id in object_ids).encode("ascii")
    output = _git_bytes_with_input(query, "cat-file", "--batch")
    cursor = 0
    blobs: dict[str, bytes] = {}
    for expected in object_ids:
        newline = output.find(b"\n", cursor)
        if newline < 0:
            raise OSError("truncated Git cat-file batch header")
        header = output[cursor:newline].split()
        cursor = newline + 1
        if len(header) != 3 or header[1] != b"blob":
            raise OSError(f"unexpected Git object response for {expected}")
        object_id = header[0].decode("ascii")
        try:
            size = int(header[2])
        except ValueError as exc:
            raise OSError("invalid Git cat-file batch size") from exc
        end = cursor + size
        if end >= len(output) or output[end : end + 1] != b"\n":
            raise OSError(f"truncated Git blob response for {object_id}")
        blobs[object_id] = output[cursor:end]
        cursor = end + 1
    if output[cursor:]:
        raise OSError("unexpected trailing Git cat-file batch data")
    return blobs


def _historical_blob_findings() -> list[str]:
    """Inspect reachable historical blobs, including deleted binary content."""

    findings: list[str] = []
    paths_by_blob = _historical_blob_paths()
    object_ids = sorted(paths_by_blob)
    sizes = _historical_blob_sizes(object_ids)
    eligible: list[str] = []
    for object_id in object_ids:
        if object_id not in sizes:
            # Gitlinks and other non-blob entries are not file contents.
            continue
        paths = sorted(paths_by_blob[object_id])
        display_path = _display_git_path(paths[0])
        size = sizes[object_id]
        if size > MAX_HISTORY_BLOB_BYTES:
            findings.append(
                f"history blob {object_id[:12]}:{display_path}: exceeds "
                f"{MAX_HISTORY_BLOB_BYTES} bytes and was not inspected"
            )
        else:
            eligible.append(object_id)

    for object_id, data in _historical_blob_data(eligible).items():
        paths = sorted(paths_by_blob[object_id])
        display_path = _display_git_path(paths[0])
        display = f"history blob {object_id[:12]}:{display_path}"
        for label in _secret_labels(data):
            findings.append(f"{display}: {label}")
        archive_paths = [
            path for path in paths if Path(path).suffix.lower() in ZIP_SUFFIXES
        ]
        if archive_paths or _is_zip_data(data):
            representative = sorted(archive_paths)[0] if archive_paths else paths[0]
            archive_display = (
                f"history archive {object_id[:12]}:"
                f"{_display_git_path(representative)}"
            )
            findings.extend(
                _zip_data_findings(
                    data,
                    archive_display,
                    check_personal_paths=False,
                )
            )
    return sorted(set(findings))


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
        if suffix in ZIP_SUFFIXES or _is_zip_data(data):
            binary_findings.extend(
                _zip_data_findings(
                    data,
                    relative,
                    check_personal_paths=relative.startswith(CURRENT_SHAREABLE),
                )
            )

    history_findings: list[str] = []
    if include_history:
        history_findings = _historical_blob_findings()

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
