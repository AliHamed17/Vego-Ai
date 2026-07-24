# Run one hardened H-layer reliability iteration and snapshot it atomically.
[CmdletBinding()]
param(
    [int]$IterationNumber = 0,
    [switch]$ReplaceLegacy,
    [switch]$ReplaceExistingHardened,
    [string]$PythonExecutable = "python",
    [string]$IterationKind = "reliability_only",
    [string]$Hypothesis = "Atomic execution, provenance manifests, and corrected metric semantics improve evidence reliability without changing baseline behavior.",
    [string]$ExpectedEffect = "No mechanism-performance improvement is expected from harness hardening.",
    [string]$ExpectedVerdict = "NEUTRAL",
    [string]$Verdict = "NEUTRAL",
    [string]$KeepRevert = "KEEP reliability hardening if all guards pass; no runtime behavior was touched."
)

$ErrorActionPreference = "Stop"
foreach ($metadata in ([ordered]@{
    IterationKind = $IterationKind
    Hypothesis = $Hypothesis
    ExpectedEffect = $ExpectedEffect
    ExpectedVerdict = $ExpectedVerdict
    Verdict = $Verdict
    KeepRevert = $KeepRevert
}).GetEnumerator()) {
    if ([string]::IsNullOrWhiteSpace([string]$metadata.Value)) {
        throw "Iteration metadata parameter $($metadata.Key) cannot be blank."
    }
}
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$iterationRoot = Join-Path $repoRoot "reports\generated\hlayer_iterations"
$generatedRoot = Join-Path $repoRoot "reports\generated"
New-Item -ItemType Directory -Force $iterationRoot | Out-Null
$iterationRootResolved = (Resolve-Path -LiteralPath $iterationRoot).Path.TrimEnd('\')

function Assert-UnderIterationRoot {
    param([Parameter(Mandatory)][string]$Path)
    $resolved = [System.IO.Path]::GetFullPath($Path).TrimEnd('\')
    $prefix = $iterationRootResolved + [System.IO.Path]::DirectorySeparatorChar
    if (-not $resolved.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Iteration path escapes reports/generated/hlayer_iterations: $resolved"
    }
    return $resolved
}

$existing = @(Get-ChildItem -LiteralPath $iterationRoot -Directory | Where-Object { $_.Name -match '^iter_(\d{3})$' } | Sort-Object Name)
if ($IterationNumber -le 0) {
    $IterationNumber = if ($existing) { [int]($existing[-1].Name.Substring(5)) + 1 } else { 1 }
}
$targetName = "iter_{0:d3}" -f $IterationNumber
$targetDir = Assert-UnderIterationRoot (Join-Path $iterationRoot $targetName)
$targetExists = Test-Path -LiteralPath $targetDir -PathType Container
$targetIsHardened = $targetExists -and (Test-Path -LiteralPath (Join-Path $targetDir "iteration_manifest.json"))
if ($targetIsHardened -and -not $ReplaceExistingHardened) {
    throw "Hardened iteration already exists and will not be overwritten: $targetDir"
}
if ($targetExists -and -not $targetIsHardened -and -not $ReplaceLegacy) {
    throw "Legacy iteration exists at $targetDir. Use -ReplaceLegacy to quarantine it after all checks pass."
}

$previous = @($existing | Where-Object { [int]($_.Name.Substring(5)) -lt $IterationNumber } | Sort-Object Name | Select-Object -Last 1)
$previousDir = if ($previous) { $previous[0].FullName } else { $null }
$protectedPaths = @("VEGO-AI\eval_output", "VEGO-AI\framework", "VEGO-AI\eval", "VEGO-AI\tests", "VEGO-AI\schemas")
Set-Location $repoRoot
$protectedBefore = (git status --porcelain=v1 -- @protectedPaths) -join "`n"

Write-Host "[iter] running hardened offline suite for iteration $IterationNumber"
& (Join-Path $PSScriptRoot "build-hlayer-experiments.ps1") -PythonExecutable $PythonExecutable
if ($LASTEXITCODE -ne 0) {
    throw "H-layer suite failed; no iteration snapshot was changed"
}

$stageDir = Assert-UnderIterationRoot (Join-Path $iterationRoot (".iter-stage-" + [guid]::NewGuid().ToString("N")))
New-Item -ItemType Directory -Path $stageDir | Out-Null
$quarantineDir = $null
try {
    foreach ($experiment in @("exp006", "exp007", "exp008", "exp009", "exp010", "exp012")) {
        foreach ($file in @("summary.json", "manifest.json")) {
            $source = Join-Path $generatedRoot "$experiment\$file"
            if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
                throw "Fresh suite output missing: $source"
            }
            Copy-Item -LiteralPath $source -Destination (Join-Path $stageDir "$experiment-$file")
        }
    }
    foreach ($file in @("hlayer_experiments_summary.md", "hlayer_suite_manifest.json", "exp005-gate.json")) {
        $source = Join-Path $generatedRoot $file
        if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Fresh suite file missing: $source" }
        $destinationName = if ($file -eq "hlayer_experiments_summary.md") { "combined-summary.md" } else { $file }
        Copy-Item -LiteralPath $source -Destination (Join-Path $stageDir $destinationName)
    }

    if ($previousDir) {
        & $PythonExecutable (Join-Path $PSScriptRoot "hlayer_iteration_compare.py") $previousDir $stageDir
        if ($LASTEXITCODE -ne 0) { throw "Iteration comparison failed" }
    } else {
        @("# H-Layer Iteration Comparison", "", "No earlier iteration exists.") -join "`n" |
            Set-Content -LiteralPath (Join-Path $stageDir "iteration_report.md") -Encoding utf8
    }

    $suiteManifest = Get-Content -Raw -LiteralPath (Join-Path $stageDir "hlayer_suite_manifest.json") | ConvertFrom-Json
    $fileHashes = [ordered]@{}
    foreach ($file in Get-ChildItem -LiteralPath $stageDir -File | Sort-Object Name) {
        if ($file.Name -ne "iteration_manifest.json" -and $file.Name -notmatch 'manifest\.json$') {
            $fileHashes[$file.Name] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    }
    $componentNormalized = [ordered]@{ suite = $suiteManifest.normalized_sha256 }
    foreach ($experiment in @("exp006", "exp007", "exp008", "exp009", "exp010", "exp012")) {
        $componentManifest = Get-Content -Raw -LiteralPath (Join-Path $stageDir "$experiment-manifest.json") | ConvertFrom-Json
        $componentNormalized[$experiment] = $componentManifest.normalized_sha256
    }
    $iterationManifest = [ordered]@{
        schema_version = "1.0"
        iteration = $IterationNumber
        run_id = $suiteManifest.run_id
        generated_at = (Get-Date).ToUniversalTime().ToString("o")
        iteration_kind = $IterationKind
        hypothesis = $Hypothesis
        expected_effect = $ExpectedEffect
        expected_verdict = $ExpectedVerdict
        verdict = $Verdict
        keep_revert = $KeepRevert
        previous_iteration = if ($previousDir) { Split-Path -Leaf $previousDir } else { $null }
        claim_scope = "Offline mechanism/design evidence only; no accuracy, generalization, or clinical-performance claim."
        decision_snapshot = $suiteManifest.decision_snapshot
        exp005_gate = $suiteManifest.exp005_gate
        component_normalized_sha256 = $componentNormalized
        outputs_sha256 = $fileHashes
    }
    $iterationManifestPath = Join-Path $stageDir "iteration_manifest.json"
    $iterationManifest | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $iterationManifestPath -Encoding utf8
    & $PythonExecutable (Join-Path $PSScriptRoot "hlayer_harness.py") normalize-manifest --input $iterationManifestPath
    if ($LASTEXITCODE -ne 0) { throw "Could not add normalized iteration-manifest digest" }

    $protectedAfter = (git status --porcelain=v1 -- @protectedPaths) -join "`n"
    if ($protectedAfter -ne $protectedBefore) {
        throw "Protected-path state changed during the offline iteration"
    }

    if ($targetExists) {
        $stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
        $quarantineReason = if ($targetIsHardened) { "superseded_hardened_snapshot" } else { "legacy_pre_hardening" }
        $quarantineName = "quarantine_${targetName}_${quarantineReason}_$stamp"
        $quarantineDir = Assert-UnderIterationRoot (Join-Path $iterationRoot $quarantineName)
        if (Test-Path -LiteralPath $quarantineDir) { throw "Quarantine destination already exists: $quarantineDir" }
        Move-Item -LiteralPath $targetDir -Destination $quarantineDir
        Write-Host "[iter] prior snapshot quarantined: $quarantineDir"
    }
    try {
        Move-Item -LiteralPath $stageDir -Destination $targetDir
    }
    catch {
        if ($quarantineDir -and (Test-Path -LiteralPath $quarantineDir) -and -not (Test-Path -LiteralPath $targetDir)) {
            Move-Item -LiteralPath $quarantineDir -Destination $targetDir
        }
        throw
    }
    Write-Host "[iter] iteration $IterationNumber complete: $targetDir"
    Write-Host "[iter] verdict: $Verdict ($IterationKind)"
    exit 0
}
finally {
    if (Test-Path -LiteralPath $stageDir) { Remove-Item -LiteralPath $stageDir -Recurse -Force }
}
