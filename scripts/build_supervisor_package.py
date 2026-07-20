#!/usr/bin/env python3
"""Build the deterministic July 21 supervisor HTML and canonical data.

The tracked base HTML provides the offline UI shell. ``--refresh-data`` lifts
its historical July 15 dataset into SupervisorPackageData v3 and joins the
tracked ProgramStatusSnapshot v1 plus locally accepted manifests. Normal
builds consume only the tracked v3 data, so clone-safe checks do not require
ignored evidence outputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_HTML = ROOT / "docs/research/meetings/2026-07-21-supervisor-explainer.base.html"
DATA_FILE = ROOT / "docs/research/meetings/2026-07-21-supervisor-package-data-v3.json"
OUTPUT_HTML = ROOT / "VEGO-AI-July1-PointByPoint-EN-HE.html"
STATUS_FILE = ROOT / "docs/research/h-layer/program-status-snapshot-v1.json"
MEETING_DIR = ROOT / "docs/research/meetings"
DATA_PATTERN = re.compile(
    r'(<script type="application/json" id="vego-data">)\s*.*?\s*(</script>)',
    re.DOTALL,
)

PACKAGE_DATE = "2026-07-21"
PROGRESS_RANGE = {"en": "July 3–20", "he": "3–20 ביולי"}

STATUS_VOCABULARY = [
    "Implemented",
    "Delivered — provisional",
    "Documented — parked",
    "Offline design",
    "Offline evidence",
    "Synthetic fixture",
    "Evaluation-ready",
    "Pending expert input",
    "Proposal — not approved",
    "Blocked",
    "Confirmed outcome",
]

DIRECTIVE_METADATA: dict[str, dict[str, str]] = {
    "D1": {
        "timestamp": "00:02:38-00:04:24",
        "speaker": "Iris",
        "confidence": "High",
        "classification": "Explicit / paraphrase",
    },
    "D2": {
        "timestamp": "00:02:55-00:03:20",
        "speaker": "Iris, with a brief confirmation from Ali",
        "confidence": "High for instruction; Medium for confirming voice",
        "classification": "Explicit / paraphrase",
    },
    "D3": {
        "timestamp": "00:13:03-00:14:08",
        "speaker": "Iris",
        "confidence": "High",
        "classification": "Explicit / paraphrase",
    },
    "D4": {
        "timestamp": "00:11:13-00:13:09; 00:22:36-00:22:59",
        "speaker": "Iris, with explanatory responses from Ali",
        "confidence": "High",
        "classification": "Explicit / paraphrase",
    },
    "D5": {
        "timestamp": "00:05:35-00:08:15",
        "speaker": "Iris and Ali",
        "confidence": "High",
        "classification": "Explicit / paraphrase",
    },
    "D6": {
        "timestamp": "00:14:08-00:17:29; 00:19:51-00:21:19",
        "speaker": "Arnon and Iris",
        "confidence": "High",
        "classification": "Explicit / paraphrase",
    },
    "D7": {
        "timestamp": "00:15:26-00:15:59",
        "speaker": "Iris",
        "confidence": "High",
        "classification": "Explicit / paraphrase",
    },
    "D8": {
        "timestamp": "00:15:59-00:17:29",
        "speaker": "Iris",
        "confidence": "High",
        "classification": "Explicit requirement / derived implementation",
    },
    "D9": {
        "timestamp": "00:17:29-00:19:48",
        "speaker": "Iris",
        "confidence": "High",
        "classification": "Explicit / paraphrase",
    },
    "D10": {
        "timestamp": "00:05:17-00:05:34; 00:18:38-00:18:57",
        "speaker": "Iris",
        "confidence": "High",
        "classification": "Explicit / paraphrase",
    },
    "D11": {
        "timestamp": "00:21:19-00:22:21; 00:27:30-00:27:57",
        "speaker": "Iris",
        "confidence": "High",
        "classification": "Explicit / paraphrase",
    },
    "D12": {
        "timestamp": "00:23:03-00:27:30; 00:28:42-00:33:57",
        "speaker": "Iris and Arnon, with responses from Ali",
        "confidence": "High for research tasks; Medium for administrative details",
        "classification": "Explicit / paraphrase; future direction only",
    },
}

DIRECTIVE_STATUS = {
    "D1": "Proposal — not approved",
    "D2": "Offline design",
    "D3": "Proposal — not approved",
    "D4": "Documented — parked",
    "D5": "Blocked",
    "D6": "Proposal — not approved",
    "D7": "Offline design",
    "D8": "Proposal — not approved",
    "D9": "Offline evidence",
    "D10": "Proposal — not approved",
    "D11": "Delivered — provisional",
    "D12": "Delivered — provisional",
}

EVENT_NAMES = {
    1: ("Guideline or requirement authored", "נכתבה הנחיה או דרישה"),
    2: ("Question asked", "נשאלה שאלה"),
    3: ("Answer persisted", "תשובה נשמרה"),
    4: ("Case context established", "הקשר מקרה נקבע"),
    5: ("Artifact version produced", "נוצרה גרסת תוצר"),
    6: ("Deviation assessed", "סטייה הוערכה"),
    7: ("Uncertainty recorded", "אי-ודאות תועדה"),
    8: ("Variability pattern produced", "נוצר דפוס שונות"),
    9: ("Human review item created", "נוצר פריט סקירה אנושית"),
    10: ("Human feedback received", "התקבל משוב אנושי"),
    11: ("Verification dialogue recorded", "תועד דיאלוג אימות"),
    12: ("Adjudication outcome recorded", "תועדה תוצאת הכרעה"),
    13: ("Correction proposal created", "נוצרה הצעת תיקון"),
    14: ("Trusted memory committed", "נשמר זיכרון מהימן"),
    15: ("Evaluation event", "אירוע הערכה"),
}

ITERATIONS = [
    {"id": f"ITER-{i:03d}", "number": i, "manifestBacked": False, "verdict": None, "runId": None}
    for i in range(1, 8)
] + [
    {
        "id": "ITER-008",
        "number": 8,
        "manifestBacked": True,
        "verdict": "NEUTRAL",
        "runId": "hlayer-20260710T171143Z-2a66e71a3f",
    },
    {
        "id": "ITER-009",
        "number": 9,
        "manifestBacked": True,
        "verdict": "NEUTRAL",
        "runId": "hlayer-20260710T175523Z-ab5175fd07",
    },
    {
        "id": "ITER-010",
        "number": 10,
        "manifestBacked": True,
        "verdict": "NEUTRAL",
        "runId": "hlayer-20260710T183658Z-9199809f30",
    },
    {
        "id": "ITER-011",
        "number": 11,
        "manifestBacked": True,
        "verdict": "NEUTRAL",
        "runId": "hlayer-20260711T102518Z-1ecc5dc68f",
    },
    {
        "id": "ITER-012",
        "number": 12,
        "manifestBacked": True,
        "verdict": "NEUTRAL",
        "runId": "hlayer-20260711T123453Z-6cca11a0c8",
    },
    {
        "id": "ITER-013",
        "number": 13,
        "manifestBacked": True,
        "verdict": "NEUTRAL",
        "runId": "hlayer-20260711T130619Z-f8a39357da",
    },
    {
        "id": "ITER-014",
        "number": 14,
        "manifestBacked": True,
        "verdict": "NEUTRAL",
        "runId": "hlayer-20260720T173308Z-d79047f5e2",
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def embedded_data(html: str) -> dict[str, Any]:
    match = DATA_PATTERN.search(html)
    if not match:
        raise ValueError(f"Embedded vego-data block not found in {BASE_HTML}")
    payload = html[match.start(1) + len(match.group(1)) : match.start(2)]
    return json.loads(payload)


def bilingual(en: str, he: str) -> dict[str, str]:
    return {"en": en, "he": he}


def full_events() -> list[dict[str, Any]]:
    gaps = {3, 9, 10, 11, 14}
    rows: list[dict[str, Any]] = []
    for number in range(1, 16):
        evaluation_only = number == 15
        rows.append(
            {
                "id": f"E{number}",
                "name": bilingual(*EVENT_NAMES[number]),
                "scope": "evaluation_only" if evaluation_only else "framework_lifecycle",
                "captureStatus": "unobservable" if number in gaps else "reconstructed",
                "eligibleForFrameworkRouting": not evaluation_only,
                "frameworkActionAllowed": False,
                "operationalStatus": (
                    "Documented — parked"
                    if evaluation_only
                    else "Proposal — not approved"
                ),
                "claimBoundary": (
                    "E15 cannot produce a framework action."
                    if evaluation_only
                    else "Offline representation does not authorize a live listener or framework action."
                ),
            }
        )
    return rows


def experiment_prefix() -> list[dict[str, Any]]:
    return [
        {
            "id": "EXP-000",
            "componentId": "C6",
            "group": "governance",
            "status": "parked",
            "statusLabel": bilingual("Documented — parked", "מתועד — מוקפא"),
            "title": bilingual("Metadata and baseline integrity", "שלמות מטא-דאטה ובסיס"),
            "result": bilingual(
                "Historical audit protocol; controlled artifacts remain local.",
                "פרוטוקול ביקורת היסטורי; תוצרים מבוקרים נשארים מקומיים.",
            ),
        },
        {
            "id": "EXP-001",
            "componentId": "C5",
            "group": "mechanism",
            "status": "delivered",
            "statusLabel": bilingual("Implemented", "ממומש"),
            "title": bilingual("Mechanism readiness", "מוכנות מנגנון"),
            "result": bilingual(
                "27 parallel comparison rows; 0 baseline classification changes.",
                "27 שורות השוואה מקבילות; 0 שינויי סיווג בסיס.",
            ),
        },
        {
            "id": "EXP-002",
            "componentId": "C3",
            "group": "evaluation",
            "status": "delivered",
            "statusLabel": bilingual("Evaluation-ready", "מוכן להערכה"),
            "title": bilingual("Expert-labeling package", "חבילת תיוג מומחים"),
            "result": bilingual(
                "Blind materials prepared; human review has not started.",
                "חומרים עיוורים הוכנו; הסקירה האנושית טרם החלה.",
            ),
        },
        {
            "id": "EXP-003",
            "componentId": "C6",
            "group": "evaluation",
            "status": "blocked",
            "statusLabel": bilingual("Pending expert input", "ממתין לקלט מומחה"),
            "title": bilingual("Held-out expert evaluation", "הערכת מומחים held-out"),
            "result": bilingual(
                "Tooling exists; quantitative results require at least 20 safe labels.",
                "קיימים כלים; תוצאות כמותיות דורשות לפחות 20 תוויות בטוחות.",
            ),
        },
        {
            "id": "EXP-004",
            "componentId": "C6",
            "group": "synthetic",
            "status": "synthetic",
            "statusLabel": bilingual("Synthetic fixture", "fixture סינתטי"),
            "title": bilingual("Policy-sensitivity simulation", "סימולציית רגישות מדיניות"),
            "result": bilingual(
                "Synthetic screening only; not independent evidence.",
                "סינון סינתטי בלבד; לא ראיה עצמאית.",
            ),
        },
    ]


def experiment_status_label(item: dict[str, Any]) -> dict[str, str]:
    mapping = {
        "EXP-005": bilingual("Pending expert input", "ממתין לקלט מומחה"),
        "EXP-006": bilingual("Offline evidence", "עדות offline"),
        "EXP-007": bilingual("Offline evidence", "עדות offline"),
        "EXP-008": bilingual("Offline evidence", "עדות offline"),
        "EXP-009": bilingual("Synthetic fixture", "fixture סינתטי"),
        "EXP-010": bilingual("Synthetic fixture", "fixture סינתטי"),
        "EXP-011": bilingual("Documented — parked", "מתועד — מוקפא"),
        "EXP-012": bilingual("Blocked", "חסום"),
        "EXP-013": bilingual("Offline evidence", "עדות offline"),
        "EXP-014": bilingual("Offline evidence", "עדות offline"),
        "EXP-015": bilingual("Offline evidence", "עדות offline"),
        "EXP-016": bilingual("Offline evidence", "עדות offline"),
        "EXP-017": bilingual("Offline evidence", "עדות offline"),
        "EXP-018": bilingual("Offline evidence", "עדות offline"),
    }
    return mapping[item["id"]]


def evidence_records() -> list[dict[str, Any]]:
    common = {
        "observationDate": "2026-07-20",
        "claimBoundary": "Descriptive/offline mechanism evidence only; not an accuracy or generalization result.",
    }
    return [
        {
            "id": "EV-REVIEW-SETTING",
            "value": 11,
            "numerator": 11,
            "denominator": 11,
            "unit": "review items",
            "sourceId": "SRC-REVIEW",
            "evidenceClass": "mechanism evidence",
            **common,
        },
        {
            "id": "EV-AGENT4-DISTRIBUTION",
            "value": 27,
            "numerator": 27,
            "denominator": 27,
            "unit": "Agent 4 patterns",
            "sourceId": "SRC-BASELINE",
            "evidenceClass": "historical baseline",
            **common,
        },
        {
            "id": "EV-M4A-ADVICE",
            "value": 8,
            "numerator": 8,
            "denominator": 8,
            "unit": "advice rows in ucd_ch subset",
            "sourceId": "SRC-MEMORY",
            "evidenceClass": "advisory subset",
            **common,
        },
        {
            "id": "EV-EXP005-CANDIDATES",
            "value": 24,
            "numerator": 24,
            "denominator": 24,
            "unit": "generalization-safe candidate rows",
            "sourceId": "SRC-EXP005",
            "evidenceClass": "evaluation readiness",
            "observationDate": "2026-07-20",
            "claimBoundary": "Zero labels are supplied; no accuracy computation is permitted.",
        },
        {
            "id": "EV-EXP005-LABELS",
            "value": 0,
            "numerator": 0,
            "denominator": 24,
            "unit": "supplied labels",
            "sourceId": "SRC-EXP005",
            "evidenceClass": "human gate",
            "observationDate": "2026-07-20",
            "claimBoundary": "EXP-012 remains NOT YET COMPUTABLE.",
        },
        {
            "id": "EV-EXP006-RECORDS",
            "value": 481,
            "numerator": 481,
            "denominator": 501,
            "unit": "captured/reconstructed contract records",
            "sourceId": "SRC-EXP006",
            "evidenceClass": "offline replay",
            "observationDate": "2026-07-20",
            "claimBoundary": "The remaining 20 are explicit gap records; neither count measures correctness.",
        },
        {
            "id": "EV-EXP006-GAPS",
            "value": 20,
            "numerator": 20,
            "denominator": 501,
            "unit": "explicit unobservable gap records",
            "sourceId": "SRC-EXP006",
            "evidenceClass": "offline replay",
            "observationDate": "2026-07-20",
            "claimBoundary": "Gap visibility does not demonstrate live observability.",
        },
        {
            "id": "EV-EXP007-SEV2-LOAD",
            "value": 0.799,
            "numerator": None,
            "denominator": "all triageable event items",
            "unit": "event-load ratio",
            "sourceId": "SRC-EXP007",
            "evidenceClass": "offline Pareto evidence",
            "observationDate": "2026-07-20",
            "claimBoundary": "threshold_sev2 is a pilot candidate only and retains about 80% load.",
        },
        {
            "id": "EV-EXP007-SEV2-COVERAGE",
            "value": 0.981,
            "numerator": None,
            "denominator": "replay-defined weighted severity mass",
            "unit": "weighted coverage ratio",
            "sourceId": "SRC-EXP007",
            "evidenceClass": "offline Pareto evidence",
            "observationDate": "2026-07-20",
            "claimBoundary": "No tested mode met coverage >=0.8 at load <=0.5.",
        },
        {
            "id": "EV-EXP008-K35",
            "value": 0.85,
            "numerator": None,
            "denominator": 160,
            "unit": "capture ratio over unstable never-reviewed guidelines",
            "sourceId": "SRC-EXP008",
            "evidenceClass": "offline cap sweep",
            "observationDate": "2026-07-20",
            "claimBoundary": "No uniform or adaptive cap is approved.",
        },
    ]


def trajectory_rows() -> list[dict[str, Any]]:
    path = ROOT / "reports/generated/hlayer_program_overview/metric_trajectories.csv"
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return [
            row
            for row in csv.DictReader(handle)
            if row.get("mode") == "threshold_sev2"
        ]


def enrich_sources(data: dict[str, Any], status: dict[str, Any]) -> None:
    existing = {item["id"]: item for item in data["sources"]}
    path_map = {
        "SRC-BASELINE": ROOT / "docs/research/h-layer/phase-0-boundary-record.md",
        "SRC-REVIEW": ROOT / "reports/generated/exp001/exp001_summary.json",
        "SRC-MEMORY": ROOT / "reports/generated/exp001/exp001_summary.json",
        "SRC-EXP006": ROOT / "reports/generated/hlayer_iterations/iter_014/exp006-summary.json",
        "SRC-EXP007": ROOT / "reports/generated/hlayer_iterations/iter_014/exp007-summary.json",
        "SRC-EXP008": ROOT / "reports/generated/hlayer_iterations/iter_014/exp008-summary.json",
        "SRC-EXP005": ROOT / "reports/generated/hlayer_iterations/iter_014/exp005-gate.json",
    }
    for source_id, path in path_map.items():
        existing[source_id]["path"] = path.relative_to(ROOT).as_posix()
        existing[source_id]["sha256"] = sha256(path)
        existing[source_id]["observationDate"] = "2026-07-20"
    additions = [
        {
            "id": "SRC-STATUS",
            "path": "docs/research/h-layer/program-status-snapshot-v1.json",
            "evidenceClass": "tracked status interface",
            "boundary": "joins accepted manifests; creates no evidence",
            "sha256": sha256(STATUS_FILE),
            "observationDate": "2026-07-20",
        },
        {
            "id": "SRC-ITER014",
            "path": "reports/generated/hlayer_iterations/iter_014/iteration_manifest.json",
            "evidenceClass": "accepted reliability manifest",
            "boundary": "NEUTRAL reliability_only; no mechanism-performance claim",
            "sha256": status["sourceHashes"]["iteration14Manifest"],
            "observationDate": "2026-07-20",
        },
        {
            "id": "SRC-CONFORMANCE",
            "path": "reports/generated/hlayer_conformance/manifest.json",
            "evidenceClass": "offline conformance",
            "boundary": "fixtures only; no live authorization",
            "sha256": status["sourceHashes"]["conformanceManifest"],
            "observationDate": "2026-07-20",
        },
        {
            "id": "SRC-DECISIONS",
            "path": "reports/generated/h_layer_decisions/decision_snapshot.json",
            "evidenceClass": "decision snapshot",
            "boundary": "M-01–M-06 effective Deferred and unconfirmed",
            "sha256": status["sourceHashes"]["decisionSnapshot"],
            "observationDate": "2026-07-20",
        },
    ]
    data["sources"] = list(existing.values()) + additions


def build_data() -> dict[str, Any]:
    base = embedded_data(BASE_HTML.read_text(encoding="utf-8"))
    status = read_json(STATUS_FILE)
    data = deepcopy(base)
    data["schemaVersion"] = "SupervisorPackageData-v3"
    data["generatedAt"] = PACKAGE_DATE
    data["meeting"] = {
        "date": PACKAGE_DATE,
        "audience": ["Iris", "Arnon"],
        "presenter": "Ali",
        "timebox": {"presentationMinutes": 20, "discussionMinutes": 20},
        "purpose": "Confirm the July 1 record, review July 3–20 progress, and record M-01–M-06.",
        "outcomeRule": "Silence or an incomplete record finalizes as Deferred with confirmationStatus=unconfirmed.",
    }
    data["statusVocabulary"] = STATUS_VOCABULARY
    data["claimBoundaries"] = [
        "July 1 wording is a machine-derived English paraphrase pending M-01 confirmation.",
        "July 3–20 work is later author work and is not attributed to Iris or Arnon.",
        "No accuracy, generalization, benchmark-superiority, reduced-effort-at-scale, or clinical-performance claim.",
        "Agent 4, protected runtime paths, and baseline eval_output remain unchanged.",
        "EXP-005 has 24 safe candidates and 0 supplied labels; EXP-012 is NOT YET COMPUTABLE.",
        "M-01–M-06 are unrecorded and effective Deferred; no default or live implementation is approved.",
        "Corrections remain proposal-only and require explicit human approval.",
        "MediVARIA is proposal-only future work; education remains the MSc empirical domain.",
    ]
    data["chronology"][1]["date"] = PROGRESS_RANGE
    data["chronology"][1]["detail"] = bilingual(
        "Later authored implementation, manifests, offline replay, synthetic fixtures, and package work.",
        "מימוש מאוחר, manifests, replay offline, fixtures סינתטיים ועבודת חבילה.",
    )
    data["chronology"][2]["date"] = bilingual("July 21", "21 ביולי")
    data["chronology"][2]["title"] = bilingual(
        "Decision request M-01–M-06", "בקשת החלטות M-01–M-06"
    )

    for directive in data["directives"]:
        meta = DIRECTIVE_METADATA[directive["id"]]
        directive.update(
            {
                "timestamp": meta["timestamp"],
                "speakerAttribution": meta["speaker"],
                "attributionConfidence": meta["confidence"],
                "explicitDerivedClass": meta["classification"],
                "englishReviewStatus": "Paraphrase pending participant confirmation",
                "hebrewReviewStatus": "Unreviewed machine ASR; selected evidence only",
                "statusLabel": DIRECTIVE_STATUS[directive["id"]],
                "componentIds": [directive["componentId"]],
                "provenance": [
                    "docs/research/meetings/2026-07-01-supervisor-meeting-iris.md",
                    "docs/research/meetings/2026-07-01-supervisor-evidence-appendix.md",
                ],
                "claimBoundary": "The recorded requirement is not a verified quotation; later implementation details remain separately classified.",
            }
        )

    for action in data["actions"]:
        action.update(
            {
                "origin": "July 1 machine-derived action record; pending M-01",
                "owner": "To be confirmed",
                "dueDate": None,
                "dependency": "M-01" if action["id"] != "J1-A04" else "External administrative response",
                "evidenceLink": "docs/research/meetings/2026-07-01-supervisor-meeting-iris.md",
                "nextCheckpoint": "2026-07-21 supervisor read-back",
            }
        )

    component_statuses = {
        "proposal": "Proposal — not approved",
        "offline": "Offline evidence",
        "blocked": "Blocked",
        "synthetic": "Synthetic fixture",
        "delivered": "Delivered — provisional",
        "parked": "Documented — parked",
    }
    component_links = {
        "C1": {
            "skillGroupIds": ["H1", "H2", "H3"],
            "skillIds": [f"S{i}" for i in range(1, 8)],
            "eventIds": [],
        },
        "C2": {
            "skillGroupIds": ["H1"],
            "skillIds": ["S1", "S2", "S3"],
            "eventIds": [f"E{i}" for i in range(1, 16)],
        },
        "C3": {
            "skillGroupIds": ["H2"],
            "skillIds": ["S4"],
            "eventIds": ["E9", "E10"],
        },
        "C4": {
            "skillGroupIds": ["H2"],
            "skillIds": ["S5"],
            "eventIds": ["E10", "E11"],
        },
        "C5": {
            "skillGroupIds": ["H3"],
            "skillIds": ["S6", "S7"],
            "eventIds": [f"E{i}" for i in range(10, 15)],
        },
        "C6": {
            "skillGroupIds": [],
            "skillIds": [],
            "eventIds": ["E15"],
        },
    }
    for component in data["components"]:
        component["statusLabel"] = component_statuses[component["status"]]
        component.update(component_links[component["id"]])

    data["events"] = full_events()
    data["iterations"] = ITERATIONS
    data["iterationMetricTrajectory"] = trajectory_rows()
    data["evidence"]["exp006"] = [
        {"label": "captured / reconstructed", "he": "נתפס / שוחזר", "value": 481},
        {"label": "explicit gaps", "he": "פערים מפורשים", "value": 20},
        {"label": "early-stage", "he": "שלב מוקדם", "value": 90},
        {"label": "uncertainty marked", "he": "מסומן אי-ודאות", "value": 235},
        {"label": "severity ≥2", "he": "חומרה ≥2", "value": 231},
    ]

    original_experiments = data["experiments"]
    for item in original_experiments:
        item["statusLabel"] = experiment_status_label(item)
        item["evidenceClass"] = (
            "synthetic fixture"
            if item["id"] in {"EXP-009", "EXP-010"}
            else "offline conformance"
            if item["id"] >= "EXP-013"
            else "evaluation gate"
            if item["id"] in {"EXP-005", "EXP-011", "EXP-012"}
            else "offline replay"
        )
        item["claimBoundary"] = "No accuracy, generalization, or live-runtime authorization."
    for item in original_experiments:
        if item["id"] == "EXP-006":
            item["result"] = bilingual(
                "481 captured/reconstructed + 20 explicit gaps = 501 contract records; not correctness evidence.",
                "481 רשומות שנתפסו/שוחזרו + 20 פערים מפורשים = 501 רשומות חוזה; לא ראיית נכונות.",
            )
        if item["id"] == "EXP-012":
            item["result"] = bilingual(
                "Generalization-safe N=0; NOT YET COMPUTABLE.",
                "N בטוח להכללה = 0; עדיין לא ניתן לחישוב.",
            )
    data["experiments"] = experiment_prefix() + original_experiments

    components_by_id = {item["id"]: item for item in data["components"]}
    for directive in data["directives"]:
        component = components_by_id[directive["componentId"]]
        directive["skillGroupIds"] = component["skillGroupIds"]
        directive["skillIds"] = component["skillIds"]
        directive["eventIds"] = component["eventIds"]
        directive["artifactIds"] = component["artifacts"]
        directive["experimentIds"] = component["experiments"]

    data["evidenceRecords"] = evidence_records()
    data["programStatus"] = status
    data["decisionExportSchema"] = {
        "schemaVersion": "MeetingDecisionExport-v1",
        "fields": [
            "ID",
            "selectedValue",
            "decisionDate",
            "outcome",
            "rationale",
            "approver",
            "owner",
            "dueDate",
            "constraints",
            "affectedArtifacts",
            "confirmationStatus",
        ],
        "allowedOutcomes": [
            "Accepted",
            "Accepted with changes",
            "Rejected",
            "Deferred",
        ],
    }
    for decision in data["decisions"]:
        decision.update(
            {
                "selectedValue": None,
                "decisionDate": None,
                "outcome": "Not recorded",
                "rationale": None,
                "approver": None,
                "approverExpected": "Iris and Arnon",
                "owner": None,
                "dueDate": None,
                "constraints": None,
                "affectedArtifacts": [],
                "confirmationStatus": "unconfirmed",
                "statusLabel": "Proposal — not approved",
            }
        )
    enrich_sources(data, status)
    return data


def serialize(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def en(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("en", value.get("label", "")))
    return "" if value is None else str(value)


def md(value: Any) -> str:
    return en(value).replace("|", r"\|").replace("\n", " ").strip()


def markdown_outputs(data: dict[str, Any]) -> dict[Path, str]:
    status = data["programStatus"]
    iteration = status["latestAcceptedIteration"]
    directives = "\n".join(
        "| {id} | {timestamp} | {speaker} | {confidence} | {classification} | {requirement} | {did} | {status} | {next} | {decisions} |".format(
            id=row["id"],
            timestamp=md(row["timestamp"]),
            speaker=md(row["speakerAttribution"]),
            confidence=md(row["attributionConfidence"]),
            classification=md(row["explicitDerivedClass"]),
            requirement=md(row["requirement"]),
            did=md(row["did"]),
            status=md(row["statusLabel"]),
            next=md(row["next"]),
            decisions=md(", ".join(row["decisionIds"])),
        )
        for row in data["directives"]
    )
    record = f"""# July 1 record confirmation and provenance — July 21 package

