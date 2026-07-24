#!/usr/bin/env python3
"""Create full-resolution QA sheets and structural checks for a rendered thesis."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat
from pypdf import PdfReader


def page_number(path: Path) -> int:
    return int(path.stem.split("-")[-1])


def font(size: int = 22):
    candidate = Path("C:/Windows/Fonts/segoeui.ttf")
    return ImageFont.truetype(str(candidate), size)


def inspect_images(pages: list[Path]) -> tuple[list[dict], list[str]]:
    records = []
    errors = []
    expected_size = None
    for path in pages:
        with Image.open(path) as image:
            rgb = image.convert("RGB")
            if expected_size is None:
                expected_size = rgb.size
            elif rgb.size != expected_size:
                errors.append(
                    f"{path.name}: size {rgb.size} differs from {expected_size}"
                )
            gray = rgb.convert("L")
            stats = ImageStat.Stat(gray)
            blank = stats.stddev[0] < 2
            inverted = ImageChops.invert(gray)
            bbox = inverted.point(lambda value: 255 if value > 12 else 0).getbbox()
            touches_edge = False
            if bbox:
                left, top, right, bottom = bbox
                touches_edge = left <= 2 or top <= 2 or right >= rgb.width - 2 or bottom >= rgb.height - 2
            if blank:
                errors.append(f"{path.name}: appears blank")
            if touches_edge:
                errors.append(f"{path.name}: non-white content touches the page edge")
            records.append(
                {
                    "page": page_number(path),
                    "size": list(rgb.size),
                    "stddev": round(stats.stddev[0], 3),
                    "contentBox": list(bbox) if bbox else None,
                    "blank": blank,
                    "touchesEdge": touches_edge,
                }
            )
    return records, errors


def inspect_pdf(pdf_path: Path) -> tuple[list[dict], list[str]]:
    records = []
    errors = []
    hard_patterns = {
        "markdown_bold": re.compile(r"\*\*"),
        "markdown_link": re.compile(r"\[[^\]]+\]\([^)]+\)"),
        "placeholder": re.compile(r"\b(?:TODO|TBD|PLACEHOLDER|LOREM IPSUM)\b", re.I),
        "internal_uri": re.compile(r"(?:file:///|codex-file-citation|oai-mem-citation)", re.I),
    }
    # A leading hash is valid inside the thesis' code samples and as a literal
    # table header, so record it for manual review without failing the render.
    review_patterns = {
        "leading_hash": re.compile(r"(?m)^#{1,6}(?:\s|$)"),
    }
    pdf = PdfReader(pdf_path)
    for index, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""
        hard_hits = [
            name for name, pattern in hard_patterns.items() if pattern.search(text)
        ]
        review_hits = [
            name for name, pattern in review_patterns.items() if pattern.search(text)
        ]
        if hard_hits:
            errors.append(
                f"page {index}: suspicious text tokens {', '.join(hard_hits)}"
            )
        records.append(
            {
                "page": index,
                "characterCount": len(text),
                "suspiciousTokens": hard_hits,
                "manualReviewTokens": review_hits,
            }
        )
    return records, errors


def create_sheets(pages: list[Path], sheet_dir: Path) -> list[Path]:
    sheet_dir.mkdir(parents=True, exist_ok=True)
    output = []
    label_font = font()
    for start in range(0, len(pages), 4):
        group = pages[start : start + 4]
        with Image.open(group[0]) as sample:
            width, height = sample.size
        gutter = 24
        label_height = 42
        canvas = Image.new(
            "RGB",
            (width * 2 + gutter * 3, (height + label_height) * 2 + gutter * 3),
            "white",
        )
        draw = ImageDraw.Draw(canvas)
        for offset, page_path in enumerate(group):
            row, col = divmod(offset, 2)
            x = gutter + col * (width + gutter)
            y = gutter + row * (height + label_height + gutter)
            draw.text(
                (x, y + 5),
                f"Page {page_number(page_path)}",
                font=label_font,
                fill="black",
            )
            with Image.open(page_path) as image:
                canvas.paste(image.convert("RGB"), (x, y + label_height))
        name = f"sheet-{page_number(group[0]):03d}-{page_number(group[-1]):03d}.png"
        path = sheet_dir / name
        canvas.save(path, optimize=True)
        output.append(path)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("page_dir", type=Path)
    args = parser.parse_args()
    pages = sorted(args.page_dir.glob("page-*.png"), key=page_number)
    if not pages:
        raise SystemExit("no page PNGs found")
    image_records, image_errors = inspect_images(pages)
    pdf_records, pdf_errors = inspect_pdf(args.pdf)
    sheets = create_sheets(pages, args.page_dir / "sheets")
    errors = image_errors + pdf_errors
    report = {
        "status": "PASS" if not errors else "FAIL",
        "pageCount": len(pages),
        "sheetCount": len(sheets),
        "imageChecks": image_records,
        "textChecks": pdf_records,
        "errors": errors,
    }
    report_path = args.page_dir / "qa-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "pageCount", "sheetCount", "errors")}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
