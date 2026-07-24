#!/usr/bin/env python3
"""Build the unified H-layer program overview.

Joins, strictly read-only, the artifacts that already exist into one
machine-readable JSON, one human-readable Markdown page, and one
chart-ready metric-trajectory CSV:

- replay-suite manifest (EXP-006..010, 012) - ``hlayer_suite_manifest.json``
- conformance-suite manifest (EXP-013..018) - ``hlayer_conformance/manifest.json``
- program validation - ``hlayer_program_validation/latest.json``
- validated EXP-005 gate (revalidated through the canonical harness helper)
- supervisor decision snapshot (through the canonical harness helper)
- accepted iteration history - ``hlayer_iterations/iter_*/`` summaries
  (drift-tolerant across the metric-schema versions of iterations 001-013)

The overview NEVER creates evidence: it carries the claim boundary of its
sources and reports gate states verbatim. Outputs land in
``reports/generated/hlayer_program_overview/`` (git-ignored).
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from typing import Any

from hlayer_harness import (
    HarnessError,
    decision_snapshot,
    exp005_gate_sentence,
    experiment_output_dir,
    generated_at,
    load_exp005_gate,
    output_root,
    read_json,
    write_json,
)

OUT = experiment_output_dir("hlayer_program_overview")
CLAIM = (
    "Program status overview only: joins existing offline mechanism/conformance artifacts. "
    "It creates no evidence and authorizes no accuracy, generalization, or clinical claim."
)

# Metric names drifted across iteration schemas; map every known alias to one
# canonical trajectory column. Missing values stay blank, never guessed.
TRAJECTORY_METRICS: dict[str, tuple[str, ...]] = {
    "event_load": ("event_load_vs_every_decision", "load_vs_every_decision"),
    "weighted_coverage": ("weighted_severity_coverage",),
    "high_severity_coverage": ("high_severity_coverage",),
    "efficiency": ("efficiency",),
    "bundled_load": ("bundled_load",),
    "bundled_efficiency": ("bundled_efficiency",),
}
TRAJECTORY_MODES = ("every_decision", "threshold_sev1", "threshold_sev2", "threshold_sev3",
                    "first_n_then_auto", "threshold", "silent")


def optional_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = read_json(path)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def iteration_dirs(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(
        (p for p in root.iterdir() if p.is_dir() and re.fullmatch(r"iter_\d{3}", p.name)),
        key=lambda p: p.name,
    )


def mode_rows(exp007_summary: dict[str, Any]) -> list[dict[str, Any]]:
    results = exp007_summary.get("results")
    if isinstance(results, dict):
        rows = results.get("ALL")
        if isinstance(rows, list):
            return [r for r in rows if isinstance(r, dict)]
        for value in results.values():  # oldest schema: no ALL key
            if isinstance(value, list):
                return [r for r in value if isinstance(r, dict)]
    return []


def first_present(row: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    for name in aliases:
        if name in row and row[name] is not None:
            return row[name]
    return None


def trajectory_rows(iterations_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for it_dir in iteration_dirs(iterations_root):
        summary = optional_json(it_dir / "exp007-summary.json")
        if summary is None:
            continue
        manifest = optional_json(it_dir / "iteration_manifest.json") or {}
        for mode_row in mode_rows(summary):
            mode = str(mode_row.get("mode") or "")
            if mode not in TRAJECTORY_MODES:
                continue
            record: dict[str, Any] = {
                "iteration": it_dir.name,
                "verdict": manifest.get("verdict") or "",
                "mode": mode,
            }
            for column, aliases in TRAJECTORY_METRICS.items():
                value = first_present(mode_row, aliases)
                record[column] = value if isinstance(value, (int, float)) else ""
            rows.append(record)
    return rows


def iteration_records(iterations_root: Path) -> list[dict[str, Any]]:
    records = []
    for it_dir in iteration_dirs(iterations_root):
        manifest = optional_json(it_dir / "iteration_manifest.json")
        records.append(
            {
                "iteration": it_dir.name,
                "has_manifest": manifest is not None,
                "iteration_kind": (manifest or {}).get("iteration_kind"),
                "verdict": (manifest or {}).get("verdict"),
                "hypothesis": (manifest or {}).get("hypothesis"),
                "run_id": (manifest or {}).get("run_id"),
            }
        )
    return records


def suite_section(root: Path) -> dict[str, Any]:
    manifest = optional_json(root / "hlayer_suite_manifest.json")
    if manifest is None:
        return {"present": False}
    return {
        "present": True,
        "run_id": manifest.get("run_id"),
        "generated_at": manifest.get("generated_at"),
        "experiments": [e.get("experiment") for e in manifest.get("experiments", [])
                        if isinstance(e, dict)],
        "normalized_sha256": manifest.get("normalized_sha256"),
        "claim_boundary": manifest.get("claim_boundary"),
    }


def conformance_section(root: Path) -> dict[str, Any]:
    manifest = optional_json(root / "hlayer_conformance" / "manifest.json")
    if manifest is None:
        return {"present": False}
    return {
        "present": True,
        "passed": manifest.get("passed"),
        "run_id": manifest.get("run_id"),
        "suite_version": manifest.get("suite_version"),
        "experiments": [e.get("experiment_id") or e.get("experiment")
                        for e in manifest.get("experiments", []) if isinstance(e, dict)],
        "live_shadow_authorized": manifest.get("live_shadow_authorized"),
        "program_mode": manifest.get("decision_snapshot_program_mode"),
    }


def validation_section(root: Path) -> dict[str, Any]:
    latest = optional_json(root / "hlayer_program_validation" / "latest.json")
    if latest is None:
        return {"present": False}
    return {
        "present": True,
        "status": latest.get("status"),
        "checks_passed": latest.get("checks_passed"),
        "failures": latest.get("failures"),
    }


def fmt(value: Any) -> str:
    return "-" if value in (None, "") else str(value)


# ---------------------------------------------------------------------------
# E8: self-contained offline HTML chart (small multiples, one metric/panel,
# single series threshold_sev2). Palette = reference slot-1 blue, validated
# for light+dark surfaces (see dataviz method); no external libraries.
# ---------------------------------------------------------------------------

CHART_MODE = "threshold_sev2"
PANEL_W, PANEL_H = 320, 170
PLOT = {"left": 46, "right": 10, "top": 14, "bottom": 30}


def _nice_domain(values: list[float]) -> tuple[float, float]:
    lo, hi = min(values), max(values)
    if lo == hi:
        pad = max(abs(hi) * 0.1, 0.05)
        return lo - pad, hi + pad
    pad = (hi - lo) * 0.12
    return lo - pad, hi + pad


def _panel_svg(metric: str, points: list[tuple[str, float | None]]) -> str:
    present = [(i, v) for i, (_, v) in enumerate(points) if isinstance(v, (int, float))]
    if not present:
        return ""
    y0, y1 = _nice_domain([v for _, v in present])
    x_lo, x_hi = PLOT["left"], PANEL_W - PLOT["right"]
    y_lo, y_hi = PANEL_H - PLOT["bottom"], PLOT["top"]
    n = len(points)

    def sx(index: int) -> float:
        return x_lo if n == 1 else x_lo + (x_hi - x_lo) * index / (n - 1)

    def sy(value: float) -> float:
        return y_lo + (y_hi - y_lo) * (value - y0) / (y1 - y0)

    # Polyline segments with gaps where a schema-era lacks the metric.
    segments: list[list[str]] = [[]]
    for index, (_, value) in enumerate(points):
        if isinstance(value, (int, float)):
            segments[-1].append(f"{sx(index):.1f},{sy(value):.1f}")
        elif segments[-1]:
            segments.append([])
    path_lines = "".join(
        f'<polyline points="{" ".join(seg)}" fill="none" stroke="var(--series-1)" '
        'stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
        for seg in segments
        if len(seg) >= 2
    )

    gridlines, ylabels = [], []
    for t in (y0, (y0 + y1) / 2, y1):
        gy = sy(t)
        gridlines.append(
            f'<line x1="{x_lo}" y1="{gy:.1f}" x2="{x_hi}" y2="{gy:.1f}" '
            'stroke="var(--grid)" stroke-width="1"/>'
        )
        ylabels.append(
            f'<text x="{x_lo - 6}" y="{gy + 3.5:.1f}" text-anchor="end" class="tick">{t:.2f}</text>'
        )
    xlabels = [
        f'<text x="{sx(i):.1f}" y="{PANEL_H - 10}" text-anchor="middle" class="tick">'
        f"{label.replace('iter_0', '')}</text>"
        for i, (label, _) in enumerate(points)
        if i % 2 == 0 or i == n - 1
    ]
    dots = "".join(
        f'<g class="pt"><circle cx="{sx(i):.1f}" cy="{sy(v):.1f}" r="3" fill="var(--series-1)"/>'
        f'<circle cx="{sx(i):.1f}" cy="{sy(v):.1f}" r="10" fill="transparent">'
        f"<title>{points[i][0]} - {metric} = {v}</title></circle></g>"
        for i, v in present
    )
    return (
        f'<figure><figcaption>{metric}</figcaption>'
        f'<svg viewBox="0 0 {PANEL_W} {PANEL_H}" role="img" aria-label="{metric} across iterations">'
        f"{''.join(gridlines)}{''.join(ylabels)}{''.join(xlabels)}{path_lines}{dots}</svg></figure>"
    )


def build_html(overview: dict[str, Any], trajectories: list[dict[str, Any]]) -> str:
    ordered = [row for row in trajectories if row["mode"] == CHART_MODE]
    iterations = sorted({row["iteration"] for row in ordered})
    panels = []
    for metric in TRAJECTORY_METRICS:
        by_iter = {row["iteration"]: row.get(metric) for row in ordered}
        points = [
            (it, by_iter.get(it) if isinstance(by_iter.get(it), (int, float)) else None)
            for it in iterations
        ]
        svg = _panel_svg(metric, points)
        if svg:
            panels.append(svg)

    table_head = "".join(f"<th>{metric}</th>" for metric in TRAJECTORY_METRICS)
    table_rows = "".join(
        "<tr><td>{}</td>{}</tr>".format(
            row["iteration"],
            "".join(f"<td>{fmt(row.get(metric))}</td>" for metric in TRAJECTORY_METRICS),
        )
        for row in ordered
    )
    gate = overview["gate_sentence"]
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>H-Layer Program Overview - Metric Trajectories</title>
<style>
.viz-root {{ color-scheme: light; --surface-1:#fcfcfb; --text-primary:#0b0b0b;
  --text-secondary:#52514e; --series-1:#2a78d6; --grid:#e4e3df;
  background:var(--surface-1); color:var(--text-primary);
  font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;
  max-width:1080px; margin:0 auto; padding:24px; }}
@media (prefers-color-scheme: dark) {{
  :root:where(:not([data-theme="light"])) .viz-root {{ color-scheme: dark;
    --surface-1:#1a1a19; --text-primary:#ffffff; --text-secondary:#c3c2b7;
    --series-1:#3987e5; --grid:#3a3936; }} }}
h1 {{ font-size:1.3rem; margin:0 0 4px; }}
p.sub {{ color:var(--text-secondary); margin:0 0 20px; }}
.panels {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:20px; }}
figure {{ margin:0; }} figcaption {{ font-weight:600; margin-bottom:2px; }}
svg {{ width:100%; height:auto; display:block; }}
.tick {{ font-size:10px; fill:var(--text-secondary); }}
.pt:hover circle:first-child {{ r:5; }}
table {{ border-collapse:collapse; margin-top:8px; font-size:12px; }}
td,th {{ border:1px solid var(--grid); padding:3px 8px; text-align:right; }}
th:first-child,td:first-child {{ text-align:left; }}
details {{ margin-top:24px; }}
.boundary {{ border-left:3px solid var(--series-1); padding:6px 10px; margin:16px 0;
  color:var(--text-secondary); }}
</style></head>
<body class="viz-root">
<h1>H-Layer Metric Trajectories - mode {CHART_MODE}</h1>
<p class="sub">Pooled ALL-settings values per accepted iteration. Generated {overview["generated_at"]}
by scripts/build_hlayer_program_overview.py. Gaps mean the metric did not exist in that iteration's schema.</p>
<div class="boundary">{gate} {CLAIM}</div>
<div class="panels">{''.join(panels)}</div>
<details><summary>Data table ({len(ordered)} rows)</summary>
<table><thead><tr><th>Iteration</th>{table_head}</tr></thead><tbody>{table_rows}</tbody></table>
</details>
</body></html>
"""


