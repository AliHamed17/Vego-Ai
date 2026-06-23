[CmdletBinding()]
param(
    [switch]$UpdateReviewState,
    [switch]$NoHtml
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$outputDir = Join-Path $repoRoot "reports\generated\project_review"
$reviewStatePath = Join-Path $repoRoot "docs\agent-memory\review-state.md"
$blindSheet = Join-Path $repoRoot "reports\generated\exp005_label_review\exp005_label_review_blind.csv"
$fullSheet = Join-Path $repoRoot "reports\generated\exp005_label_review\exp005_label_review_full.csv"

$allowedLabels = @(
    "Substantial Variability",
    "Occasional Variability",
    "Undetermined / Needs Review"
)

$requiredFields = @(
    "expert_label",
    "expert_rationale",
    "reviewer_id",
    "review_date",
    "confidence"
)

function Get-GitOutput {
    param([string[]]$Arguments)

    $output = & git -C $repoRoot @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        return @("git $($Arguments -join ' ') failed: $output")
    }
    return @($output)
}

function Read-JsonFile {
    param([string]$RelativePath)

    $path = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        return $null
    }

    try {
        return Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
    }
    catch {
        return [ordered]@{
            read_error = $_.Exception.Message
            path = $RelativePath
        }
    }
}

function Test-FileUnlocked {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return $false
    }

    try {
        $stream = [System.IO.File]::Open($Path, "Open", "ReadWrite", "None")
        $stream.Close()
        return $true
    }
    catch {
        return $false
    }
}

function Get-Exp005LabelState {
    $state = [ordered]@{
        exists = Test-Path -LiteralPath $blindSheet
        unlocked = Test-FileUnlocked -Path $blindSheet
        rows = 0
        labels_supplied_count = 0
        complete_required_rows = 0
        generalization_safe_complete_rows = 0
        invalid_label_rows = @()
        incomplete_label_rows = @()
        read_error = $null
    }

    if (-not $state.exists) {
        return $state
    }

    $safeByKey = @{}
    if (Test-Path -LiteralPath $fullSheet) {
        try {
            Import-Csv -LiteralPath $fullSheet | ForEach-Object {
                $key = "$($_.setting)::$($_.pattern_id)"
                $isSafe = ($_.generalization_safe_candidate -eq "True") -and ($_.evaluation_leakage_status -ne "same_pattern_memory_used")
                $safeByKey[$key] = $isSafe
            }
        }
        catch {
            $state.read_error = "Could not read full EXP-005 sheet: $($_.Exception.Message)"
            return $state
        }
    }

    try {
        $rowNumber = 1
        Import-Csv -LiteralPath $blindSheet | ForEach-Object {
            $rowNumber += 1
            $state.rows += 1
            $label = ($_.expert_label | ForEach-Object { "$_".Trim() })

            if (-not $label) {
                return
            }

            $state.labels_supplied_count += 1

            if ($allowedLabels -notcontains $label) {
                $state.invalid_label_rows += $rowNumber
            }

            $missing = @()
            foreach ($field in $requiredFields) {
                $value = $_.$field
                if (-not "$value".Trim()) {
                    $missing += $field
                }
            }

            if ($missing.Count -gt 0) {
                $state.incomplete_label_rows += [ordered]@{
                    row = $rowNumber
                    missing = $missing
                }
            }
            elseif ($allowedLabels -contains $label) {
                $state.complete_required_rows += 1
                $key = "$($_.setting)::$($_.pattern_id)"
                if ($safeByKey.ContainsKey($key) -and $safeByKey[$key]) {
                    $state.generalization_safe_complete_rows += 1
                }
            }
        }
    }
    catch {
        $state.read_error = "Could not read blind EXP-005 sheet: $($_.Exception.Message)"
    }

    return $state
}

