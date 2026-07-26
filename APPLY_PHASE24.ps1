$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

function Invoke-Python {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    & $python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $($Arguments -join ' ')"
    }
}

Write-Host "[1/7] Installing locked dependencies..." -ForegroundColor Cyan
Invoke-Python -m pip install -r requirements.txt

Write-Host "[2/7] Applying database migrations..." -ForegroundColor Cyan
Invoke-Python manage.py migrate --noinput

Write-Host "[3/7] Collecting static files..." -ForegroundColor Cyan
Invoke-Python manage.py collectstatic --noinput

Write-Host "[4/7] Running Django system checks..." -ForegroundColor Cyan
Invoke-Python manage.py check

Write-Host "[5/7] Running Phase 23 and Phase 24 tests..." -ForegroundColor Cyan
Invoke-Python manage.py test store.test_phase23 store.test_phase24 store.test_phase9 store.test_phase10 --keepdb

Write-Host "[6/7] Running queue audit..." -ForegroundColor Cyan
Invoke-Python manage.py phase24_link_queue_audit

Write-Host "[7/7] Verifying package structure..." -ForegroundColor Cyan
Invoke-Python scripts/verify_phase24_link_queue.py

Write-Host "Phase 24 installed successfully." -ForegroundColor Green
Write-Host "Start the worker in a second terminal with RUN_PHASE24_WORKER.ps1." -ForegroundColor Green
