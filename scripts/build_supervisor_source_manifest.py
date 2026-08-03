#!/usr/bin/env python3
"""Build a detached, hash-bound manifest from supervisor-deck source notes.

The manifest is deterministic and binds the current PPTX plus every unique
repository file or directory referenced after a ``[Sources]`` marker. It does
not establish source truth, human review, presentation approval, or delivery.

Examples:
    python scripts/build_supervisor_source_manifest.py
    python scripts/build_supervisor_source_manifest.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PPTX = (
    ROOT / "presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pptx"
)
DEFAULT_OUTPUT = (
    ROOT
    / "docs/research/meetings/2026-08-05-supervisor-source-manifest.json"
)
SCHEMA_VERSION = "IrisSupervisorSourceManifest-v1"
SOURCE_MARKER = "[Sources]"
ANNOTATION = re.compile(r"\s+\([^)]*\)\s*$")


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def valid_sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9A-F]{64}", value) is not None


def note_texts(path: Path) -> list[str]:
    if not path.is_file():
        raise ValueError(f"PPTX does not exist: {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            names = [
                name
                for name in archive.namelist()
                if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", name)
            ]
            names.sort(key=lambda name: int(re.search(r"\d+", Path(name).stem).group()))
            texts: list[str] = []
            for name in names:
                root = ElementTree.fromstring(archive.read(name))
                texts.append(
                    "\n".join(
                        node.text or ""
                        for node in root.iter()
                        if node.tag.endswith("}t")
                    )
                )
    except (OSError, zipfile.BadZipFile, ElementTree.ParseError) as error:
        raise ValueError(f"cannot inspect PPTX notes: {error}") from error
    return texts


def source_lines(note: str, slide_number: int) -> list[tuple[str, int]]:
    lines = note.splitlines()
    try:
        marker_index = lines.index(SOURCE_MARKER)
    except ValueError as error:
        raise ValueError(f"slide {slide_number} has no {SOURCE_MARKER} marker") from error
    sources = [
        (line[2:].strip(), slide_number)
        for line in lines[marker_index + 1 :]
        if line.startswith("- ") and line[2:].strip()
    ]
    if not sources:
        raise ValueError(f"slide {slide_number} has an empty source block")
    return sources


def normalize_reference(value: str) -> tuple[str, str]:
    path_text, separator, fragment = value.strip().partition("#")
    path_text = ANNOTATION.sub("", path_text)
    fragment = ANNOTATION.sub("", fragment)
    normalized = PurePosixPath(path_text.rstrip("/")).as_posix()
    if (
        not normalized
        or normalized.startswith("/")
        or re.match(r"^[A-Za-z]:", normalized)
        or ".." in PurePosixPath(normalized).parts
    ):
        raise ValueError(f"unsafe or empty source reference: {value!r}")
    return normalized, fragment if separator else ""


def directory_members(path: Path) -> list[dict[str, object]]:
    members = []
    for member in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
        members.append(
            {
                "path": relative(member),
                "bytes": member.stat().st_size,
                "sha256": sha256(member),
            }
        )
    if not members:
        raise ValueError(f"referenced directory has no files: {relative(path)}")
    return members


def build_payload(pptx: Path = DEFAULT_PPTX) -> dict[str, object]:
    notes = note_texts(pptx)
    references: dict[str, dict[str, set[object]]] = defaultdict(
        lambda: {"slides": set(), "fragments": set(), "raw_references": set()}
    )
    for slide_number, note in enumerate(notes, start=1):
        for raw, slide in source_lines(note, slide_number):
            path_text, fragment = normalize_reference(raw)
            references[path_text]["slides"].add(slide)
            if fragment:
                references[path_text]["fragments"].add(fragment)
            references[path_text]["raw_references"].add(raw)

    entries: list[dict[str, object]] = []
    for path_text in sorted(references):
        path = (ROOT / PurePosixPath(path_text)).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError as error:
            raise ValueError(f"source resolves outside repository: {path_text}") from error
        if not path.exists():
            raise ValueError(f"source does not exist: {path_text}")
        usage = references[path_text]
        common: dict[str, object] = {
            "path": path_text,
            "slides": sorted(usage["slides"]),
            "fragments": sorted(usage["fragments"]),
            "raw_references": sorted(usage["raw_references"]),
        }
        if path.is_file():
            entries.append(
                {
                    **common,
                    "kind": "file",
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
            continue
        if not path.is_dir():
            raise ValueError(f"source is neither a file nor directory: {path_text}")
        members = directory_members(path)
        canonical_members = json.dumps(
            members, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        entries.append(
            {
                **common,
                "kind": "directory",
                "member_count": len(members),
                "aggregate_sha256": sha256_text(canonical_members),
                "members": members,
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "HASH_BOUND_LOCAL_CANDIDATE",
        "generated_by": relative(Path(__file__).resolve()),
        "evidence_boundary": (
            "Hashes bind the current local PPTX source notes to exact repository "
            "bytes. They do not establish source truth, review, approval, delivery, "
            "recipient access, or supervisor acceptance."
        ),
        "presentation": {
            "path": relative(pptx),
            "bytes": pptx.stat().st_size,
            "sha256": sha256(pptx),
            "slide_count": len(notes),
            "source_note_sections": len(notes),
        },
        "unique_source_path_count": len(entries),
        "sources": entries,
    }


def render(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--pptx", type=Path, default=DEFAULT_PPTX)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        expected = render(build_payload(args.pptx.resolve()))
    except (OSError, ValueError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1
    output = args.output.resolve()
    if args.check:
        matches = output.is_file() and output.read_text(encoding="utf-8") == expected
        print(f"{'verified' if matches else 'STALE_OR_MISSING'}: {output}")
        return 0 if matches else 1
    output.write_text(expected, encoding="utf-8", newline="")
    payload = json.loads(expected)
    print(
        f"wrote: {output} ({payload['unique_source_path_count']} unique source paths)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
