#!/usr/bin/env python3
"""Fail when a protected VEGO-AI change is outside the reviewed allowlist."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
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
    "scripts/hlayer_offline/",
    "src/vego_hlayer/",
    "tests/hlayer_offline/",
)
GIT = shutil.which("git")
TRUSTED_HASH_ENV = "H_LAYER_AUTHORIZATION_SHA256"
TRUSTED_HASH_GIT_CONFIG = "vego.hlayerAuthorizationSha256"


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


def _git_paths(repo: Path, *args: str) -> set[str]:
    if not GIT:
        raise OSError("git executable not found")
    result = subprocess.run(  # noqa: S603 - executable and arguments are controlled
        [GIT, *args],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    return {
        item.decode("utf-8", errors="surrogateescape")
        for item in result.stdout.split(b"\0")
        if item
    }


def _matches_prefix(path: str, prefixes: list[str]) -> bool:
    normalized = path.rstrip("/")
    return any(
        normalized == prefix.rstrip("/") or normalized.startswith(prefix.rstrip("/") + "/")
        for prefix in prefixes
    )


def _portable_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def _is_link_or_reparse_point(path: Path) -> bool:
    try:
        metadata = os.lstat(path)
    except FileNotFoundError:
        return False
    if stat.S_ISLNK(metadata.st_mode):
        return True
    attributes = getattr(metadata, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(reparse_flag and attributes & reparse_flag)


def _path_contains_link(path: Path) -> bool:
    absolute = path if path.is_absolute() else Path.cwd() / path
    cursor = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        if part in {"", "."}:
            continue
        if part == "..":
            cursor = cursor.parent
            continue
        cursor /= part
        if _is_link_or_reparse_point(cursor):
            return True
    return False


def _git_index_path_is_symlink(repo: Path, path: str) -> bool:
    if not GIT:
        raise OSError("git executable not found")
    result = subprocess.run(  # noqa: S603 - executable and arguments are controlled
        [GIT, "ls-files", "--stage", "--", path],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return any(line.split(maxsplit=1)[0] == "120000" for line in result.stdout.splitlines())


def resolve_comparison_base(repo: Path, requested_base: str | None = None) -> str:
    """Resolve a usable comparison base without requiring an ``origin`` remote.

    An explicit non-default base remains fail-closed. The normal default may
    fall back to CI-provided revisions, a local main branch, or a parent commit
    so source archives and locally initialized repositories remain verifiable.
    """

    default_request = requested_base in {None, "", "origin/main"}
    candidates: list[str | None] = []
    if requested_base:
        candidates.append(requested_base)
    if default_request:
        candidates.extend(
            (
                os.environ.get("PR_BASE_SHA"),
                os.environ.get("H_LAYER_CHANGE_BASE"),
            )
        )
        github_base = os.environ.get("GITHUB_BASE_REF")
        if github_base:
            candidates.extend((f"origin/{github_base}", github_base))
        candidates.extend(("origin/main", "main", "HEAD^", "HEAD"))

    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        result = subprocess.run(  # noqa: S603 - Git ref is an argument, not shell input
            [GIT or "git", "rev-parse", "--verify", f"{candidate}^{{commit}}"],
            cwd=repo,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode == 0:
            return candidate
    if requested_base and not default_request:
        raise ValueError(f"Git comparison base does not resolve: {requested_base}")
    raise ValueError(
        "no usable Git comparison base; set PR_BASE_SHA or H_LAYER_CHANGE_BASE"
    )


def _trusted_authorization_sha256(
    repo: Path,
    explicit: str | None = None,
) -> str | None:
    candidate = explicit or os.environ.get(TRUSTED_HASH_ENV)
    if not candidate and GIT:
        result = subprocess.run(  # noqa: S603 - executable and arguments are controlled
            [GIT, "config", "--local", "--get", TRUSTED_HASH_GIT_CONFIG],
            cwd=repo,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode == 0:
            candidate = result.stdout.strip()
    if not candidate:
        return None
    normalized = candidate.strip().lower()
    if len(normalized) != 64 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError("trusted authorization SHA-256 must be 64 lowercase hex digits")
    return normalized


def inspect(
    repo: Path,
    authorization: Path,
    base: str,
    *,
    trusted_authorization_sha256: str | None = None,
) -> dict:
    base = resolve_comparison_base(repo, base)
    authorization_has_link = _path_contains_link(authorization)
    actual_authorization_sha256 = _portable_sha256(authorization)
    trusted_authorization_sha256 = _trusted_authorization_sha256(
        repo,
        trusted_authorization_sha256,
    )
    authorization_trusted = (
        trusted_authorization_sha256 is not None
        and actual_authorization_sha256 == trusted_authorization_sha256
        and not authorization_has_link
    )
    config = (
        json.loads(authorization.read_text(encoding="utf-8"))
        if authorization_trusted
        else {}
    )
    allowed = set(config.get("allowed_paths") or [])
    authorized_hashes = config.get("authorized_content_sha256") or {}
    forbidden = list(config.get("forbidden_paths") or [])
    merge_base = _git(repo, "merge-base", base, "HEAD").strip()
    committed = _git_paths(
        repo,
        "diff",
        "--no-renames",
        "--name-only",
        "-z",
        f"{merge_base}...HEAD",
    )
    working = _git_paths(
        repo,
        "diff",
        "--no-renames",
        "--name-only",
        "-z",
        "HEAD",
    )
    untracked = _git_paths(
        repo,
        "ls-files",
        "-z",
        "--others",
        "--exclude-standard",
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
            target_has_link = _path_contains_link(target) or _git_index_path_is_symlink(
                repo,
                path,
            )
            if not isinstance(expected, str) or len(expected) != 64:
                hash_authorization_errors.append(
                    f"protected path lacks a valid authorized hash: {path}"
                )
            elif target_has_link:
                hash_authorization_errors.append(
                    f"authorized protected path cannot be a symbolic link "
                    f"or reparse point: {path}"
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
    if authorization_has_link:
        failures.append(
            "authorization record cannot be a symbolic link or reparse point"
        )
    elif trusted_authorization_sha256 is None:
        failures.append(
            "trusted authorization SHA-256 is not configured outside the candidate tree"
        )
    elif not authorization_trusted:
        failures.append(
            "authorization record differs from the trusted authorization SHA-256"
        )
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
        "authorization_sha256": actual_authorization_sha256,
        "trusted_authorization_sha256": trusted_authorization_sha256,
        "authorization_trusted": authorization_trusted,
        "authorization_has_link": authorization_has_link,
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
    parser.add_argument("--base", default=None)
    parser.add_argument(
        "--authorization",
        type=Path,
        default=Path("configs/protected-change-authorization-v1.json"),
    )
    parser.add_argument(
        "--trusted-authorization-sha256",
        default=None,
        help=(
            "Expected portable SHA-256 from an external trust source. Defaults "
            f"to ${TRUSTED_HASH_ENV}, then local Git config "
            f"{TRUSTED_HASH_GIT_CONFIG}."
        ),
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
        result = inspect(
            repo,
            authorization,
            args.base,
            trusted_authorization_sha256=args.trusted_authorization_sha256,
        )
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
