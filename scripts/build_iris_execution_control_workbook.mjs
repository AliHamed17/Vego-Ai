#!/usr/bin/env node
/**
 * Build the evidence-honest Iris execution-control workbook from tracked
 * canonical controls. The workbook is a derived operator view: it never
 * creates human review, supervisor acceptance, expert labels, medical
 * authorization, delivery, approval, or submission evidence.
 */

import crypto from "node:crypto";
import { execFile } from "node:child_process";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { promisify } from "node:util";
import { fileURLToPath, pathToFileURL } from "node:url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const execFileAsync = promisify(execFile);
const DEFAULT_ROOT = path.resolve(SCRIPT_DIR, "..");
const DEFAULT_ARTIFACT_ROOT = path.join(
  os.homedir(),
  ".cache",
  "codex-runtimes",
  "codex-primary-runtime",
  "dependencies",
  "node",
  "node_modules",
  "@oai",
  "artifact-tool",
);

function parseArgs(argv) {
  const result = {};
  for (let index = 0; index < argv.length; index += 1) {
    const item = argv[index];
    if (!item.startsWith("--")) continue;
    const key = item.slice(2);
    const next = argv[index + 1];
    if (next && !next.startsWith("--")) {
      result[key] = next;
      index += 1;
    } else {
      result[key] = true;
    }
  }
  return result;
}

function columnName(index) {
  let value = index;
  let result = "";
  while (value > 0) {
    const remainder = (value - 1) % 26;
    result = String.fromCharCode(65 + remainder) + result;
    value = Math.floor((value - 1) / 26);
  }
  return result;
}

function tableCells(line) {
  const trimmed = line.trim();
  if (!trimmed.startsWith("|") || !trimmed.endsWith("|")) return [];
  return trimmed
    .slice(1, -1)
    .split("|")
    .map((cell) => cell.trim());
}

