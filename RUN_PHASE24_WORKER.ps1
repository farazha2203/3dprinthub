$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

Write-Host "Starting Phase 24 link analysis worker..." -ForegroundColor Cyan
& $python manage.py process_link_analysis_queue --watch --limit 3 --sleep 3
if ($LASTEXITCODE -ne 0) { throw "Phase 24 worker stopped with an error." }
