[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$packDir = Join-Path $repoRoot "literature\hitl-resource-pack"
$manifestPath = Join-Path $packDir "source-manifest.csv"
$downloadsDir = Join-Path $packDir "downloads"

if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "Manifest not found: $manifestPath"
}

$allowedStatuses = @(
    "metadata_only",
    "downloaded_open_access"
)

$rows = @(Import-Csv -LiteralPath $manifestPath)
if ($rows.Count -eq 0) {
    throw "Manifest has no rows: $manifestPath"
}

Write-Host "VEGO-AI HITL resource downloader"
Write-Host "Manifest: $manifestPath"
Write-Host "DryRun: $DryRun"
Write-Host ""

if (-not $DryRun) {
    New-Item -ItemType Directory -Force -Path $downloadsDir | Out-Null
}

$downloaded = 0
$metadataOnly = 0
$skipped = 0

foreach ($row in $rows) {
    $id = $row.id
    $downloadUrl = $row.download_url
    $localPath = $row.local_path
    $status = $row.download_status

    if ($allowedStatuses -notcontains $status) {
        Write-Host "[skip] $id status=$status"
        $skipped++
        continue
    }

    if ([string]::IsNullOrWhiteSpace($downloadUrl) -or [string]::IsNullOrWhiteSpace($localPath)) {
        if ([string]::IsNullOrWhiteSpace($row.download_status) -or $row.download_status -eq "metadata_only") {
            $row.download_status = "metadata_only"
        }
        Write-Host "[meta] $id $($row.title)"
        $metadataOnly++
        continue
    }

    $targetPath = Join-Path $packDir $localPath
    $targetDir = Split-Path -Parent $targetPath

    if ($DryRun) {
        Write-Host "[dry]  $id -> $localPath"
        continue
    }

    New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

    if ((Test-Path -LiteralPath $targetPath) -and (-not $Force)) {
        Write-Host "[keep] $id $localPath"
    }
    else {
        Write-Host "[get]  $id $downloadUrl"
        Invoke-WebRequest `
            -Uri $downloadUrl `
            -OutFile $targetPath `
            -UseBasicParsing `
            -Headers @{ "User-Agent" = "VEGO-AI-HITL-Resource-Pack/1.0" }
    }

    $hash = (Get-FileHash -LiteralPath $targetPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $row.download_status = "downloaded_open_access"
    $row.local_path = $localPath
    $row.sha256 = $hash
    $downloaded++
}

if (-not $DryRun) {
    $rows | Export-Csv -LiteralPath $manifestPath -NoTypeInformation
}

Write-Host ""
Write-Host "Summary"
Write-Host "- downloaded/open: $downloaded"
Write-Host "- metadata-only: $metadataOnly"
Write-Host "- skipped: $skipped"
Write-Host ""
Write-Host "Downloaded files are expected to remain ignored under literature/hitl-resource-pack/downloads/."

