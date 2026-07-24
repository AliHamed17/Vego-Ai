#!/usr/bin/env node
/**
 * Build the July 21 supervisor deck from the inspected July 15 visual frame.
 *
 * Two modes are used:
 *   prepare-map: create the 1:1 audited template frame map from inspection layouts.
 *   build: import the prepared starter PPTX, apply focused inherited-shape edits,
 *          add presenter notes, and export the final editable PPTX.
 */

import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

function argsFrom(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const item = argv[index];
    if (!item.startsWith("--")) continue;
    const key = item.slice(2);
    const value = argv[index + 1];
    if (value && !value.startsWith("--")) {
      args[key] = value;
      index += 1;
    } else {
      args[key] = true;
    }
  }
  return args;
}

function required(args, key) {
  if (!args[key]) throw new Error(`Missing --${key}`);
  return path.resolve(String(args[key]));
}

async function sha256(filePath) {
  return crypto.createHash("sha256").update(await fs.readFile(filePath)).digest("hex");
}

const EDITS = [
  [1, "sh/7qp4be9c", "Decision Package", "July 21 Decision Package"],
  [1, "sh/65g3298r", "Confirm the July 1 record and decide the framework", "Confirm the record, review progress, and decide M-02–M-06"],
  [1, "sh/sryl4zqx", "15 July 2026", "21 July 2026"],
  [3, "sh/czmhc7id", "Real Human Expert", "Human Reviewer"],
  [4, "sh/sna103ap", "FRAMEWORK | ACTIVE", "FRAMEWORK | OFFLINE DESIGN"],
  [5, "sh/k7mxovud", "Listen, route, capture, verify, integrate, learn", "Observe, triage, ask, capture, verify, propose, remember"],
  [6, "sh/87ipkzal", "OFFLINE EVIDENCE | Early listening matters", "OFFLINE EVIDENCE | What later work shows—and cannot show"],
  [
    6,
    "sh/ml07i9sv",
    "Historical replay of existing outputs",
    "Accepted Iteration 14 replay\nRun hlayer-20260720T173308Z-d79047f5e2\nNEUTRAL / reliability-only",
  ],
  [6, "sh/v2tcn650", "481 observable events", "481 captured/reconstructed + 20 gaps"],
  [6, "sh/u1kbu1ov", "Only 11 - about 2.3% - reached the old queue", "501 contract records; not correctness evidence"],
  [6, "sh/i54bylor", "160 of 167 unstable guidelines", "160 unstable, never-reviewed guidelines"],
  [6, "sh/twfux0ne", "Never reached the historical review queue", "EXP-008 denominator across four settings"],
  [7, "sh/f2d0b6lc", "Recommended", "Proposal only"],
  [8, "sh/5sne5wne", "0.723", "0.726"],
  [
    8,
    "sh/w3ed8r6x",
    "Observe E1-E14 passively\nRoute E4, E6, E9, E11 first\nBundle related events per case",
    "Observe E1-E14 passively\nRoute churn, uncertainty, ambiguity, conflicts\nBundle related events per case",
  ],
  [8, "sh/8bat47ml", "Approve the pilot candidate?\nUniform or adaptive cap?", "Pilot candidate only?\nUniform or adaptive cap?"],
  [9, "sh/lsn2h4fa", "Expert corrects input or explains an override", "Reviewer revises input or explains an override"],
  [9, "sh/hcji5o7a", "Propose B=2, then human adjudication", "Escalate unresolved conflict to human adjudication"],
  [10, "sh/atwbelcn", "Only after allowed-touch\nlist approval", "Only after allowed-touch list\n+ implementation authorization"],
  [13, "sh/gb6x0zm9", "Confirmed", "Proposal — not approved"],
  [13, "sh/t8fy5k3i", "Confirmed", "Offline design"],
  [13, "sh/lkvy103m", "Open choice", "Proposal — not approved"],
  [13, "sh/xozyhkbi", "Parked", "Documented — parked"],
  [13, "sh/bmhgfatc", "D5 Real human expert", "D5 Real human judgment"],
  [13, "sh/p0zyd0b6", "Confirmed", "Blocked"],
  [13, "sh/8vahgzu5", "Open choice", "Proposal — not approved"],
  [14, "sh/x4ni9ofy", "Confirmed", "Offline design"],
  [14, "sh/kre1k3y9", "Open mechanism", "Proposal — not approved"],
  [14, "sh/y5wjitgj", "D9 Verify expert input", "D9 Verify human feedback"],
  [14, "sh/0buh8zy5", "Confirmed", "Offline evidence"],
  [14, "sh/grmxwvqt", "Open bound", "Proposal — not approved"],
  [14, "sh/up4fal83", "D11 July 15 outputs", "D11 Requested deliverables"],
  [14, "sh/4vmh0vq5", "Confirmed", "Delivered — provisional"],
  [14, "sh/d0fydk7m", "Proposal elements", "Delivered — provisional"],
  [16, "sh/ip4zel83", "Artifact produced", "Guideline or requirement authored"],
  [16, "sh/fm1gzq5o", "ARTIFACT", "REQUIREMENT"],
  [16, "sh/nqlg3a5k", "Q&A question", "Question asked"],
  [16, "sh/mpgj6t8j", "Q&A answer", "Answer persisted"],
  [16, "sh/kne14jqd", "Guideline revision", "Case context established"],
  [16, "sh/ih0jedob", "ARTIFACT", "CONTEXT"],
  [16, "sh/rat4b298", "Template revision", "Artifact version produced"],
  [16, "sh/p4vmlwrm", "Uncertainty signal", "Deviation assessed"],
  [16, "sh/wnadcrqh", "SIGNAL", "ASSESS"],
  [16, "sh/kbudgrqt", "Classification output", "Uncertainty recorded"],
  [16, "sh/i9sve18n", "OUTPUT", "SIGNAL"],
  [16, "sh/3apg3atc", "Review flag", "Variability pattern produced"],
  [16, "sh/pc7y5kbi", "ROUTING", "PATTERN"],
  [16, "sh/h8ne10b6", "Recurring ambiguity", "Human review item created"],
  [16, "sh/z29gbutk", "PATTERN", "REVIEW"],
  [16, "sh/wz21c3ud", "Human feedback", "Human feedback received"],
  [17, "sh/jilcvq54", "Source conflict", "Verification dialogue recorded"],
  [17, "sh/gnepkr69", "Memory store", "Adjudication outcome recorded"],
  [17, "sh/ulw7ihoj", "MEMORY", "ADJUDICATE"],
  [17, "sh/90nq9gfi", "Memory retrieve", "Correction proposal created"],
  [17, "sh/ny5876xc", "MEMORY", "PROPOSAL"],
  [17, "sh/zul836xg", "Integration result", "Trusted memory committed"],
  [17, "sh/d83q1wfa", "FEEDBACK", "MEMORY"],
  [18, "sh/fapkr6pw", "S1 Listen", "S1 Observe"],
  [18, "sh/upg3i18r", "Watch both communication circles", "Watch artifact and Q&A events"],
  [18, "sh/t0zqp8bm", "S6 Integrate - approval-gated corrections", "S6 Correction proposals - approval-gated"],
  [18, "sh/7yh8nytw", "S7 Learn - scope-aware reuse", "S7 Memory - scope-aware reuse"],
  [19, "sh/cri1gnql", "Listen across both circles and enter early", "Observe both circles and enter early"],
  [19, "sh/zu90b29c", "Real person and configurable dosage", "Human reviewer and configurable dosage"],
  [19, "sh/oj21o7qt", "Human interface + S2", "Human review + S2-S4"],
  [20, "sh/1cnitsvy", "Never human evidence", "Not human evidence"],
  [20, "sh/mdwz2xcj", "EXP-005 remains closed", "EXP-005: 0 supplied labels"],
  [
    21,
    "sh/wnu1k7e1",
    "Current state: 0 of 24 generalization-safe labels. Evaluation remains parked; no accuracy claim is permitted.",
    "Current state: 24 generalization-safe candidates and 0 supplied labels. Evaluation remains parked; no accuracy claim is permitted.",
  ],
  [22, "sh/1cj61w7q", "Errors, traceability, workload", "Disagreement, traceability, workload"],
  [23, "sh/1graxo3i", "Explore transfer of the H-layer concept to medical guidelines", "Ask whether H-layer concepts could transfer to medical-guideline work"],
  [23, "sh/edgr294r", "MediVARIA planning draft", "MediVARIA proposal-only draft"],
  [23, "sh/oji9832t", "PROPOSED", "PROPOSAL ONLY"],
];

