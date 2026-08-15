Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "D:\projects\3DPrintHub\.venv\Scripts\python.exe"
$Launcher = Join-Path $Root "launch.py"
if (-not (Test-Path $Python)) { throw "Python venv not found: $Python" }
if (-not (Test-Path $Launcher)) { throw "Absolute launcher not found: $Launcher" }
Write-Host "3DPrintHub Catalog Intelligence v8.5.4"
Write-Host "SOURCE_ROOT=$Root"
Write-Host "PYTHON=$Python"
$PreviousPythonPath = $env:PYTHONPATH
Push-Location $Root
try {
    $env:PYTHONPATH = $Root
    & $Python -m pip install --disable-pip-version-check -r "$Root\requirements.txt"
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed" }
    & $Python "$Root\launch.py" --verify-only
    if ($LASTEXITCODE -ne 0) { throw "Installed release verification failed" }
    & $Python "$Root\launch.py"
    if ($LASTEXITCODE -ne 0) { throw "Application exited with code $LASTEXITCODE" }
} finally {
    if ($null -eq $PreviousPythonPath) {
        Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    } else {
        $env:PYTHONPATH = $PreviousPythonPath
    }
    Pop-Location
}
