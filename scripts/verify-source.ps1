# Clone-safe verification for source, contracts, security, tests, and browsers.
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
$env:PYTHONUTF8 = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"

function Invoke-Gate {
    param([string]$Name, [scriptblock]$Body)
    Write-Host "[verify-source] $Name"
    & $Body
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

Invoke-Gate "locked dependency definition" { uv lock --check }
Invoke-Gate "legacy requirement projection freshness" {
    uv run python scripts/check_dependency_lock.py --check
}
Invoke-Gate "environment doctor" { uv run python scripts/vego_doctor.py }
Invoke-Gate "canonical manifest freshness" {
    uv run python scripts/build_hardening_manifests.py --check
}
Invoke-Gate "research record schemas" {
    uv run python scripts/validate_research_records.py schemas/examples
}
Invoke-Gate "H-layer change authorization" {
    uv run python scripts/check_hlayer_change_authorization.py
}
Invoke-Gate "strict quality and security ratchet" {
    uv run python scripts/check_quality_ratchet.py
}
Invoke-Gate "tracked and historical secret, privacy, and binary audit" {
    uv run python scripts/security_audit.py --history
}
Invoke-Gate "VEGO-AI tests" {
    uv run python -m pytest VEGO-AI/tests -q -p no:cacheprovider
}
Invoke-Gate "research infrastructure tests" {
    uv run python -m pytest scripts/tests -q -p no:cacheprovider
}
Invoke-Gate "offline H-layer tests" {
    uv run python -m pytest tests/hlayer_offline -q -p no:cacheprovider
}
Invoke-Gate "evidence guard (read-only)" {
    uv run python scripts/check_evidence_consistency.py --check
}
Invoke-Gate "thesis and visualization freshness" {
    uv run python scripts/build_thesis_evidence_package.py --check
    if ($LASTEXITCODE -ne 0) { throw "thesis evidence package is stale" }
    uv run python scripts/build_thesis_progress_visual.py --check
    if ($LASTEXITCODE -ne 0) { throw "thesis progress visual is stale" }
    uv run python scripts/build_thesis_review_manifest.py --check
    if ($LASTEXITCODE -ne 0) { throw "thesis review manifest is stale" }
    uv run python visualizations-gallery/build_gallery.py --check
}
if (-not $SkipNetworkAudit) {
    Invoke-Gate "Python dependency vulnerability audit" {
        $auditFile = Join-Path ([System.IO.Path]::GetTempPath()) "vego-ai-pip-audit.txt"
        uv export --frozen --all-groups --no-hashes --quiet --output-file $auditFile
        if ($LASTEXITCODE -ne 0) { throw "uv export failed" }
        uv run pip-audit -r $auditFile --progress-spinner off
        $code = $LASTEXITCODE
        Remove-Item -LiteralPath $auditFile -ErrorAction SilentlyContinue
        if ($code -ne 0) { throw "pip-audit found a vulnerability" }
    }
    Invoke-Gate "Node dependency vulnerability audit" {
        npm audit --audit-level=high
    }
}
if (-not $SkipBrowser) {
    Invoke-Gate "offline supervisor and thesis browser checks" {
        node scripts/tests/supervisor_package_browser_smoke.mjs
        if ($LASTEXITCODE -ne 0) { throw "supervisor browser smoke failed" }
        node scripts/tests/thesis_progress_browser_smoke.mjs
    }
}
Invoke-Gate "Git whitespace hygiene" { git diff --check }
Write-Host "VERIFY-SOURCE: PASS"
