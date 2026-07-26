# Controlled-data verification. Evidence artifacts remain local and ignored.
[CmdletBinding()]
param(
    [switch]$Check,
    [switch]$Refresh
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
    Write-Host "[verify-controlled] $Name"
    & $Body
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

Invoke-Gate "controlled environment doctor" {
    uv run python scripts/vego_doctor.py --require-controlled
}
Invoke-Gate "official baseline byte and semantic locks" {
    uv run python scripts/build_hardening_manifests.py --check --require-controlled
}
Invoke-Gate "legacy/unified controlled parity" {
    uv run python scripts/verify_hlayer_controlled_parity.py
}
Invoke-Gate "BigUI controlled-corpus architecture checks" {
    uv run python scripts/run_bigui_architecture_experiments.py --check --controlled
}
Invoke-Gate "paper baseline controlled hash check" {
    $paperPdf = Get-ChildItem -LiteralPath $repoRoot -File -Filter "Variability_MAS4MODELS2026*.pdf" |
        Select-Object -First 1
    if ($null -eq $paperPdf) {
        throw "The controlled MAS4MODELS paper PDF is missing."
    }
    uv run python scripts/run_bigui_comparison_experiments.py --check --paper-pdf $paperPdf.FullName
}
$guardMode = if ($Refresh) { "--refresh" } else { "--check" }
Invoke-Gate "EXP-005, EXP-012, baseline, and claim evidence guard" {
    uv run python scripts/check_evidence_consistency.py $guardMode
}
Invoke-Gate "offline contract validator" {
    uv run python scripts/validate_hlayer_offline.py
}
Invoke-Gate "program manifest and evidence gates" {
    uv run python scripts/validate_hlayer_program.py
}
if ($Refresh) {
    Invoke-Gate "EXP-013-018 conformance refresh" {
        uv run python scripts/run_hlayer_conformance_suite.py
    }
} else {
    Invoke-Gate "EXP-013-018 conformance replay in temporary storage" {
        $temporary = Join-Path ([System.IO.Path]::GetTempPath()) (
            "vego-hlayer-conformance-" + [guid]::NewGuid().ToString("N")
        )
        try {
            uv run python scripts/run_hlayer_conformance_suite.py --output $temporary
        }
        finally {
            if (Test-Path -LiteralPath $temporary) {
                $resolved = (Resolve-Path -LiteralPath $temporary).Path
                if ($resolved.StartsWith([System.IO.Path]::GetTempPath())) {
                    Remove-Item -LiteralPath $temporary -Recurse -Force
                }
            }
        }
    }
}
Write-Host "VERIFY-CONTROLLED: PASS"