Status: machine-derived English paraphrases pending M-01 confirmation.

The raw audio and ASR remain local and unchanged. July 3–20 authored work is not attributed to Iris or Arnon. A correction to this record must be captured as a meeting outcome; it must not overwrite the raw ASR.

| ID | Timestamp | Attributed speaker | Confidence | Explicit / derived | July 1 paraphrase | What was produced later | Present status | Next step | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{directives}

## Claim boundary

- No wording above is a verified quotation.
- Stockholm and Belgium remain candidate evaluation sites only.
- March 2027 was an illustrative scenario.
- Observer + Integrator, threshold severity 2, four H-Verify source families, two rounds, and MediVARIA are later proposals—not recorded supervisor approvals.
- No accuracy, generalization, benchmark-superiority, reduced-effort-at-scale, or clinical-performance claim is made.
"""

    decisions = "\n".join(
        "| {id} | {basis} | {timestamp} | {confidence} | {evidence} | {recommendation} | {alternatives} | {request} | Not recorded | — | Iris and Arnon | To be assigned | — | {artifacts} | unconfirmed |".format(
            id=row["id"],
            basis=md(
                ", ".join(
                    directive["id"]
                    for directive in data["directives"]
                    if row["id"] in directive["decisionIds"]
                )
                or "Global"
            ),
            timestamp=md(
                "; ".join(
                    directive["timestamp"]
                    for directive in data["directives"]
                    if row["id"] in directive["decisionIds"]
                )
                or "Derived across D1–D12"
            ),
            confidence="See linked directive record",
            evidence=md(row["blocked"]),
            recommendation=md(row["recommendation"]),
            alternatives="See decision card and presenter guide",
            request=md(row["request"]),
            artifacts=md(
                ", ".join(
                    artifact["id"]
                    for artifact in data["artifacts"]
                    if artifact["componentId"] in row["componentIds"]
                )
            ),
        )
        for row in data["decisions"]
    )
    decision_register = f"""# Supervisor decision register — July 21

