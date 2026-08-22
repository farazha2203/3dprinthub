param(
    [switch]$LaunchApp
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RunnerVersion = "49.3I.0"
$Root = "D:\projects\3DPrintHub"
$Catalog = Join-Path $Root "catalog_center"
$Py = Join-Path $Root ".venv\Scripts\python.exe"
$BaseGate = Join-Path $Root "RUN_PHASE49_3H_LOCAL_GATE.ps1"

function Step([string]$Title) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Fail([string]$Message) {
    Write-Host ""
    Write-Host "PHASE49.3I LOCAL GATE FAILED" -ForegroundColor Red
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

Step "00. PHASE49.3I WINDOWS LOCAL GATE"
Write-Host "Runner     = $RunnerVersion"
Write-Host "Project    = $Root"
Write-Host "Catalog    = $Catalog"
Write-Host "Production = NOT TOUCHED" -ForegroundColor Yellow

if (-not (Test-Path $Root)) { Fail "Project root not found: $Root" }
if (-not (Test-Path $Catalog)) { Fail "Catalog Center not found: $Catalog" }
if (-not (Test-Path $Py)) { Fail "Virtualenv Python not found: $Py" }
if (-not (Test-Path $BaseGate)) { Fail "Phase49.3H base gate not found: $BaseGate" }

Step "01. VERIFY OPERATIONAL DOCUMENTATION"
$requiredDocs = @(
    "AGENTS.md",
    "PROJECT_CONTEXT.md",
    "docs\00_PROJECT_MASTER_ROADMAP_FA.md",
    "docs\CURRENT_STATE.md",
    "docs\ROADMAP.md",
    "docs\PATHS.md",
    "docs\ERRORS.md",
    "docs\HOST_CONSTRAINTS.md",
    "docs\REQUESTS.md",
    "docs\phases\PHASE49_3I_DISCOVERY_REVIEW_PRODUCT_LIST_PRICING.md"
)
foreach ($relative in $requiredDocs) {
    if (-not (Test-Path (Join-Path $Root $relative))) {
        Fail "Required project documentation missing: $relative"
    }
}
Write-Host "PHASE49_3I_DOCS=OK" -ForegroundColor Green

Step "02. RUN FULL PHASE49.3H BASE GATE"
& $BaseGate
if ($LASTEXITCODE -ne 0) {
    Fail "Phase49.3H base gate failed. Phase49.3I stopped."
}

Step "03. VERIFY PHASE49.3I SOURCE EXISTS"
$requiredFiles = @(
    "catalog_center\app\phase49_3i_discovery_review.py",
    "catalog_center\app\phase49_3i_source_safety.py",
    "catalog_center\app\phase49_3i_product_list.py",
    "catalog_center\app\phase49_3i_pricing_modes.py",
    "store\phase49_3i_pricing_modes.py",
    "catalog_center\tests\test_epic49_phase49_3i_discovery_review.py",
    "catalog_center\tests\test_epic49_phase49_3i_source_safety.py",
    "catalog_center\tests\test_epic49_phase49_3i_product_list.py",
    "catalog_center\tests\test_epic49_phase49_3i_pricing_modes.py",
    "store\test_phase49_3i_pricing_modes.py"
)
foreach ($relative in $requiredFiles) {
    if (-not (Test-Path (Join-Path $Root $relative))) {
        Fail "Required Phase49.3I file missing: $relative"
    }
}
Write-Host "PHASE49_3I_SOURCE_FILES=OK" -ForegroundColor Green

Step "04. COMPILE PHASE49.3I"
Push-Location $Root
try {
    Run-Native -File $Py -Arguments @(
        "-m", "compileall", "-q",
        "catalog_center\app\phase49_3i_discovery_review.py",
        "catalog_center\app\phase49_3i_source_safety.py",
        "catalog_center\app\phase49_3i_product_list.py",
        "catalog_center\app\phase49_3i_pricing_modes.py",
        "store\phase49_3i_pricing_modes.py",
        "store\apps.py",
        "catalog_center\launch.py"
    )
} finally {
    Pop-Location
}

Step "05. PHASE49.3I CATALOG CENTER TESTS"
Push-Location $Catalog
try {
    Run-Native -File $Py -Arguments @(
        "-m", "unittest", "-v",
        "tests.test_epic49_phase49_3i_discovery_review",
        "tests.test_epic49_phase49_3i_source_safety",
        "tests.test_epic49_phase49_3i_product_list",
        "tests.test_epic49_phase49_3i_pricing_modes",
        "tests.test_epic49_phase49_3h_image_limits",
        "tests.test_epic49_phase49_3g_workspace_usability",
        "tests.test_epic49_phase49_3g_commerce_provenance"
    )
} finally {
    Pop-Location
}

Step "06. PHASE49.3I DJANGO PRICING + MIGRATION CONTRACT"
Push-Location $Root
try {
    Run-Native -File $Py -Arguments @("manage.py", "check")
    Run-Native -File $Py -Arguments @("manage.py", "makemigrations", "--check", "--dry-run")
    Run-Native -File $Py -Arguments @("manage.py", "migrate", "--plan")
    Run-Native -File $Py -Arguments @(
        "manage.py", "test",
        "store.test_phase49_3i_pricing_modes",
        "store.test_phase49_3f_pricing",
        "store.test_phase49_3d_price_range",
        "store.test_phase49_unified_import_e2e",
        "-v", "2"
    )
    Write-Host "PHASE49_3I_DJANGO_MIGRATION=NONE" -ForegroundColor Green
} finally {
    Pop-Location
}

Step "07. VERIFY PHASE49.3I LAUNCH MARKERS"
Push-Location $Catalog
try {
    $verifyText = Invoke-NativeCapture -File $Py -Arguments @("launch.py", "--verify-only")
    Write-Host $verifyText
    $requiredMarkers = @(
        "EPIC49_3I_EXACT_SEARCH_URL=ENABLED",
        "EPIC49_3I_DISCOVERY_REVIEW_QUEUE=ENABLED",
        "EPIC49_3I_PREVIEW_ONE_IMAGE=ENABLED",
        "EPIC49_3I_APPROVAL_BEFORE_FULL_FETCH=ENABLED",
        "EPIC49_3I_ARCHIVE_BLOCK_DEDUPE=ENABLED",
        "EPIC49_3I_SOURCE_TEXT_LATIN_SAFE=ENABLED",
        "EPIC49_3I_LIGHTWEIGHT_PRODUCT_LIST=ENABLED",
        "EPIC49_3I_PRICING_FIXED_RANGE_FORMULA=ENABLED",
        "EPIC49_3H_IMAGE_LIMIT_HARD_MAX_20=ENABLED",
        "EPIC49_3H_SEO_EXECUTION_CONSOLE=ENABLED",
        "EPIC49_3G_MANUAL_OVERRIDE_GUARD=ENABLED",
        "ACTIVE_RELEASE_VERIFIED=OK"
    )
    foreach ($marker in $requiredMarkers) {
        if ($verifyText -notmatch [regex]::Escape($marker)) {
            Fail "Required Phase49.3I marker missing: $marker"
        }
    }
    Write-Host "PHASE49_3I_LAUNCH_MARKERS=OK" -ForegroundColor Green
} finally {
    Pop-Location
}

Step "08. FINAL GIT SAFETY CHECK"
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

Step "09. PHASE49.3I AUTOMATED LOCAL GATE PASSED"
Write-Host "Runner     = $RunnerVersion" -ForegroundColor Green
Write-Host "Production = UNTOUCHED" -ForegroundColor Yellow
Write-Host ""
Write-Host "Manual QA — use the real MakerWorld search URL:" -ForegroundColor Cyan
Write-Host "https://makerworld.com/en/search/models?keyword=cake+stand"
Write-Host ""
Write-Host "1) Select MakerWorld + Search mode, paste the exact URL, click 'کشف و پیش‌نمایش'."
Write-Host "2) Confirm candidate results belong to cake stand search; inspect examples 2834255 / 2845731 if MakerWorld still returns them."
Write-Host "3) Preview must show one thumbnail + product name/link and MUST NOT create full product rows before approval."
Write-Host "4) Select one candidate, set image limit 10, approve full fetch; persisted/selected/downloaded images must be <=10."
Write-Host "5) Select another candidate and choose 'آرشیو / لازم نیست'; it must enter Blocked without full data fetch."
Write-Host "6) Repeat the same search: imported/blocked identities must not full-fetch again."
Write-Host "7) New/refetched source text must not persist CJK/other unexpected scripts; URL stays exact; Persian AI/editor fields remain Persian."
Write-Host "8) Products page shows a lightweight thumbnail + product name list; detailed right-side form is gone from this page."
Write-Host "9) 'صفحه محصول / ویرایش کامل' opens Product Workspace and all detailed fields are still available there."
Write-Host "10) Pricing Fixed: enter an exact value (example 1,200,000); min=max and price is final."
Write-Host "11) Pricing Range: enter 200,000..500,000; it stays a range/consultation price and does NOT use formula calculation."
Write-Host "12) Pricing Formula: material grams/rates + print time + supervision preview still calculates through mature 49.3F engine."
Write-Host "13) 49.3H SEO Result/Error drawer, cost ledger and image hard max 20 still work."
Write-Host "14) Do LOCAL PUBLISH ONLY after visual/data QA. Do not use Production Publish."

if ($LaunchApp) {
    Step "10. START CATALOG CENTER FOR PHASE49.3I MANUAL QA"
    Start-Process -FilePath $Py -ArgumentList @("launch.py") -WorkingDirectory $Catalog
    Write-Host "Catalog Center started." -ForegroundColor Green
}
