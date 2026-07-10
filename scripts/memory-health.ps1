<#
.SYNOPSIS
    Check the health of the VEGO-AI agent memory system.

.DESCRIPTION
    Validates file sizes, staleness, reference integrity, and format consistency of memory files.

.EXAMPLE
    .\scripts\memory-health.ps1
#>
[CmdletBinding()]
param(
    [switch]$FailOnWarning
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$memoryDir = Join-Path $repoRoot "docs\agent-memory"

# Config limits
$MaxT1Size = 25KB
$MaxT2Size = 130KB
$MaxT3Size = 500KB
$StalenessThresholdDays = 7

$warnings = [System.Collections.Generic.List[string]]::new()
$errors = [System.Collections.Generic.List[string]]::new()

Write-Host "Checking Memory System Health..."
Write-Host "Memory directory: $memoryDir"
Write-Host ""

# Check files exist
$requiredFiles = @(
    "current-state.md",
    "progress.md",
    "resource-memory.md",
    "issues.md",
    "decisions.md",
    "session-log.md",
    "revert-log.md"
)

foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $memoryDir $file
    if (-not (Test-Path -LiteralPath $fullPath)) {
        $errors.Add("Missing required memory file: $file")
    }
}

# Validate file sizes of compiled tiers
$t1Path = Join-Path $memoryDir "compiled-memory-t1.md"
$t2Path = Join-Path $memoryDir "compiled-memory-t2.md"
$t3Path = Join-Path $memoryDir "compiled-memory.md"

if (Test-Path -LiteralPath $t1Path) {
    $size = (Get-Item -LiteralPath $t1Path).Length
    if ($size -gt $MaxT1Size) {
        $warnings.Add("T1 Compiled Memory is too large ($([math]::Round($size/1KB, 1)) KB, max target 25 KB)")
    }
}
if (Test-Path -LiteralPath $t2Path) {
    $size = (Get-Item -LiteralPath $t2Path).Length
    if ($size -gt $MaxT2Size) {
        $warnings.Add("T2 Compiled Memory is too large ($([math]::Round($size/1KB, 1)) KB, max target 130 KB)")
    }
}
if (Test-Path -LiteralPath $t3Path) {
    $size = (Get-Item -LiteralPath $t3Path).Length
    if ($size -gt $MaxT3Size) {
        $warnings.Add("T3 Compiled Memory is too large ($([math]::Round($size/1KB, 1)) KB, max target 500 KB)")
    }
}

# Staleness check
$currentStatePath = Join-Path $memoryDir "current-state.md"
if (Test-Path -LiteralPath $currentStatePath) {
    $lastWrite = (Get-Item -LiteralPath $currentStatePath).LastWriteTime
    $days = ((Get-Date) - $lastWrite).Days
    if ($days -gt $StalenessThresholdDays) {
        $warnings.Add("current-state.md is stale: last updated $days days ago (threshold: $StalenessThresholdDays days)")
    }
}

# Consistency check: open issues in current-state vs issues.md
if ((Test-Path -LiteralPath $currentStatePath) -and (Test-Path -LiteralPath (Join-Path $memoryDir "issues.md"))) {
    $stateContent = Get-Content -Raw -LiteralPath $currentStatePath
    $issuesContent = Get-Content -Raw -LiteralPath (Join-Path $memoryDir "issues.md")
    
    # Extract ISS-XXX references from current-state
    $matches = [regex]::Matches($stateContent, 'ISS-\d{3}')
    foreach ($m in $matches) {
        $id = $m.Value
        if ($issuesContent -notmatch $id) {
            $errors.Add("Consistency error: Blocker $id referenced in current-state.md but not found in issues.md")
        }
    }
}

# Reporting
if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host -ForegroundColor Green "PASS: Memory system is healthy!"
}
else {
    if ($errors.Count -gt 0) {
        Write-Host -ForegroundColor Red "ERRORS FOUND ($($errors.Count)):"
        foreach ($e in $errors) {
            Write-Host -ForegroundColor Red "  [ERROR] $e"
        }
    }
    if ($warnings.Count -gt 0) {
        Write-Host -ForegroundColor Yellow "WARNINGS FOUND ($($warnings.Count)):"
        foreach ($w in $warnings) {
            Write-Host -ForegroundColor Yellow "  [WARNING] $w"
        }
    }
}

Write-Host ""

if ($errors.Count -gt 0 -or ($FailOnWarning -and $warnings.Count -gt 0)) {
    exit 1
}
else {
    exit 0
}
