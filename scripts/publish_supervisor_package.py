#!/usr/bin/env python3
"""Copy the July 21 shareable package and write its tracked SHA-256 manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SHARE_DIR = Path(r"C:\Users\ahamed\Claude\Projects\vego-ai\2026-07-21-supervisor-package")
DEFAULT_MANIFEST = ROOT / "docs/research/meetings/2026-07-21-supervisor-package-manifest.json"
JULY15_HTML_SHA256 = "E96E44E6F5C61BF917B82FE0E1CCA8E40C43DCC9ADCF75A248B7C8076D65E811"

PACKAGE_FILES = [
    ("interactive_html", "Interactive bilingual explainer", "VEGO-AI-July1-PointByPoint-EN-HE.html", True),
    (
        "supervisor_deck",
        "Editable 23-slide PowerPoint",
        "presentations/VEGO-AI-Supervisor-Progress-and-Decisions-2026-07-21.pptx",
        True,
    ),
    (
        "deck_pdf",
        "Rendered 23-page deck PDF",
        "output/pdf/VEGO-AI-Supervisor-Progress-and-Decisions-2026-07-21.pdf",
        True,
    ),
    (
        "preread_pdf",
        "Two-page pre-read and decision worksheet",
        "output/pdf/VEGO-AI-Supervisor-PreRead-and-Decision-Worksheet-2026-07-21.pdf",
        True,
    ),
    (
        "package_index",
        "Package index",
        "docs/research/meetings/2026-07-21-supervisor-package.md",
        True,
    ),
    (
        "record_provenance",
        "July 1 record and provenance",
        "docs/research/meetings/2026-07-21-supervisor-record-and-provenance.md",
        True,
    ),
    (
        "decision_register",
        "Decision register",
        "docs/research/meetings/2026-07-21-supervisor-decision-register.md",
        True,
    ),
    (
        "action_register",
        "Action register",
        "docs/research/meetings/2026-07-21-supervisor-action-register.md",
        True,
    ),
    (
        "followup_annex",
        "Dated post-July 1 working annex",
        "docs/research/meetings/2026-07-21-supervisor-follow-up-annex.md",
        True,
    ),
    (
        "preread_markdown",
        "Executive pre-read source",
        "docs/research/meetings/2026-07-21-supervisor-executive-pre-read.md",
        True,
    ),
    (
        "presenter_guide",
        "Presenter guide",
        "docs/research/meetings/2026-07-21-supervisor-presenter-guide.md",
        True,
    ),
    (
        "post_meeting_template",
        "Post-meeting capture template",
        "docs/research/meetings/2026-07-21-post-meeting-capture-template.md",
        True,
    ),
    (
        "package_data",
        "AI-readable SupervisorPackageData v3",
        "docs/research/meetings/2026-07-21-supervisor-package-data-v3.json",
        True,
    ),
    (
        "program_status",
        "ProgramStatusSnapshot v1",
        "docs/research/h-layer/program-status-snapshot-v1.json",
        True,
    ),
    (
        "deck_build_report",
        "Deck construction and boundary report",
        "presentations/VEGO-AI-Supervisor-Progress-and-Decisions-2026-07-21.build.json",
        True,
    ),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def is_tracked(relative: str) -> bool:
    return (
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", relative],
            cwd=ROOT,
            capture_output=True,
        ).returncode
        == 0
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--share-dir", type=Path, default=DEFAULT_SHARE_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    share_dir = args.share_dir.resolve()
    manifest_path = args.manifest.resolve()
    share_dir.mkdir(parents=True, exist_ok=True)

    missing = [relative for _, _, relative, _ in PACKAGE_FILES if not (ROOT / relative).is_file()]
    if missing:
        raise SystemExit(f"Missing package files: {', '.join(missing)}")

    records = []
    for file_id, role, relative, copy_shareable in PACKAGE_FILES:
        source = (ROOT / relative).resolve()
        record = {
            "id": file_id,
            "role": role,
            "sourcePath": relative.replace("\\", "/"),
            "sourceAbsolutePath": str(source),
            "tracked": is_tracked(relative.replace("\\", "/")),
            "bytes": source.stat().st_size,
            "sha256": sha256(source),
        }
        if copy_shareable:
            destination = share_dir / source.name
            shutil.copy2(source, destination)
            copied_hash = sha256(destination)
            if copied_hash != record["sha256"]:
                raise SystemExit(f"Hash mismatch after copy: {source} -> {destination}")
            record["sharePath"] = str(destination)
            record["shareSha256"] = copied_hash
        records.append(record)

    status = json.loads((ROOT / "docs/research/h-layer/program-status-snapshot-v1.json").read_text(encoding="utf-8"))
    manifest = {
        "schemaVersion": "SupervisorPackageManifest-v1",
        "packageDate": "2026-07-21",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "meeting": {
            "audience": ["Iris", "Arnon"],
            "presentationMinutes": 20,
            "discussionMinutes": 20,
        },
        "repository": {
            "branch": git("branch", "--show-current"),
            "sourceRevision": git("rev-parse", "HEAD"),
            "dirtyPathsBeforeManifest": git("status", "--porcelain").splitlines(),
        },
        "acceptedEvidence": {
            "iteration": status["latestAcceptedIteration"]["iteration"],
            "runId": status["latestAcceptedIteration"]["runId"],
            "verdict": status["latestAcceptedIteration"]["verdict"],
            "iterationKind": status["latestAcceptedIteration"]["iterationKind"],
            "normalizedSha256": status["latestAcceptedIteration"]["normalizedSha256"],
            "exp005Candidates": status["exp005Gate"]["candidateRows"],
            "exp005SuppliedLabels": status["exp005Gate"]["suppliedLabels"],
            "exp012Result": status["exp012Gate"]["result"],
            "decisionConfirmationStatus": status["decisionState"]["confirmationStatus"],
            "runtimeAuthorization": status["decisionState"]["runtimeAuthorization"],
        },
        "verification": status["verificationRecord"],
        "historicalRecord": {
            "july15MaterialsPreserved": True,
            "externalJuly15HtmlSha256": JULY15_HTML_SHA256,
        },
        "privacyBoundary": {
            "rawAudioIncluded": False,
            "fullAsrIncluded": False,
            "expertLabelsIncluded": False,
            "localConfigurationIncluded": False,
        },
        "outputLocations": {
            "sourceRepository": str(ROOT),
            "shareDirectory": str(share_dir),
        },
        "files": records,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest_copy = share_dir / manifest_path.name
    shutil.copy2(manifest_path, manifest_copy)
    print(
        json.dumps(
            {
                "manifest": str(manifest_path),
                "manifestSha256": sha256(manifest_path),
                "shareDirectory": str(share_dir),
                "fileCount": len(records) + 1,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
