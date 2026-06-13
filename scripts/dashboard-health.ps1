[CmdletBinding()]
param(
    [string]$OutputDir = "docs\confluence\outbox",
    [switch]$RequireOutbox,
    [switch]$RequireLivePageIds
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$dashboardFiles = @(
    @{
        Path = "docs/dashboards/progress-dashboard.md"
        Heading = "# Progress Dashboard"
    },
    @{
        Path = "docs/dashboards/kpi-register.md"
        Heading = "# KPI Register"
    },
    @{
        Path = "docs/dashboards/results-dashboard.md"
        Heading = "# Results Dashboard"
    }
)

$requiredPageKeys = @("home", "currentState", "dashboard", "changelog", "researchOperations")
$requiredOutboxFiles = @(
    "vego-ai-wiki-home.md",
    "vego-ai-current-state.md",
    "vego-ai-progress-dashboard.md",
    "vego-ai-update-changelog.md",
    "vego-ai-research-operations.md"
)

function Read-JsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    try {
        return (Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json)
    }
    catch {
        throw "Invalid JSON in ${Path}: $($_.Exception.Message)"
    }
}

function Test-IgnoredByGit {
    param([Parameter(Mandatory = $true)][string]$RelativePath)

    & git -C $repoRoot check-ignore -q $RelativePath
    return ($LASTEXITCODE -eq 0)
}

Write-Host "VEGO-AI dashboard health"
Write-Host "Root: $repoRoot"
Write-Host ""

foreach ($dashboard in $dashboardFiles) {
    $path = Join-Path $repoRoot $dashboard.Path
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing dashboard source: $($dashboard.Path)"
    }
    $body = Get-Content -Raw -LiteralPath $path
    if (-not $body.StartsWith($dashboard.Heading)) {
        throw "Dashboard source $($dashboard.Path) must start with '$($dashboard.Heading)'."
    }
    Write-Host "[ok]      $($dashboard.Path)"
}

$kpiRegisterPath = Join-Path $repoRoot "docs/dashboards/kpi-register.md"
$kpiRegister = Get-Content -Raw -LiteralPath $kpiRegisterPath
foreach ($requiredKpi in @("Research spine clarity", "Test suite health", "Live Confluence sync")) {
    if ($kpiRegister -notmatch [regex]::Escape($requiredKpi)) {
        throw "KPI register is missing required KPI: $requiredKpi"
    }
}
Write-Host "[ok]      KPI register includes required tracking rows"

$builderPath = Join-Path $repoRoot "scripts/build-confluence-wiki.ps1"
$builder = Get-Content -Raw -LiteralPath $builderPath
foreach ($requiredBuilderText in @("docs/dashboards/progress-dashboard.md", "docs/dashboards/kpi-register.md", "docs/dashboards/results-dashboard.md", "vego-ai-progress-dashboard.md")) {
    if ($builder -notmatch [regex]::Escape($requiredBuilderText)) {
        throw "Confluence wiki builder is missing dashboard wiring: $requiredBuilderText"
    }
}
Write-Host "[ok]      Confluence wiki builder includes dashboard sources"

$templateRelative = "docs/confluence/wiki-sync-config.template.json"
$templatePath = Join-Path $repoRoot $templateRelative
$template = Read-JsonFile -Path $templatePath

foreach ($pageKey in $requiredPageKeys) {
    if (-not $template.pages.PSObject.Properties.Name.Contains($pageKey)) {
        throw "Confluence config template is missing pages.$pageKey"
    }
}
if ($template.pages.dashboard.outboxFile -ne "vego-ai-progress-dashboard.md") {
    throw "Confluence config template dashboard outboxFile must be vego-ai-progress-dashboard.md"
}
Write-Host "[ok]      Confluence config template includes dashboard page"

$localConfigRelative = "docs/confluence/wiki-sync-config.local.json"
$localConfigPath = Join-Path $repoRoot $localConfigRelative
$localConfig = $null
if (Test-Path -LiteralPath $localConfigPath) {
    $localConfig = Read-JsonFile -Path $localConfigPath
    if (-not (Test-IgnoredByGit -RelativePath $localConfigRelative)) {
        throw "Local Confluence sync config must be ignored by Git: $localConfigRelative"
    }
    foreach ($pageKey in $requiredPageKeys) {
        if (-not $localConfig.pages.PSObject.Properties.Name.Contains($pageKey)) {
            throw "Local Confluence config is missing pages.$pageKey"
        }
    }
    Write-Host "[ok]      Local Confluence config includes dashboard page and is ignored"

    if ($RequireLivePageIds) {
        $missingPageIds = @()
        foreach ($pageKey in $requiredPageKeys) {
            $pageId = $localConfig.pages.$pageKey.pageId
            if ([string]::IsNullOrWhiteSpace($pageId)) {
                $missingPageIds += $pageKey
            }
        }
        if ($missingPageIds.Count -gt 0) {
            throw "Local Confluence config is missing live page IDs for: $($missingPageIds -join ', ')"
        }
        Write-Host "[ok]      Local Confluence config has live page IDs for all curated pages"
    }
}
else {
    Write-Host "[info]    Local Confluence config not found; live sync IDs are not configured"
}

$outboxPath = Join-Path $repoRoot $OutputDir
if (Test-Path -LiteralPath $outboxPath) {
    foreach ($fileName in $requiredOutboxFiles) {
        $path = Join-Path $outboxPath $fileName
        if (-not (Test-Path -LiteralPath $path)) {
            throw "Generated Confluence outbox is missing: $fileName"
        }
    }

    $dashboardOutbox = Get-Content -Raw -LiteralPath (Join-Path $outboxPath "vego-ai-progress-dashboard.md")
    foreach ($section in @("## Progress Dashboard", "## KPI Register", "## Results Dashboard")) {
        if ($dashboardOutbox -notmatch [regex]::Escape($section)) {
            throw "Generated dashboard outbox is missing section: $section"
        }
    }
    Write-Host "[ok]      Confluence outbox includes dashboard page and required sections"
}
elseif ($RequireOutbox) {
    throw "Confluence outbox is required but was not found: $OutputDir"
}
else {
    Write-Host "[info]    Confluence outbox not generated yet"
}

Write-Host ""
Write-Host "Dashboard health check passed."
