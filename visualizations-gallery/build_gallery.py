# -*- coding: utf-8 -*-
import glob, os, html
A="assets"
def cards(items, sec, light=False, big=False):
    out=[]
    cls="card light" if light else "card"
    if big: cls+=" big"
    for src,title,desc,new in items:
        badge='<span class="new">NEW</span>' if new else ''
        d=f'<div class="desc">{html.escape(desc)}</div>' if desc else ''
        out.append(f'''<figure class="{cls}" data-sec="{sec}">
  {badge}<div class="imgwrap"><img class="shot" loading="lazy" src="{src}" alt="{html.escape(title)}"></div>
  <figcaption><div class="title">{html.escape(title)}</div>{d}</figcaption></figure>''')
    return "\n".join(out)

# ---- Architecture ----
arch=[("assets/architecture/vego-ai-architecture-enhanced.png","Enhanced Co-Reasoning Architecture","Full flow + numbered artifact chain, AI review loop & human-gated evidence",False),
      ("assets/architecture/vego-ai-architecture-before-after.png","Architecture Evolution — Before → After","v1 pipeline vs v2 with review loop & evidence gate",False),
      ("assets/architecture/vego-ai-architecture-clean.png","Co-Reasoning Architecture — Clean Redraw","Original 4-agent layout, polished orthogonal flow",False)]

# ---- New slides ----
newmeta=[("Research Methodology — Design Science","DSR cycle mapped to chapters & milestones"),
 ("Literature Positioning Map","Four research streams and the gap this thesis fills"),
 ("Detailed Data Flow — Full Pipeline","End-to-end artifacts; baseline vs reusable-judgment extension"),
 ("Schema Dependency Chain","Six JSON schemas + const-enforced guarantees"),
 ("Evaluation Conditions Matrix (C0–C4B)","Layered contribution chain, status per condition"),
 ("Two-Tier Metrics Framework","Primary (effect) vs secondary (mechanism) metrics"),
 ("Current Evidence Dashboard","All quantitative evidence currently available"),
 ("Blind Annotation Protocol — Sequence","Two-reviewer, bias-controlled labeling workflow"),
 ("Leakage Control & Evidence Gate Flow","Per-row leakage tags and gate thresholds"),
 ("Experiment Registry (EXP-000–EXP-005)","All registered experiments and status"),
 ("Policy Sensitivity — Synthetic","7-row policy table; Δ = 0.00 pp (synthetic only)"),
 ("Contribution to Knowledge","Gregor & Hevner L1/L2 mapped to research questions"),
 ("Threats to Validity","Internal · external · construct · reliability + mitigations"),
 ("PhD Continuation Roadmap","M4B-2 → M6 with the MSc/PhD boundary"),
 ("Key References & Foundations","Core anchors mapped to design decisions")]
newfiles=sorted(glob.glob("assets/new/n*.png"))
new=[(f,newmeta[i][0],newmeta[i][1],True) for i,f in enumerate(newfiles)]

# ---- Deck (38) ----
decktitles=["Title — Reusable Human Judgment","Project Status at a Glance","The Problem",
 "Research Methodology — Design Science","Literature Positioning Map","VEGO-AI Baseline Pipeline (C0)",
 "Before vs After: Closing the Human Loop","Human–AI Co-Reasoning Artifact (M1–M4B-1)","Detailed Data Flow — Full Pipeline",
 "Schema Dependency Chain","Architecture Evolution","M1 Selective Review + M2 Structured Feedback",
 "M3 Judgment Memory + M4A Advisory","M4B-1 Deterministic Parallel Comparison","Evaluation Conditions Matrix (C0–C4B)",
 "Two-Tier Metrics Framework","Current Evidence Dashboard","Running Example: Customer as Actor",
 "Interaction Sequence: Row Processing","Evidence Flow & Integrity Chain","Data Architecture & Schema Chain",
 "Experiment Status Dashboard","Experiment Registry (EXP-000–EXP-005)","Policy Sensitivity Analysis — Synthetic",
 "Evaluation Methodology","Blind Annotation Protocol — Sequence","Leakage Control & Evidence Gate Flow",
 "Five Design Principles","AI Review Loop Process","Comparison Dashboard: C0 vs Artifact",
 "Thesis Structure (10 Chapters + Appendix)","Research Questions → Artifact Mapping","Contribution to Knowledge",
 "Threats to Validity","Critical Path Forward","PhD Continuation Roadmap","Key References & Foundations","Thank You"]
NEWPOS={4,5,9,10,15,16,17,23,24,26,27,33,34,36,37}
deckfiles=sorted(glob.glob("assets/deck/deck-*.jpg"))
deck=[(f,f"{i+1}. {decktitles[i]}","",(i+1) in NEWPOS) for i,f in enumerate(deckfiles)]

