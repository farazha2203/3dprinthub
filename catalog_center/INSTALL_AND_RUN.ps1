Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$PackageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Installer = Join-Path $PackageRoot "INSTALL_OR_UPGRADE.ps1"
$TargetRunner = "D:\projects\3dprinthub_catalog_center\RUN.ps1"

Write-Host "=== Installing 3DPrintHub Catalog Center Qt 6 ===" -ForegroundColor Cyan
& $Installer -PackageRoot $PackageRoot
if ($LASTEXITCODE -ne 0) { throw "Catalog Center Qt installation failed." }
if (-not (Test-Path $TargetRunner)) { throw "Installed runner not found: $TargetRunner" }

Write-Host "=== Launching verified Qt 6 Catalog Center ===" -ForegroundColor Green
& $TargetRunner
