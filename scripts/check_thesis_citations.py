#!/usr/bin/env python3
"""Check author-year thesis citations against the references chapter."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "thesis/chapters"
REFERENCES = CHAPTER_DIR / "11-references.md"
YEAR_RE = r"(?:19|20)\d{2}[a-z]?"
ALIASES = {
    "nist": "national",
}


def normalized(value: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", value).encode(
        "ascii", "ignore"
    ).decode("ascii")
    token = re.sub(r"[^a-z0-9]+", "", ascii_text.casefold())
    return ALIASES.get(token, token)


def strip_code_fences(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def reference_entries() -> list[str]:
    text = REFERENCES.read_text(encoding="utf-8")
    return [
        paragraph.replace("\n", " ").strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip() and not paragraph.lstrip().startswith("#")
    ]


def reference_key(entry: str) -> tuple[str, str] | None:
    year_match = re.search(rf"\(({YEAR_RE})\)", entry)
    if not year_match:
        return None
    lead = entry[: year_match.start()].strip()
    first_author = lead.split(",", 1)[0].split()[0]
    return normalized(first_author), year_match.group(1).casefold()


def citation_keys(
    text: str, known_reference_keys: set[tuple[str, str]]
) -> set[tuple[str, str]]:
    text = strip_code_fences(text)
    text = "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("- ")
    )
    keys: set[tuple[str, str]] = set()
    for group in re.findall(
        rf"\(([^()\n]{{0,260}}\b{YEAR_RE}[^()\n]{{0,260}})\)", text
    ):
        for part in group.split(";"):
            match = re.search(rf"([A-Z][^,;]{{0,90}}),\s*({YEAR_RE})", part)
            if not match:
                continue
            first_author = match.group(1).strip().split()[0]
            keys.add((normalized(first_author), match.group(2).casefold()))
    narrative_patterns = (
        rf"\b([A-Z][A-Za-zÀ-ÖØ-öø-ÿ'’.-]+)\s+et\s+al\.\s+\(({YEAR_RE})\)",
        rf"\b([A-Z][A-Za-zÀ-ÖØ-öø-ÿ'’.-]+)"
        rf"\s+(?:and|&)\s+[A-Z][A-Za-zÀ-ÖØ-öø-ÿ'’.-]+['’]s?\s+\(({YEAR_RE})\)",
        rf"\b(NIST)(?:\s+AI\s+Risk\s+Management\s+Framework)?\s+\(({YEAR_RE})\)",
    )
    for pattern in narrative_patterns:
        for match in re.finditer(pattern, text):
            keys.add((normalized(match.group(1)), match.group(2).casefold()))
    # Recognize a single-author narrative only when that key exists in the
    # reference chapter. This avoids treating ordinary phrases such as
    # "framework (2023)" and bibliography initials as author citations.
    for match in re.finditer(
        rf"\b([A-Z][A-Za-zÀ-ÖØ-öø-ÿ'’.-]+)\s+\(({YEAR_RE})\)", text
    ):
        key = (normalized(match.group(1)), match.group(2).casefold())
        if key in known_reference_keys:
            keys.add(key)
    return keys


def validate_urls(entries: list[str]) -> list[str]:
    errors: list[str] = []
    for entry in entries:
        for raw_url in re.findall(r"https?://[^\s)]+", entry):
            url = raw_url.rstrip(".,")
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                errors.append(f"invalid reference URL: {url}")
            if "doi.org" in parsed.netloc and not parsed.path.strip("/"):
                errors.append(f"DOI URL has no identifier: {url}")
    return errors


def audit() -> dict[str, object]:
    entries = reference_entries()
    reference_keys: list[tuple[str, str]] = []
    errors: list[str] = []
    for entry in entries:
        key = reference_key(entry)
        if key is None:
            errors.append(f"reference has no author-year key: {entry[:100]}")
        else:
            reference_keys.append(key)
    duplicates = sorted(
        {key for key in reference_keys if reference_keys.count(key) > 1}
    )
    errors.extend(
        f"duplicate reference key: {author} {year}" for author, year in duplicates
    )

    known = set(reference_keys)
    cited: set[tuple[str, str]] = set()
    per_file: dict[str, list[str]] = {}
    for path in sorted(CHAPTER_DIR.glob("*.md")):
        if path == REFERENCES:
            continue
        keys = citation_keys(path.read_text(encoding="utf-8"), known)
        cited.update(keys)
        per_file[path.name] = [f"{author}:{year}" for author, year in sorted(keys)]

    missing = sorted(cited - known)
    errors.extend(
        f"citation has no reference: {author} {year}" for author, year in missing
    )
    errors.extend(validate_urls(entries))
    uncited = sorted(known - cited)
    return {
        "status": "PASS" if not errors else "FAIL",
        "referenceCount": len(entries),
        "citationKeyCount": len(cited),
        "uncitedReferenceKeys": [
            f"{author}:{year}" for author, year in uncited
        ],
        "citationsByFile": per_file,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit()
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["status"] == "PASS":
        print(
            "thesis citation integrity: PASS "
            f"({result['citationKeyCount']} citation keys, "
            f"{result['referenceCount']} references)"
        )
    else:
        print("thesis citation integrity: FAIL")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
