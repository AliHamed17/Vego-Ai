[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$requiredPaths = @(
    "docs/research/artifact-audit.md",
    "docs/research/provenance-register.md",
    "docs/research/publishability-register.md",
    "docs/confluence/wiki-sync.md",
    "docs/confluence/wiki-sync-config.template.json",
    "experiments/EXP-000-existing-packaged-results-audit/README.md",
    "experiments/EXP-000-existing-packaged-results-audit/config-manifest.md",
    "experiments/EXP-000-existing-packaged-results-audit/notes.md",
    "scripts/build-confluence-wiki.ps1"
)

$forbiddenTrackedPatterns = @(
    '(^|/)compiled-memory\.md$',
    '^\.claude/',
    '\.pdf$',
    '\.zip$',
    '\.exe$',
    '^VEGO-AI/models/',
    '^VEGO-AI/analysis/',
    '^VEGO-AI/eval_output/',
    '^VEGO-AI/human_review_output/',
    '^VEGO-AI/framework/get-pip\.py$',
    '^VEGO-AI/vego_visualizer_delivery/models/',
    '^VEGO-AI/vego_visualizer_delivery/compliance_vectors/',
    '^VEGO-AI/vego_visualizer_delivery/guidelines/',
    '^docs/confluence/outbox/'
)

Write-Host "VEGO-AI research health"
Write-Host "Root: $repoRoot"
Write-Host ""

$missing = @()
foreach ($relativePath in $requiredPaths) {
    $fullPath = Join-Path $repoRoot $relativePath
    if (Test-Path -LiteralPath $fullPath) {
        Write-Host "[ok]      $relativePath"
    }
    else {
        Write-Host "[missing] $relativePath"
        $missing += $relativePath
    }
}

$configPath = Join-Path $repoRoot "docs/confluence/wiki-sync-config.template.json"
if (Test-Path -LiteralPath $configPath) {
    try {
        Get-Content -Raw -LiteralPath $configPath | ConvertFrom-Json | Out-Null
        Write-Host "[ok]      Confluence config template parses as JSON"
    }
    catch {
        throw "Confluence config template is invalid JSON: $($_.Exception.Message)"
    }
}

$localConfigRelative = "docs/confluence/wiki-sync-config.local.json"
$localConfigPath = Join-Path $repoRoot $localConfigRelative
if (Test-Path -LiteralPath $localConfigPath) {
    try {
        Get-Content -Raw -LiteralPath $localConfigPath | ConvertFrom-Json | Out-Null
        Write-Host "[ok]      Local Confluence config parses as JSON"
    }
    catch {
        throw "Local Confluence config is invalid JSON: $($_.Exception.Message)"
    }

    & git -C $repoRoot check-ignore -q $localConfigRelative
    if ($LASTEXITCODE -ne 0) {
        throw "Local Confluence config must be ignored by Git: $localConfigRelative"
    }
    Write-Host "[ok]      Local Confluence config is ignored by Git"
}

$registryPath = Join-Path $repoRoot "experiments/registry.md"
$registry = Get-Content -Raw -LiteralPath $registryPath
$experimentIds = [regex]::Matches($registry, '\|\s*(EXP-[A-Za-z0-9-]+)\s*\|') |
    ForEach-Object { $_.Groups[1].Value } |
    Where-Object { $_ -ne "ID" } |
    Sort-Object -Unique

foreach ($experimentId in $experimentIds) {
    $matches = Get-ChildItem -LiteralPath (Join-Path $repoRoot "experiments") -Directory |
        Where-Object { $_.Name -eq $experimentId -or $_.Name.StartsWith("$experimentId-") }
    if ($matches.Count -gt 0) {
        Write-Host "[ok]      Experiment folder for $experimentId"
    }
    else {
        throw "Experiment registry references $experimentId but no matching folder exists."
    }
}

$tracked = & git -C $repoRoot ls-tree -r --name-only HEAD
if ($LASTEXITCODE -ne 0) {
    throw "Unable to list tracked files."
}

$forbidden = @()
foreach ($path in $tracked) {
    foreach ($pattern in $forbiddenTrackedPatterns) {
        if ($path -match $pattern) {
            $forbidden += $path
            break
        }
    }
}

if ($forbidden.Count -gt 0) {
    throw "Forbidden tracked artifacts found: $($forbidden -join ', ')"
}
Write-Host "[ok]      No forbidden tracked artifacts detected"

$outboxPath = Join-Path $repoRoot "docs/confluence/outbox"
if (Test-Path -LiteralPath $outboxPath) {
    $outboxFiles = Get-ChildItem -LiteralPath $outboxPath -Filter "*.md" -File
    foreach ($file in $outboxFiles) {
        $body = Get-Content -Raw -LiteralPath $file.FullName
        foreach ($pattern in @(
            'VEGO-AI/models/',
            'VEGO-AI/analysis/',
            'VEGO-AI/eval_output/',
            'VEGO-AI/human_review_output/',
            'Variability_MAS4MODELS',
            '\.pdf',
            '\.zip',
            '\.exe'
        )) {
            if ($body -match $pattern) {
                throw "Generated wiki outbox mentions forbidden sensitive path/pattern '$pattern' in $($file.Name)."
            }
        }
    }
    Write-Host "[ok]      Generated wiki outbox avoids forbidden sensitive path patterns"
}
else {
    Write-Host "[info]    Confluence outbox not generated yet"
}

if ($missing.Count -gt 0) {
    throw "Research health failed. Missing paths: $($missing -join ', ')"
}

Write-Host ""
Write-Host "Research health check passed."
