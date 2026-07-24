# Unified, non-blocking tracking refresh for Claude AND Codex.
#
# Pull (prompt start):   .\scripts\refresh-tracking.ps1 -Pull   -> recompiles shared memory so the agent
#                                                                  reads current context.
# Update (prompt end):   .\scripts\refresh-tracking.ps1         -> recompiles memory + regenerates the
#                                                                  progress tracker AUTO regions + runs the
#                                                                  evidence-consistency guard.
#
# Safe by design: read-only over project data (only writes compiled-memory.md and PROGRESS_TRACKER.md AUTO
# regions), no API/LLM, no baseline/Agent-4 change. ALWAYS exits 0 so it can run as a hook without blocking.
[CmdletBinding()]
param([switch]$Pull, [switch]$Quiet, [switch]$Viz)

$ErrorActionPreference = "Continue"
$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
function Log($m) { if (-not $Quiet) { Write-Host $m } }

# 1) PULL: recompile shared memory (current-state, progress, session-log, review-state, etc.)
try {
    & (Join-Path $PSScriptRoot "agent-memory-start.ps1") *> $null
    Log "[refresh] compiled-memory refreshed"
} catch { Log "[refresh] memory compile skipped: $($_.Exception.Message)" }

if ($Pull) { exit 0 }

# 2) UPDATE: regenerate the executive progress tracker AUTO regions from live sources
try {
    python (Join-Path $repoRoot "scripts/build-progress-tracker.py") *> $null
    Log "[refresh] progress tracker refreshed"
} catch { Log "[refresh] tracker skipped: $($_.Exception.Message)" }

# 3) UPDATE: run the evidence-consistency guard (non-fatal; result is reflected in the tracker stamp)
try {
    python (Join-Path $repoRoot "scripts/check_evidence_consistency.py") *> $null
    Log "[refresh] evidence guard ran (exit $LASTEXITCODE)"
} catch { Log "[refresh] guard skipped: $($_.Exception.Message)" }

# 4) UPDATE (optional): visualization agent fast set (data-driven charts + catalog + report)
if ($Viz) {
    try {
        python (Join-Path $repoRoot "scripts/visualization_agent.py") *> $null
        Log "[refresh] visualization agent refreshed (fast set)"
    } catch { Log "[refresh] viz agent skipped: $($_.Exception.Message)" }
}

exit 0