Pre-meeting state: M-01–M-06 are not recorded and effective `Deferred / unconfirmed`. Silence never authorizes implementation.

| ID | July 1 basis | Timestamp | Attribution confidence | Post-meeting evidence / dependency | Recommendation | Alternatives | Exact decision requested | Outcome | Rationale | Approver | Owner | Due date | Affected artifacts | Confirmation status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{decisions}

Allowed outcomes: `Accepted`, `Accepted with changes`, `Rejected`, or `Deferred`.
"""

    actions = "\n".join(
        f"| {row['id']} | {md(row['origin'])} | {md(row['owner'])} | — | {md(row['status'])} | {md(row['dependency'])} | {md(row['evidenceLink'])} | {md(row['nextCheckpoint'])} |"
        for row in data["actions"]
    )
    action_register = f"""# Supervisor action register — July 21

| ID | Origin | Owner | Due date | Status | Dependency | Evidence link | Next checkpoint |
| --- | --- | --- | --- | --- | --- | --- | --- |
{actions}

Owners and dates remain unconfirmed until the meeting read-back.
"""

    exp_rows = "\n".join(
        f"| {row['id']} | {md(row['title'])} | {md(row['statusLabel'])} | {md(row['result'])} | {md(row.get('claimBoundary', 'Mechanism or readiness evidence only.'))} |"
        for row in data["experiments"]
    )
    iter_rows = "\n".join(
        f"| {row['id']} | {'Manifest-backed' if row['manifestBacked'] else 'Historical / pre-manifest'} | {row['runId'] or '—'} | {row['verdict'] or '—'} |"
        for row in data["iterations"]
    )
    annex = f"""# July 3–20 follow-up annex

