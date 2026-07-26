#!/usr/bin/env python3
"""Build the self-contained bilingual VEGO-AI BigUI research observatory."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "experiment-catalog-snapshot-v1.json"
)
DEFAULT_OUTPUT = ROOT / "VEGO-AI-Research-Hub.html"
DEFAULT_INDEPENDENT_DECISIONS = (
    ROOT / "docs/research/independent-evidence/decision-register.json"
)
INDEPENDENT_DECISION_SCHEMA = (
    ROOT / "schemas/independent-evidence-decision-register-v1.schema.json"
)

TEMPLATE = r"""<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark">
<meta name="description" content="Offline VEGO-AI architecture, experiment, evidence, and validity observatory.">
<title>VEGO-AI BigUI Research Observatory</title>
<style>
:root{
  --bg:#071119;--bg2:#0b1d26;--panel:#102731;--panel2:#15343f;--line:#31515c;
  --text:#f3fbfc;--muted:#b4c8cd;--cyan:#61e6d6;--blue:#67a9ff;--green:#69db9d;
  --amber:#ffc857;--red:#ff7b78;--violet:#c5a3ff;--shadow:0 18px 60px rgba(0,0,0,.27);
  --radius:18px
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:90px}
body{margin:0;background:
  radial-gradient(circle at 8% -5%,rgba(97,230,214,.13),transparent 32rem),
  radial-gradient(circle at 96% 12%,rgba(103,169,255,.14),transparent 34rem),
  var(--bg);color:var(--text);font:15px/1.55 "Segoe UI",Arial,sans-serif}
body[dir="rtl"]{font-family:"Segoe UI",Arial,sans-serif}
a{color:var(--cyan)}
button,input,select{font:inherit}
button,select,input{color:var(--text);background:var(--panel);border:1px solid var(--line)}
button{cursor:pointer}
button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{
  outline:3px solid var(--amber);outline-offset:3px
}
.topbar{position:sticky;top:0;z-index:30;background:rgba(7,17,25,.94);
  backdrop-filter:blur(16px);border-bottom:1px solid var(--line)}
.topbar-inner{width:min(1400px,calc(100% - 28px));margin:auto;display:flex;gap:14px;
  align-items:center;padding:10px 0}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;font-weight:800;white-space:nowrap}
.mark{display:grid;place-items:center;width:34px;height:34px;border-radius:10px;
  color:#041612;background:linear-gradient(135deg,var(--cyan),var(--green));font-weight:900}
.nav{display:flex;gap:6px;overflow:auto;flex:1;padding:3px}
.nav a{flex:0 0 auto;color:var(--muted);text-decoration:none;padding:7px 10px;border-radius:9px}
.nav a:hover{background:var(--panel);color:var(--text)}
.top-actions{display:flex;gap:6px}
.top-actions button{border-radius:10px;padding:7px 10px}
.shell{width:min(1400px,calc(100% - 28px));margin:auto}
.hero{padding:58px 0 30px;display:grid;grid-template-columns:minmax(0,1.45fr) minmax(280px,.55fr);gap:28px;align-items:end}
.eyebrow{color:var(--cyan);font-size:.78rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase}
h1{font-size:clamp(2.35rem,6vw,5.4rem);line-height:.98;letter-spacing:-.055em;margin:.3rem 0 .7rem}
.lead{color:var(--muted);font-size:clamp(1rem,2vw,1.2rem);max-width:920px}
.hero-gate{background:linear-gradient(145deg,rgba(255,200,87,.13),rgba(255,123,120,.06));
  border:1px solid rgba(255,200,87,.45);border-radius:var(--radius);padding:20px;box-shadow:var(--shadow)}
.hero-gate strong{display:block;color:var(--amber);font-size:1.1rem}.hero-gate p{margin:.35rem 0;color:var(--muted)}
.he-summary{display:none;margin-top:.8rem;color:var(--muted)}
body[dir="rtl"] .he-summary{display:block}
.section{padding:38px 0;border-top:1px solid rgba(49,81,92,.7)}
.section-head{display:flex;gap:18px;justify-content:space-between;align-items:end;margin-bottom:18px}
.section-head h2{font-size:clamp(1.55rem,3vw,2.45rem);line-height:1.05;margin:0}
.section-head p{color:var(--muted);max-width:720px;margin:0}
.kpi-grid,.card-grid,.two-col,.three-col{display:grid;gap:14px;min-width:0}
.two-col>*,.three-col>*,.kpi-grid>*{min-width:0;max-width:100%}
.kpi-grid{grid-template-columns:repeat(5,minmax(0,1fr))}
.two-col{grid-template-columns:repeat(2,minmax(0,1fr))}
.three-col{grid-template-columns:repeat(3,minmax(0,1fr))}
.panel,.kpi,.arch-card,.experiment-card,.source-card,.risk-card{
  background:linear-gradient(145deg,rgba(16,39,49,.96),rgba(12,30,39,.96));
  border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);min-width:0
}
.panel{padding:20px;overflow:hidden}.kpi{padding:17px}.kpi .value{font-size:clamp(1.65rem,4vw,2.65rem);font-weight:850;line-height:1}
.kpi .label{color:var(--muted);margin-top:7px}.kpi small{display:block;color:var(--muted);margin-top:8px}
.status-row,.legend,.chips{display:flex;gap:7px;flex-wrap:wrap}
.chip,.status-badge,.evidence-badge{display:inline-flex;align-items:center;min-height:25px;padding:3px 8px;
  border-radius:999px;border:1px solid var(--line);font-size:.74rem;font-weight:750}
.evidence-badge[data-evidence="mechanism"]{color:var(--green)}
.evidence-badge[data-evidence="offline"]{color:var(--blue)}
.evidence-badge[data-evidence="synthetic"]{color:var(--violet)}
.evidence-badge[data-evidence="blocked"]{color:var(--red)}
.evidence-badge[data-evidence="proposal"],.evidence-badge[data-evidence="evaluation_ready"]{color:var(--amber)}
.boundary{border-inline-start:4px solid var(--amber);background:rgba(255,200,87,.08);padding:13px 15px;border-radius:4px 12px 12px 4px}
.system-map{display:grid;grid-template-columns:repeat(8,minmax(115px,1fr));gap:9px;align-items:stretch;overflow:auto;padding:5px}
.system-node{position:relative;display:flex;flex-direction:column;justify-content:center;min-height:118px;padding:13px;
  border:1px solid var(--line);border-radius:14px;background:var(--panel2);text-align:center}
.system-node:not(:last-child)::after{content:"→";position:absolute;inset-inline-end:-15px;top:42%;color:var(--cyan);font-size:1.3rem;z-index:2}
body[dir="rtl"] .system-node:not(:last-child)::after{content:"←"}
.system-node .id{font-weight:900;color:var(--cyan)}.system-node small{color:var(--muted)}
.system-node.baseline{border-color:var(--blue)}.system-node.human{border-color:var(--amber)}
.system-node.parked{border-style:dashed;border-color:var(--violet)}
.blocked-path{margin-top:12px;text-align:center;color:var(--red);font-weight:750}
.runtime-grid,.topology-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.arch-card{padding:16px}.arch-card h3{margin:.4rem 0}.arch-card p{color:var(--muted)}
.arch-card[data-default="true"]{border-color:var(--green)}
.pipeline,.state-machine{display:flex;gap:8px;align-items:stretch;overflow:auto;padding:5px}
.pipeline .step,.state-machine .step{flex:1 0 145px;background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:12px;text-align:center;position:relative}
.pipeline .step:not(:last-child)::after,.state-machine .step:not(:last-child)::after{
  content:"→";position:absolute;inset-inline-end:-12px;top:38%;z-index:2;color:var(--cyan)}