const CORE_NOTES = [
  "Target 1:15. Open with the meeting objective: confirm the July 1 record, review July 3–20 progress, and record M-02–M-06. State that silence is Deferred, not approval.",
  "Target 1:30. Ask Iris and Arnon to accept, correct, qualify, or defer the D1–D12 paraphrases and attributed actions. Raw ASR remains unchanged.",
  "Target 1:30. Explain the framework-first redirect: observe early, capture human judgment, verify it, and reuse only under human authority. Architecture remains proposal-only.",
  "Target 1:30. Separate the framework track from evaluation. EXP-005 has 24 candidates and 0 supplied labels; EXP-012 is not computable.",
  "Target 1:30. Show H1/H2/H3 and S1–S7 as provisional requirements. No final prompt text or live listener is authorized.",
  "Target 2:00. Report Iteration 14 and offline mechanism evidence. Say NEUTRAL/reliability-only. Do not imply accuracy, generalization, correctness, or reduced effort at scale.",
  "Target 1:45. M-02: recommend Observer + Integrator while preserving visible H1/H2/H3 groupings. Record the actual outcome and rationale.",
  "Target 2:00. M-03: threshold_sev2 is a replay pilot candidate, retaining about 80% load. No uniform or adaptive cap is approved.",
  "Target 1:45. M-04: recommend deterministic source checks first. Source families and two-round bound remain proposals. Persistent conflict goes to adjudication.",
  "Target 1:45. M-05: every phase-one correction requires human approval. Timeout preserves baseline and parks. Live hooks need both allowed-touch and implementation authorization.",
  "Target 1:15. M-06: keep education as the MSc empirical scope. MediVARIA is proposal-only future work with no clinical claim or implementation.",
  "Target 2:15. Read back M-01–M-06: outcome, selected value, rationale, approver, owner, due date, constraints, and affected artifacts. End here; do not use a generic thank-you slide.",
];

