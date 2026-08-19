param(
    [switch]$LaunchApp
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RunnerVersion = "49.3E.0"
$Root = "D:\projects\3DPrintHub"
$Catalog = Join-Path $Root "catalog_center"
$Py = Join-Path $Root ".venv\Scripts\python.exe"
$BaseGate = Join-Path $Root "RUN_PHASE49_3D_LOCAL_GATE.ps1"

function Step([string]$Title) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Fail([string]$Message) {
    Write-Host ""
    Write-Host "PHASE49.3E LOCAL GATE FAILED" -ForegroundColor Red
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

Step "00. PHASE49.3E WINDOWS LOCAL GATE"
Write-Host "Runner    = $RunnerVersion"
Write-Host "Project   = $Root"
Write-Host "Catalog   = $Catalog"
Write-Host "Production= NOT TOUCHED" -ForegroundColor Yellow

if (-not (Test-Path $Root)) { Fail "Project root not found: $Root" }
if (-not (Test-Path $Catalog)) { Fail "Catalog Center not found: $Catalog" }
if (-not (Test-Path $Py)) { Fail "Virtualenv Python not found: $Py" }
if (-not (Test-Path $BaseGate)) { Fail "Base Phase49.3D gate not found: $BaseGate" }

Step "01. RUN FULL PHASE49.3D BASE GATE"
& $BaseGate
if ($LASTEXITCODE -ne 0) {
    Fail "Phase49.3D base gate failed. Phase49.3E stopped."
}

Step "02. VERIFY PHASE49.3E SOURCE EXISTS"
$requiredFiles = @(
    "catalog_center\app\phase49_3e_ai_task_center.py",
    "catalog_center\app\phase49_3e_ai_contract.py",
    "catalog_center\tests\test_epic49_phase49_3e_ai_task_center.py"
)
foreach ($relative in $requiredFiles) {
    $path = Join-Path $Root $relative
    if (-not (Test-Path $path)) {
        Fail "Required Phase49.3E file missing: $relative"
    }
}
Write-Host "Phase49.3E source files found." -ForegroundColor Green

Step "03. COMPILE PHASE49.3E"
Push-Location $Root
try {
    Run-Native -File $Py -Arguments @(
        "-m", "compileall", "-q",
        "catalog_center\app\phase49_3e_ai_task_center.py",
        "catalog_center\app\phase49_3e_ai_contract.py",
        "catalog_center\launch.py"
    )
} finally {
    Pop-Location
}

Step "04. PHASE49.3E DEDICATED TESTS"
Push-Location $Catalog
try {
    Run-Native -File $Py -Arguments @(
        "-m", "unittest", "-v",
        "tests.test_epic49_phase49_3e_ai_task_center"
    )
} finally {
    Pop-Location
}

Step "05. VERIFY PHASE49.3E LAUNCH MARKERS"
Push-Location $Catalog
try {
    $verify = & $Py launch.py --verify-only 2>&1
    $rc = $LASTEXITCODE
    $verify | ForEach-Object { Write-Host $_ }
    if ($rc -ne 0) { Fail "launch.py --verify-only failed with exit code $rc." }

    $requiredMarkers = @(
        "EPIC49_3E_AI_TASK_CENTER=ENABLED",
        "EPIC49_3E_IMAGE_AI_SEO=ENABLED",
        "EPIC49_3E_OPERATOR_IMAGE_EDITOR=ENABLED",
        "EPIC49_3E_NON_BLOCKING_STAGE_NAV=ENABLED",
        "EPIC49_3E_LOCAL_PREFLIGHT_ALWAYS_ACCESSIBLE=ENABLED",
        "ACTIVE_RELEASE_VERIFIED=OK"
    )
    $verifyText = ($verify -join "`n")
    foreach ($marker in $requiredMarkers) {
        if ($verifyText -notmatch [regex]::Escape($marker)) {
            Fail "Required Phase49.3E marker missing: $marker"
        }
    }
    Write-Host "All required Phase49.3E markers found." -ForegroundColor Green
} finally {
    Pop-Location
}

Step "06. FINAL GIT SAFETY CHECK"
Push-Location $Root
try {
    $dirty = @(git status --porcelain --untracked-files=all)
    if ($dirty.Count -gt 0) {
        $dirty | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
        Fail "Tests left project changes. Nothing was reset or deleted."
    }
    $head = (& git rev-parse HEAD).Trim()
    Write-Host "HEAD = $head" -ForegroundColor Green
} finally {
    Pop-Location
}

Step "07. PHASE49.3E AUTOMATED LOCAL GATE PASSED"
Write-Host "Runner     = $RunnerVersion" -ForegroundColor Green
Write-Host "PRODUCTION = UNTOUCHED" -ForegroundColor Yellow
Write-Host ""
Write-Host "Manual QA:" -ForegroundColor Cyan
Write-Host "1) Open the same product and verify all 7 stage buttons are clickable, even when a stage is red."
Write-Host "2) Images stage must show: AI image SEO, manual metadata editor, final SEO file action."
Write-Host "3) AI/SEO task panel must show Persian content, product SEO, image SEO, material AI, and slider SEO."
Write-Host "4) Click AI image SEO: Alt/SEO filename/Creator/Source/Metadata should complete from real product/source facts."
Write-Host "5) If an image task stays red, open manual metadata editor, correct it, save and rebuild the SEO file."
Write-Host "6) Slider SEO task is skipped when slider is off and becomes required when slider is enabled."
Write-Host "7) Completed stages remain editable; Next stays gated only by the current stage."
Write-Host "8) Local Publish stays accessible as a preflight and must explain blockers."
Write-Host "9) Production Publish remains blocked until every required gate is green and explicit approval is given."

if ($LaunchApp) {
    Step "08. START CATALOG CENTER FOR PHASE49.3E MANUAL QA"
    Start-Process -FilePath $Py -ArgumentList @("launch.py") -WorkingDirectory $Catalog
    Write-Host "Catalog Center started." -ForegroundColor Green
}
