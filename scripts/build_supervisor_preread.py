#!/usr/bin/env python3
"""Build the July 21 two-page supervisor pre-read and decision worksheet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


INK = colors.HexColor("#0A0A12")
PANEL = colors.HexColor("#F4F2FA")
PURPLE = colors.HexColor("#8B5CF6")
CYAN = colors.HexColor("#06B6D4")
GREEN = colors.HexColor("#10B981")
RED = colors.HexColor("#EF4444")
MUTED = colors.HexColor("#5B6475")
LINE = colors.HexColor("#D9D4E8")
WHITE = colors.white


def ascii_text(value: object) -> str:
    return (
        str(value or "")
        .replace("\u2011", "-")
        .replace("\u2013", "-")
        .replace("\u2014", " - ")
        .replace("\u2212", "-")
        .replace("\u2265", ">=")
        .replace("\u2192", "->")
    )


def load_data(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("docs/research/meetings/2026-07-21-supervisor-package-data-v3.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/pdf/VEGO-AI-Supervisor-PreRead-and-Decision-Worksheet-2026-07-21.pdf"),
    )
    return parser.parse_args()


def page_chrome(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(INK)
    canvas.rect(0, height - 27 * mm, width, 27 * mm, stroke=0, fill=1)
    canvas.setFillColor(PURPLE)
    canvas.rect(17 * mm, height - 27 * mm, 38 * mm, 1.2 * mm, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 15)
    title = "VEGO-AI July 21 Supervisor Pre-read" if doc.page == 1 else "VEGO-AI Decision Worksheet"
    canvas.drawString(17 * mm, height - 15.5 * mm, title)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#C9C3D8"))
    canvas.drawRightString(width - 17 * mm, height - 15.5 * mm, f"Iris + Arnon | Page {doc.page} of 2")
    canvas.setStrokeColor(LINE)
    canvas.line(17 * mm, 13 * mm, width - 17 * mm, 13 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(17 * mm, 8.5 * mm, "Record, working evidence, and decision requests remain separate.")
    canvas.drawRightString(width - 17 * mm, 8.5 * mm, "Generated for 2026-07-21")
    canvas.restoreState()


def build_pdf(data: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    width, height = A4
    frame = Frame(
        17 * mm,
        16 * mm,
        width - 34 * mm,
        height - 48 * mm,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    doc = BaseDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=17 * mm,
        rightMargin=17 * mm,
        topMargin=31 * mm,
        bottomMargin=16 * mm,
        title="VEGO-AI July 21 Supervisor Pre-read and Decision Worksheet",
        author="Ali Hamed",
        subject="July 1 record, July 3-20 progress, and M-01-M-06 decisions",
    )
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=page_chrome)])

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=19,
        textColor=INK,
        spaceAfter=5,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=INK,
        spaceBefore=5,
        spaceAfter=3,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.6,
        leading=11.2,
        textColor=INK,
        alignment=TA_LEFT,
        spaceAfter=3,
    )
    small = ParagraphStyle(
        "Small",
        parent=body,
        fontSize=7.4,
        leading=9.2,
        textColor=MUTED,
        spaceAfter=0,
    )
    table_head = ParagraphStyle(
        "TableHead",
        parent=small,
        fontName="Helvetica-Bold",
        textColor=WHITE,
        fontSize=7.2,
        leading=8.6,
    )
    table_body = ParagraphStyle(
        "TableBody",
        parent=body,
        fontSize=7.1,
        leading=8.8,
        spaceAfter=0,
    )
    table_id = ParagraphStyle(
        "TableId",
        parent=table_body,
        fontName="Helvetica-Bold",
        textColor=PURPLE,
    )
    warning = ParagraphStyle(
        "Warning",
        parent=body,
        fontName="Helvetica-Bold",
        textColor=RED,
        fontSize=8.2,
        leading=10,
        spaceAfter=0,
    )

    story = []
    story.append(Paragraph("What this meeting needs to achieve", h1))
    story.append(
        Paragraph(
            "Confirm or correct the July 1 machine-derived record, review the work produced from July 3-20, "
            "and record explicit outcomes for M-01 through M-06. Silence remains Deferred and unconfirmed.",
            body,
        )
    )

    chronology = Table(
        [
            [Paragraph("1 | JULY 1 RECORD", table_head), Paragraph("2 | JULY 3-20 PROGRESS", table_head), Paragraph("3 | JULY 21 DECISIONS", table_head)],
            [
                Paragraph("D1-D12 are timestamped English paraphrases. Speaker attribution is inferred; selected Hebrew ASR is unreviewed.", table_body),
                Paragraph("Offline architecture, experiments, conformance checks, visualizations, and a protected evaluation gate were produced.", table_body),
                Paragraph("M-01-M-06 remain Not recorded. No architecture, routing, verifier, authority, or live-hook default is approved.", table_body),
            ],
        ],
        colWidths=[58 * mm, 58 * mm, 58 * mm],
    )
    chronology.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("BACKGROUND", (0, 1), (-1, 1), PANEL),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.extend([Spacer(1, 4), chronology, Spacer(1, 6)])

    status = data["programStatus"]
    accepted = status["latestAcceptedIteration"]
    stats = [
        ("Accepted iteration", f"{accepted['iteration']} | {accepted['verdict']} / reliability-only"),
        ("Replay run", ascii_text(accepted["runId"])),
        ("EXP-005 gate", "24 safe candidates | 0 supplied labels"),
        ("EXP-012", "NOT YET COMPUTABLE"),
        ("Runtime", "Baseline and Agent 4 unchanged"),
        ("Live listener", "Unauthorized"),
    ]
    stat_table = Table(
        [
            [
                [Paragraph(label, small), Paragraph(value, table_body)]
                for label, value in stats[:3]
            ],
            [
                [Paragraph(label, small), Paragraph(value, table_body)]
                for label, value in stats[3:]
            ],
        ],
        colWidths=[58 * mm, 58 * mm, 58 * mm],
    )
    stat_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8F7FB")),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([Paragraph("Current evidence boundary", h2), stat_table])

    decision_rows = [[Paragraph("ID", table_head), Paragraph("Decision requested", table_head), Paragraph("Provisional recommendation", table_head)]]
    for decision in data["decisions"]:
        decision_rows.append(
            [
                Paragraph(ascii_text(decision["id"]), table_id),
                Paragraph(ascii_text(decision["request"]["en"]), table_body),
                Paragraph(ascii_text(decision["recommendation"]["en"]), table_body),
            ]
        )
    decision_table = Table(decision_rows, colWidths=[13 * mm, 78 * mm, 83 * mm], repeatRows=1)
    decision_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PANEL]),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.extend([Paragraph("Six decisions for the discussion", h2), decision_table, Spacer(1, 5)])
    story.append(
        Paragraph(
            "Claim boundary: this package demonstrates mechanism readiness, traceability, baseline protection, and evaluation readiness. "
            "It does not establish improved accuracy, generalization, benchmark superiority, reduced human effort at scale, or clinical performance.",
            warning,
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("Record each outcome explicitly", h1))
    story.append(
        Paragraph(
            "Allowed outcomes: Accepted, Accepted with changes, Rejected, or Deferred. "
            "For every decision, capture rationale, approver, owner, due date, constraints, and affected artifacts.",
            body,
        )
    )

    worksheet_rows = [
        [
            Paragraph("ID", table_head),
            Paragraph("Exact decision", table_head),
            Paragraph("Outcome", table_head),
            Paragraph("Rationale / constraints", table_head),
            Paragraph("Owner / due", table_head),
        ]
    ]
    for decision in data["decisions"]:
        request = ascii_text(decision["request"]["en"])
        worksheet_rows.append(
            [
                Paragraph(decision["id"], table_id),
                Paragraph(request, table_body),
                Paragraph("Accepted / Changes / Rejected / Deferred", table_body),
                Paragraph("________________________________<br/>________________________________", table_body),
                Paragraph("______________<br/>______________", table_body),
            ]
        )
    worksheet = Table(
        worksheet_rows,
        colWidths=[12 * mm, 67 * mm, 35 * mm, 42 * mm, 20 * mm],
        rowHeights=[9 * mm] + [24 * mm] * 6,
        repeatRows=1,
    )
    worksheet.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PANEL]),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(worksheet)
    story.append(Spacer(1, 6))

    after_rows = [
        [
            Paragraph("Within the meeting", table_head),
            Paragraph("Within 24 hours", table_head),
            Paragraph("Do not cross", table_head),
        ],
        [
            Paragraph("Read back all six outcomes, approvers, owners, dates, constraints, and affected documents.", table_body),
            Paragraph("Issue corrected minutes; update decision and action registers; regenerate package hashes only where decisions require changes.", table_body),
            Paragraph("Do not mark Approved from silence. Do not alter raw ASR, Agent 4, baseline outputs, EXP-005 labels, or protected runtime paths.", table_body),
        ],
    ]
    after_table = Table(after_rows, colWidths=[58 * mm, 58 * mm, 58 * mm])
    after_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F8F7FB")),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.extend([Paragraph("Read-back and follow-up", h2), after_table])
    doc.build(story)


def main() -> None:
    args = parse_args()
    data = load_data(args.data)
    build_pdf(data, args.output)
    print(args.output.resolve())


if __name__ == "__main__":
    main()
