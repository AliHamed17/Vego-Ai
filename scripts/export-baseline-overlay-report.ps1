[CmdletBinding()]
param(
    [string]$OutputDir = "artifacts\topology-export",
    [switch]$Open
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$outputPath = Join-Path $repoRoot $OutputDir
$htmlPath = Join-Path $outputPath "VEGO_BASELINE_OVERLAY_REPORT.html"
$pdfPath = Join-Path $outputPath "VEGO_BASELINE_OVERLAY_REPORT.pdf"
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
  <title>VEGO-AI Baseline Architecture With Human Judgment Overlay</title>
  <style>
    :root {
      --ink: #172033;
      --muted: #526070;
      --panel: #ffffff;
      --line: #cbd5e1;
      --baseline: #243447;
      --blue: #2f75b5;
      --green: #1f8a70;
      --purple: #6d3fa3;
      --orange: #c47a00;
      --overlay: #d6336c;
      --overlay2: #0b7285;
      --bg: #f7f9fc;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.45 "Segoe UI", Arial, sans-serif;
    }
    main {
      max-width: 1320px;
      margin: 0 auto;
      padding: 28px;
    }
    h1 { margin: 0; font-size: 30px; }
    h2 { margin: 28px 0 10px; font-size: 21px; border-bottom: 2px solid var(--line); padding-bottom: 7px; }
    p { margin: 6px 0; }
    .meta { color: var(--muted); }
    .sheet {
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      margin-top: 16px;
      overflow-x: auto;
    }
    svg {
      display: block;
      width: 100%;
      height: auto;
      background: #fff;
      border: 1px solid #d0d7de;
    }
    .base-box { fill: #f8fafc; stroke: #6b7280; stroke-width: 2.2; }
    .agent-text { fill: white; font-weight: 700; font-size: 16px; }
    .small-text { fill: #172033; font-size: 13px; }
    .tiny { font-size: 11px; }
    .legend {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-top: 12px;
    }
    .legend div {
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      background: #fff;
    }
    .swatch {
      display: inline-block;
      width: 14px;
      height: 14px;
      border-radius: 3px;
      margin-right: 6px;
      vertical-align: -2px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      background: #fff;
    }
    th, td {
      border: 1px solid var(--line);
      padding: 8px 10px;
      vertical-align: top;
      text-align: left;
    }
    th { background: #eef2f7; }
    code {
      background: #eef2f7;
      border: 1px solid #d7dee8;
      border-radius: 5px;
      padding: 1px 5px;
      font-family: Consolas, "Courier New", monospace;
    }
    .callout {
      border-left: 5px solid var(--overlay);
      background: #fff5f7;
      padding: 12px;
      margin-top: 12px;
    }
    @media print {
      body { background: #fff; }
      main { max-width: none; padding: 16px; }
      .sheet { page-break-inside: avoid; }
    }
  </style>
</head>
<body>
<main>
  <h1>VEGO-AI Baseline Architecture With Human Judgment Overlay</h1>
  <p class="meta">Generated: $generatedAt<br>Base concept: Figure 1, VEGO-AI Architecture, main research PDF. Overlay: current M1-M4B-1 + EXP-005 research flow.</p>

  <section class="sheet">
    <svg viewBox="0 0 1280 760" role="img" aria-label="VEGO-AI baseline architecture with human judgment memory overlay">
      <defs>
        <marker id="arrowBase" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L9,3 z" fill="#243447"/>
        </marker>
        <marker id="arrowOverlay" markerWidth="12" markerHeight="12" refX="10" refY="4" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,8 L11,4 z" fill="#d6336c"/>
        </marker>
        <marker id="arrowTeal" markerWidth="12" markerHeight="12" refX="10" refY="4" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,8 L11,4 z" fill="#0b7285"/>
        </marker>
        <filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">
          <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.22"/>
        </filter>
      </defs>

      <text x="42" y="44" font-size="24" font-family="Georgia, serif">Not All Differences Matter</text>
      <text x="840" y="44" font-size="22" font-family="Georgia, serif">MODELS, October, 2026, Malaga, Spain</text>

      <!-- Baseline figure frame -->
      <rect x="285" y="150" width="700" height="395" class="base-box"/>

      <!-- External inputs/outputs -->
      <rect x="76" y="332" width="175" height="58" rx="7" fill="#dff0da" stroke="#6eaa5e" stroke-width="2"/>
      <text x="116" y="366" class="small-text" font-weight="700">Domain Description</text>

      <rect x="72" y="508" width="180" height="58" rx="7" fill="#fff0dd" stroke="#e6a000" stroke-width="2"/>
      <text x="107" y="542" class="small-text" font-weight="700">Variability Patterns</text>

      <rect x="1010" y="270" width="150" height="58" rx="7" fill="#efe0ff" stroke="#8f5bd6" stroke-width="2"/>
      <text x="1050" y="304" class="small-text" font-weight="700" fill="#4b2a75">Case Model</text>

      <rect x="1016" y="400" width="150" height="58" rx="7" fill="#efe0ff" stroke="#8f5bd6" stroke-width="2"/>
      <text x="1053" y="434" class="small-text" font-weight="700" fill="#4b2a75">Case Feedback</text>

      <rect x="485" y="70" width="150" height="58" rx="7" fill="#eef6ff" stroke="#5d95d6" stroke-width="2" stroke-dasharray="9 6"/>
      <text x="501" y="96" class="small-text" fill="#254a7b" font-weight="700">Language Reference</text>
      <text x="528" y="114" class="small-text" fill="#254a7b" font-weight="700">Manual</text>

      <rect x="655" y="70" width="175" height="58" rx="7" fill="#eef6ff" stroke="#5d95d6" stroke-width="2" stroke-dasharray="9 6"/>
      <text x="674" y="96" class="small-text" fill="#254a7b" font-weight="700">Language Definition</text>
      <text x="681" y="114" class="small-text" fill="#254a7b" font-weight="700">(grammar, metamodels)</text>

      <!-- Agents -->
      <rect x="560" y="190" width="185" height="66" fill="#2f75b5" stroke="#1d4f7d" stroke-width="2.5" filter="url(#shadow)"/>
      <text x="620" y="218" class="agent-text">Agent 1</text>
      <text x="595" y="238" class="agent-text">Language Advisor</text>

      <rect x="315" y="350" width="210" height="70" fill="#1f8a70" stroke="#176350" stroke-width="2.5" filter="url(#shadow)"/>
      <text x="390" y="380" class="agent-text">Agent 2</text>
      <text x="365" y="402" class="agent-text">Domain Advisor</text>

      <rect x="750" y="350" width="210" height="70" fill="#6d3fa3" stroke="#4f2b78" stroke-width="2.5" filter="url(#shadow)"/>
      <text x="825" y="380" class="agent-text">Agent 3</text>
      <text x="805" y="402" class="agent-text">Model Inspector</text>

      <rect x="560" y="465" width="185" height="70" fill="#c47a00" stroke="#915b00" stroke-width="2.5" filter="url(#shadow)"/>
      <text x="625" y="495" class="agent-text" fill="#111827">Agent 4</text>
      <text x="595" y="516" class="agent-text" fill="#111827">Variability Explorer</text>

      <!-- Baseline arrows -->
      <path d="M251 361 L315 361" stroke="#2f7d32" stroke-width="2.4" fill="none" marker-end="url(#arrowBase)"/>
      <path d="M1010 299 L960 364" stroke="#243447" stroke-width="2.2" fill="none" marker-end="url(#arrowBase)"/>
      <path d="M1016 429 L960 394" stroke="#243447" stroke-width="2.2" fill="none" marker-end="url(#arrowBase)"/>
      <path d="M652 128 L652 190" stroke="#243447" stroke-width="2.2" fill="none" marker-end="url(#arrowBase)"/>
      <path d="M525 385 L750 385" stroke="#243447" stroke-width="2.2" fill="none" marker-end="url(#arrowBase)"/>
      <path d="M750 402 L525 402" stroke="#243447" stroke-width="2.2" fill="none" marker-end="url(#arrowBase)"/>
      <path d="M525 395 C570 438, 585 448, 604 465" stroke="#243447" stroke-width="2.2" fill="none" marker-end="url(#arrowBase)"/>
      <path d="M750 385 C705 430, 695 445, 670 465" stroke="#243447" stroke-width="2.2" fill="none" marker-end="url(#arrowBase)"/>
      <path d="M560 500 L252 537" stroke="#243447" stroke-width="2.2" fill="none" marker-end="url(#arrowBase)"/>
      <text x="603" y="340" class="tiny" fill="#243447">Questions / Answers / Reference Guidelines</text>
      <text x="455" y="452" class="tiny" fill="#243447">Identified Variability</text>
      <text x="768" y="444" class="tiny" fill="#243447">Observed Variability</text>

      <!-- Overlay zone -->
      <rect x="285" y="570" width="700" height="145" rx="10" fill="#fff5f7" stroke="#d6336c" stroke-width="2.5" stroke-dasharray="10 7"/>
      <text x="305" y="596" fill="#b4235a" font-size="18" font-weight="800">Reusable Human Judgment Overlay</text>

      <rect x="315" y="618" width="125" height="58" rx="8" fill="#ffe3ec" stroke="#d6336c" stroke-width="2"/>
      <text x="346" y="642" fill="#8a1741" font-size="14" font-weight="800">M1</text>
      <text x="328" y="662" fill="#8a1741" font-size="12" font-weight="700">Review Queue</text>

      <rect x="462" y="618" width="135" height="58" rx="8" fill="#ffe3ec" stroke="#d6336c" stroke-width="2"/>
      <text x="515" y="642" fill="#8a1741" font-size="14" font-weight="800">M2</text>
      <text x="480" y="662" fill="#8a1741" font-size="12" font-weight="700">Feedback Manager</text>

      <rect x="620" y="618" width="135" height="58" rx="8" fill="#ffe3ec" stroke="#d6336c" stroke-width="2"/>
      <text x="674" y="642" fill="#8a1741" font-size="14" font-weight="800">M3</text>
      <text x="638" y="662" fill="#8a1741" font-size="12" font-weight="700">Judgment Memory</text>

      <rect x="778" y="618" width="125" height="58" rx="8" fill="#ffe3ec" stroke="#d6336c" stroke-width="2"/>
      <text x="828" y="642" fill="#8a1741" font-size="14" font-weight="800">M4A</text>
      <text x="792" y="662" fill="#8a1741" font-size="12" font-weight="700">Memory Advice</text>

      <rect x="925" y="618" width="135" height="58" rx="8" fill="#e3fafc" stroke="#0b7285" stroke-width="2"/>
      <text x="978" y="642" fill="#07575f" font-size="14" font-weight="800">M4B-1</text>
      <text x="938" y="662" fill="#07575f" font-size="12" font-weight="700">Parallel Compare</text>

      <rect x="1078" y="618" width="130" height="58" rx="8" fill="#e6fcf5" stroke="#0f766e" stroke-width="2"/>
      <text x="1128" y="642" fill="#0b5f56" font-size="14" font-weight="800">EXP-005</text>
      <text x="1091" y="662" fill="#0b5f56" font-size="12" font-weight="700">Real Label Gate</text>

      <!-- Overlay arrows -->
      <path d="M650 535 C640 585, 420 575, 378 618" stroke="#d6336c" stroke-width="3.2" fill="none" marker-end="url(#arrowOverlay)"/>
      <path d="M440 647 L462 647" stroke="#d6336c" stroke-width="3.2" fill="none" marker-end="url(#arrowOverlay)"/>
      <path d="M597 647 L620 647" stroke="#d6336c" stroke-width="3.2" fill="none" marker-end="url(#arrowOverlay)"/>
      <path d="M755 647 L778 647" stroke="#d6336c" stroke-width="3.2" fill="none" marker-end="url(#arrowOverlay)"/>
      <path d="M903 647 L925 647" stroke="#0b7285" stroke-width="3.2" fill="none" marker-end="url(#arrowTeal)"/>
      <path d="M1060 647 L1078 647" stroke="#0b7285" stroke-width="3.2" fill="none" marker-end="url(#arrowTeal)"/>

      <path d="M840 618 C820 560, 775 535, 735 510" stroke="#d6336c" stroke-width="3" fill="none" stroke-dasharray="8 6" marker-end="url(#arrowOverlay)"/>
      <text x="765" y="575" fill="#b4235a" font-size="12" font-weight="800">advisory only</text>

      <path d="M745 500 C840 520, 910 560, 990 618" stroke="#0b7285" stroke-width="3" fill="none" marker-end="url(#arrowTeal)"/>
      <text x="872" y="548" fill="#07575f" font-size="12" font-weight="800">original + memory advice</text>

      <path d="M1144 618 C1135 565, 1068 525, 985 497" stroke="#0f766e" stroke-width="3" fill="none" stroke-dasharray="8 6" marker-end="url(#arrowTeal)"/>
      <text x="1010" y="536" fill="#0b5f56" font-size="12" font-weight="800">expert labels evaluate</text>

      <rect x="1020" y="486" width="200" height="74" rx="8" fill="#fff" stroke="#0f766e" stroke-width="2"/>
      <text x="1037" y="512" fill="#0b5f56" font-size="14" font-weight="800">Dashboard / Visualizer / Thesis</text>
      <text x="1037" y="533" fill="#334155" font-size="12">Evidence and reporting layer</text>
      <text x="1037" y="550" fill="#334155" font-size="12">No baseline overwrite</text>

      <path d="M1060 654 C1100 640, 1130 600, 1120 560" stroke="#0f766e" stroke-width="2.8" fill="none" marker-end="url(#arrowTeal)"/>

      <rect x="68" y="628" width="190" height="68" rx="8" fill="#fff" stroke="#d6336c" stroke-width="2"/>
      <text x="88" y="653" fill="#b4235a" font-size="14" font-weight="800">Human / Supervisor</text>
      <text x="88" y="674" fill="#334155" font-size="12">Reviews blind EXP-005 rows</text>
      <path d="M258 662 L315 650" stroke="#d6336c" stroke-width="3" fill="none" marker-end="url(#arrowOverlay)"/>
    </svg>

    <div class="legend">
      <div><span class="swatch" style="background:#243447"></span>Original VEGO-AI data/control flow</div>
      <div><span class="swatch" style="background:#d6336c"></span>Reusable human judgment flow</div>
      <div><span class="swatch" style="background:#0b7285"></span>Parallel comparison/evaluation flow</div>
      <div><span class="swatch" style="background:#0f766e"></span>Expert-label and reporting gate</div>
    </div>
  </section>

  <section class="sheet">
    <h2>How To Read The Overlay</h2>
    <table>
      <tr><th>Overlay Part</th><th>Where It Sits On The Original Architecture</th><th>Meaning</th></tr>
      <tr><td>M1 Review Queue</td><td>After Agent 4 identifies variability patterns</td><td>Selectively triggers human review for cases where judgment matters.</td></tr>
      <tr><td>M2 Feedback Manager</td><td>Between human/supervisor and stored memory</td><td>Turns expert decisions into structured records.</td></tr>
      <tr><td>M3 Judgment Memory</td><td>Reusable store below the baseline agents</td><td>Stores reusable judgments with provenance.</td></tr>
      <tr><td>M4A Memory Advice</td><td>Dashed advisory arrow back toward Agent 4 / comparison</td><td>Retrieves relevant memory as evidence, not as a replacement.</td></tr>
      <tr><td>M4B-1 Parallel Compare</td><td>Receives original Agent 4 output plus memory advice</td><td>Creates a non-destructive comparison artifact.</td></tr>
      <tr><td>EXP-005 Gate</td><td>After comparison, before any accuracy claim</td><td>Requires real, generalization-safe expert labels.</td></tr>
    </table>
    <div class="callout">
      <strong>Research boundary:</strong> the overlay explains the MSc/PhD extension on top of VEGO-AI. It does not imply Agent 4 has been changed. Current accuracy improvement remains unproven until EXP-005 labels are filled.
    </div>
  </section>

  <section class="sheet">
    <h2>Commands</h2>
    <p>Regenerate this overlay report:</p>
    <pre>.\scripts\export-baseline-overlay-report.ps1</pre>
    <p>Open it after generation:</p>
    <pre>.\scripts\export-baseline-overlay-report.ps1 -Open</pre>
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
