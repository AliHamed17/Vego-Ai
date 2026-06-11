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

if (-not $NoPull) {
    & $startScript | Out-Host
}

Write-Host "Agent memory updated."

