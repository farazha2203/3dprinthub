param([string]$HostMirror = "D:\projects\3dprinthub-houst")
$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$Source=Join-Path $Root "server\store\management\commands\phase37_import_catalog_center.py"
$Target=Join-Path $HostMirror "store\management\commands\phase37_import_catalog_center.py"
if (-not (Test-Path $HostMirror)) { throw "Host mirror not found: $HostMirror" }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Target) | Out-Null
if (Test-Path $Target) {
    $backup="$Target.backup_v84_$(Get-Date -Format yyyyMMdd_HHmmss)"
    Copy-Item -LiteralPath $Target -Destination $backup -Force
    Write-Host "BACKUP=$backup"
}
Copy-Item -LiteralPath $Source -Destination $Target -Force
& "D:\projects\3DPrintHub\.venv\Scripts\python.exe" -m py_compile $Target
if ($LASTEXITCODE -ne 0) { throw "Server importer py_compile failed" }
Write-Host "CATALOG_INTELLIGENCE_V8_4_SERVER_COMMAND_TO_MIRROR=OK"
