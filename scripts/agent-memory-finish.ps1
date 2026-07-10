[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Agent,

    [Parameter(Mandatory = $true)]
    [string]$Title,

    [Parameter(Mandatory = $true)]
    [string]$Request,

    [string[]]$Actions = @(),
    [string[]]$FilesChanged = @(),
    [string[]]$Commands = @(),
    [string]$Status = "completed",
    [string]$NextSteps = "Unknown",
    [string]$RollbackNote = "",
    [switch]$SkipRevertLog,
    [switch]$NoPull,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$memoryDir = Join-Path $repoRoot "docs\agent-memory"
$sessionLog = Join-Path $memoryDir "session-log.md"
$revertLog = Join-Path $memoryDir "revert-log.md"
$startScript = Join-Path $PSScriptRoot "agent-memory-start.ps1"

function Format-MemoryBullets {
    param(
        [string[]]$Items,
        [string]$Fallback
    )

    if ($null -eq $Items -or $Items.Count -eq 0) {
        return "  - $Fallback"
    }

    return (($Items | ForEach-Object { "  - $_" }) -join [Environment]::NewLine)
}

function Optimize-LogFile {
    param(
        [string]$LogPath,
        [string]$ArchivePath,
        [int]$KeepDays,
        [string]$LogName
    )

    if (-not (Test-Path -LiteralPath $LogPath)) { return }
    $content = Get-Content -Raw -LiteralPath $LogPath
    
    # Headers like "## 2026-06-24" or "## 2026-06-24 12:34"
    $matches = [regex]::Matches($content, '(?m)^##\s+(\d{4}-\d{2}-\d{2})')
    if ($matches.Count -eq 0) { return }
    
    $preamble = $content.Substring(0, $matches[0].Index)
    
    $keepEntries = [System.Collections.Generic.List[string]]::new()
    $archiveEntries = [System.Collections.Generic.List[string]]::new()
    $cutoffDate = (Get-Date).AddDays(-$KeepDays)
    
    for ($i = 0; $i -lt $matches.Count; $i++) {
        $startIdx = $matches[$i].Index
        $endIdx = if ($i + 1 -lt $matches.Count) { $matches[$i + 1].Index } else { $content.Length }
        $entryContent = $content.Substring($startIdx, $endIdx - $startIdx).Trim()
        
        $dateStr = $matches[$i].Groups[1].Value
        
        try {
            $entryDate = [DateTime]::ParseExact($dateStr, "yyyy-MM-dd", $null)
            if ($entryDate -lt $cutoffDate) {
                $archiveEntries.Add($entryContent)
            } else {
                $keepEntries.Add($entryContent)
            }
        }
        catch {
            # Default to keep if date format parsing fails
            $keepEntries.Add($entryContent)
        }
    }
    
    if ($archiveEntries.Count -gt 0) {
        Write-Host "Archiving $($archiveEntries.Count) entries from $LogName..."
        
        # Write keep entries back to LogPath
        $newLogContent = $preamble.TrimEnd() + [Environment]::NewLine + [Environment]::NewLine + ($keepEntries -join ([Environment]::NewLine + [Environment]::NewLine)) + [Environment]::NewLine
        Set-Content -LiteralPath $LogPath -Value $newLogContent -Encoding UTF8
        
        # Archive entries to ArchivePath
        $archivePreamble = "# $LogName Archive" + [Environment]::NewLine + [Environment]::NewLine + "Historical entries." + [Environment]::NewLine + [Environment]::NewLine
        $existingArchive = ""
        if (Test-Path -LiteralPath $ArchivePath) {
            $existingArchive = Get-Content -Raw -LiteralPath $ArchivePath
            if ($existingArchive -match '(?m)^##\s+') {
                $archivePreamble = ""
            }
        }
        
        $newArchiveContent = $existingArchive.TrimEnd() + [Environment]::NewLine + [Environment]::NewLine + $archivePreamble + ($archiveEntries -join ([Environment]::NewLine + [Environment]::NewLine)) + [Environment]::NewLine
        $newArchiveContent = $newArchiveContent.TrimStart()
        Set-Content -LiteralPath $ArchivePath -Value $newArchiveContent -Encoding UTF8
    }
}

if (-not (Test-Path -LiteralPath $memoryDir)) {
    throw "Memory directory not found: $memoryDir"
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm zzz"
$actionsBlock = Format-MemoryBullets -Items $Actions -Fallback "Unknown"
$filesBlock = Format-MemoryBullets -Items $FilesChanged -Fallback "No file changes recorded"
$commandsBlock = Format-MemoryBullets -Items $Commands -Fallback "No commands/checks recorded"

$sessionEntry = @"

## $timestamp - $Agent - $Title

- Request: $Request
- Actions taken:
$actionsBlock
- Files changed:
$filesBlock
- Commands/checks:
$commandsBlock
- Status: $Status
- Next steps: $NextSteps
"@

$shouldWriteRevert = (-not $SkipRevertLog) -and (-not [string]::IsNullOrWhiteSpace($RollbackNote))

$revertEntry = @"

## $timestamp - $Agent - $Title

- Files changed:
$filesBlock
- Rollback note: $RollbackNote
- Git commit: none recorded by script.
"@

if ($DryRun) {
    Write-Output "Session entry preview:"
    Write-Output $sessionEntry
    if ($shouldWriteRevert) {
        Write-Output "Revert entry preview:"
        Write-Output $revertEntry
    }
    return
}

Add-Content -LiteralPath $sessionLog -Value $sessionEntry -Encoding UTF8

if ($shouldWriteRevert) {
    Add-Content -LiteralPath $revertLog -Value $revertEntry -Encoding UTF8
}

# Run optimization/archival to keep logs compact
Optimize-LogFile -LogPath $sessionLog -ArchivePath (Join-Path $memoryDir "session-log-archive.md") -KeepDays 14 -LogName "Session Log"
Optimize-LogFile -LogPath $revertLog -ArchivePath (Join-Path $memoryDir "revert-log-archive.md") -KeepDays 30 -LogName "Revert Log"

if (-not $NoPull) {
    & $startScript | Out-Host
}

Write-Host "Agent memory updated."

