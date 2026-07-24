[CmdletBinding()]
param(
    [string]$MarkdownOutputPath = "docs\dashboards\e2e-dashboard.generated.md",
    [string]$HtmlOutputPath = "reports\generated\e2e_dashboard\index.html"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$markdownFullPath = Join-Path $repoRoot $MarkdownOutputPath
$htmlFullPath = Join-Path $repoRoot $HtmlOutputPath
$generated = Get-Date -Format "yyyy-MM-dd HH:mm zzz"
$fence = '```'

function Read-RepoText {
    param([Parameter(Mandatory = $true)][string]$RelativePath)

    $path = Join-Path $repoRoot $RelativePath
    if (Test-Path -LiteralPath $path) {
        return (Get-Content -Raw -LiteralPath $path)
    }
    return ""
}

function Read-RepoJson {
    param([Parameter(Mandatory = $true)][string]$RelativePath)

    $path = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        return $null
    }

    try {
        return (Get-Content -Raw -LiteralPath $path | ConvertFrom-Json)
    }
    catch {
        return $null
    }
}

function Get-JsonValue {
    param(
        $Object,
        [Parameter(Mandatory = $true)][string[]]$Path,
        $Default = $null
    )

    $current = $Object
    foreach ($segment in $Path) {
        if ($null -eq $current) {
            return $Default
        }
        $property = $current.PSObject.Properties[$segment]
        if (-not $property) {
            return $Default
        }
        $current = $property.Value
    }

    if ($null -eq $current) {
        return $Default
    }
    return $current
}

function ConvertTo-ValueArray {
    param($Value)

    if ($null -eq $Value) {
        return @()
    }
    if ($Value -is [System.Array]) {
        return @($Value)
    }
    return @($Value)
}

function Split-MarkdownTableLine {
    param([Parameter(Mandatory = $true)][string]$Line)

    $trimmed = $Line.Trim()
    if ($trimmed.StartsWith("|")) {
        $trimmed = $trimmed.Substring(1)
    }
    if ($trimmed.EndsWith("|")) {
        $trimmed = $trimmed.Substring(0, $trimmed.Length - 1)
    }
    return @($trimmed -split "\|" | ForEach-Object { $_.Trim() })
}

function Get-MarkdownSection {
    param(
        [Parameter(Mandatory = $true)][string]$Markdown,
        [Parameter(Mandatory = $true)][string]$Heading
    )

    $pattern = "(?ms)^##\s+$([regex]::Escape($Heading))\s*(.+?)(?=^##\s+|\z)"
    $match = [regex]::Match($Markdown, $pattern)
    if ($match.Success) {
        return $match.Groups[1].Value
    }
    return ""
}

function Get-MarkdownTableRows {
    param(
        [Parameter(Mandatory = $true)][string]$Markdown,
        [Parameter(Mandatory = $true)][string]$HeaderName
    )

    $rows = @()
    $headers = $null
    $capturing = $false

    foreach ($line in ($Markdown -split "`r?`n")) {
        if ($line -notmatch '^\s*\|') {
            if ($capturing -and $rows.Count -gt 0) {
                break
            }
            continue
        }

        if (-not $headers) {
            if ($line -match [regex]::Escape($HeaderName)) {
                $headers = Split-MarkdownTableLine -Line $line
                $capturing = $true
            }
            continue
        }

        if ($line -match '^\s*\|\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$') {
            continue
        }

        $columns = Split-MarkdownTableLine -Line $line
        if ($columns.Count -lt $headers.Count) {
            continue
        }

        $object = [ordered]@{}
        for ($i = 0; $i -lt $headers.Count; $i++) {
            $object[$headers[$i]] = $columns[$i]
        }
        $rows += [pscustomobject]$object
    }

    return @($rows)
}

function Get-Cell {
    param(
        [Parameter(Mandatory = $true)]$Row,
        [Parameter(Mandatory = $true)][string]$ColumnName
    )

    $property = $Row.PSObject.Properties[$ColumnName]
    if ($property) {
        return [string]$property.Value
    }
    return ""
}

function ConvertTo-StatusBucket {
    param([string]$Status)

    $statusText = ""
    if ($null -ne $Status) {
        $statusText = $Status.Trim()
    }
    if ($statusText -match '^(Green|Done|Passed|Available|Active rule|Supported)\b') { return "Done/Green" }
    if ($statusText -match '^(Yellow|Open|In progress|In review|Next)\b') { return "In progress/Yellow" }
    if ($statusText -match '^(Red|At risk|Not claimed)\b') { return "Risk/Red" }
    if ($statusText -match '^(Blocked|Deferred)\b') { return "Blocked" }
    if ($statusText -match '^(Planned)\b') { return "Planned" }
    return "Other"
}

function New-StatusCounts {
    return [ordered]@{
        "Done/Green" = 0
        "In progress/Yellow" = 0
        "Risk/Red" = 0
        "Blocked" = 0
        "Planned" = 0
        "Other" = 0
    }
}

function Get-StatusCounts {
    param(
        [Parameter(Mandatory = $true)]$Rows,
        [Parameter(Mandatory = $true)][string]$StatusColumn
    )

    $counts = New-StatusCounts
    foreach ($row in $Rows) {
        $bucket = ConvertTo-StatusBucket -Status (Get-Cell -Row $row -ColumnName $StatusColumn)
        $counts[$bucket] += 1
    }
    return $counts
}

function Get-CountTotal {
    param([Parameter(Mandatory = $true)]$Counts)

    $total = 0
    foreach ($key in $Counts.Keys) {
        $total += [int]$Counts[$key]
    }
    return $total
}

