[CmdletBinding()]
param(
    [string]$Exp002Sheet = "reports\generated\exp002\expert_labeling_sheet.csv",
    [string]$OutputDir = "reports\generated\exp003"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$scriptPath = Join-Path $repoRoot "VEGO-AI\analysis\evaluate_accuracy_improvement.py"
$sheetPath = Join-Path $repoRoot $Exp002Sheet
$outputPath = Join-Path $repoRoot $OutputDir

if (-not (Test-Path -LiteralPath $scriptPath)) {
    throw "EXP-003 evaluator not found: $scriptPath"
}

if (-not (Test-Path -LiteralPath $sheetPath)) {
    throw "EXP-002 labeling sheet not found: $sheetPath. Run .\scripts\build-exp002-labeling-package.ps1 first."
}

& python $scriptPath --exp002-sheet $sheetPath --output-dir $outputPath
