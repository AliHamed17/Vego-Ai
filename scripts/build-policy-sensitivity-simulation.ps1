[CmdletBinding()]
param(
    [string]$InputSheet = "reports\generated\exp003\expert_labeling_sheet_full.csv",
    [string]$OutputDir = "reports\generated\policy_sensitivity",
    [string]$ArtifactCopy = "artifacts\POLICY_SENSITIVITY_EXPERIMENT_REPORT.md"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$scriptPath = Join-Path $repoRoot "scripts\policy_sensitivity_simulation.py"
$inputPath = Join-Path $repoRoot $InputSheet
$outputPath = Join-Path $repoRoot $OutputDir
$artifactPath = Join-Path $repoRoot $ArtifactCopy

if (-not (Test-Path -LiteralPath $scriptPath)) {
    throw "Policy sensitivity simulator not found: $scriptPath"
}

if (-not (Test-Path -LiteralPath $inputPath)) {
    throw "Input sheet not found: $inputPath. Run .\scripts\build-exp003-error-analysis.ps1 first."
}

& python $scriptPath --input-sheet $inputPath --output-dir $outputPath --artifact-copy $artifactPath
