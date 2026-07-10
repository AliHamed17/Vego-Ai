# Runs the offline H-layer experiment suite in a fresh staging directory and
# promotes results only after every experiment, manifest, and evidence guard passes.
[CmdletBinding()]
param(
    [string]$PythonExecutable = "python",
    [string]$EvidenceGuardScript = "",
    [string]$ProtectedPathGuardScript = "",
    [ValidateSet("", "exp006", "exp007", "exp008", "exp009", "exp010", "exp012")]
    [string]$TestFailExperiment = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$generatedRoot = Join-Path $repoRoot "reports\generated"
$evidenceGuard = if ($EvidenceGuardScript) {
    (Resolve-Path -LiteralPath $EvidenceGuardScript).Path
} else {
    Join-Path $repoRoot "scripts\check_evidence_consistency.py"
}
$protectedPathGuard = if ($ProtectedPathGuardScript) {
    (Resolve-Path -LiteralPath $ProtectedPathGuardScript).Path
} else {
    Join-Path $repoRoot "scripts\check_hlayer_protected_paths.py"
}
$experimentNames = @("exp006", "exp007", "exp008", "exp009", "exp010", "exp012")
$experimentScripts = @(
    "scripts\exp006_event_replay.py",
    "scripts\exp007_dosage_replay.py",
    "scripts\exp008_trigger_mining.py",
    "scripts\exp009_seeded_conflict.py",
    "scripts\exp010_convergence_sweep.py",
    "scripts\exp012_accuracy_baseline.py"
)
$runId = "hlayer-{0}-{1}" -f (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ"), ([guid]::NewGuid().ToString("N").Substring(0, 10))
$generatedAt = (Get-Date).ToUniversalTime().ToString("o")
New-Item -ItemType Directory -Force $generatedRoot | Out-Null
$stageRoot = Join-Path $generatedRoot (".hlayer-stage-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $stageRoot | Out-Null

$oldOutputRoot = $env:HLAYER_OUTPUT_ROOT
$oldRunId = $env:HLAYER_RUN_ID
$oldGeneratedAt = $env:HLAYER_GENERATED_AT
$oldPythonUtf8 = $env:PYTHONUTF8
$env:HLAYER_OUTPUT_ROOT = $stageRoot
$env:HLAYER_RUN_ID = $runId
$env:HLAYER_GENERATED_AT = $generatedAt
$env:PYTHONUTF8 = "1"

function Invoke-CheckedPython {
    param([Parameter(Mandatory)][string[]]$Arguments, [Parameter(Mandatory)][string]$Label)
    Write-Host "[hlayer-exp] $Label"
    & $PythonExecutable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
}

try {
    Set-Location $repoRoot
    Invoke-CheckedPython -Arguments @($protectedPathGuard) -Label "checking protected-path hashes before execution"
    foreach ($script in $experimentScripts) {
        Invoke-CheckedPython -Arguments @($script) -Label "running $script"
        $completedExperiment = [System.IO.Path]::GetFileNameWithoutExtension($script) -replace '^exp(\d{3}).*$', 'exp$1'
        if ($TestFailExperiment -and $completedExperiment -eq $TestFailExperiment) {
            throw "Injected test-only failure after $completedExperiment"
        }
    }

    Invoke-CheckedPython -Arguments @(
        "scripts\hlayer_harness.py", "snapshot-gate", "--output", (Join-Path $stageRoot "exp005-gate.json")
    ) -Label "snapshotting validated EXP-005 gate"

    $combinedPath = Join-Path $stageRoot "hlayer_experiments_summary.md"
    $gateSnapshot = Get-Content -Raw -LiteralPath (Join-Path $stageRoot "exp005-gate.json") | ConvertFrom-Json
    $safeLabels = [int]$gateSnapshot.counts.generalization_safe_valid_label_count
    $parts = [System.Collections.Generic.List[string]]::new()
    $parts.Add("# H-Layer Offline Experiment Suite - Combined Summary")
    $parts.Add("")
    $parts.Add("Run ID: ``$runId``")
    $parts.Add("Generated: $generatedAt")
    $parts.Add("")
    $parts.Add("Claim scope: offline mechanism/design evidence only. No accuracy, generalization, or clinical-performance claim.")
    $parts.Add("EXP-005 validated generalization-safe label count: $safeLabels.")
    $parts.Add("")
    foreach ($experiment in $experimentNames) {
        $summary = Join-Path $stageRoot "$experiment\summary.md"
        if (-not (Test-Path -LiteralPath $summary -PathType Leaf)) {
            throw "Fresh summary is missing: $summary"
        }
        foreach ($line in Get-Content -LiteralPath $summary -Encoding utf8) { $parts.Add($line) }
        $parts.Add("")
    }
    $parts -join "`n" | Set-Content -LiteralPath $combinedPath -Encoding utf8

    $suiteManifestArgs = @(
        "scripts\hlayer_harness.py", "suite-manifest",
        "--output-root", $stageRoot,
        "--output", (Join-Path $stageRoot "hlayer_suite_manifest.json"),
        "--experiments"
    ) + $experimentNames
    Invoke-CheckedPython -Arguments $suiteManifestArgs -Label "building suite manifest"

    foreach ($experiment in $experimentNames) {
        foreach ($required in @("summary.json", "summary.md", "manifest.json")) {
            $path = Join-Path $stageRoot "$experiment\$required"
            if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
                throw "Fresh staged output is incomplete: $path"
            }
        }
    }

    # This check refreshes ignored evidence-consistency snapshots. Its nonzero
    # exit code is a hard suite failure and prevents any experiment promotion.
    Invoke-CheckedPython -Arguments @($evidenceGuard) -Label "running evidence-consistency guard (refreshes ignored snapshots)"
    Invoke-CheckedPython -Arguments @($protectedPathGuard) -Label "rechecking protected-path hashes before promotion"

    $directories = $experimentNames
    $promoteArgs = @(
        "scripts\hlayer_harness.py", "promote",
        "--stage-root", $stageRoot,
        "--target-root", $generatedRoot,
        "--directories"
    ) + $directories + @(
        "--files", "hlayer_experiments_summary.md", "hlayer_suite_manifest.json", "exp005-gate.json"
    )
    Invoke-CheckedPython -Arguments $promoteArgs -Label "atomically promoting complete suite"

    Write-Host "[hlayer-exp] all experiments completed and promoted: $runId"
    Write-Host "[hlayer-exp] suite manifest: $(Join-Path $generatedRoot 'hlayer_suite_manifest.json')"
    exit 0
}
catch {
    Write-Error "[hlayer-exp] FAILED before promotion: $($_.Exception.Message)"
    exit 1
}
finally {
    if (Test-Path -LiteralPath $stageRoot) {
        Remove-Item -LiteralPath $stageRoot -Recurse -Force
    }
    $env:HLAYER_OUTPUT_ROOT = $oldOutputRoot
    $env:HLAYER_RUN_ID = $oldRunId
    $env:HLAYER_GENERATED_AT = $oldGeneratedAt
    $env:PYTHONUTF8 = $oldPythonUtf8
}
