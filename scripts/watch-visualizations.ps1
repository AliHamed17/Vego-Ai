# 24/7 visualization + tracking watcher.
#
# Polls the project's SOURCE files and, on any change, runs `refresh-tracking.ps1 -Viz` in PARALLEL
# (non-blocking) so diagrams/graphs/tracker/guard update automatically as you work. The deterministic
# engine uses no API/LLM and only writes generated/viz outputs, so this is safe to run continuously.
#
# Usage:
#   .\scripts\watch-visualizations.ps1                 # run the watcher loop (Ctrl+C or -Stop to end)
#   .\scripts\watch-visualizations.ps1 -Once           # one change-check + refresh, then exit (for testing)
#   .\scripts\watch-visualizations.ps1 -Stop           # signal a running watcher to stop
#   .\scripts\watch-visualizations.ps1 -Install        # register a per-user Scheduled Task (24/7 at logon)
#   .\scripts\watch-visualizations.ps1 -Uninstall      # remove the Scheduled Task
#
# Anti-loop: only SOURCE files are fingerprinted; everything the refresh itself writes (generated/viz/
# tracker/compiled-memory/figures/dashboard) is ignored, so refreshes never re-trigger the watcher.
[CmdletBinding()]
param(
    [switch]$Once,
    [switch]$Stop,
    [switch]$Install,
    [switch]$Uninstall,
    [int]$IntervalSeconds = 5
)

$ErrorActionPreference = "Continue"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$stateDir = Join-Path $repoRoot "reports\generated\visualization_agent"
$stopFlag = Join-Path $stateDir ".watcher.stop"
$statusFile = Join-Path $stateDir ".watcher.status"
$taskName = "VEGO-AI Visualization Watcher"
New-Item -ItemType Directory -Force -Path $stateDir | Out-Null

# --- Scheduled Task install / uninstall (durable 24/7) ----------------------
$startupDir = [Environment]::GetFolderPath('Startup')
$startupCmd = Join-Path $startupDir "vego-ai-visualization-watcher.cmd"

if ($Install) {
    # Primary (no admin needed): Startup-folder entry -> launches the hidden watcher at every logon.
    $line = "@echo off`r`nstart `"`" /min pwsh -NoProfile -WindowStyle Hidden -File `"$PSScriptRoot\watch-visualizations.ps1`""
    Set-Content -LiteralPath $startupCmd -Value $line -Encoding ascii
    Write-Host "Installed logon autostart: $startupCmd"
    # Best-effort: also register a Scheduled Task (only works if this shell is elevated).
    try {
        $action = New-ScheduledTaskAction -Execute "pwsh" -Argument "-NoProfile -WindowStyle Hidden -File `"$PSScriptRoot\watch-visualizations.ps1`""
        $trigger = New-ScheduledTaskTrigger -AtLogOn
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Force -ErrorAction Stop | Out-Null
        Write-Host "Also registered scheduled task '$taskName'."
    } catch { Write-Host "(Scheduled task needs admin; Startup-folder autostart is used instead.)" }
    # Start immediately (detached, hidden) so it is live now without waiting for the next logon.
    Start-Process -FilePath "pwsh" -WindowStyle Hidden -WorkingDirectory $repoRoot `
        -ArgumentList @("-NoProfile", "-File", "$PSScriptRoot\watch-visualizations.ps1") | Out-Null
    Write-Host "Watcher started now (hidden). Stop with: .\scripts\watch-visualizations.ps1 -Stop"
    return
}
if ($Uninstall) {
    if (Test-Path $startupCmd) { Remove-Item $startupCmd -Force; Write-Host "Removed logon autostart." }
    try { Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction Stop; Write-Host "Removed scheduled task." } catch {}
    New-Item -ItemType File -Force -Path $stopFlag | Out-Null
    Write-Host "Stop flag written; a running watcher will exit shortly."
    return
}
if ($Stop) {
    New-Item -ItemType File -Force -Path $stopFlag | Out-Null
    Write-Host "Stop flag written; the watcher will exit within $IntervalSeconds s."
    return
}

# --- watched SOURCE roots + ignore patterns ---------------------------------
$watchRoots = @(
    "VEGO-AI\eval_output", "VEGO-AI\framework", "VEGO-AI\schemas", "VEGO-AI\tests", "VEGO-AI\analysis",
    "docs\agent-memory", "docs\research", "docs\architecture", "docs\dashboards", "docs\visualizations",
    "thesis", "reports\generated\exp001", "reports\generated\exp002", "reports\generated\exp003",
    "reports\generated\evaluation_comparison"
) | ForEach-Object { Join-Path $repoRoot $_ } | Where-Object { Test-Path $_ }
$extents = @("*.py", "*.ps1", "*.md", "*.json", "*.csv")
# ignore everything the refresh writes (prevents feedback loops)
$ignore = 'visualization_agent|\\figures\\|catalog\.generated|compiled-memory|PROGRESS_TRACKER|results_dashboard|\.generated\.|__pycache__|\\.git\\|\\runs\\|\.watcher\.'

function Get-Fingerprint {
    $sb = New-Object System.Text.StringBuilder
    foreach ($root in $watchRoots) {
        Get-ChildItem -LiteralPath $root -Recurse -File -Include $extents -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch $ignore } |
            ForEach-Object { [void]$sb.Append($_.FullName).Append($_.LastWriteTimeUtc.Ticks).Append(';') }
    }
    return $sb.ToString()
}

