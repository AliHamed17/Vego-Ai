#!/usr/bin/env python3
"""Build the blinded EXP-019/020 independent-evidence package.

The generated package is local and ignored. It contains no supplied labels and
never exposes Agent 4 labels, memory advice, leakage state, or the sealed split
to reviewers. The private mapping is written separately for later adjudication
and evaluation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import random
import shutil
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "reports/generated/exp002/expert_labeling_sheet.csv"
DEFAULT_OUTPUT = ROOT / "reports/generated/independent_evidence_v1"
SCHEMA = ROOT / "schemas/independent-evidence-package-v1.schema.json"
PACKAGE_VERSION = "1.0.0"
GENERATED_AT = "2026-07-26T00:00:00Z"
PARTITION_SEED = 2026
REVIEWER_SEEDS = (2027, 2028)
HOLDOUT_PER_SETTING = {"cd_ch": 1, "cd_pw": 2, "ucd_ch": 2, "ucd_pw": 3}
LABELS = [
    "Substantial Variability",
    "Occasional Variability",
    "Undetermined / Needs Review",
]
DOMAIN = {
    "ucd_ch": "Cheers",
    "cd_ch": "Cheers",
    "ucd_pw": "ParkWise",
    "cd_pw": "ParkWise",
}
DIAGRAM = {
    "ucd_ch": "Use-case diagram",
    "ucd_pw": "Use-case diagram",
    "cd_ch": "Class diagram",
    "cd_pw": "Class diagram",
}
PUBLIC_FIELDS = [
    "anonymous_item_id",
    "setting",
    "domain",
    "diagram_type",
    "related_guideline_id",
    "affected_cases",
    "pattern_description",
]
REVIEW_FIELDS = [
    "expert_label",
    "expert_rationale",
    "confidence",
    "review_requirement",
    "routing_rationale",
    "review_priority",
    "reviewer_id",
    "review_date",
    "active_seconds",
    "notes",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def load_source(path: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 27:
        raise ValueError(f"expected 27 source rows, found {len(rows)}")
    safe = [row for row in rows if truthy(row.get("generalization_safe_candidate", ""))]
    calibration = [row for row in rows if row not in safe]
    if len(safe) != 24 or len(calibration) != 3:
        raise ValueError(
            "expected 24 generalization-safe rows and 3 calibration rows; "
            f"found {len(safe)} and {len(calibration)}"
        )
    return safe, calibration


def public_item(row: dict[str, str], anonymous_id: str) -> dict[str, str]:
    setting = row["setting"]
    return {
        "anonymous_item_id": anonymous_id,
        "setting": setting,
        "domain": DOMAIN.get(setting, setting),
        "diagram_type": DIAGRAM.get(setting, ""),
        "related_guideline_id": row.get("related_guideline_id", ""),
        "affected_cases": row.get("affected_cases", ""),
        "pattern_description": row.get("pattern_description", ""),
    }


def assign_items(
    safe_rows: list[dict[str, str]],
    calibration_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    ordered_safe = sorted(safe_rows, key=lambda row: (row["setting"], row["pattern_id"]))
    ordered_calibration = sorted(
        calibration_rows,
        key=lambda row: (row["setting"], row["pattern_id"]),
    )
    safe_items: list[dict[str, str]] = []
    calibration_items: list[dict[str, str]] = []
    private_rows: list[dict[str, str]] = []

    split_by_key: dict[tuple[str, str], str] = {}
    rng = random.Random(PARTITION_SEED)
    for setting, holdout_count in HOLDOUT_PER_SETTING.items():
        setting_rows = [row for row in ordered_safe if row["setting"] == setting]
        rng.shuffle(setting_rows)
        for index, row in enumerate(setting_rows):
            split_by_key[(row["setting"], row["pattern_id"])] = (
                "sealed_holdout" if index < holdout_count else "development"
            )

    for index, row in enumerate(ordered_safe, 1):
        anonymous_id = f"ITEM-{index:02d}"
        safe_items.append(public_item(row, anonymous_id))
        private_rows.append(
            {
                "anonymous_item_id": anonymous_id,
                "setting": row["setting"],
                "pattern_id": row["pattern_id"],
                "partition": split_by_key[(row["setting"], row["pattern_id"])],
                "leakage_class": row.get("evaluation_leakage_status", ""),
                "generalization_safe": "true",
                "original_agent4_classification": row.get(
                    "original_agent4_classification", ""
                ),
                "memory_informed_classification": row.get(
                    "memory_informed_classification", ""
                ),
                "baseline_requires_human_review": row.get(
                    "requires_human_review", ""
                ),
                "memory_requires_human_review": row.get(
                    "requires_human_review_after_memory", ""
                ),
            }
        )

    for index, row in enumerate(ordered_calibration, 1):
        anonymous_id = f"CAL-{index:02d}"
        calibration_items.append(public_item(row, anonymous_id))
        private_rows.append(
            {
                "anonymous_item_id": anonymous_id,
                "setting": row["setting"],
                "pattern_id": row["pattern_id"],
                "partition": "calibration",
                "leakage_class": row.get("evaluation_leakage_status", ""),
                "generalization_safe": "false",
                "original_agent4_classification": row.get(
                    "original_agent4_classification", ""
                ),
                "memory_informed_classification": row.get(
                    "memory_informed_classification", ""
                ),
                "baseline_requires_human_review": row.get(
                    "requires_human_review", ""
                ),
                "memory_requires_human_review": row.get(
                    "requires_human_review_after_memory", ""
                ),
            }
        )

    development = sum(row["partition"] == "development" for row in private_rows)
    holdout = sum(row["partition"] == "sealed_holdout" for row in private_rows)
    if development != 16 or holdout != 8:
        raise ValueError(f"partition must be 16/8, found {development}/{holdout}")
    return safe_items, calibration_items, private_rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = PUBLIC_FIELDS + REVIEW_FIELDS
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def json_for_script(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace(
        "<", "\\u003c"
    )


def reviewer_html(
    *,
    items: list[dict[str, str]],
    slot: str,
    phase: str,
    source_sheet_sha256: str,
) -> str:
    expected = len(items)
    title = (
        "VEGO-AI reviewer calibration"
        if phase == "calibration"
        else "VEGO-AI independent expert review"
    )
    phase_note = (
        "These three cases calibrate the vocabulary. They are excluded from all "
        "accuracy and generalization measurements."
        if phase == "calibration"
        else "These cases are blind: no Agent 4 label, memory advice, leakage "
        "state, or development/holdout assignment is shown."
    )
    data = json_for_script(items)
    labels = json_for_script(LABELS)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · {html.escape(slot)}</title>
<style>
:root{{--ink:#e9f0f7;--muted:#9eafc0;--bg:#07111d;--panel:#102033;--line:#28435f;
--blue:#5ec8ff;--green:#70e1a1;--amber:#ffd47a;--danger:#ff8c8c}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}
header,main,footer{{width:min(980px,calc(100% - 28px));margin:auto}}
header{{padding:28px 0 16px}} h1{{font-size:clamp(1.55rem,4vw,2.4rem);margin:.2rem 0}}
.notice,.card,.controls{{background:var(--panel);border:1px solid var(--line);
border-radius:16px;padding:18px}} .notice{{border-left:5px solid var(--amber)}}
.controls{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:16px 0}}
label{{display:block;font-weight:700}} input,textarea,select,button{{width:100%;margin-top:6px;
padding:10px;border-radius:9px;border:1px solid var(--line);background:#081522;color:var(--ink);
font:inherit}} textarea{{min-height:100px;resize:vertical}} button{{cursor:pointer;font-weight:800}}
button.primary{{background:#0f5d85;border-color:var(--blue)}} button.secondary{{background:#18314a}}
.progress{{height:12px;background:#06101a;border-radius:9px;overflow:hidden;margin:10px 0}}
.progress span{{display:block;height:100%;background:var(--green);width:0}}
.meta{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:12px 0}}
.meta div{{background:#091827;border:1px solid var(--line);padding:10px;border-radius:10px}}
.meta strong{{display:block;color:var(--muted);font-size:.78rem;text-transform:uppercase}}
.choices{{display:grid;gap:8px;margin:14px 0}} .choice{{display:flex;gap:10px;align-items:flex-start;
background:#091827;border:1px solid var(--line);padding:10px;border-radius:10px}}
.choice input{{width:auto;margin:4px 0 0}} .choice label{{font-weight:600;flex:1}}
.nav{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:15px}}
.status{{color:var(--muted)}} .hidden{{display:none!important}} footer{{padding:22px 0 40px;color:var(--muted)}}
:focus-visible{{outline:3px solid var(--blue);outline-offset:2px}}
@media(max-width:620px){{.controls,.meta{{grid-template-columns:1fr}}}}
@media(prefers-reduced-motion:no-preference){{.progress span{{transition:width .2s ease}}}}
@media print{{.controls,.nav,.export{{display:none}}body{{background:white;color:black}}.card,.notice{{border-color:#555;background:white}}}}
</style>
</head>
<body>
<header>
<p class="status">Independent evidence · {html.escape(slot)} · {html.escape(phase)}</p>
<h1>{html.escape(title)}</h1>
<div class="notice"><strong>Human review only.</strong> {html.escape(phase_note)}
Do not consult VEGO-AI outputs, another reviewer, or generative AI while labeling.</div>
</header>
<main>
<section class="controls" aria-label="Reviewer information">
<label>Anonymous reviewer ID<input id="reviewer-id" autocomplete="off" placeholder="expert_01"></label>
<label>Review date<input id="review-date" type="date"></label>
<label style="grid-column:1/-1"><input id="protocol-confirm" type="checkbox" style="width:auto;margin-right:8px">
I confirm that the approved review instructions and data-use information were provided to me.</label>
</section>
<section class="card">
<div id="counter" class="status"></div>
<div class="progress" aria-label="Completion progress"><span id="bar"></span></div>
<h2 id="item-title"></h2>
<div id="meta" class="meta"></div>
<h3>Pattern description</h3><p id="description"></p>
<fieldset class="choices"><legend><strong>Your expert classification</strong></legend>
<div id="choices"></div></fieldset>
<label>Rationale<textarea id="rationale" placeholder="Explain why this label is appropriate."></textarea></label>
<label>Confidence<select id="confidence"><option value="">Select…</option><option>Low</option><option>Medium</option><option>High</option></select></label>
<fieldset class="choices"><legend><strong>Should this case be routed to a human?</strong></legend>
<div id="routing-choices"></div></fieldset>
<label>Routing rationale<textarea id="routing-rationale" placeholder="Explain why human review is or is not required."></textarea></label>
<label>Review priority<select id="review-priority"><option value="">Select…</option><option>Low</option><option>Medium</option><option>High</option></select></label>
<label>Optional notes<textarea id="notes" placeholder="Ambiguity, assumptions, or missing information."></textarea></label>
<div class="nav"><button id="previous" class="secondary">Previous</button><button id="next" class="primary">Next</button></div>
</section>
<section class="card export" style="margin-top:16px">
<h2>Local export</h2>
<p>No information is sent over the network. Export only when all {expected} cases are complete.</p>
<div class="nav"><button id="export-json" class="primary">Export JSON return</button><button id="export-csv" class="secondary">Export CSV return</button></div>
<p id="export-status" class="status" role="status"></p>
</section>
</main>
<footer>Package {PACKAGE_VERSION} · source {source_sheet_sha256[:12]}… · baseline labels intentionally hidden.</footer>
<script>
const ITEMS={data}, LABELS={labels}, SLOT={json.dumps(slot)}, PHASE={json.dumps(phase)},
ROUTING=["Human review required","Automatic handling acceptable","Insufficient context"],
SOURCE_SHA={json.dumps(source_sheet_sha256)}, VERSION={json.dumps(PACKAGE_VERSION)};
const key=`vego-independent-${{VERSION}}-${{SLOT}}-${{PHASE}}`;
const initial=()=>({{index:0,reviewerId:"",reviewDate:new Date().toISOString().slice(0,10),
confirmed:false,records:Object.fromEntries(ITEMS.map(x=>[x.anonymous_item_id,
{{expertLabel:"",expertRationale:"",confidence:"",notes:"",activeSeconds:0}}]))}});
let state; try{{state=JSON.parse(localStorage.getItem(key))||initial()}}catch(_e){{state=initial()}}
const $=id=>document.getElementById(id), esc=s=>String(s??"").replace(/[&<>"']/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[c]));
function save(){{localStorage.setItem(key,JSON.stringify(state))}}
function current(){{return ITEMS[state.index]}}
function complete(r){{return !!(r.expertLabel&&r.expertRationale.trim().length>=3&&r.confidence&&
r.reviewRequirement&&r.routingRationale?.trim().length>=3&&r.reviewPriority)}}
function capture(){{const id=current().anonymous_item_id,r=state.records[id];
r.expertLabel=document.querySelector('input[name=label]:checked')?.value||"";
r.expertRationale=$("rationale").value;r.confidence=$("confidence").value;r.notes=$("notes").value;
r.reviewRequirement=document.querySelector('input[name=routing]:checked')?.value||"";
r.routingRationale=$("routing-rationale").value;r.reviewPriority=$("review-priority").value;
state.reviewerId=$("reviewer-id").value.trim();state.reviewDate=$("review-date").value;
state.confirmed=$("protocol-confirm").checked;save()}}
function render(){{const item=current(),r=state.records[item.anonymous_item_id];
$("reviewer-id").value=state.reviewerId;$("review-date").value=state.reviewDate;
$("protocol-confirm").checked=state.confirmed;$("counter").textContent=`Case ${{state.index+1}} of ${{ITEMS.length}}`;
$("bar").style.width=`${{100*Object.values(state.records).filter(complete).length/ITEMS.length}}%`;
$("item-title").textContent=item.anonymous_item_id;
$("meta").innerHTML=[["Setting",item.setting],["Domain",item.domain],["Diagram",item.diagram_type],
["Guideline",item.related_guideline_id],["Affected cases",item.affected_cases]].map(([a,b])=>`<div><strong>${{esc(a)}}</strong>${{esc(b||"Not supplied")}}</div>`).join("");
$("description").textContent=item.pattern_description||"No description supplied.";
$("choices").innerHTML=LABELS.map(label=>`<div class="choice"><input type="radio" name="label" id="l-${{LABELS.indexOf(label)}}" value="${{esc(label)}}" ${{r.expertLabel===label?"checked":""}}><label for="l-${{LABELS.indexOf(label)}}">${{esc(label)}}</label></div>`).join("");
$("routing-choices").innerHTML=ROUTING.map(value=>`<div class="choice"><input type="radio" name="routing" id="r-${{ROUTING.indexOf(value)}}" value="${{esc(value)}}" ${{r.reviewRequirement===value?"checked":""}}><label for="r-${{ROUTING.indexOf(value)}}">${{esc(value)}}</label></div>`).join("");
$("rationale").value=r.expertRationale;$("confidence").value=r.confidence;$("notes").value=r.notes;
$("routing-rationale").value=r.routingRationale||"";$("review-priority").value=r.reviewPriority||"";
$("previous").disabled=state.index===0;$("next").textContent=state.index===ITEMS.length-1?"Finish":"Next";
}}
function validateAll(){{capture();if(!state.confirmed)throw new Error("Confirm the approved protocol first.");
if(!state.reviewerId||state.reviewerId.length<3)throw new Error("Enter a stable anonymous reviewer ID.");
if(!state.reviewDate)throw new Error("Enter the review date.");
const missing=ITEMS.filter(x=>!complete(state.records[x.anonymous_item_id])).map(x=>x.anonymous_item_id);
if(missing.length)throw new Error(`Complete all cases. Missing: ${{missing.join(", ")}}`)}}
function records(){{return ITEMS.map(x=>{{const r=state.records[x.anonymous_item_id];return {{
anonymousItemId:x.anonymous_item_id,expertLabel:r.expertLabel,expertRationale:r.expertRationale.trim(),
confidence:r.confidence,reviewRequirement:r.reviewRequirement,routingRationale:r.routingRationale.trim(),
reviewPriority:r.reviewPriority,reviewDate:state.reviewDate,activeSeconds:r.activeSeconds,notes:r.notes.trim()}}}})}}
function download(name,text,type){{const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([text],{{type}}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}}
document.addEventListener("input",()=>{{capture()}});$("previous").onclick=()=>{{capture();state.index=Math.max(0,state.index-1);save();render()}};
$("next").onclick=()=>{{capture();if(state.index<ITEMS.length-1)state.index++;save();render()}};
$("export-json").onclick=()=>{{try{{validateAll();const payload={{schemaVersion:PHASE==="evaluation"?"IndependentReviewReturn-v1":"IndependentCalibrationReturn-v1",packageVersion:VERSION,reviewerSlot:SLOT,reviewerId:state.reviewerId,sourceSheetSha256:SOURCE_SHA,completedAt:new Date().toISOString(),records:records()}};download(`${{SLOT}}-${{PHASE}}-return.json`,JSON.stringify(payload,null,2)+"\\n","application/json");$("export-status").textContent="JSON export created."}}catch(e){{$("export-status").textContent=e.message}}}};
$("export-csv").onclick=()=>{{try{{validateAll();const head=["anonymous_item_id","expert_label","expert_rationale","confidence","review_requirement","routing_rationale","review_priority","reviewer_id","review_date","active_seconds","notes"];const q=v=>`"${{String(v??"").replaceAll('"','""')}}"`;const lines=[head.join(","),...records().map(r=>[r.anonymousItemId,r.expertLabel,r.expertRationale,r.confidence,r.reviewRequirement,r.routingRationale,r.reviewPriority,state.reviewerId,r.reviewDate,r.activeSeconds,r.notes].map(q).join(","))];download(`${{SLOT}}-${{PHASE}}-return.csv`,lines.join("\\r\\n")+"\\r\\n","text/csv");$("export-status").textContent="CSV export created."}}catch(e){{$("export-status").textContent=e.message}}}};
setInterval(()=>{{if(!document.hidden){{state.records[current().anonymous_item_id].activeSeconds++;save()}}}},1000);
render();
</script>
</body>
</html>
"""


