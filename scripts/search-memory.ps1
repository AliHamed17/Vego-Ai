<#
.SYNOPSIS
    Search across all VEGO-AI agent memory files.

.DESCRIPTION
    Searches docs/agent-memory/ and related project files for a query string.
    Returns results with file, line number, and context in Markdown format.

.PARAMETER Query
    The search term (case-insensitive by default).

.PARAMETER Scope
    Comma-separated list of scopes: all, state, issues, decisions, sessions, progress, resources, meetings, revert
    Default: all

.PARAMETER Since
    Only show results from session-log entries after this date (YYYY-MM-DD). Only applies to session scope.

.PARAMETER CaseSensitive
    If set, search is case-sensitive.

.EXAMPLE
    .\scripts\search-memory.ps1 -Query "human expert" -Scope "all"
    .\scripts\search-memory.ps1 -Query "M4B" -Scope "decisions,issues"
    .\scripts\search-memory.ps1 -Query "feedback" -Scope "sessions" -Since "2026-06-20"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Query,

    [string]$Scope = "all",

    [string]$Since = "",

    [switch]$CaseSensitive
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$memoryDir = Join-Path $repoRoot "docs\agent-memory"

# Define scope -> file mappings
$scopeMap = @{
    "state"     = @("current-state.md", "shared-state-report.md", "review-state.md")
    "issues"    = @("issues.md")
    "decisions" = @("decisions.md")
    "sessions"  = @("session-log.md")
    "progress"  = @("progress.md")
    "resources" = @("resource-memory.md")
    "meetings"  = @()  # handled separately
    "revert"    = @("revert-log.md")
}

# Build file list from scope
$requestedScopes = $Scope -split "," | ForEach-Object { $_.Trim().ToLower() }
$filesToSearch = [System.Collections.Generic.List[string]]::new()

if ($requestedScopes -contains "all") {
    foreach ($key in $scopeMap.Keys) {
        foreach ($f in $scopeMap[$key]) {
            $full = Join-Path $memoryDir $f
            if ((Test-Path -LiteralPath $full) -and -not $filesToSearch.Contains($full)) {
                $filesToSearch.Add($full)
            }
        }
    }
    # Also search meeting notes
    $meetingDir = Join-Path $memoryDir "meeting-notes"
    if (Test-Path -LiteralPath $meetingDir) {
        Get-ChildItem -Path $meetingDir -Filter "*.md" | ForEach-Object {
            $filesToSearch.Add($_.FullName)
        }
    }
}
else {
    foreach ($s in $requestedScopes) {
        if ($scopeMap.ContainsKey($s)) {
            foreach ($f in $scopeMap[$s]) {
                $full = Join-Path $memoryDir $f
                if ((Test-Path -LiteralPath $full) -and -not $filesToSearch.Contains($full)) {
                    $filesToSearch.Add($full)
                }
            }
        }
        elseif ($s -eq "meetings") {
            $meetingDir = Join-Path $memoryDir "meeting-notes"
            if (Test-Path -LiteralPath $meetingDir) {
                Get-ChildItem -Path $meetingDir -Filter "*.md" | ForEach-Object {
                    $filesToSearch.Add($_.FullName)
                }
            }
        }
        else {
            Write-Warning "Unknown scope: $s (available: all, state, issues, decisions, sessions, progress, resources, meetings, revert)"
        }
    }
}

if ($filesToSearch.Count -eq 0) {
    Write-Host "No files to search."
    return
}

# Search
$comparison = if ($CaseSensitive) { "ccontains" } else { "icontains" }
$totalMatches = 0

Write-Host ""
Write-Host "## Memory Search Results"
Write-Host ""
Write-Host "Query: ``$Query`` | Scope: $Scope | Files: $($filesToSearch.Count)"
Write-Host ""

foreach ($filePath in $filesToSearch) {
    $fileName = Split-Path -Leaf $filePath
    $relPath = $filePath.Replace($repoRoot, "").TrimStart("\")
    $lines = Get-Content -LiteralPath $filePath -Encoding UTF8
    $matches = [System.Collections.Generic.List[string]]::new()

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        $found = if ($CaseSensitive) { $line.Contains($Query) } else { $line.ToLower().Contains($Query.ToLower()) }
        if ($found) {
            $lineNum = $i + 1
            $trimmed = $line.Trim()
            if ($trimmed.Length -gt 200) { $trimmed = $trimmed.Substring(0, 200) + "..." }
            $matches.Add("  L${lineNum}: $trimmed")
        }
    }

    if ($matches.Count -gt 0) {
        $totalMatches += $matches.Count
        Write-Host "### $relPath ($($matches.Count) matches)"
        Write-Host ""
        foreach ($m in $matches) {
            Write-Host $m
        }
        Write-Host ""
    }
}

Write-Host "---"
Write-Host "Total: $totalMatches matches across $($filesToSearch.Count) files."