function Get-Percent {
    param(
        [int]$Part,
        [int]$Total
    )

    if ($Total -le 0) {
        return 0
    }
    return [int][Math]::Round(($Part / $Total) * 100)
}

function New-AsciiBar {
    param(
        [int]$Percent,
        [int]$Width = 20
    )

    $bounded = [Math]::Max(0, [Math]::Min(100, $Percent))
    $filled = [int][Math]::Round(($bounded / 100) * $Width)
    return "[" + ("#" * $filled) + ("-" * ($Width - $filled)) + "] $bounded%"
}

function ConvertTo-HtmlText {
    param([string]$Text)

    $value = ""
    if ($null -ne $Text) {
        $value = [string]$Text
    }
    return [System.Net.WebUtility]::HtmlEncode($value)
}

function New-HtmlBar {
    param(
        [string]$Label,
        [int]$Value,
        [int]$Total,
        [string]$ClassName
    )

    $percent = Get-Percent -Part $Value -Total $Total
    $safeLabel = ConvertTo-HtmlText $Label
    return "<div class=""bar-row""><span>$safeLabel</span><div class=""bar-track""><div class=""bar-fill $ClassName"" style=""width:$percent%""></div></div><strong>$Value</strong></div>"
}

function New-HtmlBadge {
    param(
        [string]$Text,
        [string]$ClassName
    )

    $safeText = ConvertTo-HtmlText $Text
    return "<span class=""badge $ClassName"">$safeText</span>"
}

function ConvertTo-DataAttr {
    param([string]$Text)

    $value = ""
    if ($null -ne $Text) {
        $value = [string]$Text
    }
    return [System.Net.WebUtility]::HtmlEncode($value.ToLowerInvariant())
}

function ConvertTo-StatusClass {
    param([string]$Status)

    $bucket = ConvertTo-StatusBucket -Status $Status
    if ($bucket -eq "Done/Green") { return "ok" }
    if ($bucket -eq "Blocked" -or $bucket -eq "Risk/Red") { return "risk" }
    if ($bucket -eq "Planned") { return "info" }
    return "warn"
}

function Get-GitSummary {
    $summary = [ordered]@{
        Branch = "unknown"
        Head = "unknown"
        PendingCount = 0
        PendingPreview = @()
    }

    $branch = & git -C $repoRoot rev-parse --abbrev-ref HEAD 2>$null
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($branch)) {
        $summary.Branch = $branch.Trim()
    }

    $head = & git -C $repoRoot rev-parse --short HEAD 2>$null
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($head)) {
        $summary.Head = $head.Trim()
    }

    $status = @(& git -C $repoRoot status --short 2>$null)
    if ($LASTEXITCODE -eq 0) {
        $summary.PendingCount = $status.Count
        $summary.PendingPreview = @($status | Select-Object -First 12)
    }

    return [pscustomobject]$summary
}

$progressMarkdown = Read-RepoText "docs/agent-memory/progress.md"
$currentStateMarkdown = Read-RepoText "docs/agent-memory/current-state.md"
$kpiMarkdown = Read-RepoText "docs/dashboards/kpi-register.md"
$progressDashboardMarkdown = Read-RepoText "docs/dashboards/progress-dashboard.md"
$resultsDashboardMarkdown = Read-RepoText "docs/dashboards/results-dashboard.md"
$issuesMarkdown = Read-RepoText "docs/agent-memory/issues.md"

$milestoneRows = Get-MarkdownTableRows -Markdown (Get-MarkdownSection -Markdown $progressMarkdown -Heading "Milestones") -HeaderName "Date"
$activeRows = Get-MarkdownTableRows -Markdown (Get-MarkdownSection -Markdown $progressMarkdown -Heading "Active Work") -HeaderName "ID"
$completedRows = Get-MarkdownTableRows -Markdown (Get-MarkdownSection -Markdown $progressMarkdown -Heading "Completed Work") -HeaderName "Date"
$kpiRows = Get-MarkdownTableRows -Markdown (Get-MarkdownSection -Markdown $kpiMarkdown -Heading "KPI Snapshot") -HeaderName "KPI"
$executiveRows = Get-MarkdownTableRows -Markdown (Get-MarkdownSection -Markdown $progressDashboardMarkdown -Heading "Executive Snapshot") -HeaderName "Area"
$issueRows = Get-MarkdownTableRows -Markdown (Get-MarkdownSection -Markdown $issuesMarkdown -Heading "Open") -HeaderName "ID"

$milestoneCounts = Get-StatusCounts -Rows $milestoneRows -StatusColumn "Status"
$activeCounts = Get-StatusCounts -Rows $activeRows -StatusColumn "Status"
$kpiCounts = Get-StatusCounts -Rows $kpiRows -StatusColumn "Status"
$executiveCounts = Get-StatusCounts -Rows $executiveRows -StatusColumn "Status"

$milestoneTotal = Get-CountTotal -Counts $milestoneCounts
$activeTotal = Get-CountTotal -Counts $activeCounts
$kpiTotal = Get-CountTotal -Counts $kpiCounts
$executiveTotal = Get-CountTotal -Counts $executiveCounts

$milestoneDonePercent = Get-Percent -Part $milestoneCounts["Done/Green"] -Total $milestoneTotal
$activeDonePercent = Get-Percent -Part $activeCounts["Done/Green"] -Total $activeTotal
$kpiGreenPercent = Get-Percent -Part $kpiCounts["Done/Green"] -Total $kpiTotal
$executiveGreenPercent = Get-Percent -Part $executiveCounts["Done/Green"] -Total $executiveTotal
$kpiRiskCount = [int]$kpiCounts["Risk/Red"] + [int]$kpiCounts["Blocked"]

