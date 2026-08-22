param(
    [switch]$LaunchApp
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RunnerVersion = "49.3G.0"
$Root = "D:\projects\3DPrintHub"
$Catalog = Join-Path $Root "catalog_center"
$Py = Join-Path $Root ".venv\Scripts\python.exe"
$BaseGate = Join-Path $Root "RUN_PHASE49_3F_LOCAL_GATE.ps1"

function Step([string]$Title) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Fail([string]$Message) {
    Write-Host ""
    Write-Host "PHASE49.3G LOCAL GATE FAILED" -ForegroundColor Red
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

function Invoke-NativeCapture {
    param(
        [Parameter(Mandatory=$true)][string]$File,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )
    $previous = $ErrorActionPreference
    $captured = @()
    $exitCode = $null
    try {
        $ErrorActionPreference = "Continue"
        $captured = @(& $File @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previous
    }
    $text = (@($captured) | ForEach-Object { $_.ToString() }) -join "`n"
    if ($exitCode -ne 0) {
        Fail "Command failed ($exitCode): $File $($Arguments -join ' ')`n$text"
    }
    return $text
}

Step "00. PHASE49.3G WINDOWS LOCAL GATE"
Write-Host "Runner     = $RunnerVersion"
Write-Host "Project    = $Root"
Write-Host "Catalog    = $Catalog"
Write-Host "Production = NOT TOUCHED" -ForegroundColor Yellow

if (-not (Test-Path $Root)) { Fail "Project root not found: $Root" }
if (-not (Test-Path $Catalog)) { Fail "Catalog Center not found: $Catalog" }
if (-not (Test-Path $Py)) { Fail "Virtualenv Python not found: $Py" }
if (-not (Test-Path $BaseGate)) { Fail "Phase49.3F base gate not found: $BaseGate" }

Step "01. RUN FULL PHASE49.3F.1 BASE GATE"
& $BaseGate
if ($LASTEXITCODE -ne 0) {
    Fail "Phase49.3F.1 base gate failed. Phase49.3G stopped."
}

Step "02. VERIFY PHASE49.3G SOURCE EXISTS"
$requiredFiles = @(
    "catalog_center\app\phase49_3g_workspace_usability.py",
    "catalog_center\app\phase49_3g_commerce_provenance.py",
    "catalog_center\tests\test_epic49_phase49_3g_workspace_usability.py",
    "catalog_center\tests\test_epic49_phase49_3g_commerce_provenance.py"
)
foreach ($relative in $requiredFiles) {
    if (-not (Test-Path (Join-Path $Root $relative))) {
        Fail "Required Phase49.3G file missing: $relative"
    }
}
Write-Host "Phase49.3G source/test files found." -ForegroundColor Green

Step "03. COMPILE PHASE49.3G"
Push-Location $Root
try {
    Run-Native -File $Py -Arguments @(
        "-m", "compileall", "-q",
        "catalog_center\app\phase49_3g_workspace_usability.py",
        "catalog_center\app\phase49_3g_commerce_provenance.py",
        "catalog_center\app\phase49_3f_source_refresh_guard.py",
        "catalog_center\launch.py"
    )
} finally {
    Pop-Location
}

Step "04. PHASE49.3G DEDICATED TESTS"
Push-Location $Catalog
try {
    Run-Native -File $Py -Arguments @(
        "-m", "unittest", "-v",
        "tests.test_epic49_phase49_3g_workspace_usability",
        "tests.test_epic49_phase49_3g_commerce_provenance"
    )
} finally {
    Pop-Location
}

Step "05. VERIFY PHASE49.3G LAUNCH MARKERS"
Push-Location $Catalog
try {
    $verifyText = Invoke-NativeCapture -File $Py -Arguments @("launch.py", "--verify-only")
    Write-Host $verifyText
    $requiredMarkers = @(
        "EPIC49_3G_WORKSPACE_VERTICAL_SCROLL=ENABLED",
        "EPIC49_3G_GALLERY_HORIZONTAL_SCROLL=ENABLED",
        "EPIC49_3G_COMPACT_COMMERCE=ENABLED",
        "EPIC49_3G_AI_AUTOFILL_PROVENANCE=ENABLED",
        "EPIC49_3G_MANUAL_OVERRIDE_GUARD=ENABLED",
        "EPIC49_3G_AI_DISABLE_PER_GROUP=ENABLED",
        "EPIC49_3G_COMMERCE_PROVENANCE=ENABLED",
        "EPIC49_3F_SELECTED_IMAGE_TEXT_ONLY_AI=ENABLED",
        "ACTIVE_RELEASE_VERIFIED=OK"
    )
    foreach ($marker in $requiredMarkers) {
        if ($verifyText -notmatch [regex]::Escape($marker)) {
            Fail "Required Phase49.3G marker missing: $marker"
        }
    }
    Write-Host "PHASE49_3G_LAUNCH_MARKERS=OK" -ForegroundColor Green
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
    Write-Host "FINAL_HEAD = $head" -ForegroundColor Green
} finally {
    Pop-Location
}

Step "07. PHASE49.3G AUTOMATED LOCAL GATE PASSED"
Write-Host "Runner     = $RunnerVersion" -ForegroundColor Green
Write-Host "Production = UNTOUCHED" -ForegroundColor Yellow
Write-Host ""
Write-Host "Manual QA:" -ForegroundColor Cyan
Write-Host "1) Commerce/Product pages scroll vertically with mouse wheel and visible scrollbar; Stage rail stays accessible."
Write-Host "2) Commerce fields are compact; pricing/rate table no longer expands into an unusable tall block."
Write-Host "3) Images gallery is one horizontal thumbnail strip with a visible horizontal scrollbar."
Write-Host "4) Gallery status/buttons still work: selected/site/primary/slider/remove/open."
Write-Host "5) Task Center shows AI/manual/disabled ownership suffixes."
Write-Host "6) Commerce page shows material AI ownership controls; fixed price/sale approval/license remain operator-owned."
Write-Host "7) Run 'تکمیل هوشمند محصول با AI'; only missing allowed fields may be filled."
Write-Host "8) AI must never auto-approve sale/license/fixed price or Production Publish."
Write-Host "9) Disable AI for one group; rerun autofill and confirm that group is not modified."
Write-Host "10) Manually edit an AI-owned field + Save; group becomes manual override and stays protected until operator releases it."
Write-Host "11) Image SEO remains selected-only and text-only; unselected metadata remains unchanged."
Write-Host "12) Production remains untouched until explicit approval."

if ($LaunchApp) {
    Step "08. START CATALOG CENTER FOR PHASE49.3G MANUAL QA"
    Start-Process -FilePath $Py -ArgumentList @("launch.py") -WorkingDirectory $Catalog
    Write-Host "Catalog Center started." -ForegroundColor Green
}
