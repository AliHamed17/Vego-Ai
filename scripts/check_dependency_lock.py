#!/usr/bin/env python3
"""Check or refresh legacy requirement projections from canonical pyproject pins."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 compatibility
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
PROJECTIONS = {
    "project": ROOT / "VEGO-AI" / "framework" / "requirements.txt",
    "dev": ROOT / "requirements-dev.txt",
    "thesis": ROOT / "requirements-thesis.txt",
}


def expected() -> dict[Path, str]:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    groups = {
        "project": list(data["project"]["dependencies"]),
        **data.get("dependency-groups", {}),
    }
    outputs: dict[Path, str] = {}
    for name, path in PROJECTIONS.items():
        requirements = groups[name]
        if not all("==" in requirement for requirement in requirements):
            raise ValueError(f"{name} contains an unpinned direct dependency")
        outputs[path] = "\n".join(sorted(requirements, key=str.casefold)) + "\n"
    return outputs


def validate_node_lock() -> None:
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
    declared = package.get("devDependencies") or {}
    locked = lock.get("packages", {}).get("", {}).get("devDependencies") or {}
    if declared != locked:
        raise ValueError("package-lock root dependencies differ from package.json")
    for name, version in declared.items():
        record = (lock.get("packages") or {}).get(f"node_modules/{name}") or {}
        if record.get("version") != version:
            raise ValueError(f"Node dependency is not locked exactly: {name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--refresh", action="store_true")
    args = parser.parse_args(argv)
    try:
        projections = expected()
        validate_node_lock()
    except (OSError, KeyError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"dependency lock projection: FAIL: {exc}", file=sys.stderr)
        return 2
    stale: list[str] = []
    for path, content in projections.items():
        if path.is_file() and path.read_text(encoding="utf-8") == content:
            continue
        if args.refresh:
            path.write_text(content, encoding="utf-8", newline="\n")
            print(f"WROTE: {path.relative_to(ROOT).as_posix()}")
        else:
            stale.append(path.relative_to(ROOT).as_posix())
    if stale:
        print(
            f"dependency lock projection: STALE: {', '.join(stale)}",
            file=sys.stderr,
        )
        return 1
    print("dependency lock projection: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