$exp001 = Read-RepoJson "reports/generated/exp001/exp001_summary.json"
$exp002 = Read-RepoJson "reports/generated/exp002/exp002_summary.json"
$exp003 = Read-RepoJson "reports/generated/exp003/accuracy_summary.json"
$exp005 = Read-RepoJson "reports/generated/exp005_label_review/label_validation_summary.json"
$projectReview = Read-RepoJson "reports/generated/project_review/latest-review.json"
$metricsSnapshot = Read-RepoJson "VEGO-AI/reports/results_dashboard/metrics_snapshot.json"

$git = Get-GitSummary
$reviewVerdict = [string](Get-JsonValue -Object $projectReview -Path @("verdict") -Default "not generated")
$reviewNextAction = [string](Get-JsonValue -Object $projectReview -Path @("next_action") -Default "Run .\scripts\run-project-review.ps1 -UpdateReviewState.")
$reviewBlockers = ConvertTo-ValueArray (Get-JsonValue -Object $projectReview -Path @("blockers") -Default @())
$approvedClaims = ConvertTo-ValueArray (Get-JsonValue -Object $projectReview -Path @("approved_claims") -Default @())
$blockedClaims = ConvertTo-ValueArray (Get-JsonValue -Object $projectReview -Path @("blocked_claims") -Default @())

$exp001Comparisons = [int](Get-JsonValue -Object $exp001 -Path @("totals", "comparison_count") -Default 0)
$exp001Changed = [int](Get-JsonValue -Object $exp001 -Path @("totals", "changed_count") -Default 0)
$exp001SafeLabels = [int](Get-JsonValue -Object $exp001 -Path @("totals", "generalization_safe_expert_labeled_count") -Default 0)
$exp002Rows = [int](Get-JsonValue -Object $exp002 -Path @("totals", "row_count") -Default 0)
$exp002SafeCandidates = [int](Get-JsonValue -Object $exp002 -Path @("totals", "generalization_safe_candidate_count") -Default 0)
$exp003Rows = [int](Get-JsonValue -Object $exp003 -Path @("row_count") -Default 0)
$exp003SafeLabeled = [int](Get-JsonValue -Object $exp003 -Path @("generalization_safe_labeled_count") -Default 0)
$exp003Gate = [string](Get-JsonValue -Object $exp003 -Path @("strict_gate", "status") -Default "Unavailable")
$exp005Rows = [int](Get-JsonValue -Object $exp005 -Path @("row_count") -Default 0)
$exp005SafeCandidates = [int](Get-JsonValue -Object $exp005 -Path @("generalization_safe_candidate_count") -Default 0)
$exp005Labels = [int](Get-JsonValue -Object $exp005 -Path @("labels_supplied_count") -Default 0)
$exp005SafeValid = [int](Get-JsonValue -Object $exp005 -Path @("generalization_safe_valid_label_count") -Default 0)
$exp005Gate = [string](Get-JsonValue -Object $exp005 -Path @("strict_gate", "status") -Default "Unavailable")
$accuracyClaimAllowed = [bool](Get-JsonValue -Object $exp005 -Path @("strict_gate", "accuracy_improvement_claim_allowed") -Default $false)

$settingsCount = [int](Get-JsonValue -Object $metricsSnapshot -Path @("overview", "settings_count") -Default 0)
$caseCount = [int](Get-JsonValue -Object $metricsSnapshot -Path @("overview", "case_count") -Default 0)
$patternCount = [int](Get-JsonValue -Object $metricsSnapshot -Path @("overview", "variability_pattern_count") -Default 0)
$reviewQueueCount = [int](Get-JsonValue -Object $metricsSnapshot -Path @("overview", "human_review_queue_count") -Default 0)
$memoryCount = [int](Get-JsonValue -Object $metricsSnapshot -Path @("overview", "judgment_memory_count") -Default 0)
$adviceCount = [int](Get-JsonValue -Object $metricsSnapshot -Path @("overview", "memory_advice_count") -Default 0)
$baselineChanges = [int](Get-JsonValue -Object $metricsSnapshot -Path @("overview", "ai_classification_changed_count") -Default 0)

$openActiveRows = @($activeRows | Where-Object {
    (ConvertTo-StatusBucket -Status (Get-Cell -Row $_ -ColumnName "Status")) -ne "Done/Green"
} | Select-Object -First 12)
$openIssueRows = @($issueRows | Select-Object -First 8)
$recentCompletedRows = @($completedRows | Select-Object -Last 8)
$allProgressDates = @(
    $milestoneRows | ForEach-Object { Get-Cell -Row $_ -ColumnName "Date" }
    $activeRows | ForEach-Object { Get-Cell -Row $_ -ColumnName "Started" }
    $completedRows | ForEach-Object { Get-Cell -Row $_ -ColumnName "Date" }
) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique

$dateOptionsHtml = ($allProgressDates | ForEach-Object {
    $safeDate = ConvertTo-HtmlText $_
    "<option value=""$safeDate"">$safeDate</option>"
}) -join "`n"

$claimBadge = if ($accuracyClaimAllowed) {
    New-HtmlBadge -Text "accuracy claim allowed" -ClassName "ok"
}
else {
    New-HtmlBadge -Text "accuracy claim blocked" -ClassName "risk"
}

$reviewBadgeClass = if ($reviewVerdict -match "pass|ready|green") { "ok" } elseif ($reviewVerdict -match "blocked|red") { "risk" } else { "warn" }
$reviewBadge = New-HtmlBadge -Text $reviewVerdict -ClassName $reviewBadgeClass
$gitBadge = if ($git.PendingCount -eq 0) { New-HtmlBadge -Text "clean" -ClassName "ok" } else { New-HtmlBadge -Text "$($git.PendingCount) pending changes" -ClassName "warn" }