This annex describes authored work produced after July 1. It does not retroactively attribute proposals or experiment results to Iris or Arnon.

## Authoritative current state

- Latest accepted iteration: **{iteration['iteration']}**.
- Run: `{iteration['runId']}`.
- Verdict: **{iteration['verdict']} / {iteration['iterationKind']}**.
- EXP-005: **24 candidates, 0 supplied labels**.
- EXP-012: **NOT YET COMPUTABLE**.
- M-01–M-06: **unrecorded / effective Deferred**.
- Live shadow listener: **not authorized**.
- Agent 4 and protected baseline: **unchanged**.

## Experiment register

| ID | Question / package | Status | Current result | Claim boundary |
| --- | --- | --- | --- | --- |
{exp_rows}

## Iteration chronology

| Iteration | Evidence class | Run ID | Verdict |
| --- | --- | --- | --- |
{iter_rows}
"""

    preread = f"""# VEGO-AI supervisor pre-read — July 21

Audience: Iris and Arnon
Timebox: 20-minute presentation + 20-minute decision discussion

## Page 1 — What changed since July 1

The July 1 meeting redirected the work to a framework-first H-layer: observe early, route selectively, capture structured human judgment, verify it against deterministic sources, and reuse only verified or adjudicated judgments without changing the Agent 4 baseline.

