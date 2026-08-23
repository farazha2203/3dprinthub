param(
    [switch]$LaunchApp
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = "D:\projects\3DPrintHub"
$Catalog = Join-Path $Root "catalog_center"
$Py = Join-Path $Root ".venv\Scripts\python.exe"
$PreviousGate = Join-Path $Root "RUN_PHASE49_3I16_FALLBACK_GATE.ps1"
$Branch = "epic/phase49-unified-product-slider-sync"
$RemoteRef = "origin/$Branch"

function Fail([string]$Message) {
    Write-Host ""
    Write-Host "PHASE49.3I.17 SINGLE AI GATE FAILED" -ForegroundColor Red
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
Write-Host "PHASE49.3I.17 SINGLE ACTIVE AI RUNTIME" -ForegroundColor Cyan
Write-Host "NO RESET / NO STASH / NO DELETE / NO PRODUCTION" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

if (-not (Test-Path $Root)) { Fail "Project root missing: $Root" }
if (-not (Test-Path $Catalog)) { Fail "Catalog Center missing: $Catalog" }
if (-not (Test-Path $Py)) { Fail "Virtualenv Python missing: $Py" }
if (-not (Test-Path $PreviousGate)) { Fail "Phase49.3I.16 gate missing: $PreviousGate" }

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
    Write-Host "PHASE49_3I17_GIT_SNAPSHOT=OK" -ForegroundColor Green
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "=== ALL PREVIOUS PHASE49.3I REGRESSIONS ===" -ForegroundColor Cyan
& $PreviousGate
if ($LASTEXITCODE -ne 0) {
    Fail "Previous Phase49.3I.16 gate failed."
}

Write-Host ""
Write-Host "=== PHASE49.3I.17 COMPILE ===" -ForegroundColor Cyan
Push-Location $Root
try {
    Run-Native -File $Py -Arguments @(
        "-m", "compileall", "-q",
        "catalog_center\app\phase49_3i17_single_active_ai_runtime.py",
        "catalog_center\app\phase49_3i_local_qa_hotfix.py",
        "catalog_center\tests\test_epic49_phase49_3i17_single_active_ai_runtime.py"
    )
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "=== PHASE49.3I.17 TARGETED TESTS ===" -ForegroundColor Cyan
Push-Location $Catalog
try {
    Run-Native -File $Py -Arguments @(
        "-m", "unittest", "-v",
        "tests.test_epic49_phase49_3i17_single_active_ai_runtime",
        "tests.test_epic49_phase49_3i_schema_runtime_recovery",
        "tests.test_epic49_phase49_3i_ai_trace_recovery",
        "tests.test_epic49_phase49_3i_ai_execution_recovery"
    )
} finally {
    Pop-Location
}

Write-Host "PHASE49_3I17_ACTIVE_PROVIDER_MODEL=EXACT_SAVED_ONLY" -ForegroundColor Green
Write-Host "PHASE49_3I17_AUTO_AI_ON_OPEN=DISABLED" -ForegroundColor Green
Write-Host "PHASE49_3I17_TASK_MODEL_PROBE=NO_NETWORK" -ForegroundColor Green
Write-Host "PHASE49_3I17_CROSS_PROVIDER_FALLBACK=FORBIDDEN" -ForegroundColor Green
Write-Host "PHASE49_3I17_GOOGLE_EXACT_MODEL=NO_MODEL_LIST_PREFLIGHT" -ForegroundColor Green
Write-Host "PHASE49_3I17_STALE_WIDGET_CALLBACK=SAFE" -ForegroundColor Green
Write-Host "PHASE49_3I17_PREVIOUS_REGRESSIONS=PRESERVED" -ForegroundColor Green
Write-Host "PHASE49_3I17_PRODUCTION=UNTOUCHED" -ForegroundColor Yellow

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
Write-Host "PHASE49.3I.17 SINGLE AI GATE PASSED" -ForegroundColor Green

if ($LaunchApp) {
    Start-Process -FilePath $Py -ArgumentList @("launch.py") -WorkingDirectory $Catalog
    Write-Host "Catalog Center started for focused single-AI QA." -ForegroundColor Green
}
