[CmdletBinding()]
param(
    [switch]$Gui,
    [switch]$All,
    [switch]$Health,
    [switch]$Wiki,
    [switch]$SkipGenerate,
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$vegoRoot = Join-Path $repoRoot "VEGO-AI"
$dashboardScript = Join-Path $vegoRoot "analysis\build_results_dashboard.py"
$dashboardOut = Join-Path $vegoRoot "reports\results_dashboard"
$visualizerDir = Join-Path $vegoRoot "vego_visualizer_delivery"
$visualizerScript = Join-Path $visualizerDir "visualize_compliance.py"
$exp005Script = Join-Path $repoRoot "scripts\build-exp005-label-review.ps1"
$e2eScript = Join-Path $repoRoot "scripts\build-e2e-progress-report.ps1"
$e2eHtml = Join-Path $repoRoot "reports\generated\e2e_dashboard\index.html"
$wikiScript = Join-Path $repoRoot "scripts\build-confluence-wiki.ps1"

function Invoke-WorkbenchStep {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    Write-Host "[workbench] $Name"
    & $Action
}

function Open-WorkbenchPath {
    param(
        [string]$Path
    )

    if ($NoOpen) {
        return
    }

    if (Test-Path -LiteralPath $Path) {
        $resolved = Resolve-Path -LiteralPath $Path
        Write-Host "[open] $resolved"
        Start-Process -FilePath $resolved
    }
    else {
        Write-Warning "Not found, skipping open: $Path"
    }
}

function Start-Visualizer {
    if (-not (Test-Path -LiteralPath $visualizerScript)) {
        throw "Visualizer script not found: $visualizerScript"
    }

    Write-Host "[open] VEGO visualizer GUI"
    Start-Process -FilePath "python" -ArgumentList ".\visualize_compliance.py" -WorkingDirectory $visualizerDir
}

if (-not (Test-Path -LiteralPath $vegoRoot)) {
    throw "VEGO-AI root not found: $vegoRoot"
}

if (-not $SkipGenerate) {
    Invoke-WorkbenchStep "Build results dashboard" {
        if (-not (Test-Path -LiteralPath $dashboardScript)) {
            throw "Dashboard generator not found: $dashboardScript"
        }
        & python $dashboardScript --root $vegoRoot --out $dashboardOut
    }

    Invoke-WorkbenchStep "Build EXP-005 label-review package" {
        if (-not (Test-Path -LiteralPath $exp005Script)) {
            throw "EXP-005 wrapper not found: $exp005Script"
        }
        & $exp005Script
    }

    Invoke-WorkbenchStep "Build E2E progress report" {
        if (-not (Test-Path -LiteralPath $e2eScript)) {
            throw "E2E progress report generator not found: $e2eScript"
        }
        & $e2eScript
    }
}

if ($Wiki -or $All) {
    Invoke-WorkbenchStep "Build Confluence wiki outbox and manual sync pack" {
        if (-not (Test-Path -LiteralPath $wikiScript)) {
            throw "Confluence wiki builder not found: $wikiScript"
        }
        & $wikiScript
    }
}

Open-WorkbenchPath (Join-Path $dashboardOut "index.html")
Open-WorkbenchPath $e2eHtml
Open-WorkbenchPath (Join-Path $repoRoot "reports\generated\exp005_label_review\label_these_first.md")
Open-WorkbenchPath (Join-Path $repoRoot "reports\generated\exp005_label_review\exp005_label_review_blind.csv")
Open-WorkbenchPath (Join-Path $repoRoot "reports\generated\exp005_label_review\exp005_adjudication_sheet.csv")
Open-WorkbenchPath (Join-Path $repoRoot "reports\generated\exp005_label_review\evidence_verdict.md")
Open-WorkbenchPath (Join-Path $repoRoot "artifacts\EXP005_LABEL_REVIEW_PACKAGE.md")
Open-WorkbenchPath (Join-Path $repoRoot "artifacts\RESULTS_AND_ACCURACY_FULL_REPORT.md")

if (($Gui -or $All) -and -not $NoOpen) {
    Start-Visualizer
}

if ($Health -or $All) {
    Invoke-WorkbenchStep "Run project health" {
        & (Join-Path $repoRoot "scripts\project-health.ps1")
    }
    Invoke-WorkbenchStep "Run research health" {
        & (Join-Path $repoRoot "scripts\research-health.ps1")
    }
    Invoke-WorkbenchStep "Run dashboard health" {
        & (Join-Path $repoRoot "scripts\dashboard-health.ps1") -RequireOutbox
    }
}

Write-Host ""
Write-Host "VEGO workbench ready."
Write-Host "Core command: .\scripts\open-vego-workbench.ps1"
Write-Host "Open GUI too: .\scripts\open-vego-workbench.ps1 -Gui"
Write-Host "Full check:   .\scripts\open-vego-workbench.ps1 -All"
Write-Host "After labels: .\scripts\open-vego-workbench.ps1 -SkipGenerate"