# ---- Figures ----
fignames={"ec_E1_leakage_distribution":"Leakage-status distribution","ec_E2_advice_strength":"M4A advice-strength distribution",
 "ec_E3_escalation_and_change":"Escalation & classification change","ec_E4_label_coverage":"Label coverage",
 "exp003_label_coverage":"EXP-003 · Label coverage","exp003_memory_advice_strength":"EXP-003 · Memory advice strength",
 "sd_01_research_spine":"Research spine","sd_02_milestone_architecture":"Milestone architecture",
 "sd_03_non_destructive_boundary":"Non-destructive boundary","sd_04_artifact_chain":"Artifact chain",
 "sd_05_dashboard_snapshot":"Dashboard snapshot","sd_06_validation_gate":"Validation gate",
 "sd_07_exp001_findings":"EXP-001 findings","sd_08_exp002_workflow":"EXP-002 workflow",
 "sd_F4_review_cases_by_setting":"Review cases by setting","sd_F5_m4a_advice_strength":"M4A advice strength",
 "sd_F6_exp002_label_readiness":"EXP-002 label readiness","sd_F7_claim_boundary":"Claim boundary"}
figfiles=sorted(glob.glob("assets/figures/*.svg"))
figs=[(f,fignames.get(os.path.splitext(os.path.basename(f))[0],os.path.basename(f)),"",False) for f in figfiles]

CSS="""
:root{--bg:#0A0A12;--p1:#1B1430;--p2:#120C20;--edge:#9333EA;--neon:#A855F7;--neon2:#C084FC;--ink:#F6F3FF;--txt:#D8D3EA;--mut:#9A93B4;--faint:#6E6786;--green:#10B981;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font-family:'Segoe UI',Helvetica,Arial,sans-serif;line-height:1.5;-webkit-font-smoothing:antialiased}
a{color:var(--neon2);text-decoration:none}
.orb{position:fixed;border-radius:50%;filter:blur(40px);z-index:0;pointer-events:none;opacity:.5}
.orb1{width:560px;height:560px;left:-160px;top:-160px;background:radial-gradient(circle,#7C3AED,transparent 70%)}
.orb2{width:620px;height:620px;right:-200px;bottom:-220px;background:radial-gradient(circle,#C026D3,transparent 70%)}
.wrap{position:relative;z-index:1;max-width:1320px;margin:0 auto;padding:0 28px}
header.hero{padding:64px 0 26px}
.kick{color:var(--neon2);font-weight:700;letter-spacing:3px;font-size:13px;text-transform:uppercase}
h1{font-size:42px;color:var(--ink);margin:10px 0 8px;line-height:1.1}
.sub{color:var(--mut);font-size:18px;max-width:820px}
.counts{display:flex;gap:14px;flex-wrap:wrap;margin-top:24px}
.pill{background:linear-gradient(180deg,var(--p1),var(--p2));border:1px solid rgba(147,51,234,.55);border-radius:14px;padding:14px 20px;min-width:120px}
.pill b{display:block;font-size:30px;color:var(--neon2);font-weight:800}
.pill span{font-size:12px;color:var(--mut);letter-spacing:.6px;text-transform:uppercase}
nav.secnav{position:sticky;top:0;z-index:20;background:rgba(10,10,18,.82);backdrop-filter:blur(10px);border-bottom:1px solid rgba(147,51,234,.28);padding:12px 0;margin:26px 0 0}
nav.secnav .wrap{display:flex;gap:8px;flex-wrap:wrap}
nav.secnav a{font-size:13.5px;color:var(--txt);border:1px solid rgba(147,51,234,.4);border-radius:999px;padding:7px 15px}
nav.secnav a:hover{background:rgba(168,85,247,.18);color:#fff}
section{padding:40px 0 8px}
.sechead{display:flex;align-items:baseline;gap:14px;margin-bottom:6px}
.sechead h2{font-size:27px;color:var(--ink)}
.sechead .n{color:var(--neon2);font-weight:700;font-size:14px;border:1px solid rgba(147,51,234,.5);border-radius:999px;padding:3px 12px}
.secsub{color:var(--mut);font-size:15px;margin-bottom:20px}
.grid{display:grid;gap:18px}
.g-arch{grid-template-columns:1fr}
.g-new{grid-template-columns:repeat(auto-fill,minmax(330px,1fr))}
.g-deck{grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}
.g-fig{grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}
.card{position:relative;background:linear-gradient(180deg,var(--p1),var(--p2));border:1px solid rgba(147,51,234,.45);border-radius:16px;overflow:hidden;transition:transform .15s,box-shadow .15s,border-color .15s}
.card:hover{transform:translateY(-4px);border-color:var(--neon);box-shadow:0 12px 34px rgba(124,58,237,.35)}
.imgwrap{cursor:zoom-in;display:flex;align-items:center;justify-content:center;background:#0c0a14}
.card.light .imgwrap{background:#ffffff}
.card .shot{width:100%;height:auto;display:block}
.card.big .imgwrap{padding:0}
figcaption{padding:13px 15px 15px}
.title{color:var(--ink);font-weight:600;font-size:15px}
.desc{color:var(--mut);font-size:12.5px;margin-top:4px}
.new{position:absolute;top:10px;right:10px;z-index:3;background:var(--neon);color:#fff;font-size:11px;font-weight:800;letter-spacing:.5px;padding:4px 9px;border-radius:999px;box-shadow:0 0 14px rgba(168,85,247,.8)}
footer{padding:50px 0 70px;color:var(--faint);font-size:13px;border-top:1px solid rgba(147,51,234,.2);margin-top:40px}
#lb{position:fixed;inset:0;z-index:100;background:rgba(5,4,10,.94);display:none;align-items:center;justify-content:center}
#lb.on{display:flex}
#lb img{max-width:94vw;max-height:88vh;border-radius:10px;box-shadow:0 0 60px rgba(124,58,237,.5)}
#lb .cap{position:fixed;bottom:22px;left:0;right:0;text-align:center;color:var(--txt);font-size:15px}
#lb .x{position:fixed;top:20px;right:26px;font-size:30px;color:#fff;cursor:pointer;opacity:.8}
#lb .nav{position:fixed;top:50%;transform:translateY(-50%);font-size:46px;color:#fff;cursor:pointer;opacity:.7;user-select:none;padding:0 22px}
#lb .prev{left:6px}#lb .next{right:6px}
#lb .nav:hover,#lb .x:hover{opacity:1}
"""