Progress from July 3–20:

- The July 1 machine-derived record is mapped point-by-point through D1–D12 and J1-A01–J1-A06.
- H1/H2/H3 and S1–S7 are mapped into a contract-driven flow.
- The implemented chain—review queue, stable identity, feedback, memory, advisory retrieval, and parallel comparison—remains non-destructive.
- EXP-006–008 provide offline observability and dosage evidence.
- EXP-009/010 are synthetic rule fixtures only.
- EXP-013–018 provide offline conformance and safety evidence only.
- Iteration {iteration['iteration']} is the latest accepted reliability snapshot with a `{iteration['verdict']}` verdict.
- Agent 4, protected runtime paths, and baseline outputs remain unchanged.

Evidence stop: EXP-005 has 24 prepared candidates and zero supplied independent labels. EXP-012 is not computable. No accuracy or generalization claim is available.

## Page 2 — Decisions requested

1. **M-01 — Record:** accept, correct, qualify, or defer D1–D12 and actions.
2. **M-02 — Architecture:** choose Observer + Integrator, three H-agents, or one modular agent.
3. **M-03 — Observation and dosage:** choose passive scope, active triggers, and uniform versus adaptive limits.
4. **M-04 — H-Verify:** choose deterministic source order, source families, round bound, and adjudication.
5. **M-05 — Authority:** confirm explicit human approval, timeout parking, reviewer roles, and the live-hook authorization boundary.
6. **M-06 — Thesis:** decide when to revise the MSc question and keep MediVARIA as future work only.

