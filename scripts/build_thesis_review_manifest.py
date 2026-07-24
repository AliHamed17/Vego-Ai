#!/usr/bin/env python3
"""Build or validate the portable thesis review package manifest.

The tracked manifest contains repository-relative paths and logical delivery
identifiers only. Personal paths and share-copy locations are written to an
ignored local-delivery record.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_DATE = "2026-07-24"
MANIFEST = ROOT / "docs/research/thesis-evidence/THESIS_REVIEW_PACKAGE_MANIFEST.json"
LOCAL_DELIVERY = (
    ROOT / "reports/generated/thesis_review/local-delivery-manifest.json"
)
SNAPSHOT = ROOT / "docs/research/thesis-evidence/thesis-evidence-snapshot-v1.json"
HTML = ROOT / "VEGO-AI-Thesis-Baseline-Progress.html"
SCHEMA = ROOT / "schemas/thesis-review-package-manifest-v1.schema.json"
WINDOWS_ABSOLUTE = re.compile(r"(?i)\b[a-z]:[\\/]")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str, binary: bool = False) -> str | bytes:
    result = subprocess.check_output(["git", *args], cwd=ROOT)
    return result if binary else result.decode("utf-8").strip()


def is_ancestor(revision: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", revision, "HEAD"],
            cwd=ROOT,
            capture_output=True,
        ).returncode
        == 0
    )


def generated_at(refresh: bool) -> str:
    if MANIFEST.exists() and not refresh:
        existing = json.loads(MANIFEST.read_text(encoding="utf-8"))
        value = existing.get("generatedAt")
        if value:
            return value
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def relative_artifact(path: Path, tracked: bool = True) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "tracked": tracked,
    }


def package_paths(
    package_date: str, output_dir: Path
) -> tuple[Path, Path]:
    stem = f"VEGO-AI-MSc-Thesis-Evidence-Ready-Draft-{package_date}"
    return output_dir / f"{stem}.docx", ROOT / "output/pdf" / f"{stem}.pdf"


def load_qa(qa_report: Path | None) -> tuple[dict[str, Any], str | None]:
    if qa_report is None or not qa_report.is_file():
        return {}, None
    payload = json.loads(qa_report.read_text(encoding="utf-8"))
    return payload, sha256(qa_report)


def tracked_manifest(
    *,
    package_date: str,
    output_dir: Path,
    source_revision: str,
    package_revision: str,
    qa_report: Path | None,
    refresh_timestamp: bool,
) -> dict[str, Any]:
    docx, pdf = package_paths(package_date, output_dir)
    required = [docx, HTML, SNAPSHOT, SCHEMA]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"missing required package files: {', '.join(missing)}")

    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if snapshot.get("sourceRevision") != source_revision:
        raise SystemExit(
            "source revision differs from the canonical evidence snapshot"
        )
    for name, revision in (
        ("sourceRevision", source_revision),
        ("packageRevision", package_revision),
    ):
        if not is_ancestor(revision):
            raise SystemExit(f"{name} is not an ancestor of HEAD: {revision}")

    qa, qa_hash = load_qa(qa_report)
    pdf_metadata: dict[str, Any] = {
        "logicalDeliveryId": "thesis-review-pdf-local",
        "filename": pdf.name,
        "tracked": False,
        "availableInClone": False,
        "sha256": None,
        "bytes": None,
    }
    render_metadata: dict[str, Any] = {
        "status": "NOT_RECORDED",
        "pdfPageCount": None,
        "renderedPageCount": None,
        "sheetCount": None,
        "qaReportSha256": None,
    }
    if pdf.is_file():
        pdf_metadata.update({"sha256": sha256(pdf), "bytes": pdf.stat().st_size})
        render_metadata["pdfPageCount"] = len(PdfReader(pdf).pages)
    if qa:
        render_metadata.update(
            {
                "status": qa.get("status", "NOT_RECORDED"),
                "renderedPageCount": qa.get("pageCount"),
                "sheetCount": qa.get("sheetCount"),
                "qaReportSha256": qa_hash,
            }
        )

    sources = [
        {"path": path, "sha256": digest}
        for path, digest in sorted(snapshot["sourceHashes"].items())
    ]
    payload = {
        "schemaVersion": "ThesisReviewPackageManifest-v1",
        "generatedAt": generated_at(refresh_timestamp),
        "packageDate": package_date,
        "sourceRevision": source_revision,
        "packageRevision": package_revision,
        "sourceTreeHash": snapshot["sourceTreeHash"],
        "canonicalSourcesDirtyAtGeneration": snapshot[
            "canonicalSourcesDirty"
        ],
        "claimBoundary": (
            "Mechanism, traceability, governance, and evaluation readiness only. "
            "At 0/24 supplied independent labels, empirical performance metrics "
            "remain null; accuracy improvement, generalization, reduced human "
            "effort, and benchmark superiority are not established."
        ),
        "evidenceSnapshot": relative_artifact(SNAPSHOT),
        "trackedOutputs": {
            "docx": relative_artifact(docx),
            "interactiveHtml": relative_artifact(HTML),
        },
        "localArtifacts": {
            "pdf": pdf_metadata,
            "renderVerification": render_metadata,
        },
        "sourceFiles": sources,
        "toolVersions": {
            "python": sys.version.split()[0],
            "jsonschema": importlib.metadata.version("jsonschema"),
        },
        "protectedRuntimeChanged": False,
        "expertLabelsCreatedOrModified": False,
        "runtimeFeatureCodeImplemented": False,
        "researchInfrastructureImplemented": True,
    }
    jsonschema.Draft202012Validator(
        json.loads(SCHEMA.read_text(encoding="utf-8")),
        format_checker=jsonschema.FormatChecker(),
    ).validate(payload)
    return payload


def local_delivery_record(
    *,
    tracked: dict[str, Any],
    package_date: str,
    output_dir: Path,
    qa_report: Path | None,
    share_dir: Path | None,
) -> dict[str, Any]:
    docx, pdf = package_paths(package_date, output_dir)
    primary = {"docx": docx, "pdf": pdf, "html": HTML}
    shares: dict[str, Any] = {}
    if share_dir is not None:
        for key, source in primary.items():
            target = share_dir / source.name
            shares[key] = {
                "path": str(target.resolve()),
                "exists": target.is_file(),
                "sha256": sha256(target) if target.is_file() else None,
                "byteIdenticalToPrimary": (
                    target.is_file()
                    and source.is_file()
                    and sha256(target) == sha256(source)
                ),
            }
    return {
        "schemaVersion": "ThesisLocalDeliveryRecord-v1",
        "generatedAt": tracked["generatedAt"],
        "trackedManifestPath": str(MANIFEST.resolve()),
        "trackedManifestSha256": None,
        "primaryPaths": {
            key: str(path.resolve()) for key, path in primary.items()
        },
        "qaReportPath": str(qa_report.resolve()) if qa_report else None,
        "shareableCopies": shares,
    }


def validate_manifest() -> list[str]:
    errors: list[str] = []
    if not MANIFEST.is_file():
        return [f"manifest is missing: {MANIFEST.relative_to(ROOT)}"]
    try:
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        ).validate(payload)
    except (OSError, json.JSONDecodeError, jsonschema.ValidationError) as exc:
        return [f"manifest/schema validation failed: {exc}"]

    if WINDOWS_ABSOLUTE.search(MANIFEST.read_text(encoding="utf-8")):
        errors.append("tracked manifest contains a personal absolute Windows path")
    for name in ("sourceRevision", "packageRevision"):
        if not is_ancestor(payload[name]):
            errors.append(f"{name} is not an ancestor of HEAD")
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if payload["sourceRevision"] != snapshot.get("sourceRevision"):
        errors.append("manifest sourceRevision differs from snapshot")
    if payload["sourceTreeHash"] != snapshot.get("sourceTreeHash"):
        errors.append("manifest sourceTreeHash differs from snapshot")

    artifact_items = [
        payload["evidenceSnapshot"],
        *payload["trackedOutputs"].values(),
        *payload["sourceFiles"],
    ]
    for item in artifact_items:
        path = ROOT / item["path"]
        if not path.is_file():
            errors.append(f"tracked path is missing: {item['path']}")
        elif sha256(path) != item["sha256"]:
            errors.append(f"tracked path hash drift: {item['path']}")

    for item in payload["sourceFiles"]:
        try:
            source_bytes = git(
                "show",
                f"{payload['sourceRevision']}:{item['path']}",
                binary=True,
            )
        except subprocess.CalledProcessError:
            errors.append(
                f"source file missing from sourceRevision: {item['path']}"
            )
            continue
        if sha256_bytes(source_bytes) != item["sha256"]:
            errors.append(
                f"sourceRevision does not contain recorded hash: {item['path']}"
            )

    for item in payload["trackedOutputs"].values():
        try:
            package_bytes = git(
                "show",
                f"{payload['packageRevision']}:{item['path']}",
                binary=True,
            )
        except subprocess.CalledProcessError:
            errors.append(
                f"tracked output missing from packageRevision: {item['path']}"
            )
            continue
        if sha256_bytes(package_bytes) != item["sha256"]:
            errors.append(
                f"packageRevision does not contain recorded hash: {item['path']}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--package-date", default=DEFAULT_PACKAGE_DATE)
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "thesis/output"
    )
    parser.add_argument("--source-revision")
    parser.add_argument("--package-revision")
    parser.add_argument("--qa-report", type=Path)
    parser.add_argument("--share-dir", type=Path)
    parser.add_argument("--refresh-timestamp", action="store_true")
    args = parser.parse_args()

    if args.check:
        errors = validate_manifest()
        if errors:
            print("thesis review package manifest: FAIL")
            for error in errors:
                print(f"- {error}")
            return 1
        print("thesis review package manifest: PASS")
        return 0

    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    source_revision = args.source_revision or snapshot["sourceRevision"]
    package_revision = args.package_revision or str(git("rev-parse", "HEAD"))
    payload = tracked_manifest(
        package_date=args.package_date,
        output_dir=args.output_dir.resolve(),
        source_revision=source_revision,
        package_revision=package_revision,
        qa_report=args.qa_report.resolve() if args.qa_report else None,
        refresh_timestamp=args.refresh_timestamp,
    )
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    MANIFEST.write_text(rendered, encoding="utf-8", newline="\n")

    local_payload = local_delivery_record(
        tracked=payload,
        package_date=args.package_date,
        output_dir=args.output_dir.resolve(),
        qa_report=args.qa_report.resolve() if args.qa_report else None,
        share_dir=args.share_dir.resolve() if args.share_dir else None,
    )
    local_payload["trackedManifestSha256"] = sha256(MANIFEST)
    LOCAL_DELIVERY.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_DELIVERY.write_text(
        json.dumps(local_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(MANIFEST)
    print(LOCAL_DELIVERY)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
