#!/usr/bin/env python3
"""Validate the July 29 Iris requirements-closure control package.

The checks in this module are documentation and governance conformance checks.
They do not turn a pending supervisor decision, human transcript review, live
presentation rehearsal, medical gate, or empirical evaluation into completed
evidence.

Examples:
    python scripts/validate_iris_requirements_closure.py --all
    python scripts/validate_iris_requirements_closure.py --experiment IRIS-EXP-01
    python scripts/validate_iris_requirements_closure.py --all --refresh
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

MASTER = ROOT / "docs/research/phd-proposal/master-traceability-register.md"
CLOSURE = ROOT / "docs/research/phd-proposal/iris-requirements-closure-audit.md"
REQUIREMENT_REGISTER = (
    ROOT / "docs/research/meetings/2026-07-29-iris-requirements-register.md"
)
ACTION_REGISTER = (
    ROOT / "docs/research/meetings/2026-07-29-iris-supervisor-action-register.md"
)
EXPERIMENT_REGISTER = (
    ROOT / "docs/research/phd-proposal/iris-alignment-experiment-register.md"
)
PRESENTATION = (
    ROOT
    / "docs/research/meetings/2026-08-05-supervisor-presentation-checklist.md"
)
WEEKLY_TEMPLATE = (
    ROOT / "docs/templates/weekly-supervisor-pre-read.md"
)
DECISION_LOG = ROOT / "docs/research/phd-proposal/decision-change-log.md"
CLAIM_REGISTER = ROOT / "docs/research/phd-proposal/claim-register.md"

EXPERIMENTS = (
    "IRIS-EXP-01",
    "IRIS-EXP-02",
    "IRIS-EXP-03",
    "IRIS-EXP-04",
)
EXPECTED_IDS = (
    tuple(f"R-{index:02d}" for index in range(1, 20))
    + tuple(f"A-{index:02d}" for index in range(1, 16))
    + tuple(f"Q-{index:02d}" for index in range(1, 11))
)
EXPECTED_STATUS_COUNTS = {
    "Verified complete": 2,
    "Implemented awaiting human acceptance": 6,
    "Partial": 22,
    "Open": 5,
    "Blocked": 9,
}
CANONICAL_QUESTIONS = (
    "How can reusable human judgment be captured, governed, and reused in "
    "agentic AI assessment of domain-specific artifacts and processes to "
    "support auditable, reliable, and transferable human–AI co-reasoning?",
    "When and how should an agentic assessment system request human judgment "
    "so that important uncertainties are addressed without unnecessary expert "
    "burden?",
    "How should expert judgments be represented, validated, reconciled, and "
    "stored so they can be reused transparently without unsafe generalization "
    "or loss of human authority?",
    "To what extent does the resulting framework improve assessment quality, "
    "consistency, traceability, and expert effort across domains, first in "
    "software/modeling and, when governance and access permit, in healthcare?",
)
RQ_FILES = (
    MASTER,
    ROOT / "docs/research/phd-proposal/README.md",
    ROOT / "docs/research/phd-proposal/2026-07-29-doctoral-execution-plan.md",
    ROOT / "docs/research/phd-proposal/2026-08-05-rq-decision-pack.md",
    ROOT / "docs/research/phd-proposal/three-study-contract.md",
    ROOT / "docs/research/phd-proposal/proposal-v0.1.md",
)


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class Result:
    experiment: str
    state: str
    checks: tuple[Check, ...]
    evidence_boundary: str

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)


def read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def table_rows(path: Path) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in read(path).splitlines():
        match = re.match(r"^\|\s*((?:R|A|Q)-\d{2})\s*\|", line)
        if not match:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[match.group(1)] = cells
    return rows


def local_link_errors(path: Path) -> list[str]:
    errors: list[str] = []
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", read(path)):
        clean_target = target.strip()
        if (
            clean_target.startswith(("http://", "https://", "mailto:", "#"))
            or clean_target == ""
        ):
            continue
        target_parts = clean_target.split("#", 1)
        file_part = unquote(target_parts[0]).strip("<>")
        resolved = (path.parent / file_part).resolve()
        if not resolved.exists():
            errors.append(f"{path.relative_to(ROOT)} -> {clean_target}")
            continue
        if (
            len(target_parts) == 2
            and "iris-supervisor-bilingual-transcript" in resolved.name
        ):
            anchor = unquote(target_parts[1]).lower()
            target_text = read(resolved).lower()
            if f'<a id="{anchor}"></a>' not in target_text:
                errors.append(
                    f"{path.relative_to(ROOT)} -> missing anchor {clean_target}"
                )
    return errors


def exp01() -> Result:
    master_rows = table_rows(MASTER)
    closure_rows = table_rows(CLOSURE)
    requirement_rows = table_rows(REQUIREMENT_REGISTER)
    action_rows = table_rows(ACTION_REGISTER)
    master_ids = tuple(master_rows)
    closure_ids = tuple(closure_rows)
    source_ids = tuple(requirement_rows) + tuple(action_rows)
    status_counts = Counter(
        row[5] for row in closure_rows.values() if len(row) >= 6
    )
    incomplete_master = sorted(
        row_id
        for row_id, row in master_rows.items()
        if len(row) != 11 or any(not cell for cell in row)
    )
    incomplete_closure = sorted(
        row_id
        for row_id, row in closure_rows.items()
        if len(row) != 7 or any(not cell for cell in row)
    )
    missing_locator = sorted(
        row_id
        for row_id, row in closure_rows.items()
        if len(row) < 2 or "S-" not in row[1] or "00:" not in row[1]
    )
    link_errors: list[str] = []
    for path in (
        REQUIREMENT_REGISTER,
        ACTION_REGISTER,
        MASTER,
        CLOSURE,
        PRESENTATION,
    ):
        link_errors.extend(local_link_errors(path))

    checks = (
        Check(
            "source registers contain the exact 19/15/10 ID set",
            source_ids == EXPECTED_IDS,
            f"found {len(source_ids)} rows",
        ),
        Check(
            "master contains the exact 19/15/10 ID set",
            master_ids == EXPECTED_IDS,
            f"found {len(master_ids)} rows",
        ),
        Check(
            "closure audit contains the exact 19/15/10 ID set",
            closure_ids == EXPECTED_IDS,
            f"found {len(closure_ids)} rows",
        ),
        Check(
            "master owner/gate/evidence/acceptance/status fields are populated",
            not incomplete_master,
            "missing or malformed: " + ", ".join(incomplete_master)
            if incomplete_master
            else "44/44 rows populated",
        ),
        Check(
            "closure rows contain all seven control fields",
            not incomplete_closure,
            "missing or malformed: " + ", ".join(incomplete_closure)
            if incomplete_closure
            else "44/44 rows populated",
        ),
        Check(
            "every closure row has a segment and timestamp locator",
            not missing_locator,
            "missing: " + ", ".join(missing_locator)
            if missing_locator
            else "44/44 locators present",
        ),
        Check(
            "closure classifications preserve the audited readiness boundary",
            dict(status_counts) == EXPECTED_STATUS_COUNTS,
            f"found {dict(status_counts)}",
        ),
        Check(
            "closure and presentation local links resolve",
            not link_errors,
            "; ".join(link_errors) if link_errors else "all local links resolve",
        ),
    )
    return Result(
        experiment="IRIS-EXP-01",
        state="PASS" if all(check.passed for check in checks) else "FAIL",
        checks=checks,
        evidence_boundary=(
            "A PASS proves control completeness and link integrity, not that all "
            "requirements have been accepted or completed."
        ),
    )


def exp02() -> Result:
    text = read(PRESENTATION)
    required_sections = (
        "## Presentation sequence",
        "## Requirement coverage matrix",
        "## Before the meeting",
        "## During the meeting",
        "## After the meeting",
        "## Forbidden claims",
    )
    missing_sections = [section for section in required_sections if section not in text]
    missing_requirements = [
        row_id for row_id in EXPECTED_IDS[:19] if row_id not in text
    ]
    required_decisions = [f"D-RQ-{index:02d}" for index in range(1, 11)]
    missing_decisions = [decision for decision in required_decisions if decision not in text]
    checks = (
        Check(
            "presentation checklist contains the full preflight/live/closeout flow",
            not missing_sections,
            "missing: " + ", ".join(missing_sections)
            if missing_sections
            else "all required sections present",
        ),
        Check(
            "presentation maps R-01 through R-19",
            not missing_requirements,
            "missing: " + ", ".join(missing_requirements)
            if missing_requirements
            else "19/19 requirements mapped",
        ),
        Check(
            "presentation exposes all ten supervisor decisions",
            not missing_decisions,
            "missing: " + ", ".join(missing_decisions)
            if missing_decisions
            else "10/10 decision IDs present",
        ),
        Check(
            "presentation explicitly records the human rehearsal boundary",
            "Live rehearsal status: **NOT RUN**" in text,
            "live rehearsal must remain NOT RUN until a dated human session occurs",
        ),
    )
    return Result(
        experiment="IRIS-EXP-02",
        state=(
            "READY_PENDING_HUMAN_RUN"
            if all(check.passed for check in checks)
            else "FAIL"
        ),
        checks=checks,
        evidence_boundary=(
            "Document preflight may pass automatically. Timing, comprehensibility, "
            "speaker handoffs, and decision capture require a dated human rehearsal."
        ),
    )


def exp03() -> Result:
    rq_missing: list[str] = []
    for path in RQ_FILES:
        text = read(path)
        for index, question in enumerate(CANONICAL_QUESTIONS):
            if question not in text:
                rq_missing.append(f"{path.relative_to(ROOT)}: RQ{index}")

    claim_text = read(CLAIM_REGISTER)
    required_claim_states = (
        "Established",
        "Preliminary",
        "Planned",
        "Blocked",
        "Partner-dependent",
    )
    closure_text = read(CLOSURE)
    presentation_assertions = read(PRESENTATION).split(
        "\n## Forbidden claims", 1
    )[0]
    package_text = "\n".join(
        (
            read(CLOSURE),
            presentation_assertions,
            read(ROOT / "docs/research/meetings/2026-08-05-supervisor-pre-read.md"),
            read(ROOT / "docs/research/phd-proposal/proposal-v0.1.md"),
        )
    )
    unsafe_patterns = (
        r"\ball (?:Iris )?requirements (?:are|have been) "
        r"(?:done|complete|completed|satisfied)\b",
        r"\bmedical readiness (?:is|has been) (?:complete|completed|approved)\b",
        r"\bEXP-005 (?:is|has) (?:complete|completed|passed)\b",
        r"\bclinical performance (?:is|has been) (?:proven|validated|improved)\b",
    )
    unsafe_matches: list[str] = []
    for line in package_text.splitlines():
        if re.search(
            r"\b(?:not|never|cannot|can't|do not|does not|no longer)\b",
            line,
            re.IGNORECASE,
        ):
            continue
        for pattern in unsafe_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                unsafe_matches.append(f"{pattern}: {line.strip()}")
    checks = (
        Check(
            "canonical one-plus-three wording is identical in core artifacts",
            not rq_missing,
            "; ".join(rq_missing) if rq_missing else "all six artifacts agree",
        ),
        Check(
            "all five claim states remain explicit",
            all(state in claim_text for state in required_claim_states),
            "required states: " + ", ".join(required_claim_states),
        ),
        Check(
            "closure audit preserves EXP-005 and medical gates",
            "EXP-005 remains `0/24`" in closure_text
            and "Medical readiness remains `0/6`" in closure_text,
            "both current gate values must be explicit",
        ),
        Check(
            "package contains no prohibited completion or performance claim",
            not unsafe_matches,
            "matched patterns: " + ", ".join(unsafe_matches)
            if unsafe_matches
            else "no prohibited pattern found",
        ),
        Check(
            "machine transcript and attribution caveat remains explicit",
            "machine-derived" in closure_text
            and "S-0001–S-0006" in closure_text
            and "direct quotation" in closure_text,
            "named attribution and quotation boundary must be visible",
        ),
    )
    return Result(
        experiment="IRIS-EXP-03",
        state="PASS" if all(check.passed for check in checks) else "FAIL",
        checks=checks,
        evidence_boundary=(
            "A PASS proves wording and claim-boundary consistency. It supplies no "
            "expert labels, medical evidence, or supervisor approval."
        ),
    )


def exp04() -> Result:
    weekly = read(WEEKLY_TEMPLATE)
    decision = read(DECISION_LOG)
    master = read(MASTER)
    required_weekly_fields = (
        "Previous commitment",
        "Completed evidence",
        "Blocker",
        "Decision requested",
        "Proposal delta",
        "One next task",
        "Definition of done",
        "Decision read-back",
    )
    missing_weekly = [field for field in required_weekly_fields if field not in weekly]
    required_decision_fields = (
        "Decision",
        "Date",
        "Rationale",
        "Affected artifacts",
        "Supersedes",
    )
    missing_decision = [
        field for field in required_decision_fields if field not in decision
    ]
    checks = (
        Check(
            "weekly pre-read template contains the commitment-to-closeout chain",
            not missing_weekly,
            "missing: " + ", ".join(missing_weekly)
            if missing_weekly
            else "all required fields present",
        ),
        Check(
            "decision log preserves change-propagation fields",
            not missing_decision,
            "missing: " + ", ".join(missing_decision)
            if missing_decision
            else "all required fields present",
        ),
        Check(
            "master register binds weekly evidence and decision read-back",
            "Dated weekly pre-reads, proposal deltas, and completed artifacts" in master
            and "decision read-back" in master,
            "R-06/R-13 controls must stay explicit",
        ),
        Check(
            "next-cycle execution remains evidence-honest",
            "First live-cycle status: **NOT RUN**" in weekly,
            "status must remain NOT RUN until the next meeting cycle is closed",
        ),
    )
    return Result(
        experiment="IRIS-EXP-04",
        state=(
            "READY_PENDING_NEXT_MEETING"
            if all(check.passed for check in checks)
            else "FAIL"
        ),
        checks=checks,
        evidence_boundary=(
            "The protocol is testable now; propagation effectiveness is not observed "
            "until a real weekly meeting produces a pre-read, decision, and proposal delta."
        ),
    )


RUNNERS = {
    "IRIS-EXP-01": exp01,
    "IRIS-EXP-02": exp02,
    "IRIS-EXP-03": exp03,
    "IRIS-EXP-04": exp04,
}


def render(results: list[Result]) -> str:
    lines = [
        "# Iris Requirements-Closure Validation",
        "",
        "These are documentation/governance conformance results. A passing automated "
        "check does not close a human or external gate.",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"## {result.experiment}",
                "",
                f"- State: **{result.state}**",
                f"- Evidence boundary: {result.evidence_boundary}",
                "",
            ]
        )
        for check in result.checks:
            marker = "PASS" if check.passed else "FAIL"
            lines.append(f"- [{marker}] {check.name} — {check.detail}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--experiment",
        choices=EXPERIMENTS,
        help="Run one Iris-alignment experiment.",
    )
    selection.add_argument("--all", action="store_true", help="Run all experiments.")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Write ignored JSON/Markdown diagnostics under reports/generated.",
    )
    args = parser.parse_args()

    selected = EXPERIMENTS if args.all else (args.experiment,)
    results = [RUNNERS[experiment]() for experiment in selected]
    report = render(results)
    print(report)

    if args.refresh:
        output = ROOT / "reports/generated/iris_requirements_closure"
        output.mkdir(parents=True, exist_ok=True)
        (output / "latest.md").write_text(report + "\n", encoding="utf-8")
        payload = {
            "schemaVersion": "IrisRequirementsClosureValidation-v1",
            "results": [
                {
                    **asdict(result),
                    "passed": result.passed,
                }
                for result in results
            ],
        }
        (output / "latest.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
