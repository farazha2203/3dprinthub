param(
    [switch]$LaunchApp
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = "D:\projects\3DPrintHub"
$Catalog = Join-Path $Root "catalog_center"
$Py = Join-Path $Root ".venv\Scripts\python.exe"
$BaseGate = Join-Path $Root "RUN_PHASE49_3I_LOCAL_GATE.ps1"
$Branch = "epic/phase49-unified-product-slider-sync"
$RemoteRef = "origin/$Branch"

function Fail([string]$Message) {
    Write-Host ""
    Write-Host "PHASE49.3I.14 HOTFIX GATE FAILED" -ForegroundColor Red
    Write-Host $Message -ForegroundColor Red
    throw $Message
}

function Run-Native {
    param(
        [Parameter(Mandatory=$true)][string]$File,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )
    & $File @Arguments
    if ($LASTEXITCODE -ne 0) {
        Fail "Command failed ($LASTEXITCODE): $File $($Arguments -join ' ')"
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "PHASE49.3I.14 LEGACY SCAN RESTORE + SINGLE PRODUCT RECOVERY" -ForegroundColor Cyan
Write-Host "NO RESET / NO STASH / NO DELETE / NO PRODUCTION" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

if (-not (Test-Path $Root)) { Fail "Project root missing: $Root" }
if (-not (Test-Path $Catalog)) { Fail "Catalog Center missing: $Catalog" }
if (-not (Test-Path $Py)) { Fail "Virtualenv Python missing: $Py" }
if (-not (Test-Path $BaseGate)) { Fail "Base Phase49.3I gate missing: $BaseGate" }

Push-Location $Root
try {
    $dirty = @(git status --porcelain --untracked-files=all)
    if ($dirty.Count -gt 0) {
        $dirty | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
        Fail "Local worktree is not clean. Inspect it; do not reset/stash/delete as a shortcut."
    }

    $currentBranch = (git branch --show-current).Trim()
    if ($currentBranch -ne $Branch) {
        Fail "Wrong branch. Expected $Branch but found $currentBranch"
    }

    Run-Native -File "git" -Arguments @("fetch", "--prune", "origin")
    $localHead = (git rev-parse HEAD).Trim()
    $remoteHead = (git rev-parse $RemoteRef).Trim()
    Write-Host "LOCAL_HEAD  = $localHead"
    Write-Host "REMOTE_HEAD = $remoteHead"
    if ($localHead -ne $remoteHead) {
        Fail "Local HEAD does not match fetched GitHub HEAD. Pull with --ff-only and rerun."
    }
    Write-Host "PHASE49_3I14_GIT_SNAPSHOT=OK" -ForegroundColor Green
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "=== BASE PHASE49.3I GATE ===" -ForegroundColor Cyan
& $BaseGate
if ($LASTEXITCODE -ne 0) {
    Fail "Base Phase49.3I gate failed."
}

Write-Host ""
Write-Host "=== PHASE49.3I.14 COMPILE ===" -ForegroundColor Cyan
Push-Location $Root
try {
    Run-Native -File $Py -Arguments @(
        "-m", "compileall", "-q",
        "catalog_center\app\phase49_3i14_legacy_scan_restore.py",
        "catalog_center\app\phase49_3i12_runtime_bridge.py",
        "catalog_center\tests\test_epic49_phase49_3i14_legacy_scan_restore.py"
    )
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "=== PHASE49.3I.14 TEST ===" -ForegroundColor Cyan
Push-Location $Catalog
try {
    Run-Native -File $Py -Arguments @(
        "-m", "unittest", "-v",
        "tests.test_epic49_phase49_3i14_legacy_scan_restore"
    )
} finally {
    Pop-Location
}

Write-Host "PHASE49_3I14_LEGACY_TOP_SCAN=RESTORED" -ForegroundColor Green
Write-Host "PHASE49_3I14_SINGLE_PRODUCT_ROUTE=MATURE_BASE_SCAN" -ForegroundColor Green
Write-Host "PHASE49_3I14_NEW_PREVIEW_APPROVE_UI=PRESERVED" -ForegroundColor Green
Write-Host "PHASE49_3I14_DIRECT_SMART_LINK_OPTION=PRESERVED" -ForegroundColor Green
Write-Host "PHASE49_3I14_PRODUCTION=UNTOUCHED" -ForegroundColor Yellow

Push-Location $Root
try {
    $dirtyAfter = @(git status --porcelain --untracked-files=all)
    if ($dirtyAfter.Count -gt 0) {
        $dirtyAfter | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
        Fail "Tests left the Local worktree dirty."
    }
    Write-Host "FINAL_HEAD = $((git rev-parse HEAD).Trim())" -ForegroundColor Green
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "PHASE49.3I.14 HOTFIX GATE PASSED" -ForegroundColor Green

if ($LaunchApp) {
    Start-Process -FilePath $Py -ArgumentList @("launch.py") -WorkingDirectory $Catalog
    Write-Host "Catalog Center started for manual QA." -ForegroundColor Green
}