JS="""
const shots=[...document.querySelectorAll('.shot')];
const lb=document.getElementById('lb'),lbimg=document.getElementById('lbimg'),lbcap=document.getElementById('lbcap');
let idx=0;
function open(i){idx=i;lbimg.src=shots[i].src;lbcap.textContent=shots[i].alt;lb.classList.add('on');}
function close(){lb.classList.remove('on');lbimg.src='';}
function step(d){idx=(idx+d+shots.length)%shots.length;lbimg.src=shots[idx].src;lbcap.textContent=shots[idx].alt;}
shots.forEach((s,i)=>s.addEventListener('click',()=>open(i)));
document.getElementById('lbx').onclick=close;
document.getElementById('lbprev').onclick=e=>{e.stopPropagation();step(-1);};
document.getElementById('lbnext').onclick=e=>{e.stopPropagation();step(1);};
lb.addEventListener('click',e=>{if(e.target===lb)close();});
document.addEventListener('keydown',e=>{if(!lb.classList.contains('on'))return;if(e.key==='Escape')close();if(e.key==='ArrowRight')step(1);if(e.key==='ArrowLeft')step(-1);});
"""

def section(sid,n,title,sub,grid,html_cards):
    return f'''<section id="{sid}"><div class="wrap">
<div class="sechead"><h2>{title}</h2><span class="n">{n}</span></div>
<div class="secsub">{sub}</div>
<div class="grid {grid}">{html_cards}</div></div></section>'''

doc=f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>VEGO-AI — Visualization Gallery</title><style>{CSS}</style></head><body>
<div class="orb orb1"></div><div class="orb orb2"></div>
<header class="hero"><div class="wrap">
<div class="kick">VEGO-AI · Reusable Human Judgment in AI-Assisted Domain Model Assessment</div>
<h1>Visualization Gallery</h1>
<div class="sub">Every diagram, slide, and figure produced for the thesis — architecture diagrams, the 38-slide defense deck (15 new research visualizations), and the project's existing figures. Click any image to enlarge.</div>
<div class="counts">
<div class="pill"><b>3</b><span>Architecture diagrams</span></div>
<div class="pill"><b>15</b><span>New research visuals</span></div>
<div class="pill"><b>38</b><span>Deck slides</span></div>
<div class="pill"><b>18</b><span>Project figures</span></div>
</div></div></header>
<nav class="secnav"><div class="wrap">
<a href="#arch">Architecture</a><a href="#new">New research visuals</a><a href="#deck">Full deck (38)</a><a href="#figs">Project figures</a>
</div></nav>
{section("arch","3","Architecture Diagrams","The VEGO-AI multi-agent co-reasoning pipeline — three views.","g-arch",cards(arch,"arch",light=True,big=True))}
{section("new","15","New Research Visualizations","Built for the thesis defense deck and inserted into the presentation.","g-new",cards(new,"new"))}
{section("deck","38","Full Thesis Defense Deck","All 38 slides in order — the 15 new visualizations are tagged NEW.","g-deck",cards(deck,"deck"))}
{section("figs","18","Existing Project Figures","Previously generated figures from the repository (supervisor demo, evaluation & EXP-003).","g-fig",cards(figs,"figs",light=True))}
<footer><div class="wrap">VEGO-AI — Visualization Gallery · generated {os.popen("date +%Y-%m-%d").read().strip()} · Ali Ahmed · MSc Information Systems</div></footer>
<div id="lb"><span class="x" id="lbx">&times;</span><span class="nav prev" id="lbprev">&#8249;</span><img id="lbimg" alt=""><span class="nav next" id="lbnext">&#8250;</span><div class="cap" id="lbcap"></div></div>
<script>{JS}</script></body></html>'''
open("index.html","w",encoding="utf-8").write(doc)
print("index.html written:",len(doc),"bytes")
print("cards: arch",len(arch),"new",len(new),"deck",len(deck),"figs",len(figs))