def build_markdown(overview: dict[str, Any], trajectories: list[dict[str, Any]]) -> str:
    suite = overview["replay_suite"]
    conf = overview["conformance_suite"]
    val = overview["program_validation"]
    gate = overview["exp005_gate"]
    decisions = overview["decision_snapshot"]
    iterations = overview["iterations"]

    lines = [
        "# H-Layer Program Overview",
        "",
        f"Generated: {overview['generated_at']} (regenerate: `python scripts/build_hlayer_program_overview.py`)",
        "",
        f"Claim scope: {CLAIM}",
        "",
        f"**Gate state:** {overview['gate_sentence']}",
        "",
        "## Program At A Glance",
        "",
        "| Area | State |",
        "| --- | --- |",
        f"| Replay suite (EXP-006..010, 012) | {'run ' + fmt(suite.get('run_id')) if suite.get('present') else 'MISSING'} |",
        f"| Conformance suite (EXP-013..018) | {('PASS' if conf.get('passed') else 'FAIL') if conf.get('present') else 'MISSING'} (run {fmt(conf.get('run_id'))}) |",
        f"| Program validation | {fmt(val.get('status')) if val.get('present') else 'MISSING'} ({fmt(val.get('checks_passed'))} checks) |",
        f"| Accepted iterations | {len(iterations)} ({fmt(iterations[-1]['iteration']) if iterations else '-'} latest) |",
        f"| EXP-005 validated safe labels | {fmt(gate.get('counts', {}).get('generalization_safe_valid_label_count'))} |",
        f"| Program mode | {fmt(conf.get('program_mode')) if conf.get('present') else fmt(decisions.get('status'))} |",
        f"| Live shadow authorized | {fmt(conf.get('live_shadow_authorized'))} |",
        "",
        "## Iterations",
        "",
        "| Iteration | Kind | Verdict |",
        "| --- | --- | --- |",
    ]
    for record in iterations:
        lines.append(
            f"| {record['iteration']} | {fmt(record.get('iteration_kind'))} | {fmt(record.get('verdict'))} |"
        )

    lines += [
        "",
        "## Metric Trajectories (threshold_sev2, pooled ALL)",
        "",
        "| Iteration | Event load | Weighted coverage | High-sev coverage | Efficiency | Bundled load | Bundled efficiency |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in trajectories:
        if row["mode"] != "threshold_sev2":
            continue
        lines.append(
            "| {iteration} | {event_load} | {weighted_coverage} | {high_severity_coverage} | "
            "{efficiency} | {bundled_load} | {bundled_efficiency} |".format(
                **{k: fmt(v) for k, v in row.items()}
            )
        )
    lines += [
        "",
        "Full per-mode trajectories: `metric_trajectories.csv` in this directory.",
        "",
        "## Sources",
        "",
        "- `reports/generated/hlayer_suite_manifest.json` (replay suite)",
        "- `reports/generated/hlayer_conformance/manifest.json` (conformance suite)",
        "- `reports/generated/hlayer_program_validation/latest.json` (program validator)",
        "- `reports/generated/hlayer_iterations/iter_*/` (accepted iterations)",
        "- validated EXP-005 gate + supervisor decision snapshot via `hlayer_harness`",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    root = output_root()
    try:
        gate = load_exp005_gate()
        decisions = decision_snapshot()
    except HarnessError as exc:
        print(f"program overview error: {exc}", file=sys.stderr)
        return 2

    iterations_root = root / "hlayer_iterations"
    trajectories = trajectory_rows(iterations_root)
    overview = {
        "schema_version": "1.0",
        "generated_at": generated_at(),
        "claim_scope": CLAIM,
        "gate_sentence": exp005_gate_sentence(gate),
        "replay_suite": suite_section(root),
        "conformance_suite": conformance_section(root),
        "program_validation": validation_section(root),
        "exp005_gate": {"counts": gate.get("counts"), "snapshot_sha256": gate.get("snapshot_sha256")},
        "decision_snapshot": {
            "present": decisions.get("present"),
            "status": decisions.get("status"),
            "offline_only": decisions.get("offline_only"),
        },
        "iterations": iteration_records(iterations_root),
        "trajectory_rows": len(trajectories),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / "program_overview.json", overview)
    columns = ["iteration", "verdict", "mode", *TRAJECTORY_METRICS.keys()]
    with (OUT / "metric_trajectories.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(trajectories)
    (OUT / "program_overview.md").write_text(build_markdown(overview, trajectories), encoding="utf-8")
    (OUT / "program_overview.html").write_text(build_html(overview, trajectories), encoding="utf-8")

    print(
        f"program overview: {len(overview['iterations'])} iterations, "
        f"{overview['trajectory_rows']} trajectory rows, "
        f"replay={'ok' if overview['replay_suite'].get('present') else 'missing'}, "
        f"conformance={'PASS' if overview['conformance_suite'].get('passed') else 'see file'} -> {OUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
