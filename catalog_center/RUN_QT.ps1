param(
    [switch]$VerifyOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "D:\projects\3DPrintHub\.venv\Scripts\python.exe"
$Pythonw = "D:\projects\3DPrintHub\.venv\Scripts\pythonw.exe"
$Launcher = Join-Path $Root "qt_launch.py"
$DataRoot = "D:\projects\3dprinthub-catalog-manager"

if (-not (Test-Path -LiteralPath $Python)) { throw "Python venv not found: $Python" }
if (-not (Test-Path -LiteralPath $Launcher)) { throw "Qt launcher not found: $Launcher" }
if (-not (Test-Path -LiteralPath (Join-Path $DataRoot "catalog.sqlite3"))) { throw "Catalog SQLite not found under: $DataRoot" }

$PreviousPythonPath = $env:PYTHONPATH
$PreviousDataRoot = $env:CATALOG_DATA_ROOT

Push-Location $Root
try {
    $env:PYTHONPATH = $Root
    $env:CATALOG_DATA_ROOT = $DataRoot

    Write-Host "3DPrintHub Catalog Center - Qt 6" -ForegroundColor Cyan
    Write-Host "SOURCE_ROOT=$Root"
    Write-Host "CATALOG_DATA_ROOT=$DataRoot"
    Write-Host "LAUNCHER=$Launcher"

    & $Python $Launcher --verify-only
    if ($LASTEXITCODE -ne 0) { throw "Qt release verification failed with code $LASTEXITCODE" }

    if ($VerifyOnly) {
        Write-Host "QT_OPERATOR_LAUNCHER_VERIFY=PASS" -ForegroundColor Green
        return
    }

    if (Test-Path -LiteralPath $Pythonw) {
        Start-Process -FilePath $Pythonw -ArgumentList @($Launcher) -WorkingDirectory $Root
    } else {
        Start-Process -FilePath $Python -ArgumentList @($Launcher) -WorkingDirectory $Root
    }
    Write-Host "QT_CATALOG_CENTER_LAUNCHED=YES" -ForegroundColor Green
} finally {
    if ($null -eq $PreviousPythonPath) {
        Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    } else {
        $env:PYTHONPATH = $PreviousPythonPath
    }

    if ($null -eq $PreviousDataRoot) {
        Remove-Item Env:CATALOG_DATA_ROOT -ErrorAction SilentlyContinue
    } else {
        $env:CATALOG_DATA_ROOT = $PreviousDataRoot
    }
    Pop-Location
}
