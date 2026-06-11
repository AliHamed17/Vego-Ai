[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$requiredPaths = @(
    "README.md",
    "PROJECT_CHARTER.md",
    "AGENTS.md",
    "CLAUDE.md",
    "docs/agent-memory/current-state.md",
    "docs/agent-memory/progress.md",
    "docs/architecture/project-map.md",
    "docs/research/research-plan.md",
    "experiments/registry.md",
    "VEGO-AI/README.md"
)

Write-Host "VEGO-AI project health"
Write-Host "Root: $root"
Write-Host ""

$missing = @()
foreach ($relativePath in $requiredPaths) {
    $fullPath = Join-Path $root $relativePath
    if (Test-Path -LiteralPath $fullPath) {
        Write-Host "[ok]      $relativePath"
    }
    else {
        Write-Host "[missing] $relativePath"
        $missing += $relativePath
    }
}

Write-Host ""
try {
    $gitStatus = & git -C $root status --short 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[ok] Git repository detected"
        if ($gitStatus) {
            Write-Host "Git has pending changes/untracked files."
        }
        else {
            Write-Host "Git working tree is clean."
        }
    }
    else {
        Write-Host "[warn] Git status failed: $($gitStatus -join ' ')"
    }
}
catch {
    Write-Host "[warn] Git check failed: $($_.Exception.Message)"
}

if ($missing.Count -gt 0) {
    throw "Project health failed. Missing paths: $($missing -join ', ')"
}

Write-Host ""
Write-Host "Project health check passed."