$markdownLines = New-Object System.Collections.Generic.List[string]
$markdownLines.Add("# VEGO-AI E2E Progress Report")
$markdownLines.Add("")
$markdownLines.Add("Generated: $generated.")
$markdownLines.Add("")
$markdownLines.Add('This generated report connects repo memory, curated dashboards, generated experiment summaries, Confluence outbox status, and the 4-hour update loop. Regenerate it with `.\scripts\build-e2e-progress-report.ps1`.')
$markdownLines.Add("")
$markdownLines.Add("## Executive Status")
$markdownLines.Add("")
$markdownLines.Add("| Signal | Value | Visual |")
$markdownLines.Add("| --- | --- | --- |")
$markdownLines.Add("| Milestones done/green | $($milestoneCounts["Done/Green"]) of $milestoneTotal | $(New-AsciiBar -Percent $milestoneDonePercent) |")
$markdownLines.Add("| KPIs green | $($kpiCounts["Done/Green"]) of $kpiTotal | $(New-AsciiBar -Percent $kpiGreenPercent) |")
$markdownLines.Add("| Active work done | $($activeCounts["Done/Green"]) of $activeTotal | $(New-AsciiBar -Percent $activeDonePercent) |")
$markdownLines.Add("| Executive dashboard green | $($executiveCounts["Done/Green"]) of $executiveTotal | $(New-AsciiBar -Percent $executiveGreenPercent) |")
$markdownLines.Add("| Review verdict | $reviewVerdict | Next action: $reviewNextAction |")
$markdownLines.Add("| Git workspace | $($git.Branch) @ $($git.Head) | $($git.PendingCount) pending status rows |")
$markdownLines.Add("")
$markdownLines.Add("## E2E Evidence Snapshot")
$markdownLines.Add("")
$markdownLines.Add("| Area | Current Value | Gate |
| --- | --- | --- |
| VEGO runtime snapshot | $settingsCount settings, $caseCount cases, $patternCount variability patterns | Baseline AI classification changes: $baselineChanges |
| Human judgment chain | $reviewQueueCount review queue items, $memoryCount reusable memory entries, $adviceCount advice items | M4A/M4B-1 remain non-destructive |
| EXP-001 | $exp001Comparisons comparisons, $exp001Changed memory-informed classification changes, $exp001SafeLabels safe expert labels | Mechanism/readiness only |
| EXP-002 | $exp002Rows labeling rows, $exp002SafeCandidates safe candidates | Human/supervisor labels pending |
| EXP-003 | $exp003Rows rows, $exp003SafeLabeled safe labeled rows | $exp003Gate |
| EXP-005 | $exp005Rows rows, $exp005SafeCandidates safe candidates, $exp005Labels supplied labels, $exp005SafeValid safe valid labels | $exp005Gate |")
$markdownLines.Add("")
$markdownLines.Add("## Update Architecture")
$markdownLines.Add("")
$markdownLines.Add($fence + "mermaid")
$markdownLines.Add("flowchart LR")
$markdownLines.Add("    Memory[Memory docs] --> Dashboards[Curated dashboards]")
$markdownLines.Add("    Dashboards --> E2E[E2E report and web page]")
$markdownLines.Add("    Dashboards --> Visuals[Progress visualizations]")
$markdownLines.Add("    E2E --> Wiki[Confluence outbox]")
$markdownLines.Add("    Visuals --> Wiki")
$markdownLines.Add("    Wiki --> Health[Dashboard and research health]")
$markdownLines.Add("    Health --> Updates[4-hour Codex thread updates]")
$markdownLines.Add($fence)
$markdownLines.Add("")
$markdownLines.Add("## Current Blockers")
$markdownLines.Add("")
if ($reviewBlockers.Count -eq 0) {
    $markdownLines.Add("- No generated review blockers found.")
}
else {
    foreach ($blocker in $reviewBlockers) {
        $markdownLines.Add("- $blocker")
    }
}
$markdownLines.Add("")
$markdownLines.Add("## Open Active Work")
$markdownLines.Add("")
if ($openActiveRows.Count -eq 0) {
    $markdownLines.Add("_No open active work rows found._")
}
else {
    $markdownLines.Add("| ID | Status | Summary | Next Step |")
    $markdownLines.Add("| --- | --- | --- | --- |")
    foreach ($row in $openActiveRows) {
        $markdownLines.Add("| $(Get-Cell -Row $row -ColumnName "ID") | $(Get-Cell -Row $row -ColumnName "Status") | $(Get-Cell -Row $row -ColumnName "Summary") | $(Get-Cell -Row $row -ColumnName "Next Step") |")
    }
}
$markdownLines.Add("")
$markdownLines.Add("## Open Issues")
$markdownLines.Add("")
if ($openIssueRows.Count -eq 0) {
    $markdownLines.Add("_No open issue rows found._")
}
else {
    $markdownLines.Add("| ID | Severity | Status | Summary | Next Step |")
    $markdownLines.Add("| --- | --- | --- | --- | --- |")
    foreach ($row in $openIssueRows) {
        $markdownLines.Add("| $(Get-Cell -Row $row -ColumnName "ID") | $(Get-Cell -Row $row -ColumnName "Severity") | $(Get-Cell -Row $row -ColumnName "Status") | $(Get-Cell -Row $row -ColumnName "Summary") | $(Get-Cell -Row $row -ColumnName "Next Step") |")
    }
}
$markdownLines.Add("")
$markdownLines.Add("## Approved Claims")
$markdownLines.Add("")
foreach ($claim in $approvedClaims) {
    $markdownLines.Add("- $claim")
}
$markdownLines.Add("")
$markdownLines.Add("## Blocked Claims")
$markdownLines.Add("")
foreach ($claim in $blockedClaims) {
    $markdownLines.Add("- $claim")
}
$markdownLines.Add("")
$markdownLines.Add("## Refresh Commands")
$markdownLines.Add("")
$markdownLines.Add($fence + "powershell")
$markdownLines.Add(".\scripts\build-e2e-progress-report.ps1")
$markdownLines.Add(".\scripts\build-progress-visualizations.ps1")
$markdownLines.Add(".\scripts\build-confluence-wiki.ps1")
$markdownLines.Add(".\scripts\dashboard-health.ps1 -RequireOutbox")
$markdownLines.Add(".\scripts\research-health.ps1")
$markdownLines.Add(".\scripts\project-health.ps1")
$markdownLines.Add($fence)
$markdownLines.Add("")
$markdownLines.Add("## Generated Web Page")
$markdownLines.Add("")
$markdownLines.Add('Open `reports/generated/e2e_dashboard/index.html` for the full local web dashboard.')

New-Item -ItemType Directory -Path (Split-Path -Parent $markdownFullPath) -Force | Out-Null
Set-Content -LiteralPath $markdownFullPath -Value ($markdownLines -join "`r`n") -Encoding UTF8

$kpiBars = @(
    New-HtmlBar -Label "Green" -Value ([int]$kpiCounts["Done/Green"]) -Total $kpiTotal -ClassName "good"
    New-HtmlBar -Label "Yellow / In progress" -Value ([int]$kpiCounts["In progress/Yellow"]) -Total $kpiTotal -ClassName "warn-fill"
    New-HtmlBar -Label "Red / Blocked" -Value $kpiRiskCount -Total $kpiTotal -ClassName "risk-fill"
) -join "`n"

$activeBars = @(
    New-HtmlBar -Label "Done" -Value ([int]$activeCounts["Done/Green"]) -Total $activeTotal -ClassName "good"
    New-HtmlBar -Label "Open / In progress" -Value ([int]$activeCounts["In progress/Yellow"]) -Total $activeTotal -ClassName "warn-fill"
    New-HtmlBar -Label "Blocked" -Value ([int]$activeCounts["Blocked"]) -Total $activeTotal -ClassName "risk-fill"
) -join "`n"

$blockerHtml = if ($reviewBlockers.Count -eq 0) {
    "<li>No generated review blockers found.</li>"
}
else {
    ($reviewBlockers | ForEach-Object { "<li>$(ConvertTo-HtmlText $_)</li>" }) -join "`n"
}

$openActiveHtml = if ($openActiveRows.Count -eq 0) {
    "<tr><td colspan=""4"">No open active work rows found.</td></tr>"
}
else {
    ($openActiveRows | ForEach-Object {
        $id = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "ID")
        $status = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Status")
        $summary = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Summary")
        $next = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Next Step")
        "<tr><td>$id</td><td>$status</td><td>$summary</td><td>$next</td></tr>"
    }) -join "`n"
}

