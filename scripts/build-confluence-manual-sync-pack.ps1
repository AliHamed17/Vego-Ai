[CmdletBinding()]
param(
    [string]$OutboxDir = "docs\confluence\outbox",
    [string]$OutputPath = "docs\confluence\manual-sync-pack.generated.md",
    [string]$ConfigPath = "docs\confluence\wiki-sync-config.local.json"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$outboxPath = Join-Path $repoRoot $OutboxDir
$outputFullPath = Join-Path $repoRoot $OutputPath
$configFullPath = Join-Path $repoRoot $ConfigPath
$generated = Get-Date -Format "yyyy-MM-dd HH:mm zzz"

function Get-FileSha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Read-JsonOrNull {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }
    return (Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json)
}

function Read-TextOrMissing {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (Test-Path -LiteralPath $Path) {
        return (Get-Content -Raw -LiteralPath $Path)
    }
    return "_Missing file: $Path_"
}

$config = Read-JsonOrNull -Path $configFullPath
if ($null -eq $config) {
    $templatePath = Join-Path $repoRoot "docs\confluence\wiki-sync-config.template.json"
    $config = Read-JsonOrNull -Path $templatePath
}

if ($null -eq $config) {
    throw "No Confluence sync config found."
}

$pageOrder = @("home", "currentState", "dashboard", "changelog", "researchOperations")
$rows = @()
$sections = @()

foreach ($pageKey in $pageOrder) {
    $page = $config.pages.$pageKey
    if ($null -eq $page) {
        throw "Confluence config is missing pages.$pageKey."
    }

    $fileName = $page.outboxFile
    $outboxFilePath = Join-Path $outboxPath $fileName
    $state = if (Test-Path -LiteralPath $outboxFilePath) { "Ready" } else { "Missing" }
    $sha = if ($state -eq "Ready") { Get-FileSha256 -Path $outboxFilePath } else { "n/a" }
    $pageId = if ([string]::IsNullOrWhiteSpace($page.pageId)) { "pending" } else { $page.pageId }

    $rows += "| $pageKey | $($page.title) | $pageId | $fileName | $state | $sha |"

    $body = Read-TextOrMissing -Path $outboxFilePath
    $sections += @"

## $($page.title)

| Field | Value |
| --- | --- |
| Config key | $pageKey |
| Page ID | $pageId |
| Outbox file | $fileName |
| SHA-256 | $sha |

~~~markdown
$body
~~~
"@
}

$siteUrl = if ($config.siteUrl) { $config.siteUrl } else { $config.cloudId }
$parentId = if ($config.parentId) { $config.parentId } else { "pending" }
$cloudId = if ($config.cloudId) { $config.cloudId } else { "pending" }
$spaceId = if ($config.spaceId) { $config.spaceId } else { "pending" }
$contentFormat = if ($config.contentFormat) { $config.contentFormat } else { "markdown" }

$body = @"
# Confluence Manual Sync Pack

Generated: $generated.

This generated pack is for manual or browser-assisted Confluence publishing when Atlassian Rovo live access is unavailable. It is ignored by Git and contains only curated/sanitized wiki outbox content.

## Target

| Field | Value |
| --- | --- |
| Site URL | $siteUrl |
| Cloud ID | $cloudId |
| Space ID/key | $spaceId |
| Parent page ID | $parentId |
| Content format | $contentFormat |

## Page Inventory

| Key | Title | Page ID | Outbox File | State | SHA-256 |
| --- | --- | --- | --- | --- | --- |
$($rows -join "`n")

## Sync Notes

- Update the home page first, then create or update the four child pages under parent page $parentId.
- Use the page titles exactly as shown in the inventory.
- After live pages are created, store child page IDs only in `docs/confluence/wiki-sync-config.local.json`.
- Do not commit this generated pack, the outbox, or the local config.

$($sections -join "`n")
"@

New-Item -ItemType Directory -Path (Split-Path -Parent $outputFullPath) -Force | Out-Null
Set-Content -LiteralPath $outputFullPath -Value $body -Encoding UTF8
Write-Host "Confluence manual sync pack generated: $outputFullPath"
