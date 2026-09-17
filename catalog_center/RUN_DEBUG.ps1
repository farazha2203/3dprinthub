Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "D:\projects\3DPrintHub\.venv\Scripts\python.exe"
$QtRunner = Join-Path $Root "RUN_QT.ps1"
$DataRoot = "D:\projects\3dprinthub-catalog-manager"
$LogDir = Join-Path $DataRoot "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Transcript = Join-Path $LogDir ("powershell-qt-debug-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".log")

Write-Host "=== 3DPrintHub Catalog Center Qt 6 DEBUG ===" -ForegroundColor Cyan
Write-Host "SOURCE_ROOT=$Root"
Write-Host "PYTHON=$Python"
Write-Host "TRANSCRIPT=$Transcript"
if (-not (Test-Path -LiteralPath $Python)) { throw "Python venv not found: $Python" }
if (-not (Test-Path -LiteralPath $QtRunner)) { throw "Qt operator launcher not found: $QtRunner" }

Start-Transcript -Path $Transcript -Force | Out-Null
$PreviousDebug = $env:CATALOG_DEBUG
Push-Location $Root
try {
    $env:CATALOG_DEBUG = "1"
    & $Python -m app.debug_cli --connections
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Connection preflight failed. The Qt UI will still start so settings can be corrected."
    }
    Write-Host "=== Starting Qt UI in foreground; Python/Qt errors are shown live below ===" -ForegroundColor Yellow
    & $QtRunner -Foreground
} catch {
    Write-Error ($_ | Out-String)
} finally {
    Pop-Location
    if ($null -eq $PreviousDebug) {
        Remove-Item Env:CATALOG_DEBUG -ErrorAction SilentlyContinue
    } else {
        $env:CATALOG_DEBUG = $PreviousDebug
    }
    Stop-Transcript | Out-Null
    Write-Host "QT_DEBUG_LOG=$Transcript"
}