$milestoneRowsHtml = if ($milestoneRows.Count -eq 0) {
    "<tr><td colspan=""4"">No milestone rows found.</td></tr>"
}
else {
    ($milestoneRows | ForEach-Object {
        $date = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Date")
        $title = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Milestone")
        $status = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Status")
        $notes = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Notes")
        $statusClass = ConvertTo-StatusClass (Get-Cell -Row $_ -ColumnName "Status")
        $dataDate = ConvertTo-DataAttr (Get-Cell -Row $_ -ColumnName "Date")
        $dataStatus = ConvertTo-DataAttr (Get-Cell -Row $_ -ColumnName "Status")
        $dataSearch = ConvertTo-DataAttr ("$title $status $notes")
        "<tr class=""change-row"" data-type=""milestone"" data-date=""$dataDate"" data-status=""$dataStatus"" data-search=""$dataSearch""><td>$date</td><td>$title</td><td><span class=""badge $statusClass"">$status</span></td><td>$notes</td></tr>"
    }) -join "`n"
}

$activeRowsHtml = if ($activeRows.Count -eq 0) {
    "<tr><td colspan=""5"">No active work rows found.</td></tr>"
}
else {
    ($activeRows | ForEach-Object {
        $id = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "ID")
        $date = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Started")
        $status = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Status")
        $summary = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Summary")
        $next = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Next Step")
        $statusClass = ConvertTo-StatusClass (Get-Cell -Row $_ -ColumnName "Status")
        $dataDate = ConvertTo-DataAttr (Get-Cell -Row $_ -ColumnName "Started")
        $dataStatus = ConvertTo-DataAttr (Get-Cell -Row $_ -ColumnName "Status")
        $dataSearch = ConvertTo-DataAttr ("$id $status $summary $next")
        "<tr class=""change-row"" data-type=""active"" data-date=""$dataDate"" data-status=""$dataStatus"" data-search=""$dataSearch""><td>$id</td><td>$date</td><td><span class=""badge $statusClass"">$status</span></td><td>$summary</td><td>$next</td></tr>"
    }) -join "`n"
}

$completedRowsHtml = if ($completedRows.Count -eq 0) {
    "<tr><td colspan=""3"">No completed work rows found.</td></tr>"
}
else {
    ($completedRows | ForEach-Object {
        $date = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Date")
        $summary = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Summary")
        $files = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Files")
        $dataDate = ConvertTo-DataAttr (Get-Cell -Row $_ -ColumnName "Date")
        $dataSearch = ConvertTo-DataAttr ("$summary $files")
        "<tr class=""change-row"" data-type=""completed"" data-date=""$dataDate"" data-status=""done"" data-search=""$dataSearch""><td>$date</td><td>$summary</td><td>$files</td></tr>"
    }) -join "`n"
}

