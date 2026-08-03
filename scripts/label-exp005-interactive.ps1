[CmdletBinding()]
param(
    [string]$InputSheet = "reports\generated\exp005_label_review\exp005_label_review_blind.csv",
    [string]$OutputSheet = "reports\generated\exp005_label_review\exp005_label_review_filled.csv",
    [string]$ReviewerId = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$scriptPath = Join-Path $repoRoot "scripts\exp005_interactive_labeler.py"
$inputPath = Join-Path $repoRoot $InputSheet
$outputPath = Join-Path $repoRoot $OutputSheet

if (-not (Test-Path -LiteralPath $scriptPath)) {
    throw "EXP-005 interactive labeler not found: $scriptPath"
}

if (-not (Test-Path -LiteralPath $inputPath)) {
    throw "EXP-005 blind sheet not found: $inputPath. Run .\scripts\build-exp005-label-review.ps1 first."
}

$argsList = @("--input", $inputPath, "--output", $outputPath)
if ($ReviewerId) {
    $argsList += @("--reviewer-id", $ReviewerId)
}

& python $scriptPath @argsList
