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

$snapshotRelative = "docs/dashboards/status-snapshot.generated.md"
$visualMarkdownRelative = "docs/dashboards/progress-visualizations.generated.md"
$visualHtmlRelative = "docs/dashboards/progress-visualizations.generated.html"
$e2eMarkdownRelative = "docs/dashboards/e2e-dashboard.generated.md"
$e2eHtmlRelative = "reports/generated/e2e_dashboard/index.html"
$manualSyncPackRelative = "docs/confluence/manual-sync-pack.generated.md"
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

$snapshotPath = Join-Path $repoRoot $snapshotRelative
if (Test-Path -LiteralPath $snapshotPath) {
    $snapshot = Get-Content -Raw -LiteralPath $snapshotPath
    if (-not $snapshot.StartsWith("# Dashboard Status Snapshot")) {
        throw "Generated dashboard snapshot must start with '# Dashboard Status Snapshot'."
    }
    if (-not (Test-IgnoredByGit -RelativePath $snapshotRelative)) {
        throw "Generated dashboard snapshot must be ignored by Git: $snapshotRelative"
    }
    Write-Host "[ok]      Generated dashboard status snapshot exists and is ignored"
}
elseif ($RequireOutbox) {
    throw "Generated dashboard status snapshot is required but missing: $snapshotRelative"
}
else {
    Write-Host "[info]    Generated dashboard status snapshot not generated yet"
}

$builderPath = Join-Path $repoRoot "scripts/build-confluence-wiki.ps1"
$builder = Get-Content -Raw -LiteralPath $builderPath
foreach ($requiredBuilderText in @("docs/dashboards/progress-dashboard.md", "docs/dashboards/kpi-register.md", "docs/dashboards/results-dashboard.md", "build-dashboard-snapshot.ps1", "status-snapshot.generated.md", "build-progress-visualizations.ps1", "progress-visualizations.generated.md", "build-e2e-progress-report.ps1", "e2e-dashboard.generated.md", "reports\generated\e2e_dashboard\index.html", "build-confluence-manual-sync-pack.ps1", "manual-sync-pack.generated.md", "vego-ai-progress-dashboard.md")) {
    if ($builder -notmatch [regex]::Escape($requiredBuilderText)) {
        throw "Confluence wiki builder is missing dashboard wiring: $requiredBuilderText"
    }
}
Write-Host "[ok]      Confluence wiki builder includes dashboard sources"

$visualMarkdownPath = Join-Path $repoRoot $visualMarkdownRelative
if (Test-Path -LiteralPath $visualMarkdownPath) {
    $visualMarkdown = Get-Content -Raw -LiteralPath $visualMarkdownPath
    if (-not $visualMarkdown.StartsWith("# Progress Visualizations")) {
        throw "Generated progress visualizations markdown must start with '# Progress Visualizations'."
    }
    if (-not (Test-IgnoredByGit -RelativePath $visualMarkdownRelative)) {
        throw "Generated progress visualizations markdown must be ignored by Git: $visualMarkdownRelative"
    }
    Write-Host "[ok]      Generated progress visualization markdown exists and is ignored"
}

$visualHtmlPath = Join-Path $repoRoot $visualHtmlRelative
if (Test-Path -LiteralPath $visualHtmlPath) {
    $visualHtml = Get-Content -Raw -LiteralPath $visualHtmlPath
    if ($visualHtml -notmatch "<title>VEGO-AI Progress Visualizations</title>") {
        throw "Generated progress visualization HTML is missing the expected title."
    }
    if (-not (Test-IgnoredByGit -RelativePath $visualHtmlRelative)) {
        throw "Generated progress visualization HTML must be ignored by Git: $visualHtmlRelative"
    }
    Write-Host "[ok]      Generated progress visualization HTML exists and is ignored"
}

$e2eMarkdownPath = Join-Path $repoRoot $e2eMarkdownRelative
if (Test-Path -LiteralPath $e2eMarkdownPath) {
    $e2eMarkdown = Get-Content -Raw -LiteralPath $e2eMarkdownPath
    if (-not $e2eMarkdown.StartsWith("# VEGO-AI E2E Progress Report")) {
        throw "Generated E2E dashboard markdown must start with '# VEGO-AI E2E Progress Report'."
    }
    if (-not (Test-IgnoredByGit -RelativePath $e2eMarkdownRelative)) {
        throw "Generated E2E dashboard markdown must be ignored by Git: $e2eMarkdownRelative"
    }
    Write-Host "[ok]      Generated E2E dashboard markdown exists and is ignored"
}
elseif ($RequireOutbox) {
    throw "Generated E2E dashboard markdown is required but missing: $e2eMarkdownRelative"
}

$e2eHtmlPath = Join-Path $repoRoot $e2eHtmlRelative
if (Test-Path -LiteralPath $e2eHtmlPath) {
    $e2eHtml = Get-Content -Raw -LiteralPath $e2eHtmlPath
    if ($e2eHtml -notmatch "<title>VEGO-AI E2E Progress Report</title>") {
        throw "Generated E2E dashboard HTML is missing the expected title."
    }
    if (-not (Test-IgnoredByGit -RelativePath $e2eHtmlRelative)) {
        throw "Generated E2E dashboard HTML must be ignored by Git: $e2eHtmlRelative"
    }
    Write-Host "[ok]      Generated E2E dashboard HTML exists and is ignored"
}
elseif ($RequireOutbox) {
    throw "Generated E2E dashboard HTML is required but missing: $e2eHtmlRelative"
}

$manualPackPath = Join-Path $repoRoot $manualSyncPackRelative
if (Test-Path -LiteralPath $manualPackPath) {
    $manualPack = Get-Content -Raw -LiteralPath $manualPackPath
    foreach ($requiredText in @("# Confluence Manual Sync Pack", "VEGO-AI Wiki Home", "VEGO-AI Progress Dashboard", "SHA-256")) {
        if ($manualPack -notmatch [regex]::Escape($requiredText)) {
            throw "Generated manual sync pack is missing required text: $requiredText"
        }
    }
    if (-not (Test-IgnoredByGit -RelativePath $manualSyncPackRelative)) {
        throw "Generated manual sync pack must be ignored by Git: $manualSyncPackRelative"
    }
    Write-Host "[ok]      Generated Confluence manual sync pack exists and is ignored"
}
elseif ($RequireOutbox) {
    throw "Generated Confluence manual sync pack is required but missing: $manualSyncPackRelative"
}
else {
    Write-Host "[info]    Generated Confluence manual sync pack not generated yet"
}

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
    foreach ($section in @("## Status Snapshot", "# Dashboard Status Snapshot", "## Progress Dashboard", "## Progress Visualizations", "## E2E Progress Report", "# VEGO-AI E2E Progress Report", "## KPI Register", "## Results Dashboard")) {
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