For every decision, record outcome, rationale, approver, owner, due date, constraints, and affected artifacts. Incomplete entries finalize as `Deferred / unconfirmed`.
"""

    capture = """# July 21 post-meeting capture template

Meeting: VEGO-AI supervisor follow-up
Participants: Iris, Arnon, Ali
Date: 2026-07-21

## Decision read-back

| ID | Outcome | Selected value | Rationale | Constraints | Approver | Owner | Due date | Affected artifacts | Confirmation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M-01 |  |  |  |  |  |  |  |  |  |
| M-02 |  |  |  |  |  |  |  |  |  |
| M-03 |  |  |  |  |  |  |  |  |  |
| M-04 |  |  |  |  |  |  |  |  |  |
| M-05 |  |  |  |  |  |  |  |  |  |
| M-06 |  |  |  |  |  |  |  |  |  |

Allowed outcomes: Accepted; Accepted with changes; Rejected; Deferred.

## Record corrections

Capture corrections to D1–D12 without editing the raw ASR.

## Within 24 hours

- Issue corrected minutes to Iris and Arnon for confirmation.
- Update decision and action registers.
- Revise provisional specifications only where recorded decisions require it.
- Record implementation-path authorization explicitly.
- Regenerate the package and update hashes.
- Do not mark any deliverable Approved without an explicit confirmed outcome.
"""

    slide_rows = [
        ("1", "Objective and required outcomes", "1:15", "Set the six-decision goal."),
        ("2", "July 1 record requiring confirmation", "1:30", "Ask for corrections, not silent acceptance."),
        ("3", "Framework-first redirect", "1:30", "Anchor the architecture story."),
        ("4", "Framework and evaluation are separate", "1:30", "Keep EXP-005/012 behind the human gate."),
        ("5", "Skills map and prompt requirements", "1:30", "Show H1/H2/H3 and S1–S7."),
        ("6", "Later evidence and its limits", "2:00", "Report mechanism evidence without performance claims."),
        ("7", "M-02 architecture", "1:45", "Record the decomposition choice."),
        ("8", "M-03 observation and dosage", "2:00", "Use the Pareto plot and avoid declaring a default."),
        ("9", "M-04 H-Verify", "1:45", "Confirm deterministic-first verification."),
        ("10", "M-05 authority and implementation boundary", "1:45", "Confirm human approval and timeout parking."),
        ("11", "M-06 thesis and future scope", "1:15", "Keep education empirical; future work is proposal-only."),
        ("12", "Decision read-back", "2:15", "Repeat outcomes, owners, dates, and unresolved items."),
    ]
    presenter_rows = "\n".join(
        f"| {n} | {title} | {time} | {cue} |" for n, title, time, cue in slide_rows
    )
    presenter = f"""# July 21 presenter guide

