#!/usr/bin/env python3
"""Build the compact, offline VEGO-AI gallery and research hub."""

from __future__ import annotations

import argparse
import hashlib
import html
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "visualizations-gallery"
GALLERY_OUTPUT = GALLERY / "index.html"
HUB_OUTPUT = ROOT / "VEGO-AI-Research-Hub.html"
DATE = "2026-07-21"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked_paths() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return {line.strip().replace("\\", "/") for line in result.stdout.splitlines()}


def card(href: str, title: str, description: str, badge: str, meta: str = "") -> str:
    return f"""<a class="card" href="{html.escape(href)}">
  <span class="badge">{html.escape(badge)}</span>
  <h3>{html.escape(title)}</h3>
  <p>{html.escape(description)}</p>
  <small>{html.escape(meta or href)}</small>
</a>"""


def image_card(href: str, title: str, description: str, badge: str) -> str:
    return f"""<a class="visual" href="{html.escape(href)}">
  <img loading="lazy" src="{html.escape(href)}" alt="{html.escape(title)}">
  <span class="badge">{html.escape(badge)}</span>
  <h3>{html.escape(title)}</h3>
  <p>{html.escape(description)}</p>
</a>"""


SHELL = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#07131a;--surface:#10232b;--surface2:#153039;--line:#2c4d55;--text:#f4fbfc;--muted:#b8cbd0;--teal:#0f766e;--cyan:#5eead4;--amber:#f59e0b;--red:#ef4444}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:linear-gradient(145deg,#07131a,#0c2028 55%,#07131a);color:var(--text);font-family:Segoe UI,Arial,sans-serif;line-height:1.55}
a{color:inherit}.shell{max-width:1180px;margin:auto;padding:24px}.hero{padding:34px 0 20px}.eyebrow{color:var(--cyan);font-size:.78rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase}
h1{font-size:clamp(2rem,6vw,4rem);line-height:1.02;margin:.3em 0}.lead{max-width:850px;color:var(--muted);font-size:1.05rem}.boundary{border-left:4px solid var(--amber);background:rgba(245,158,11,.08);padding:14px 16px;margin:22px 0}
.status{display:flex;gap:9px;flex-wrap:wrap;margin:18px 0}.pill,.badge{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:4px 9px;font-size:.72rem;font-weight:700}.pill strong{color:var(--cyan)}
nav{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0 30px}nav a{border:1px solid var(--line);border-radius:9px;padding:8px 11px;text-decoration:none;background:var(--surface)}
section{padding:20px 0}h2{margin:0 0 6px;font-size:1.6rem}.section-copy{color:var(--muted);margin:0 0 15px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}.card,.visual{display:block;text-decoration:none;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px;min-width:0}.card:hover,.visual:hover{border-color:var(--cyan)}
.card h3,.visual h3{margin:10px 0 6px;font-size:1rem}.card p,.visual p{color:var(--muted);font-size:.9rem}.card small{color:var(--muted);overflow-wrap:anywhere}.visual img{width:100%;height:190px;object-fit:contain;background:#fff;border-radius:8px}
details{background:rgba(16,35,43,.65);border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin:12px 0}summary{cursor:pointer;font-weight:700;color:var(--cyan)}
.archive-list{columns:3;column-gap:24px;margin-top:12px}.archive-list a{display:block;color:var(--muted);padding:3px 0;overflow-wrap:anywhere}
footer{border-top:1px solid var(--line);color:var(--muted);padding:28px 0;margin-top:24px;font-size:.82rem}
@media(max-width:720px){.shell{padding:15px}.archive-list{columns:1}.visual img{height:auto}nav a{flex:1 1 145px;text-align:center}}
@media(max-width:340px){.grid{grid-template-columns:1fr}.shell{padding:10px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{body{background:#fff;color:#111}.shell{max-width:none}.card,.visual,details{break-inside:avoid;background:#fff;color:#111}.lead,.section-copy,.card p,.visual p,footer{color:#333}nav{display:none}}
</style></head><body><main class="shell">__BODY__</main></body></html>
"""


def build_gallery() -> str:
    tracked = tracked_paths()
    architecture = [
        ("assets/architecture/vego-ai-architecture-enhanced.svg", "Enhanced architecture", "Historical architecture illustration; verify current decisions in the July 21 explainer."),
        ("assets/architecture/vego-ai-architecture-before-after.svg", "Before and after", "Original four-agent flow beside the non-destructive human-judgment extension."),
        ("assets/architecture/vego-ai-architecture-clean.svg", "Original architecture", "Read-only baseline architecture reference."),
    ]
    evidence = [
        ("assets/figures/sd_01_research_spine.svg", "Research spine"),
        ("assets/figures/sd_03_non_destructive_boundary.svg", "Non-destructive boundary"),
        ("assets/figures/sd_04_artifact_chain.svg", "Artifact chain"),
        ("assets/figures/sd_06_validation_gate.svg", "Validation gate"),
        ("assets/figures/sd_F4_review_cases_by_setting.svg", "Review items by setting"),
        ("assets/figures/sd_F5_m4a_advice_strength.svg", "M4A advice subset"),
        ("assets/figures/sd_F6_exp002_label_readiness.svg", "Label readiness"),
        ("assets/figures/sd_F7_claim_boundary.svg", "Claim boundary"),
    ]
    architecture_html = "".join(
        image_card(path, title, description, "Historical visual · mechanism only")
        for path, title, description in architecture
        if f"visualizations-gallery/{path}" in tracked
    )
    evidence_html = "".join(
        image_card(path, title, "Packaged descriptive figure; use the July 21 page for current provenance.", "Descriptive snapshot")
        for path, title in evidence
        if f"visualizations-gallery/{path}" in tracked
    )
    deck_links = "\n".join(
        f'<a href="assets/deck/deck-{index:02d}.jpg">Historical deck frame {index:02d}</a>'
        for index in range(1, 39)
        if f"visualizations-gallery/assets/deck/deck-{index:02d}.jpg" in tracked
    )
    body = f"""<header class="hero">
  <div class="eyebrow">VEGO-AI · offline visualization index · {DATE}</div>
  <h1>See the governed system, then inspect the evidence</h1>
  <p class="lead">The July 21 bilingual explainer is the current presentation entry point. Older diagrams remain available as dated historical illustrations—not as current evidence or supervisor approval.</p>
  <div class="boundary"><strong>Claim boundary:</strong> EXP-005 has 24 candidates and 0 supplied labels; EXP-012 is not computable. Agent 4 and the baseline remain unchanged. M-01–M-06 are unrecorded.</div>
  <div class="status"><span class="pill"><strong>14</strong> accepted iterations</span><span class="pill"><strong>19</strong> experiments represented</span><span class="pill"><strong>0/24</strong> supplied labels</span><span class="pill"><strong>Offline</strong> no external runtime</span></div>
</header>
<nav><a href="#current">Current package</a><a href="#architecture">Architecture</a><a href="#evidence">Evidence figures</a><a href="#archive">Historical archive</a></nav>
<section id="current"><h2>Current decision package</h2><p class="section-copy">Use these files for the Iris and Arnon follow-up.</p><div class="grid">
{card("../VEGO-AI-July1-PointByPoint-EN-HE.html", "Interactive EN/HE architecture puzzle", "Six guided pieces plus the complete D1–D12, EXP-000–018, iteration, evidence, and decision reference.", "Featured · July 21")}
{card("../presentations/VEGO-AI-Supervisor-Progress-and-Decisions-2026-07-21.pptx", "23-slide supervisor deck", "Twelve core decision slides and eleven evidence appendices.", "Current deck")}
{card("../docs/research/meetings/2026-07-21-supervisor-package.md", "Auditable package index", "Canonical Markdown entry point for record, decisions, actions, annex, and post-meeting capture.", "Tracked record")}
</div></section>
<section id="architecture"><h2>Architecture views</h2><p class="section-copy">Historical visual references. Current status and authorization always come from the July 21 package.</p><div class="grid">{architecture_html}</div></section>
<section id="evidence"><h2>Evidence and boundary figures</h2><p class="section-copy">Descriptive mechanism snapshots; no accuracy, generalization, or workload-reduction-at-scale conclusion.</p><div class="grid">{evidence_html}</div></section>
<section id="archive"><h2>Historical archive</h2><p class="section-copy">Collapsed by default to keep the mobile page compact.</p>
<details><summary>July 15 and earlier interface examples</summary><div class="grid" style="margin-top:12px">
{card("../VEGO-AI-Agent-Flow.html", "Agent flow example", "Historical interface snapshot; content may predate Iteration 14.", "Historical · do not cite")}
{card("../VEGO-AI-Demo-Flow.html", "Demo flow example", "Historical mechanism illustration; not independent human evidence.", "Historical · do not cite")}
{card("../VEGO-AI-Live-Demo.html", "Live demo example", "Historical interactive example; not a validated performance result.", "Historical · do not cite")}
</div></details>
<details><summary>Historical 38-slide image archive</summary><div class="archive-list">{deck_links}</div></details>
<details><summary>Historical motion asset</summary><p class="section-copy">Controls are user-operated; no autoplay.</p><video controls preload="none" style="max-width:100%;height:auto"><source src="assets/motion/vego-ai-agent-flow.mp4" type="video/mp4">Motion preview unavailable.</video></details>
</section>
<footer>Generated {DATE} from curated repository paths · self-contained runtime · current authority: SupervisorPackageData v3 and ProgramStatusSnapshot v1.</footer>"""
    return SHELL.replace("__TITLE__", "VEGO-AI — Visualization Gallery").replace("__BODY__", body)


def build_hub() -> str:
    body = f"""<header class="hero">
  <div class="eyebrow">VEGO-AI research hub · {DATE}</div>
  <h1>One current route through the research</h1>
  <p class="lead">Start with the July 21 decision package. The framework and offline experiment program are evidence-ready; independent-label evaluation remains stopped.</p>
  <div class="boundary"><strong>Current stop/go state:</strong> 24 generalization-safe candidates, 0 supplied labels, EXP-012 not computable, M-01–M-06 unrecorded, live listener unauthorized, baseline unchanged.</div>
  <div class="status"><span class="pill"><strong>ITER-014</strong> latest accepted</span><span class="pill"><strong>NEUTRAL</strong> reliability-only</span><span class="pill"><strong>EXP-000–018</strong> represented</span><span class="pill"><strong>Draft PR #8</strong> review route</span></div>
</header>
<nav><a href="#meeting">Supervisor meeting</a><a href="#research">Research truth</a><a href="#evaluation">Evaluation gate</a><a href="#archive">Historical material</a></nav>
<section id="meeting"><h2>July 21 supervisor package</h2><p class="section-copy">The common source for Iris and Arnon.</p><div class="grid">
{card("VEGO-AI-July1-PointByPoint-EN-HE.html", "Interactive EN/HE explainer", "Guided puzzle, complete audit reference, evidence plots, and local-only decision capture.", "Featured")}
{card("presentations/VEGO-AI-Supervisor-Progress-and-Decisions-2026-07-21.pptx", "Supervisor decision deck", "Twelve core slides plus eleven appendices, ending with decision read-back.", "23 slides")}
{card("docs/research/meetings/2026-07-21-supervisor-executive-pre-read.md", "Two-page pre-read source", "Progress, boundaries, and six exact decision requests.", "Pre-read")}
{card("docs/research/meetings/2026-07-21-supervisor-package.md", "Package index", "Record, registers, annex, presenter guide, and capture template.", "Audit trail")}
</div></section>
<section id="research"><h2>Research truth</h2><div class="grid">
{card("docs/research/h-layer/program-status-snapshot-v1.json", "ProgramStatusSnapshot v1", "Manifest-backed iteration, experiment, decision, gate, protected-path, and hash state.", "Canonical status")}
{card("docs/research/h-layer/experiment-iteration-ledger.md", "Iteration ledger", "Iterations 1–7 historical/pre-manifest and 8–14 manifest-backed.", "Ledger")}
{card("experiments/registry.md", "Experiment registry", "EXP-000–018 status and evidence classes.", "Registry")}
{card("docs/dashboards/results-dashboard.md", "Results dashboard record", "Descriptive and mechanism state with claim boundaries.", "Dashboard source")}
</div></section>
<section id="evaluation"><h2>Evaluation gate</h2><div class="grid">
{card("docs/research/meetings/2026-07-21-supervisor-decision-register.md", "M-01–M-06 register", "No blank response becomes approval; incomplete entries finalize Deferred/unconfirmed.", "Human decision gate")}
{card("experiments/EXP-005-real-label-accuracy-gate/README.md", "EXP-005 human-label gate", "Independent human input is required; labels are never invented or prefilled.", "0 supplied labels")}
{card("docs/research/meetings/2026-07-21-post-meeting-capture-template.md", "Post-meeting capture", "Outcome, rationale, approver, owner, date, constraints, and affected artifacts.", "Within 24 hours")}
</div></section>
<section id="archive"><h2>Historical material</h2><div class="grid">
{card("visualizations-gallery/index.html", "Visualization gallery", "Compact offline index with current and archived visuals clearly separated.", "Offline")}
{card("docs/research/meetings/2026-07-15-supervisor-meeting-package.md", "July 15 package", "Historical package retained without implying that its decisions were recorded.", "Historical")}
</div></section>
<footer>VEGO-AI Research Hub · generated {DATE} · education remains the MSc empirical scope · MediVARIA remains future-work proposal only.</footer>"""
    return SHELL.replace("__TITLE__", "VEGO-AI — Research Hub").replace("__BODY__", body)


def write_or_check(path: Path, content: str, check: bool) -> bool:
    content = content.rstrip() + "\n"
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            print(f"STALE: {path.relative_to(ROOT)}", file=sys.stderr)
            return False
        return True
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"wrote {path.relative_to(ROOT)} ({sha256(path)})")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    ok = write_or_check(GALLERY_OUTPUT, build_gallery(), args.check)
    ok = write_or_check(HUB_OUTPUT, build_hub(), args.check) and ok
    if args.check and ok:
        print("visualization entry points: PASS")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
