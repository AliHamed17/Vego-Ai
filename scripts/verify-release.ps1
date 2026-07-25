# Final clean-tree publication gate.
[CmdletBinding()]
param(
    [switch]$Check,
    [switch]$Refresh,
    [switch]$SkipBrowser,
    [switch]$SkipNetworkAudit
)

$ErrorActionPreference = "Stop"
if ($Check -and $Refresh) {
    throw "Use either -Check or -Refresh, not both."
}
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

if ($Refresh) {
    & "$PSScriptRoot\verify-controlled.ps1" -Refresh
} else {
    & "$PSScriptRoot\verify-controlled.ps1" -Check
}
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& "$PSScriptRoot\verify-source.ps1" -Check `
    -SkipBrowser:$SkipBrowser -SkipNetworkAudit:$SkipNetworkAudit
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

uv run python scripts/build_hardening_manifests.py --check --require-controlled
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$status = @(git status --porcelain=v1)
if ($LASTEXITCODE -ne 0) {
    throw "Unable to inspect the Git worktree."
}
if ($status.Count -gt 0) {
    $status | ForEach-Object { Write-Host $_ }
    throw "Release verification requires a clean tracked worktree."
}
Write-Host "VERIFY-RELEASE: PASS"