## Core timing

| Slide | Takeaway | Target | Facilitation cue |
| --- | --- | --- | --- |
{presenter_rows}

Total core time: approximately 20 minutes. Reserve the following 20 minutes for M-01–M-06.

## Non-negotiable wording

- Say “machine-derived paraphrase pending confirmation,” never “verified transcript.”
- Say “offline replay,” “synthetic fixture,” or “offline conformance,” never empirical validation.
- Say “24 candidates and zero supplied labels; not computable,” never accuracy improvement.
- Say “proposal-only,” never approved default, for M-02–M-06 choices.
- Say “Agent 4 and baseline unchanged.”

## Discussion close

Read back each outcome using the allowed vocabulary, then repeat approver, owner, due date, constraints, and affected artifacts. Silence is Deferred.
"""

    package_index = f"""# VEGO-AI July 21 supervisor package

This package connects the July 1 machine-derived record to July 3–20 authored progress and the decisions requested from Iris and Arnon on July 21.

## Current truth

- Latest accepted iteration: **{iteration['iteration']}** (`{iteration['runId']}`).
- Iteration verdict: **{iteration['verdict']} / {iteration['iterationKind']}**.
- M-01–M-06: **not recorded / effective Deferred**.
- EXP-005: **24 candidates, 0 supplied labels**.
- EXP-012: **NOT YET COMPUTABLE**.
- Agent 4 and protected baseline: **unchanged**.