function appendixNote(slideNumber) {
  const labels = {
    13: "D1–D6 record matrix. Every row remains a machine-derived paraphrase pending M-01.",
    14: "D7–D12 record matrix. Later deliverables and future proposals are not supervisor-approved.",
    15: "Selected Hebrew ASR only. All excerpts remain unreviewed; English wording is paraphrase.",
    16: "E1–E10 provisional event catalog. Offline design only; no live listener authorization.",
    17: "E11–E15 and governed channels. E15 is evaluation-only and cannot produce a framework action.",
    18: "S1–S7 grouping. Skill names and decomposition remain provisional pending M-02.",
    19: "Prompt-requirements traceability. Requirements only; no final prompt text or runtime change.",
    20: "Offline method and evidence classes. Synthetic fixtures are not human evidence.",
    21: "EXP-005 stop/go gate. Twenty-four candidates, zero supplied labels, no accuracy computation.",
    22: "Future comparison design is parked until architecture approval, at least 20 safe labels, and supervisor go-ahead.",
    23: "MediVARIA is proposal-only future work; no transferability or clinical-performance claim.",
  };
  return `Appendix—use only if asked. ${labels[slideNumber]}`;
}

async function prepareMap(args) {
  const layouts = required(args, "layouts");
  const mapPath = required(args, "map");
  const auditPath = required(args, "audit");
  const deviationPath = required(args, "deviations");
  const completeInspectPath = required(args, "complete-inspect");
  const outputSlides = [];
  const completeInspectRows = [];
  for (let slide = 1; slide <= 23; slide += 1) {
    const layoutPath = path.join(layouts, `source-slide-${String(slide).padStart(2, "0")}.layout.json`);
    const layout = JSON.parse(await fs.readFile(layoutPath, "utf8"));
    completeInspectRows.push({ kind: "slide", id: layout.slide.aid, slide });
    for (const element of layout.elements) {
      const row = {
        kind: typeof element.text === "string" ? "textbox" : "shape",
        id: element.aid,
        slide,
      };
      if (typeof element.text === "string") {
        row.textChars = element.text.length;
        row.textLines = element.text.split(/\r?\n/).length;
      }
      completeInspectRows.push(row);
    }
    const textIds = layout.elements.filter((element) => typeof element.text === "string").map((element) => element.aid);
    outputSlides.push({
      outputSlide: slide,
      sourceSlide: slide,
      narrativeRole: slide <= 12 ? `core decision narrative ${slide}` : `evidence appendix ${slide - 12}`,
      reuseMode: "duplicate-slide",
      editTargets: textIds.map((sourceElementId) => ({ action: "rewrite", sourceElementId })),
    });
  }
  await fs.writeFile(
    completeInspectPath,
    `${completeInspectRows.map((row) => JSON.stringify(row)).join("\n")}\n`,
    "utf8",
  );
  await fs.writeFile(mapPath, `${JSON.stringify({ outputSlides, omittedSourceSlides: [] }, null, 2)}\n`, "utf8");
  await fs.writeFile(
    auditPath,
    [
      "VEGO-AI July 21 template audit",
      "Source: 23-slide July 15 supervisor decision package.",
      "Inventory: 12 core narrative slides + 11 appendix slides.",
      "Reuse contract: one-to-one duplicate-slide mapping; every inherited text object is explicitly classified as rewrite-capable.",
      "Inspection note: the complete inspect index is rebuilt from the artifact-tool layout manifests so all 23 slides are validated even when the console-oriented inspect stream is truncated.",
      "Brand: #0A0A12 dark canvas, purple/cyan/green decision accents, Calibri typography, provenance footer on every slide.",
      "Insertion contract: no new primitives, no added slides, no master/layout change, no background overlays.",
      "All source slide previews and layout JSON files were inspected before mapping.",
      "",
    ].join("\n"),
    "utf8",
  );
  await fs.writeFile(
    deviationPath,
    [
      "VEGO-AI July 21 deviation log",
      "Slides 1, 3–10, 13–14, and 16–23: focused wording/status/evidence updates only.",
      "All slides: speaker notes refreshed for July 21 timing and evidence boundaries.",
      "No geometry, imagery, master, layout, or theme departure is intended.",
      "No additional slide or decorative primitive is introduced.",
      "",
    ].join("\n"),
    "utf8",
  );
  console.log(mapPath);
}