$script:refreshProc = $null
$script:pending = $false
function Invoke-Refresh {
    # parallel / non-blocking, but COALESCED: never run two refreshes at once (avoids concurrent writes
    # to the tracker). If one is in flight, mark pending; the loop flushes it when the current one exits.
    if ($script:refreshProc -and -not $script:refreshProc.HasExited) { $script:pending = $true; return }
    $script:pending = $false
    $script:refreshProc = Start-Process -FilePath "pwsh" -WindowStyle Hidden -WorkingDirectory $repoRoot `
        -PassThru -ArgumentList @("-NoProfile", "-File", "$PSScriptRoot\refresh-tracking.ps1", "-Quiet", "-Viz")
}

function Write-Status($msg) {
    "$(Get-Date -Format o)  $msg" | Set-Content -LiteralPath $statusFile -Encoding utf8
}

# --- run ---------------------------------------------------------------------
if (Test-Path $stopFlag) { Remove-Item $stopFlag -Force -ErrorAction SilentlyContinue }
$last = Get-Fingerprint

if ($Once) {
    Invoke-Refresh
    Write-Status "ran one refresh (-Once)"
    Write-Host "watcher: triggered one parallel refresh."
    return
}

# Singleton: refuse to start a second watcher (prevents duplicate/concurrent refreshes).
$lockFile = Join-Path $stateDir ".watcher.lock"
if (Test-Path $lockFile) {
    $otherPid = (Get-Content $lockFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($otherPid -and (Get-Process -Id $otherPid -ErrorAction SilentlyContinue)) {
        Write-Host "watcher: another instance (PID $otherPid) is already running; exiting."
        return
    }
}
$PID | Set-Content -LiteralPath $lockFile -Encoding ascii

Write-Host "watcher: watching $($watchRoots.Count) source roots every $IntervalSeconds s. Stop with -Stop or Ctrl+C."
Write-Status "started; watching $($watchRoots.Count) roots (PID $PID)"
try {
    Invoke-Refresh   # initial refresh on start
    while ($true) {
        Start-Sleep -Seconds $IntervalSeconds
        if (Test-Path $stopFlag) { Write-Status "stopped via flag"; Remove-Item $stopFlag -Force -ErrorAction SilentlyContinue; break }
        $now = Get-Fingerprint
        if ($now -ne $last) {
            $last = $now
            Invoke-Refresh
            Write-Status "change detected -> refresh"
        } elseif ($script:pending -and $script:refreshProc -and $script:refreshProc.HasExited) {
            Invoke-Refresh   # flush a coalesced change after the previous refresh finished
            Write-Status "flushed pending refresh"
        } else {
            Write-Status "idle"
        }
    }
} finally {
    Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
}
Write-Host "watcher: stopped."
