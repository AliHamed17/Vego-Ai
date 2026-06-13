[CmdletBinding()]
param(
    [string]$OutputDir = "docs\confluence\outbox",
    [int]$MaxChangelogEntries = 20
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$outputPath = Join-Path $repoRoot $OutputDir
New-Item -ItemType Directory -Path $outputPath -Force | Out-Null

function Read-RepoText {
    param([Parameter(Mandatory = $true)][string]$RelativePath)
    $path = Join-Path $repoRoot $RelativePath
    if (Test-Path -LiteralPath $path) {
        return (Get-Content -Raw -LiteralPath $path)
    }
    return "_Missing: $RelativePath_`n"
}

function Write-WikiPage {
    param(
        [Parameter(Mandatory = $true)][string]$FileName,
        [Parameter(Mandatory = $true)][string]$Body
    )
    $path = Join-Path $outputPath $FileName
    Set-Content -LiteralPath $path -Value (Protect-WikiContent $Body) -Encoding UTF8
    Write-Host "[wiki] $FileName"
}

function Protect-WikiContent {
    param([Parameter(Mandatory = $true)][string]$Body)

    $protected = $Body
    $replacements = @{
        'VEGO-AI/models/' = '[controlled case-model path omitted]'
        'VEGO-AI/analysis/' = '[controlled analysis path omitted]'
        'VEGO-AI/eval_output/' = '[controlled eval-output path omitted]'
        'VEGO-AI/human_review_output/' = '[controlled human-review-output path omitted]'
        'VEGO-AI/vego_visualizer_delivery/models/' = '[controlled visualizer-model path omitted]'
        'VEGO-AI/vego_visualizer_delivery/compliance_vectors/' = '[controlled compliance-vector path omitted]'
        'VEGO-AI/vego_visualizer_delivery/guidelines/' = '[controlled visualizer-guideline path omitted]'
        'Variability_MAS4MODELS2026_Mar28_IRB2' = '[controlled IRB/PDF artifact omitted]'
        '.pdf' = '[PDF omitted]'
        '.zip' = '[archive omitted]'
        '.exe' = '[binary omitted]'
    }

    foreach ($key in $replacements.Keys) {
        $protected = $protected.Replace($key, $replacements[$key])
    }

    return $protected
}

function Get-RecentSessionEntries {
    param([int]$Limit)
    $session = Read-RepoText "docs/agent-memory/session-log.md"
    $matches = [regex]::Matches($session, "(?ms)^## .+?(?=^## |\z)")
    $entries = @()
    foreach ($match in $matches) {
        $entries += $match.Value.Trim()
    }
    if ($entries.Count -eq 0) {
        return "_No session entries found._"
    }
    $start = [Math]::Max(0, $entries.Count - $Limit)
    return (($entries[$start..($entries.Count - 1)]) -join "`n`n")
}

$generated = Get-Date -Format "yyyy-MM-dd HH:mm zzz"
$currentState = Read-RepoText "docs/agent-memory/current-state.md"
$progress = Read-RepoText "docs/agent-memory/progress.md"
$issues = Read-RepoText "docs/agent-memory/issues.md"
$decisions = Read-RepoText "docs/agent-memory/decisions.md"
$roadmap = Read-RepoText "docs/project-management/roadmap.md"
$risks = Read-RepoText "docs/project-management/risk-register.md"
$experimentRegistry = Read-RepoText "experiments/registry.md"
$artifactAudit = Read-RepoText "docs/research/artifact-audit.md"
$provenance = Read-RepoText "docs/research/provenance-register.md"
$publishability = Read-RepoText "docs/research/publishability-register.md"
$researchPlan = Read-RepoText "docs/research/research-plan.md"
$architecture = Read-RepoText "docs/architecture/project-map.md"
$progressDashboard = Read-RepoText "docs/dashboards/progress-dashboard.md"
$kpiRegister = Read-RepoText "docs/dashboards/kpi-register.md"
$resultsDashboard = Read-RepoText "docs/dashboards/results-dashboard.md"
$changelog = Get-RecentSessionEntries -Limit $MaxChangelogEntries

$homePage = @"
# VEGO-AI Wiki Home

Generated from repository memory on $generated.

This Confluence wiki is a curated external view. The Git repository and `docs/agent-memory/` remain the source of truth.

## Navigation

- VEGO-AI Current State
- VEGO-AI Progress Dashboard
- VEGO-AI Update Changelog
- VEGO-AI Research Operations

## Project Summary

VEGO-AI is a PhD research workspace for agentic AI support for variability exploration of domain models.

## Architecture

$architecture

## Research Plan

$researchPlan
"@

$current = @"
# VEGO-AI Current State

Generated from repository memory on $generated.

$currentState

## Progress

$progress

## Open Issues

$issues

## Durable Decisions

$decisions
"@

$updates = @"
# VEGO-AI Update Changelog

Generated from repository memory on $generated.

Showing the latest $MaxChangelogEntries session entries.

$changelog
"@

$dashboard = @"
# VEGO-AI Progress Dashboard

Generated from repository memory on $generated.

## Progress Dashboard

$progressDashboard

## KPI Register

$kpiRegister

## Results Dashboard

$resultsDashboard
"@

$ops = @"
# VEGO-AI Research Operations

Generated from repository memory on $generated.

## Roadmap

$roadmap

## Risk Register

$risks

## Experiment Registry

$experimentRegistry

## Artifact Audit

$artifactAudit

## Provenance Register

$provenance

## Publishability Register

$publishability
"@

Write-WikiPage -FileName "vego-ai-wiki-home.md" -Body $homePage
Write-WikiPage -FileName "vego-ai-current-state.md" -Body $current
Write-WikiPage -FileName "vego-ai-progress-dashboard.md" -Body $dashboard
Write-WikiPage -FileName "vego-ai-update-changelog.md" -Body $updates
Write-WikiPage -FileName "vego-ai-research-operations.md" -Body $ops

Write-Host "Confluence wiki outbox generated: $outputPath"
Write-Host "Live Confluence update requires Atlassian access plus page IDs in docs/confluence/wiki-sync-config.local.json."
