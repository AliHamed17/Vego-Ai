[CmdletBinding()]
param(
    [string]$RunRoot = "VEGO-AI\runs\20260614-122150\human",
    [string]$EvalOutputRoot = "VEGO-AI\eval_output",
    [string]$AnalysisRoot = "VEGO-AI\analysis",
    [string]$OutputDir = "reports\generated\exp002",
    [int]$RecommendedLimit = 30
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$runRootPath = Join-Path $repoRoot $RunRoot
$evalOutputRootPath = Join-Path $repoRoot $EvalOutputRoot
$analysisRootPath = Join-Path $repoRoot $AnalysisRoot
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

function Get-Array {
    param($Value)

    if ($null -eq $Value) {
        return @()
    }
    if ($Value -is [System.Array]) {
        return @($Value)
    }
    return @($Value)
}

function Join-Values {
    param($Value)

    $items = Get-Array -Value $Value
    if ($items.Count -eq 0) {
        return ""
    }
    return (($items | ForEach-Object { [string]$_ }) -join ";")
}

function Get-FirstFile {
    param(
        [string]$Directory,
        [string[]]$Filters
    )

    if (-not (Test-Path -LiteralPath $Directory)) {
        return $null
    }

    foreach ($filter in $Filters) {
        $file = Get-ChildItem -LiteralPath $Directory -Filter $filter -File -ErrorAction SilentlyContinue |
            Sort-Object Name |
            Select-Object -First 1
        if ($file) {
            return $file
        }
    }
    return $null
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

function Get-TextOrFallback {
    param([object[]]$Values)

    foreach ($value in $Values) {
        if (-not [string]::IsNullOrWhiteSpace([string]$value)) {
            return [string]$value
        }
    }
    return ""
}

function Limit-Text {
    param(
        [string]$Text,
        [int]$MaxLength = 180
    )

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return ""
    }
    $normalized = $Text -replace "\s+", " "
    if ($normalized.Length -le $MaxLength) {
        return $normalized
    }
    return $normalized.Substring(0, $MaxLength - 3) + "..."
}

function Format-MarkdownCell {
    param($Value)

    $text = [string]$Value
    $text = $text -replace "\r?\n", " "
    $text = $text -replace "\|", "\|"
    return $text
}

$classByPattern = @{}
$deviationByPattern = @{}
$reviewByPattern = @{}
$adviceByPattern = @{}
$expertByPattern = @{}
$sourceFiles = [ordered]@{
    comparison_files = @()
    memory_advice_files = @()
    variability_class_files = @()
    deviation_pattern_files = @()
    review_queue_files = @()
    memory_files = @()
}

$memoryFiles = Get-ChildItem -LiteralPath $runRootPath -Recurse -Filter "human_judgment_memory.jsonl" -File -ErrorAction SilentlyContinue |
    Sort-Object FullName
foreach ($file in $memoryFiles) {
    $sourceFiles.memory_files += (ConvertTo-RelativePath -Path $file.FullName)
    foreach ($memory in (Read-JsonLines -Path $file.FullName)) {
        $setting = [string]$memory.provenance.source_setting
        $pattern = [string]$memory.provenance.source_pattern_id
        if ([string]::IsNullOrWhiteSpace($setting) -or [string]::IsNullOrWhiteSpace($pattern)) {
            continue
        }
        $expertByPattern["$setting|$pattern"] = [ordered]@{
            label = [string]$memory.human_classification
            source = [string]$memory.memory_id
            reviewer_id = [string]$memory.expert_id
        }
    }
}

$comparisonFiles = Get-ChildItem -LiteralPath $runRootPath -Recurse -Filter "memory_informed_comparison.json" -File -ErrorAction SilentlyContinue |
    Sort-Object FullName

foreach ($comparisonFile in $comparisonFiles) {
    $sourceFiles.comparison_files += (ConvertTo-RelativePath -Path $comparisonFile.FullName)
    $comparisonDoc = Read-JsonFile -Path $comparisonFile.FullName
    $setting = [string]$comparisonDoc.setting_id
    if ([string]::IsNullOrWhiteSpace($setting)) {
        $setting = Split-Path -Leaf (Split-Path -Parent $comparisonFile.FullName)
    }

    $settingRunDir = Split-Path -Parent $comparisonFile.FullName
    $settingEvalDir = Join-Path $evalOutputRootPath $setting

    $adviceFile = Get-FirstFile -Directory $settingRunDir -Filters @("memory_advice.json")
    if ($adviceFile) {
        $sourceFiles.memory_advice_files += (ConvertTo-RelativePath -Path $adviceFile.FullName)
        $adviceDoc = Read-JsonFile -Path $adviceFile.FullName
        foreach ($advice in (Get-Array -Value $adviceDoc.advice)) {
            $adviceByPattern["$setting|$($advice.pattern_id)"] = $advice
        }
    }

    $reviewFiles = Get-ChildItem -LiteralPath $settingRunDir -Filter "human_review_queue*.jsonl" -File -ErrorAction SilentlyContinue |
        Sort-Object Name
    foreach ($reviewFile in $reviewFiles) {
        $sourceFiles.review_queue_files += (ConvertTo-RelativePath -Path $reviewFile.FullName)
        foreach ($review in (Read-JsonLines -Path $reviewFile.FullName)) {
            $reviewByPattern["$setting|$($review.pattern_id)"] = $review
        }
    }

    $analysisClassPath = Join-Path $analysisRootPath "agentD_variability_classes_$setting.json"
    $classFile = $null
    if (Test-Path -LiteralPath $analysisClassPath) {
        $classFile = Get-Item -LiteralPath $analysisClassPath
    }
    if (-not $classFile) {
        $classFile = Get-FirstFile -Directory $settingEvalDir -Filters @("agentD_variability_classes*.json")
    }
    if ($classFile) {
        $sourceFiles.variability_class_files += (ConvertTo-RelativePath -Path $classFile.FullName)
        $classDoc = Read-JsonFile -Path $classFile.FullName
        foreach ($classification in (Get-Array -Value $classDoc.variability_classifications)) {
            $classByPattern["$setting|$($classification.pattern_id)"] = $classification
        }
    }

    $deviationFile = Get-FirstFile -Directory $settingEvalDir -Filters @("agentD_deviation_patterns*.json")
    if ($deviationFile) {
        $sourceFiles.deviation_pattern_files += (ConvertTo-RelativePath -Path $deviationFile.FullName)
        $deviationDoc = Read-JsonFile -Path $deviationFile.FullName
        foreach ($pattern in (Get-Array -Value $deviationDoc.recurring_guideline_patterns)) {
            $deviationByPattern["$setting|$($pattern.pattern_id)"] = [ordered]@{
                description = [string]$pattern.description
                affected_cases = Join-Values -Value $pattern.affected_cases
                related_guideline_id = [string]$pattern.guideline_id
                pattern_strength = [string]$pattern.pattern_strength
                pattern_kind = "guideline"
            }
        }
        foreach ($pattern in (Get-Array -Value $deviationDoc.recurring_fragment_patterns)) {
            $deviationByPattern["$setting|$($pattern.pattern_id)"] = [ordered]@{
                description = [string]$pattern.description
                affected_cases = Join-Values -Value $pattern.affected_cases
                related_guideline_id = ""
                pattern_strength = [string]$pattern.pattern_strength
                pattern_kind = "fragment:$($pattern.fragment_label)"
            }
        }
    }
}

$rows = [System.Collections.Generic.List[object]]::new()

foreach ($comparisonFile in $comparisonFiles) {
    $comparisonDoc = Read-JsonFile -Path $comparisonFile.FullName
    foreach ($comparison in (Get-Array -Value $comparisonDoc.comparisons)) {
        $setting = [string]$comparison.setting_id
        $pattern = [string]$comparison.pattern_id
        $key = "$setting|$pattern"

        $classification = $classByPattern[$key]
        $deviation = $deviationByPattern[$key]
        $review = $reviewByPattern[$key]
        $advice = $adviceByPattern[$key]
        $expert = $expertByPattern[$key]

        $original = $comparison.original_agent4_classification
        $memoryAdvice = $comparison.memory_advice
        $memoryInformed = $comparison.memory_informed_classification
        $leakage = [string]$comparison.evaluation_leakage_status
        if ([string]::IsNullOrWhiteSpace($leakage)) {
            $leakage = "unknown"
        }

        $patternDescription = Get-TextOrFallback -Values @(
            $deviation.description,
            $review.target_fragment,
            $classification.justification,
            $classification.evidence
        )
        $affectedCases = Get-TextOrFallback -Values @(
            $deviation.affected_cases,
            (Join-Values -Value $review.affected_cases)
        )
        $relatedGuideline = Get-TextOrFallback -Values @(
            $deviation.related_guideline_id,
            $review.related_guideline_id,
            $advice.query.related_guideline_id
        )
        $patternStrength = Get-TextOrFallback -Values @(
            $deviation.pattern_strength,
            $review.pattern_strength.display,
            $review.pattern_strength.value
        )
        $classificationValue = Get-TextOrFallback -Values @(
            $original.classification,
            $classification.classification
        )
        $confidence = Get-TextOrFallback -Values @(
            $original.confidence,
            $classification.confidence
        )
        $requiresReview = if ($null -ne $original.requires_human_review) {
            [bool]$original.requires_human_review
        } elseif ($null -ne $classification.requires_human_review) {
            [bool]$classification.requires_human_review
        } else {
            $false
        }
        $guidelineUpdate = if ($null -ne $original.flag_for_guidelines_update) {
            [bool]$original.flag_for_guidelines_update
        } elseif ($null -ne $classification.flag_for_guidelines_update) {
            [bool]$classification.flag_for_guidelines_update
        } else {
            $false
        }

        $memoryMatchIds = @()
        if ($memoryAdvice.memory_match_ids) {
            $memoryMatchIds = Get-Array -Value $memoryAdvice.memory_match_ids
        } elseif ($advice.memory_matches) {
            $memoryMatchIds = Get-Array -Value $advice.memory_matches | ForEach-Object { $_.memory_id }
        }

        $priority = 0
        $reasons = [System.Collections.Generic.List[string]]::new()
        if ([bool]$comparison.memory_informed_differs_from_original) {
            $priority += 100
            $reasons.Add("memory-informed differs from original")
        }
        if ([bool]$comparison.requires_human_review_after_memory) {
            $priority += 90
            $reasons.Add("requires human review after memory")
        }
        if ($requiresReview) {
            $priority += 70
            $reasons.Add("original requires human review")
        }
        if ($confidence -match "Medium|Low") {
            $priority += 60
            $reasons.Add("medium/low original confidence")
        }
        if ($guidelineUpdate) {
            $priority += 50
            $reasons.Add("guideline-update candidate")
        }
        if ($leakage -match "cross_setting|cross_domain|cross_diagram") {
            $priority += 40
            $reasons.Add("cross-context memory candidate")
        }
        if ([string]$memoryAdvice.advice_strength -match "strong|moderate") {
            $priority += 30
            $reasons.Add("moderate/strong memory advice")
        }
        if ([string]$memoryAdvice.advice_strength -eq "none") {
            $priority += 20
            $reasons.Add("no memory baseline coverage")
        }
        if ($null -eq $expert) {
            $priority += 10
            $reasons.Add("needs independent expert label")
        }
        if ($leakage -eq "same_pattern_memory_used") {
            $priority -= 180
            $reasons.Add("same-pattern memory; mechanism-only")
        }

        $rows.Add([pscustomobject][ordered]@{
            setting = $setting
            pattern_id = $pattern
            pattern_description = $patternDescription
            affected_cases = $affectedCases
            related_guideline_id = $relatedGuideline
            pattern_strength = $patternStrength
            pattern_kind = [string]$deviation.pattern_kind
            original_agent4_classification = $classificationValue
            original_confidence = $confidence
            original_justification = [string]$classification.justification
            requires_human_review = $requiresReview
            flag_for_guidelines_update = $guidelineUpdate
            memory_advice_strength = [string]$memoryAdvice.advice_strength
            memory_advice_summary = Get-TextOrFallback -Values @($memoryAdvice.advice_summary, $advice.advice_summary)
            memory_match_ids = ($memoryMatchIds -join ";")
            memory_informed_classification = [string]$memoryInformed.classification
            memory_informed_differs_from_original = [bool]$comparison.memory_informed_differs_from_original
            requires_human_review_after_memory = [bool]$comparison.requires_human_review_after_memory
            rule_applied = [string]$comparison.rule_applied
            evaluation_leakage_status = $leakage
            generalization_safe_candidate = ($leakage -ne "same_pattern_memory_used")
            existing_expert_label = if ($expert) { [string]$expert.label } else { "" }
            existing_expert_label_source = if ($expert) { [string]$expert.source } else { "" }
            existing_reviewer_id = if ($expert) { [string]$expert.reviewer_id } else { "" }
            expert_label = ""
            expert_rationale = ""
            reviewer_id = ""
            reviewer_confidence = ""
            sampling_priority_score = $priority
            sampling_reasons = ($reasons -join "; ")
            source_comparison_file = ConvertTo-RelativePath -Path $comparisonFile.FullName
        })
    }
}

$rows = @($rows | Sort-Object setting, @{ Expression = { [int](([string]$_.pattern_id) -replace "\D", "") } })

$settingCounts = @{}
$leakageCounts = @{}
$adviceCounts = @{}
$classificationCounts = @{}
foreach ($row in $rows) {
    Add-Count -Counts $settingCounts -Key $row.setting
    Add-Count -Counts $leakageCounts -Key $row.evaluation_leakage_status
    Add-Count -Counts $adviceCounts -Key $row.memory_advice_strength
    Add-Count -Counts $classificationCounts -Key $row.original_agent4_classification
}

$existingExpertRows = @($rows | Where-Object { -not [string]::IsNullOrWhiteSpace($_.existing_expert_label) })
$generalizationSafeRows = @($rows | Where-Object { $_.generalization_safe_candidate })
$reviewAfterRows = @($rows | Where-Object { $_.requires_human_review_after_memory })
$changedRows = @($rows | Where-Object { $_.memory_informed_differs_from_original })
$recommendedRows = @($rows |
    Sort-Object @{ Expression = { $_.sampling_priority_score }; Descending = $true }, setting, pattern_id |
    Select-Object -First ([Math]::Min($RecommendedLimit, $rows.Count)))

$sheetCsvPath = Join-Path $outputPath "expert_labeling_sheet.csv"
$sheetMdPath = Join-Path $outputPath "expert_labeling_sheet.md"
$recommendedPath = Join-Path $outputPath "recommended_patterns_to_label.md"
$summaryPath = Join-Path $outputPath "exp002_summary.json"

$rows | Export-Csv -NoTypeInformation -Encoding UTF8 -LiteralPath $sheetCsvPath

$sheetLines = [System.Collections.Generic.List[string]]::new()
$sheetLines.Add("# EXP-002 Expert Labeling Sheet")
$sheetLines.Add("")
$sheetLines.Add("Generated: $((Get-Date).ToUniversalTime().ToString("o"))")
$sheetLines.Add("")
$sheetLines.Add("Allowed expert labels: `Substantial Variability`, `Occasional Variability`, `Undetermined / Needs Review`.")
$sheetLines.Add("")
$sheetLines.Add("| Setting | Pattern | Description | Original | Confidence | Advice | Memory-Informed | Leakage | Existing Expert Label | Expert Label | Expert Rationale | Reviewer |")
$sheetLines.Add("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
foreach ($row in $rows) {
    $sheetLines.Add("| $(Format-MarkdownCell $row.setting) | $(Format-MarkdownCell $row.pattern_id) | $(Format-MarkdownCell (Limit-Text $row.pattern_description 160)) | $(Format-MarkdownCell $row.original_agent4_classification) | $(Format-MarkdownCell $row.original_confidence) | $(Format-MarkdownCell $row.memory_advice_strength) | $(Format-MarkdownCell $row.memory_informed_classification) | $(Format-MarkdownCell $row.evaluation_leakage_status) | $(Format-MarkdownCell $row.existing_expert_label) |  |  |  |")
}
$sheetLines | Set-Content -LiteralPath $sheetMdPath -Encoding UTF8

$recommendedLines = [System.Collections.Generic.List[string]]::new()
$recommendedLines.Add("# EXP-002 Recommended Patterns To Label")
$recommendedLines.Add("")
$recommendedLines.Add("Generated: $((Get-Date).ToUniversalTime().ToString("o"))")
$recommendedLines.Add("")
$recommendedLines.Add("Purpose: prioritize human labels that can turn M4B-1 from mechanism/readiness evidence into leakage-aware empirical evaluation.")
$recommendedLines.Add("")
$recommendedLines.Add("Minimum target: 20 expert-labeled patterns. Preferred target: 30-50 expert-labeled patterns; the current local package has $($rows.Count) available comparison rows.")
$recommendedLines.Add("")
$recommendedLines.Add("Prioritization favors review-after-memory, medium/low confidence, guideline-update candidates, cross-context memory, no-memory coverage, and rows without existing expert labels. Same-pattern memory rows are kept visible but deprioritized because they support mechanism validation only.")
$recommendedLines.Add("")
$recommendedLines.Add("## Summary")
$recommendedLines.Add("")
$recommendedLines.Add("- Total rows: $($rows.Count)")
$recommendedLines.Add("- Generalization-safe candidates: $($generalizationSafeRows.Count)")
$recommendedLines.Add("- Existing expert labels found: $($existingExpertRows.Count)")
$recommendedLines.Add("- Requires human review after memory: $($reviewAfterRows.Count)")
$recommendedLines.Add("- Memory-informed differs from original: $($changedRows.Count)")
$recommendedLines.Add("")
$recommendedLines.Add("## Recommended Labeling Order")
$recommendedLines.Add("")
$recommendedLines.Add("| Rank | Setting | Pattern | Priority | Reasons | Original | Memory-Informed | Advice | Leakage | Description |")
$recommendedLines.Add("| ---: | --- | --- | ---: | --- | --- | --- | --- | --- | --- |")
$rank = 1
foreach ($row in $recommendedRows) {
    $recommendedLines.Add("| $rank | $(Format-MarkdownCell $row.setting) | $(Format-MarkdownCell $row.pattern_id) | $($row.sampling_priority_score) | $(Format-MarkdownCell $row.sampling_reasons) | $(Format-MarkdownCell $row.original_agent4_classification) | $(Format-MarkdownCell $row.memory_informed_classification) | $(Format-MarkdownCell $row.memory_advice_strength) | $(Format-MarkdownCell $row.evaluation_leakage_status) | $(Format-MarkdownCell (Limit-Text $row.pattern_description 140)) |")
    $rank += 1
}
$recommendedLines | Set-Content -LiteralPath $recommendedPath -Encoding UTF8

$summary = [ordered]@{
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    experiment_id = "EXP-002"
    purpose = "Expert Label Expansion and Holdout Evaluation"
    run_root = ($RunRoot -replace "\\", "/")
    output_dir = ($OutputDir -replace "\\", "/")
    source_files = $sourceFiles
    totals = [ordered]@{
        row_count = $rows.Count
        existing_expert_label_count = $existingExpertRows.Count
        generalization_safe_candidate_count = $generalizationSafeRows.Count
        requires_human_review_after_memory_count = $reviewAfterRows.Count
        memory_informed_differs_from_original_count = $changedRows.Count
        recommended_count = $recommendedRows.Count
    }
    distributions = [ordered]@{
        setting = Convert-CountsToObjects -Counts $settingCounts
        original_classification = Convert-CountsToObjects -Counts $classificationCounts
        memory_advice_strength = Convert-CountsToObjects -Counts $adviceCounts
        evaluation_leakage_status = Convert-CountsToObjects -Counts $leakageCounts
    }
    label_protocol = [ordered]@{
        allowed_labels = @("Substantial Variability", "Occasional Variability", "Undetermined / Needs Review")
        minimum_target = 20
        preferred_target = "30-50"
        accuracy_claim_allowed_before_labels = $false
    }
}

$summary | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $summaryPath -Encoding UTF8

Write-Host "EXP-002 expert-labeling package generated:"
Write-Host "- $(ConvertTo-RelativePath -Path $sheetCsvPath)"
Write-Host "- $(ConvertTo-RelativePath -Path $sheetMdPath)"
Write-Host "- $(ConvertTo-RelativePath -Path $recommendedPath)"
Write-Host "- $(ConvertTo-RelativePath -Path $summaryPath)"
Write-Host ""
Write-Host "Rows: $($rows.Count)"
Write-Host "Existing expert labels found: $($existingExpertRows.Count)"
Write-Host "Generalization-safe candidate rows: $($generalizationSafeRows.Count)"
Write-Host "Recommended labeling targets: $($recommendedRows.Count)"
