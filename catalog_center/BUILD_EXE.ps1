$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$PreferredPython = "D:\projects\3DPrintHub\.venv\Scripts\python.exe"
$Python = if (Test-Path -LiteralPath $PreferredPython) { $PreferredPython } else { (Get-Command python -ErrorAction Stop).Source }

Set-Location $Root

& $Python -m pip install -r "$Root\requirements.txt"
if ($LASTEXITCODE -ne 0) { throw "Requirements install failed: $LASTEXITCODE" }

& $Python "$Root\build_portable_exe.py" --python $Python
if ($LASTEXITCODE -ne 0) { throw "Portable EXE build failed: $LASTEXITCODE" }

Write-Host "PORTABLE_MODE=SINGLE_FILE"
Write-Host "INSTALLER_REQUIRED=NO"
Write-Host "TARGET_PYTHON_REQUIRED=NO"
Write-Host "PORTABLE_DATA_FOLDER=3DPrintHub-CatalogCenter-Data"
Write-Host "BUILD_EXE=OK"
