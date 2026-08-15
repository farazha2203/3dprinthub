$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "D:\projects\3DPrintHub\.venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    $Python = "python"
}

Write-Host "=== Verify Phase43.1 datafix package ==="
& $Python (Join-Path $Root "VERIFY_PACKAGE.py")
if ($LASTEXITCODE -ne 0) {
    throw "Package verification failed."
}

$ServerZip = Join-Path $Root "3dprinthub_phase43_catalog_metrics_datafix_v43_1_0_server.zip"
if (-not (Test-Path -LiteralPath $ServerZip -PathType Leaf)) {
    throw "Server ZIP missing: $ServerZip"
}

Write-Host ""
Write-Host "PACKAGE_READY=OK"
Write-Host "UPLOAD_TO_SERVER=$ServerZip"
Write-Host ""
Write-Host "Production root: /home/sfkilvrs/3dprinthub"
