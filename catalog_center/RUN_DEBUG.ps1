Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "D:\projects\3DPrintHub\.venv\Scripts\python.exe"
$Launcher = Join-Path $Root "launch.py"
$DataRoot = "D:\projects\3dprinthub-catalog-manager"
$LogDir = Join-Path $DataRoot "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Transcript = Join-Path $LogDir ("powershell-debug-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".log")

Write-Host "=== 3DPrintHub Catalog Intelligence v8.5.4 DEBUG ===" -ForegroundColor Cyan
Write-Host "SOURCE_ROOT=$Root"
Write-Host "PYTHON=$Python"
Write-Host "TRANSCRIPT=$Transcript"
if (-not (Test-Path $Python)) { throw "Python venv not found: $Python" }
if (-not (Test-Path $Launcher)) { throw "Absolute launcher not found: $Launcher" }

Start-Transcript -Path $Transcript -Force | Out-Null
$PreviousPythonPath = $env:PYTHONPATH
Push-Location $Root
try {
    $env:PYTHONPATH = $Root
    $env:CATALOG_DEBUG = "1"
    & $Python -m app.debug_cli --connections
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Connection preflight failed. The UI will still start so settings can be corrected."
    }
    Write-Host "=== Starting UI; Python errors are shown live below ===" -ForegroundColor Yellow
    & $Python "$Root\launch.py" --debug
    if ($LASTEXITCODE -ne 0) { Write-Error "Application exited with code $LASTEXITCODE" }
} catch {
    Write-Error ($_ | Out-String)
} finally {
    if ($null -eq $PreviousPythonPath) {
        Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    } else {
        $env:PYTHONPATH = $PreviousPythonPath
    }
    Pop-Location
    Stop-Transcript | Out-Null
    Write-Host "DEBUG_LOG=$Transcript"
}