async function importArtifactUtils() {
  const skillDir = process.env.PRESENTATIONS_SKILL_DIR;
  if (!skillDir) throw new Error("PRESENTATIONS_SKILL_DIR is required");
  const modulePath = path.join(skillDir, "container_tools", "artifact_tool_utils.mjs");
  return import(pathToFileURL(modulePath).href);
}

function slideItems(presentation) {
  if (Array.isArray(presentation.slides?.items)) return presentation.slides.items;
  if (Number.isInteger(presentation.slides?.count)) {
    return Array.from({ length: presentation.slides.count }, (_, index) => presentation.slides.getItem(index));
  }
  throw new Error("Unable to enumerate slides");
}

async function buildDeck(args) {
  const workspace = required(args, "workspace");
  const starterPptxPath = required(args, "starter");
  const output = required(args, "out");
  const reportPath = required(args, "report");
  const { ensureArtifactToolWorkspace, importArtifactTool } = await importArtifactUtils();
  await ensureArtifactToolWorkspace(workspace);
  const { FileBlob, PresentationFile } = await importArtifactTool(workspace);
  const presentation = await PresentationFile.importPptx(await FileBlob.load(starterPptxPath));
  const slides = slideItems(presentation);
  if (slides.length !== 23) throw new Error(`Expected 23 slides, found ${slides.length}`);

  const applied = [];
  for (const [slide, sourceElementId, oldText, newText] of EDITS) {
    const target = presentation.resolve(sourceElementId);
    if (!target?.text || typeof target.text.replace !== "function") {
      throw new Error(`Could not resolve editable text target ${sourceElementId} on slide ${slide}`);
    }
    target.text.replace(oldText, newText);
    applied.push({ slide, sourceElementId, oldText, newText });
  }

  for (let index = 0; index < slides.length; index += 1) {
    const slideNumber = index + 1;
    const notes = slideNumber <= 12 ? CORE_NOTES[index] : appendixNote(slideNumber);
    slides[index].speakerNotes.textFrame.setText(notes);
    slides[index].speakerNotes.setVisible(true);
  }

  await fs.mkdir(path.dirname(output), { recursive: true });
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(output);

  const inspection = await presentation.inspect({
    kind: "slide,textbox,shape,notes",
    maxChars: 200000,
  });
  const inspectPath = path.join(workspace, "final-deck-inspect.ndjson");
  await fs.writeFile(inspectPath, `${inspection.ndjson.trim()}\n`, "utf8");
  const report = {
    schemaVersion: "SupervisorDeckBuildReport-v1",
    generatedFor: "2026-07-21",
    sourceStarterSha256: await sha256(starterPptxPath),
    outputSha256: await sha256(output),
    slideCount: slides.length,
    coreSlides: 12,
    appendixSlides: 11,
    appliedEdits: applied.length,
    speakerNotesUpdated: slides.length,
    boundaries: [
      "Agent 4 and the baseline remain unchanged.",
      "EXP-005 has 24 candidates and 0 supplied labels.",
      "EXP-012 remains NOT YET COMPUTABLE.",
      "M-01 through M-06 are unrecorded.",
      "No accuracy, generalization, benchmark-superiority, reduced-effort-at-scale, or clinical-performance claim.",
    ],
  };
  await fs.writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  console.log(output);
}

async function main() {
  const args = argsFrom(process.argv.slice(2));
  const mode = args.mode;
  if (mode === "prepare-map") return prepareMap(args);
  if (mode === "build") return buildDeck(args);
  throw new Error("--mode must be prepare-map or build");
}

main().catch((error) => {
  console.error(error?.stack || String(error));
  process.exitCode = 1;
});
