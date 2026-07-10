#!/usr/bin/env python3
"""Read-only integrity and content validation for the supervisor decision package."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree


REQUIRED_FILES = {
    "record": "docs/research/meetings/2026-07-01-supervisor-meeting-iris.md",
    "evidence": "docs/research/meetings/2026-07-01-supervisor-evidence-appendix.md",
    "provenance": "docs/research/meetings/2026-07-01-supervisor-provenance-manifest.md",
    "decisions": "docs/research/meetings/2026-07-15-supervisor-decision-register.md",
    "actions": "docs/research/meetings/2026-07-15-supervisor-action-register.md",
    "annex": "docs/research/meetings/2026-07-15-supervisor-follow-up-annex.md",
    "pre_read": "docs/research/meetings/2026-07-15-supervisor-executive-pre-read.md",
    "capture": "docs/research/meetings/2026-07-15-post-meeting-capture-template.md",
    "package_index": "docs/research/meetings/2026-07-15-meeting-package.md",
    "output_manifest": "docs/research/meetings/2026-07-15-decision-package-manifest.md",
    "redirect": "docs/research/extension-plan-2026-07-supervisor-redirect.md",
}

CANONICAL_HASHES = {
    "docs/video1832857678.mp4": "23b16a5cc3c1a90402dd038f6b30dd85fd9e3df23e9deaa151eede3a94e8ab31",
    "docs/video1832857678.transcript.he.txt": "5b01a08ae3a6209bb594d9fa0c74a91f970886b2054ae1820e87652ddc13f087",
    "docs/video1832857678.transcript.he.md": "b34b0b0f28567449e443702377df61c2cae63f036cf2eef21784b0bf99a34b3c",
    "docs/video1832857678.transcript.he.srt": "bac968598b7b1d7efef3d512776e4aed7d360674c316b12ba984c17b3666428e",
}

DECISION_FIELDS = (
    "ID",
    "July 1 basis",
    "timestamp",
    "attribution confidence",
    "post-meeting evidence",
    "recommendation",
    "alternatives",
    "exact decision requested",
    "outcome",
    "rationale",
    "approver",
    "owner",
    "due date",
    "affected artifacts",
    "confirmation status",
)

ACTION_FIELDS = (
    "ID",
    "Origin",
    "Owner",
    "Due date",
    "Status",
    "Dependency",
    "Evidence link",
    "Next checkpoint",
)

EXPECTED_DECISIONS = [f"M-{number:02d}" for number in range(1, 7)]
EXPECTED_DIRECTIVES = [f"D{number}" for number in range(1, 13)]
EXPECTED_JULY1_ACTIONS = [f"J1-A{number:02d}" for number in range(1, 7)]


def read_text(path: Path, failures: list[str]) -> str:
    if not path.is_file():
        failures.append(f"missing required file: {path}")
        return ""
    return path.read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(text: str, needle: str, label: str, failures: list[str]) -> None:
    if needle.casefold() not in text.casefold():
        failures.append(f"{label}: missing required text {needle!r}")


def table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def section_map(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^##\s+(M-0[1-6])\s+-.*$", text, re.MULTILINE))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1)] = text[match.start() : end]
    return sections


def decision_field(section: str, field: str) -> str:
    match = re.search(
        rf"^\|\s*{re.escape(field)}\s*\|\s*(.*?)\s*\|\s*$",
        section,
        re.MULTILINE | re.IGNORECASE,
    )
    return match.group(1).strip() if match else ""


def pptx_slide_texts(path: Path, failures: list[str]) -> list[str]:
    if not path.is_file():
        return []
    texts: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            slide_names = sorted(
                (
                    name
                    for name in archive.namelist()
                    if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
                ),
                key=lambda name: int(re.search(r"(\d+)", Path(name).stem).group(1)),
            )
            for name in slide_names:
                root = ElementTree.fromstring(archive.read(name))
                parts = [
                    element.text or ""
                    for element in root.iter()
                    if element.tag.endswith("}t")
                ]
                texts.append("\n".join(parts))
    except (OSError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        failures.append(f"cannot inspect PPTX {path}: {exc}")
    return texts


def pptx_note_texts(path: Path, failures: list[str]) -> list[str]:
    if not path.is_file():
        return []
    texts: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            note_names = sorted(
                (
                    name
                    for name in archive.namelist()
                    if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", name)
                ),
                key=lambda name: int(re.search(r"(\d+)", Path(name).stem).group(1)),
            )
            for name in note_names:
                root = ElementTree.fromstring(archive.read(name))
                parts = [
                    element.text or ""
                    for element in root.iter()
                    if element.tag.endswith("}t")
                ]
                texts.append("\n".join(parts))
    except (OSError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        failures.append(f"cannot inspect PPTX notes {path}: {exc}")
    return texts


def pdf_page_count(path: Path) -> int:
    return len(re.findall(rb"/Type\s*/Page\b", path.read_bytes()))


def validate_artifacts(
    root: Path, manifest: str, failures: list[str]
) -> tuple[list[str], list[str]]:
    share = root.parent / "Claude" / "Projects" / "vego-ai"
    artifacts = {
        "primary PPTX": root
        / "artifacts/supervisor_meeting_2026-07-15/VEGO-AI-Supervisor-Decision-Package-2026-07-15.pptx",
        "primary deck PDF": root
        / "output/pdf/VEGO-AI-Supervisor-Decision-Package-2026-07-15.pdf",
        "primary pre-read PDF": root
        / "output/pdf/VEGO-AI-Supervisor-PreRead-and-Decision-Worksheet-2026-07-15.pdf",
        "shareable PPTX": share / "VEGO-AI-Supervisor-Decision-Package-2026-07-15.pptx",
        "shareable deck PDF": share / "VEGO-AI-Supervisor-Decision-Package-2026-07-15.pdf",
        "shareable pre-read PDF": share
        / "VEGO-AI-Supervisor-PreRead-and-Decision-Worksheet-2026-07-15.pdf",
    }
    hashes: dict[str, str] = {}
    for label, path in artifacts.items():
        if not path.is_file():
            failures.append(f"missing generated artifact: {label}: {path}")
            continue
        digest = sha256(path)
        hashes[label] = digest
        if digest.casefold() not in manifest.casefold():
            failures.append(f"output manifest does not contain {label} hash {digest}")
        if str(path).casefold() not in manifest.casefold():
            failures.append(f"output manifest does not contain {label} path {path}")

    for primary, copy in (
        ("primary PPTX", "shareable PPTX"),
        ("primary deck PDF", "shareable deck PDF"),
        ("primary pre-read PDF", "shareable pre-read PDF"),
    ):
        if primary in hashes and copy in hashes and hashes[primary] != hashes[copy]:
            failures.append(f"artifact copy mismatch: {primary} != {copy}")

    deck_pdf = artifacts["primary deck PDF"]
    if deck_pdf.is_file() and pdf_page_count(deck_pdf) != 23:
        failures.append(
            f"deck PDF must have 23 pages; found {pdf_page_count(deck_pdf)}"
        )
    pre_read_pdf = artifacts["primary pre-read PDF"]
    if pre_read_pdf.is_file() and pdf_page_count(pre_read_pdf) != 2:
        failures.append(
            f"pre-read PDF must have 2 pages; found {pdf_page_count(pre_read_pdf)}"
        )

    pptx_path = artifacts["primary PPTX"]
    return pptx_slide_texts(pptx_path, failures), pptx_note_texts(pptx_path, failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="VEGO-AI repository root",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    failures: list[str] = []
    texts = {
        name: read_text(root / relative, failures)
        for name, relative in REQUIRED_FILES.items()
    }

    record = texts["record"]
    for status in (
        "Confirmed directive",
        "Discussion or proposal",
        "Open choice",
        "Parked",
        "Needs transcript verification",
    ):
        require(record, status, "record status legend", failures)

    directive_rows = re.findall(
        r"^(\|\s*(D(?:[1-9]|1[0-2]))\s*\|.*)$", record, re.MULTILINE
    )
    directive_counts = Counter(identifier for _, identifier in directive_rows)
    if directive_counts != Counter(EXPECTED_DIRECTIVES):
        failures.append(f"D1-D12 rows must be unique and complete; found {directive_counts}")
    for line, identifier in directive_rows:
        cells = table_cells(line)
        if len(cells) != 8:
            failures.append(f"{identifier}: evidence row must have 8 fields; found {len(cells)}")
            continue
        if not re.search(r"\d{2}:\d{2}:\d{2}", cells[2]) and "derived" not in cells[5].casefold():
            failures.append(f"{identifier}: requires a timestamp or Derived classification")
        if not re.search(r"explicit|derived", cells[5], re.I):
            failures.append(f"{identifier}: explicit-versus-derived classification is missing")
    d1_line = next((line for line, identifier in directive_rows if identifier == "D1"), "")
    d6_line = next((line for line, identifier in directive_rows if identifier == "D6"), "")
    require(d1_line, "M-03", "D1 decision traceability", failures)
    require(d6_line, "M-05", "D6 decision traceability", failures)

    evidence = texts["evidence"]
    require(evidence, "Hebrew", "evidence appendix", failures)
    require(evidence, "unreviewed machine ASR", "evidence appendix", failures)
    require(evidence, "unverified paraphrase", "evidence appendix", failures)
    require(evidence, "not a quotation", "evidence appendix", failures)

    provenance = texts["provenance"]
    for relative, expected in CANONICAL_HASHES.items():
        source = root / relative
        if not source.is_file():
            failures.append(f"missing canonical local source: {source}")
            continue
        actual = sha256(source)
        if actual != expected:
            failures.append(
                f"canonical source hash mismatch for {relative}: expected {expected}, found {actual}"
            )
        if expected not in provenance.casefold():
            failures.append(f"provenance does not record canonical hash for {relative}")
    if not re.search(r"(?:raw|full) ASR (?:must )?remain local|keep the full recording and full ASR local", provenance, re.I):
        failures.append("privacy policy must keep the full/raw ASR local")

    decisions = texts["decisions"]
    heading_counts = Counter(
        re.findall(r"^##\s+(M-0[1-6])\s+-", decisions, re.MULTILINE)
    )
    if heading_counts != Counter(EXPECTED_DECISIONS):
        failures.append(f"decision headings must be unique and complete; found {heading_counts}")
    sections = section_map(decisions)
    for identifier in EXPECTED_DECISIONS:
        section = sections.get(identifier, "")
        if not section:
            continue
        for field in DECISION_FIELDS:
            matches = re.findall(
                rf"^\|\s*{re.escape(field)}\s*\|", section, re.MULTILINE | re.I
            )
            if len(matches) != 1:
                failures.append(
                    f"{identifier}: field {field!r} must appear exactly once; found {len(matches)}"
                )
        if decision_field(section, "ID") != identifier:
            failures.append(f"{identifier}: ID field does not match its heading")
        if not decision_field(section, "exact decision requested"):
            failures.append(f"{identifier}: exact decision request is blank")
    for outcome in ("Accepted", "Accepted with changes", "Rejected", "Deferred"):
        require(decisions, outcome, "decision outcome vocabulary", failures)
    require(decisions, "Not yet recorded", "pre-meeting outcome placeholder", failures)

    for identifier in EXPECTED_DECISIONS:
        request = decision_field(sections.get(identifier, ""), "exact decision requested")
        if identifier == "M-05":
            require(request, "timeout", "M-05 exact decision", failures)
        elif re.search(r"\btimeout\b", request, re.I):
            failures.append(f"{identifier}: timeout must be decided only under M-05")

    m03 = sections.get("M-03", "")
    require(m03, "historical recorded outputs", "M-03 evidence provenance", failures)
    require(m03, "not rerun for this package", "M-03 evidence provenance", failures)
    if re.search(r"candidate default", m03, re.I):
        failures.append("M-03 must not label threshold_sev2 as a candidate default")

    actions = texts["actions"]
    action_rows = re.findall(
        r"^(\|\s*(J1-A\d{2}|A-\d{2})\s*\|.*)$", actions, re.MULTILINE
    )
    action_counts = Counter(identifier for _, identifier in action_rows)
    duplicates = sorted(identifier for identifier, count in action_counts.items() if count != 1)
    if duplicates:
        failures.append(f"action register contains duplicate action rows: {duplicates}")
    for identifier in EXPECTED_JULY1_ACTIONS:
        if action_counts[identifier] != 1:
            failures.append(f"action register must preserve {identifier} exactly once")
    for line, identifier in action_rows:
        if len(table_cells(line)) != len(ACTION_FIELDS):
            failures.append(
                f"{identifier}: action row must contain {len(ACTION_FIELDS)} fields"
            )
    for field in ACTION_FIELDS:
        require(actions, field, "action register interface", failures)
    j1a04 = next((line for line, identifier in action_rows if identifier == "J1-A04"), "")
    require(j1a04, "Not specified", "J1-A04 due-date fidelity", failures)

    capture = texts["capture"]
    for identifier in EXPECTED_JULY1_ACTIONS:
        rows = re.findall(rf"^\|\s*{re.escape(identifier)}\s*\|", capture, re.MULTILINE)
        if len(rows) != 1:
            failures.append(f"capture template must contain {identifier} exactly once")
    capture_m03 = re.findall(r"^\|\s*M-03\s*\|.*$", capture, re.MULTILINE)
    capture_m05 = re.findall(r"^\|\s*M-05\s*\|.*$", capture, re.MULTILINE)
    if any(re.search(r"\btimeout\b", row, re.I) for row in capture_m03):
        failures.append("capture template must keep timeout out of M-03")
    if not any(re.search(r"\btimeout\b", row, re.I) for row in capture_m05):
        failures.append("capture template must record timeout under M-05")

    pre_read = texts["pre_read"]
    if "0.6667" in pre_read:
        failures.append("executive pre-read must not contain the EXP-012 0.6667 pilot")
    for needle in (
        "threshold_sev2",
        "pilot candidate",
        "EXP-009",
        "EXP-010",
        "synthetic",
        "cannot be evaluated",
        "historical recorded outputs",
        "not rerun for this package",
    ):
        require(pre_read, needle, "executive pre-read", failures)

    package_index = texts["package_index"]
    for prohibited in ("candidate default", "0.6667"):
        if prohibited.casefold() in package_index.casefold():
            failures.append(f"package index contains prohibited legacy wording: {prohibited}")
    require(package_index, "superseded", "legacy package reconciliation", failures)
    require(package_index, "M-01 through M-06", "package decision interface", failures)

    redirect = texts["redirect"]
    for pattern in (
        r"\(verified meeting notes\)",
        r"interpretations verified",
        r"key claims verified",
        r"open questions confirmed with Iris on 2026-07-15",
    ):
        if re.search(pattern, redirect, re.I):
            failures.append(f"redirect plan retains premature verification wording: {pattern}")
    require(redirect, "awaiting participant confirmation", "redirect evidence status", failures)

    package_core = "\n".join(
        texts[name]
        for name in (
            "decisions",
            "actions",
            "annex",
            "pre_read",
            "capture",
            "package_index",
        )
    )
    prohibited_claims = (
        r"\baccuracy (?:has )?improved\b",
        r"\bproves? generalization\b",
        r"\bdemonstrates? generalization\b",
        r"\bclinical performance (?:has )?improved\b",
        r"\b(?:Iris|Arnon|supervisors?) (?:approved|endorsed|selected) (?:Option B|MediVARIA|the four-source|the two-round|threshold_sev2)",
        r"\b(?:Option B|MediVARIA|the four-source set|the two-round bound) (?:is|was) supervisor-approved\b",
    )
    for pattern in prohibited_claims:
        if re.search(pattern, package_core, re.I):
            failures.append(f"prohibited or premature claim matched: {pattern}")

    manifest = texts["output_manifest"]
    slide_texts, note_texts = validate_artifacts(root, manifest, failures)
    if slide_texts:
        if len(slide_texts) != 23:
            failures.append(f"decision deck must have 23 slides; found {len(slide_texts)}")
        provenance_terms = ("record", "working draft", "offline evidence", "decision", "outcome")
        for number, text in enumerate(slide_texts, start=1):
            if not any(term in text.casefold() for term in provenance_terms):
                failures.append(f"slide {number}: missing visible provenance label")
        main_story = "\n".join(slide_texts[:12])
        if "0.6667" in main_story:
            failures.append("EXP-012 0.6667 must remain outside the 12-slide main story")
        if len(slide_texts) >= 15 and not re.search(r"[\u0590-\u05ff]", slide_texts[14]):
            failures.append("slide 15 must contain selected timestamped Hebrew evidence")
        for pattern in prohibited_claims[:4]:
            if re.search(pattern, main_story, re.I):
                failures.append(f"deck main story contains prohibited claim: {pattern}")
        if re.search(r"\btimeout\b", slide_texts[7], re.I):
            failures.append("M-03 slide must not ask the timeout question")
        if not re.search(r"\btimeout\b", slide_texts[9], re.I):
            failures.append("M-05 slide must contain the timeout decision")
    if note_texts:
        if len(note_texts) != 23:
            failures.append(f"decision deck must have 23 speaker-note records; found {len(note_texts)}")
        for number, note in enumerate(note_texts[:12], start=1):
            if "Timing:" not in note:
                failures.append(f"slide {number}: core-slide speaker notes need a timing cue")
        if len(note_texts) >= 8 and re.search(r"\btimeout\b", note_texts[7], re.I):
            failures.append("M-03 speaker notes must not duplicate the timeout decision")

    if failures:
        print("SUPERVISOR DECISION PACKAGE: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("SUPERVISOR DECISION PACKAGE: PASS")
    print("- canonical sources rehashed and D1-D12 traceability is unique")
    print("- every M-record and action row conforms to its document interface")
    print("- July 1, later work, and requested decisions remain separated")
    print("- timeout is owned by M-05 and historical replay status is explicit")
    print("- PPTX/PDF/pre-read copies, hashes, slide/page counts, and provenance labels agree")
    print("- pilot, evidence, privacy, and claim boundaries pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
