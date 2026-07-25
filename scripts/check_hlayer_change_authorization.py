#!/usr/bin/env python3
"""Fail when a protected VEGO-AI change is outside the reviewed allowlist."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

PROTECTED_PREFIXES = (
    "VEGO-AI/framework/",
    "VEGO-AI/schemas/",
    "VEGO-AI/tests/",
    "VEGO-AI/eval/",
    "VEGO-AI/eval_output/",
    "VEGO-AI/inputs/",
)
GIT = shutil.which("git")


def _git(repo: Path, *args: str) -> str:
    if not GIT:
        raise OSError("git executable not found")
    result = subprocess.run(  # noqa: S603 - executable and arguments are controlled
        [GIT, *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def _matches_prefix(path: str, prefixes: list[str]) -> bool:
    normalized = path.rstrip("/")
    return any(
        normalized == prefix.rstrip("/") or normalized.startswith(prefix.rstrip("/") + "/")
        for prefix in prefixes
    )


def _portable_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def inspect(repo: Path, authorization: Path, base: str) -> dict:
    config = json.loads(authorization.read_text(encoding="utf-8"))
    allowed = set(config.get("allowed_paths") or [])
    authorized_hashes = config.get("authorized_content_sha256") or {}
    forbidden = list(config.get("forbidden_paths") or [])
    merge_base = _git(repo, "merge-base", base, "HEAD").strip()
    committed = set(
        line
        for line in _git(
            repo,
            "diff",
            "--no-renames",
            "--name-only",
            f"{merge_base}...HEAD",
        ).splitlines()
        if line
    )
    working = set(
        line
        for line in _git(
            repo,
            "diff",
            "--no-renames",
            "--name-only",
            "HEAD",
        ).splitlines()
        if line
    )
    untracked = set(
        line
        for line in _git(repo, "ls-files", "--others", "--exclude-standard").splitlines()
        if line
    )
    changed = committed | working | untracked
    protected = sorted(
        path for path in changed if path.startswith(PROTECTED_PREFIXES)
    )
    unauthorized = sorted(path for path in protected if path not in allowed)
    forbidden_changes = sorted(
        path for path in changed if _matches_prefix(path, forbidden)
    )
    missing_review_gate = not bool(config.get("merge_requires_independent_approval"))
    hash_authorization_errors: list[str] = []
    authorization_expired = False
    if protected:
        if not isinstance(authorized_hashes, dict):
            hash_authorization_errors.append("authorized_content_sha256 must be an object")
            authorized_hashes = {}
        missing_hashes = sorted(path for path in allowed if path not in authorized_hashes)
        if missing_hashes:
            hash_authorization_errors.append(
                f"allowed paths missing content authorization: {', '.join(missing_hashes)}"
            )
        for path in protected:
            expected = authorized_hashes.get(path)
            target = repo / path
            if not isinstance(expected, str) or len(expected) != 64:
                hash_authorization_errors.append(
                    f"protected path lacks a valid authorized hash: {path}"
                )
            elif not target.is_file():
                hash_authorization_errors.append(f"authorized protected path is missing: {path}")
            elif _portable_sha256(target) != expected:
                hash_authorization_errors.append(
                    f"protected path content differs from authorization: {path}"
                )
        expiry = config.get("authorization_expires_on")
        try:
            authorization_expired = date.today() > date.fromisoformat(expiry)
        except (TypeError, ValueError):
            hash_authorization_errors.append(
                "authorization_expires_on must be an ISO date"
            )
    failures = []
    if unauthorized:
        failures.append(f"unauthorized protected changes: {', '.join(unauthorized)}")
    if forbidden_changes:
        failures.append(f"forbidden changes: {', '.join(forbidden_changes)}")
    if missing_review_gate:
        failures.append("authorization must require independent approval")
    failures.extend(hash_authorization_errors)
    if authorization_expired:
        failures.append("protected-change authorization has expired")
    return {
        "schema_version": "1.0",
        "base": base,
        "merge_base": merge_base,
        "authorization": authorization.relative_to(repo).as_posix(),
        "protected_changes": protected,
        "unauthorized_changes": unauthorized,
        "forbidden_changes": forbidden_changes,
        "hash_authorization_errors": hash_authorization_errors,
        "authorization_expired": authorization_expired,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main")
    parser.add_argument(
        "--authorization",
        type=Path,
        default=Path("configs/protected-change-authorization-v1.json"),
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    repo = Path(__file__).resolve().parents[1]
    authorization = (
        args.authorization
        if args.authorization.is_absolute()
        else repo / args.authorization
    )
    try:
        result = inspect(repo, authorization, args.base)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"protected_change_status: {result['status']}")
        for path in result["protected_changes"]:
            print(f"  allowed: {path}")
        for failure in result["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
