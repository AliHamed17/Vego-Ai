#!/usr/bin/env python3
"""Verify the Phase 0 tracked-file fingerprints for protected VEGO-AI paths."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

PROTECTED_PATHS = (
    "VEGO-AI/framework",
    "VEGO-AI/schemas",
    "VEGO-AI/tests",
    "VEGO-AI/eval",
    "VEGO-AI/inputs",
)


class BoundaryError(RuntimeError):
    """Raised when the boundary record or Git state cannot be inspected."""


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=repo,
            check=check,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = (
            exc.stderr.strip()
            if isinstance(exc, subprocess.CalledProcessError) and exc.stderr
            else str(exc)
        )
        raise BoundaryError(f"git {' '.join(args)} failed: {detail}") from exc


def parse_boundary_table(text: str) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    row_pattern = re.compile(
        r"^\|\s*`(?P<path>VEGO-AI/(?:framework|schemas|tests|eval|inputs))`\s*"
        r"\|\s*(?P<count>\d+)\s*\|\s*`(?P<sha>[0-9a-fA-F]{64})`\s*\|\s*$",
        re.MULTILINE,
    )
    for match in row_pattern.finditer(text):
        records[match.group("path")] = {
            "tracked_files": int(match.group("count")),
            "tree_sha256": match.group("sha").lower(),
        }
    missing = [path for path in PROTECTED_PATHS if path not in records]
    if missing:
        raise BoundaryError(f"boundary table is missing: {', '.join(missing)}")
    return records


def tracked_tree(repo: Path, directory: str) -> dict[str, Any]:
    output = run_git(repo, "ls-files", "--", directory).stdout
    paths = [line for line in output.splitlines() if line]
    # This mirrors Windows PowerShell Sort-Object: case-insensitive path order,
    # with the original path as a stable secondary key.
    paths.sort(key=lambda item: (item.casefold(), item))
    rows: list[str] = []
    for relative in paths:
        file_path = repo / Path(relative)
        if not file_path.is_file():
            raise BoundaryError(f"tracked file is absent from the working tree: {relative}")
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        rows.append(f"{relative}\t{digest}")
    tree_hash = hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()
    untracked = [
        line
        for line in run_git(
            repo, "ls-files", "--others", "--exclude-standard", "--", directory
        ).stdout.splitlines()
        if line
    ]
    return {
        "tracked_files": len(paths),
        "tree_sha256": tree_hash,
        "nonignored_untracked": untracked,
    }


def check_boundary(repo: Path, record_path: Path) -> dict[str, Any]:
    expected = parse_boundary_table(record_path.read_text(encoding="utf-8"))
    paths: dict[str, Any] = {}
    failures: list[str] = []
    for directory in PROTECTED_PATHS:
        current = tracked_tree(repo, directory)
        baseline = expected[directory]
        matches = (
            current["tracked_files"] == baseline["tracked_files"]
            and current["tree_sha256"] == baseline["tree_sha256"]
            and not current["nonignored_untracked"]
        )
        paths[directory] = {"baseline": baseline, "current": current, "matches": matches}
        if current["tracked_files"] != baseline["tracked_files"]:
            failures.append(
                f"{directory}: tracked-file count {current['tracked_files']} != {baseline['tracked_files']}"
            )
        if current["tree_sha256"] != baseline["tree_sha256"]:
            failures.append(
                f"{directory}: tree SHA-256 {current['tree_sha256']} != {baseline['tree_sha256']}"
            )
        if current["nonignored_untracked"]:
            failures.append(
                f"{directory}: nonignored untracked files: {', '.join(current['nonignored_untracked'])}"
            )

    diff = run_git(repo, "diff", "--name-only", "HEAD", "--", *PROTECTED_PATHS).stdout.splitlines()
    if diff:
        failures.append(f"protected tracked diff is nonempty: {', '.join(diff)}")
    try:
        record_label = record_path.relative_to(repo).as_posix()
    except ValueError:
        record_label = record_path.as_posix()
    return {
        "schema_version": "1.0",
        "boundary_record": record_label,
        "protected_paths": paths,
        "protected_diff": diff,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--record",
        type=Path,
        default=Path("docs/research/h-layer/phase-0-boundary-record.md"),
        help="Tracked boundary record",
    )
    parser.add_argument("--json", action="store_true", help="Print the full result as JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo = Path(__file__).resolve().parents[1]
    record = args.record if args.record.is_absolute() else repo / args.record
    try:
        result = check_boundary(repo, record)
    except (OSError, UnicodeError, BoundaryError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for directory, details in result["protected_paths"].items():
            marker = "OK" if details["matches"] else "FAIL"
            print(f"{marker}: {directory} ({details['current']['tracked_files']} tracked files)")
        for failure in result["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
        print(f"protected_path_status: {result['status']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