function Get-ForbiddenTrackedArtifacts {
    $tracked = Get-GitOutput @("ls-files")
    $forbidden = New-Object System.Collections.Generic.List[string]
    $allowedTracked = @(
        "artifacts/README.md",
        "reports/generated/README.md",
        "VEGO-AI/analysis/build_results_dashboard.py",
        "VEGO-AI/analysis/evaluate_accuracy_improvement.py"
    )

    foreach ($item in $tracked) {
        $path = "$item".Replace("\", "/")
        if (-not $path.Trim()) {
            continue
        }

        if ($allowedTracked -contains $path) {
            continue
        }

        $isForbidden = $false
        if ($path -match "\.pdf$") { $isForbidden = $true }
        if ($path -match "\.(zip|exe|tar|tar\.gz|tgz|7z|rar)$") { $isForbidden = $true }
        if ($path -match "^reports/generated/") { $isForbidden = $true }
        if ($path -match "^artifacts/" -and $path -ne "artifacts/README.md") { $isForbidden = $true }
        if ($path -match "^VEGO-AI/eval_output/") { $isForbidden = $true }
        if ($path -match "^VEGO-AI/models/") { $isForbidden = $true }
        if ($path -match "^VEGO-AI/analysis/" -and $path -ne "VEGO-AI/analysis/build_results_dashboard.py") { $isForbidden = $true }

        if ($isForbidden) {
            $forbidden.Add($path)
        }
    }

    return @($forbidden)
}

function ConvertTo-ShortJsonValue {
    param(
        [object]$Object,
        [string]$PropertyPath
    )

    if ($null -eq $Object) {
        return $null
    }

    $current = $Object
    foreach ($part in $PropertyPath.Split(".")) {
        if ($null -eq $current) {
            return $null
        }
        $property = $current.PSObject.Properties[$part]
        if ($null -eq $property) {
            return $null
        }
        $current = $property.Value
    }
    return $current
}

New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

$generatedAt = (Get-Date).ToString("o")
$head = (Get-GitOutput @("rev-parse", "--short", "HEAD")) -join "`n"
$branch = (Get-GitOutput @("branch", "--show-current")) -join "`n"
$gitStatus = Get-GitOutput @("status", "-sb", "--short")
$protectedDiff = Get-GitOutput @("diff", "--name-status", "--", "VEGO-AI\eval_output", "VEGO-AI\framework", "VEGO-AI\eval")
$protectedDiff = @($protectedDiff | Where-Object { "$_".Trim() })
$forbiddenTracked = Get-ForbiddenTrackedArtifacts
$labelState = Get-Exp005LabelState

$exp001 = Read-JsonFile "reports/generated/exp001/exp001_summary.json"
$exp002 = Read-JsonFile "reports/generated/exp002/exp002_summary.json"
$exp003 = Read-JsonFile "reports/generated/exp003/accuracy_summary.json"
$exp005 = Read-JsonFile "reports/generated/exp005_label_review/label_validation_summary.json"
$comparison = Read-JsonFile "reports/generated/evaluation_comparison/evaluation_summary.json"

$unsafeReasons = New-Object System.Collections.Generic.List[string]
$blockers = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

if ($protectedDiff.Count -gt 0) {
    $unsafeReasons.Add("Protected VEGO behavior paths have diffs.")
}
if ($forbiddenTracked.Count -gt 0) {
    $unsafeReasons.Add("Forbidden/generated/controlled artifacts are tracked.")
}
if ($labelState.read_error) {
    $blockers.Add($labelState.read_error)
}
if (-not $labelState.exists) {
    $blockers.Add("EXP-005 blind label sheet is missing.")
}
elseif ($labelState.labels_supplied_count -eq 0) {
    $blockers.Add("EXP-005 has 0 supplied real labels.")
}
elseif (-not $labelState.unlocked) {
    $blockers.Add("EXP-005 blind label sheet is locked/open.")
}
elseif ($labelState.invalid_label_rows.Count -gt 0) {
    $blockers.Add("EXP-005 has invalid label values.")
}
elseif ($labelState.incomplete_label_rows.Count -gt 0) {
    $blockers.Add("EXP-005 has incomplete required label rows.")
}
elseif ($labelState.generalization_safe_complete_rows -lt 20) {
    $warnings.Add("EXP-005 has fewer than 20 generalization-safe complete labels; evidence is pilot-only.")
}

if (($gitStatus | Where-Object { "$_".Trim() -and ($_ -notmatch "^## ") }).Count -gt 0) {
    $warnings.Add("Working tree has local changes; review before commit or tag.")
}

$verdict = "green"
if ($unsafeReasons.Count -gt 0) {
    $verdict = "unsafe"
}
elseif ($blockers.Count -gt 0) {
    $verdict = "blocked"
}
elseif ($warnings.Count -gt 0) {
    $verdict = "yellow"
}

$approvedClaims = @(
    "Reusable human judgment architecture is implemented through M1, M2, M3, M4A, and M4B-1.",
    "M4B-1 is a non-destructive parallel comparison and preserves original Agent 4 outputs.",
    "Current evidence supports traceability, explainability, review routing, advisory evidence, dashboard reporting, and mechanism readiness."
)

$blockedClaims = @(
    "Classification accuracy improved.",
    "Human Judgment Memory generalizes across held-out settings.",
    "Synthetic EXP-004 or EXP-005 outputs prove real accuracy gains.",
    "Same-pattern memory rows prove generalization.",
    "M4B-2 or Agent 4 behavior changes are justified."
)

$nextAction = switch ($verdict) {
    "unsafe" { "Stop and resolve protected-path or forbidden-artifact issues before continuing." }
    "blocked" { "Collect real EXP-005 labels, save and close the CSV, then rerun the review and EXP-005 downstream gate." }
    "yellow" { "Continue with docs, QA, or evidence preparation only; do not claim accuracy improvement." }
    default { "Proceed with the approved next evidence step while preserving VEGO behavior boundaries." }
}

$evidenceSnapshot = [ordered]@{
    exp001_comparisons = ConvertTo-ShortJsonValue $exp001 "totals.comparison_count"
    exp001_generalization_safe_expert_labels = ConvertTo-ShortJsonValue $exp001 "totals.generalization_safe_expert_labeled_count"
    exp001_changed_count = ConvertTo-ShortJsonValue $exp001 "totals.changed_count"
    exp002_rows = ConvertTo-ShortJsonValue $exp002 "totals.row_count"
    exp002_generalization_safe_candidates = ConvertTo-ShortJsonValue $exp002 "totals.generalization_safe_candidate_count"
    exp003_row_count = ConvertTo-ShortJsonValue $exp003 "row_count"
    exp003_generalization_safe_labeled_count = ConvertTo-ShortJsonValue $exp003 "generalization_safe_labeled_count"
    exp003_gate = ConvertTo-ShortJsonValue $exp003 "strict_gate.status"
    exp005_rows = $labelState.rows
    exp005_supplied_labels = $labelState.labels_supplied_count
    exp005_complete_required_rows = $labelState.complete_required_rows
    exp005_safe_complete_rows = $labelState.generalization_safe_complete_rows
    exp005_generated_safe_candidates = ConvertTo-ShortJsonValue $exp005 "generalization_safe_candidate_count"
    comparison_rows = ConvertTo-ShortJsonValue $comparison "totals.patterns"
    comparison_memory_informed_differs = ConvertTo-ShortJsonValue $comparison "totals.memory_informed_differs_from_original"
}

$result = [ordered]@{
    generated_at = $generatedAt
    verdict = $verdict
    git = [ordered]@{
        branch = $branch.Trim()
        head = $head.Trim()
        status = @($gitStatus)
        protected_diff = @($protectedDiff)
        forbidden_tracked_artifacts = @($forbiddenTracked)
    }
    exp005_label_state = $labelState
    evidence_snapshot = $evidenceSnapshot
    blockers = @($blockers)
    warnings = @($warnings)
    unsafe_reasons = @($unsafeReasons)
    approved_claims = $approvedClaims
    blocked_claims = $blockedClaims
    next_action = $nextAction
}

$jsonPath = Join-Path $outputDir "latest-review.json"
$mdPath = Join-Path $outputDir "latest-review.md"
$htmlPath = Join-Path $outputDir "review-dashboard.html"
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

$md = @()
$md += "# VEGO-AI Project Review"
$md += ""
$md += "- Generated: $generatedAt"
$md += "- Verdict: $verdict"
$md += "- Branch: $($result.git.branch)"
$md += "- Head: $($result.git.head)"
$md += ""
$md += "## EXP-005 Gate"
$md += ""
$md += "| Measure | Value |"
$md += "| --- | ---: |"
$md += "| Rows | $($labelState.rows) |"
$md += "| Supplied labels | $($labelState.labels_supplied_count) |"
$md += "| Complete required rows | $($labelState.complete_required_rows) |"
$md += "| Generalization-safe complete rows | $($labelState.generalization_safe_complete_rows) |"
$md += "| Sheet unlocked | $($labelState.unlocked) |"
$md += ""
$md += "## Evidence Snapshot"
$md += ""
$md += "| Measure | Value |"
$md += "| --- | --- |"
foreach ($property in $evidenceSnapshot.Keys) {
    $value = $evidenceSnapshot[$property]
    if ($null -eq $value) { $value = "Unknown" }
    $md += "| $property | $value |"
}
$md += ""
$md += "## Blockers"
$md += ""
if ($blockers.Count -eq 0) { $md += "- None" } else { foreach ($item in $blockers) { $md += "- $item" } }
$md += ""
$md += "## Warnings"
$md += ""
if ($warnings.Count -eq 0) { $md += "- None" } else { foreach ($item in $warnings) { $md += "- $item" } }
$md += ""
$md += "## Unsafe Reasons"
$md += ""
if ($unsafeReasons.Count -eq 0) { $md += "- None" } else { foreach ($item in $unsafeReasons) { $md += "- $item" } }
$md += ""
$md += "## Approved Claims"
$md += ""
foreach ($claim in $approvedClaims) { $md += "- $claim" }
$md += ""
$md += "## Blocked Claims"
$md += ""
foreach ($claim in $blockedClaims) { $md += "- $claim" }
$md += ""
$md += "## Next Action"
$md += ""
$md += $nextAction
$md += ""
$md += "## Required Validation Before Evidence Claims"
$md += ""
$md += '```powershell'
$md += 'python -m compileall -q VEGO-AI\framework VEGO-AI\eval VEGO-AI\analysis VEGO-AI\vego_visualizer_delivery scripts'
$md += '.\scripts\project-health.ps1'
$md += '.\scripts\research-health.ps1'
$md += '.\scripts\dashboard-health.ps1 -RequireOutbox'
$md += 'git diff --name-status -- VEGO-AI\eval_output VEGO-AI\framework VEGO-AI\eval'
$md += '```'
$md += ""
$md | Set-Content -LiteralPath $mdPath -Encoding UTF8

if (-not $NoHtml) {
    $encoded = [System.Net.WebUtility]::HtmlEncode(($md -join [Environment]::NewLine))
    $html = @"
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>VEGO-AI Project Review</title>
  <style>
    body { font-family: Segoe UI, Arial, sans-serif; margin: 32px; line-height: 1.45; color: #172033; }
    pre { white-space: pre-wrap; background: #f5f7fb; border: 1px solid #d8deea; padding: 18px; border-radius: 6px; }
  </style>
</head>
<body>
  <pre>$encoded</pre>
</body>
</html>
"@
    $html | Set-Content -LiteralPath $htmlPath -Encoding UTF8
}

if ($UpdateReviewState) {
    $state = @()
    $state += "# Review State"
    $state += ""
    $state += "Fast review state for Codex and Claude. Update this after meaningful review cycles so future prompts can continue from the same evidence and governance state."
    $state += ""
    $state += "## Last Updated"
    $state += ""
    $state += "- $((Get-Date).ToString('yyyy-MM-dd HH:mm zzz')) by Codex review runner."
    $state += ""
    $state += "## Latest Verdict"
    $state += ""
    $state += "- Verdict: ``$verdict``"
    $state += "- Reason: $nextAction"
    $state += "- Review architecture: ``docs/operations/project-review-architecture.md``"
    $state += "- Review runner: ``scripts/run-project-review.ps1``"
    $state += "- Latest generated review output: ``reports/generated/project_review/latest-review.md`` (ignored)"
    $state += ""
    $state += "## Current Blockers"
    $state += ""
    if ($blockers.Count -eq 0 -and $unsafeReasons.Count -eq 0) {
        $state += "- None."
    }
    else {
        foreach ($item in $unsafeReasons) { $state += "- $item" }
        foreach ($item in $blockers) { $state += "- $item" }
    }
    $state += ""
    $state += "## EXP-005 Label State"
    $state += ""
    $state += "- Rows: $($labelState.rows)"
    $state += "- Supplied labels: $($labelState.labels_supplied_count)"
    $state += "- Complete required rows: $($labelState.complete_required_rows)"
    $state += "- Generalization-safe complete rows: $($labelState.generalization_safe_complete_rows)"
    $state += "- Sheet unlocked: $($labelState.unlocked)"
    $state += ""
    $state += "## Approved Claims"
    $state += ""
    foreach ($claim in $approvedClaims) { $state += "- $claim" }
    $state += ""
    $state += "## Blocked Claims"
    $state += ""
    foreach ($claim in $blockedClaims) { $state += "- $claim" }
    $state += ""
    $state += "## Next Action"
    $state += ""
    $state += $nextAction
    $state += ""
    $state += "## Last Validation Command Set"
    $state += ""
    $state += '```powershell'
    $state += 'python -m compileall -q VEGO-AI\framework VEGO-AI\eval VEGO-AI\analysis VEGO-AI\vego_visualizer_delivery scripts'
    $state += '.\scripts\project-health.ps1'
    $state += '.\scripts\research-health.ps1'
    $state += '.\scripts\dashboard-health.ps1 -RequireOutbox'
    $state += 'git diff --name-status -- VEGO-AI\eval_output VEGO-AI\framework VEGO-AI\eval'
    $state += '```'
    $state += ""
    $state | Set-Content -LiteralPath $reviewStatePath -Encoding UTF8
}

Write-Host "Project review verdict: $verdict"
Write-Host "Summary: $mdPath"
Write-Host "JSON: $jsonPath"
if (-not $NoHtml) {
    Write-Host "HTML: $htmlPath"
}
if ($blockers.Count -gt 0) {
    Write-Host "Blockers:"
    foreach ($item in $blockers) {
        Write-Host " - $item"
    }
}
if ($unsafeReasons.Count -gt 0) {
    Write-Host "Unsafe reasons:"
    foreach ($item in $unsafeReasons) {
        Write-Host " - $item"
    }
}
