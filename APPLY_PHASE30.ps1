param(
    [switch]$SkipDependencyInstall,
    [switch]$SkipFullTests,
    [switch]$ProductionAudit
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Invoke-Python {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    & python @Arguments
    if ($LASTEXITCODE -ne 0) {
        $ExitCode = $LASTEXITCODE
        throw ("Python command failed with exit code {0}: {1}" -f $ExitCode, ($Arguments -join " "))
    }
}

Write-Host "[1/9] Validating Phase 30 files..."
Invoke-Python scripts/verify_phase30.py

Write-Host "[2/9] Installing locked dependencies..."
if (-not $SkipDependencyInstall) {
    Invoke-Python -m pip install -r requirements.txt
} else {
    Write-Host "Dependency installation skipped."
}

Write-Host "[3/9] Resolving existing Phase 29 migration branches..."
if (Test-Path "scripts/ensure_phase29_migration_merge.py") {
    Invoke-Python scripts/ensure_phase29_migration_merge.py
}

Write-Host "[4/9] Applying migrations and checking model state..."
Invoke-Python manage.py migrate
Invoke-Python manage.py makemigrations --check --dry-run

Write-Host "[5/9] Collecting static assets..."
Invoke-Python manage.py collectstatic --noinput

Write-Host "[6/9] Running Django checks..."
Invoke-Python manage.py check

Write-Host "[7/9] Running Phase 30 and payment regression tests..."
Invoke-Python manage.py test website.test_phase30_online_payment website.test_phase30_zarinpal_provider website.test_phase28_payment store.test_phase28 store.test_phase29 --keepdb

Write-Host "[8/9] Running full project test suite..."
if (-not $SkipFullTests) {
    Invoke-Python manage.py test --keepdb
} else {
    Write-Host "Full test suite skipped by request."
}

Write-Host "[9/9] Running payment and deployment audits..."
Invoke-Python manage.py phase30_payment_audit
Invoke-Python scripts/verify_phase30.py
if ($ProductionAudit) {
    Invoke-Python manage.py check --deploy
    Invoke-Python manage.py phase30_payment_audit --strict
    Invoke-Python manage.py deployment_readiness_check --strict
}

Write-Host "Phase 30 installed successfully."
Write-Host "Keep PAYMENT_GATEWAY_ENABLED=0 until sandbox and callback tests pass."
