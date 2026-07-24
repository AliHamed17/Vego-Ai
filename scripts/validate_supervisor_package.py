#!/usr/bin/env python3
"""Validate the July 21 supervisor package without controlled evidence inputs."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "docs/research/meetings/2026-07-21-supervisor-package-data-v3.json"
HTML_FILE = ROOT / "VEGO-AI-July1-PointByPoint-EN-HE.html"
BUILDER = ROOT / "scripts/build_supervisor_package.py"
DATA_PATTERN = re.compile(
    r'<script type="application/json" id="vego-data">\s*(.*?)\s*</script>',
    re.DOTALL,
)

EXPECTED = {
    "directives": [f"D{i}" for i in range(1, 13)],
    "actions": [f"J1-A{i:02d}" for i in range(1, 7)],
    "events": [f"E{i}" for i in range(1, 16)],
    "experiments": [f"EXP-{i:03d}" for i in range(19)],
    "iterations": [f"ITER-{i:03d}" for i in range(1, 15)],
    "decisions": [f"M-{i:02d}" for i in range(1, 7)],
}

PROHIBITED_POSITIVE_CLAIMS = [
    r"\bimproved accuracy\b",
    r"\baccuracy (?:has )?improved\b",
    r"\bproven generalization\b",
    r"\bgeneralizes? across\b",
    r"\bbetter than (?:the )?baseline\b",
    r"\bbenchmark superiority (?:is )?(?:shown|proven|demonstrated)\b",
    r"\breduced human effort at scale\b",
    r"\bclinical performance (?:is )?(?:shown|improved|validated)\b",
    r"\bexpert-confirmed\b",
    r"\bautomatic reclassification\b",
]


class PackageHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.external_runtime_urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(str(values["id"]))
        for name in ("src", "href"):
            value = values.get(name)
            if value and re.match(r"^(?:https?:)?//", value):
                self.external_runtime_urls.append(value)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def ids(rows: list[dict[str, Any]]) -> list[str]:
    return [str(row["id"]) for row in rows]


def bilingual_coverage(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        if "en" in value:
            if "he" not in value:
                fail(errors, f"{path}: bilingual object must contain en and he")
            elif not all(isinstance(value[key], str) and value[key].strip() for key in ("en", "he")):
                fail(errors, f"{path}: bilingual values must be non-empty strings")
        elif "he" in value:
            if not isinstance(value.get("label"), str) or not value["label"].strip():
                fail(errors, f"{path}: chart label with he must also contain a non-empty English label")
            elif not isinstance(value["he"], str) or not value["he"].strip():
                fail(errors, f"{path}: Hebrew chart label must be non-empty")
        for key, child in value.items():
            bilingual_coverage(child, f"{path}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            bilingual_coverage(child, f"{path}[{index}]", errors)


def validate() -> list[str]:
    errors: list[str] = []
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    html = HTML_FILE.read_text(encoding="utf-8")

    if data.get("schemaVersion") != "SupervisorPackageData-v3":
        fail(errors, "schemaVersion must be SupervisorPackageData-v3")
    for collection, expected in EXPECTED.items():
        actual = ids(data.get(collection, []))
        if actual != expected:
            fail(errors, f"{collection}: expected {expected}, found {actual}")
        duplicates = [item for item, count in Counter(actual).items() if count > 1]
        if duplicates:
            fail(errors, f"{collection}: duplicate IDs {duplicates}")

    valid = {
        "components": set(ids(data["components"])),
        "directives": set(ids(data["directives"])),
        "events": set(ids(data["events"])),
        "skills": set(ids(data["skills"])),
        "artifacts": set(ids(data["artifacts"])),
        "experiments": set(ids(data["experiments"])),
        "decisions": set(ids(data["decisions"])),
        "sources": set(ids(data["sources"])),
    }
    required_directive_fields = [
        "timestamp",
        "speakerAttribution",
        "attributionConfidence",
        "explicitDerivedClass",
        "englishReviewStatus",
        "hebrewReviewStatus",
        "requirement",
        "did",
        "current",
        "next",
        "boundary",
        "componentIds",
        "skillIds",
        "eventIds",
        "artifactIds",
        "experimentIds",
        "decisionIds",
        "provenance",
        "claimBoundary",
    ]
    link_fields = {
        "componentIds": "components",
        "skillIds": "skills",
        "eventIds": "events",
        "artifactIds": "artifacts",
        "experimentIds": "experiments",
        "decisionIds": "decisions",
    }
    components = {row["id"]: row for row in data["components"]}
    for directive in data["directives"]:
        for field in required_directive_fields:
            if field not in directive or directive[field] in (None, ""):
                fail(errors, f"{directive['id']}: missing {field}")
        for field, collection in link_fields.items():
            unknown = set(directive.get(field, [])) - valid[collection]
            if unknown:
                fail(errors, f"{directive['id']}.{field}: unresolved {sorted(unknown)}")
        component = components.get(directive["componentId"])
        if not component or directive["id"] not in component.get("directives", []):
            fail(errors, f"{directive['id']}: component link is not bidirectional")

    for component in data["components"]:
        for field, collection in {
            "directives": "directives",
            "skillIds": "skills",
            "eventIds": "events",
            "artifacts": "artifacts",
            "experiments": "experiments",
            "decisionIds": "decisions",
        }.items():
            unknown = set(component.get(field, [])) - valid[collection]
            if unknown:
                fail(errors, f"{component['id']}.{field}: unresolved {sorted(unknown)}")

    source_by_id = {row["id"]: row for row in data["sources"]}
    for evidence in data["evidenceRecords"]:
        for field in (
            "value",
            "denominator",
            "unit",
            "sourceId",
            "evidenceClass",
            "observationDate",
            "claimBoundary",
        ):
            if evidence.get(field) in (None, ""):
                fail(errors, f"{evidence['id']}: missing {field}")
        source = source_by_id.get(evidence.get("sourceId"))
        if not source:
            fail(errors, f"{evidence['id']}: unresolved source")
        elif not re.fullmatch(r"[0-9a-fA-F]{64}", str(source.get("sha256", ""))):
            fail(errors, f"{evidence['id']}: source has no valid SHA-256")

    e15 = next(row for row in data["events"] if row["id"] == "E15")
    if e15["scope"] != "evaluation_only" or e15["frameworkActionAllowed"]:
        fail(errors, "E15 must remain evaluation-only and unable to create a framework action")
    if any(row["frameworkActionAllowed"] for row in data["events"]):
        fail(errors, "No event may authorize a live framework action while M-05 is deferred")

    status = data["programStatus"]
    if status["latestAcceptedIteration"]["iteration"] != 14:
        fail(errors, "latest accepted iteration must be 14")
    if status["latestAcceptedIteration"]["verdict"] != "NEUTRAL":
        fail(errors, "Iteration 14 verdict must be NEUTRAL")
    if status["exp005Gate"]["suppliedLabels"] != 0:
        fail(errors, "EXP-005 supplied labels must remain zero")
    if status["exp012Gate"]["result"] != "NOT YET COMPUTABLE":
        fail(errors, "EXP-012 must remain NOT YET COMPUTABLE")
    if set(status["decisionState"][f"M-{i:02d}"] for i in range(1, 7)) != {"Deferred"}:
        fail(errors, "M-01 through M-06 must remain Deferred before recorded outcomes")
    if status["decisionState"]["runtimeAuthorization"]:
        fail(errors, "runtime authorization must remain false")
    for decision in data["decisions"]:
        if decision["outcome"] != "Not recorded" or decision["confirmationStatus"] != "unconfirmed":
            fail(errors, f"{decision['id']}: pre-meeting outcome must remain unrecorded/unconfirmed")

    match = DATA_PATTERN.search(html)
    if not match:
        fail(errors, "HTML has no embedded canonical data")
    else:
        embedded = json.loads(match.group(1))
        if embedded != data:
            fail(errors, "HTML embedded data differs from canonical JSON")

    parser = PackageHTMLParser()
    parser.feed(html)
    duplicate_dom_ids = [item for item, count in Counter(parser.ids).items() if count > 1]
    if duplicate_dom_ids:
        fail(errors, f"HTML duplicate DOM IDs: {duplicate_dom_ids[:10]}")
    if parser.external_runtime_urls:
        fail(errors, f"HTML runtime has external dependencies: {parser.external_runtime_urls}")

    lowered = html.lower()
    for pattern in PROHIBITED_POSITIVE_CLAIMS:
        if re.search(pattern, lowered):
            fail(errors, f"prohibited positive claim matched: {pattern}")
    if "agent 4 remains unchanged" not in lowered:
        fail(errors, "baseline protection statement is missing")
    if "not yet computable" not in lowered:
        fail(errors, "EXP-012 stop statement is missing")
    bilingual_coverage(data, "data", errors)

    result = subprocess.run(
        [sys.executable, str(BUILDER), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        fail(errors, f"deterministic build check failed: {result.stderr or result.stdout}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        print(f"supervisor package validation: {len(errors)} failure(s)", file=sys.stderr)
        return 1
    digest = hashlib.sha256(HTML_FILE.read_bytes()).hexdigest()
    print(f"supervisor package validation: PASS ({digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