## Package files

| Deliverable | Canonical location |
| --- | --- |
| Interactive bilingual explainer | `VEGO-AI-July1-PointByPoint-EN-HE.html` |
| Supervisor deck | `presentations/VEGO-AI-Supervisor-Progress-and-Decisions-2026-07-21.pptx` |
| Deck PDF | `output/pdf/VEGO-AI-Supervisor-Progress-and-Decisions-2026-07-21.pdf` |
| Two-page pre-read | `output/pdf/VEGO-AI-Supervisor-PreRead-and-Decision-Worksheet-2026-07-21.pdf` |
| Record and provenance | `docs/research/meetings/2026-07-21-supervisor-record-and-provenance.md` |
| Decision register | `docs/research/meetings/2026-07-21-supervisor-decision-register.md` |
| Action register | `docs/research/meetings/2026-07-21-supervisor-action-register.md` |
| Follow-up annex | `docs/research/meetings/2026-07-21-supervisor-follow-up-annex.md` |
| Post-meeting capture | `docs/research/meetings/2026-07-21-post-meeting-capture-template.md` |
| Presenter guide | `docs/research/meetings/2026-07-21-supervisor-presenter-guide.md` |
| SHA-256 manifest | `docs/research/meetings/2026-07-21-supervisor-package-manifest.json` |

## Use order

Read the two-page pre-read, present the 12 core slides, use appendices only when needed, capture M-01–M-06, and run the post-meeting workflow within 24 hours.
"""

    return {
        MEETING_DIR / "2026-07-21-supervisor-record-and-provenance.md": record,
        MEETING_DIR / "2026-07-21-supervisor-decision-register.md": decision_register,
        MEETING_DIR / "2026-07-21-supervisor-action-register.md": action_register,
        MEETING_DIR / "2026-07-21-supervisor-follow-up-annex.md": annex,
        MEETING_DIR / "2026-07-21-supervisor-executive-pre-read.md": preread,
        MEETING_DIR / "2026-07-21-post-meeting-capture-template.md": capture,
        MEETING_DIR / "2026-07-21-supervisor-presenter-guide.md": presenter,
        MEETING_DIR / "2026-07-21-supervisor-package.md": package_index,
    }


def render_html(data: dict[str, Any]) -> str:
    html = BASE_HTML.read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)
    rendered, count = DATA_PATTERN.subn(
        lambda match: f"{match.group(1)}\n{payload}{match.group(2)}",
        html,
        count=1,
    )
    if count != 1:
        raise ValueError("Expected exactly one vego-data replacement")
    return rendered.replace("2026-07-15", PACKAGE_DATE).replace(
        "July 3–14", "July 3–20"
    ).replace("3–14 ביולי", "3–20 ביולי")


def check_equal(path: Path, expected: str) -> bool:
    if not path.is_file():
        print(f"STALE: missing {path.relative_to(ROOT)}", file=sys.stderr)
        return False
    if path.read_text(encoding="utf-8") != expected:
        print(f"STALE: {path.relative_to(ROOT)}", file=sys.stderr)
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refresh-data",
        action="store_true",
        help="Rebuild tracked SupervisorPackageData v3 from accepted local manifests.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the tracked HTML is not the deterministic render of tracked data.",
    )
    args = parser.parse_args()

    if args.refresh_data:
        data = build_data()
        DATA_FILE.write_text(serialize(data), encoding="utf-8", newline="\n")
    else:
        if not DATA_FILE.is_file():
            print(f"Missing canonical data: {DATA_FILE}", file=sys.stderr)
            return 2
        data = read_json(DATA_FILE)

    expected_html = render_html(data)
    expected_markdown = markdown_outputs(data)
    if args.check:
        ok = check_equal(OUTPUT_HTML, expected_html)
        for path, content in expected_markdown.items():
            ok = check_equal(path, content.rstrip() + "\n") and ok
        if ok:
            print("supervisor package: deterministic HTML and Markdown are current")
            return 0
        return 1

    OUTPUT_HTML.write_text(expected_html, encoding="utf-8", newline="\n")
    for path, content in expected_markdown.items():
        path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")
    print(
        f"supervisor package: {data['schemaVersion']} -> "
        f"{OUTPUT_HTML.relative_to(ROOT)} ({len(data['experiments'])} experiments, "
        f"{len(data['iterations'])} iterations)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