function plainText(value) {
  return String(value ?? "")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/<br\s*\/?\s*>/gi, "\n")
    .replace(/[`*_]/g, "")
    .replace(/&ndash;/g, "–")
    .replace(/&mdash;/g, "—")
    .trim();
}

function parseLocalDate(value) {
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(String(value));
  if (!match) throw new Error(`Unsupported zoned date: ${value}`);
  // artifact-tool serializes Date values from UTC components. Construct the
  // intended Asia/Jerusalem wall-clock value as UTC and keep the timezone in a
  // separate visible column so Excel displays the exact meeting time.
  return new Date(Date.UTC(
    Number(match[1]),
    Number(match[2]) - 1,
    Number(match[3]),
    Number(match[4]),
    Number(match[5]),
  ));
}

function dateOnly(value) {
  const [year, month, day] = String(value).split("-").map(Number);
  return new Date(Date.UTC(year, month - 1, day, 12, 0, 0));
}

async function applyNativeFreezePanes(outputPath) {
  // artifact-tool 2.8.x exposes freezePanes but does not persist it in XLSX
  // export. It also exports list-validation rules with the correct Excel
  // default STOP alert style but without enabling the visible error alert.
  // Apply those two missing Excel persistence details after the artifact-tool
  // build; all data, formulas, styles, tables, list values, conditional
  // formatting, and charts still originate above.
  const paneMap = {
    Executive: [5, 0],
    Work_Packages: [3, 2],
    Control_Acceptance: [3, 2],
    Experiment_Crosswalk: [3, 2],
    Role_Assignments: [3, 2],
    Schedule: [3, 3],
    Decision_Log: [3, 2],
    Human_Review: [3, 2],
    Literature_Search: [3, 2],
    Medical_Gates: [3, 2],
    Acceptance_Tests: [3, 2],
    Controlled_Lists: [3, 1],
  };
  const paneLiteral = Object.entries(paneMap)
    .map(([name, [rows, columns]]) => `@('${name}',${rows},${columns})`)
    .join(",");
  const validationRanges = [
    ["Work_Packages", "H4:H32"],
    ["Control_Acceptance", "N4:N200"],
    ["Schedule", "F4:F32"],
    ["Decision_Log", "D4:D100"],
    ["Human_Review", "H4:H100"],
    ["Literature_Search", "F4:F100"],
    ["Medical_Gates", "G4:G100"],
    ["Acceptance_Tests", "D4:D100"],
  ];
  const validationLiteral = validationRanges
    .map(([name, range]) => `@('${name}','${range}')`)
    .join(",");
  const escapedPath = outputPath.replaceAll("'", "''");
  const script = `$ErrorActionPreference='Stop'; $excel=$null; $book=$null; try { `
    + `$excel=New-Object -ComObject Excel.Application; $excel.Visible=$false; $excel.DisplayAlerts=$false; `
    + `$book=$excel.Workbooks.Open('${escapedPath}',0,$false); `
    + `$panes=@(${paneLiteral}); foreach($entry in $panes){ `
    + `$sheet=$book.Worksheets.Item([string]$entry[0]); $sheet.Activate(); `
    + `$window=$excel.ActiveWindow; $window.FreezePanes=$false; $window.SplitRow=[int]$entry[1]; `
    + `$window.SplitColumn=[int]$entry[2]; $window.FreezePanes=$true; `
    + `[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($window); `
    + `[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($sheet) }; `
    + `$validationRanges=@(${validationLiteral}); foreach($entry in $validationRanges){ `
    + `$sheet=$book.Worksheets.Item([string]$entry[0]); $range=$sheet.Range([string]$entry[1]); `
    + `if([int]$range.Validation.AlertStyle -ne 1){throw "Validation alert is not STOP: $($entry[0])!$($entry[1])"}; `
    + `$range.Validation.ShowError=$true; `
    + `[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($range); `
    + `[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($sheet) }; `
    + `$book.Worksheets.Item('Executive').Activate(); $book.Save(); `
    + `} finally { if($book){$book.Close($false);[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($book)}; `
    + `if($excel){$excel.Quit();[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($excel)}; `
    + `[GC]::Collect();[GC]::WaitForPendingFinalizers() }`;
  const encoded = Buffer.from(script, "utf16le").toString("base64");
  await execFileAsync("powershell.exe", ["-NoProfile", "-NonInteractive", "-EncodedCommand", encoded], {
    windowsHide: true,
    maxBuffer: 1024 * 1024,
  });
}

function reverseCoverage(mapping) {
  const reverse = new Map();
  for (const [itemId, wpIds] of Object.entries(mapping)) {
    for (const wpId of wpIds) {
      if (!reverse.has(wpId)) reverse.set(wpId, []);
      reverse.get(wpId).push(itemId);
    }
  }
  return reverse;
}

function summarizeItems(items, mapper) {
  if (!items?.length) return "None";
  return items.map(mapper).join(" | ");
}

function parseMasterRegister(markdown) {
  const main = new Map();
  const dimensions = new Map();
  for (const line of markdown.split(/\r?\n/)) {
    const cells = tableCells(line);
    if (!/^[RAQ]-\d{2}$/.test(cells[0] ?? "")) continue;
    if (cells.length === 11 && !main.has(cells[0])) {
      main.set(cells[0], {
        id: cells[0],
        type: plainText(cells[1]),
        item: plainText(cells[2]),
        source: plainText(cells[3]),
        owner: plainText(cells[4]),
        due: plainText(cells[5]),
        dependencies: plainText(cells[6]),
        evidence: plainText(cells[7]),
        acceptanceCheck: plainText(cells[8]),
        proseStatus: plainText(cells[9]),
        gateNote: plainText(cells[10]),
      });
    } else if (cells.length === 5) {
      dimensions.set(cells[0], {
        extraction: plainText(cells[1]),
        implementation: plainText(cells[2]),
        acceptance: plainText(cells[3]),
        ongoing: plainText(cells[4]),
      });
    }
  }
  return { main, dimensions };
}

function parseExperimentTable(markdown, prefix) {
  const rows = [];
  for (const line of markdown.split(/\r?\n/)) {
    const cells = tableCells(line);
    const idMatch = new RegExp(`${prefix}-\\d{2}`).exec(plainText(cells[0] ?? ""));
    if (!idMatch) continue;
    rows.push({ id: idMatch[0], cells: cells.map(plainText) });
  }
  return rows;
}

function parseLiteratureExecution(markdown) {
  const queryDetails = new Map();
  const sectionPattern = /^### (QL-\d{2}) - (.+)$/gm;
  const sections = [...markdown.matchAll(sectionPattern)];
  for (let index = 0; index < sections.length; index += 1) {
    const current = sections[index];
    const start = current.index + current[0].length;
    const end = sections[index + 1]?.index ?? markdown.length;
    const body = markdown.slice(start, end);
    const query = /```text\s*([\s\S]*?)```/.exec(body)?.[1]?.trim() ?? "Pending execution";
    const mapping = /Primary mapping:\s*([^\n]+)/.exec(body)?.[1]?.trim() ?? "Not recorded";
    queryDetails.set(current[1], { concept: current[2], query, mapping });
  }

  const rows = [];
  for (const line of markdown.split(/\r?\n/)) {
    const cells = tableCells(line);
    if (!/^QL-\d{2}$/.test(cells[0] ?? "") || cells.length !== 9) continue;
    if (!cells[1] || cells[1] === "Database") continue;
    const details = queryDetails.get(cells[0]) ?? {};
    rows.push([
      cells[0],
      details.concept ?? "Unknown",
      details.query ?? "Pending execution",
      plainText(cells[1]),
      plainText(cells[2]),
      plainText(cells[3]),
      null,
      null,
      null,
      details.mapping ?? "Not recorded",
      "No count or coverage claim until executed",
    ]);
  }
  return rows;
}

function exactRule(range, value, fill, fontColor = "#000000") {
  range.conditionalFormats.add("cellIs", {
    operator: "equal",
    formula: `"${value.replaceAll('"', '""')}"`,
    format: { fill, font: { color: fontColor, bold: true } },
  });
}

function addListValidation(range, values, label) {
  range.dataValidation = {
    allowBlank: false,
    rule: { type: "list", values },
    errorAlert: {
      style: "stop",
      title: `Invalid ${label}`,
      message: `Choose a value from the ${label} drop-down list.`,
    },
  };
}

function applyStatusFormatting(range) {
  exactRule(range, "planned", "#E7E6E6", "#595959");
  exactRule(range, "in_progress", "#D9EAF7", "#1F4E78");
  exactRule(range, "partial", "#FFF2CC", "#9C6500");
  exactRule(range, "evidence_ready", "#E2F0D9", "#2E7D32");
  exactRule(range, "acceptance_check_passed", "#E2F0D9", "#2E7D32");
  exactRule(range, "blocked", "#FCE4D6", "#C00000");
  for (const state of [
    "accepted",
    "accepted_ongoing",
    "accepted_after_correction",
    "superseded_approved",
    "not_applicable_approved",
  ]) exactRule(range, state, "#E2F0D9", "#2E7D32");
}

function applyGateFormatting(range) {
  exactRule(range, "PASS", "#E2F0D9", "#2E7D32");
  exactRule(range, "FAIL", "#FCE4D6", "#C00000");
  exactRule(range, "PENDING", "#FFF2CC", "#9C6500");
  exactRule(range, "NOT RUN", "#FFF2CC", "#9C6500");
  exactRule(range, "NOT APPLICABLE", "#E7E6E6", "#595959");
}

function applyOverdueFormatting(range) {
  exactRule(range, "OVERDUE", "#FCE4D6", "#C00000");
  exactRule(range, "ON TRACK", "#E2F0D9", "#2E7D32");
  exactRule(range, "CLOSED", "#D9EAD3", "#2E7D32");
}

function prepareDataSheet(sheet, title, note, headers, rows, options = {}) {
  const lastColumn = columnName(headers.length);
  const lastRow = rows.length + 3;
  sheet.getRange(`A1:${lastColumn}1`).merge();
  sheet.getRange("A1").values = [[title]];
  sheet.getRange(`A2:${lastColumn}2`).merge();
  sheet.getRange("A2").values = [[note]];
  sheet.getRange(`A3:${lastColumn}3`).values = [headers];
  if (rows.length) sheet.getRange(`A4:${lastColumn}${lastRow}`).values = rows;

  sheet.getRange(`A1:${lastColumn}1`).format = {
    fill: "#1F4E78",
    font: { color: "#FFFFFF", bold: true, size: 16 },
    verticalAlignment: "center",
  };
  sheet.getRange(`A2:${lastColumn}2`).format = {
    fill: "#FFF2CC",
    font: { color: "#7F6000", italic: true, size: 10 },
    wrapText: true,
    verticalAlignment: "center",
  };
  sheet.getRange(`A3:${lastColumn}3`).format = {
    fill: "#2F75B5",
    font: { color: "#FFFFFF", bold: true, size: 10 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
  };
  if (rows.length) {
    sheet.getRange(`A4:${lastColumn}${lastRow}`).format = {
      font: { size: 9, color: "#333333" },
      verticalAlignment: "top",
      wrapText: true,
    };
  }
  sheet.getRange("A1").format.rowHeight = 30;
  sheet.getRange("A2").format.rowHeight = 34;
  sheet.getRange(`A3:${lastColumn}3`).format.rowHeight = 32;

  const widths = options.widths ?? headers.map(() => 18);
  widths.forEach((width, index) => {
    sheet.getRange(`${columnName(index + 1)}1:${columnName(index + 1)}${lastRow}`).format.columnWidth = width;
  });

  if (rows.length) {
    const table = sheet.tables.add(`A3:${lastColumn}${lastRow}`, true, options.tableName);
    table.style = options.tableStyle ?? "TableStyleMedium2";
  }
  sheet.freezePanes.freezeRows(3);
  if (options.freezeColumns) sheet.freezePanes.freezeColumns(options.freezeColumns);
  sheet.showGridLines = false;
  return { lastColumn, lastRow };
}

function humanReviewRows() {
  return [
    ["CAL-01", "30 balanced sample rows", 30, "Codebook/format calibration only; no shared substantive answers", "Ali", null, null, "Not started", dateOnly("2026-08-02"), null, "Two blind sample returns + frozen codebook"],
    ["PRI-01", "S-0053-S-0126", 74, "Candidacy outcomes and follow-up examination", "Ali", null, null, "Not started", dateOnly("2026-08-04"), null, "Both reviewer rows"],
    ["PRI-02", "S-0150-S-0185", 36, "Milestones and reported availability", "Ali", null, null, "Not started", dateOnly("2026-08-04"), null, "Both reviewer rows"],
    ["PRI-03", "S-0891-S-0972", 82, "Medical assertions and MIMIC organization", "Ali", null, null, "Not started", dateOnly("2026-08-04"), null, "Both reviewer rows"],
    ["PRI-04", "S-1058-S-1152", 95, "Partner meeting, access terminology, and retrieval", "Ali", null, null, "Not started", dateOnly("2026-08-04"), null, "Both reviewer rows"],
    ["REM-01", "S-0001-S-0052", 52, "Remaining chronological review", "Ali", null, null, "Not started", dateOnly("2026-08-09"), null, "Both reviewer rows"],
    ["REM-02", "S-0127-S-0149", 23, "Remaining chronological review", "Ali", null, null, "Not started", dateOnly("2026-08-09"), null, "Both reviewer rows"],
    ["REM-03", "S-0186-S-0285", 100, "Remaining chronological review", "Ali", null, null, "Not started", dateOnly("2026-08-09"), null, "Both reviewer rows"],
    ["REM-04", "S-0286-S-0385", 100, "Remaining chronological review", "Ali", null, null, "Not started", dateOnly("2026-08-09"), null, "Both reviewer rows"],
    ["REM-05", "S-0386-S-0485", 100, "Remaining chronological review", "Ali", null, null, "Not started", dateOnly("2026-08-09"), null, "Both reviewer rows"],
    ["REM-06", "S-0486-S-0585", 100, "Remaining chronological review", "Ali", null, null, "Not started", dateOnly("2026-08-09"), null, "Both reviewer rows"],
    ["REM-07", "S-0586-S-0685", 100, "Remaining chronological review", "Ali", null, null, "Not started", dateOnly("2026-08-09"), null, "Both reviewer rows"],
    ["REM-08", "S-0686-S-0785", 100, "Remaining chronological review", "Ali", null, null, "Not started", dateOnly("2026-08-09"), null, "Both reviewer rows"],
    ["REM-09", "S-0786-S-0885", 100, "Remaining chronological review", "Ali", null, null, "Not started", dateOnly("2026-08-09"), null, "Both reviewer rows"],
    ["REM-10", "S-0886-S-0890", 5, "Remaining chronological review", "Ali", null, null, "Not started", dateOnly("2026-08-09"), null, "Both reviewer rows"],
    ["REM-11", "S-0973-S-1057", 85, "Remaining chronological review", "Ali", null, null, "Not started", dateOnly("2026-08-09"), null, "Both reviewer rows"],
    ["REM-12", "S-1153-S-1195", 43, "Remaining chronological review", "Ali", null, null, "Not started", dateOnly("2026-08-09"), null, "Both reviewer rows"],
    ["MEDIA-A", "Full 46:26.283 media", 1, "Reviewer A full-media evidence including ASR edges", "Ali", null, null, "Not started", dateOnly("2026-08-09"), null, "MEDIA-TIMELINE row"],
    ["MEDIA-B", "Full 46:26.283 media", 1, "Reviewer B full-media evidence including ASR edges", null, null, null, "Not started", dateOnly("2026-08-09"), null, "MEDIA-TIMELINE row"],
    ["ADJ-01", "All mechanical disagreements", null, "Third-person adjudication", null, null, null, "Not started", dateOnly("2026-08-11"), null, "One adjudication per disagreement"],
    ["MERGE-01", "S-0001-S-1195", 1195, "Deterministic final merge and provenance", null, null, null, "Not started", dateOnly("2026-08-12"), null, "CSV/JSON; readiness checks; hashes"],
  ];
}

const DECISIONS = [
  ["D-RQ-01", "Umbrella RQ wording", "Mandatory"],
  ["D-RQ-02", "SQ1-SQ3 wording", "Mandatory"],
  ["D-RQ-03", "Three-study mapping and methods", "Mandatory"],
  ["D-RQ-04", "Plan A conditional medical / Plan B non-medical", "Mandatory"],
  ["D-RQ-05", "Every RQ answerable under Plan B", "Mandatory"],
  ["D-RQ-06", "August 26 medical fallback trigger", "Mandatory"],
  ["D-RQ-07", "Evidence boundary and five claim states", "Mandatory"],
  ["D-RQ-08", "Literature scope and taxonomy", "Time permitting"],
  ["D-RQ-09", "MIMIC metadata-only boundary", "Time permitting"],
  ["D-RQ-10", "Medical and university-process owners", "Assignment"],
];

const MEDICAL_GATES = [
  ["G1 Use case", "Workflow, owner, unit, I/O, baseline, non-goals, and measures", "CLINICAL_OWNER; IRIS; ALI", null, null, null, "FAIL", "Plan B if control absent Aug26", "No approved clinical use case"],
  ["G2 People", "Clinician, custodian, ethics, VDI, methods, and escalation roles", "CLINICAL_OWNER; DATA_CUSTODIAN; PRIVACY_ETHICS_OWNER; VDI_ADMIN; METHODS_REVIEWER", null, null, null, "FAIL", "Plan B if control absent Aug26", "Required roles unfilled"],
  ["G3 Authorization", "Named-user, project-specific permission and expiry", "DATA_CUSTODIAN", null, null, null, "FAIL", "Plan B if control absent Aug26", "Shared access is not authorization"],
  ["G4 Ethics/privacy", "Written dataset/protocol determination and incident rules", "PRIVACY_ETHICS_OWNER; DATA_CUSTODIAN", null, null, null, "FAIL", "Plan B if control absent Aug26", "No project-specific determination"],
  ["G5 Environment", "Approved VDI, storage, logging, egress, and local-model decision", "VDI_ADMIN; DATA_CUSTODIAN", null, null, null, "FAIL", "Plan B if control absent Aug26", "No approved environment/model"],
  ["G6 Protocol", "Cohort, mappings, outcomes, missingness, leakage, statistics, and stop rules", "IRIS; ARNON; CLINICAL_OWNER; METHODS_REVIEWER", null, null, null, "FAIL", "Plan B if control absent Aug26", "No approved medical protocol"],
];

const ACCEPTANCE_TESTS = [
  ["AT-01", "44-control structural coverage", "PASS", "PASS", "structure", "44/44 exact IDs", "Local control structure valid"],
  ["AT-02", "Canonical work-package coverage", "29/29", "29/29", "structure", "WP-001 through WP-029", "Canonical board visible"],
  ["AT-03", "Assurance/canonical/scientific experiment coverage", "10/10; 10/10; 6/6", "10/10; 10/10; 6/6", "structure", "Experiment_Crosswalk", "Experiment denominator visible"],
  ["AT-04", "D-RQ decision coverage", "10/10", "10/10", "structure", "D-RQ-01 through D-RQ-10", "Decision worksheet complete"],
  ["AT-05", "Deck/PDF/notes/render QA", "PASS", "PASS", "structure", "21 slides; 21 source blocks", "Local package built"],
  ["AT-06", "Ali exact-package approval", "PASS", "PENDING", "delivery", "No signed release row", "Blocks sharing"],
  ["AT-07", "Timed and adversarial human rehearsal", "PASS", "NOT RUN", "delivery", "Rehearsal templates only", "Blocks sharing"],
  ["AT-08", "Iris and Arnon recipient access", "PASS", "NOT RUN", "delivery", "Not shared or tested", "Blocks delivered status"],
  ["AT-09", "Dual review + full-media + adjudication", "PASS", "FAIL", "readiness", "0/1,195 per reviewer; 0/1 media", "Blocks transcript closure"],
  ["AT-10", "Literature searches/screening", "PASS", "NOT RUN", "proposal", "Protocol ready", "Novelty remains preliminary"],
  ["AT-11", "EXP-005 human evidence", "20-24 eligible labels", "FAIL", "scientific", "0/24; 0/2 reviewers", "Blocks quantitative claim"],
  ["AT-12", "Medical readiness", "6/6 before rows", "FAIL", "medical", "0/6", "Blocks all row-level medical work"],
  ["AT-13", "Official candidacy process", "Authoritative response", "PENDING", "submission", "Checklist only", "Blocks candidacy deck/submission"],
  ["AT-14", "Authorized submission receipt", "PASS", "FAIL", "closure", "NOT_SUBMITTED template", "Blocks closure certificate"],
];

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const root = path.resolve(String(args.root ?? DEFAULT_ROOT));
  const artifactRoot = path.resolve(
    String(args["artifact-root"] ?? process.env.CODEX_ARTIFACT_TOOL_ROOT ?? DEFAULT_ARTIFACT_ROOT),
  );
  const artifactModule = path.join(artifactRoot, "dist", "artifact_tool.mjs");
  const { SpreadsheetFile, Workbook } = await import(pathToFileURL(artifactModule).href);

  const boardPath = path.join(root, "docs/research/phd-proposal/aug1-oct7-execution-control-board.json");
  const masterPath = path.join(root, "docs/research/phd-proposal/master-traceability-register.md");
  const irisExperimentPath = path.join(root, "docs/research/phd-proposal/iris-alignment-experiment-register.md");
  const scientificPath = path.join(root, "docs/research/phd-proposal/scientific-experiment-crosswalk.md");
  const literaturePath = path.join(root, "docs/research/phd-proposal/literature-search-execution-register.md");
  const outputDir = path.resolve(
    String(args.out ?? path.join(root, "outputs/iris-next-step-2026-08-01-implementation")),
  );
  const outputPath = path.join(outputDir, "VEGO-AI-Iris-Next-Step-Execution-Control-2026-08-01.xlsx");
  const previewDir = path.join(outputDir, "previews");

  const [boardText, masterText, irisExperimentText, scientificText, literatureText] = await Promise.all([
    fs.readFile(boardPath, "utf8"),
    fs.readFile(masterPath, "utf8"),
    fs.readFile(irisExperimentPath, "utf8"),
    fs.readFile(scientificPath, "utf8"),
    fs.readFile(literaturePath, "utf8"),
  ]);
  const board = JSON.parse(boardText);
  const controls = parseMasterRegister(masterText);
  const irisExperiments = parseExperimentTable(irisExperimentText, "IRIS-EXP");
  const scientificExperiments = parseExperimentTable(scientificText, "SCI-EXP");
  const literatureRows = parseLiteratureExecution(literatureText);

  const expectedControlIds = board.coverageRequirements.controlIds;
  const expectedIrisExperimentIds = board.coverageRequirements.assuranceExperimentIds;
  const expectedCanonicalExperimentIds = board.coverageRequirements.canonicalExperimentIds;
  const expectedScientificIds = Array.from({ length: 6 }, (_, index) => `SCI-EXP-${String(index + 1).padStart(2, "0")}`);
  for (const expected of expectedControlIds) {
    if (!controls.main.has(expected) || !controls.dimensions.has(expected)) {
      throw new Error(`Master register is missing required control or dimension row: ${expected}`);
    }
  }
  if (board.workPackages.length !== 29) throw new Error(`Expected 29 canonical work packages, found ${board.workPackages.length}`);
  if (board.roles.length !== 19) throw new Error(`Expected 19 canonical roles, found ${board.roles.length}`);
  if (irisExperiments.length !== 10) throw new Error(`Expected 10 IRIS experiments, found ${irisExperiments.length}`);
  if (scientificExperiments.length !== 6) throw new Error(`Expected 6 SCI experiment aliases, found ${scientificExperiments.length}`);

  const controlsByWp = reverseCoverage(board.coverageMap.controls);
  const assuranceByWp = reverseCoverage(board.coverageMap.assuranceExperiments);
  const canonicalExperimentsByWp = reverseCoverage(board.coverageMap.canonicalExperiments);
  const wpById = new Map(board.workPackages.map((wp) => [wp.id, wp]));

  const wb = Workbook.create();
  const sheetNames = [
    "Executive",
    "Work_Packages",
    "Control_Acceptance",
    "Experiment_Crosswalk",
    "Role_Assignments",
    "Schedule",
    "Decision_Log",
    "Human_Review",
    "Literature_Search",
    "Medical_Gates",
    "Acceptance_Tests",
    "Controlled_Lists",
  ];
  for (const name of sheetNames) wb.worksheets.add(name);

  const workStatusValues = [
    "planned",
    "in_progress",
    "partial",
    "evidence_ready",
    "acceptance_check_passed",
    "blocked",
    ...board.completionPolicy.finalStatuses,
  ];
  const decisionValues = ["Pending", "Confirm", "Confirm with correction", "Retire or supersede", "Defer"];
  const gateValues = ["PASS", "FAIL", "PENDING", "NOT RUN", "NOT APPLICABLE"];
  const reviewValues = ["Not started", "Calibration", "In progress", "Reviewer complete", "Adjudication required", "Adjudicated"];
  const finalStateValues = [
    "Pending",
    "Accepted",
    "Accepted with ongoing control",
    "Accepted after correction",
    "Superseded by approved decision",
    "Not applicable by approved Plan B or other decision",
  ];

  const controlledRows = Array.from({ length: Math.max(workStatusValues.length, decisionValues.length, gateValues.length, reviewValues.length, finalStateValues.length) }, (_, index) => [
    workStatusValues[index] ?? null,
    decisionValues[index] ?? null,
    gateValues[index] ?? null,
    reviewValues[index] ?? null,
    finalStateValues[index] ?? null,
  ]);
  const controlledSheet = wb.worksheets.getItem("Controlled_Lists");
  prepareDataSheet(
    controlledSheet,
    "Controlled Lists — Stop-Validated Values",
    "Drop-down error alerts use STOP behavior; canonical source values remain unchanged.",
    ["Work Package Status", "Decision Outcome", "Gate Result", "Review Status", "Control Final State"],
    controlledRows,
    { tableName: "ControlledListsTable", widths: [28, 30, 22, 28, 52], freezeColumns: 1 },
  );

  const workPackageRows = board.workPackages.map((wp) => [
    wp.id,
    wp.title,
    wp.phase,
    wp.ownerRoles.join(", "),
    parseLocalDate(wp.dueAt),
    board.timezone,
    wp.dependsOn.join(", ") || "None",
    wp.status,
    null,
    (controlsByWp.get(wp.id) ?? []).join(", ") || "None",
    (assuranceByWp.get(wp.id) ?? []).join(", ") || "None",
    (canonicalExperimentsByWp.get(wp.id) ?? []).join(", ") || "None",
    summarizeItems(wp.deliverables, (item) => `${item.id}: ${item.description}`),
    summarizeItems(wp.acceptanceChecks, (item) => `${item.id} [${item.state}]: ${item.description}`),
    summarizeItems(wp.evidence, (item) => `${item.id} [${item.state}] ${item.locator}`),
    summarizeItems(wp.gates, (item) => `${item.id} [${item.state}] ${item.description}`),
  ]);
  const workSheet = wb.worksheets.getItem("Work_Packages");
  const workLayout = prepareDataSheet(
    workSheet,
    "VEGO-AI Iris Requirements — Canonical Work Packages",
    "Direct view of WP-001 through WP-029 from the canonical JSON board; no aggregate WP namespace remains.",
    ["WP_ID", "Work Package", "Phase", "Owner Roles", "Due (local)", "Timezone", "Dependencies", "Status", "Overdue", "Controls", "IRIS Experiments", "Canonical Experiments", "Deliverables", "Acceptance Checks", "Evidence", "Gates"],
    workPackageRows,
    { tableName: "CanonicalWorkPackagesTable", widths: [12, 38, 28, 24, 20, 18, 24, 24, 16, 28, 25, 25, 52, 58, 52, 48], freezeColumns: 2 },
  );
  workSheet.getRange(`E4:E${workLayout.lastRow}`).format.numberFormat = "yyyy-mm-dd hh:mm";
  workSheet.getRange("I4").formulas = [["=IF(OR(H4=\"accepted\",H4=\"accepted_ongoing\",H4=\"accepted_after_correction\",H4=\"superseded_approved\",H4=\"not_applicable_approved\"),\"CLOSED\",IF(E4<NOW(),\"OVERDUE\",\"ON TRACK\"))"]];
  workSheet.getRange(`I4:I${workLayout.lastRow}`).fillDown();
  addListValidation(workSheet.getRange(`H4:H${workLayout.lastRow}`), workStatusValues, "work-package status");
  applyStatusFormatting(workSheet.getRange(`H4:H${workLayout.lastRow}`));
  applyOverdueFormatting(workSheet.getRange(`I4:I${workLayout.lastRow}`));

  const controlRows = expectedControlIds.map((id) => {
    const main = controls.main.get(id);
    const dimensions = controls.dimensions.get(id);
    const kind = id.startsWith("R-") ? "Requirement" : id.startsWith("A-") ? "Action" : "Open question";
    return [
      id,
      kind,
      main.type,
      main.item,
      main.source,
      main.owner,
      main.due,
      main.dependencies,
      main.evidence,
      main.acceptanceCheck,
      dimensions.extraction,
      dimensions.implementation,
      dimensions.acceptance,
      "Pending",
      dimensions.ongoing,
      null,
      (board.coverageMap.controls[id] ?? []).join(", "),
      main.gateNote,
    ];
  });
  const controlSheet = wb.worksheets.getItem("Control_Acceptance");
  const controlLayout = prepareDataSheet(
    controlSheet,
    "Dynamic Control Acceptance — 19 Requirements / 15 Actions / 10 Questions",
    "Final state is Pending for all 44 baseline controls. New discovered controls must receive a stable ID and be appended; closure denominator then increases automatically.",
    ["Control_ID", "Kind", "Type", "Control Item", "Source", "Owner", "Due/Gate", "Dependencies", "Deliverable/Evidence", "Acceptance Check", "Extraction", "Implementation", "Acceptance", "Final State", "Ongoing Control", "Closure Eligible", "Canonical WPs", "Gate Note"],
    controlRows,
    { tableName: "ControlAcceptanceTable", widths: [12, 16, 28, 48, 40, 32, 30, 28, 48, 56, 34, 30, 38, 48, 48, 18, 26, 48], freezeColumns: 2 },
  );
  controlSheet.getRange("P4").formulas = [["=IF(OR(N4=\"Accepted\",N4=\"Accepted with ongoing control\",N4=\"Accepted after correction\",N4=\"Superseded by approved decision\",N4=\"Not applicable by approved Plan B or other decision\"),\"YES\",\"NO\")"]];
  controlSheet.getRange(`P4:P${controlLayout.lastRow}`).fillDown();
  addListValidation(controlSheet.getRange("N4:N200"), finalStateValues, "control final state");
  exactRule(controlSheet.getRange("P4:P200"), "YES", "#E2F0D9", "#2E7D32");
  exactRule(controlSheet.getRange("P4:P200"), "NO", "#FCE4D6", "#C00000");
  for (const state of finalStateValues.slice(1)) exactRule(controlSheet.getRange("N4:N200"), state, "#E2F0D9", "#2E7D32");
  exactRule(controlSheet.getRange("N4:N200"), "Pending", "#FFF2CC", "#9C6500");

  const experimentRows = [];
  for (const id of expectedIrisExperimentIds) {
    const parsed = irisExperiments.find((item) => item.id === id);
    const mappedWps = board.coverageMap.assuranceExperiments[id] ?? [];
    experimentRows.push([
      "Assurance",
      id,
      parsed?.cells[1] ?? id,
      parsed?.cells[2] ?? "Unknown",
      mappedWps.join(", "),
      "Governed by IRIS assurance protocol",
      parsed?.cells[4] ?? "See experiment register",
      parsed?.cells[6] ?? "No interpretation beyond registered boundary",
    ]);
  }

  const experimentDirectories = await fs.readdir(path.join(root, "experiments"), { withFileTypes: true });
  for (const id of expectedCanonicalExperimentIds) {
    const directory = experimentDirectories.find((item) => item.isDirectory() && item.name.startsWith(`${id}-`));
    const mappedWps = board.coverageMap.canonicalExperiments[id] ?? [];
    const statusText = mappedWps.map((wpId) => `${wpId}:${wpById.get(wpId)?.status ?? "unknown"}`).join("; ");
    experimentRows.push([
      "Canonical scientific",
      id,
      directory ? directory.name.slice(id.length + 1).replaceAll("-", " ") : id,
      statusText || "No mapped work package",
      mappedWps.join(", ") || "None",
      id,
      directory ? `experiments/${directory.name}/README.md` : "Missing canonical directory",
      "No result claim before the canonical protocol, human gates, and claim-state checks pass.",
    ]);
  }

  for (const id of expectedScientificIds) {
    const parsed = scientificExperiments.find((item) => item.id === id);
    experimentRows.push([
      "Proposal alias",
      id,
      parsed?.cells[0]?.replace(`${id} — `, "") ?? id,
      parsed?.cells[5] ?? "Planned / human-gated",
      "See canonical mapping",
      parsed?.cells[3] ?? "See scientific crosswalk",
      "docs/research/phd-proposal/scientific-experiment-crosswalk.md",
      parsed?.cells[6] ?? "Alias has no independent result state.",
    ]);
  }
  const experimentSheet = wb.worksheets.getItem("Experiment_Crosswalk");
  prepareDataSheet(
    experimentSheet,
    "Experiment Coverage and Crosswalk",
    "All 10 IRIS assurance experiments, 10 canonical execution experiments, and 6 SCI proposal aliases are explicit; SCI aliases never create a second result set.",
    ["Layer", "Experiment_ID", "Name", "Current Evidence State", "Mapped WPs", "Canonical/Related Mapping", "Locator", "Claim Boundary"],
    experimentRows,
    { tableName: "ExperimentCrosswalkTable", widths: [20, 18, 38, 48, 28, 58, 46, 58], freezeColumns: 2 },
  );

  const gateBindingsByRole = new Map();
  for (const [gateId, binding] of Object.entries(board.gateEvidenceBindings)) {
    for (const role of binding.requiredApproverRoles) {
      if (!gateBindingsByRole.has(role)) gateBindingsByRole.set(role, []);
      gateBindingsByRole.get(role).push(gateId);
    }
  }
  const roleRows = board.roles.map((role) => {
    const status = role.filled ? (role.kind === "tool" ? "Tool available" : "Filled") : role.kind === "external_gate" ? "Unfilled external" : "Unfilled human";
    const requiredEvidence = role.kind === "tool"
      ? "Deterministic local validator output"
      : role.kind === "external_gate"
        ? "Written role acceptance and authoritative evidence"
        : role.kind === "human_gate"
          ? "Name, acceptance, availability, and independent evidence return"
          : "Dated decisions and role-specific acceptance evidence";
    return [
      role.id,
      role.title,
      role.kind,
      role.name,
      role.filled ? "YES" : "NO",
      status,
      (gateBindingsByRole.get(role.id) ?? []).join(", ") || "None",
      requiredEvidence,
      role.filled ? "Role exists; evidence gates still apply" : "Mapped gates remain blocked",
    ];
  });
  const roleSheet = wb.worksheets.getItem("Role_Assignments");
  prepareDataSheet(
    roleSheet,
    "All 19 Canonical Human, External, and Tool Roles",
    "Roles are copied from the canonical board. Unfilled roles remain explicit blockers; data, ethics, VDI, and methods roles are not bundled.",
    ["Role_ID", "Role", "Kind", "Current Assignee", "Filled", "Status", "Gate Bindings", "Evidence Required", "Fail-Closed Consequence"],
    roleRows,
    { tableName: "CanonicalRolesTable", widths: [26, 42, 20, 28, 12, 22, 38, 48, 38], freezeColumns: 2 },
  );
  exactRule(roleSheet.getRange("E4:E22"), "YES", "#E2F0D9", "#2E7D32");
  exactRule(roleSheet.getRange("E4:E22"), "NO", "#FCE4D6", "#C00000");

  const scheduleRows = board.workPackages.map((wp) => [
    parseLocalDate(wp.dueAt),
    board.timezone,
    wp.id,
    wp.title,
    wp.ownerRoles.join(", "),
    wp.status,
    null,
    summarizeItems(wp.acceptanceChecks, (item) => `${item.id} [${item.state}]`),
  ]);
  const scheduleSheet = wb.worksheets.getItem("Schedule");
  const scheduleLayout = prepareDataSheet(
    scheduleSheet,
    "Canonical Dependency-Ordered Schedule",
    "Due values are real Excel dates with an explicit Asia/Jerusalem timezone column. Overdue is calculated from NOW(); working targets remain provisional where noted in source controls.",
    ["Due (local)", "Timezone", "WP_ID", "Checkpoint", "Owner Roles", "Status", "Overdue", "Acceptance Evidence"],
    scheduleRows,
    { tableName: "CanonicalScheduleTable", widths: [22, 18, 12, 48, 28, 24, 16, 42], freezeColumns: 3 },
  );
  scheduleSheet.getRange(`A4:A${scheduleLayout.lastRow}`).format.numberFormat = "yyyy-mm-dd hh:mm";
  scheduleSheet.getRange("G4").formulas = [["=IF(OR(F4=\"accepted\",F4=\"accepted_ongoing\",F4=\"accepted_after_correction\",F4=\"superseded_approved\",F4=\"not_applicable_approved\"),\"CLOSED\",IF(A4<NOW(),\"OVERDUE\",\"ON TRACK\"))"]];
  scheduleSheet.getRange(`G4:G${scheduleLayout.lastRow}`).fillDown();
  addListValidation(scheduleSheet.getRange(`F4:F${scheduleLayout.lastRow}`), workStatusValues, "schedule status");
  applyStatusFormatting(scheduleSheet.getRange(`F4:F${scheduleLayout.lastRow}`));
  applyOverdueFormatting(scheduleSheet.getRange(`G4:G${scheduleLayout.lastRow}`));

  const decisionRows = DECISIONS.map(([id, request, priority]) => [
    id,
    request,
    priority,
    "Pending",
    null,
    "Iris and Arnon",
    null,
    null,
    "RQ pack; proposal; deck; master",
    "Not started",
  ]);
  const decisionSheet = wb.worksheets.getItem("Decision_Log");
  const decisionLayout = prepareDataSheet(
    decisionSheet,
    "August 5 Supervisor Decision Capture",
    "Silence is Defer. Retire or supersede is explicitly representable; written propagation evidence remains required.",
    ["Decision_ID", "Decision Requested", "Priority", "Outcome", "Exact Correction/Rationale", "Approver", "Owner", "Written Deadline", "Affected Artifacts", "Propagation Status"],
    decisionRows,
    { tableName: "DecisionLogTable", widths: [16, 44, 18, 28, 48, 24, 22, 22, 40, 24], freezeColumns: 2 },
  );
  addListValidation(decisionSheet.getRange("D4:D100"), decisionValues, "decision outcome");
  const decisionRange = decisionSheet.getRange("D4:D100");
  exactRule(decisionRange, "Pending", "#FFF2CC", "#9C6500");
  exactRule(decisionRange, "Confirm", "#E2F0D9", "#2E7D32");
  exactRule(decisionRange, "Confirm with correction", "#D9EAF7", "#1F4E78");
  exactRule(decisionRange, "Retire or supersede", "#E7E6E6", "#595959");
  exactRule(decisionRange, "Defer", "#FFF2CC", "#9C6500");

  const humanRows = humanReviewRows();
  const humanSheet = wb.worksheets.getItem("Human_Review");
  const humanLayout = prepareDataSheet(
    humanSheet,
    "July 29 Zoom Human Review — Operational Batches",
    "Chronological PRI/REM ranges cover S-0001 through S-1195 exactly once. Calibration and full-media rows are separate evidence controls.",
    ["Batch_ID", "Segment Range", "Segment Count", "Purpose", "Reviewer A", "Reviewer B", "Adjudicator", "Status", "Due", "Overdue", "Completion Evidence"],
    humanRows,
    { tableName: "HumanReviewBatchesTable", widths: [14, 22, 15, 48, 20, 20, 20, 24, 16, 16, 42], freezeColumns: 2 },
  );
  humanSheet.getRange(`I4:I${humanLayout.lastRow}`).format.numberFormat = "yyyy-mm-dd";
  humanSheet.getRange("J4").formulas = [["=IF(OR(H4=\"Reviewer complete\",H4=\"Adjudicated\"),\"CLOSED\",IF(I4<NOW(),\"OVERDUE\",\"ON TRACK\"))"]];
  humanSheet.getRange(`J4:J${humanLayout.lastRow}`).fillDown();
  addListValidation(humanSheet.getRange("H4:H100"), reviewValues, "review status");
  const reviewRange = humanSheet.getRange("H4:H100");
  exactRule(reviewRange, "Not started", "#E7E6E6", "#595959");
  exactRule(reviewRange, "Calibration", "#D9EAF7", "#1F4E78");
  exactRule(reviewRange, "In progress", "#D9EAF7", "#1F4E78");
  exactRule(reviewRange, "Reviewer complete", "#E2F0D9", "#2E7D32");
  exactRule(reviewRange, "Adjudication required", "#FFF2CC", "#9C6500");
  exactRule(reviewRange, "Adjudicated", "#E2F0D9", "#2E7D32");
  applyOverdueFormatting(humanSheet.getRange("J4:J100"));

  const literatureSheet = wb.worksheets.getItem("Literature_Search");
  const literatureLayout = prepareDataSheet(
    literatureSheet,
    "Literature Search Execution Register — Protocol Ready, Not Run",
    "Rows are generated from the tracked QL-01 through QL-05 execution register. Blank dates/counts are evidence-honest, not missing generated data.",
    ["Query_ID", "Concept", "Frozen Boolean Query", "Database", "Field/Filter Handling", "Status", "Search Date", "Returned", "Included", "SQ/Study Mapping", "Evidence/Access Note"],
    literatureRows,
    { tableName: "LiteratureExecutionTable", widths: [12, 32, 72, 22, 42, 26, 20, 14, 14, 34, 42], freezeColumns: 2 },
  );
  literatureSheet.getRange(`G4:G${literatureLayout.lastRow}`).format.numberFormat = "yyyy-mm-dd hh:mm";
  const literatureStatusValues = ["Protocol ready / not run", "In progress", "Executed", "Blocked", "Not applicable"];
  addListValidation(literatureSheet.getRange("F4:F100"), literatureStatusValues, "literature status");
  const literatureStatusRange = literatureSheet.getRange("F4:F100");
  exactRule(literatureStatusRange, "Protocol ready / not run", "#FFF2CC", "#9C6500");
  exactRule(literatureStatusRange, "In progress", "#D9EAF7", "#1F4E78");
  exactRule(literatureStatusRange, "Executed", "#E2F0D9", "#2E7D32");
  exactRule(literatureStatusRange, "Blocked", "#FCE4D6", "#C00000");
  exactRule(literatureStatusRange, "Not applicable", "#E7E6E6", "#595959");

  const medicalSheet = wb.worksheets.getItem("Medical_Gates");
  const medicalLayout = prepareDataSheet(
    medicalSheet,
    "Plan A Medical Readiness — NO-GO at 0/6",
    "No row-level medical work begins unless every gate reaches PASS with authorized evidence. At 0–5/6 on August 26, Plan B activates.",
    ["Gate", "Required Control", "Accountable Roles", "Named Owner", "Evidence Path", "Feasible Date", "Actual Result", "Checkpoint Disposition", "Current Blocker"],
    MEDICAL_GATES,
    { tableName: "MedicalReadinessTable", widths: [16, 48, 38, 24, 38, 20, 18, 34, 42], freezeColumns: 2 },
  );
  medicalSheet.getRange(`F4:F${medicalLayout.lastRow}`).format.numberFormat = "yyyy-mm-dd";
  addListValidation(medicalSheet.getRange("G4:G100"), gateValues, "medical gate result");
  applyGateFormatting(medicalSheet.getRange("G4:G100"));

  const acceptanceSheet = wb.worksheets.getItem("Acceptance_Tests");
  const acceptanceLayout = prepareDataSheet(
    acceptanceSheet,
    "Current Acceptance and Release Gates",
    "Structure PASS never substitutes for readiness or closure. Human, external, medical, empirical, and submission gates remain fail-closed.",
    ["Test_ID", "Gate", "Required Result", "Current Result", "Mode", "Evidence", "Release Effect"],
    ACCEPTANCE_TESTS,
    { tableName: "AcceptanceTestsTable", widths: [12, 42, 28, 28, 18, 46, 42], freezeColumns: 2 },
  );
  addListValidation(acceptanceSheet.getRange("D4:D100"), [...gateValues, "29/29", "10/10", "10/10; 10/10; 6/6"], "acceptance result");
  applyGateFormatting(acceptanceSheet.getRange("D4:D100"));

  const executive = wb.worksheets.getItem("Executive");
  executive.getRange("A1:K1").merge();
  executive.getRange("A1").values = [["VEGO-AI Iris Requirements — Canonical Execution Control"]];
  executive.getRange("A3:K3").merge();
  executive.getRange("A3").values = [["Evidence-honest baseline: canonical work, control, experiment, role, and schedule denominators are visible; human and external gates remain open."]];
  executive.getRange("A5:B5").values = [["Baseline Metric", "Current Value"]];
  executive.getRange("D5:E5").values = [["Canonical WP Status", "Count"]];
  executive.getRange("G5:K5").merge();
  executive.getRange("G5").values = [["Immediate Critical Path"]];
  executive.getRange("A6:A14").values = [
    ["Control rows"],
    ["Closure-eligible controls"],
    ["Supervisor decisions"],
    ["Transcript dual review"],
    ["EXP-005 safe labels"],
    ["Medical readiness"],
    ["Recipient access tests"],
    ["Experiment IDs visible"],
    ["Canonical roles visible"],
  ];
  executive.getRange("B6").formulas = [["=COUNTA('Control_Acceptance'!$A$4:$A$200)"]];
  executive.getRange("B7").formulas = [["=COUNTIF('Control_Acceptance'!$P$4:$P$200,\"YES\")&\"/\"&COUNTA('Control_Acceptance'!$A$4:$A$200)"]];
  executive.getRange("B8").formulas = [["=COUNTIF('Decision_Log'!$D$4:$D$13,\"<>Pending\")&\"/10\""]];
  executive.getRange("B9:B10").values = [["0/1,195"], ["0/24"]];
  executive.getRange("B11").formulas = [["=COUNTIF('Medical_Gates'!$G$4:$G$9,\"PASS\")&\"/6\""]];
  executive.getRange("B12:B13").values = [["0/2"], ["26/26 (10 IRIS + 10 canonical + 6 SCI)"]];
  executive.getRange("B14").formulas = [["=COUNTA('Role_Assignments'!$A$4:$A$22)&\"/19\""]];
  executive.getRange("D6:D10").values = [["blocked"], ["partial"], ["planned"], ["evidence_ready"], ["accepted/final"]];
  executive.getRange("E6").formulas = [["=COUNTIF('Work_Packages'!$H$4:$H$32,D6)"]];
  executive.getRange("E6:E8").fillDown();
  executive.getRange("E9").formulas = [["=COUNTIF('Work_Packages'!$H$4:$H$32,D9)"]];
  executive.getRange("E10").formulas = [["=SUM(COUNTIF('Work_Packages'!$H$4:$H$32,{\"accepted\",\"accepted_ongoing\",\"accepted_after_correction\",\"superseded_approved\",\"not_applicable_approved\"}))"]];
  executive.getRange("G6:K12").values = [
    [1, "Reconcile overdue canonical source/provenance gate", "partial", "WP-001", "Human review pending"],
    [2, "Complete two independent bilingual reviews", "blocked", "WP-002", "0/1,195 per reviewer"],
    [3, "Rehearse exact presentation", "blocked", "WP-005", "Human rehearsal not run"],
    [4, "Approve/deliver/access-test exact package", "blocked", "WP-006", "Not shared or tested"],
    [5, "Obtain August 5 decisions", "planned", "WP-007", "0/10 outcomes"],
    [6, "Execute first literature tranche", "partial", "WP-009", "Protocol ready; not run"],
    [7, "Keep medicine NO-GO unless G1–G6 pass", "blocked", "WP-018", "0/6"],
  ];
  executive.getRange("A16:K16").merge();
  executive.getRange("A16").values = [["Do not claim completion: structure can pass while readiness and closure remain non-zero until real human/external evidence exists."]];
  executive.getRange("A18:B18").values = [["Workbook as-of (dynamic)", null]];
  executive.getRange("B18").formulas = [["=NOW()"]];
  executive.getRange("B18").format.numberFormat = "yyyy-mm-dd hh:mm";

  executive.getRange("A1:K1").format = { fill: "#1F4E78", font: { color: "#FFFFFF", bold: true, size: 17 }, verticalAlignment: "center" };
  executive.getRange("A3:K3").format = { fill: "#FFF2CC", font: { color: "#7F6000", bold: true, size: 10 }, wrapText: true, verticalAlignment: "center" };
  for (const range of ["A5:B5", "D5:E5", "G5:K5"]) executive.getRange(range).format = { fill: "#2F75B5", font: { color: "#FFFFFF", bold: true }, horizontalAlignment: "center", verticalAlignment: "center" };
  executive.getRange("A6:K14").format = { font: { size: 10 }, wrapText: true, verticalAlignment: "top" };
  executive.getRange("A16:K16").format = { fill: "#FCE4D6", font: { color: "#C00000", bold: true }, wrapText: true };
  executive.getRange("A1:K18").format.borders = { preset: "inside", style: "thin", color: "#D9E2F3" };
  [24, 34, 4, 24, 12, 4, 8, 44, 22, 16, 34].forEach((width, index) => executive.getRange(`${columnName(index + 1)}1:${columnName(index + 1)}34`).format.columnWidth = width);
  applyStatusFormatting(executive.getRange("D6:D10"));
  applyStatusFormatting(executive.getRange("I6:I12"));
  const chart = executive.charts.add("bar", executive.getRange("D5:E10"));
  chart.title = "Canonical Work-Package Distribution";
  chart.hasLegend = false;
  chart.setPosition("A20", "K36");
  executive.showGridLines = false;
  executive.freezePanes.freezeRows(5);

  const renderedSheets = [];
  await fs.mkdir(outputDir, { recursive: true });
  await fs.mkdir(previewDir, { recursive: true });
  for (const name of sheetNames) {
    const preview = await wb.render({ sheetName: name, autoCrop: "all", scale: 1, format: "png" });
    const previewPath = path.join(previewDir, `${name}.png`);
    await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));
    renderedSheets.push({ name, previewPath });
  }

  const inspect = await wb.inspect({
    kind: "workbook,sheet,table,formula",
    maxChars: 200000,
    tableMaxRows: 8,
    tableMaxCols: 12,
    tableMaxCellChars: 120,
    options: { maxResults: 1000 },
  });
  const inspectText = inspect.ndjson ?? JSON.stringify(inspect);
  const formulaErrors = [];
  for (const name of sheetNames) {
    const used = wb.worksheets.getItem(name).getUsedRange();
    const values = used.values;
    const formulas = used.formulas;
    for (let rowIndex = 0; rowIndex < values.length; rowIndex += 1) {
      for (let columnIndex = 0; columnIndex < (values[rowIndex]?.length ?? 0); columnIndex += 1) {
        const value = values[rowIndex][columnIndex];
        if (typeof value === "string" && /^#(REF!|DIV\/0!|VALUE!|NAME\?|N\/A|NUM!|NULL!)/.test(value)) {
          formulaErrors.push({
            sheet: name,
            cell: `${columnName(columnIndex + 1)}${rowIndex + 1}`,
            value,
            formula: formulas[rowIndex]?.[columnIndex] ?? null,
          });
        }
      }
    }
  }
  if (formulaErrors.length) throw new Error(`Formula errors detected: ${JSON.stringify(formulaErrors)}`);

  const xlsx = await SpreadsheetFile.exportXlsx(wb);
  const tempPath = `${outputPath}.tmp.xlsx`;
  await xlsx.save(tempPath);
  await fs.copyFile(tempPath, outputPath);
  await applyNativeFreezePanes(outputPath);
  await fs.rm(tempPath, { force: true });
  await fs.rm(`${tempPath}.inspect.ndjson`, { force: true });
  const outputBytes = await fs.readFile(outputPath);
  const sha256 = crypto.createHash("sha256").update(outputBytes).digest("hex").toUpperCase();

  const auditSummary = {
    schemaVersion: "VegoIrisExecutionWorkbookBuild-v2",
    outputPath,
    sha256,
    size: outputBytes.length,
    sheetCount: sheetNames.length,
    sheets: sheetNames,
    controlCoverage: `${expectedControlIds.length}/${expectedControlIds.length}`,
    workPackageCoverage: `${board.workPackages.length}/29`,
    roleCoverage: `${board.roles.length}/19`,
    irisExperimentCoverage: `${expectedIrisExperimentIds.length}/10`,
    canonicalExperimentCoverage: `${expectedCanonicalExperimentIds.length}/10`,
    scientificAliasCoverage: `${expectedScientificIds.length}/6`,
    formulaErrors: formulaErrors.length,
    renderedSheets: renderedSheets.length,
    evidenceBoundary: board.claimBoundary,
  };
  await Promise.all([
    fs.writeFile(path.join(outputDir, "execution-control-inspect.ndjson"), `${inspectText}\n${JSON.stringify(auditSummary)}\n`, "utf8"),
    fs.writeFile(`${outputPath}.inspect.ndjson`, `${inspectText}\n${JSON.stringify(auditSummary)}\n`, "utf8"),
    fs.writeFile(path.join(outputDir, "execution-control-formula-errors.ndjson"), `${JSON.stringify({ formulaErrors: [] })}\n`, "utf8"),
  ]);
  console.log(JSON.stringify(auditSummary, null, 2));
}

await main();