$recentCompletedHtml = if ($recentCompletedRows.Count -eq 0) {
    "<li>No completed work rows found.</li>"
}
else {
    ($recentCompletedRows | ForEach-Object {
        $date = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Date")
        $summary = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Summary")
        "<li><strong>$date</strong><span>$summary</span></li>"
    }) -join "`n"
}

$approvedHtml = if ($approvedClaims.Count -eq 0) {
    "<li>No approved claims found in latest project review.</li>"
}
else {
    ($approvedClaims | ForEach-Object { "<li>$(ConvertTo-HtmlText $_)</li>" }) -join "`n"
}

$blockedHtml = if ($blockedClaims.Count -eq 0) {
    "<li>No blocked claims found in latest project review.</li>"
}
else {
    ($blockedClaims | ForEach-Object { "<li>$(ConvertTo-HtmlText $_)</li>" }) -join "`n"
}

$gitPreviewHtml = if ($git.PendingPreview.Count -eq 0) {
    "<li>Working tree status output is clean.</li>"
}
else {
    ($git.PendingPreview | ForEach-Object { "<li><code>$(ConvertTo-HtmlText $_)</code></li>" }) -join "`n"
}

$safeReviewNextAction = ConvertTo-HtmlText $reviewNextAction
$safeExp003Gate = ConvertTo-HtmlText $exp003Gate
$safeExp005Gate = ConvertTo-HtmlText $exp005Gate
$safeGenerated = ConvertTo-HtmlText $generated
$safeBranch = ConvertTo-HtmlText $git.Branch
$safeHead = ConvertTo-HtmlText $git.Head

