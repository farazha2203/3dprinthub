Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$PackageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Installer = Join-Path $PackageRoot "INSTALL_OR_UPGRADE.ps1"
$TargetRunner = "D:\projects\3dprinthub_catalog_center\RUN.ps1"

Write-Host "=== Installing 3DPrintHub Catalog Intelligence v8.5.4 ===" -ForegroundColor Cyan
& $Installer -PackageRoot $PackageRoot
if ($LASTEXITCODE -ne 0) { throw "v8.5.4 installation failed." }
if (-not (Test-Path $TargetRunner)) { throw "Installed runner not found: $TargetRunner" }

Write-Host "=== Launching verified v8.5.4 ===" -ForegroundColor Green
& $TargetRunner
