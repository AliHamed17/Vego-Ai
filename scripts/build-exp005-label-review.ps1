[CmdletBinding()]
param(
    [string]$SourceSheet = "reports\generated\exp003\expert_labeling_sheet_full.csv",
    [string]$FilledLabelsSheet = "",
    [string]$OutputDir = "reports\generated\exp005_label_review",
    [string]$ArtifactCopy = "artifacts\EXP005_LABEL_REVIEW_PACKAGE.md",
    [switch]$RunDownstream
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$scriptPath = Join-Path $repoRoot "scripts\exp005_label_review.py"
$sourcePath = Join-Path $repoRoot $SourceSheet
$outputPath = Join-Path $repoRoot $OutputDir
$artifactPath = Join-Path $repoRoot $ArtifactCopy

if (-not (Test-Path -LiteralPath $scriptPath)) {
    throw "EXP-005 helper not found: $scriptPath"
}

if (-not (Test-Path -LiteralPath $sourcePath)) {
    throw "EXP-005 source sheet not found: $sourcePath. Run .\scripts\build-exp003-error-analysis.ps1 first."
}

$argsList = @(
    "--source-sheet", $sourcePath,
    "--output-dir", $outputPath,
    "--artifact-copy", $artifactPath
)

$filledPath = $null
if ($FilledLabelsSheet) {
    $filledPath = Join-Path $repoRoot $FilledLabelsSheet
    if (-not (Test-Path -LiteralPath $filledPath)) {
        throw "Filled EXP-005 label sheet not found: $filledPath"
    }
    $argsList += @("--filled-label-sheet", $filledPath)
}

& python $scriptPath @argsList

if ($RunDownstream) {
    if (-not $filledPath) {
        Write-Warning "RunDownstream was requested without FilledLabelsSheet; EXP-003/EXP-004 downstream rerun skipped."
    }
    else {
        $exp003Script = Join-Path $repoRoot "VEGO-AI\analysis\evaluate_accuracy_improvement.py"
        $policyScript = Join-Path $repoRoot "scripts\policy_sensitivity_simulation.py"
        $exp003Output = Join-Path $outputPath "exp003_filled"
        $policyOutput = Join-Path $outputPath "policy_sensitivity"
        $policyArtifact = Join-Path $repoRoot "artifacts\EXP005_POLICY_SENSITIVITY_REPORT.md"

        if (-not (Test-Path -LiteralPath $exp003Script)) {
            throw "EXP-003 evaluator not found: $exp003Script"
        }
        if (-not (Test-Path -LiteralPath $policyScript)) {
            throw "EXP-004 policy-sensitivity helper not found: $policyScript"
        }

        $mergedFullSheet = Join-Path $outputPath "exp005_label_review_full.csv"
        if (-not (Test-Path -LiteralPath $mergedFullSheet)) {
            throw "Merged EXP-005 full sheet not found: $mergedFullSheet"
        }

        & python $exp003Script --exp002-sheet $mergedFullSheet --output-dir $exp003Output
        $filledFullSheet = Join-Path $exp003Output "expert_labeling_sheet_full.csv"
        & python $policyScript --input-sheet $filledFullSheet --output-dir $policyOutput --artifact-copy $policyArtifact
    }
}
