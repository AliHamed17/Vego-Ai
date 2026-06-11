[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Slug,

    [Parameter(Mandatory = $true)]
    [string]$Title,

    [string]$ResearchQuestion = "Unknown"
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$safeSlug = ($Slug.ToLowerInvariant() -replace "[^a-z0-9]+", "-").Trim("-")
if ([string]::IsNullOrWhiteSpace($safeSlug)) {
    throw "Slug must contain at least one letter or number."
}

$date = Get-Date -Format "yyyyMMdd"
$experimentId = "EXP-$date-$safeSlug"
$experimentDir = Join-Path $root "experiments\$experimentId"

if (Test-Path -LiteralPath $experimentDir) {
    throw "Experiment already exists: $experimentDir"
}

New-Item -ItemType Directory -Path $experimentDir | Out-Null

$readme = @"
# $experimentId - $Title

## Metadata

- Experiment ID: $experimentId
- Title: $Title
- Status: planned
- Research question: $ResearchQuestion
- Date created: $(Get-Date -Format "yyyy-MM-dd")

## Purpose

Describe what this experiment is meant to prove, compare, or inspect.

## Commands

```powershell
# Add exact commands here.
```

## Inputs

## Outputs

## Results

## Interpretation

## Limitations

## Reproducibility
"@

Set-Content -LiteralPath (Join-Path $experimentDir "README.md") -Value $readme -Encoding UTF8
Set-Content -LiteralPath (Join-Path $experimentDir "notes.md") -Value "# Notes`n" -Encoding UTF8
Set-Content -LiteralPath (Join-Path $experimentDir "config-manifest.md") -Value "# Config Manifest`n" -Encoding UTF8

Write-Host "Created experiment: $experimentId"
Write-Host "Folder: $experimentDir"
Write-Host "Add it to experiments/registry.md before running."

