[CmdletBinding()]
param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$venv = Join-Path $root ".venv"

if (-not (Test-Path -LiteralPath $venv)) {
    & $Python -m venv $venv
}

$pip = Join-Path $venv "Scripts\pip.exe"
& $pip install --upgrade pip
& $pip install -r (Join-Path $root "VEGO-AI\framework\requirements.txt")
& $pip install -r (Join-Path $root "requirements-dev.txt")

Write-Host "Python environment ready: $venv"