def write_private_mapping(path: Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "anonymous_item_id",
        "setting",
        "pattern_id",
        "partition",
        "leakage_class",
        "generalization_safe",
        "original_agent4_classification",
        "memory_informed_classification",
        "baseline_requires_human_review",
        "memory_requires_human_review",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_adjudication(path: Path, items: list[dict[str, str]]) -> None:
    fields = [
        "anonymous_item_id",
        "reviewer_1_label",
        "reviewer_1_rationale",
        "reviewer_1_confidence",
        "reviewer_1_review_requirement",
        "reviewer_1_routing_rationale",
        "reviewer_1_review_priority",
        "reviewer_2_label",
        "reviewer_2_rationale",
        "reviewer_2_confidence",
        "reviewer_2_review_requirement",
        "reviewer_2_routing_rationale",
        "reviewer_2_review_priority",
        "agreement_status",
        "adjudicated_label",
        "adjudicated_rationale",
        "adjudicated_review_requirement",
        "adjudicated_routing_rationale",
        "adjudicated_review_priority",
        "adjudicator_id",
        "adjudication_date",
        "notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for item in items:
            writer.writerow({"anonymous_item_id": item["anonymous_item_id"]})


def write_gold_template(path: Path, items: list[dict[str, str]]) -> None:
    fields = [
        "anonymous_item_id",
        "gold_label",
        "gold_rationale",
        "gold_review_requirement",
        "gold_routing_rationale",
        "gold_review_priority",
        "adjudicator_id",
        "adjudication_date",
        "reviewer_1_return_sha256",
        "reviewer_2_return_sha256",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for item in items:
            writer.writerow({"anonymous_item_id": item["anonymous_item_id"]})


def write_docs(output: Path, source_sha: str) -> None:
    (output / "README.md").write_text(
        """# Independent Evidence Package v1

This local package starts EXP-019 reviewer calibration and prepares EXP-020.
It contains no expert labels.

## Required order

1. Iris/Arnon record the ethics, consent, anonymity, storage, and reviewer-role decisions.
2. Send each reviewer only their calibration HTML.
3. Preserve both calibration returns unchanged; discuss discrepancies.
4. Freeze the clarified instruction version.
5. Send each reviewer only their evaluation HTML.
6. Preserve both raw returns unchanged and validate them.
7. Compute agreement before adjudication.
8. Adjudicate disagreements and freeze gold labels.
9. Run development-only baseline/error and routing/retrieval analysis.
10. Keep the eight-row holdout sealed until a deterministic policy is approved and frozen.

Never send `private/` to reviewers. Never copy AI labels into a reviewer return.
""",
        encoding="utf-8",
        newline="\n",
    )
    (output / "REVIEWER_INSTRUCTIONS.md").write_text(
        f"""# Independent reviewer instructions

You are labeling recurring variability patterns in student domain models.

Choose exactly one label:

- {LABELS[0]}
- {LABELS[1]}
- {LABELS[2]}

Judge only the pattern description, domain, diagram type, affected cases, and
guideline reference shown in your blind page. Do not consult VEGO-AI output,
Human Judgment Memory, another reviewer, or generative AI.

For every case provide a rationale of at least three characters and confidence
(`Low`, `Medium`, or `High`). Independently record whether the case should be
routed to a human, the routing rationale, and review priority. Use
`Undetermined / Needs Review` and `Insufficient context` when the available
neutral context is insufficient.

The page stores progress in your browser and makes local JSON/CSV downloads.
It makes no network request. Send the exported return through the approved
research channel.

Source package hash: `{source_sha}`.
""",
        encoding="utf-8",
        newline="\n",
    )
    (output / "SUPERVISOR_APPROVAL_CHECKLIST.md").write_text(
        """# Supervisor approval checklist

Record before reviewer outreach:

- [ ] Reviewer roles and required expertise are approved.
- [ ] Consent or ethics/IRB requirements are recorded.
- [ ] Reviewer anonymity/pseudonym policy is recorded.
- [ ] Approved transfer channel for reviewer returns is recorded.
- [ ] Storage location and retention period are recorded.
- [ ] Two reviewers will work independently.
- [ ] Adjudicator role is identified.
- [ ] The 16/8 private partition remains hidden.
- [ ] No AI, memory, or synthetic label is treated as ground truth.
- [ ] Accuracy claims remain blocked until adjudicated safe labels exist.
""",
        encoding="utf-8",
        newline="\n",
    )
    returns = output / "returns"
    returns.mkdir(exist_ok=True)
    (returns / "README.md").write_text(
        """# Raw returns

Place reviewer exports here unchanged. Do not commit this directory.

Expected names:

- `reviewer_1_calibration_return.json`
- `reviewer_2_calibration_return.json`
- `reviewer_1_evaluation_return.json`
- `reviewer_2_evaluation_return.json`

Raw returns are immutable evidence. Correct mistakes through an adjudication
record, never by editing the returned files.
""",
        encoding="utf-8",
        newline="\n",
    )


def build(source: Path, output: Path) -> dict[str, Any]:
    safe_rows, calibration_rows = load_source(source)
    safe, calibration, private_rows = assign_items(safe_rows, calibration_rows)
    if output.exists():
        shutil.rmtree(output)
    (output / "private").mkdir(parents=True)
    source_sha = sha256_file(source)

    generated: list[tuple[Path, str, bool, bool]] = []
    for index, seed in enumerate(REVIEWER_SEEDS, 1):
        slot = f"reviewer_{index}"
        evaluation_order = list(safe)
        calibration_order = list(calibration)
        random.Random(seed).shuffle(evaluation_order)
        random.Random(seed + 100).shuffle(calibration_order)
        evaluation_csv = output / f"{slot}_evaluation.csv"
        calibration_csv = output / f"{slot}_calibration.csv"
        evaluation_html = output / f"{slot}_evaluation.html"
        calibration_html = output / f"{slot}_calibration.html"
        write_csv(evaluation_csv, evaluation_order)
        write_csv(calibration_csv, calibration_order)
        evaluation_html.write_text(
            reviewer_html(
                items=evaluation_order,
                slot=slot,
                phase="evaluation",
                source_sheet_sha256=source_sha,
            ),
            encoding="utf-8",
            newline="\n",
        )
        calibration_html.write_text(
            reviewer_html(
                items=calibration_order,
                slot=slot,
                phase="calibration",
                source_sheet_sha256=source_sha,
            ),
            encoding="utf-8",
            newline="\n",
        )
        generated.extend(
            [
                (evaluation_csv, "empty evaluation CSV template", True, False),
                (evaluation_html, "interactive blind evaluation", True, False),
                (calibration_csv, "empty calibration CSV template", True, False),
                (calibration_html, "interactive blind calibration", True, False),
            ]
        )

    mapping = output / "private/item_mapping_PRIVATE.csv"
    adjudication = output / "private/adjudication_template.csv"
    gold = output / "private/gold_labels_template.csv"
    write_private_mapping(mapping, private_rows)
    write_adjudication(adjudication, safe)
    write_gold_template(gold, safe)
    write_docs(output, source_sha)
    generated.extend(
        [
            (output / "README.md", "local workflow", False, False),
            (
                output / "REVIEWER_INSTRUCTIONS.md",
                "reviewer instructions",
                True,
                False,
            ),
            (
                output / "SUPERVISOR_APPROVAL_CHECKLIST.md",
                "approval gate",
                False,
                False,
            ),
            (output / "returns/README.md", "raw-return handling", False, False),
            (mapping, "private mapping and sealed split", False, True),
            (adjudication, "private adjudication template", False, True),
            (gold, "private gold-label template", False, True),
        ]
    )
    manifest = {
        "schemaVersion": "IndependentEvidencePackage-v1",
        "packageVersion": PACKAGE_VERSION,
        "generatedAt": GENERATED_AT,
        "source": {"path": rel(source), "sha256": source_sha},
        "counts": {
            "candidateRows": 24,
            "calibrationRows": 3,
            "developmentRows": 16,
            "sealedHoldoutRows": 8,
            "reviewerCount": 2,
            "suppliedLabels": 0,
        },
        "randomization": {
            "partitionSeed": PARTITION_SEED,
            "reviewerOrderSeeds": list(REVIEWER_SEEDS),
        },
        "labelVocabulary": LABELS,
        "reviewWorkflow": [
            "supervisor_approval",
            "independent_calibration",
            "freeze_instructions",
            "independent_evaluation",
            "agreement_before_adjudication",
            "adjudication_and_gold_freeze",
            "development_only_analysis",
            "one_time_holdout_after_policy_freeze",
        ],
        "gate": {
            "status": "HUMAN_INPUT_REQUIRED",
            "minimumSafeLabels": 20,
            "accuracyMetricsComputable": False,
            "generalizationClaimAllowed": False,
            "humanInputRequired": True,
        },
        "files": [
            {
                "path": path.relative_to(output).as_posix(),
                "sha256": sha256_file(path),
                "role": role,
                "sendToReviewer": send,
                "containsPrivateMapping": private,
            }
            for path, role, send, private in sorted(generated, key=lambda item: item[0])
        ],
        "claimBoundary": (
            "Package readiness only. No expert label, accuracy, macro-F1, "
            "generalization, effort reduction, paper superiority, topology "
            "selection, or routing-policy approval is created by this build."
        ),
    }
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    ).validate(manifest)
    (output / "package_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def check(source: Path, output: Path) -> dict[str, Any]:
    if not output.is_dir():
        raise ValueError(f"package is missing: {output}")
    temporary = output.with_name(output.name + ".check")
    try:
        expected = build(source, temporary)
        actual_path = output / "package_manifest.json"
        if not actual_path.is_file():
            raise ValueError("package_manifest.json is missing")
        actual = json.loads(actual_path.read_text(encoding="utf-8"))
        if expected != actual:
            raise ValueError("package manifest is stale")
        for item in actual["files"]:
            path = output / item["path"]
            if not path.is_file() or sha256_file(path) != item["sha256"]:
                raise ValueError(f"package file hash mismatch: {item['path']}")
        forbidden = [
            "original_agent4_classification",
            "memory_informed_classification",
            "evaluation_leakage_status",
            "same_pattern_memory_used",
            "sealed_holdout",
        ]
        for item in actual["files"]:
            if not item["sendToReviewer"]:
                continue
            text = (output / item["path"]).read_text(encoding="utf-8")
            for token in forbidden:
                if token in text:
                    raise ValueError(
                        f"reviewer file exposes forbidden token {token}: {item['path']}"
                    )
        return actual
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--refresh", action="store_true")
    action.add_argument("--check", action="store_true")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        if args.refresh:
            manifest = build(args.source, args.output)
        else:
            manifest = check(args.source, args.output)
        print(
            "Independent evidence package: PASS "
            f"({manifest['counts']['candidateRows']} evaluation rows, "
            f"{manifest['counts']['calibrationRows']} calibration rows, "
            f"{manifest['counts']['suppliedLabels']} supplied labels)"
        )
    except (OSError, ValueError, json.JSONDecodeError, jsonschema.ValidationError) as exc:
        print(f"Independent evidence package: FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