$html = @"
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>VEGO-AI E2E Progress Report</title>
  <style>
    :root {
      --ink: #152033;
      --muted: #657080;
      --line: #d7dee8;
      --page: #f5f7fa;
      --panel: #ffffff;
      --good: #2f855a;
      --warn: #b7791f;
      --risk: #c53030;
      --blue: #315ea8;
      --teal: #0f766e;
      --soft-good: #e7f4ec;
      --soft-warn: #fff7df;
      --soft-risk: #fff0f0;
      --soft-blue: #edf2ff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", Arial, sans-serif;
      background: var(--page);
      color: var(--ink);
    }
    header, main {
      width: min(1240px, calc(100% - 32px));
      margin: 0 auto;
    }
    header {
      padding: 28px 0 18px;
    }
    h1 {
      margin: 0 0 8px;
      font-size: 34px;
      line-height: 1.1;
      letter-spacing: 0;
    }
    h2 {
      margin: 0 0 14px;
      font-size: 19px;
      line-height: 1.25;
      letter-spacing: 0;
    }
    p, li, td, th {
      line-height: 1.45;
    }
    p, small {
      color: var(--muted);
    }
    .meta {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      padding: 3px 9px;
      border-radius: 8px;
      border: 1px solid var(--line);
      font-size: 13px;
      color: var(--ink);
      background: #fff;
    }
    .badge.ok { background: var(--soft-good); border-color: #b8dfc7; color: #1f5f3f; }
    .badge.warn { background: var(--soft-warn); border-color: #ead08b; color: #7a4c00; }
    .badge.risk { background: var(--soft-risk); border-color: #efb4b4; color: #8a1f1f; }
    .badge.info { background: var(--soft-blue); border-color: #c8d4f5; color: #25477f; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(225px, 1fr));
      gap: 14px;
      margin: 14px 0;
    }
    .card, .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }
    .card strong {
      display: block;
      font-size: 30px;
      line-height: 1;
      margin-bottom: 8px;
    }
    .card span {
      color: var(--muted);
    }
    .panel {
      margin: 14px 0;
    }
    .toolbar {
      display: grid;
      grid-template-columns: minmax(220px, 1.4fr) repeat(3, minmax(150px, 1fr));
      gap: 10px;
      margin: 12px 0 4px;
    }
    .field {
      display: grid;
      gap: 5px;
    }
    .field span {
      color: var(--muted);
      font-size: 12px;
      font-weight: 600;
    }
    input, select {
      width: 100%;
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      color: var(--ink);
      padding: 7px 9px;
      font: inherit;
    }
    .filter-summary {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-top: 10px;
      color: var(--muted);
      font-size: 14px;
    }
    .filter-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    button {
      min-height: 34px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      color: var(--ink);
      padding: 6px 10px;
      font: inherit;
      cursor: pointer;
    }
    button:hover {
      border-color: var(--blue);
    }
    .split {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 14px;
    }
    .bar-row {
      display: grid;
      grid-template-columns: minmax(130px, 180px) 1fr 48px;
      align-items: center;
      gap: 10px;
      margin: 10px 0;
      font-size: 14px;
    }
    .bar-track {
      height: 14px;
      background: #e8edf5;
      border-radius: 7px;
      overflow: hidden;
    }
    .bar-fill {
      height: 100%;
      min-width: 2px;
    }
    .good { background: var(--good); }
    .warn-fill { background: var(--warn); }
    .risk-fill { background: var(--risk); }
    .pipeline {
      display: grid;
      grid-template-columns: repeat(6, minmax(120px, 1fr));
      gap: 8px;
      margin-top: 12px;
    }
    .stage {
      min-height: 92px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 12px;
      position: relative;
    }
    .stage strong {
      display: block;
      margin-bottom: 6px;
    }
    .stage small {
      display: block;
    }
    .stage::after {
      content: "";
      position: absolute;
      top: 44px;
      right: -8px;
      width: 8px;
      height: 2px;
      background: var(--line);
    }
    .stage:last-child::after {
      display: none;
    }
    .gate {
      border-left: 5px solid var(--risk);
      background: #fffafa;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      border: 1px solid var(--line);
      background: #fff;
    }
    th, td {
      border-bottom: 1px solid var(--line);
      padding: 10px;
      text-align: left;
      vertical-align: top;
      font-size: 14px;
    }
    th {
      background: #eef2f7;
      font-weight: 600;
    }
    .table-wrap {
      overflow-x: auto;
    }
    code {
      background: #eef2f7;
      border-radius: 4px;
      padding: 2px 5px;
    }
    .claim-grid {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 14px;
    }
    .timeline {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    .timeline li {
      display: grid;
      grid-template-columns: 96px 1fr;
      gap: 10px;
      padding: 9px 0;
      border-bottom: 1px solid var(--line);
    }
    @media (max-width: 900px) {
      .split, .claim-grid { grid-template-columns: 1fr; }
      .toolbar { grid-template-columns: 1fr 1fr; }
      .pipeline { grid-template-columns: repeat(2, minmax(130px, 1fr)); }
      .stage::after { display: none; }
    }
    @media (max-width: 620px) {
      header, main { width: min(100% - 20px, 1240px); }
      h1 { font-size: 27px; }
      .bar-row { grid-template-columns: 1fr; gap: 5px; }
      .toolbar { grid-template-columns: 1fr; }
      .pipeline { grid-template-columns: 1fr; }
      .timeline li { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <h1>VEGO-AI E2E Progress Report</h1>
    <p>Generated $safeGenerated from project memory, dashboards, experiment summaries, review state, and Git status.</p>
    <div class="meta">
      $reviewBadge
      $claimBadge
      $gitBadge
      <span class="badge">branch $safeBranch</span>
      <span class="badge">head $safeHead</span>
    </div>
  </header>
  <main>
    <section class="grid" aria-label="Progress summary">
      <div class="card"><strong>$milestoneDonePercent%</strong><span>Milestones done or green ($($milestoneCounts["Done/Green"]) of $milestoneTotal)</span></div>
      <div class="card"><strong>$kpiGreenPercent%</strong><span>KPIs green ($($kpiCounts["Done/Green"]) of $kpiTotal)</span></div>
      <div class="card"><strong>$activeDonePercent%</strong><span>Active work done ($($activeCounts["Done/Green"]) of $activeTotal)</span></div>
      <div class="card"><strong>$exp005SafeValid</strong><span>Generalization-safe valid EXP-005 labels</span></div>
    </section>

    <section class="panel gate">
      <h2>Current Gate</h2>
      <p><strong>EXP-005:</strong> $safeExp005Gate</p>
      <p><strong>EXP-003:</strong> $safeExp003Gate</p>
      <p><strong>Next action:</strong> $safeReviewNextAction</p>
      <ul>
        $blockerHtml
      </ul>
    </section>

    <section class="panel">
      <h2>E2E Update Architecture</h2>
      <div class="pipeline" aria-label="Pipeline stages">
        <div class="stage"><strong>Memory</strong><small>current-state.md and progress.md</small></div>
        <div class="stage"><strong>Dashboards</strong><small>progress, KPI, results</small></div>
        <div class="stage"><strong>Generated Views</strong><small>E2E web page and visual charts</small></div>
        <div class="stage"><strong>Wiki Outbox</strong><small>Confluence manual sync pack</small></div>
        <div class="stage"><strong>Health</strong><small>dashboard, research, project checks</small></div>
        <div class="stage"><strong>4-Hour Update</strong><small>Codex thread check-in</small></div>
      </div>
    </section>

    <section class="split">
      <div class="panel">
        <h2>KPI Mix</h2>
        $kpiBars
      </div>
      <div class="panel">
        <h2>Active Work Mix</h2>
        $activeBars
      </div>
    </section>

    <section class="panel" id="progress-dashboards">
      <h2>Progress Dashboards</h2>
      <div class="toolbar" aria-label="Progress filters">
        <label class="field">
          <span>Search changes</span>
          <input id="changeSearch" type="search" placeholder="milestone, task, EXP-005, Confluence">
        </label>
        <label class="field">
          <span>Date</span>
          <select id="dateFilter">
            <option value="">All dates</option>
            $dateOptionsHtml
          </select>
        </label>
        <label class="field">
          <span>Status</span>
          <select id="statusFilter">
            <option value="">All statuses</option>
            <option value="done">Done</option>
            <option value="green">Green</option>
            <option value="open">Open</option>
            <option value="in progress">In progress</option>
            <option value="in review">In review</option>
            <option value="blocked">Blocked</option>
            <option value="red">Red</option>
            <option value="yellow">Yellow</option>
            <option value="planned">Planned</option>
          </select>
        </label>
        <label class="field">
          <span>Change type</span>
          <select id="typeFilter">
            <option value="">All change types</option>
            <option value="milestone">Milestones</option>
            <option value="active">Active work</option>
            <option value="completed">Completed work</option>
          </select>
        </label>
      </div>
      <div class="filter-summary">
        <span id="filterResultCount">Showing all progress rows.</span>
        <div class="filter-actions">
          <button type="button" data-preset="blocked">Blocked only</button>
          <button type="button" data-preset="open">Open work</button>
          <button type="button" data-preset="done">Done changes</button>
          <button type="button" id="clearFilters">Clear filters</button>
        </div>
      </div>
    </section>

    <section class="panel">
      <h2>Milestones</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Date</th><th>Milestone</th><th>Status</th><th>Notes</th></tr></thead>
          <tbody>
            $milestoneRowsHtml
          </tbody>
        </table>
      </div>
    </section>

    <section class="panel">
      <h2>Active Work</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>ID</th><th>Started</th><th>Status</th><th>Summary</th><th>Next Step</th></tr></thead>
          <tbody>
            $activeRowsHtml
          </tbody>
        </table>
      </div>
    </section>

    <section class="panel">
      <h2>Completed Work</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Date</th><th>Summary</th><th>Files</th></tr></thead>
          <tbody>
            $completedRowsHtml
          </tbody>
        </table>
      </div>
    </section>

    <section class="panel">
      <h2>Evidence Snapshot</h2>
      <table>
        <thead><tr><th>Area</th><th>Value</th><th>Gate</th></tr></thead>
        <tbody>
          <tr><td>VEGO runtime</td><td>$settingsCount settings, $caseCount cases, $patternCount variability patterns</td><td>$baselineChanges baseline AI classification changes</td></tr>
          <tr><td>Human judgment chain</td><td>$reviewQueueCount review queue items, $memoryCount reusable memory entries, $adviceCount advice items</td><td>M4A/M4B-1 remain non-destructive</td></tr>
          <tr><td>EXP-001</td><td>$exp001Comparisons comparisons, $exp001Changed memory-informed classification changes, $exp001SafeLabels safe expert labels</td><td>Mechanism/readiness only</td></tr>
          <tr><td>EXP-002</td><td>$exp002Rows rows, $exp002SafeCandidates safe candidates</td><td>Human/supervisor labels pending</td></tr>
          <tr><td>EXP-003</td><td>$exp003Rows rows, $exp003SafeLabeled safe labeled rows</td><td>$safeExp003Gate</td></tr>
          <tr><td>EXP-005</td><td>$exp005Rows rows, $exp005SafeCandidates safe candidates, $exp005Labels supplied labels, $exp005SafeValid safe valid labels</td><td>$safeExp005Gate</td></tr>
        </tbody>
      </table>
    </section>

    <section class="claim-grid">
      <div class="panel">
        <h2>Approved Claims</h2>
        <ul>$approvedHtml</ul>
      </div>
      <div class="panel gate">
        <h2>Blocked Claims</h2>
        <ul>$blockedHtml</ul>
      </div>
    </section>

    <section class="split">
      <div class="panel">
        <h2>Recent Completed Work</h2>
        <ul class="timeline">$recentCompletedHtml</ul>
      </div>
      <div class="panel">
        <h2>Repo Status Preview</h2>
        <ul>$gitPreviewHtml</ul>
      </div>
    </section>

    <section class="panel">
      <h2>Refresh Commands</h2>
      <p><code>.\scripts\build-e2e-progress-report.ps1</code></p>
      <p><code>.\scripts\build-progress-visualizations.ps1</code></p>
      <p><code>.\scripts\build-confluence-wiki.ps1</code></p>
      <p><code>.\scripts\dashboard-health.ps1 -RequireOutbox</code></p>
      <p><code>.\scripts\research-health.ps1</code></p>
      <p><code>.\scripts\project-health.ps1</code></p>
    </section>
  </main>
  <script>
    const filterState = {
      search: document.getElementById('changeSearch'),
      date: document.getElementById('dateFilter'),
      status: document.getElementById('statusFilter'),
      type: document.getElementById('typeFilter'),
      count: document.getElementById('filterResultCount')
    };

    function applyProgressFilters() {
      const search = filterState.search.value.trim().toLowerCase();
      const date = filterState.date.value.trim().toLowerCase();
      const status = filterState.status.value.trim().toLowerCase();
      const type = filterState.type.value.trim().toLowerCase();
      const rows = Array.from(document.querySelectorAll('.change-row'));
      let shown = 0;

      rows.forEach((row) => {
        const rowSearch = row.dataset.search || '';
        const rowDate = row.dataset.date || '';
        const rowStatus = row.dataset.status || '';
        const rowType = row.dataset.type || '';
        const matchesSearch = !search || rowSearch.includes(search);
        const matchesDate = !date || rowDate === date;
        const matchesStatus = !status || rowStatus.includes(status);
        const matchesType = !type || rowType === type;
        const visible = matchesSearch && matchesDate && matchesStatus && matchesType;
        row.style.display = visible ? '' : 'none';
        if (visible) {
          shown += 1;
        }
      });

      filterState.count.textContent = `Showing ${shown} of ${rows.length} progress rows.`;
    }

    ['input', 'change'].forEach((eventName) => {
      filterState.search.addEventListener(eventName, applyProgressFilters);
      filterState.date.addEventListener(eventName, applyProgressFilters);
      filterState.status.addEventListener(eventName, applyProgressFilters);
      filterState.type.addEventListener(eventName, applyProgressFilters);
    });

    document.querySelectorAll('[data-preset]').forEach((button) => {
      button.addEventListener('click', () => {
        filterState.search.value = '';
        filterState.date.value = '';
        filterState.type.value = '';
        filterState.status.value = button.dataset.preset;
        applyProgressFilters();
      });
    });

    document.getElementById('clearFilters').addEventListener('click', () => {
      filterState.search.value = '';
      filterState.date.value = '';
      filterState.status.value = '';
      filterState.type.value = '';
      applyProgressFilters();
    });

    applyProgressFilters();
  </script>
</body>
</html>
"@

New-Item -ItemType Directory -Path (Split-Path -Parent $htmlFullPath) -Force | Out-Null
Set-Content -LiteralPath $htmlFullPath -Value $html -Encoding UTF8

Write-Host "E2E progress report generated:"
Write-Host "- $markdownFullPath"
Write-Host "- $htmlFullPath"
