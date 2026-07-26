#!/usr/bin/env python3
"""Build and verify an immutable, read-only BigUI deployment package."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "deploy" / "ai-studio"
BIGUI = ROOT / "docs" / "research" / "bigui"
DEFAULT_OUTPUT = ROOT / "reports" / "generated" / "ai-studio-deployment"
DEPLOYMENT_SCHEMA = ROOT / "schemas" / "deployment-snapshot-v1.schema.json"

INPUTS = {
    "public/index.html": ROOT / "VEGO-AI-Research-Hub.html",
    "data/catalog.json": BIGUI / "experiment-catalog-snapshot-v1.json",
    "data/result-views.json": BIGUI / "experiment-result-views-v1.json",
    "data/paper-baseline.json": BIGUI / "paper-baseline-snapshot-v1.json",
    "data/deployment.json": BIGUI / "deployment-snapshot-v1.json",
    "public/archive/workspace-v1/index.html": (
        SOURCE / "archive" / "workspace-v1.html"
    ),
    "server.js": SOURCE / "server.js",
    "package.json": SOURCE / "package.json",
    "package-lock.json": SOURCE / "package-lock.json",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path.relative_to(ROOT)}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_default_output(output: Path) -> Path:
    target = output.resolve()
    allowed = (ROOT / "reports" / "generated").resolve()
    try:
        target.relative_to(allowed)
    except ValueError as exc:
        raise ValueError(
            "deployment output must remain under reports/generated"
        ) from exc
    if target == allowed:
        raise ValueError("deployment output cannot be the generated-output root")
    return target


def canonical_package_hash(root: Path) -> str:
    digest = hashlib.sha256()
    excluded = {"data/deployment.json", "package-manifest.json"}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative in excluded:
            continue
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256(path)))
    return digest.hexdigest()


def validate_revision(value: str | None) -> str | None:
    if value is None:
        return None
    if len(value) != 40 or any(char not in "0123456789abcdef" for char in value):
        raise ValueError("--main-revision must be a lowercase 40-character SHA")
    return value


def materialize(
    output: Path,
    main_revision: str | None,
    deployed_at: str | None,
) -> dict[str, Any]:
    for source in INPUTS.values():
        if not source.is_file():
            raise ValueError(f"missing deployment input: {source.relative_to(ROOT)}")
        if source.is_symlink():
            raise ValueError(f"symlinked deployment input rejected: {source}")
    for relative, source in INPUTS.items():
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    deployment_path = output / "data" / "deployment.json"
    deployment = load_json(deployment_path)
    deployment["mainBranchRevision"] = main_revision
    deployment["deployedAt"] = deployed_at
    deployment["publicationState"] = (
        "deployed" if main_revision and deployed_at else "candidate"
    )
    package_hash = canonical_package_hash(output)
    deployment["deploymentPackageSha256"] = package_hash
    deployment_path.write_text(
        json.dumps(deployment, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    jsonschema.Draft202012Validator(
        load_json(DEPLOYMENT_SCHEMA),
        format_checker=jsonschema.FormatChecker(),
    ).validate(deployment)

    files = [
        {
            "path": path.relative_to(output).as_posix(),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        }
        for path in sorted(item for item in output.rglob("*") if item.is_file())
    ]
    manifest = {
        "schemaVersion": "AIStudioDeploymentPackageManifest-v1",
        "generatedAt": deployment["generatedAt"],
        "mainBranchRevision": main_revision,
        "deploymentPackageSha256": package_hash,
        "catalogSha256": deployment["catalogSha256"],
        "resultViewsSha256": deployment["resultViewsSha256"],
        "experimentCount": deployment["experimentCount"],
        "currentAcceptedRunCount": deployment["currentAcceptedRunCount"],
        "historicalAcceptedRunCount": deployment["historicalAcceptedRunCount"],
        "metricObservationCount": deployment["metricObservationCount"],
        "files": files,
        "claimBoundary": deployment["claimBoundary"],
    }
    (output / "package-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def validate_package(output: Path, manifest: dict[str, Any]) -> None:
    catalog = load_json(output / "data" / "catalog.json")
    results = load_json(output / "data" / "result-views.json")
    deployment = load_json(output / "data" / "deployment.json")
    if len(catalog["experiments"]) != 41:
        raise ValueError("deployment catalog must contain 41 experiments")
    if len(results["resultViews"]) != 41:
        raise ValueError("deployment result view must contain 41 experiments")
    if deployment["catalogSha256"] != sha256(output / "data" / "catalog.json"):
        raise ValueError("deployment catalog hash mismatch")
    if deployment["resultViewsSha256"] != sha256(
        output / "data" / "result-views.json"
    ):
        raise ValueError("deployment result-view hash mismatch")
    if canonical_package_hash(output) != manifest["deploymentPackageSha256"]:
        raise ValueError("deployment package hash mismatch")
    required = {
        "public/index.html",
        "data/catalog.json",
        "data/result-views.json",
        "data/paper-baseline.json",
        "data/deployment.json",
        "public/archive/workspace-v1/index.html",
        "server.js",
        "package.json",
        "package-lock.json",
    }
    present = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
    }
    if not required.issubset(present):
        raise ValueError(f"deployment package missing: {sorted(required - present)}")
    html = (output / "public" / "index.html").read_text(encoding="utf-8")
    if "ExperimentCatalogSnapshot-v1" not in html or "EXP-040" not in html:
        raise ValueError("deployment landing is not the canonical BigUI")
    forbidden = ("api_key", "sk-proj-", "reviewer_identity", "raw_transcript")
    lower = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore").lower()
        for path in output.rglob("*")
        if path.is_file()
    )
    for term in forbidden:
        if term in lower:
            raise ValueError(f"forbidden deployment content: {term}")


def build_candidate(
    output: Path,
    main_revision: str | None,
    deployed_at: str | None,
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=False)
    manifest = materialize(output, main_revision, deployed_at)
    validate_package(output, manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--refresh", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--main-revision")
    parser.add_argument("--deployed-at")
    args = parser.parse_args()
    try:
        revision = validate_revision(args.main_revision)
        if bool(revision) != bool(args.deployed_at):
            raise ValueError(
                "--main-revision and --deployed-at must be supplied together"
            )
        if args.check:
            with tempfile.TemporaryDirectory(prefix="vego-ai-deploy-check-") as raw:
                output = Path(raw) / "package"
                manifest = build_candidate(
                    output, revision, args.deployed_at
                )
        else:
            target = safe_default_output(
                args.output if args.output.is_absolute() else ROOT / args.output
            )
            with tempfile.TemporaryDirectory(
                prefix="vego-ai-deploy-build-",
                dir=target.parent if target.parent.exists() else None,
            ) as raw:
                temporary = Path(raw) / "package"
                manifest = build_candidate(
                    temporary, revision, args.deployed_at
                )
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(temporary, target)
        print(
            "AI Studio package: PASS "
            f"({manifest['experimentCount']} experiments; "
            f"{manifest['currentAcceptedRunCount']} current runs; "
            f"{manifest['historicalAcceptedRunCount']} historical bundles; "
            f"{manifest['deploymentPackageSha256'][:12]}...)"
        )
        return 0
    except Exception as exc:
        print(f"AI Studio package: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
