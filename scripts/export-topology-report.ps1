[CmdletBinding()]
param(
    [string]$OutputDir = "artifacts\topology-export",
    [switch]$Open
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$outputPath = Join-Path $repoRoot $OutputDir
$htmlPath = Join-Path $outputPath "VEGO_TOPOLOGY_FLOW_REPORT.html"
$pdfPath = Join-Path $outputPath "VEGO_TOPOLOGY_FLOW_REPORT.pdf"
$generatedAt = Get-Date -Format "yyyy-MM-dd HH:mm zzz"

function Get-EdgePath {
    $command = Get-Command msedge -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $candidates = @(
        "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    return $null
}

New-Item -ItemType Directory -Force -Path $outputPath | Out-Null

$html = @"
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>VEGO-AI Topology And Flow Report</title>
  <style>
    :root {
      --ink: #172033;
      --muted: #526070;
      --line: #c9d3df;
      --blue: #0b5cad;
      --teal: #0f766e;
      --green: #2f7d32;
      --amber: #9a6700;
      --red: #b42318;
      --bg: #f7f9fc;
      --panel: #ffffff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font: 14px/1.55 "Segoe UI", Arial, sans-serif;
      color: var(--ink);
      background: var(--bg);
    }
    main {
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px;
    }
    h1, h2, h3 { margin: 0 0 12px; line-height: 1.2; }
    h1 { font-size: 34px; }
    h2 { font-size: 22px; margin-top: 28px; border-bottom: 2px solid var(--line); padding-bottom: 8px; }
    h3 { font-size: 16px; margin-top: 18px; }
    p { margin: 0 0 10px; }
    .subtitle { color: var(--muted); font-size: 16px; }
    .meta { color: var(--muted); margin-top: 8px; }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      margin: 16px 0;
      break-inside: avoid;
    }
    .grid {
      display: grid;
      gap: 12px;
    }
    .grid-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
    .grid-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .node {
      border: 1px solid var(--line);
      border-top: 5px solid var(--blue);
      background: #fff;
      border-radius: 8px;
      padding: 12px;
      min-height: 88px;
    }
    .node h3 { margin: 0 0 6px; font-size: 15px; }
    .node p { margin: 0; color: var(--muted); font-size: 13px; }
    .baseline { border-top-color: var(--blue); }
    .memory { border-top-color: var(--teal); }
    .evaluation { border-top-color: var(--green); }
    .blocked { border-top-color: var(--red); }
    .ops { border-top-color: var(--amber); }
    .chain {
      display: flex;
      flex-wrap: wrap;
      align-items: stretch;
      gap: 8px;
      margin-top: 10px;
    }
    .step {
      flex: 1 1 150px;
      min-width: 140px;
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      position: relative;
    }
    .step strong { display: block; margin-bottom: 4px; }
    .arrow {
      align-self: center;
      color: var(--muted);
      font-weight: 700;
    }
    table {
      border-collapse: collapse;
      width: 100%;
      background: #fff;
      margin-top: 10px;
    }
    th, td {
      border: 1px solid var(--line);
      padding: 8px 10px;
      text-align: left;
      vertical-align: top;
    }
    th { background: #edf2f7; }
    code {
      background: #eef2f7;
      border: 1px solid #d7dee8;
      border-radius: 5px;
      padding: 1px 5px;
      font-family: Consolas, "Courier New", monospace;
    }
    pre {
      background: #111827;
      color: #f9fafb;
      padding: 14px;
      border-radius: 8px;
      overflow: auto;
      font-family: Consolas, "Courier New", monospace;
      font-size: 13px;
    }
    .callout {
      border-left: 5px solid var(--red);
      background: #fff7f7;
      padding: 12px 14px;
      margin: 14px 0;
    }
    .ok {
      border-left-color: var(--green);
      background: #f4fbf5;
    }
    @media print {
      body { background: #fff; }
      main { max-width: none; padding: 20px; }
      .panel { page-break-inside: avoid; }
      a { color: var(--ink); text-decoration: none; }
    }
  </style>
</head>
<body>
<main>
  <h1>VEGO-AI Topology And Flow Report</h1>
  <p class="subtitle">How the baseline VEGO pipeline, reusable human judgment layer, experiments, dashboard, visualizer, and wiki fit together.</p>
  <p class="meta">Generated: $generatedAt<br>Workspace: $repoRoot</p>

  <section class="panel">
    <h2>1. Core Topology</h2>
    <div class="grid grid-4">
      <div class="node baseline">
        <h3>Inputs</h3>
        <p>Student UML/domain models, settings, guidelines, and existing VEGO result artifacts.</p>
      </div>
      <div class="node baseline">
        <h3>Baseline VEGO-AI</h3>
        <p>Agents 1-4 assess models and produce original variability classifications.</p>
      </div>
      <div class="node memory">
        <h3>Human Judgment Layer</h3>
        <p>M1-M4B-1 captures, stores, retrieves, and compares reusable human judgment.</p>
      </div>
      <div class="node evaluation">
        <h3>Evidence Layer</h3>
        <p>EXP-001 to EXP-005, dashboard, visualizer, reports, thesis, and wiki.</p>
      </div>
    </div>
  </section>

  <section class="panel">
    <h2>2. Baseline And Memory Flow</h2>
    <div class="chain">
      <div class="step"><strong>Student Models</strong>UML/domain model submissions.</div>
      <div class="arrow">-&gt;</div>
      <div class="step"><strong>Agent 1</strong>Language Advisor.</div>
      <div class="arrow">-&gt;</div>
      <div class="step"><strong>Agent 2</strong>Domain Advisor.</div>
      <div class="arrow">-&gt;</div>
      <div class="step"><strong>Agent 3</strong>Model Inspector.</div>
      <div class="arrow">-&gt;</div>
      <div class="step"><strong>Agent 4</strong>Variability Explorer.</div>
      <div class="arrow">-&gt;</div>
      <div class="step"><strong>Original Output</strong>Substantial / Occasional classification.</div>
    </div>
    <div class="chain">
      <div class="step"><strong>M1</strong>Human Review Queue detects uncertain or important cases.</div>
      <div class="arrow">-&gt;</div>
      <div class="step"><strong>M2</strong>Human Feedback Manager captures expert decisions structurally.</div>
      <div class="arrow">-&gt;</div>
      <div class="step"><strong>M3</strong>Human Judgment Memory stores reusable knowledge.</div>
      <div class="arrow">-&gt;</div>
      <div class="step"><strong>M4A</strong>Memory Advisory Layer retrieves relevant judgments.</div>
      <div class="arrow">-&gt;</div>
      <div class="step"><strong>M4B-1</strong>Parallel memory-informed comparison.</div>
    </div>
    <div class="callout">
      <strong>Boundary:</strong> M4B-1 does not overwrite the original Agent 4 output. It produces a parallel comparison artifact and keeps baseline behavior unchanged.
    </div>
  </section>

  <section class="panel">
    <h2>3. Research Evaluation Flow</h2>
    <div class="grid grid-3">
      <div class="node evaluation">
        <h3>EXP-001</h3>
        <p>Mechanism/readiness evaluation of M4B-1 comparisons.</p>
      </div>
      <div class="node evaluation">
        <h3>EXP-002 / EXP-003</h3>
        <p>Expert labeling package and strict accuracy/error-analysis tooling.</p>
      </div>
      <div class="node evaluation">
        <h3>EXP-004</h3>
        <p>Synthetic policy sensitivity only. Useful for risk screening, not proof.</p>
      </div>
      <div class="node evaluation">
        <h3>EXP-005</h3>
        <p>Real-label accuracy gate with blind labels and downstream rerun support.</p>
      </div>
      <div class="node blocked">
        <h3>Blocked Claim</h3>
        <p>Accuracy improvement cannot be claimed until enough safe expert labels exist.</p>
      </div>
      <div class="node memory">
        <h3>Future Gate</h3>
        <p>M4B-1.1 or M4B-2 only after real labels justify a deterministic change.</p>
      </div>
    </div>
  </section>

  <section class="panel">
    <h2>4. Operational Flow</h2>
    <div class="chain">
      <div class="step"><strong>Memory Start</strong><code>agent-memory-start.ps1</code></div>
      <div class="arrow">-&gt;</div>
      <div class="step"><strong>Workbench</strong><code>open-vego-workbench.ps1</code></div>
      <div class="arrow">-&gt;</div>
      <div class="step"><strong>Dashboard</strong>Local static HTML report.</div>
      <div class="arrow">+</div>
      <div class="step"><strong>Visualizer</strong>Tkinter GUI for inspecting model/result pairs.</div>
      <div class="arrow">+</div>
      <div class="step"><strong>EXP-005 Labels</strong>Blind label sheet and label-first summary.</div>
      <div class="arrow">-&gt;</div>
      <div class="step"><strong>Wiki Outbox</strong>Curated Confluence markdown pages.</div>
    </div>
  </section>

  <section class="panel">
    <h2>5. Current Evidence State</h2>
    <table>
      <tr><th>Measure</th><th>Current Value</th><th>Interpretation</th></tr>
      <tr><td>M4B-1 comparison rows</td><td>27</td><td>Comparison mechanism exists.</td></tr>
      <tr><td>Generalization-safe candidates</td><td>24</td><td>Rows ready for expert labeling.</td></tr>
      <tr><td>Safe expert labels</td><td>0</td><td>Accuracy cannot be evaluated yet.</td></tr>
      <tr><td>Memory-informed classification changes</td><td>0 / 27</td><td>Current M4B-1 clarifies and escalates; it does not change classification.</td></tr>
      <tr><td>Review-after-memory cases</td><td>2</td><td>Useful cases for supervisor review.</td></tr>
      <tr><td>Accuracy claim</td><td>Not allowed</td><td>Requires at least 20 safe expert labels, preferably 30-50.</td></tr>
    </table>
  </section>

  <section class="panel">
    <h2>6. Key Commands</h2>
    <pre>.\scripts\open-vego-workbench.ps1 -Gui
.\scripts\build-exp005-label-review.ps1
.\scripts\build-exp005-label-review.ps1 -FilledLabelsSheet reports\generated\exp005_label_review\exp005_label_review_blind.csv -RunDownstream
.\scripts\build-confluence-wiki.ps1
.\scripts\dashboard-health.ps1 -RequireOutbox</pre>
  </section>

  <section class="panel">
    <h2>7. What Not To Change Yet</h2>
    <div class="callout">
      Do not implement M4B-2, do not modify Agent 4, do not overwrite <code>VEGO-AI/eval_output</code>, do not call LLM/API services for reclassification, and do not claim accuracy improvement until EXP-005 has enough real labels.
    </div>
  </section>
</main>
</body>
</html>
"@

Set-Content -LiteralPath $htmlPath -Value $html -Encoding UTF8
Write-Host "HTML exported: $htmlPath"

$edgePath = Get-EdgePath
if ($edgePath) {
    if (Test-Path -LiteralPath $pdfPath) {
        Remove-Item -LiteralPath $pdfPath -Force
    }

    $fileUrl = "file:///" + ($htmlPath -replace "\\", "/")
    $edgeArgs = @(
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--allow-file-access-from-files",
        "--virtual-time-budget=3000",
        "--print-to-pdf=$pdfPath",
        $fileUrl
    )
    & $edgePath @edgeArgs | Out-Null

    $deadline = (Get-Date).AddSeconds(15)
    while ((-not (Test-Path -LiteralPath $pdfPath)) -and (Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 250
    }

    if ((Test-Path -LiteralPath $pdfPath) -and (Get-Item -LiteralPath $pdfPath).Length -gt 0) {
        Write-Host "PDF exported: $pdfPath"
    }
    else {
        throw "PDF export failed: $pdfPath was not created."
    }
}
else {
    Write-Warning "Microsoft Edge was not found. HTML was exported, but PDF was not generated."
}

if ($Open) {
    Start-Process -FilePath (Resolve-Path -LiteralPath $htmlPath)
    if (Test-Path -LiteralPath $pdfPath) {
        Start-Process -FilePath (Resolve-Path -LiteralPath $pdfPath)
    }
}
