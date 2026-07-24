# One-command verification gate for the entire H-layer program.
# Runs every check that defines "all green", prints a single PASS/FAIL table,
# and exits nonzero if anything fails. Read-only except for the ignored
# generated outputs the checks themselves refresh.
#
#   .\scripts\verify-hlayer-all.ps1               # full gauntlet
#   .\scripts\verify-hlayer-all.ps1 -SkipSlow     # skip the two pytest suites
#   .\scripts\verify-hlayer-all.ps1 -WithOverview # also rebuild the program overview
[CmdletBinding()]
param(
    [switch]$SkipSlow,
    [switch]$WithOverview,
    [string]$LogRoot = "reports\generated\verification"
)

$ErrorActionPreference = "Continue"
$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot
$env:PYTHONUTF8 = "1"
$runStamp = Get-Date -Format "yyyyMMddTHHmmss"
$runLogDir = Join-Path $LogRoot $runStamp
New-Item -ItemType Directory -Force -Path $runLogDir | Out-Null

$results = [System.Collections.Generic.List[object]]::new()

function Invoke-Check {
    param(
        [string]$Name,
        [scriptblock]$Body,
        [switch]$RefreshesIgnoredOutputs
    )
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $safeName = ($Name -replace '[^A-Za-z0-9._-]+', '-').Trim('-').ToLowerInvariant()
    $logPath = Join-Path $runLogDir "$safeName.log"
    $code = 0
    $output = @()
    try {
        $global:LASTEXITCODE = 0
        $output = @(& $Body 2>&1)
        if ($LASTEXITCODE -ne 0) {
            $code = $LASTEXITCODE
        }
    }
    catch {
        $code = 1
        $output += $_ | Out-String
    }
    $output | Out-File -LiteralPath $logPath -Encoding utf8
    $sw.Stop()
    $results.Add([pscustomobject]@{
        Check        = $Name
        Result       = if ($code -eq 0) { "PASS" } else { "FAIL" }
        OutputEffect = if ($RefreshesIgnoredOutputs) { "refreshes ignored outputs" } else { "read-only" }
        Seconds      = [math]::Round($sw.Elapsed.TotalSeconds, 1)
        Log          = $logPath
    })
    if ($code -ne 0) {
        Write-Host ""
        Write-Host "Failure detail: $Name" -ForegroundColor Red
        $output | Select-Object -Last 80 | ForEach-Object { Write-Host $_ }
        Write-Host "Full log: $logPath" -ForegroundColor DarkYellow
    }
}

Invoke-Check "protected paths (VEGO-AI hash guard)" { python scripts\check_hlayer_protected_paths.py }
Invoke-Check "git: VEGO-AI unmodified" {
    $protected = @(
        "VEGO-AI/framework",
        "VEGO-AI/schemas",
        "VEGO-AI/tests",
        "VEGO-AI/eval",
        "VEGO-AI/inputs"
    )
    $diff = @(git status --porcelain -- $protected)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to inspect protected paths."
    }
    if ($diff.Count -gt 0) {
        $diff
        throw "Protected VEGO-AI paths have working-tree changes."
    }
}
Invoke-Check "evidence consistency" { python scripts\check_evidence_consistency.py } -RefreshesIgnoredOutputs
Invoke-Check "offline package validator" { python scripts\validate_hlayer_offline.py }
Invoke-Check "program validator (manifests, gates, boundary)" { python scripts\validate_hlayer_program.py }
Invoke-Check "conformance suite (EXP-013..018)" { python scripts\run_hlayer_conformance_suite.py } -RefreshesIgnoredOutputs
if (-not $SkipSlow) {
    Invoke-Check "pytest VEGO-AI/tests" { python -m pytest VEGO-AI\tests -q }
    Invoke-Check "pytest scripts/tests" { python -m pytest scripts\tests -q }
}
if ($WithOverview) {
    Invoke-Check "program overview rebuild" { python scripts\build_hlayer_program_overview.py } -RefreshesIgnoredOutputs
}
Invoke-Check "supervisor package schema and content" { python scripts\validate_supervisor_package.py }
Invoke-Check "visualization catalog freshness" { python visualizations-gallery\build_gallery.py --check }
Invoke-Check "repository privacy and secret scan" { python scripts\check_repository_privacy.py }
Invoke-Check "project health" { .\scripts\project-health.ps1 }
Invoke-Check "research health" { .\scripts\research-health.ps1 }
Invoke-Check "dashboard health with outbox" { .\scripts\dashboard-health.ps1 -RequireOutbox }
Invoke-Check "Git whitespace and EOF hygiene" { git diff --check }

Write-Host ""
Write-Host "H-layer verification gate" -ForegroundColor Cyan
$results | Format-Table -AutoSize | Out-String | Write-Host
Write-Host "Saved diagnostic logs: $runLogDir" -ForegroundColor DarkCyan

$failed = @($results | Where-Object { $_.Result -ne "PASS" })
if ($failed.Count -gt 0) {
    Write-Host ("FAILED: " + (($failed | ForEach-Object { $_.Check }) -join "; ")) -ForegroundColor Red
    exit 1
}
Write-Host "ALL CHECKS PASSED" -ForegroundColor Green
exit 0
