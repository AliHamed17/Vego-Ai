#!/usr/bin/env python3
"""Build the self-contained thesis evidence-progress explainer."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = (
    ROOT / "docs/research/thesis-evidence/thesis-evidence-snapshot-v1.json"
)
OUTPUT_PATH = ROOT / "VEGO-AI-Thesis-Baseline-Progress.html"


def render(data: dict) -> str:
    embedded = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    generated = html.escape(data["generatedAt"])
    revision = html.escape(data["sourceRevision"][:8])
    evidence = data["evidence"]
    gate = data["labelGate"]
    program = data["programSnapshot"]
    stats = data["statisticalProtocol"]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>VEGO-AI Thesis Evidence Baseline</title>
<style>
:root {{
  --bg:#07111f; --panel:#0d1a2b; --panel2:#11243a; --ink:#edf4ff;
  --muted:#a9bad0; --line:#2b4260; --blue:#55a7ff; --cyan:#56d6d1;
  --green:#68d391; --amber:#f6c85f; --red:#ff7b7b; --violet:#b59cff;
  --shadow:0 18px 55px rgba(0,0,0,.28);
}}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{
  margin:0; background:
  radial-gradient(circle at 15% -5%,rgba(85,167,255,.18),transparent 34rem),
  radial-gradient(circle at 95% 10%,rgba(86,214,209,.11),transparent 28rem),
  var(--bg); color:var(--ink); font-family:Inter,Segoe UI,Arial,sans-serif;
  line-height:1.55;
}}
a {{ color:var(--cyan); }}
button {{ font:inherit; }}
.shell {{ width:min(1180px,calc(100% - 32px)); margin:auto; }}
header {{ padding:46px 0 24px; }}
.eyebrow {{ color:var(--cyan); letter-spacing:.14em; text-transform:uppercase; font-size:.78rem; font-weight:700; }}
h1 {{ margin:.35rem 0 .5rem; max-width:950px; font-size:clamp(2rem,5vw,4rem); line-height:1.03; letter-spacing:-.04em; }}
h2 {{ margin:0 0 .45rem; font-size:clamp(1.35rem,3vw,2rem); line-height:1.15; }}
h3 {{ margin:0 0 .3rem; font-size:1.05rem; }}
p {{ margin:.35rem 0; }}
.lead {{ max-width:900px; color:var(--muted); font-size:clamp(1rem,2vw,1.18rem); }}
.meta {{ display:flex; gap:.55rem; flex-wrap:wrap; margin-top:1.1rem; }}
.badge {{ display:inline-flex; align-items:center; min-height:30px; padding:.25rem .62rem; border:1px solid var(--line); border-radius:999px; color:var(--muted); background:rgba(17,36,58,.72); font-size:.82rem; }}
.badge.stop {{ color:#201500; background:var(--amber); border-color:var(--amber); font-weight:700; }}
.nav {{ position:sticky; top:0; z-index:20; background:rgba(7,17,31,.94); backdrop-filter:blur(15px); border-block:1px solid rgba(43,66,96,.7); }}
.nav .shell {{ display:flex; align-items:center; gap:.65rem; padding:.55rem 0; overflow-x:auto; }}
.nav a {{ white-space:nowrap; color:var(--muted); text-decoration:none; padding:.34rem .55rem; border-radius:.45rem; }}
.nav a:hover,.nav a:focus-visible {{ color:var(--ink); background:var(--panel2); outline:2px solid transparent; }}
.nav button {{ margin-left:auto; border:1px solid var(--line); background:var(--panel2); color:var(--ink); border-radius:.55rem; padding:.42rem .7rem; cursor:pointer; white-space:nowrap; }}
.nav button:focus-visible,.step:focus-visible,.trace-row:focus-visible,.decision:focus-visible,.exp:focus-visible,.risk:focus-visible {{ outline:3px solid var(--cyan); outline-offset:3px; }}
main {{ padding:24px 0 72px; }}
section {{ padding:34px 0; scroll-margin-top:64px; }}
.section-intro {{ color:var(--muted); max-width:850px; margin-bottom:1.2rem; }}
.panel {{ background:linear-gradient(145deg,rgba(17,36,58,.95),rgba(13,26,43,.95)); border:1px solid var(--line); border-radius:18px; box-shadow:var(--shadow); padding:clamp(16px,3vw,28px); }}
.warning {{ border-left:5px solid var(--amber); }}
.warning strong {{ color:var(--amber); }}
.ladder {{ display:grid; grid-template-columns:1fr; gap:18px; align-items:stretch; }}
.ladder > * {{ min-width:0; }}
.steps {{ display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:8px; align-items:stretch; position:relative; min-width:0; }}
.step {{ border:1px solid var(--line); color:var(--ink); background:var(--panel); min-height:150px; min-width:0; border-radius:14px; padding:13px; cursor:pointer; text-align:left; position:relative; overflow-wrap:anywhere; }}
.step::after {{ content:""; position:absolute; top:50%; right:-9px; width:9px; border-top:2px solid var(--line); }}
.step:last-child::after {{ display:none; }}
.step:hover {{ border-color:var(--blue); }}
.step[aria-pressed="true"] {{ border-color:var(--cyan); box-shadow:0 0 0 2px rgba(86,214,209,.2) inset; background:#12314a; }}
.step-id {{ display:block; color:var(--cyan); font-size:.78rem; font-weight:800; letter-spacing:.09em; }}
.step strong {{ display:block; margin:.3rem 0; line-height:1.22; }}
.step small {{ display:block; color:var(--muted); }}
.step.done {{ border-top:4px solid var(--green); }}
.step.human {{ border-top:4px solid var(--amber); }}
.step.blocked {{ border-top:4px solid var(--red); }}
.detail {{ min-height:180px; min-width:0; overflow-wrap:anywhere; }}
.detail .state {{ color:var(--cyan); font-weight:700; }}
.detail dl {{ display:grid; grid-template-columns:105px 1fr; gap:.45rem .7rem; margin:1rem 0 0; }}
.detail dt {{ color:var(--muted); }}
.detail dd {{ margin:0; min-width:0; overflow-wrap:anywhere; }}
.context-line {{ margin-top:10px; color:var(--muted); min-height:1.6em; }}
.is-related {{ border-color:var(--cyan)!important; box-shadow:0 0 0 2px rgba(86,214,209,.18) inset; }}
.flow-grid {{ display:grid; grid-template-columns:repeat(7,minmax(110px,1fr)); gap:8px; align-items:center; }}
.node {{ min-height:118px; padding:14px; border-radius:13px; border:1px solid var(--line); background:var(--panel); }}
.node.base {{ border-top:4px solid var(--blue); }}
.node.human {{ border-top:4px solid var(--amber); }}
.node.memory {{ border-top:4px solid var(--violet); }}
.node.eval {{ border-top:4px solid var(--green); }}
.node strong {{ display:block; line-height:1.2; }}
.node span {{ display:block; margin-top:.35rem; color:var(--muted); font-size:.82rem; }}
.arrow {{ text-align:center; color:var(--cyan); font-size:1.5rem; }}
.no-overwrite {{ margin-top:12px; padding:10px 13px; border:1px dashed var(--red); color:#ffd0d0; border-radius:12px; text-align:center; }}
.grid2 {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:18px; }}
.chart {{ min-height:280px; }}
.chart-title {{ display:flex; justify-content:space-between; gap:12px; align-items:flex-start; margin-bottom:16px; }}
.chart-title small {{ color:var(--muted); text-align:right; }}
.bars {{ display:grid; gap:12px; }}
.bar-row {{ display:grid; grid-template-columns:minmax(130px,.8fr) minmax(120px,2fr) 52px; gap:10px; align-items:center; }}
.track {{ height:18px; background:#07111f; border:1px solid var(--line); border-radius:999px; overflow:hidden; }}
.fill {{ height:100%; min-width:0; border-radius:999px; background:var(--blue); }}
.fill.cyan {{ background:var(--cyan); }} .fill.amber {{ background:var(--amber); }} .fill.violet {{ background:var(--violet); }}
.value {{ text-align:right; font-variant-numeric:tabular-nums; font-weight:700; }}
.caption {{ color:var(--muted); font-size:.82rem; margin-top:14px; }}
.gate-visual {{ display:grid; grid-template-columns:1fr auto 1fr; align-items:center; gap:16px; margin-top:18px; }}
.gate-side {{ padding:18px; border:1px solid var(--line); border-radius:14px; min-height:145px; }}
.gate-side.current {{ border-color:var(--amber); }}
.gate-side.target {{ border-color:var(--green); }}
.gate-arrow {{ font-size:2rem; color:var(--cyan); }}
.big {{ font-size:2.35rem; line-height:1; font-weight:800; }}
.muted {{ color:var(--muted); }}
.compare {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:18px; margin-top:18px; }}
.compare article {{ min-width:0; }}
.compare ul {{ margin:.65rem 0 0; padding-left:1.15rem; }}
.funnel {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin-top:18px; }}
.funnel-stage {{ border:1px solid var(--line); border-top:4px solid var(--amber); border-radius:13px; padding:13px; min-width:0; }}
.funnel-stage:first-child {{ border-top-color:var(--blue); }}
.funnel-stage strong,.funnel-stage span {{ display:block; }}
.funnel-stage strong {{ font-size:1.55rem; }}
.funnel-stage span {{ color:var(--muted); }}
.trace-list {{ display:grid; gap:8px; }}
.trace-row {{ width:100%; display:grid; grid-template-columns:86px minmax(160px,.9fr) minmax(180px,1.4fr) minmax(125px,.8fr); gap:12px; align-items:start; text-align:left; color:var(--ink); background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:13px; cursor:pointer; }}
.trace-row strong {{ color:var(--cyan); }}
.trace-row span {{ min-width:0; overflow-wrap:anywhere; }}
.trace-row small {{ color:var(--muted); }}
.decision-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }}
.decision {{ color:var(--ink); background:var(--panel); border:1px solid var(--line); border-radius:13px; padding:14px; text-align:left; cursor:pointer; min-width:0; }}
.decision strong,.decision span,.decision small {{ display:block; }}
.decision strong {{ color:var(--cyan); }}
.decision span {{ margin:.3rem 0; }}
.decision small {{ color:var(--muted); }}
.roadmap {{ display:grid; grid-template-columns:repeat(9,minmax(105px,1fr)); gap:8px; }}
.exp {{ border:1px solid var(--line); border-radius:13px; padding:12px; min-height:150px; background:var(--panel); color:var(--ink); position:relative; text-align:left; cursor:pointer; }}
.exp::after {{ content:"›"; position:absolute; right:-8px; top:50%; color:var(--cyan); font-size:1.25rem; }}
.exp:last-child::after {{ display:none; }}
.exp .id {{ color:var(--cyan); font-weight:800; font-size:.76rem; }}
.exp strong {{ display:block; margin:.32rem 0; line-height:1.2; }}
.exp small {{ color:var(--muted); }}
.exp.ready {{ border-top:4px solid var(--green); }}
.exp.pending {{ border-top:4px solid var(--amber); }}
.exp.blocked {{ border-top:4px solid var(--red); }}
.risk-path {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; }}
.risk {{ border:1px solid var(--line); border-top:4px solid var(--red); background:var(--panel); color:var(--ink); border-radius:13px; padding:14px; text-align:left; cursor:pointer; min-width:0; }}
.risk strong,.risk span,.risk small {{ display:block; }}
.risk strong {{ color:var(--amber); }}
.risk span {{ margin:.35rem 0; }}
.risk small {{ color:var(--muted); }}
.matrix {{ display:grid; grid-template-columns:145px repeat(2,minmax(120px,1fr)); border:1px solid var(--line); border-radius:12px; overflow:hidden; }}
.matrix div {{ padding:13px; border-right:1px solid var(--line); border-bottom:1px solid var(--line); min-height:52px; }}
.matrix div:nth-child(3n) {{ border-right:0; }}
.matrix .head {{ background:#152942; font-weight:700; }}
.matrix .empty {{ text-align:center; color:var(--amber); font-size:1.25rem; }}
.claims {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; }}
.claim {{ border-top:4px solid var(--line); }}
.claim.safe {{ border-top-color:var(--green); }}
.claim.conditional {{ border-top-color:var(--amber); }}
.claim.no {{ border-top-color:var(--red); }}
.claim ul {{ margin:.65rem 0 0; padding-left:1.15rem; }}
.claim li {{ margin:.36rem 0; }}
footer {{ color:var(--muted); border-top:1px solid var(--line); padding:24px 0 40px; font-size:.84rem; }}
.sr-only {{ position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }}
@media (max-width:980px) {{
  .ladder,.grid2,.compare {{ grid-template-columns:1fr; }}
  .steps {{ grid-template-columns:repeat(3,minmax(0,1fr)); }}
  .step::after {{ display:none; }}
  .flow-grid {{ grid-template-columns:1fr; }}
  .arrow {{ transform:rotate(90deg); }}
  .roadmap {{ grid-template-columns:repeat(3,minmax(0,1fr)); }}
  .decision-grid,.risk-path {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
  .trace-row {{ grid-template-columns:86px minmax(0,1fr); }}
  .trace-row span:nth-child(n+3),.trace-row small {{ grid-column:2; }}
  .exp::after {{ display:none; }}
}}
@media (max-width:620px) {{
  .shell {{ width:min(100% - 20px,1180px); }}
  header {{ padding-top:32px; }}
  .nav .shell {{ padding-inline:0; }}
  .nav button {{ margin-left:0; }}
  .steps,.roadmap,.claims,.decision-grid,.risk-path,.funnel {{ grid-template-columns:1fr; }}
  .step {{ min-height:110px; }}
  .detail dl {{ grid-template-columns:1fr; gap:.08rem; }}
  .detail dd {{ margin-bottom:.55rem; }}
  .bar-row {{ grid-template-columns:1fr 44px; }}
  .track {{ grid-column:1 / -1; grid-row:2; }}
  .gate-visual {{ grid-template-columns:1fr; }}
  .gate-arrow {{ transform:rotate(90deg); text-align:center; }}
  .matrix {{ grid-template-columns:105px repeat(2,minmax(85px,1fr)); font-size:.83rem; }}
  .matrix div {{ padding:9px 6px; }}
}}
@media (prefers-reduced-motion:reduce) {{ html {{ scroll-behavior:auto; }} * {{ transition:none!important; animation:none!important; }} }}
@media print {{
  :root {{ --bg:#fff; --panel:#fff; --panel2:#f4f6f9; --ink:#111; --muted:#444; --line:#999; }}
  body {{ background:#fff; color:#111; }}
  .nav {{ display:none; }} .panel {{ box-shadow:none; break-inside:avoid; }}
  section {{ padding:18px 0; }} .shell {{ width:100%; }}
  .step[aria-pressed="true"] {{ background:#eee; }}
}}
</style>
</head>
<body>
<header class="shell">
  <div class="eyebrow">VEGO-AI · MSc thesis evidence</div>
  <h1>Progress is stronger evidence—not guaranteed accuracy.</h1>
  <p class="lead">The reusable-human-judgment mechanism is implemented and the baseline is preserved. The next empirical step is independent human labeling; all performance fields remain intentionally empty until that gate opens.</p>
  <div class="meta">
    <span class="badge stop">{gate["generalizationSafeLabels"]} / {gate["candidateRows"]} safe labels</span>
    <span class="badge">Iteration {program["latestAcceptedIteration"]} · {html.escape(program["verdict"])} · reliability-only</span>
    <span class="badge">Agent 4 changes: {evidence["memoryInformedChanges"]["value"]} / {evidence["comparisonRows"]["value"]}</span>
    <span class="badge">Revision {revision}</span>
  </div>
</header>
<nav class="nav" aria-label="Page sections">
  <div class="shell">
    <a href="#ladder">B0–B5</a><a href="#architecture">Architecture</a><a href="#evidence">Evidence</a><a href="#traceability">RQ map</a><a href="#decisions">Decisions</a><a href="#roadmap">Experiments</a><a href="#risks">Risks</a><a href="#accuracy">Accuracy gate</a><a href="#claims">Claims</a>
    <button type="button" id="copy-context">Copy evidence context</button>
  </div>
</nav>
<main class="shell">
  <section>
    <div class="panel warning">
      <strong>Research boundary.</strong> Accuracy, macro-F1, net correction, paired significance, generalization, and human-effort reduction are not yet established. No label is inferred or generated by this page.
    </div>
  </section>

  <section id="ladder" aria-labelledby="ladder-title">
    <h2 id="ladder-title">B0–B5: the evidence-maturity ladder</h2>
    <p class="section-intro">Select a stage to see its purpose, gate, and permitted claim. Green stages exist now; amber requires human evidence; red remains blocked or unapproved.</p>
    <div class="ladder">
      <div class="steps" id="baseline-steps" aria-label="Evidence baseline stages"></div>
      <article class="panel detail" id="baseline-detail" aria-live="polite"></article>
    </div>
    <p class="context-line" id="context-detail" aria-live="polite"></p>
  </section>

  <section id="architecture" aria-labelledby="architecture-title">
    <h2 id="architecture-title">The baseline stays visible through the entire flow</h2>
    <p class="section-intro">Human judgment is routed, captured, stored, and retrieved around the original result. The candidate comparison is parallel; there is no direct path back to overwrite Agent 4.</p>
    <div class="panel">
      <div class="flow-grid" role="img" aria-label="Agent 4 baseline flows to review queue, feedback, memory, advisory evidence, parallel comparison, and gated evaluation. No component overwrites Agent 4.">
        <div class="node base"><strong>Agent 4 baseline</strong><span>{evidence["agent4Patterns"]["value"]} frozen pattern classifications</span></div>
        <div class="arrow" aria-hidden="true">→</div>
        <div class="node human"><strong>M1–M2 human review</strong><span>{evidence["reviewItems"]["value"]} queue items; structured decisions</span></div>
        <div class="arrow" aria-hidden="true">→</div>
        <div class="node memory"><strong>M3 judgment memory</strong><span>{evidence["reusableJudgments"]["value"]} reusable same-pattern records</span></div>
        <div class="arrow" aria-hidden="true">→</div>
        <div class="node memory"><strong>M4A advisory evidence</strong><span>{evidence["memoryAdviceItems"]["value"]} advice items; no AI change</span></div>
      </div>
      <div class="flow-grid" style="margin-top:8px" role="img" aria-label="Advisory evidence flows to a parallel comparison, expert labeling gate, and external evaluation.">
        <div class="node eval"><strong>M4B-1 comparison</strong><span>{evidence["comparisonRows"]["value"]} rows; {evidence["memoryInformedChanges"]["value"]} candidate changes</span></div>
        <div class="arrow" aria-hidden="true">→</div>
        <div class="node human"><strong>EXP-019/020 labels</strong><span>Two reviewers and adjudication</span></div>
        <div class="arrow" aria-hidden="true">→</div>
        <div class="node eval"><strong>Development + holdout</strong><span>{gate["developmentRows"]} rows / {gate["sealedHoldoutRows"]} sealed rows</span></div>
        <div class="arrow" aria-hidden="true">→</div>
        <div class="node eval"><strong>External replication</strong><span>Minimum {gate["externalMinimum"]}; target {gate["externalTarget"]}</span></div>
      </div>
      <div class="no-overwrite">✕ No memory, advice, policy, timeout, or evaluation path may overwrite the frozen Agent 4 output.</div>
    </div>
  </section>

  <section id="evidence" aria-labelledby="evidence-title">
    <h2 id="evidence-title">What the current evidence actually contains</h2>
    <p class="section-intro">Counts use different units and are therefore shown as separate profiles, not as an attrition funnel.</p>
    <div class="grid2">
      <figure class="panel chart">
        <div class="chart-title"><h3>Agent 4 class distribution</h3><small>27 baseline patterns</small></div>
        <div class="bars" id="class-bars"></div>
        <figcaption class="caption">Source: frozen Agent 4 output. These are system classifications, not independent expert labels.</figcaption>
      </figure>
      <figure class="panel chart">
        <div class="chart-title"><h3>Mechanism evidence profile</h3><small>Mixed units; values are not additive</small></div>
        <div class="bars" id="mechanism-bars"></div>
        <figcaption class="caption">Queue items, memory records, advice items, and comparison rows have different denominators. No human-effort claim follows from these counts.</figcaption>
      </figure>
    </div>
    <div class="panel gate-visual" role="img" aria-label="Current safe expert labels are {gate["generalizationSafeLabels"]} of {gate["candidateRows"]}. Quantitative MSc evaluation needs at least {gate["quantitativeMinimum"]}. Formal external claim eligibility needs at least {gate["externalMinimum"]} new rows, with a preferred target of {gate["externalTarget"]}.">
      <div class="gate-side current"><div class="big">{gate["generalizationSafeLabels"]} / {gate["candidateRows"]}</div><strong>Current safe labels</strong><p class="muted">Accuracy status: {html.escape(gate["accuracyStatus"])}</p></div>
      <div class="gate-arrow" aria-hidden="true">→</div>
      <div class="gate-side target"><div class="big">{gate["quantitativeMinimum"]} → {gate["sealedHoldoutRows"]} → {gate["externalMinimum"]}+</div><strong>Evidence sequence</strong><p class="muted">MSc minimum → sealed pilot → external formal-claim eligibility (target {gate["externalTarget"]})</p></div>
    </div>
    <div class="funnel" id="label-funnel" aria-label="Independent label gate funnel"></div>
    <div class="compare">
      <article class="panel">
        <h3>Mechanism evidence available now</h3>
        <ul>
          <li>Selective review, structured feedback, reusable memory, advisory retrieval, and parallel comparison execute offline.</li>
          <li>Traceability, provenance, leakage classes, escalation, and baseline preservation are inspectable.</li>
          <li>This evidence supports mechanism readiness—not empirical performance.</li>
        </ul>
      </article>
      <article class="panel">
        <h3>Empirical effect evidence still missing</h3>
        <ul>
          <li id="empirical-label-state"></li>
          <li>Accuracy, macro-F1, net correction, and paired significance remain null.</li>
          <li>Independent review, adjudication, policy freeze, holdout, and external replication remain gated.</li>
        </ul>
      </article>
    </div>
  </section>

  <section id="traceability" aria-labelledby="traceability-title">
    <h2 id="traceability-title">Every research question ends at an evidence gate</h2>
    <p class="section-intro">Select a row to highlight its experiments, chapters, and unresolved supervisor decisions. Status describes the present evidence—not the hoped-for result.</p>
    <div class="trace-list" id="rq-traceability" aria-label="Research question and hypothesis evidence-gap matrix"></div>
  </section>

  <section id="decisions" aria-labelledby="decisions-title">
    <h2 id="decisions-title">Supervisor decisions control which experiments can open</h2>
    <p class="section-intro">Silence is not approval. Every current outcome remains deferred and unconfirmed until explicitly recorded.</p>
    <div class="decision-grid" id="decision-dependencies" aria-label="Supervisor decision to experiment dependencies"></div>
  </section>

  <section id="roadmap" aria-labelledby="roadmap-title">
    <h2 id="roadmap-title">EXP-019–EXP-027: one-way gates with legitimate stop outcomes</h2>
    <p class="section-intro">The roadmap does not presume a candidate policy. It stops if reviewers disagree on the protocol, if development errors are not safely correctable, or if holdout/external evidence is null or harmful.</p>
    <div class="roadmap" id="experiment-roadmap" aria-label="Experiments 19 through 27"></div>
  </section>

  <section id="risks" aria-labelledby="risks-title">
    <h2 id="risks-title">Four gates prevent circular or overfit conclusions</h2>
    <p class="section-intro">Each risk blocks a specific claim until its mitigation is satisfied. Selecting a gate highlights the experiments that carry that safeguard.</p>
    <div class="risk-path" id="risk-path" aria-label="Leakage, small sample, overfitting, and external validity gates"></div>
  </section>

  <section id="accuracy" aria-labelledby="accuracy-title">
    <h2 id="accuracy-title">Paired performance remains blank at safe N=0</h2>
    <p class="section-intro">Dashes mean missing admissible evidence—not zero. They can only be filled from adjudicated, generalization-safe human labels.</p>
    <div class="grid2">
      <div class="panel">
        <h3>Paired correctness matrix</h3>
        <div class="matrix" role="table" aria-label="Paired correctness matrix, not yet computable">
          <div class="head"></div><div class="head">Candidate correct</div><div class="head">Candidate wrong</div>
          <div class="head">Baseline correct</div><div class="empty">—</div><div class="empty">—</div>
          <div class="head">Baseline wrong</div><div class="empty">—</div><div class="empty">—</div>
        </div>
      </div>
      <div class="panel">
        <h3>Preregistered formal gate</h3>
        <ul>
          <li>External adjudicated safe N ≥ {gate["externalMinimum"]}.</li>
          <li>Policy frozen before data inspection.</li>
          <li>{stats["pairedBootstrapReplicates"]:,}-replicate bootstrap interval excludes zero.</li>
          <li>Exact McNemar p &lt; 0.05.</li>
          <li>Macro-F1 non-decline and no predefined subgroup harm.</li>
          <li>Baseline and protected-path hashes unchanged.</li>
        </ul>
      </div>
    </div>
  </section>

  <section id="claims" aria-labelledby="claims-title">
    <h2 id="claims-title">Claim boundary</h2>
    <div class="claims">
      <article class="panel claim safe"><h3>Safe now</h3><ul id="claims-safe"></ul></article>
      <article class="panel claim conditional"><h3>Conditional</h3><ul id="claims-conditional"></ul></article>
      <article class="panel claim no"><h3>Not established</h3><ul id="claims-no"></ul></article>
    </div>
  </section>
</main>
<footer><div class="shell">Generated {generated} · source revision {revision} · self-contained and offline · canonical source: ThesisEvidenceSnapshot-v1</div></footer>
<script id="thesis-data" type="application/json">{embedded}</script>
<script>
(() => {{
  "use strict";
  const data = JSON.parse(document.getElementById("thesis-data").textContent);
  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value).replace(/[&<>"']/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[c]));
  const stateClass = (status) => status === "Implemented" ? "done" : status.includes("Pending") ? "human" : "blocked";
  const intersects = (left, right) => left.some(value => right.includes(value));
  const baselineIdsFor = (experimentIds=[], decisionIds=[]) => data.baselines
    .filter(item => intersects(item.experimentIds,experimentIds) || intersects(item.decisionIds,decisionIds))
    .map(item => item.id);
  function setContextData(element, values) {{
    element.dataset.context = "true";
    element.dataset.baselines = (values.baselineIds || []).join(",");
    element.dataset.experiments = (values.experimentIds || []).join(",");
    element.dataset.chapters = (values.chapterIds || []).join(",");
    element.dataset.decisions = (values.decisionIds || []).join(",");
    element.dataset.research = (values.researchIds || []).join(",");
    element.dataset.risks = (values.riskIds || []).join(",");
  }}
  function applyContext(values, label) {{
    const keys = ["baselines","experiments","chapters","decisions","research","risks"];
    document.querySelectorAll("[data-context]").forEach(element => {{
      const related = keys.some(key => {{
        const selected = values[key] || [];
        const present = (element.dataset[key] || "").split(",").filter(Boolean);
        return selected.length && intersects(selected,present);
      }});
      element.classList.toggle("is-related",related);
    }});
    document.querySelectorAll('[aria-pressed="true"]').forEach(element => element.setAttribute("aria-pressed","false"));
    $("context-detail").textContent = label;
  }}
  function activate(element, values, label, hash, updateHash=true) {{
    applyContext(values,label);
    if (element) element.setAttribute("aria-pressed","true");
    if (!/^B[0-5]$/.test(hash)) {{
      detail.innerHTML = `<span class="state">Selected evidence context</span><h3>${{esc(hash)}}</h3><p>${{esc(label)}}</p>`;
    }}
    if (updateHash) history.replaceState(null,"",`#${{hash}}`);
  }}

  const steps = $("baseline-steps");
  const detail = $("baseline-detail");
  function selectBaseline(id, updateHash=true) {{
    const item = data.baselines.find(x => x.id === id) || data.baselines[0];
    detail.innerHTML = `<span class="state">${{esc(item.status)}}</span><h3>${{esc(item.id)}} · ${{esc(item.name)}}</h3><p>${{esc(item.purpose)}}</p><dl><dt>Data</dt><dd>${{esc(item.data)}}</dd><dt>Policy</dt><dd>${{esc(item.policy)}}</dd><dt>Gate</dt><dd>${{esc(item.evaluationGate)}}</dd><dt>Allowed claim</dt><dd>${{esc(item.allowedClaim)}}</dd></dl>`;
    const context = {{
      baselines:[item.id],
      experiments:item.experimentIds,
      chapters:item.chapterIds,
      decisions:item.decisionIds
    }};
    activate(
      steps.querySelector(`[data-id="${{item.id}}"]`),
      context,
      `${{item.id}} connects to ${{item.experimentIds.join(", ") || "no gated experiment"}}, Chapters ${{item.chapterIds.join(", ")}}, and ${{item.decisionIds.join(", ")}}.`,
      item.id,
      updateHash
    );
  }}
  data.baselines.forEach(item => {{
    const btn = document.createElement("button");
    btn.type = "button"; btn.className = `step ${{stateClass(item.status)}}`;
    btn.dataset.id = item.id; btn.setAttribute("aria-pressed","false");
    setContextData(btn,{{
      baselineIds:[item.id],
      experimentIds:item.experimentIds,
      chapterIds:item.chapterIds,
      decisionIds:item.decisionIds
    }});
    btn.innerHTML = `<span class="step-id">${{esc(item.id)}}</span><strong>${{esc(item.name)}}</strong><small>${{esc(item.status)}}</small>`;
    btn.addEventListener("click", () => selectBaseline(item.id));
    steps.appendChild(btn);
  }});

  function bars(target, values, max, colors) {{
    target.innerHTML = values.map((item,i) => `<div class="bar-row"><span>${{esc(item.label)}}</span><div class="track"><div class="fill ${{colors[i] || ""}}" style="width:${{Math.max(0,Math.min(100,item.value/max*100))}}%"></div></div><span class="value">${{item.value}}</span></div>`).join("");
  }}
  bars($("class-bars"),[
    {{label:"Substantial",value:data.evidence.substantialPatterns.value}},
    {{label:"Occasional",value:data.evidence.occasionalPatterns.value}},
    {{label:"Undetermined",value:data.evidence.undeterminedPatterns.value}}
  ],data.evidence.agent4Patterns.value,["cyan","amber","violet"]);
  bars($("mechanism-bars"),[
    {{label:"Review queue items",value:data.evidence.reviewItems.value}},
    {{label:"Reusable judgments",value:data.evidence.reusableJudgments.value}},
    {{label:"Advice items",value:data.evidence.memoryAdviceItems.value}},
    {{label:"Comparison rows",value:data.evidence.comparisonRows.value}}
  ],data.evidence.comparisonRows.value,["amber","violet","cyan",""]);

  const funnelStages = [
    {{label:"Candidate rows",value:data.labelGate.candidateRows}},
    {{label:"Supplied labels",value:data.labelGate.suppliedLabels}},
    {{label:"Valid labels",value:data.labelGate.validLabels}},
    {{label:"Generalization-safe",value:data.labelGate.generalizationSafeLabels}}
  ];
  $("label-funnel").innerHTML = funnelStages.map(item => `<div class="funnel-stage"><strong>${{item.value}}</strong><span>${{esc(item.label)}}</span></div>`).join("");
  $("empirical-label-state").textContent = `${{data.labelGate.generalizationSafeLabels}} of ${{data.labelGate.candidateRows}} candidate rows currently have admissible labels; status is ${{data.labelGate.accuracyStatus}}.`;

  const traceRoot = $("rq-traceability");
  data.researchFrame.traceability.forEach(item => {{
    const button = document.createElement("button");
    button.type = "button";
    button.className = "trace-row";
    button.dataset.id = item.id;
    button.setAttribute("aria-pressed","false");
    const baselineIds = baselineIdsFor(item.experimentIds,[]);
    setContextData(button,{{
      baselineIds,
      experimentIds:item.experimentIds,
      chapterIds:item.chapterIds,
      decisionIds:item.decisionIds,
      researchIds:[item.id]
    }});
    button.innerHTML = `<strong>${{esc(item.id)}}</strong><span>${{esc(item.metricOrGate)}}</span><span>${{esc(item.experimentIds.join(", "))}} · Chapters ${{esc(item.chapterIds.join(", "))}} · ${{esc(item.decisionIds.join(", "))}}</span><small>${{esc(item.evidenceState)}}</small>`;
    button.addEventListener("click",() => activate(button,{{
      baselines:baselineIds,
      experiments:item.experimentIds,
      chapters:item.chapterIds,
      decisions:item.decisionIds,
      research:[item.id]
    }},`${{item.id}} is ${{item.evidenceState}}; required evidence: ${{item.metricOrGate}}.`,item.id));
    traceRoot.appendChild(button);
  }});

  const decisionRoot = $("decision-dependencies");
  data.decisionDependencies.forEach(item => {{
    const button = document.createElement("button");
    button.type = "button";
    button.className = "decision";
    button.dataset.id = item.id;
    button.setAttribute("aria-pressed","false");
    setContextData(button,{{
      baselineIds:item.baselineIds,
      experimentIds:item.experimentIds,
      decisionIds:[item.id]
    }});
    button.innerHTML = `<strong>${{esc(item.id)}} · ${{esc(item.outcome)}}</strong><span>${{esc(item.title)}}</span><small>Unlocks: ${{esc(item.unlock)}} · ${{esc(item.experimentIds.join(", "))}}</small>`;
    button.addEventListener("click",() => activate(button,{{
      baselines:item.baselineIds,
      experiments:item.experimentIds,
      decisions:[item.id]
    }},`${{item.id}} remains ${{item.outcome}} (${{item.confirmationStatus}}); it controls ${{item.experimentIds.join(", ")}}.`,item.id));
    decisionRoot.appendChild(button);
  }});

  const expClasses = (status) => status === "Evaluation-ready" ? "ready" : status.includes("Pending") ? "pending" : "blocked";
  const roadmapRoot = $("experiment-roadmap");
  data.experiments.forEach(item => {{
    const button = document.createElement("button");
    button.type = "button";
    button.className = `exp ${{expClasses(item.status)}}`;
    button.dataset.id = item.id;
    button.setAttribute("aria-pressed","false");
    const relatedDecisions = data.decisionDependencies.filter(decision => decision.experimentIds.includes(item.id)).map(decision => decision.id);
    const baselineIds = baselineIdsFor([item.id],[]);
    const chapterIds = data.chapterTraceability.filter(chapter => chapter.experiments.includes(item.id)).map(chapter => chapter.chapter);
    const researchIds = data.researchFrame.traceability.filter(row => row.experimentIds.includes(item.id)).map(row => row.id);
    setContextData(button,{{
      baselineIds,
      experimentIds:[item.id],
      chapterIds,
      decisionIds:relatedDecisions,
      researchIds
    }});
    button.innerHTML = `<span class="id">${{esc(item.id)}}</span><strong>${{esc(item.title)}}</strong><small>${{esc(item.status)}}</small>`;
    button.addEventListener("click",() => activate(button,{{
      baselines:baselineIds,
      experiments:[item.id],
      chapters:chapterIds,
      decisions:relatedDecisions,
      research:researchIds
    }},`${{item.id}} is ${{item.status}}; claim boundary: ${{item.claimBoundary}}`,item.id));
    roadmapRoot.appendChild(button);
  }});

  const riskRoot = $("risk-path");
  data.riskGates.forEach(item => {{
    const button = document.createElement("button");
    button.type = "button";
    button.className = "risk";
    button.dataset.id = item.id;
    button.setAttribute("aria-pressed","false");
    const baselineIds = baselineIdsFor(item.experimentIds,[]);
    setContextData(button,{{
      baselineIds,
      experimentIds:item.experimentIds,
      riskIds:[item.id]
    }});
    button.innerHTML = `<strong>${{esc(item.id)}} · ${{esc(item.status)}}</strong><span>${{esc(item.risk)}}</span><small>${{esc(item.mitigation)}} Blocks: ${{esc(item.blockedClaim)}}.</small>`;
    button.addEventListener("click",() => activate(button,{{
      baselines:baselineIds,
      experiments:item.experimentIds,
      risks:[item.id]
    }},`${{item.id}} blocks “${{item.blockedClaim}}” until: ${{item.mitigation}}`,item.id));
    riskRoot.appendChild(button);
  }});

  function routeFromHash(updateHash=false) {{
    const id = location.hash.slice(1);
    if (/^B[0-5]$/.test(id)) return selectBaseline(id,updateHash);
    const selectors = [
      [data.experiments,"#experiment-roadmap","experimentIds","experiments"],
      [data.decisionDependencies,"#decision-dependencies","decisionIds","decisions"],
      [data.researchFrame.traceability,"#rq-traceability","researchIds","research"],
      [data.riskGates,"#risk-path","riskIds","risks"]
    ];
    for (const [collection,rootSelector,dataKey,contextKey] of selectors) {{
      const item = collection.find(entry => entry.id === id);
      if (!item) continue;
      const element = document.querySelector(`${{rootSelector}} [data-id="${{id}}"]`);
      const values = {{
        baselines:(element.dataset.baselines || "").split(",").filter(Boolean),
        experiments:(element.dataset.experiments || "").split(",").filter(Boolean),
        chapters:(element.dataset.chapters || "").split(",").filter(Boolean),
        decisions:(element.dataset.decisions || "").split(",").filter(Boolean),
        research:(element.dataset.research || "").split(",").filter(Boolean),
        risks:(element.dataset.risks || "").split(",").filter(Boolean)
      }};
      activate(element,values,`${{id}} · ${{item.status || item.outcome || item.evidenceState}}`,id,updateHash);
      return;
    }}
    selectBaseline("B0",updateHash);
  }}
  routeFromHash(false);
  window.addEventListener("hashchange",() => routeFromHash(false));

  const list = (id, values) => $(id).innerHTML = values.map(value => `<li>${{esc(value)}}</li>`).join("");
  list("claims-safe",data.claimGates.safeNow);
  list("claims-conditional",data.claimGates.conditionalAfterLabels);
  list("claims-no",data.claimGates.notAllowed);

  $("copy-context").addEventListener("click", async () => {{
    const summary = [
      "VEGO-AI thesis evidence context",
      `Revision: ${{data.sourceRevision}}`,
      `Latest accepted iteration: ${{data.programSnapshot.latestAcceptedIteration}} (${{data.programSnapshot.verdict}})`,
      `Safe labels: ${{data.labelGate.generalizationSafeLabels}}/${{data.labelGate.candidateRows}}`,
      `Accuracy status: ${{data.labelGate.accuracyStatus}}`,
      `Memory-informed changes: ${{data.evidence.memoryInformedChanges.value}}/${{data.evidence.comparisonRows.value}}`,
      "B0-B1 implemented; B2 human-gated; B3-B5 blocked or unapproved.",
      "No accuracy, generalization, reduced-effort, benchmark-superiority, clinical-performance, or automatic-mutation claim."
    ].join("\\n");
    try {{ await navigator.clipboard.writeText(summary); $("copy-context").textContent = "Copied"; setTimeout(() => $("copy-context").textContent = "Copy evidence context",1200); }}
    catch {{ $("copy-context").textContent = "Copy unavailable"; }}
  }});
}})();
</script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    content = render(data).replace("\r\n", "\n")
    if OUTPUT_PATH.exists() and OUTPUT_PATH.read_text(encoding="utf-8").replace(
        "\r\n", "\n"
    ) == content:
        print(f"FRESH: {OUTPUT_PATH.relative_to(ROOT)}")
        return 0
    if args.check:
        print(f"STALE: {OUTPUT_PATH.relative_to(ROOT)}")
        return 1
    OUTPUT_PATH.write_text(content, encoding="utf-8", newline="\n")
    print(f"WROTE: {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