body[dir="rtl"] .pipeline .step:not(:last-child)::after,
body[dir="rtl"] .state-machine .step:not(:last-child)::after{content:"←"}
.pipeline .step.complete{border-color:var(--green);background:rgba(105,219,157,.10)}
.pipeline .step.current{border-color:var(--amber);background:rgba(255,200,87,.10)}
.pipeline .step.sealed{border-style:dashed;color:var(--muted)}
.pipeline .step small{display:block;margin-top:5px;color:var(--muted)}
.metric-bars{display:grid;gap:10px}.metric-bar{display:grid;grid-template-columns:minmax(110px,1fr) 3fr auto;gap:10px;align-items:center}
.bar-track{height:12px;background:#07141b;border-radius:999px;overflow:hidden;border:1px solid var(--line)}
.bar-fill{height:100%;background:linear-gradient(90deg,var(--cyan),var(--blue))}
.metric-meta{margin-top:10px;border-top:1px solid var(--line);padding-top:9px;color:var(--muted);font-size:.78rem}
.filters{display:grid;grid-template-columns:2fr repeat(4,minmax(130px,1fr));gap:9px;margin:14px 0}
.filters label{display:grid;gap:4px;color:var(--muted);font-size:.8rem}.filters input,.filters select{width:100%;padding:9px;border-radius:10px}
.experiment-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.experiment-card{padding:15px;text-align:start;width:100%;color:inherit}
.experiment-card:hover{border-color:var(--cyan);transform:translateY(-1px)}
.experiment-card h3{font-size:1rem;margin:.5rem 0 .3rem}.experiment-card p{color:var(--muted);margin:.25rem 0}
.experiment-card .id{color:var(--cyan);font-weight:850}.experiment-card .next{font-size:.82rem;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.empty{padding:28px;text-align:center;border:1px dashed var(--line);border-radius:14px;color:var(--muted)}
dialog{width:min(900px,calc(100% - 24px));max-height:88vh;color:var(--text);background:var(--bg2);border:1px solid var(--line);
  border-radius:18px;padding:0;box-shadow:var(--shadow)}
dialog::backdrop{background:rgba(0,0,0,.72)}.dialog-head{position:sticky;top:0;background:var(--bg2);padding:16px 20px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:15px;z-index:2}
.dialog-body{padding:20px}.dialog-head h2{margin:0}.dialog-close{border-radius:10px;padding:7px 11px}
.detail-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.detail-block{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px}
.detail-block h3{font-size:.8rem;color:var(--cyan);text-transform:uppercase;letter-spacing:.08em;margin:0 0 5px}.detail-block p,.detail-block ul{margin:.2rem 0;color:var(--muted)}
.chart{min-height:260px}.evidence-bars{display:flex;align-items:end;gap:10px;height:230px;border-bottom:1px solid var(--line);padding:10px}
.evidence-column{flex:1;min-width:60px;display:flex;flex-direction:column;justify-content:end;align-items:center;height:100%;gap:6px}
.evidence-column .bar{width:min(64px,100%);min-height:3px;border-radius:9px 9px 0 0;background:linear-gradient(var(--cyan),var(--blue))}
.evidence-column small{font-size:.7rem;color:var(--muted);text-align:center;overflow-wrap:anywhere}
.timeline{display:flex;gap:10px;overflow-x:auto;overflow-y:hidden;padding:8px 2px;width:100%;max-width:100%;min-width:0;contain:inline-size paint}.timeline-item{flex:0 0 min(245px,calc(100vw - 70px));max-width:calc(100vw - 70px);border:1px solid var(--line);border-radius:13px;padding:12px;background:var(--panel2)}
.timeline-item strong{color:var(--cyan)}.timeline-item small{color:var(--muted);display:block;overflow-wrap:anywhere}
.compare-controls{display:grid;grid-template-columns:1fr 1fr auto;gap:9px}.compare-controls select,.compare-controls button{padding:9px;border-radius:10px}
.compare-verdict{margin-top:14px}.check-table{width:100%;border-collapse:collapse}.check-table th,.check-table td{padding:8px;border-bottom:1px solid var(--line);text-align:start;overflow-wrap:anywhere}
.pass{color:var(--green)}.fail{color:var(--red)}
.funnel{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.funnel-stage{clip-path:polygon(0 0,92% 0,100% 50%,92% 100%,0 100%,8% 50%);
  padding:18px 14px;background:var(--panel2);text-align:center;border:1px solid var(--line)}
.funnel-stage strong{display:block;font-size:1.8rem}.funnel-stage.stop{background:rgba(255,123,120,.14);color:var(--red)}
.result-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.empty-result{padding:18px;border:1px dashed var(--red);border-radius:12px;text-align:center;background:rgba(255,123,120,.05)}
.empty-result strong{display:block;font-size:1.4rem;color:var(--red)}.empty-result span{color:var(--muted)}
.matrix{display:grid;grid-template-columns:130px repeat(2,1fr);gap:6px}.matrix>div{padding:13px;border:1px solid var(--line);border-radius:9px;text-align:center}.matrix .head{background:var(--panel2);font-weight:750}.matrix-empty{color:var(--red);border-style:dashed!important}
.validity-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.risk-card{padding:14px}.risk-card h3{font-size:.95rem;margin:.25rem 0}.risk-card p{color:var(--muted);font-size:.85rem}
.workspace-list,.source-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.workspace-item,.source-card{padding:13px;border:1px solid var(--line);border-radius:12px;background:var(--panel2)}
.workspace-item strong,.source-card strong{color:var(--cyan)}.workspace-item p,.source-card p{color:var(--muted);margin:.25rem 0;overflow-wrap:anywhere}
.workspace-item button{margin-top:6px;padding:6px 9px;border-radius:8px}
.source-card code{display:block;color:var(--muted);overflow-wrap:anywhere;font-size:.72rem}
.run-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.run-card{padding:15px;border:1px solid var(--line);border-radius:14px;background:var(--panel2)}
.run-card strong{color:var(--cyan)}.run-card p{margin:.3rem 0;color:var(--muted)}
.run-card button{margin-top:8px;padding:7px 10px;border-radius:9px}
.metric-table{width:100%;border-collapse:collapse}.metric-table th,.metric-table td{
  padding:8px;border-bottom:1px solid var(--line);text-align:start;vertical-align:top}
.metric-table td{color:var(--muted)}.result-lane{display:grid;gap:14px}
.plot-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.compact-bars{display:grid;gap:8px}.compact-row{display:grid;grid-template-columns:minmax(120px,1fr) 3fr auto;gap:9px;align-items:center}
.compact-row small{color:var(--muted)}.engineering-miss{color:var(--amber)}
.evidence-lanes{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}
.evidence-lane{padding:14px;border:1px solid var(--line);border-radius:14px;background:var(--panel2)}
.evidence-lane strong{display:block;margin:.35rem 0}.evidence-lane p{color:var(--muted);font-size:.82rem;margin:.2rem 0}
.evidence-lane[data-status="demonstrated"]{border-color:var(--green)}
.evidence-lane[data-status="contextual_only"]{border-color:var(--amber)}
.evidence-lane[data-status="not_yet_measurable"]{border-style:dashed;border-color:var(--red)}
.grouped-counts{display:grid;gap:12px}.grouped-count{display:grid;grid-template-columns:minmax(120px,1fr) 3fr;gap:12px;align-items:center}
.dual-bars{display:grid;gap:5px}.dual-bar{display:grid;grid-template-columns:74px 1fr 42px;gap:7px;align-items:center}
.dual-bar small{color:var(--muted)}.dual-bar .paper{background:linear-gradient(90deg,var(--violet),var(--blue))}
.dual-bar .current{background:linear-gradient(90deg,var(--cyan),var(--green))}
.capability-grid{display:grid;grid-template-columns:minmax(180px,2fr) 1fr 1fr;gap:6px}
.capability-grid>div{padding:9px;border-bottom:1px solid var(--line)}.capability-grid .head{color:var(--cyan);font-weight:800}
.capability-yes{color:var(--green);font-weight:800}.capability-no{color:var(--muted)}
.scorecard-table{width:100%;border-collapse:collapse}.scorecard-table th,.scorecard-table td{padding:9px;border-bottom:1px solid var(--line);text-align:start}
.scorecard-table td{color:var(--muted)}.scorecard-table .demonstrated{color:var(--green)}.scorecard-table .not_yet_measurable{color:var(--red)}
.pareto-shell{overflow:auto}.pareto-shell svg{width:100%;min-width:540px;height:auto;display:block}
.plot-axis{stroke:var(--line);stroke-width:1}.plot-gridline{stroke:rgba(180,200,205,.18);stroke-width:1}
.plot-label{fill:var(--muted);font:12px "Segoe UI",Arial,sans-serif}.plot-point{fill:var(--cyan);stroke:#041612;stroke-width:2}
.tradeoff-card{padding:12px;border:1px solid var(--line);border-radius:12px;background:rgba(7,17,25,.35)}
.tradeoff-card h4{margin:.1rem 0 .35rem;color:var(--cyan)}.tradeoff-card p{margin:.2rem 0;color:var(--muted)}
.proof-rule{border:1px solid var(--green);background:rgba(105,219,157,.08);padding:15px;border-radius:14px}
.provenance-note{color:var(--muted);font-size:.8rem;margin-top:12px}
.dimension-map{display:grid;grid-template-columns:repeat(7,minmax(120px,1fr));gap:8px;overflow:auto;padding:4px}
.dimension-node{min-height:118px;padding:12px;border:1px solid var(--line);border-radius:13px;background:var(--panel2)}
.dimension-node strong{display:block;color:var(--cyan);margin-bottom:4px}.dimension-node small{display:block;color:var(--muted)}
.benchmark-bars{display:grid;gap:9px}.benchmark-row{display:grid;grid-template-columns:minmax(150px,1fr) 3fr 52px;gap:9px;align-items:center}
.benchmark-row .track{display:flex;height:13px;background:#07141b;border:1px solid var(--line);border-radius:999px;overflow:hidden}
.benchmark-row .pass-segment{background:var(--green)}.benchmark-row .partial-segment{background:var(--amber)}
.benchmark-row .other-segment{background:var(--line)}
.baseline-ladder{display:grid;grid-template-columns:repeat(6,minmax(150px,1fr));gap:9px;overflow:auto}
.baseline-stage{padding:13px;border:1px solid var(--line);border-radius:13px;background:var(--panel2);min-height:142px}
.baseline-stage strong{display:block;color:var(--cyan);font-size:1.25rem}.baseline-stage span{display:block;margin:.25rem 0;font-weight:750}
.baseline-stage[data-state="not_eligible"],.baseline-stage[data-state="not_started"]{border-style:dashed}
.benchmark-table{width:100%;border-collapse:collapse;min-width:1180px}.benchmark-table th,.benchmark-table td{padding:8px;border-bottom:1px solid var(--line);text-align:start;vertical-align:top}
.benchmark-table tbody tr{cursor:pointer}.benchmark-table tbody tr:hover{background:rgba(97,230,214,.05)}
.dimension-state{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:3px 7px;font-size:.7rem;font-weight:750}
.dimension-state.pass{color:var(--green)}.dimension-state.partial,.dimension-state.not_measured{color:var(--amber)}
.dimension-state.fail,.dimension-state.not_eligible{color:var(--red)}.dimension-state.not_applicable{color:var(--muted)}
.parameter-grid,.comparison-family-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.parameter-card,.comparison-family{padding:12px;border:1px solid var(--line);border-radius:12px;background:var(--panel2)}
.parameter-card summary{cursor:pointer;color:var(--cyan);font-weight:800}.parameter-card p,.comparison-family p{color:var(--muted);margin:.35rem 0}
.comparison-family strong{color:var(--cyan)}.benchmark-link{display:inline-flex;margin-top:12px;padding:8px 11px;border:1px solid var(--cyan);border-radius:10px;text-decoration:none}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
footer{padding:28px 0 45px;border-top:1px solid var(--line);color:var(--muted)}
@media(max-width:1100px){
  .kpi-grid{grid-template-columns:repeat(3,1fr)}.experiment-grid{grid-template-columns:repeat(2,1fr)}
  .evidence-lanes{grid-template-columns:repeat(3,minmax(0,1fr))}
  .dimension-map{grid-template-columns:repeat(4,minmax(145px,1fr))}
  .baseline-ladder{grid-template-columns:repeat(3,minmax(160px,1fr))}
  .filters{grid-template-columns:repeat(3,1fr)}.filters .search{grid-column:span 3}
  .system-map{grid-template-columns:repeat(4,minmax(145px,1fr))}
  .system-node:nth-child(4)::after{display:none}
}
@media(max-width:760px){
  .topbar-inner{align-items:flex-start}.nav{display:none}.brand{flex:1}.hero{grid-template-columns:1fr;padding-top:35px}
  .kpi-grid,.two-col,.three-col,.runtime-grid,.topology-grid,.result-grid,.validity-grid,.run-grid,.plot-grid{grid-template-columns:1fr}
  .evidence-lanes{grid-template-columns:1fr 1fr}.capability-grid{grid-template-columns:minmax(145px,2fr) 1fr 1fr}
  .dimension-map{display:flex;flex-direction:column;overflow:visible}.dimension-node{min-height:auto}
  .baseline-ladder{grid-template-columns:1fr 1fr}.parameter-grid,.comparison-family-grid{grid-template-columns:1fr}
  .experiment-grid{grid-template-columns:1fr}.filters{grid-template-columns:1fr 1fr}.filters .search{grid-column:span 2}
  .system-map{display:flex;flex-direction:column;overflow:visible}.system-node{min-height:88px}
  .system-node:not(:last-child)::after{content:"↓";inset-inline-end:auto;left:50%;top:auto;bottom:-18px}
  body[dir="rtl"] .system-node:not(:last-child)::after{content:"↓"}
  .pipeline,.state-machine{flex-direction:column;overflow:visible}.pipeline .step,.state-machine .step{flex:auto}
  .pipeline .step:not(:last-child)::after,.state-machine .step:not(:last-child)::after{content:"↓";inset-inline-end:auto;left:50%;top:auto;bottom:-15px}
  body[dir="rtl"] .pipeline .step:not(:last-child)::after,body[dir="rtl"] .state-machine .step:not(:last-child)::after{content:"↓"}
  .compare-controls{grid-template-columns:1fr}.funnel{grid-template-columns:1fr}.funnel-stage{clip-path:none;border-radius:12px}
  .matrix{grid-template-columns:90px repeat(2,minmax(0,1fr))}.detail-grid,.workspace-list,.source-grid{grid-template-columns:1fr}
  .section-head{display:block}.section-head p{margin-top:6px}
}
@media(max-width:420px){
  .shell,.topbar-inner{width:min(100% - 18px,1400px)}.top-actions button{padding:6px 8px}
  .brand .brand-text{display:none}.filters{grid-template-columns:1fr}.filters .search{grid-column:auto}
  .kpi-grid{grid-template-columns:1fr 1fr}.metric-bar{grid-template-columns:1fr}.evidence-bars{overflow:auto}
  .evidence-lanes{grid-template-columns:1fr}.grouped-count{grid-template-columns:1fr}.capability-grid{font-size:.78rem}
  .baseline-ladder{grid-template-columns:1fr}.benchmark-row{grid-template-columns:1fr}
}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;transition:none!important;animation:none!important}}
@media print{
  :root{--bg:#fff;--panel:#fff;--panel2:#f4f4f4;--text:#111;--muted:#333;--line:#777;--shadow:none}
  body{background:#fff}.topbar,.top-actions,.filters,.dialog-close,.compare-controls{display:none!important}
  .shell{width:100%}.section{break-before:auto}.panel,.kpi,.arch-card,.experiment-card,.risk-card{break-inside:avoid;box-shadow:none}
  .experiment-grid{grid-template-columns:repeat(2,1fr)}dialog{display:none}.hero{padding-top:15px}
}
</style>
</head>
<body>
<div class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="#overview"><span class="mark">V</span><span class="brand-text">VEGO-AI BigUI</span></a>
    <nav class="nav" aria-label="Research sections">
      <a href="#overview" data-i18n="navOverview">Overview</a>
      <a href="#baseline-progress" data-i18n="navProgress">Progress proof</a>
      <a href="#experiment-benchmarks" data-i18n="navBenchmark">Benchmark</a>
      <a href="#executed-results" data-i18n="navResults">Results</a>
      <a href="#run-center">Runs</a>
      <a href="#architecture" data-i18n="navArchitecture">Architecture</a>
      <a href="#experiments" data-i18n="navExperiments">Experiments</a>
      <a href="#evaluation" data-i18n="navEvaluation">Validity</a>
      <a href="#independent-evidence">Evidence lab</a>
      <a href="#workspaces" data-i18n="navWorkspaces">MSc / PhD</a>
      <a href="#operations" data-i18n="navOperations">Operations</a>
    </nav>
    <div class="top-actions">
      <button id="language-toggle" type="button" aria-label="Switch language">עברית</button>
      <button type="button" onclick="window.print()" data-i18n="print">Print</button>
    </div>
  </div>
</div>
<main id="bigui-root" class="shell">
  <header class="hero" id="overview">
    <div>
      <div class="eyebrow">VEGO-AI · ExperimentCatalogSnapshot-v1 · offline</div>
      <h1 data-i18n="heroTitle">Measured experiments first. Architecture and evidence behind every result.</h1>
      <p class="lead" data-i18n="heroLead">BigUI begins with accepted runs and measured outcomes, then connects each result to its experiment design, architecture, source hash, evaluation, and next action.</p>
      <p class="he-summary" lang="he">המערכת מרכזת את הארכיטקטורה, הניסויים, הראיות והמגבלות במקום אחד — בלי להציג נתוני מנגנון כהוכחת דיוק.</p>
      <div class="status-row" id="hero-status"></div>
    </div>
    <aside class="hero-gate" aria-label="Current evidence gate">
      <strong data-i18n="gateTitle">Current evaluation stage</strong>
      <p id="gate-summary"></p>
      <div class="boundary" data-i18n="gateBoundary">Agent 4 and the official baseline remain frozen. Empty performance panels are intentional.</div>
    </aside>
  </header>

  <section class="section" aria-labelledby="overview-title">
    <div class="section-head"><div><h2 id="overview-title" data-i18n="overviewTitle">Research baseline</h2><p data-i18n="overviewCopy">The frozen corpus and baseline against which every accepted result is interpreted.</p></div></div>
    <div class="kpi-grid" id="overview-kpis"></div>
    <div class="two-col" style="margin-top:14px">
      <article class="panel"><h3 data-i18n="safeNow">Safe to say now</h3><ul id="safe-claims"></ul></article>
      <article class="panel"><h3 data-i18n="notAllowed">Not allowed yet</h3><ul id="blocked-claims"></ul></article>
    </div>
  </section>

  <section class="section" id="baseline-progress" aria-labelledby="baseline-progress-title">
    <div class="section-head"><div><h2 id="baseline-progress-title" data-i18n="progressTitle">Paper baseline and evidence of progress</h2><p data-i18n="progressCopy">A proof-oriented view separates architectural capability, reliability, contextual version differences, and empirical value.</p></div></div>
    <div id="comparison-lanes" class="evidence-lanes" aria-label="Evidence comparison lanes"></div>
    <div class="two-col" style="margin-top:14px">
      <article class="panel"><h3 data-i18n="paperCurrentCounts">Paper versus frozen repository counts</h3><div id="paper-current-counts" class="grouped-counts"></div><p class="provenance-note">A larger corpus or pattern count is a version difference, not a quality improvement.</p></article>
      <article class="panel"><h3 data-i18n="capabilityExtension">Human-judgment capability extension</h3><div id="capability-matrix" class="capability-grid"></div></article>
    </div>
    <article class="panel" style="margin-top:14px"><h3 data-i18n="improvementScorecard">Multidimensional improvement scorecard</h3><div style="overflow:auto"><table class="scorecard-table"><thead><tr><th>Dimension</th><th>Paper baseline</th><th>Current evidence</th><th>Status</th><th>Interpretation</th></tr></thead><tbody id="improvement-scorecard"></tbody></table></div><div class="proof-rule" style="margin-top:12px"><strong>Proof rule:</strong> a result is called better only for a shared metric, cohort, definition, and evidence class—and only with its trade-off and guardrail visible. No global weighted score is used.</div></article>
    <div class="plot-grid" style="margin-top:14px">
      <article class="panel"><h3>EXP-007 · routing Pareto frontier</h3><div id="routing-pareto" class="pareto-shell"></div></article>
      <article class="panel"><h3>EXP-039 · why configurations differ</h3><div id="comparison-tradeoffs" class="result-lane"></div></article>
      <article class="panel"><h3>EXP-034 · topology evidence</h3><div id="topology-proof" class="compact-bars"></div></article>
      <article class="panel"><h3>EXP-040 · thesis claim readiness</h3><div id="thesis-readiness"></div></article>
    </div>
  </section>

  <section class="section" id="experiment-benchmarks" aria-labelledby="experiment-benchmarks-title">
    <div class="section-head"><div><h2 id="experiment-benchmarks-title" data-i18n="benchmarkTitle">All-experiment evaluation benchmark</h2><p data-i18n="benchmarkCopy">One measurable standard evaluates protocol, data, execution, reproducibility, safety, comparability, and empirical validity without hiding missing evidence.</p></div><a class="benchmark-link" href="VEGO-AI-Experiment-Benchmark-Report.html">Open full analytics report</a></div>
    <div class="kpi-grid" id="benchmark-kpis"></div>
    <article class="panel" style="margin-top:14px"><h3>Data → model → architecture → experiment → result → evaluation → test</h3><div id="benchmark-dimensions" class="dimension-map" role="img" aria-label="Seven independent evaluation dimensions connect data, model, architecture, experiments, results, evaluation, and tests."></div><p class="provenance-note">No global weighted value score is calculated. Not-applicable and not-eligible dimensions are never converted into zero.</p></article>
    <div class="two-col" style="margin-top:14px">
      <article class="panel"><h3>Dimension pass coverage</h3><div id="benchmark-dimension-bars" class="benchmark-bars"></div><p class="provenance-note">Counts show exact dimension outcomes across 41 registered experiments; they are not a quality ranking.</p></article>
      <article class="panel"><h3>Program disposition</h3><div id="benchmark-verdict-bars" class="benchmark-bars"></div><p class="provenance-note">A gated non-run is a valid methodological outcome when consent, labels, approval, or sealed data are required.</p></article>
      <article class="panel"><h3>Latest accepted guardrail outcomes</h3><div id="benchmark-guardrail-bars" class="benchmark-bars"></div><p class="provenance-note">Only latest-run observations with a declared numerical guardrail or a required null are counted. Historical misses remain reported separately.</p></article>
      <article class="panel"><h3>Observation volume by executed experiment</h3><div id="benchmark-observation-bars" class="benchmark-bars"></div><p class="provenance-note">Observation count indicates analytical coverage, not result quality. EXP-036 is large because scale, mode, and repetition dimensions are explicit.</p></article>
    </div>
    <article class="panel" style="margin-top:14px"><h3>B0–B5 evidence and benchmark ladder</h3><div id="benchmark-baseline-ladder" class="baseline-ladder"></div></article>
    <article class="panel" id="benchmark-highlights-panel" style="margin-top:14px"><h3>Measured result highlights</h3><p>Selected latest-run observations with denominator, source hash, date, evidence class, and claim boundary.</p><div id="benchmark-highlights" class="plot-grid"></div></article>
    <article class="panel" style="margin-top:14px">
      <h3>EXP-000–EXP-040 evaluation matrix</h3>
      <div class="filters">
        <label class="search"><span>Find experiment</span><input id="benchmark-search" type="search" placeholder="EXP-036, routing, labels…" autocomplete="off"></label>
        <label><span>Verdict</span><select id="benchmark-verdict"><option value="">All</option></select></label>
        <label><span>Evidence</span><select id="benchmark-evidence"><option value="">All</option></select></label>
        <label><span>Execution</span><select id="benchmark-execution"><option value="">All</option></select></label>
      </div>
      <strong id="benchmark-count" aria-live="polite"></strong>
      <div style="overflow:auto"><table class="benchmark-table"><thead><tr><th>Experiment</th><th>Execution</th><th>Verdict</th><th>Protocol</th><th>Data</th><th>Reproducibility</th><th>Safety</th><th>Comparability</th><th>Empirical</th><th>Observations</th></tr></thead><tbody id="benchmark-table-body"></tbody></table></div>
    </article>
    <div class="two-col" style="margin-top:14px">
      <article class="panel"><h3>Canonical parameter dictionary</h3><div id="benchmark-parameters" class="parameter-grid"></div></article>
      <article class="panel"><h3>Valid comparison families</h3><div id="benchmark-comparison-families" class="comparison-family-grid"></div></article>
    </div>
  </section>

  <section class="section" id="executed-results" aria-labelledby="executed-results-title">
    <div class="section-head"><div><h2 id="executed-results-title">Executed results</h2><p>Measured observations from accepted, privacy-safe run bundles. Engineering misses remain visible; an executed run is not automatically a positive result.</p></div></div>
    <div class="kpi-grid" id="executed-kpis"></div>
    <div class="plot-grid" style="margin-top:14px">
      <article class="panel"><h3>EXP-006 · observed lifecycle profile</h3><div id="event-profile" class="compact-bars"></div></article>
      <article class="panel"><h3>EXP-007 · routing workload and coverage</h3><div id="routing-plot" class="compact-bars"></div><p class="provenance-note">Overlapping reconstructed events; denominator 289 for the aggregate routing replay.</p></article>
      <article class="panel"><h3>EXP-033 · controlled runtime parity</h3><div id="parity-result"></div></article>
      <article class="panel"><h3>EXP-035 · authority and fault safety</h3><div id="fault-result"></div></article>
      <article class="panel"><h3>EXP-036 · scale and latency</h3><div id="scale-result" class="compact-bars"></div></article>
      <article class="panel"><h3>Empirical classification performance</h3><div class="empty">Intentionally empty: 0/24 independent safe labels. Accuracy, macro-F1, paired correction, and generalization are not computable.</div></article>
    </div>
  </section>

  <section class="section" id="run-center" aria-labelledby="run-center-title">
    <div class="section-head"><div><h2 id="run-center-title">Accepted run center</h2><p>One traceable run record per accepted experiment result, with metric definitions, source hashes, acceptance criteria, artifacts, and claim boundaries.</p></div><strong id="run-center-count"></strong></div>
    <div class="filters">
      <label class="search"><span>Find a run</span><input id="run-search" type="search" placeholder="EXP-007, routing, parity…" autocomplete="off"></label>
      <label><span>Evidence</span><select id="run-evidence"><option value="">All</option></select></label>
      <label><span>Execution</span><select id="run-execution"><option value="">All</option></select></label>
      <label><span>History</span><select id="run-history"><option value="latest">Latest per experiment</option><option value="all">All accepted history</option></select></label>
    </div>
    <div id="run-grid" class="run-grid"></div>
  </section>

  <section class="section" id="architecture" aria-labelledby="architecture-title">
    <div class="section-head"><div><h2 id="architecture-title" data-i18n="architectureTitle">Architecture laboratory</h2><p data-i18n="architectureCopy">The original pipeline stays read-only; every H-layer path is advisory, explicit, and fail-closed.</p></div></div>
    <article class="panel">
      <h3 data-i18n="completeArchitecture">Original-to-enhanced governed architecture</h3>
      <div class="system-map" role="img" aria-label="Original agents one through four flow to selective review, feedback, memory, advisory comparison, and parked evaluation.">
        <div class="system-node baseline"><span class="id">A1–A4</span><strong>Original VEGO-AI</strong><small>Language → domain → model → variability</small></div>
        <div class="system-node"><span class="id">S1–S3</span><strong>Observe & route</strong><small>Selective intervention; E1–E14</small></div>
        <div class="system-node human"><span class="id">M1</span><strong>Human review queue</strong><small>Stable identity and evidence</small></div>
        <div class="system-node human"><span class="id">M2 / S4</span><strong>Structured feedback</strong><small>Human authority</small></div>
        <div class="system-node"><span class="id">S5</span><strong>Deterministic verify</strong><small>Conflict → adjudication</small></div>
        <div class="system-node"><span class="id">M3 / S7</span><strong>Judgment memory</strong><small>Scoped, provenance-aware</small></div>
        <div class="system-node"><span class="id">M4A / M4B-1</span><strong>Advise & compare</strong><small>Parallel, non-destructive</small></div>
        <div class="system-node parked"><span class="id">E15</span><strong>Evaluation track</strong><small>Parked until labels</small></div>
      </div>
      <div class="blocked-path">⛔ Memory / H3 → Agent 4 overwrite is forbidden</div>
    </article>
    <div class="two-col" style="margin-top:14px">
      <article class="panel"><h3 data-i18n="runtimeModes">Legacy, unified, and parity modes</h3><div class="runtime-grid" id="runtime-cards"></div></article>
      <article class="panel"><h3 data-i18n="topologyOptions">H-layer topology options A / B / C</h3><div class="topology-grid" id="topology-cards"></div></article>
    </div>
    <div class="two-col" style="margin-top:14px">
      <article class="panel">
        <h3 data-i18n="artifactPipeline">Artifact transformation pipeline</h3>
        <div class="pipeline" role="img" aria-label="Agent 4 output becomes review queue, resolved feedback, memory, advice, comparison, and evaluation reports.">
          <div class="step"><bdi>Agent 4 JSON</bdi></div><div class="step"><bdi>M1 queue</bdi></div>
          <div class="step"><bdi>M2 feedback</bdi></div><div class="step"><bdi>M3 memory</bdi></div>
          <div class="step"><bdi>M4A advice</bdi></div><div class="step"><bdi>M4B-1 comparison</bdi></div>
        </div>
      </article>
      <article class="panel">
        <h3 data-i18n="authorityFlow">Human-authority state machine</h3>
        <div class="state-machine" role="img" aria-label="Pending review moves through feedback and verification to approval, rejection, deferral, timeout parking, or adjudication.">
          <div class="step">pending_review</div><div class="step">feedback_received</div><div class="step">verified / adjudicate</div>
          <div class="step">pending_approval</div><div class="step">approved / rejected / deferred</div>
        </div>
        <p class="provenance-note">Timeout, conflict, rejection, and missing evidence preserve the baseline and write nothing to trusted memory.</p>
      </article>
    </div>
    <article class="panel" style="margin-top:14px">
      <h3 data-i18n="topologyMetrics">Topology structural trade-offs — EXP-034 fixture</h3>
      <div id="topology-bars" class="metric-bars" role="img" aria-label="Structural topology metrics; lower handoffs and boundaries trade against broader failure propagation."></div>
      <p class="provenance-note">All three fixture topologies produced the same canonical output. M-02 is deferred; no winner or production default is selected.</p>
    </article>
  </section>

  <section class="section" id="experiments" aria-labelledby="experiments-title">
    <div class="section-head"><div><h2 id="experiments-title" data-i18n="experimentsTitle">Experiment observatory</h2><p data-i18n="experimentsCopy">Search EXP-000–EXP-040 and inspect design, gates, evidence, accepted runs, and the exact next action.</p></div><strong id="experiment-count" aria-live="polite"></strong></div>
    <div class="filters">
      <label class="search"><span data-i18n="search">Search</span><input id="filter-search" type="search" placeholder="EXP-033, parity, labels…" autocomplete="off"></label>
      <label><span data-i18n="space">Space</span><select id="filter-space"><option value="">All</option></select></label>
      <label><span data-i18n="status">Status</span><select id="filter-status"><option value="">All</option></select></label>
      <label><span data-i18n="evidence">Evidence</span><select id="filter-evidence"><option value="">All</option></select></label>
      <label><span data-i18n="architecture">Architecture</span><select id="filter-architecture"><option value="">All</option></select></label>
    </div>
    <div class="experiment-grid" id="experiment-grid"></div>
    <div id="experiment-empty" class="empty" hidden>No experiments match these filters.</div>
  </section>

  <section class="section" id="results" aria-labelledby="results-title">
    <div class="section-head"><div><h2 id="results-title" data-i18n="resultsTitle">Results and comparisons</h2><p data-i18n="resultsCopy">Compare only equivalent runs. Incompatible cohorts, policies, models, metrics, leakage classes, or evidence classes are refused.</p></div></div>
    <div class="two-col">
      <article class="panel chart"><h3 data-i18n="evidenceDistribution">Experiments by evidence class</h3><div class="evidence-bars" id="evidence-bars" role="img" aria-label="Bar chart of registered experiments by evidence class."></div></article>
      <article class="panel"><h3 data-i18n="runTimeline">Accepted-run timeline</h3><div class="timeline" id="run-timeline"></div></article>
    </div>
    <article class="panel" style="margin-top:14px">
      <h3 data-i18n="comparisonGuard">Run comparison guard</h3>
      <div class="compare-controls">
        <label><span class="sr-only">Left run</span><select id="compare-left"></select></label>
        <label><span class="sr-only">Right run</span><select id="compare-right"></select></label>
        <button id="compare-button" type="button" data-i18n="compare">Compare</button>
      </div>
      <div id="compare-result" class="compare-verdict" aria-live="polite"></div>
    </article>
  </section>

  <section class="section" id="evaluation" aria-labelledby="evaluation-title">
    <div class="section-head"><div><h2 id="evaluation-title" data-i18n="evaluationTitle">Evaluation and validity</h2><p data-i18n="evaluationCopy">The label gate, empty accuracy panels, paired matrix, and validity threats make missing evidence visible.</p></div></div>
    <article class="panel">
      <h3 data-i18n="labelFunnel">Independent-label funnel</h3>
      <div id="label-funnel" class="funnel" role="img" aria-label="Twenty-four candidate rows and zero supplied, valid, or generalization-safe labels."></div>
      <p class="provenance-note">At safe N=0, empirical performance fields must remain null. At N=1–19, results are pilot-only; N≥20 enables limited MSc quantitative reporting.</p>
    </article>
    <div class="two-col" style="margin-top:14px">
      <article class="panel"><h3 data-i18n="accuracyPanels">Accuracy and macro-F1</h3><div id="accuracy-panels" class="result-grid"></div></article>
      <article class="panel"><h3 data-i18n="pairedMatrix">Paired correctness</h3>
        <div id="paired-matrix" class="matrix" role="img" aria-label="Paired correctness matrix is blank because independent labels are unavailable.">
          <div></div><div class="head">Candidate correct</div><div class="head">Candidate wrong</div>
          <div class="head">Original correct</div><div class="matrix-empty">—</div><div class="matrix-empty">—</div>
          <div class="head">Original wrong</div><div class="matrix-empty">—</div><div class="matrix-empty">—</div>
        </div>
      </article>
    </div>
    <div class="two-col" style="margin-top:14px">
      <article class="panel"><h3>Routing validity</h3><div class="empty">Precision, recall, high-severity recall, and missed-review rate await adjudicated targets in EXP-022.</div></article>
      <article class="panel"><h3>Retrieval validity</h3><div class="empty">Top-1/top-k relevance, scope correctness, conflict detection, and leakage rate await a blind audit.</div></article>
    </div>
    <article class="panel" style="margin-top:14px"><h3 data-i18n="validityRisks">Validity-threat heatmap</h3><div id="validity-grid" class="validity-grid"></div></article>
  </section>

  <section class="section" id="independent-evidence" aria-labelledby="independent-evidence-title">
    <div class="section-head"><div><h2 id="independent-evidence-title">Independent evidence lab</h2>
      <p>The executable path from a blinded human judgment to classification, routing, generalization, and effort evidence.</p></div>
      <a class="benchmark-link" href="docs/research/independent-evidence/README.md">Open execution protocol</a></div>
    <p class="boundary" id="independent-evidence-phase"></p>
    <div class="kpi-grid" id="independent-evidence-kpis"></div>
    <article class="panel" style="margin-top:14px">
      <h3>Real-evidence workflow</h3>
      <div class="pipeline" role="img" aria-label="Supervisor approval is followed by calibration, two independent reviews, agreement, adjudication, development evaluation, a frozen holdout pilot, and external replication.">
        <div class="step complete">Protocol approved<small>IE-01–IE-10 accepted</small></div>
        <div class="step current">Calibrate 2 humans<small>current phase</small></div>
        <div class="step sealed">Blind 24-item review<small>sealed until calibration freeze</small></div>
        <div class="step sealed">Agreement + adjudication</div>
        <div class="step sealed">Development N=16</div><div class="step sealed">Sealed pilot N=8</div>
        <div class="step sealed">External replication</div>
      </div>
      <p class="boundary">Software prepares, validates, and measures the evidence. Only independent humans may supply or adjudicate the labels.</p>
    </article>
    <div class="two-col" style="margin-top:14px">
      <article class="panel"><h3>What the 24-item review measures</h3>
        <div class="capability-grid">
          <div class="head">Question</div><div class="head">Independent target</div><div class="head">Metric</div>
          <div>Classification</div><div>Adjudicated class</div><div>Accuracy · macro-F1</div>
          <div>Review routing</div><div>Need + priority</div><div>Precision · recall · workload</div>
          <div>Reliability</div><div>Two raw reviews</div><div>Agreement · Cohen κ</div>
          <div>Annotation effort</div><div>Active seconds</div><div>Time distribution only</div>
        </div>
      </article>
      <article class="panel"><h3>What requires a later experiment</h3>
        <div id="independent-evidence-later" class="workspace-list"></div>
      </article>
    </div>
  </section>

  <section class="section" id="workspaces" aria-labelledby="workspaces-title">
    <div class="section-head"><div><h2 id="workspaces-title" data-i18n="workspacesTitle">MSc and PhD workspaces</h2><p data-i18n="workspacesCopy">Education remains the MSc empirical domain. External replication and domain transfer remain later, separately gated work.</p></div></div>
    <div class="two-col">
      <article class="panel"><h3>MSc · education critical path</h3><div id="msc-workspace" class="workspace-list"></div></article>
      <article class="panel"><h3>PhD · extension protocols</h3><div id="phd-workspace" class="workspace-list"></div><p class="boundary">MediVARIA remains future work. No clinical data or clinical-performance claim is present.</p></article>
    </div>
    <article class="panel" style="margin-top:14px">
      <h3 data-i18n="evidenceLadder">MSc-to-PhD evidence ladder</h3>
      <div class="pipeline" role="img" aria-label="Mechanism evidence proceeds through independent labels, sealed pilot, external education replication, effort study, and later domain transfer.">
        <div class="step">Mechanism</div><div class="step">Independent labels</div><div class="step">Sealed MSc pilot</div>
        <div class="step">External education replication</div><div class="step">Human effort</div><div class="step">Future domain transfer</div>
      </div>
    </article>
  </section>

  <section class="section" id="operations" aria-labelledby="operations-title">
    <div class="section-head"><div><h2 id="operations-title" data-i18n="operationsTitle">Operations and reproducibility</h2><p data-i18n="operationsCopy">Freshness, hashes, tests, baseline integrity, privacy tier, and security controls are visible and machine-readable.</p></div></div>
    <div class="kpi-grid" id="operations-kpis"></div>
    <div class="source-grid" id="source-grid" style="margin-top:14px"></div>
    <p class="provenance-note" id="catalog-provenance"></p>
  </section>
</main>

<dialog id="experiment-dialog" aria-labelledby="dialog-title">
  <div class="dialog-head"><h2 id="dialog-title"></h2><button class="dialog-close" id="dialog-close" type="button" aria-label="Close">✕</button></div>
  <div class="dialog-body" id="dialog-body"></div>
</dialog>

<footer><div class="shell">VEGO-AI BigUI · tracked sanitized tier by default · no external network runtime · research outcomes are read-only · <a href="VEGO-AI-Thesis-Baseline-Progress.html">historical thesis evidence view</a>.</div></footer>
<script id="bigui-catalog" type="application/json">__CATALOG__</script>
<script id="independent-evidence-decisions" type="application/json">__INDEPENDENT_DECISIONS__</script>
<script>
(() => {
  "use strict";
  const data = JSON.parse(document.getElementById("bigui-catalog").textContent);
  const evidenceDecisions = JSON.parse(document.getElementById("independent-evidence-decisions").textContent);
  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
  const legacyMetrics = data.metricObservations || [];
  const runMetrics = data.metricObservationsV2 || [];
  const metrics = Object.fromEntries(legacyMetrics.map((item) => [item.metricId,item]));
  const observations = Object.fromEntries(runMetrics.map((item) => [item.observationId,item]));
  const metricSeries = runMetrics.reduce((index,item)=>{
    (index[item.metricId] ||= []).push(item);return index;
  },{});
  const experiments = Object.fromEntries(data.experiments.map((item) => [item.id,item]));
  const benchmark = data.experimentBenchmark;
  const evaluationStandard = data.evaluationStandard;
  const benchmarkRecords = Object.fromEntries(
    benchmark.evaluationRecords.map((item) => [item.experimentId,item])
  );
  const runEntries = (data.acceptedRunBundles || []).map((bundle,index) => ({
    ...bundle.envelope,_bundle:bundle,_key:`${index}|${bundle.envelope.experimentId}|${bundle.envelope.runId}`
  }));
  const latestRunIdByExperiment = Object.fromEntries(
    data.currentRunIndex.currentRuns.map(item=>[item.experimentId,item.runId])
  );
  const comparisonFields = data.comparisonRules.requiredMatchingFields;
  const i18n = {
    en:{navOverview:"Overview",navProgress:"Progress proof",navBenchmark:"Benchmark",navArchitecture:"Architecture",navExperiments:"Experiments",navResults:"Results",navEvaluation:"Validity",navWorkspaces:"MSc / PhD",navOperations:"Operations",print:"Print",
      heroTitle:"Measured experiments first. Architecture and evidence behind every result.",heroLead:"BigUI begins with accepted runs and measured outcomes, then connects each result to its experiment design, architecture, source hash, evaluation, and next action.",
      gateTitle:"Current evaluation stage",gateBoundary:"Agent 4 and the official baseline remain frozen. Empty performance panels are intentional.",
      overviewTitle:"Research baseline",overviewCopy:"The frozen corpus and baseline against which every accepted result is interpreted.",safeNow:"Measured and supported now",notAllowed:"Requires independent evaluation",
      progressTitle:"Paper baseline and evidence of progress",progressCopy:"A proof-oriented view separates architectural capability, reliability, contextual version differences, and empirical value.",paperCurrentCounts:"Paper versus frozen repository counts",capabilityExtension:"Human-judgment capability extension",improvementScorecard:"Multidimensional improvement scorecard",
      benchmarkTitle:"All-experiment evaluation benchmark",benchmarkCopy:"One measurable standard evaluates protocol, data, execution, reproducibility, safety, comparability, and empirical validity without hiding missing evidence.",
      architectureTitle:"Architecture laboratory",architectureCopy:"The original pipeline stays read-only; every H-layer path is advisory, explicit, and fail-closed.",completeArchitecture:"Original-to-enhanced governed architecture",
      runtimeModes:"Legacy, unified, and parity modes",topologyOptions:"H-layer topology options A / B / C",artifactPipeline:"Artifact transformation pipeline",authorityFlow:"Human-authority state machine",topologyMetrics:"Topology structural trade-offs — EXP-034 fixture",
      experimentsTitle:"Experiment observatory",experimentsCopy:"Search EXP-000–EXP-040 and inspect design, gates, evidence, accepted runs, and the exact next action.",search:"Search",space:"Space",status:"Status",evidence:"Evidence",architecture:"Architecture",
      resultsTitle:"Results and comparisons",resultsCopy:"Compare only equivalent runs. Incompatible cohorts, policies, models, metrics, leakage classes, or evidence classes are refused.",evidenceDistribution:"Experiments by evidence class",runTimeline:"Accepted-run timeline",comparisonGuard:"Run comparison guard",compare:"Compare",
      evaluationTitle:"Evaluation and validity",evaluationCopy:"The label gate, empty accuracy panels, paired matrix, and validity threats make missing evidence visible.",labelFunnel:"Independent-label funnel",accuracyPanels:"Accuracy and macro-F1",pairedMatrix:"Paired correctness",validityRisks:"Validity-threat heatmap",
      workspacesTitle:"MSc and PhD workspaces",workspacesCopy:"Education remains the MSc empirical domain. External replication and domain transfer remain later, separately gated work.",evidenceLadder:"MSc-to-PhD evidence ladder",
      operationsTitle:"Operations and reproducibility",operationsCopy:"Freshness, hashes, tests, baseline integrity, privacy tier, and security controls are visible and machine-readable."},
    he:{navOverview:"סקירה",navProgress:"הוכחת התקדמות",navBenchmark:"מדד השוואה",navArchitecture:"ארכיטקטורה",navExperiments:"ניסויים",navResults:"תוצאות",navEvaluation:"תוקף",navWorkspaces:"MSc / PhD",navOperations:"תפעול",print:"הדפסה",
      heroTitle:"משטח עבודה אחד לארכיטקטורה, ניסויים וראיות",heroLead:"מעקב אחר כל ניסוי — מהשאלה והשער ועד ריצות, מדדים, מגבלות והפעולה הבאה. מוכנות מנגנון אינה תחליף לתוקף אמפירי.",
      gateTitle:"שלב ההערכה הנוכחי",gateBoundary:"Agent 4 וקו הבסיס הרשמי נשארים קפואים. לוחות הביצועים הריקים הם מכוונים.",
      overviewTitle:"קו הבסיס המחקרי",overviewCopy:"הקורפוס וקו הבסיס הקפואים שלפיהם כל תוצאה מאושרת מתפרשת.",safeNow:"נמדד ונתמך כעת",notAllowed:"דורש הערכה בלתי תלויה",
      progressTitle:"קו הבסיס של המאמר והוכחת התקדמות",progressCopy:"הצגה מוכוונת-ראיות המפרידה יכולת ארכיטקטונית, אמינות, הבדלי גרסה ותוקף אמפירי.",paperCurrentCounts:"ספירות המאמר מול המאגר הקפוא",capabilityExtension:"הרחבת יכולות השיפוט האנושי",improvementScorecard:"לוח שיפור רב-ממדי",
      benchmarkTitle:"מדד הערכה לכל הניסויים",benchmarkCopy:"תקן מדיד אחד מעריך פרוטוקול, נתונים, ביצוע, שחזור, בטיחות, השוואתיות ותוקף אמפירי בלי להסתיר ראיות חסרות.",
      architectureTitle:"מעבדת הארכיטקטורה",architectureCopy:"הצינור המקורי לקריאה בלבד; שכבת H מייעצת, מפורשת ונכשלת בצורה בטוחה.",completeArchitecture:"הארכיטקטורה המלאה והמוגנת",
      runtimeModes:"מצבי Legacy, Unified ו-Parity",topologyOptions:"חלופות טופולוגיה A / B / C",artifactPipeline:"זרימת הארטיפקטים",authorityFlow:"מכונת מצבי סמכות אנושית",topologyMetrics:"פשרות מבניות — ניסוי EXP-034",
      experimentsTitle:"מצפה הניסויים",experimentsCopy:"חיפוש EXP-000–EXP-040 ובדיקה של תכנון, שערים, ראיות, ריצות והפעולה הבאה.",search:"חיפוש",space:"מרחב",status:"מצב",evidence:"ראיות",architecture:"ארכיטקטורה",
      resultsTitle:"תוצאות והשוואות",resultsCopy:"השוואה מותרת רק בין ריצות שקולות. המערכת מסרבת להשוואות לא תקפות.",evidenceDistribution:"ניסויים לפי סוג ראיה",runTimeline:"ציר זמן של ריצות מאושרות",comparisonGuard:"מגן ההשוואה",compare:"השווה",
      evaluationTitle:"הערכה ותוקף",evaluationCopy:"שער התוויות, לוחות הדיוק הריקים ואיומי התוקף מציגים בגלוי את הראיות החסרות.",labelFunnel:"משפך תוויות בלתי תלויות",accuracyPanels:"דיוק ו-Macro-F1",pairedMatrix:"מטריצת נכונות זוגית",validityRisks:"מפת איומי תוקף",
      workspacesTitle:"מרחבי MSc ו-PhD",workspacesCopy:"תחום ה-MSc נשאר חינוך. רפליקציה והעברת תחום הן עבודה עתידית עם שערים נפרדים.",evidenceLadder:"סולם ראיות מ-MSc ל-PhD",
      operationsTitle:"תפעול ושחזור",operationsCopy:"טריות, גיבובים, בדיקות, שלמות קו בסיס, פרטיות ואבטחה מוצגים בצורה קריאה למכונה."}
  };
  let language = localStorage.getItem("vego-bigui-language") || "en";

  function setLanguage(next){
    language = next === "he" ? "he" : "en";
    document.documentElement.lang = language;
    document.documentElement.dir = language === "he" ? "rtl" : "ltr";
    document.body.dir = document.documentElement.dir;
    document.querySelectorAll("[data-i18n]").forEach((node) => {
      const key=node.dataset.i18n;if(i18n[language][key]) node.textContent=i18n[language][key];
    });
    $("language-toggle").textContent = language === "en" ? "עברית" : "English";
    localStorage.setItem("vego-bigui-language",language);
  }

  const fmt = (value) => value == null ? "—" : (typeof value === "number" && !Number.isInteger(value) ? value.toFixed(3) : String(value));
  const series = (metricId,experimentId=null) => (metricSeries[metricId]||[]).filter(item=>
    !experimentId||(item.experimentId===experimentId&&item.runId===latestRunIdByExperiment[experimentId])
  );
  const firstMetric = (metricId,experimentId=null) => series(metricId,experimentId)[0] || metrics[metricId];
  function metricFooter(item){
    if(!item) return "";
    const denominator=item.denominator == null ? "n/a" : fmt(item.denominator);
    return `<div class="metric-meta">Denominator: ${esc(denominator)} · ${esc(item.unit)} · ${esc(item.evidenceClass)} · ${esc(item.observationDate)}<br>${esc(item.claimBoundary)}</div>`;
  }
  function kpi(label,value,footer=""){
    return `<article class="kpi"><div class="value">${esc(value)}</div><div class="label">${esc(label)}</div>${footer}</article>`;
  }

  function renderOverview(){
    const p=data.programState;
    $("gate-summary").textContent=`${p.safeLabels}/${p.candidateLabels} generalization-safe labels; accuracy is ${p.accuracyStatus}. M4B-1 changes ${p.classificationChanges}/${p.comparisonRows} classifications.`;
    $("hero-status").innerHTML=[
      `ITER-${String(p.latestAcceptedIteration).padStart(3,"0")} · ${p.iterationVerdict}`,
      `${data.experiments.length} experiments`,
      `${data.runStoreSummary.uniqueExperimentRunCount} accepted experiment runs`,
      data.publicationTier.replaceAll("_"," ")
    ].map(value=>`<span class="chip">${esc(value)}</span>`).join("");
    $("overview-kpis").innerHTML=[
      kpi("Accepted iteration",p.latestAcceptedIteration,`<small>${esc(p.iterationVerdict)} · reliability-only</small>`),
      kpi("Registered experiments",data.experiments.length,"<small>EXP-000–EXP-040</small>"),
      kpi("Safe labels",`${p.safeLabels}/${p.candidateLabels}`,metricFooter(metrics.LABEL_GENERALIZATION_SAFE)),
      kpi("Comparison changes",`${p.classificationChanges}/${p.comparisonRows}`,metricFooter(metrics.SAFETY_CLASSIFICATION_CHANGES)),
      kpi("Accuracy / macro-F1","—","<small>NOT YET COMPUTABLE</small>")
    ].join("");
    $("safe-claims").innerHTML=data.claimBoundaries.safeNow.map(item=>`<li>${esc(item)}</li>`).join("");
    $("blocked-claims").innerHTML=data.claimBoundaries.notAllowed.map(item=>`<li>${esc(item)}</li>`).join("");
  }

  function comparisonExperiment(id){
    return data.baselineComparisonResults.experiments.find(item=>item.experimentId===id);
  }
  function renderBaselineProgress(){
    const baseline=data.baselineComparisonResults;
    const paper=data.paperBaseline;
    $("comparison-lanes").innerHTML=baseline.comparisonLanes.map(lane=>`<article class="evidence-lane" data-status="${esc(lane.status)}">
      <span class="evidence-badge" data-evidence="${lane.status==="demonstrated"?"offline":"blocked"}">${esc(lane.status.replaceAll("_"," "))}</span>
      <strong>${esc(lane.title)}</strong><p>${esc(lane.explanation)}</p>
      <small>${lane.directlyComparable?"Direct comparison permitted":"Context or gate only"}</small></article>`).join("");

    const countRows=[
      ["Case models",baseline.paperBaseline.caseModels,baseline.currentBaseline.caseModelTotal],
      ["Variability patterns",baseline.paperBaseline.patterns,baseline.currentBaseline.patternTotal],
      ["Substantial",baseline.paperBaseline.substantial,baseline.currentBaseline.substantialTotal],
      ["Occasional",baseline.paperBaseline.occasional,baseline.currentBaseline.occasionalTotal]
    ];
    const countMax=Math.max(...countRows.flatMap(row=>row.slice(1)));
    $("paper-current-counts").innerHTML=countRows.map(([label,paperValue,currentValue])=>`<div class="grouped-count">
      <strong>${esc(label)}</strong><div class="dual-bars">
        <div class="dual-bar"><small>Paper</small><div class="bar-track"><div class="bar-fill paper" style="width:${paperValue/countMax*100}%"></div></div><b>${paperValue}</b></div>
        <div class="dual-bar"><small>Current</small><div class="bar-track"><div class="bar-fill current" style="width:${currentValue/countMax*100}%"></div></div><b>${currentValue}</b></div>
      </div></div>`).join("")+`<div class="metric-meta">Paper: pages ${paper.source.reviewedPages.join(", ")} · sha256 ${esc(paper.source.sha256)}<br>${esc(paper.comparisonBoundary)}</div>`;

    $("capability-matrix").innerHTML=`<div class="head">Capability</div><div class="head">Paper</div><div class="head">Current H-layer</div>`+
      paper.humanJudgmentCapabilities.map(item=>`<div>${esc(item.id.replaceAll("_"," "))}</div>
        <div class="${item.paperBaseline?"capability-yes":"capability-no"}">${item.paperBaseline?"✓ explicit":"— not explicit"}</div>
        <div class="${item.currentExtension?"capability-yes":"capability-no"}">${item.currentExtension?"✓ implemented":"— absent"}</div>`).join("")+
      `<div class="metric-meta" style="grid-column:1/-1">Capability presence is a design property. It does not measure classification correctness.</div>`;

    const exp038=comparisonExperiment("EXP-038");
    $("improvement-scorecard").innerHTML=exp038.details.scorecard.map(row=>`<tr>
      <td>${esc(row.dimension.replaceAll("_"," "))}</td><td>${esc(fmt(row.paperBaseline))}</td><td>${esc(fmt(row.current))}</td>
      <td class="${esc(row.status)}">${esc(row.status.replaceAll("_"," "))}</td><td>${esc(row.interpretation)}</td></tr>`).join("");

    const routingModes=["silent","threshold_sev3","threshold_sev2","threshold_sev1","every_decision"];
    const loads=Object.fromEntries(series("ROUTING_EVENT_LOAD","EXP-007").map(item=>[item.dimensions.mode,item]));
    const coverage=Object.fromEntries(series("ROUTING_WEIGHTED_COVERAGE","EXP-007").map(item=>[item.dimensions.mode,item]));
    const plotWidth=620,plotHeight=310,left=55,right=28,top=24,bottom=48;
    const x=value=>left+Number(value)*(plotWidth-left-right);
    const y=value=>top+(1-Number(value))*(plotHeight-top-bottom);
    const ticks=[0,.25,.5,.75,1];
    $("routing-pareto").innerHTML=`<svg viewBox="0 0 ${plotWidth} ${plotHeight}" role="img" aria-labelledby="routing-pareto-title routing-pareto-desc">
      <title id="routing-pareto-title">Routing workload versus weighted coverage</title>
      <desc id="routing-pareto-desc">Each routing mode is plotted by event review load on the horizontal axis and weighted severity coverage on the vertical axis. Threshold severity two increases coverage compared with severity three while also increasing load.</desc>
      ${ticks.map(t=>`<line class="plot-gridline" x1="${x(t)}" y1="${top}" x2="${x(t)}" y2="${plotHeight-bottom}"></line><text class="plot-label" x="${x(t)}" y="${plotHeight-20}" text-anchor="middle">${t.toFixed(2)}</text>`).join("")}
      ${ticks.map(t=>`<line class="plot-gridline" x1="${left}" y1="${y(t)}" x2="${plotWidth-right}" y2="${y(t)}"></line><text class="plot-label" x="${left-8}" y="${y(t)+4}" text-anchor="end">${t.toFixed(2)}</text>`).join("")}
      <line class="plot-axis" x1="${left}" y1="${plotHeight-bottom}" x2="${plotWidth-right}" y2="${plotHeight-bottom}"></line>
      <line class="plot-axis" x1="${left}" y1="${top}" x2="${left}" y2="${plotHeight-bottom}"></line>
      <text class="plot-label" x="${(left+plotWidth-right)/2}" y="${plotHeight-3}" text-anchor="middle">Review load</text>
      <text class="plot-label" transform="translate(14 ${(top+plotHeight-bottom)/2}) rotate(-90)" text-anchor="middle">Weighted coverage</text>
      ${routingModes.filter(mode=>loads[mode]&&coverage[mode]).map(mode=>`<g><circle class="plot-point" cx="${x(loads[mode].value)}" cy="${y(coverage[mode].value)}" r="7"><title>${esc(mode)}: load ${fmt(loads[mode].value)}, coverage ${fmt(coverage[mode].value)}</title></circle><text class="plot-label" x="${x(loads[mode].value)+9}" y="${y(coverage[mode].value)-9}">${esc(mode.replace("threshold_","t-"))}</text></g>`).join("")}
    </svg>${metricFooter(coverage.threshold_sev2)}`;

    const exp039=comparisonExperiment("EXP-039");
    const comparisons=exp039.details.eligibleComparisons;
    $("comparison-tradeoffs").innerHTML=comparisons.map(item=>`<article class="tradeoff-card"><h4>${esc(item.family)} · ${esc(item.left)} → ${esc(item.right)}</h4>
      <p>${Object.entries(item.deltas).map(([key,value])=>`${esc(key)}: <strong>${Number(value)>=0?"+":""}${esc(fmt(value))}</strong>`).join(" · ")}</p>
      <p>${esc(item.interpretation)}</p></article>`).join("")+
      exp039.details.refusedComparisons.map(item=>`<article class="tradeoff-card"><h4 class="fail">Refused · ${esc(item.family)}</h4><p>${esc(item.left)} → ${esc(item.right)}</p><ul>${item.reasons.map(reason=>`<li>${esc(reason)}</li>`).join("")}</ul></article>`).join("");

    const topologyRows=["topology-a","topology-b","topology-c"].map(topology=>({
      label:topology,
      handoffs:series("TOPOLOGY_HANDOFF_COUNT","EXP-034").find(item=>item.dimensions.topology===topology)?.value,
      failure:series("TOPOLOGY_FAILURE_BREADTH","EXP-034").find(item=>item.dimensions.topology===topology)?.value,
      context:series("TOPOLOGY_CONTEXT_BYTES","EXP-034").find(item=>item.dimensions.topology===topology)?.value
    }));
    $("topology-proof").innerHTML=topologyRows.map(row=>`<article class="tradeoff-card"><h4>${esc(row.label)}</h4>
      <p>Handoffs <strong>${esc(row.handoffs)}</strong> · context bytes <strong>${esc(row.context)}</strong> · failure breadth <strong>${esc(row.failure)}</strong></p></article>`).join("")+
      `<p class="provenance-note">All three produced contract-equivalent canonical outputs. Lower coordination cost trades against broader single-component failure impact; no topology is approved.</p>`;

    const exp040=comparisonExperiment("EXP-040");
    const ready=Object.fromEntries(exp040.metrics.map(item=>[item.metricId,item]));
    $("thesis-readiness").innerHTML=`<div class="kpi-grid" style="grid-template-columns:1fr 1fr">
      ${kpi("Safe current claims",ready.THESIS_SAFE_CURRENT_CLAIMS.value,metricFooter(ready.THESIS_SAFE_CURRENT_CLAIMS))}
      ${kpi("Empirical claims ready",`${ready.THESIS_EMPIRICAL_IMPROVEMENT_CLAIMS_READY.numerator}/${ready.THESIS_EMPIRICAL_IMPROVEMENT_CLAIMS_READY.denominator}`,metricFooter(ready.THESIS_EMPIRICAL_IMPROVEMENT_CLAIMS_READY))}
      ${kpi("Hypotheses confirmed",`${ready.THESIS_HYPOTHESES_CONFIRMED.numerator}/${ready.THESIS_HYPOTHESES_CONFIRMED.denominator}`,metricFooter(ready.THESIS_HYPOTHESES_CONFIRMED))}
      ${kpi("Traceability records",ready.THESIS_TRACEABILITY_RECORDS.value,metricFooter(ready.THESIS_TRACEABILITY_RECORDS))}
    </div>`;
  }

  function dimensionState(result){
    return `<span class="dimension-state ${esc(result.status)}">${esc(result.status.replaceAll("_"," "))}</span>`;
  }
  function renderExperimentBenchmarks(){
    const summary=benchmark.summary;
    $("benchmark-kpis").innerHTML=[
      kpi("Evaluated",summary.evaluatedExperiments,"<small>complete EXP-000–EXP-040 program</small>"),
      kpi("Executed",summary.executedExperiments,"<small>accepted source-backed runs</small>"),
      kpi("Protocol / gated",summary.protocolOnlyExperiments,"<small>no result invented</small>"),
      kpi("Engineering evidence",summary.experimentsWithMeasuredEngineeringEvidence,"<small>mechanism and operations</small>"),
      kpi("Empirical classification",summary.experimentsWithEmpiricalClassificationEvidence,"<small>safe N=0</small>")
    ].join("");
    $("benchmark-dimensions").innerHTML=evaluationStandard.dimensions.map((item,index)=>`<article class="dimension-node">
      <strong>${index+1}. ${esc(item.title)}</strong><small>${esc(item.question)}</small></article>`).join("");

    const dimensionIds=evaluationStandard.dimensions.map(item=>item.id);
    $("benchmark-dimension-bars").innerHTML=dimensionIds.map(dimension=>{
      const counts={pass:0,partial:0,other:0};
      benchmark.evaluationRecords.forEach(record=>{
        const status=record.dimensions[dimension].status;
        if(status==="pass")counts.pass++;
        else if(status==="partial")counts.partial++;
        else counts.other++;
      });
      const total=benchmark.evaluationRecords.length;
      return `<div class="benchmark-row"><span>${esc(dimension.replaceAll("_"," "))}</span>
        <div class="track" title="${counts.pass} pass, ${counts.partial} partial, ${counts.other} other">
          <i class="pass-segment" style="width:${counts.pass/total*100}%"></i>
          <i class="partial-segment" style="width:${counts.partial/total*100}%"></i>
          <i class="other-segment" style="width:${counts.other/total*100}%"></i>
        </div><b>${counts.pass}/${total}</b></div>`;
    }).join("");
    const verdictCounts={};
    benchmark.evaluationRecords.forEach(item=>verdictCounts[item.verdict]=(verdictCounts[item.verdict]||0)+1);
    const verdictMax=Math.max(...Object.values(verdictCounts),1);
    $("benchmark-verdict-bars").innerHTML=Object.entries(verdictCounts).sort().map(([label,value])=>`<div class="benchmark-row">
      <span>${esc(label.replaceAll("_"," "))}</span><div class="bar-track"><div class="bar-fill" style="width:${value/verdictMax*100}%"></div></div><b>${value}</b></div>`).join("");
    const guardrails=benchmark.guardrailSummary;
    const guardrailMax=Math.max(guardrails.met,guardrails.missed,guardrails.notComputable,1);
    $("benchmark-guardrail-bars").innerHTML=[
      ["met",guardrails.met],["missed",guardrails.missed],["not computable",guardrails.notComputable]
    ].map(([label,value])=>`<div class="benchmark-row"><span>${esc(label)}</span><div class="bar-track"><div class="bar-fill" style="width:${value/guardrailMax*100}%"></div></div><b>${value}</b></div>`).join("")+
      `<div class="metric-meta">${guardrails.assessedObservations} latest observations · ${guardrails.experimentsWithMissedGuardrails} experiments with a current miss<br>${guardrails.historicalMissed}/${guardrails.historicalAssessedObservations} target-bearing observations missed across accepted history.</div>`;
    const observed=benchmark.evaluationRecords.filter(item=>item.observationCount>0).sort((a,b)=>b.observationCount-a.observationCount);
    const observationMax=Math.max(...observed.map(item=>item.observationCount),1);
    $("benchmark-observation-bars").innerHTML=observed.map(item=>`<div class="benchmark-row"><span><bdi dir="ltr">${esc(item.experimentId)}</bdi></span>
      <div class="bar-track"><div class="bar-fill" style="width:${item.observationCount/observationMax*100}%"></div></div><b>${item.observationCount}</b></div>`).join("");
    $("benchmark-baseline-ladder").innerHTML=evaluationStandard.baselineLadder.map(item=>`<article class="baseline-stage" data-state="${esc(item.currentState)}">
      <strong>${esc(item.id)}</strong><span>${esc(item.title)}</span><p>${esc(item.purpose)}</p>
      <small>${esc(item.currentState.replaceAll("_"," "))}</small></article>`).join("");
    $("benchmark-highlights").innerHTML=benchmark.resultHighlights.map(item=>`<article class="tradeoff-card">
      <div class="status-row"><strong><bdi dir="ltr">${esc(item.experimentId)}</bdi> · ${esc(item.title)}</strong>
      <span class="evidence-badge" data-evidence="${esc(item.evidenceClass)}">${esc(item.evidenceClass)}</span></div>
      <p>${esc(item.summary)}</p>
      <div class="result-lane">${item.metrics.map(metric=>`<div class="detail-block">
        <strong><bdi dir="ltr">${esc(metric.metricId)}</bdi></strong>
        <p><b>${esc(fmt(metric.value))}</b> ${esc(metric.unit)} · N=${esc(fmt(metric.denominator))}</p>
        <small>${esc(Object.entries(metric.dimensions||{}).map(([key,value])=>`${key}=${value}`).join(" · ")||"aggregate")}</small>
        <div class="metric-meta">${esc(metric.observationDate)} · ${esc(metric.sourcePath)} · ${esc(metric.sourceSha256.slice(0,12))}…<br>${esc(metric.claimBoundary)}</div>
      </div>`).join("")}</div>
      <div class="boundary">${esc(item.claimBoundary)}</div></article>`).join("");
    optionValues($("benchmark-verdict"),benchmark.evaluationRecords.map(item=>item.verdict));
    optionValues($("benchmark-evidence"),benchmark.evaluationRecords.map(item=>item.evidenceClass));
    optionValues($("benchmark-execution"),benchmark.evaluationRecords.map(item=>item.executionState));
    for(const id of ["benchmark-search","benchmark-verdict","benchmark-evidence","benchmark-execution"]){
      $(id).addEventListener("input",filterBenchmarkRecords);
      $(id).addEventListener("change",filterBenchmarkRecords);
    }
    filterBenchmarkRecords();
    $("benchmark-parameters").innerHTML=benchmark.parameterDictionary.map(item=>`<details class="parameter-card">
      <summary><bdi dir="ltr">${esc(item.id)}</bdi> · ${esc(item.title)}</summary><p>${esc(item.definition)}</p>
      <p><strong>Allowed:</strong> ${esc(item.allowedValues.join(" · "))}</p><small>${esc(item.whyItMatters)}</small></details>`).join("");
    $("benchmark-comparison-families").innerHTML=benchmark.comparisonFamilies.map(item=>`<article class="comparison-family">
      <span class="evidence-badge" data-evidence="${item.status==="demonstrated"?"offline":"blocked"}">${esc(item.status.replaceAll("_"," "))}</span>
      <strong>${esc(item.family.replaceAll("_"," "))}</strong><p>${esc(item.experiments.join(" · "))}</p><p>${esc(item.interpretation)}</p></article>`).join("");
  }
  function filterBenchmarkRecords(){
    const query=$("benchmark-search").value.trim().toLowerCase();
    const verdict=$("benchmark-verdict").value,evidence=$("benchmark-evidence").value,execution=$("benchmark-execution").value;
    const filtered=benchmark.evaluationRecords.filter(item=>{
      const haystack=[item.experimentId,item.title,item.status,item.evidenceClass,item.verdict,item.baseline,item.comparator].join(" ").toLowerCase();
      return (!query||haystack.includes(query))&&(!verdict||item.verdict===verdict)&&(!evidence||item.evidenceClass===evidence)&&(!execution||item.executionState===execution);
    });
    $("benchmark-count").textContent=`${filtered.length} / ${benchmark.evaluationRecords.length}`;
    $("benchmark-table-body").innerHTML=filtered.map(item=>`<tr tabindex="0" data-id="${esc(item.experimentId)}" aria-label="Open ${esc(item.experimentId)} evaluation">
      <td><strong><bdi dir="ltr">${esc(item.experimentId)}</bdi></strong><small>${esc(item.title)}</small></td>
      <td>${esc(item.executionState.replaceAll("_"," "))}</td><td>${esc(item.verdict.replaceAll("_"," "))}</td>
      <td>${dimensionState(item.dimensions.protocol)}</td><td>${dimensionState(item.dimensions.data)}</td>
      <td>${dimensionState(item.dimensions.reproducibility)}</td><td>${dimensionState(item.dimensions.safety)}</td>
      <td>${dimensionState(item.dimensions.comparability)}</td><td>${dimensionState(item.dimensions.empiricalValidity)}</td>
      <td>${item.observationCount}</td></tr>`).join("");
    $("benchmark-table-body").querySelectorAll("tr").forEach(row=>{
      const open=()=>openExperiment(row.dataset.id,true);
      row.addEventListener("click",open);
      row.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();open()}});
    });
  }

  function compactBars(rows,maximum=null){
    const max=maximum ?? Math.max(...rows.map(row=>Number(row.value)||0),1);
    return rows.map(row=>`<div class="compact-row"><small>${esc(row.label)}</small>
      <div class="bar-track"><div class="bar-fill" style="width:${Math.max(row.value==null?0:2,(Number(row.value)||0)/max*100)}%"></div></div>
      <b>${esc(fmt(row.value))}</b></div>`).join("");
  }

  function renderExecutedResults(){
    const s=data.runStoreSummary;
    const parity=firstMetric("ARCH_SEMANTIC_PARITY_RATE","EXP-033");
    const safety=firstMetric("SAFETY_FAULT_CASE_PASS_RATE","EXP-035");
    $("executed-kpis").innerHTML=[
      kpi("Executed experiments",`${s.experimentsWithAcceptedRuns}/${data.experiments.length}`,"<small>accepted, source-backed bundles</small>"),
      kpi("Accepted runs",s.uniqueExperimentRunCount,"<small>one or more attempts per experiment</small>"),
      kpi("Measured observations",s.metricObservationCount,"<small>MetricObservation-v2</small>"),
      kpi("Runtime semantic parity",fmt(parity?.value),metricFooter(parity)),
      kpi("Fault cases passed",safety?`${safety.numerator}/${safety.denominator}`:"—",metricFooter(safety))
    ].join("");
    $("event-profile").innerHTML=compactBars([
      {label:"Reconstructed events",value:firstMetric("EVENT_TOTAL_RECONSTRUCTED","EXP-006")?.value},
      {label:"Severity 2+",value:firstMetric("EVENT_SEV2PLUS","EXP-006")?.value},
      {label:"Early stage",value:firstMetric("EVENT_EARLY_STAGE","EXP-006")?.value},
      {label:"Uncertainty marked",value:firstMetric("EVENT_UNCERTAINTY_MARKED","EXP-006")?.value}
    ]);
    const modes=["threshold_sev3","threshold_sev2","threshold_sev1","every_decision"];
    const routing=series("ROUTING_WEIGHTED_COVERAGE","EXP-007");
    const load=series("ROUTING_EVENT_LOAD","EXP-007");
    $("routing-plot").innerHTML=modes.map(mode=>{
      const coverage=routing.find(item=>item.dimensions.mode===mode)?.value;
      const burden=load.find(item=>item.dimensions.mode===mode)?.value;
      return `<div><strong>${esc(mode)}</strong>${compactBars([
        {label:"weighted coverage",value:coverage},{label:"event load",value:burden}
      ],1)}</div>`;
    }).join("");
    $("parity-result").innerHTML=[
      kpi("Semantic parity",fmt(firstMetric("ARCH_SEMANTIC_PARITY_RATE","EXP-033")?.value)),
      kpi("Deterministic repetitions",fmt(firstMetric("ARCH_REPLAY_DETERMINISM","EXP-033")?.numerator)),
      kpi("Classification changes",fmt(firstMetric("ARCH_CLASSIFICATION_CHANGES","EXP-033")?.value))
    ].join("");
    $("fault-result").innerHTML=safety?
      `${kpi("Safe outcomes",`${safety.numerator}/${safety.denominator}`,metricFooter(safety))}
       <p class="provenance-note">Finite synthetic fault catalog; this is conformance evidence, not a universal safety probability.</p>`:
      '<div class="empty">No accepted safety observation.</div>';
    const latency=series("ARCH_P95_RATIO_TO_LEGACY","EXP-036").filter(item=>item.dimensions.mode!=="legacy");
    const latencyHistory=runEntries.filter(run=>run.experimentId==="EXP-036").sort((a,b)=>`${a.completedAt}|${a.runId}`.localeCompare(`${b.completedAt}|${b.runId}`)).map(run=>{
      const unified=run._bundle.metricObservations.filter(item=>item.metricId==="ARCH_P95_RATIO_TO_LEGACY"&&item.dimensions.mode==="unified");
      return {label:run.runId.slice(-12),value:Math.max(...unified.map(item=>Number(item.value)||0),0)};
    });
    const exp036Verdict=benchmarkRecords["EXP-036"]?.verdict;
    $("scale-result").innerHTML=compactBars(latency.map(item=>({
      label:`${item.dimensions.fixture} · ${item.dimensions.mode}`,value:item.value
    })),2.25)+`<p class="${exp036Verdict==="MEASURED_PASS"?"pass":"engineering-miss"}"><strong>Latest engineering verdict:</strong> ${esc(exp036Verdict||"—")}. The unified limit is ≤1.15 and the parity limit is ≤2.25.</p>
      <h4>Accepted-run history · worst unified p95 ratio</h4>${compactBars(latencyHistory,Math.max(1.15,...latencyHistory.map(item=>item.value)))}
      <p class="provenance-note">The latest accepted run is evaluated as current; earlier misses remain visible as reproducibility history.</p>`;
  }

  function renderRunCenter(){
    optionValues($("run-evidence"),runEntries.map(item=>item.evidenceClass));
    optionValues($("run-execution"),runEntries.map(item=>item.executionStatus));
    for(const id of ["run-search","run-evidence","run-execution","run-history"]){
      $(id).addEventListener("input",filterRuns);$(id).addEventListener("change",filterRuns);
    }
    filterRuns();
  }
  function filterRuns(){
    const query=$("run-search").value.trim().toLowerCase();
    const evidence=$("run-evidence").value,execution=$("run-execution").value;
    const history=$("run-history").value;
    const latestKeys=new Set(runEntries.filter(
      run=>latestRunIdByExperiment[run.experimentId]===run.runId
    ).map(run=>run._key));
    const filtered=runEntries.filter(run=>{
      const experiment=experiments[run.experimentId];
      const haystack=[run.experimentId,run.runId,experiment?.title,run.evidenceClass,run.manifestSchema].join(" ").toLowerCase();
      return (history==="all"||latestKeys.has(run._key))&&(!query||haystack.includes(query))&&(!evidence||run.evidenceClass===evidence)&&(!execution||run.executionStatus===execution);
    });
    $("run-center-count").textContent=`${filtered.length} / ${runEntries.length}`;
    $("run-grid").innerHTML=filtered.map(run=>`<article class="run-card"><div class="status-row">
      <span class="id"><bdi dir="ltr">${esc(run.experimentId)}</bdi></span><span class="evidence-badge" data-evidence="${esc(run.evidenceClass)}">${esc(run.evidenceClass)}</span></div>
      <strong>${esc(experiments[run.experimentId]?.title||run.experimentId)}</strong>
      <p>${esc(run.runId)} · ${run.metricObservationIds.length} observations</p>
      <div class="chips"><span class="chip">${esc(run.executionStatus)}</span><span class="chip">${esc(run.acceptanceStatus)}</span></div>
      <button type="button" data-run="${esc(run._key)}">Inspect run</button></article>`).join("");
    $("run-grid").querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>openRun(button.dataset.run)));
  }
  function openRun(key){
    const run=runEntries.find(item=>item._key===key);if(!run)return;
    const bundle=run._bundle;
    $("dialog-title").innerHTML=`<bdi dir="ltr">${esc(run.experimentId)}</bdi> · ${esc(run.runId)}`;
    $("dialog-body").innerHTML=`<div class="status-row"><span class="status-badge">${esc(run.acceptanceStatus)}</span>
      <span class="evidence-badge" data-evidence="${esc(run.evidenceClass)}">${esc(run.evidenceClass)}</span><span class="chip">${esc(run.executionStatus)}</span></div>
      <div class="detail-grid" style="margin-top:12px">
      <div class="detail-block"><h3>Evaluation</h3><p>Execution valid: ${esc(run.evaluation.executionValid)}</p><p>Engineering target met: ${esc(run.evaluation.engineeringTargetMet)}</p><p>Verdict: ${esc(run.evaluation.resultVerdict)}</p></div>
      <div class="detail-block"><h3>Provenance</h3><p>Manifest: ${esc(run.manifestPath)}</p><p>SHA-256: ${esc(run.manifestSha256)}</p><p>Source revision: ${esc(run.sourceRevision)}</p></div>
      <div class="detail-block"><h3>Acceptance criteria</h3>${bundle.acceptance.criteriaOutcomes.map(item=>`<p class="${item.passed?"pass":"fail"}">${item.passed?"✓":"✕"} ${esc(item.id)} · ${esc(item.detail)}</p>`).join("")}</div>
      <div class="detail-block"><h3>Artifacts</h3>${list(run.artifactRefs)}</div></div>
      <div class="detail-block" style="margin-top:12px"><h3>Measured observations</h3><div style="overflow:auto"><table class="metric-table"><thead><tr><th>Metric</th><th>Value</th><th>Denominator</th><th>Dimensions</th></tr></thead><tbody>
      ${bundle.metricObservations.map(item=>`<tr><td>${esc(item.metricId)}</td><td>${esc(fmt(item.value))} ${esc(item.unit)}</td><td>${esc(fmt(item.denominator))}</td><td>${esc(Object.entries(item.dimensions||{}).map(([k,v])=>`${k}=${v}`).join(", ")||"—")}</td></tr>`).join("")}
      </tbody></table></div></div><div class="boundary" style="margin-top:12px">${esc(run.evaluation.claimBoundary)}</div>`;
    if(!$("experiment-dialog").open)$("experiment-dialog").showModal();
  }

  function renderArchitecture(){
    const runtime=data.architectureVariants.filter(item=>item.kind==="runtime_mode");
    const topologies=data.architectureVariants.filter(item=>item.kind==="h_layer_topology");
    const cards=(items)=>items.map(item=>`<article class="arch-card" id="architecture-${esc(item.id)}" data-default="${item.default}">
      <span class="evidence-badge" data-evidence="${esc(item.evidenceClass)}">${esc(item.status)}</span>
      <h3><bdi dir="ltr">${esc(item.id)}</bdi> · ${esc(item.title)}</h3><p>${esc(item.failureBehavior)}</p>
      <div class="chips"><span class="chip">${item.default?"default":"not default"}</span><span class="chip">${item.approved?"approved":"not approved"}</span></div>
      <div class="metric-meta">${esc(item.claimBoundary)}</div></article>`).join("");
    $("runtime-cards").innerHTML=cards(runtime);
    $("topology-cards").innerHTML=cards(topologies);
    const topologyIds=[["topology-a","A"],["topology-b","B"],["topology-c","C"]];
    const fields=[
      ["TOPOLOGY_HANDOFF_COUNT","Handoffs"],["TOPOLOGY_CONTEXT_BYTES","Context bytes"],
      ["TOPOLOGY_STATE_BOUNDARIES","State boundaries"],["TOPOLOGY_FAILURE_BREADTH","Failure breadth"]
    ];
    $("topology-bars").innerHTML=fields.map(([metricId,label])=>{
      const values=topologyIds.map(([id])=>series(metricId,"EXP-034").find(item=>item.dimensions.topology===id)?.value ?? 0);
      const max=Math.max(...values,1);
      return `<div><strong>${esc(label)}</strong>${topologyIds.map(([id,short],index)=>`<div class="metric-bar">
        <span>Topology ${short}</span><div class="bar-track"><div class="bar-fill" style="width:${Math.max(3,values[index]/max*100)}%"></div></div><b>${esc(values[index])}</b>
      </div>`).join("")}</div>`;
    }).join("")+metricFooter(series("TOPOLOGY_TRACE_COMPLETENESS","EXP-034")[0]);
  }

  function optionValues(select,values){
    select.innerHTML='<option value="">All</option>'+[...new Set(values)].sort().map(value=>`<option value="${esc(value)}">${esc(value)}</option>`).join("");
  }
  function restoreFilters(){
    try{return JSON.parse(localStorage.getItem("vego-bigui-filters")||"{}")}catch{return{}}
  }
  function renderExperiments(){
    const saved=restoreFilters();
    optionValues($("filter-space"),data.experiments.map(item=>item.researchSpace));
    optionValues($("filter-status"),data.experiments.map(item=>item.status));
    optionValues($("filter-evidence"),data.experiments.map(item=>item.evidenceClass));
    optionValues($("filter-architecture"),data.experiments.flatMap(item=>item.architectureTargets));
    for(const id of ["filter-search","filter-space","filter-status","filter-evidence","filter-architecture"]){
      if(saved[id]) $(id).value=saved[id];
      $(id).addEventListener("input",filterExperiments);
      $(id).addEventListener("change",filterExperiments);
    }
    filterExperiments();
  }
  function filterExperiments(){
    const query=$("filter-search").value.trim().toLowerCase();
    const space=$("filter-space").value,status=$("filter-status").value,evidence=$("filter-evidence").value,architecture=$("filter-architecture").value;
    const filtered=data.experiments.filter(item=>{
      const haystack=[item.id,item.title,item.researchTrack,item.researchQuestion,item.nextAction,...item.architectureTargets].join(" ").toLowerCase();
      return (!query||haystack.includes(query))&&(!space||item.researchSpace===space)&&(!status||item.status===status)&&(!evidence||item.evidenceClass===evidence)&&(!architecture||item.architectureTargets.includes(architecture));
    });
    $("experiment-count").textContent=`${filtered.length} / ${data.experiments.length}`;
    $("experiment-empty").hidden=filtered.length>0;
    $("experiment-grid").innerHTML=filtered.map(item=>`<button type="button" class="experiment-card" data-id="${item.id}" aria-label="Open ${esc(item.id)} ${esc(item.title)}">
      <div class="status-row"><span class="id"><bdi dir="ltr">${item.id}</bdi></span><span class="evidence-badge" data-evidence="${esc(item.evidenceClass)}">${esc(item.evidenceClass.replaceAll("_"," "))}</span></div>
      <h3>${esc(item.title)}</h3><p>${esc(item.researchSpace)} · ${esc(item.researchTrack)}</p>
      <div class="chips"><span class="chip">${esc(item.status)}</span><span class="chip">${item.acceptedRunIds.length} accepted run${item.acceptedRunIds.length===1?"":"s"}</span></div>
      <p class="next">${esc(item.nextAction)}</p></button>`).join("");
    $("experiment-grid").querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>openExperiment(button.dataset.id,true)));
    localStorage.setItem("vego-bigui-filters",JSON.stringify({
      "filter-search":query,"filter-space":space,"filter-status":status,"filter-evidence":evidence,"filter-architecture":architecture
    }));
  }
  const list=(values)=>values.length?`<ul>${values.map(value=>`<li>${esc(value)}</li>`).join("")}</ul>`:"<p>None recorded.</p>";
  function openExperiment(id,updateHash=false){
    const item=experiments[id];if(!item)return;
    const evaluation=benchmarkRecords[id];
    $("dialog-title").innerHTML=`<bdi dir="ltr">${esc(item.id)}</bdi> · ${esc(item.title)}`;
    const observed=item.latestResult?.metricObservationIds.map(metricId=>observations[metricId]||metrics[metricId]).filter(Boolean)||[];
    const dimensionDetails=evaluation?Object.entries(evaluation.dimensions).map(([key,result])=>`<p>${dimensionState(result)} <strong>${esc(key.replaceAll("_"," "))}:</strong> ${esc(result.explanation)}</p>`).join(""):"<p>No benchmark record.</p>";
    const signalDetails=evaluation?.engineeringSignals.length?`<div style="overflow:auto"><table class="metric-table"><thead><tr><th>Metric</th><th>Dimensions</th><th>Value</th><th>Target</th><th>Status</th></tr></thead><tbody>
      ${evaluation.engineeringSignals.map(signal=>`<tr><td>${esc(signal.metricId)}</td><td>${esc(Object.entries(signal.dimensions||{}).map(([k,v])=>`${k}=${v}`).join(", ")||"—")}</td><td>${esc(fmt(signal.value))} ${esc(signal.unit)}</td><td>${esc(signal.target||"descriptive")}</td><td class="${signal.status==="met"?"pass":signal.status==="missed"?"fail":""}">${esc(signal.status.replaceAll("_"," "))}</td></tr>`).join("")}
      </tbody></table></div>`:"<p>No measured engineering signal.</p>";
    $("dialog-body").innerHTML=`<div class="status-row"><span class="status-badge">${esc(item.status)}</span><span class="evidence-badge" data-evidence="${esc(item.evidenceClass)}">${esc(item.evidenceClass)}</span><span class="chip">${esc(item.researchSpace)}</span></div>
      <div class="detail-grid" style="margin-top:12px">
        <div class="detail-block"><h3>Research question</h3><p>${esc(item.researchQuestion)}</p></div>
        <div class="detail-block"><h3>Architecture targets</h3>${list(item.architectureTargets)}</div>
        <div class="detail-block"><h3>Baseline</h3><p>${esc(item.baseline)}</p><h3>Comparator</h3><p>${esc(item.comparator)}</p></div>
        <div class="detail-block"><h3>Prerequisites</h3>${list(item.prerequisites)}<h3>Approval gates</h3>${list(item.approvalGates)}</div>
        <div class="detail-block"><h3>Accepted runs</h3>${list(item.acceptedRunIds)}<h3>Owner</h3><p>${esc(item.owner)}</p></div>
        <div class="detail-block"><h3>Metric definitions</h3>${list(item.metricDefinitions)}</div>
        <div class="detail-block"><h3>Current observations</h3>${observed.length?observed.map(metric=>`<p><strong>${esc(metric.metricId)}:</strong> ${esc(fmt(metric.value))}</p>${metricFooter(metric)}`).join(""):"<p>No accepted observation.</p>"}</div>
        <div class="detail-block"><h3>Validity threats</h3>${list(item.validityThreats)}</div>
      </div>
      <div class="detail-grid" style="margin-top:12px">
        <div class="detail-block"><h3>Benchmark verdict</h3><p><strong>${esc(evaluation?.verdict||"—")}</strong></p><p>Execution: ${esc(evaluation?.executionState||"—")} · eligibility: ${esc(evaluation?.eligibility||"—")}</p><p>${esc(evaluation?.observationCount||0)} observations · ${esc(evaluation?.acceptedRunCount||0)} accepted run bundles</p></div>
        <div class="detail-block"><h3>Seven-dimension evaluation</h3>${dimensionDetails}</div>
      </div>
      <div class="detail-block" style="margin-top:12px"><h3>Measured engineering signals and guardrails</h3>${signalDetails}</div>
      <div class="boundary" style="margin-top:12px"><strong>Claim boundary:</strong> ${esc(item.claimBoundary)}</div>
      <div class="detail-block" style="margin-top:12px"><h3>Next action</h3><p>${esc(item.nextAction)}</p><h3>Artifacts</h3>${list(item.artifactLinks)}</div>`;
    if(!$("experiment-dialog").open)$("experiment-dialog").showModal();
    if(updateHash)history.pushState(null,"",`#experiment-${id}`);
  }

  function renderResults(){
    const counts={};data.experiments.forEach(item=>counts[item.evidenceClass]=(counts[item.evidenceClass]||0)+1);
    const max=Math.max(...Object.values(counts));
    $("evidence-bars").innerHTML=Object.entries(counts).sort().map(([label,value])=>`<div class="evidence-column">
      <strong>${value}</strong><div class="bar" style="height:${Math.max(4,value/max*155)}px"></div><small>${esc(label.replaceAll("_"," "))}</small></div>`).join("");
    $("run-timeline").innerHTML=runEntries.length?runEntries.map(run=>`<article class="timeline-item"><strong><bdi dir="ltr">${esc(run.experimentId)}</bdi></strong>
      <span class="evidence-badge" data-evidence="${esc(run.evidenceClass)}">${esc(run.evidenceClass)}</span><small>${esc(run.acceptedAt||"pending")}</small>
      <small>${esc(run.runId)}</small></article>`).join(""):'<div class="empty">No accepted runs.</div>';
    const options=runEntries.map(run=>`<option value="${esc(run._key)}">${esc(run.experimentId)} · ${esc(run.evidenceClass)} · ${esc(run.runId)}</option>`).join("");
    $("compare-left").innerHTML=options;$("compare-right").innerHTML=options;
    if(runEntries.length>1)$("compare-right").selectedIndex=1;
    $("compare-button").addEventListener("click",compareRuns);
    compareRuns();
  }
  function compareRuns(){
    const left=runEntries.find(item=>item._key===$("compare-left").value);
    const right=runEntries.find(item=>item._key===$("compare-right").value);
    if(!left||!right){$("compare-result").innerHTML='<div class="empty">Choose two runs.</div>';return}
    if(left._key===right._key){$("compare-result").innerHTML='<div class="boundary fail">Choose two distinct run records.</div>';return}
    const checks=[
      {field:"experimentId",left:left.experimentId,right:right.experimentId,matches:left.experimentId===right.experimentId},
      ...comparisonFields.map(field=>({field,left:left.comparisonContext[field],right:right.comparisonContext[field],matches:left.comparisonContext[field]!=null&&right.comparisonContext[field]!=null&&left.comparisonContext[field]===right.comparisonContext[field]}))
    ];
    const eligible=checks.every(item=>item.matches);
    const leftMetrics=new Map(left._bundle.metricObservations.map(item=>[`${item.metricId}|${JSON.stringify(item.dimensions||{},Object.keys(item.dimensions||{}).sort())}`,item]));
    const rightMetrics=new Map(right._bundle.metricObservations.map(item=>[`${item.metricId}|${JSON.stringify(item.dimensions||{},Object.keys(item.dimensions||{}).sort())}`,item]));
    const deltas=eligible?[...leftMetrics.entries()].flatMap(([key,leftMetric])=>{
      const rightMetric=rightMetrics.get(key);
      if(!rightMetric||typeof leftMetric.value!=="number"||typeof rightMetric.value!=="number"||leftMetric.metricDefinitionSha256!==rightMetric.metricDefinitionSha256)return[];
      const delta=rightMetric.value-leftMetric.value;
      const direction=leftMetric.direction;
      const interpretation=delta===0?"no change":(
        direction==="lower_is_better"?(delta<0?"better on this metric":"worse on this metric"):
        direction==="higher_is_better"?(delta>0?"better on this metric":"worse on this metric"):
        "difference only"
      );
      return[{metricId:leftMetric.metricId,dimensions:leftMetric.dimensions,delta,unit:leftMetric.unit,direction,interpretation,denominator:leftMetric.denominator}];
    }):[];
    $("compare-result").innerHTML=`<div class="boundary ${eligible?"pass":"fail"}"><strong>${eligible?"Directly comparable":"Not directly comparable"}</strong><br>${eligible?"Every required comparison dimension matches.":"At least one required dimension is missing or differs; no delta chart is produced."}</div>
      <div style="overflow:auto"><table class="check-table"><thead><tr><th>Field</th><th>${esc(left.experimentId)}</th><th>${esc(right.experimentId)}</th><th>Match</th></tr></thead><tbody>
      ${checks.map(item=>`<tr><td>${esc(item.field)}</td><td>${esc(item.left)}</td><td>${esc(item.right)}</td><td class="${item.matches?"pass":"fail"}">${item.matches?"✓":"✕"}</td></tr>`).join("")}</tbody></table></div>
      ${eligible?`<div class="detail-block" style="margin-top:12px"><h3>Metric deltas · right minus left</h3>${deltas.length?`<div style="overflow:auto"><table class="metric-table"><thead><tr><th>Metric</th><th>Dimensions</th><th>Delta</th><th>Denominator</th><th>Interpretation</th></tr></thead><tbody>${deltas.map(item=>`<tr><td>${esc(item.metricId)}</td><td>${esc(Object.entries(item.dimensions).map(([k,v])=>`${k}=${v}`).join(", ")||"—")}</td><td>${item.delta>=0?"+":""}${esc(fmt(item.delta))} ${esc(item.unit)}</td><td>${esc(fmt(item.denominator))}</td><td>${esc(item.interpretation)}</td></tr>`).join("")}</tbody></table></div>`:"<p>No shared numeric metric observations with identical definitions.</p>"}</div>`:""}`;
  }

  function renderEvaluation(){
    const p=data.programState;
    const stages=[["Candidate rows",p.candidateLabels],["Supplied labels",0],["Valid labels",0],["Generalization-safe",p.safeLabels]];
    $("label-funnel").innerHTML=stages.map((item,index)=>`<div class="funnel-stage ${index>0?"stop":""}"><strong>${item[1]}</strong><span>${esc(item[0])}</span></div>`).join("");
    const ids=["CLASSIFICATION_ACCURACY_B0","CLASSIFICATION_ACCURACY_B1","CLASSIFICATION_MACRO_F1_B0","CLASSIFICATION_MACRO_F1_B1"];
    $("accuracy-panels").innerHTML=ids.map(id=>`<div class="empty-result"><strong>—</strong><span>${esc(id.replace("CLASSIFICATION_","").replaceAll("_"," "))}</span>${metricFooter(metrics[id])}</div>`).join("");
    const risks=[
      ["Leakage","Same-pattern evidence cannot enter generalization-safe metrics.","Blocked claim: generalization",p.safeLabels===0?"active":"controlled"],
      ["Small N","0/24 independent safe labels; N≥20 is only limited MSc evidence.","Blocked claim: accuracy",p.safeLabels<20?"active":"controlled"],
      ["Policy overfit","Freeze 16/8 development/holdout before policy inspection.","Blocked claim: held-out effect","active"],
      ["External validity","Require a new education-domain batch before broader claims.","Blocked claim: external validity","active"]
    ];
    $("validity-grid").innerHTML=risks.map(([title,copy,boundary,status])=>`<article class="risk-card"><span class="evidence-badge" data-evidence="${status==="active"?"blocked":"offline"}">${esc(status)}</span><h3>${esc(title)}</h3><p>${esc(copy)}</p><strong>${esc(boundary)}</strong></article>`).join("");
  }
  function renderIndependentEvidence(){
    const p=data.programState;
    const accepted=evidenceDecisions.decisions.filter(item=>item.outcome==="Accepted").length;
    $("independent-evidence-phase").innerHTML=`<strong>Current phase: calibration.</strong> ${accepted}/10 IE decisions are accepted. The two three-case calibration packages may be released after reviewer consent; all 24 evaluation cases remain sealed until two valid calibration returns and a human instruction freeze exist.`;
    $("independent-evidence-kpis").innerHTML=[
      kpi("Protocol decisions",`${accepted} / 10`,"<small>accepted · conversation recorded</small>"),
      kpi("Candidate rows",p.candidateLabels,"<small>blind evaluation set</small>"),
      kpi("Independent reviewers","0 / 2","<small>calibration returns required</small>"),
      kpi("Adjudicated labels",`${p.safeLabels} / ${p.candidateLabels}`,"<small>current safe gold set</small>"),
      kpi("Accuracy / macro-F1","—","<small>null at safe N=0</small>")
    ].join("");
    const later=[
      ["Unseen generalization","Freeze one candidate, open N=8 once, then replicate externally."],
      ["Lower human effort","Run counterbalanced EXP-026; annotation time alone is insufficient."],
      ["Paper superiority","Reconstruct an equivalent labeled cohort or report not directly comparable."],
      ["Best topology","Use EXP-034 Pareto evidence plus M-02; no single weighted winner."],
      ["Best routing rule","Use adjudicated routing targets, then freeze and test one rule."]
    ];
    $("independent-evidence-later").innerHTML=later.map(([title,copy])=>`<article class="workspace-item"><strong>${esc(title)}</strong><p>${esc(copy)}</p></article>`).join("");
  }
  function renderWorkspace(id,space){
    const items=data.experiments.filter(item=>item.researchSpace===space&&Number(item.id.slice(-3))>=19);
    $(id).innerHTML=items.map(item=>`<article class="workspace-item"><strong><bdi dir="ltr">${item.id}</bdi> · ${esc(item.status)}</strong><p>${esc(item.title)}</p><button type="button" data-exp="${item.id}">Open</button></article>`).join("");
    $(id).querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>openExperiment(button.dataset.exp,true)));
  }
  function renderOperations(){
    const security=metrics.OPS_SECURITY_CONTROLS_PASS;
    const acceptedExperiments=data.runStoreSummary.experimentsWithAcceptedRuns;
    $("operations-kpis").innerHTML=[
      kpi("Source hashes",data.sources.length,"<small>validated on catalog refresh</small>"),
      kpi("Accepted-run coverage",`${acceptedExperiments}/${data.experiments.length}`,"<small>absence stays visible</small>"),
      kpi("Security controls",`${security.value}/${security.denominator}`,metricFooter(security)),
      kpi("Baseline frozen","YES","<small>Agent 4 unchanged</small>"),
      kpi("Publication tier",data.publicationTier.replaceAll("_"," "),"<small>private raw records excluded</small>")
    ].join("");
    $("source-grid").innerHTML=data.sources.map(source=>`<article class="source-card"><strong>${esc(source.role)}</strong><p>${esc(source.path)}</p><code>sha256 ${esc(source.sha256)}</code></article>`).join("");
    $("catalog-provenance").textContent=`Generated ${data.generatedAt} from accepted source revision ${data.sourceRevision}. The UI contains no raw expert labels, transcripts, or controlled records.`;
  }
  function routeHash(){
    const hash=decodeURIComponent(location.hash.slice(1));
    if(hash.startsWith("experiment-"))openExperiment(hash.replace("experiment-",""),false);
    else if(hash.startsWith("architecture-"))document.getElementById(hash)?.scrollIntoView();
  }

  $("dialog-close").addEventListener("click",()=>{$("experiment-dialog").close();if(location.hash.startsWith("#experiment-"))history.replaceState(null,"","#experiments")});
  $("experiment-dialog").addEventListener("cancel",()=>{if(location.hash.startsWith("#experiment-"))history.replaceState(null,"","#experiments")});
  $("language-toggle").addEventListener("click",()=>setLanguage(language==="en"?"he":"en"));
  renderOverview();renderBaselineProgress();renderExperimentBenchmarks();renderExecutedResults();renderRunCenter();renderArchitecture();renderExperiments();renderResults();renderEvaluation();renderIndependentEvidence();
  renderWorkspace("msc-workspace","MSc");renderWorkspace("phd-workspace","PhD");renderOperations();setLanguage(language);routeHash();
  window.addEventListener("hashchange",routeHash);
})();
</script>
</body>
</html>
"""


def load_catalog(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schemaVersion") != "ExperimentCatalogSnapshot-v1":
        raise ValueError("BigUI requires ExperimentCatalogSnapshot-v1")
    return value


def load_independent_decisions(
    path: Path = DEFAULT_INDEPENDENT_DECISIONS,
) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(INDEPENDENT_DECISION_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    ).validate(value)
    return value


def render(catalog: dict) -> str:
    embedded = json.dumps(
        catalog, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).replace("</", "<\\/")
    decisions = json.dumps(
        load_independent_decisions(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    return (
        TEMPLATE.replace("__CATALOG__", embedded)
        .replace("__INDEPENDENT_DECISIONS__", decisions)
        .replace("\r\n", "\n")
    )


def safe_output(path: Path, controlled: bool) -> Path:
    target = path if path.is_absolute() else ROOT / path
    target = target.resolve()
    if controlled:
        allowed = (ROOT / "VEGO-AI" / "reports" / "results_dashboard").resolve()
        if target != allowed / "index.html":
            raise ValueError(
                "controlled BigUI output must be VEGO-AI/reports/results_dashboard/index.html"
            )
    elif target != DEFAULT_OUTPUT.resolve():
        raise ValueError("tracked BigUI output must be VEGO-AI-Research-Hub.html")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--controlled", action="store_true")
    args = parser.parse_args()
    if args.check and args.controlled:
        parser.error("--check validates the tracked BigUI only")
    try:
        catalog_path = (
            args.catalog if args.catalog.is_absolute() else ROOT / args.catalog
        )
        catalog = load_catalog(catalog_path)
        if args.controlled and catalog["publicationTier"] != "controlled_local":
            catalog = json.loads(json.dumps(catalog))
            catalog["publicationTier"] = "controlled_local"
        content = render(catalog)
        output = safe_output(args.output, args.controlled)
        if args.check:
            if not output.is_file() or output.read_text(encoding="utf-8") != content:
                print(f"STALE: {output.relative_to(ROOT)}", file=sys.stderr)
                return 1
            print("BigUI HTML: PASS")
            return 0
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8", newline="\n")
        print(f"WROTE: {output.relative_to(ROOT)}")
        return 0
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        jsonschema.ValidationError,
    ) as exc:
        print(f"BigUI HTML: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
