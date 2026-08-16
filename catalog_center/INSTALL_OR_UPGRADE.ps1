param(
    [string]$PackageRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($PackageRoot)) {
    $PackageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}
$Python = "D:\projects\3DPrintHub\.venv\Scripts\python.exe"
$Target = "D:\projects\3dprinthub_catalog_center"
$DataRoot = "D:\projects\3dprinthub-catalog-manager"
$BackupRoot = "D:\projects\3dprinthub-backups"
$UpgradeScript = Join-Path $PackageRoot "app\upgrade.py"
$VersionScript = Join-Path $PackageRoot "app\version.py"

if (-not (Test-Path $Python)) { throw "Python venv not found: $Python" }
if (-not (Test-Path $UpgradeScript)) { throw "Upgrade script not found: $UpgradeScript" }
if (-not (Test-Path $VersionScript)) { throw "Version script not found: $VersionScript" }

$VersionOutput = @(& $Python $VersionScript)
if ($LASTEXITCODE -ne 0) { throw "Unable to read package version from $VersionScript" }
$VersionLine = $VersionOutput | Where-Object { $_ -like "APP_VERSION=*" } | Select-Object -First 1
if ([string]::IsNullOrWhiteSpace($VersionLine)) { throw "APP_VERSION marker was not returned by $VersionScript" }
$ExpectedVersion = $VersionLine.Substring("APP_VERSION=".Length).Trim()
if ([string]::IsNullOrWhiteSpace($ExpectedVersion)) { throw "Package version is empty." }
$VersionMarker = $ExpectedVersion.Replace(".", "_")

$NeutralLocation = Split-Path -Parent $Target
Push-Location $NeutralLocation
try {
    & $Python $UpgradeScript --source $PackageRoot --target $Target --data-root $DataRoot --backup-root $BackupRoot
    if ($LASTEXITCODE -ne 0) { throw "v$ExpectedVersion source upgrade failed before verification." }
} finally {
    Pop-Location
}

try {
    & $Python -m pip install -r "$Target\requirements.txt"
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
    $PreviousPythonPath = $env:PYTHONPATH
    Push-Location $Target
    try {
        $env:PYTHONPATH = $Target
        & $Python -m compileall -q "$Target\app" "$Target\tests"
        if ($LASTEXITCODE -ne 0) { throw "Python compile verification failed." }
        & $Python -m unittest discover -s tests -p "test_*.py"
        if ($LASTEXITCODE -ne 0) { throw "Unit/contract verification failed." }
        $Launcher = Join-Path $Target "launch.py"
        $InstalledVersionOutput = @(& $Python $Launcher --verify-only)
        if ($LASTEXITCODE -ne 0) { throw "Installed launcher verification failed." }
        $InstalledVersionOutput | ForEach-Object { Write-Host $_ }
        if ($InstalledVersionOutput -notcontains "ACTIVE_VERSION=$ExpectedVersion") { throw "Wrong installed version. Expected $ExpectedVersion." }
        if ($InstalledVersionOutput -notcontains "ACTIVE_SOURCE=$Target") { throw "Wrong installed source path. Expected $Target." }
    } finally {
        if ($null -eq $PreviousPythonPath) { Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue } else { $env:PYTHONPATH = $PreviousPythonPath }
        Pop-Location
    }
} catch {
    Write-Warning "Verification failed. Restoring the previous application and SQLite backup."
    $RollbackScript = Join-Path $Target "app\upgrade.py"
    if (Test-Path $RollbackScript) { & $Python $RollbackScript --rollback --backup-root $BackupRoot }
    throw
}

Write-Host "INSTALL_PATH=$Target"
Write-Host "DATA_PATH=$DataRoot\catalog.sqlite3"
Write-Host "CATALOG_CENTER_V${VersionMarker}_READY=OK" -ForegroundColor Green
