# One-command full program evaluation: verification gate -> experiment benchmark ->
# component contribution verdicts -> program overview (+charts) -> LLM analyst ->
# one consolidated verdict. Read-only over protected paths; writes only generated
# analysis outputs. Exit 0 only when every evidence-bearing stage passes.
#
#   .\scripts\run-full-evaluation.ps1              # everything
#   .\scripts\run-full-evaluation.ps1 -SkipSlow    # skip the two pytest suites inside the gate
[CmdletBinding()]
param(
    [switch]$SkipSlow
)

$ErrorActionPreference = "Continue"
$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot
$env:PYTHONUTF8 = "1"

$logDir = Join-Path $repoRoot (Join-Path "reports" (Join-Path "generated" (Join-Path "full_evaluation" (Get-Date -Format "yyyyMMddTHHmmss"))))
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$results = [System.Collections.Generic.List[object]]::new()
function Invoke-Stage {
    param([string]$Name, [scriptblock]$Body, [string]$Kind = "evidence")
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $log = Join-Path $logDir (($Name -replace "[^A-Za-z0-9._-]", "-") + ".log")
    # $LASTEXITCODE is only set by native commands / explicit `exit`; reset it so a
    # stage that throws before running anything cannot inherit the previous PASS.
    $global:LASTEXITCODE = $null
    $threw = $false
    try {
        & $Body *> $log
    } catch {
        $_ | Out-String | Add-Content -Path $log
        $threw = $true
    }
    $code = $LASTEXITCODE
    $sw.Stop()
    $results.Add([pscustomobject]@{
        Stage   = $Name
        Kind    = $Kind
        Result  = if (-not $threw -and $code -eq 0) { "PASS" } else { "FAIL" }
        Seconds = [math]::Round($sw.Elapsed.TotalSeconds, 1)
    })
}

# 1. Full verification gate (16 checks incl. tests, guards, health)
if ($SkipSlow) {
    Invoke-Stage "verification gate (verify-hlayer-all -SkipSlow)" { & .\scripts\verify-hlayer-all.ps1 -SkipSlow }
} else {
    Invoke-Stage "verification gate (verify-hlayer-all)" { & .\scripts\verify-hlayer-all.ps1 }
}

# 2. Experiment benchmark (per-experiment metrics, sources, evidence classes)
Invoke-Stage "experiment benchmark" { python scripts\build_experiment_benchmark.py --refresh }

# 3. Component contribution verdicts (per-agent answers with citations)
Invoke-Stage "component contribution report" { python scripts\build_agent_contribution_report.py }

# 4. Unified program overview + trajectory charts (JSON/MD/CSV/HTML)
Invoke-Stage "program overview + charts" { python scripts\build_hlayer_program_overview.py }

# 5. LLM analyst (advisory narrative; deterministic fallback without a key)
Invoke-Stage "program analyst (advisory)" { python scripts\hlayer_llm_analyst.py } "advisory"

Write-Host ""
Write-Host "Full program evaluation" -ForegroundColor Cyan
$results | Format-Table -AutoSize | Out-String | Write-Host
Write-Host "Per-stage logs: $logDir"

Write-Host "Read the answers here:" -ForegroundColor Cyan
Write-Host "  components & verdicts : reports\generated\agent_contribution\agent_contribution.md"
Write-Host "  experiment benchmark  : docs\research\bigui\EXPERIMENT_BENCHMARK_ANALYTICS_REPORT.md"
Write-Host "  program overview      : reports\generated\hlayer_program_overview\program_overview.md (+ .html charts)"
Write-Host "  analyst narrative     : reports\generated\llm_analyst\analysis.md (ADVISORY)"
Write-Host "  Iris coverage matrix  : docs\research\iris-july1-implementation-matrix.md"

$failedEvidence = @($results | Where-Object { $_.Result -ne "PASS" -and $_.Kind -eq "evidence" })
$failedAdvisory = @($results | Where-Object { $_.Result -ne "PASS" -and $_.Kind -eq "advisory" })
if ($failedAdvisory.Count -gt 0) {
    Write-Host "ADVISORY stage failed (does not gate): $(($failedAdvisory | ForEach-Object Stage) -join '; ')" -ForegroundColor Yellow
}
if ($failedEvidence.Count -gt 0) {
    Write-Host ("FAILED: " + (($failedEvidence | ForEach-Object Stage) -join "; ")) -ForegroundColor Red
    exit 1
}
Write-Host "FULL EVALUATION PASSED" -ForegroundColor Green
exit 0
