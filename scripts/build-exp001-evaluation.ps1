[CmdletBinding()]
param(
    [string]$RunRoot = "VEGO-AI\runs\20260614-122150\human",
    [string]$OutputDir = "reports\generated\exp001"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$runRootPath = Join-Path $repoRoot $RunRoot
$outputPath = Join-Path $repoRoot $OutputDir

if (-not (Test-Path -LiteralPath $runRootPath)) {
    throw "Run root not found: $runRootPath"
}

New-Item -ItemType Directory -Force -Path $outputPath | Out-Null

function ConvertTo-RelativePath {
    param([string]$Path)

    $resolved = Resolve-Path -LiteralPath $Path
    $relative = [System.IO.Path]::GetRelativePath($repoRoot, $resolved)
    return $relative -replace "\\", "/"
}

function Read-JsonFile {
    param([string]$Path)
    return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Read-JsonLines {
    param([string]$Path)

    $items = [System.Collections.Generic.List[object]]::new()
    if (-not (Test-Path -LiteralPath $Path)) {
        return $items
    }

    Get-Content -LiteralPath $Path | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object {
        $items.Add(($_ | ConvertFrom-Json))
    }
    return $items
}

function Add-Count {
    param(
        [hashtable]$Counts,
        [string]$Key
    )

    if ([string]::IsNullOrWhiteSpace($Key)) {
        $Key = "unknown"
    }
    if (-not $Counts.ContainsKey($Key)) {
        $Counts[$Key] = 0
    }
    $Counts[$Key] += 1
}

function Convert-CountsToObjects {
    param([hashtable]$Counts)

    return @(
        foreach ($key in ($Counts.Keys | Sort-Object)) {
            [ordered]@{
                value = $key
                count = $Counts[$key]
            }
        }
    )
}

$expertByPattern = @{}
$memoryFiles = Get-ChildItem -LiteralPath $runRootPath -Recurse -Filter "human_judgment_memory.jsonl" -File -ErrorAction SilentlyContinue
foreach ($file in $memoryFiles) {
    foreach ($memory in (Read-JsonLines -Path $file.FullName)) {
        $sourceSetting = $memory.provenance.source_setting
        $sourcePattern = $memory.provenance.source_pattern_id
        if ([string]::IsNullOrWhiteSpace($sourceSetting) -or [string]::IsNullOrWhiteSpace($sourcePattern)) {
            continue
        }

        $key = "$sourceSetting|$sourcePattern"
        $expertByPattern[$key] = [ordered]@{
            expert_classification = $memory.human_classification
            expert_id = $memory.expert_id
            expert_label_source = $memory.memory_id
            source_file = ConvertTo-RelativePath -Path $file.FullName
        }
    }
}

$rows = [System.Collections.Generic.List[object]]::new()
$comparisonFiles = Get-ChildItem -LiteralPath $runRootPath -Recurse -Filter "memory_informed_comparison.json" -File -ErrorAction SilentlyContinue |
    Sort-Object FullName

foreach ($file in $comparisonFiles) {
    $comparisonDoc = Read-JsonFile -Path $file.FullName
    foreach ($comparison in $comparisonDoc.comparisons) {
        $setting = [string]$comparison.setting_id
        $pattern = [string]$comparison.pattern_id
        $key = "$setting|$pattern"

        $expertClassification = ""
        $expertSource = "none_found"
        $expertId = ""
        if ($expertByPattern.ContainsKey($key)) {
            $expertClassification = $expertByPattern[$key].expert_classification
            $expertSource = $expertByPattern[$key].expert_label_source
            $expertId = $expertByPattern[$key].expert_id
        }

        $original = [string]$comparison.original_agent4_classification.classification
        $memoryInformed = [string]$comparison.memory_informed_classification.classification
        $leakage = [string]$comparison.evaluation_leakage_status
        $hasExpert = -not [string]::IsNullOrWhiteSpace($expertClassification)

        $originalMatchesExpert = ""
        $memoryMatchesExpert = ""
        if ($hasExpert) {
            $originalMatchesExpert = ([string]($original -eq $expertClassification)).ToLowerInvariant()
            $memoryMatchesExpert = ([string]($memoryInformed -eq $expertClassification)).ToLowerInvariant()
        }

        $memoryIds = @()
        if ($comparison.human_memory_used) {
            $memoryIds = @($comparison.human_memory_used | ForEach-Object {
                if ($_.memory_id) { $_.memory_id } else { [string]$_ }
            })
        }

        $rows.Add([pscustomobject][ordered]@{
            setting = $setting
            pattern_id = $pattern
            original_classification = $original
            memory_informed_classification = $memoryInformed
            expert_classification = $expertClassification
            expert_label_source = $expertSource
            expert_id = $expertId
            original_matches_expert = $originalMatchesExpert
            memory_informed_matches_expert = $memoryMatchesExpert
            advice_strength = [string]$comparison.memory_advice.advice_strength
            rule_applied = [string]$comparison.rule_applied
            evaluation_leakage_status = $leakage
            requires_human_review_after_memory = [bool]$comparison.requires_human_review_after_memory
            memory_informed_differs_from_original = [bool]$comparison.memory_informed_differs_from_original
            human_memory_used_count = $memoryIds.Count
            human_memory_used = ($memoryIds -join ";")
            has_conflicting_memory = [bool]$comparison.memory_advice.has_conflicting_memory
            mechanism_validation_subset = $true
            generalization_safe_subset = ($leakage -ne "same_pattern_memory_used")
            source_file = ConvertTo-RelativePath -Path $file.FullName
        })
    }
}

$adviceStrengthCounts = @{}
$leakageCounts = @{}
$ruleCounts = @{}
$settingCounts = @{}
$expertRows = @()
$generalizationExpertRows = @()
$changedRows = @()
$reviewAfterRows = @()
$conflictRows = @()

foreach ($row in $rows) {
    Add-Count -Counts $adviceStrengthCounts -Key $row.advice_strength
    Add-Count -Counts $leakageCounts -Key $row.evaluation_leakage_status
    Add-Count -Counts $ruleCounts -Key $row.rule_applied
    Add-Count -Counts $settingCounts -Key $row.setting
    if ($row.memory_informed_differs_from_original) { $changedRows += $row }
    if ($row.requires_human_review_after_memory) { $reviewAfterRows += $row }
    if ($row.has_conflicting_memory) { $conflictRows += $row }
    if (-not [string]::IsNullOrWhiteSpace($row.expert_classification)) {
        $expertRows += $row
        if ($row.generalization_safe_subset) {
            $generalizationExpertRows += $row
        }
    }
}

$originalExpertMatches = @($expertRows | Where-Object { $_.original_matches_expert -eq "true" }).Count
$memoryExpertMatches = @($expertRows | Where-Object { $_.memory_informed_matches_expert -eq "true" }).Count
$generalizationOriginalMatches = @($generalizationExpertRows | Where-Object { $_.original_matches_expert -eq "true" }).Count
$generalizationMemoryMatches = @($generalizationExpertRows | Where-Object { $_.memory_informed_matches_expert -eq "true" }).Count

function Get-Rate {
    param(
        [int]$Numerator,
        [int]$Denominator
    )
    if ($Denominator -eq 0) {
        return $null
    }
    return [Math]::Round($Numerator / $Denominator, 4)
}

$summary = [ordered]@{
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    experiment_id = "EXP-001"
    run_root = ($RunRoot -replace "\\", "/")
    output_dir = ($OutputDir -replace "\\", "/")
    source_files = [ordered]@{
        comparison_files = @($comparisonFiles | ForEach-Object { ConvertTo-RelativePath -Path $_.FullName })
        memory_files = @($memoryFiles | ForEach-Object { ConvertTo-RelativePath -Path $_.FullName })
    }
    totals = [ordered]@{
        comparison_count = $rows.Count
        expert_labeled_count = $expertRows.Count
        generalization_safe_expert_labeled_count = $generalizationExpertRows.Count
        changed_count = $changedRows.Count
        requires_human_review_after_memory_count = $reviewAfterRows.Count
        conflict_or_ambiguous_count = $conflictRows.Count
    }
    distributions = [ordered]@{
        setting = Convert-CountsToObjects -Counts $settingCounts
        advice_strength = Convert-CountsToObjects -Counts $adviceStrengthCounts
        rule_applied = Convert-CountsToObjects -Counts $ruleCounts
        evaluation_leakage_status = Convert-CountsToObjects -Counts $leakageCounts
    }
    agreement = [ordered]@{
        mechanism_validation = [ordered]@{
            expert_labeled_count = $expertRows.Count
            original_matches_expert = $originalExpertMatches
            memory_informed_matches_expert = $memoryExpertMatches
            original_expert_agreement_rate = Get-Rate -Numerator $originalExpertMatches -Denominator $expertRows.Count
            memory_informed_expert_agreement_rate = Get-Rate -Numerator $memoryExpertMatches -Denominator $expertRows.Count
            interpretation = "Includes any expert labels found in reusable human memory; same-pattern memory is mechanism evidence, not generalization proof."
        }
        generalization_safe = [ordered]@{
            expert_labeled_count = $generalizationExpertRows.Count
            original_matches_expert = $generalizationOriginalMatches
            memory_informed_matches_expert = $generalizationMemoryMatches
            original_expert_agreement_rate = Get-Rate -Numerator $generalizationOriginalMatches -Denominator $generalizationExpertRows.Count
            memory_informed_expert_agreement_rate = Get-Rate -Numerator $generalizationMemoryMatches -Denominator $generalizationExpertRows.Count
            interpretation = "Excludes same-pattern memory; if count is zero, no generalization claim is allowed."
        }
    }
    conclusion = [ordered]@{
        m4b1_behavior = "non_destructive_parallel_comparison"
        expert_alignment_status = $(if ($expertRows.Count -eq 0) { "not_evaluable_no_expert_labels" } elseif ($generalizationExpertRows.Count -eq 0) { "mechanism_validation_only_no_generalization_safe_expert_labels" } else { "partially_evaluable" })
        improvement_claim_allowed = $false
        statement = "This run can support mechanism/readiness analysis. It cannot support an accuracy-improvement claim without generalization-safe expert labels."
    }
}

$csvPath = Join-Path $outputPath "exp001_evaluation_dataset.csv"
$summaryJsonPath = Join-Path $outputPath "exp001_summary.json"
$summaryMarkdownPath = Join-Path $outputPath "exp001_summary.md"
$tableMarkdownPath = Join-Path $outputPath "exp001_evaluation_table.md"

$rows | Export-Csv -NoTypeInformation -Encoding UTF8 -LiteralPath $csvPath
$summary | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $summaryJsonPath -Encoding UTF8

$tableLines = [System.Collections.Generic.List[string]]::new()
$tableLines.Add("# EXP-001 Evaluation Dataset")
$tableLines.Add("")
$tableLines.Add("Generated: $($summary.generated_at)")
$tableLines.Add("")
$tableLines.Add("| Setting | Pattern | Original | Memory-Informed | Expert | Advice | Rule | Leakage | Review After Memory | Differs |")
$tableLines.Add("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
foreach ($row in $rows) {
    $expert = if ([string]::IsNullOrWhiteSpace($row.expert_classification)) { "Not available" } else { $row.expert_classification }
    $tableLines.Add("| $($row.setting) | $($row.pattern_id) | $($row.original_classification) | $($row.memory_informed_classification) | $expert | $($row.advice_strength) | $($row.rule_applied) | $($row.evaluation_leakage_status) | $($row.requires_human_review_after_memory) | $($row.memory_informed_differs_from_original) |")
}
$tableLines | Set-Content -LiteralPath $tableMarkdownPath -Encoding UTF8

$summaryLines = [System.Collections.Generic.List[string]]::new()
$summaryLines.Add("# EXP-001 Summary")
$summaryLines.Add("")
$summaryLines.Add("Generated: $($summary.generated_at)")
$summaryLines.Add("")
$summaryLines.Add("## Headline")
$summaryLines.Add("")
$summaryLines.Add("- Comparisons: $($summary.totals.comparison_count)")
$summaryLines.Add("- Expert-labeled comparisons available from reusable memory: $($summary.totals.expert_labeled_count)")
$summaryLines.Add("- Generalization-safe expert-labeled comparisons: $($summary.totals.generalization_safe_expert_labeled_count)")
$summaryLines.Add("- Memory-informed classifications differing from original: $($summary.totals.changed_count)")
$summaryLines.Add("- Human-review-after-memory flags: $($summary.totals.requires_human_review_after_memory_count)")
$summaryLines.Add("- Conflicting memory flags: $($summary.totals.conflict_or_ambiguous_count)")
$summaryLines.Add("")
$summaryLines.Add("## Agreement")
$summaryLines.Add("")
$summaryLines.Add("| Subset | Expert Labels | Original Matches | Memory-Informed Matches | Original Rate | Memory-Informed Rate |")
$summaryLines.Add("| --- | ---: | ---: | ---: | ---: | ---: |")
$summaryLines.Add("| Mechanism validation | $($summary.agreement.mechanism_validation.expert_labeled_count) | $($summary.agreement.mechanism_validation.original_matches_expert) | $($summary.agreement.mechanism_validation.memory_informed_matches_expert) | $($summary.agreement.mechanism_validation.original_expert_agreement_rate) | $($summary.agreement.mechanism_validation.memory_informed_expert_agreement_rate) |")
$summaryLines.Add("| Generalization-safe | $($summary.agreement.generalization_safe.expert_labeled_count) | $($summary.agreement.generalization_safe.original_matches_expert) | $($summary.agreement.generalization_safe.memory_informed_matches_expert) | $($summary.agreement.generalization_safe.original_expert_agreement_rate) | $($summary.agreement.generalization_safe.memory_informed_expert_agreement_rate) |")
$summaryLines.Add("")
$summaryLines.Add("## Conclusion")
$summaryLines.Add("")
$summaryLines.Add($summary.conclusion.statement)
$summaryLines | Set-Content -LiteralPath $summaryMarkdownPath -Encoding UTF8

Write-Host "EXP-001 evaluation outputs generated:"
Write-Host "- $(ConvertTo-RelativePath -Path $csvPath)"
Write-Host "- $(ConvertTo-RelativePath -Path $tableMarkdownPath)"
Write-Host "- $(ConvertTo-RelativePath -Path $summaryJsonPath)"
Write-Host "- $(ConvertTo-RelativePath -Path $summaryMarkdownPath)"
Write-Host ""
Write-Host "Conclusion: $($summary.conclusion.statement)"
