[CmdletBinding()]
param(
    [switch]$OpenBlockedMaterials,
    [switch]$RefreshWiki,
    [switch]$RunHealth,
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$outputDir = Join-Path $repoRoot "reports\generated\next_step_loop"
$realBlindSheet = Join-Path $repoRoot "reports\generated\exp005_label_review\exp005_label_review_blind.csv"
$realFullSheet = Join-Path $repoRoot "reports\generated\exp005_label_review\exp005_label_review_full.csv"
$exp005Script = Join-Path $repoRoot "scripts\build-exp005-label-review.ps1"
$wikiScript = Join-Path $repoRoot "scripts\build-confluence-wiki.ps1"
$dashboardHealthScript = Join-Path $repoRoot "scripts\dashboard-health.ps1"
$projectHealthScript = Join-Path $repoRoot "scripts\project-health.ps1"
$researchHealthScript = Join-Path $repoRoot "scripts\research-health.ps1"
$projectReviewScript = Join-Path $repoRoot "scripts\run-project-review.ps1"

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

function Get-GitOutput {
    param([string[]]$Arguments)

    $output = & git @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        return @("git $($Arguments -join ' ') failed: $output")
    }
    return @($output)
}

function Get-Exp005LabelState {
    param(
        [string]$BlindSheet,
        [string]$FullSheet
    )

    $state = [ordered]@{
        exists = Test-Path -LiteralPath $BlindSheet
        unlocked = Test-FileUnlocked -Path $BlindSheet
        rows = 0
        labels_supplied_count = 0
        complete_required_rows = 0
        invalid_label_rows = @()
        incomplete_label_rows = @()
        generalization_safe_complete_rows = 0
    }

    if (-not $state.exists) {
        return $state
    }

    $safeByKey = @{}
    if (Test-Path -LiteralPath $FullSheet) {
        Import-Csv -LiteralPath $FullSheet | ForEach-Object {
            $key = "$($_.setting)::$($_.pattern_id)"
            $isSafe = ($_.generalization_safe_candidate -eq "True") -and ($_.evaluation_leakage_status -ne "same_pattern_memory_used")
            $safeByKey[$key] = $isSafe
        }
    }

    $rowNumber = 1
    Import-Csv -LiteralPath $BlindSheet | ForEach-Object {
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

    return $state
}

function Open-IfPresent {
    param([string]$Path)

    if ($NoOpen) {
        return
    }

    if (Test-Path -LiteralPath $Path) {
        $resolved = Resolve-Path -LiteralPath $Path
        Start-Process -FilePath $resolved
    }
}

New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

$startedAt = (Get-Date).ToString("o")
$actions = New-Object System.Collections.Generic.List[string]
$blockers = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

$head = (Get-GitOutput @("rev-parse", "--short", "HEAD")) -join "`n"
$gitStatus = Get-GitOutput @("status", "-sb", "--short")
$protectedDiff = Get-GitOutput @("diff", "--name-status", "--", "VEGO-AI\eval_output", "VEGO-AI\framework", "VEGO-AI\eval")
if (($protectedDiff | Where-Object { "$_".Trim() }).Count -gt 0) {
    $blockers.Add("Protected VEGO behavior paths have diffs; stopping before evidence actions.")
}

$labelState = Get-Exp005LabelState -BlindSheet $realBlindSheet -FullSheet $realFullSheet

if (-not $labelState.exists) {
    $blockers.Add("EXP-005 blind label sheet is missing.")
}
elseif ($labelState.labels_supplied_count -eq 0) {
    $blockers.Add("EXP-005 has 0 supplied real labels.")
}
elseif (-not $labelState.unlocked) {
    $blockers.Add("EXP-005 blind label sheet is locked/open; save and close it before downstream evidence.")
}
elseif ($labelState.invalid_label_rows.Count -gt 0) {
    $blockers.Add("EXP-005 has invalid label values.")
}
elseif ($labelState.incomplete_label_rows.Count -gt 0) {
    $blockers.Add("EXP-005 has incomplete required label rows.")
}

if ($blockers.Count -eq 0) {
    if (-not (Test-Path -LiteralPath $exp005Script)) {
        throw "EXP-005 wrapper not found: $exp005Script"
    }
    & $exp005Script -FilledLabelsSheet "reports\generated\exp005_label_review\exp005_label_review_blind.csv" -RunDownstream
    $actions.Add("Ran EXP-005 downstream evidence workflow using saved real labels.")
}
else {
    $actions.Add("Stopped before downstream evidence because the EXP-005 gate is blocked.")
    if (Test-Path -LiteralPath $projectReviewScript) {
        & $projectReviewScript -NoHtml
        $actions.Add("Ran the project review cycle and wrote reports/generated/project_review/latest-review.md.")
    }
    else {
        $warnings.Add("Project review script not found; skipped structured review cycle.")
    }
    if ($OpenBlockedMaterials -and -not $NoOpen) {
        Open-IfPresent (Join-Path $repoRoot "reports\generated\exp005_label_review\label_these_first.md")
        Open-IfPresent $realBlindSheet
        Open-IfPresent (Join-Path $repoRoot "docs\research\m4b1-synthetic-policy-candidate-review.md")
        Open-IfPresent (Join-Path $repoRoot "artifacts\topology-export\VEGO_BASELINE_OVERLAY_REPORT.pdf")
        $actions.Add("Opened EXP-005 labeling materials for manual review.")
    }
}

if ($RefreshWiki) {
    & $wikiScript
    & $dashboardHealthScript -RequireOutbox
    $actions.Add("Refreshed Confluence wiki outbox and verified dashboard health.")
}

if ($RunHealth) {
    & $projectHealthScript
    & $researchHealthScript
    & $dashboardHealthScript -RequireOutbox
    $actions.Add("Ran project, research, and dashboard health checks.")
}

$status = if ($blockers.Count -eq 0) { "advanced" } else { "blocked" }

$result = [ordered]@{
    generated_at = (Get-Date).ToString("o")
    started_at = $startedAt
    status = $status
    git_head = $head.Trim()
    git_status = @($gitStatus)
    protected_diff = @($protectedDiff | Where-Object { "$_".Trim() })
    exp005_label_state = $labelState
    actions = @($actions)
    blockers = @($blockers)
    warnings = @($warnings)
    project_review_summary = "reports/generated/project_review/latest-review.md"
    next_step = if ($status -eq "advanced") {
        "Review EXP-005 evidence verdict and reproducibility manifest; do not implement policy changes without supervisor approval."
    }
    else {
        "Fill real EXP-005 labels, save and close Excel, then rerun this script or the EXP-005 downstream command."
    }
}

$jsonPath = Join-Path $outputDir "last-run.json"
$mdPath = Join-Path $outputDir "last-run.md"
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

$md = @()
$md += "# Codex Next-Step Loop"
$md += ""
$md += "- Generated: $($result.generated_at)"
$md += "- Status: $status"
$md += "- Git head: $($result.git_head)"
$md += ""
$md += "## EXP-005 Gate"
$md += ""
$md += "- Rows: $($labelState.rows)"
$md += "- Supplied labels: $($labelState.labels_supplied_count)"
$md += "- Complete required rows: $($labelState.complete_required_rows)"
$md += "- Generalization-safe complete rows: $($labelState.generalization_safe_complete_rows)"
$md += "- Sheet unlocked: $($labelState.unlocked)"
$md += ""
$md += "## Actions"
$md += ""
foreach ($action in $actions) {
    $md += "- $action"
}
$md += ""
$md += "## Project Review"
$md += ""
$md += "- Summary: $($result.project_review_summary)"
$md += ""
$md += "## Blockers"
$md += ""
if ($blockers.Count -eq 0) {
    $md += "- None"
}
else {
    foreach ($blocker in $blockers) {
        $md += "- $blocker"
    }
}
$md += ""
$md += "## Next Step"
$md += ""
$md += $result.next_step
$md += ""

$md | Set-Content -LiteralPath $mdPath -Encoding UTF8

Write-Host "Codex next-step loop status: $status"
Write-Host "Summary: $mdPath"
Write-Host "JSON: $jsonPath"
if ($blockers.Count -gt 0) {
    Write-Host "Blockers:"
    foreach ($blocker in $blockers) {
        Write-Host " - $blocker"
    }
}
