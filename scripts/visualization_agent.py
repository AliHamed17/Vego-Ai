#!/usr/bin/env python3
"""Visualization Agent — deterministic engine.

Role: ONLY produces/refreshes diagrams, graphs, and charts. It is *advised by the orchestrator* through a
task file and *reports back* through a report file. It coordinates the existing generators; it never touches
Agent 4, the baseline, eval_output, policy, schemas, or thesis text, and uses no API/LLM.

Orchestrator -> agent:  reports/generated/visualization_agent/tasks.json
Agent -> orchestrator:  reports/generated/visualization_agent/report.json (+ report.md)

Run:
  python scripts/visualization_agent.py            # fast set (data-driven charts + catalog)
  python scripts/visualization_agent.py --full      # also heavy generators (dashboard, progress viz)
  python scripts/visualization_agent.py --tasks <file>
Always exits 0 (safe to call from the per-prompt refresh hook).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VDIR = ROOT / "reports" / "generated" / "visualization_agent"
TASKS = VDIR / "tasks.json"
REPORT_JSON = VDIR / "report.json"
REPORT_MD = VDIR / "report.md"
CATALOG = ROOT / "docs" / "visualizations" / "catalog.generated.md"

PY = sys.executable
# generator registry: id -> (heavy?, command, requires-exist)
GENERATORS = {
    "evaluation-charts": (False, [PY, "reports/generated/evaluation_comparison/figures/_charts.py"],
                          "reports/generated/evaluation_comparison/evaluation_summary.json"),
    "supervisor-figures": (False, [PY, "artifacts/supervisor_demo_2026-06-17/figures/_make_figs.py"], None),
    "progress-visualizations": (True, ["pwsh", "-NoProfile", "-File", "scripts/build-progress-visualizations.ps1"], None),
    "results-dashboard": (True, [PY, "VEGO-AI/analysis/build_results_dashboard.py", "--root", "VEGO-AI",
                                 "--out", "VEGO-AI/reports/results_dashboard"], None),
}
DEFAULT_FAST = ["evaluation-charts", "supervisor-figures", "catalog"]
CATALOG_DIRS = ["docs", "reports/generated", "artifacts", "thesis", "VEGO-AI/reports"]


def run(cmd, timeout=300):
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        tail = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()
        return r.returncode, (tail[-1] if tail else "")
    except Exception as e:  # noqa: BLE001
        return 1, str(e)[:160]


def build_catalog():
    counts = {"mmd": 0, "svg": 0, "html": 0}
    items = []
    for d in CATALOG_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for ext in counts:
            for p in base.rglob(f"*.{ext}"):
                counts[ext] += 1
                items.append(str(p.relative_to(ROOT)).replace("\\", "/"))
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Visualization Catalog (generated)", "",
             f"Generated: {datetime.now(timezone.utc).isoformat()}", "",
             f"Totals: **{counts['mmd']}** Mermaid · **{counts['svg']}** SVG · **{counts['html']}** HTML.", "",
             "<details><summary>All diagram/graph files</summary>", ""]
    lines += [f"- `{i}`" for i in sorted(items)]
    lines += ["", "</details>"]
    CATALOG.write_text("\n".join(lines), encoding="utf-8")
    return counts, len(items)


def load_tasks(path, full):
    p = Path(path) if path else TASKS
    if p.exists():
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
            ids = [t.get("type") for t in doc.get("tasks", []) if t.get("status", "requested") != "done"]
            ids = [i for i in ids if i] or list(DEFAULT_FAST)
        except Exception:
            ids = list(DEFAULT_FAST)
    else:
        ids = list(DEFAULT_FAST)
    # include heavy generators only when --full or explicitly requested
    if full:
        for g, (heavy, *_rest) in GENERATORS.items():
            if g not in ids:
                ids.append(g)
    if "catalog" not in ids:
        ids.append("catalog")
    return ids


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="also run heavy generators (dashboard, progress viz)")
    ap.add_argument("--tasks", default=None)
    args = ap.parse_args(argv)
    VDIR.mkdir(parents=True, exist_ok=True)

    task_ids = load_tasks(args.tasks, args.full)
    results = []
    for tid in task_ids:
        if tid == "catalog":
            counts, n = build_catalog()
            results.append({"task": "catalog", "status": "done",
                            "detail": f"{n} files (mmd {counts['mmd']}, svg {counts['svg']}, html {counts['html']})"})
            continue
        spec = GENERATORS.get(tid)
        if not spec:
            results.append({"task": tid, "status": "skipped", "detail": "unknown task type"})
            continue
        heavy, cmd, requires = spec
        if heavy and not args.full:
            results.append({"task": tid, "status": "deferred", "detail": "heavy; run with --full or request explicitly"})
            continue
        if requires and not (ROOT / requires).exists():
            results.append({"task": tid, "status": "skipped", "detail": f"missing input {requires}"})
            continue
        rc, tail = run(cmd)
        results.append({"task": tid, "status": "done" if rc == 0 else "failed", "detail": tail[:200]})

    ok = sum(r["status"] == "done" for r in results)
    report = {
        "agent": "visualization-agent",
        "to": "orchestrator",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": f"{ok}/{len(results)} tasks done",
        "boundaries": "viz only; no Agent4/baseline/eval_output/policy/schema/thesis-text/API changes",
        "results": results,
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = ["# Visualization Agent — report to orchestrator", "",
          f"Generated: {report['generated_at']} · {report['summary']}", "",
          "| Task | Status | Detail |", "| --- | --- | --- |"]
    md += [f"| {r['task']} | {r['status']} | {r['detail']} |" for r in results]
    md += ["", f"_Boundaries: {report['boundaries']}._",
           "", "Orchestrator: write next tasks to `reports/generated/visualization_agent/tasks.json` "
           "(schema in `docs/visualizations/README.md`)."]
    REPORT_MD.write_text("\n".join(md), encoding="utf-8")

    # seed/refresh the task inbox so the contract is visible even on first run
    if not TASKS.exists():
        TASKS.write_text(json.dumps({
            "from": "orchestrator", "note": "edit tasks then rerun the visualization agent",
            "generated_at": report["generated_at"],
            "tasks": [{"id": f"VIZ-{i+1:03d}", "type": t, "status": "done"} for i, t in enumerate(task_ids)],
        }, indent=2), encoding="utf-8")

    print(f"[viz-agent] {report['summary']} -> reports/generated/visualization_agent/report.md")
    for r in results:
        print(f"  - {r['task']}: {r['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
