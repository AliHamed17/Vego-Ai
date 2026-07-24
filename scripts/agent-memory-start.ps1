[CmdletBinding()]
param(
    [switch]$Print,
    [ValidateSet("t1", "t2", "t3", "all")]
    [string]$Tier = "all"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$memoryDir = Join-Path $repoRoot "docs\agent-memory"

# Output paths for each tier
$outputT1 = Join-Path $memoryDir "compiled-memory-t1.md"
$outputT2 = Join-Path $memoryDir "compiled-memory-t2.md"
$outputT3 = Join-Path $memoryDir "compiled-memory.md"

# ---------------------------------------------------------------------------
# Tier definitions
# T1 = Quick Start (< 8 KB target)
# T2 = Working Context (< 40 KB target)
# T3 = Full Archive (unlimited, backward-compatible)
# ---------------------------------------------------------------------------

$t1Paths = @(
    "docs/agent-memory/current-state.md",
    "docs/agent-memory/review-state.md",
    "docs/agent-memory/resource-memory.md"
)

$t2Paths = @(
    "docs/agent-memory/current-state.md",
    "docs/agent-memory/shared-state-report.md",
    "docs/agent-memory/resource-memory.md",
    "docs/agent-memory/review-state.md",
    "docs/agent-memory/progress.md",
    "docs/agent-memory/issues.md",
    "docs/agent-memory/decisions.md",
    "docs/agent-memory/milestone-workflow-rules.md"
)

$t3Paths = @(
    "docs/agent-memory/current-state.md",
    "docs/agent-memory/shared-state-report.md",
    "docs/agent-memory/resource-memory.md",
    "docs/agent-memory/review-state.md",
    "docs/agent-memory/progress.md",
    "docs/agent-memory/issues.md",
    "docs/agent-memory/decisions.md",
    "docs/agent-memory/milestone-workflow-rules.md",
    "docs/agent-memory/session-log.md",
    "docs/agent-memory/revert-log.md",
    "docs/agent-memory/README.md",
    "README.md",
    "PROJECT_CHARTER.md",
    "docs/architecture/project-map.md",
    "docs/architecture/research-lifecycle.md",
    "docs/architecture/reproducibility-contract.md",
    "docs/architecture/source-package-manifest.md",
    "docs/research/research-plan.md",
    "docs/research/evaluation-plan.md",
    "docs/research/evaluation-report.md",
    "experiments/registry.md"
)

if (-not (Test-Path -LiteralPath $memoryDir)) {
    throw "Memory directory not found: $memoryDir"
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"

# Git status
$gitStatusText = "Unknown"
try {
    $gitOutput = & git -C $repoRoot status --short 2>&1
    if ($LASTEXITCODE -eq 0) {
        if ($gitOutput) {
            $dirtyCount = ($gitOutput | Measure-Object).Count
            $gitStatusText = "$dirtyCount file(s) changed"
        }
        else {
            $gitStatusText = "Clean"
        }
    }
    else {
        $gitStatusText = "Not a Git repository"
    }
}
catch {
    $gitStatusText = "Git check failed: $($_.Exception.Message)"
}

# Get last 3 session log entries for T1
function Get-RecentSessions {
    param([string]$SessionLogPath, [int]$Count = 3)
    if (-not (Test-Path -LiteralPath $SessionLogPath)) { return "No session log found." }
    $content = Get-Content -Raw -LiteralPath $SessionLogPath
    $entries = [regex]::Matches($content, '(?m)^## \d{4}-\d{2}-\d{2}.*$')
    if ($entries.Count -eq 0) { return "No sessions recorded." }

    $result = [System.Collections.Generic.List[string]]::new()
    $startIdx = [Math]::Max(0, $entries.Count - $Count)
    for ($i = $startIdx; $i -lt $entries.Count; $i++) {
        $entryStart = $entries[$i].Index
        $entryEnd = if ($i + 1 -lt $entries.Count) { $entries[$i + 1].Index } else { $content.Length }
        $chunk = $content.Substring($entryStart, $entryEnd - $entryStart).Trim()
        $lines = $chunk -split "`n"
        $header = $lines[0]
        $requestLine = ($lines | Where-Object { $_ -match '^\s*-\s*Request:' } | Select-Object -First 1)
        $statusLine = ($lines | Where-Object { $_ -match '^\s*-\s*Status:' } | Select-Object -First 1)
        $result.Add($header)
        if ($requestLine) { $result.Add($requestLine.Trim()) }
        if ($statusLine) { $result.Add($statusLine.Trim()) }
        $result.Add("")
    }
    return ($result -join [Environment]::NewLine)
}

# Count active blockers from issues.md
function Get-BlockerCount {
    $issuesPath = Join-Path $memoryDir "issues.md"
    if (-not (Test-Path -LiteralPath $issuesPath)) { return 0 }
    $content = Get-Content -Raw -LiteralPath $issuesPath
    return ([regex]::Matches($content, '(?i)\bBlocked\b')).Count
}

# Memory file sizes for health summary
function Get-MemoryHealth {
    $files = @("current-state.md", "session-log.md", "revert-log.md", "compiled-memory.md",
               "progress.md", "issues.md", "decisions.md", "resource-memory.md")
    $result = [System.Collections.Generic.List[string]]::new()
    foreach ($f in $files) {
        $path = Join-Path $memoryDir $f
        if (Test-Path -LiteralPath $path) {
            $size = (Get-Item -LiteralPath $path).Length
            $sizeKB = [math]::Round($size / 1024, 1)
            $lastWrite = (Get-Item -LiteralPath $path).LastWriteTime.ToString("yyyy-MM-dd")
            $warning = ""
            if ($f -eq "compiled-memory.md" -and $size -gt 102400) { $warning = " LARGE" }
            if ($f -eq "session-log.md" -and $size -gt 51200) { $warning = " LARGE" }
            if ($f -eq "revert-log.md" -and $size -gt 20480) { $warning = " LARGE" }
            $result.Add("| $f | $sizeKB KB | $lastWrite |$warning")
        }
    }
    return ($result -join [Environment]::NewLine)
}

# ---------------------------------------------------------------------------
# Build a compiled tier
# ---------------------------------------------------------------------------
function Build-Tier {
    param(
        [string]$TierName,
        [string]$TierDesc,
        [string[]]$Paths,
        [string]$OutputPath,
        [string]$ExtraHeader
    )

    $sections = [System.Collections.Generic.List[string]]::new()
    $sections.Add("# Compiled Agent Memory - $TierName")
    $sections.Add("")
    $sections.Add("Generated: $timestamp | Git: $gitStatusText")
    $sections.Add("")
    $sections.Add("> $TierDesc")
    $sections.Add("")

    if ($ExtraHeader) {
        $sections.Add($ExtraHeader)
        $sections.Add("")
    }

    foreach ($relativePath in $Paths) {
        $path = Join-Path $repoRoot $relativePath
        $displayPath = $relativePath -replace "\\", "/"
        $sections.Add("## Source: $displayPath")
        $sections.Add("")

        if (Test-Path -LiteralPath $path) {
            $content = Get-Content -Raw -LiteralPath $path
            $sections.Add($content.TrimEnd())
        }
        else {
            $sections.Add("Missing file: $displayPath")
        }

        $sections.Add("")
    }

    $compiled = $sections -join [Environment]::NewLine
    Set-Content -LiteralPath $OutputPath -Value $compiled -Encoding UTF8
    $sizeKB = [math]::Round((Get-Item -LiteralPath $OutputPath).Length / 1024, 1)
    Write-Host "  ${TierName}: ${OutputPath} (${sizeKB} KB)"
    return $compiled
}

# ---------------------------------------------------------------------------
# Generate requested tiers
# ---------------------------------------------------------------------------

Write-Host "Agent memory compilation ($timestamp)"
Write-Host ""

$sessionLogPath = Join-Path $memoryDir "session-log.md"
$recentSessions = Get-RecentSessions -SessionLogPath $sessionLogPath -Count 3
$blockerCount = Get-BlockerCount
$healthTable = Get-MemoryHealth

$t1Extra = @"
## Quick Orientation

- Active blockers: $blockerCount
- Git: $gitStatusText

### Memory Health

| File | Size | Updated |
| --- | ---: | --- |
$healthTable

### Last 3 Sessions

$recentSessions
"@

if ($Tier -eq "t1" -or $Tier -eq "all") {
    Build-Tier -TierName "T1 Quick Start" -TierDesc "Fast orientation for every prompt. Read this first. Expand to T2 or T3 only when deeper context is needed." -Paths $t1Paths -OutputPath $outputT1 -ExtraHeader $t1Extra | Out-Null
}

if ($Tier -eq "t2" -or $Tier -eq "all") {
    Build-Tier -TierName "T2 Working Context" -TierDesc "Full working context: state, issues, decisions, progress, resources. Use when the task needs more than T1 orientation." -Paths $t2Paths -OutputPath $outputT2 | Out-Null
}

if ($Tier -eq "t3" -or $Tier -eq "all") {
    Build-Tier -TierName "T3 Full Archive" -TierDesc "Complete archive including session log, revert log, and all project docs. Use for deep research or historical investigation." -Paths $t3Paths -OutputPath $outputT3 | Out-Null
}

Write-Host ""
Write-Host "Agent memory compiled."

if ($Print) {
    if (Test-Path -LiteralPath $outputT1) {
        Write-Output (Get-Content -Raw -LiteralPath $outputT1)
    }
}
