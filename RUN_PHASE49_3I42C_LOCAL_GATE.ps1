param(
    [string]$ExpectedHead = "",
    [switch]$LaunchApp
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RunnerVersion = "49.3I.52.1"
$Root = "D:\projects\3DPrintHub"
$Catalog = Join-Path $Root "catalog_center"
$Py = Join-Path $Root ".venv\Scripts\python.exe"
$Branch = "agent/phase49-3i18-operator-bulk-ai-rebuild"
$CatalogDb = "D:\projects\3dprinthub-catalog-manager\catalog.sqlite3"
$CatalogDataRoot = Split-Path -Parent $CatalogDb
$BackupRoot = "D:\projects\3dprinthub-backups"

function Step([string]$Title) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Fail([string]$Message) {
    Write-Host ""
    Write-Host "PHASE49.3I.52 LOCAL GATE FAILED" -ForegroundColor Red
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
    $text = (@($captured) | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine
    if ($exitCode -ne 0) {
        Fail ("Command failed ({0}): {1} {2}{3}{4}" -f $exitCode, $File, ($Arguments -join ' '), [Environment]::NewLine, $text)
    }
    return $text
}

function Invoke-PythonStdin {
    param(
        [Parameter(Mandatory=$true)][string]$Script
    )
    $previous = $ErrorActionPreference
    $captured = @()
    $exitCode = $null
    try {
        $ErrorActionPreference = "Continue"
        $captured = @($Script | & $Py - 2>&1)
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previous
    }
    [pscustomobject]@{
        ExitCode = [int]$exitCode
        Text = ((@($captured) | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine)
    }
}

Step "00. PHASE49.3I.52 SITE AUTHORING + BIDIRECTIONAL SYNC LOCAL GATE"
Write-Host "Runner     = $RunnerVersion"
Write-Host "Project    = $Root"
Write-Host "Catalog    = $Catalog"
Write-Host "Production = NOT TOUCHED" -ForegroundColor Yellow
Write-Host "Host       = NOT TOUCHED" -ForegroundColor Yellow
Write-Host "Migration  = SITE CANDIDATE ONLY - NOT APPLIED BY THIS GATE" -ForegroundColor Yellow

if (-not (Test-Path -LiteralPath $Root)) { Fail "Project root not found: $Root" }
if (-not (Test-Path -LiteralPath $Catalog)) { Fail "Catalog Center not found: $Catalog" }
if (-not (Test-Path -LiteralPath $Py)) { Fail "Virtualenv Python not found: $Py" }
if (-not (Test-Path -LiteralPath $CatalogDb)) { Fail "Catalog SQLite not found: $CatalogDb" }

Step "01. VERIFY REPOSITORY / LIVE GITHUB HEAD"
Set-Location -LiteralPath $Root

$Origin = (& git remote get-url origin).Trim()
$CurrentBranch = (& git branch --show-current).Trim()
$Dirty = @(git status --porcelain --untracked-files=all)
$LocalHead = (& git rev-parse HEAD).Trim()

if ($Origin -notmatch "farazha2203/3dprinthub(\.git)?$") { Fail "WRONG REPOSITORY: $Origin" }
if ($CurrentBranch -ne $Branch) { Fail "WRONG BRANCH: $CurrentBranch" }
if ($Dirty.Count -gt 0) {
    $Dirty | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
    Fail "WORKTREE DIRTY - inspect it; do not reset/stash/delete"
}

$RemoteLineBefore = (& git ls-remote origin "refs/heads/$Branch")
if ($LASTEXITCODE -ne 0 -or -not $RemoteLineBefore) { Fail "git ls-remote failed" }
$LiveHeadBefore = (($RemoteLineBefore -split "\s+")[0]).Trim()

if ($ExpectedHead -and $LiveHeadBefore -ne $ExpectedHead) {
    Fail "EXPECTED HEAD IS STALE: expected=$ExpectedHead live=$LiveHeadBefore"
}

Run-Native -File "git" -Arguments @(
    "fetch", "--no-tags", "origin",
    "refs/heads/$($Branch):refs/remotes/origin/$($Branch)"
)

$FetchedHead = (& git rev-parse "origin/$Branch").Trim()
$RemoteLineAfter = (& git ls-remote origin "refs/heads/$Branch")
if ($LASTEXITCODE -ne 0 -or -not $RemoteLineAfter) { Fail "second git ls-remote failed" }
$LiveHeadAfter = (($RemoteLineAfter -split "\s+")[0]).Trim()

Write-Host "ORIGIN=$Origin"
Write-Host "BRANCH=$CurrentBranch"
Write-Host "LOCAL_HEAD=$LocalHead"
Write-Host "LIVE_HEAD_BEFORE=$LiveHeadBefore"
Write-Host "FETCHED_HEAD=$FetchedHead"
Write-Host "LIVE_HEAD_AFTER=$LiveHeadAfter"

if ($LiveHeadBefore -ne $FetchedHead -or $FetchedHead -ne $LiveHeadAfter) {
    Fail "REMOTE BRANCH CHANGED DURING GATE PREFLIGHT - rerun after it stabilizes"
}
if ($LocalHead -ne $FetchedHead) {
    Fail "LOCAL IS NOT AT LIVE GITHUB HEAD. Run: git pull --ff-only origin $Branch"
}

Step "02. VERIFY REQUIRED DOCUMENTATION / SOURCE"
$required = @(
    "AGENTS.md",
    "docs\CURRENT_STATE.md",
    "docs\ROADMAP.md",
    "docs\PATHS.md",
    "docs\ERRORS.md",
    "docs\HOST_CONSTRAINTS.md",
    "docs\REQUESTS.md",
    "docs\phases\PHASE49_3I42_QT6_DESKTOP_MODERNIZATION.md",
    "docs\phases\PHASE49_3I51_WINDOWS_SITE_FINALIZATION.md",
    "docs\phases\PHASE49_3I52_SITE_AUTHORING_SHARED_AI.md",
    "catalog_center\qt_launch.py",
    "catalog_center\qt6\acquisition_runtime.py",
    "catalog_center\qt6\pages.py",
    "catalog_center\app\classic_methods.py",
    "catalog_center\app\phase49_3i43_modern_acquisition_intelligence.py",
    "catalog_center\app\phase49_3i45_incremental_discovery_intelligence.py",
    "catalog_center\app\phase49_3c_image_pipeline.py",
    "catalog_center\tests\test_phase49_3i42c_acquisition_runtime.py",
    "catalog_center\tests\test_phase49_3i42c3_ai_crawl_parity.py",
    "catalog_center\tests\test_phase49_3i46_catalog_paging_parity.py",
    "catalog_center\tests\test_phase49_3i47_qt_workspace_image_bulk_ai.py",
    "catalog_center\tests\test_phase49_3i48_owner_filament_site_foundation.py",
    "catalog_center\tests\test_phase49_3i49_site_bulk_publish.py",
    "catalog_center\tests\test_phase49_3i51_windows_site_finalization.py",
    "catalog_center\tests\test_phase49_3i52b_bidirectional_site_sync.py",
    "catalog_center\app\phase49_3i49_site_publish.py",
    "catalog_center\app\ai_model_catalog.py",
    "templates\store\product_detail.html",
    "static\admin\phase49-admin-tabs.css",
    "static\admin\phase49-admin-tabs.js",
    "static\store\css\phase49-product-info-tabs.css",
    "static\store\js\phase49-product-info-tabs.js"
)
foreach ($relative in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $Root $relative))) {
        Fail "Required file missing: $relative"
    }
}
Write-Host "PHASE49_3I47_REQUIRED_FILES=OK" -ForegroundColor Green

Step "03. CHECKSUM BACKUP CATALOG SQLITE"
New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupDir = Join-Path $BackupRoot "phase49-3i42c-$Stamp"
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
$BackupDb = Join-Path $BackupDir "catalog-before-qt42c-qa.sqlite3"

Copy-Item -LiteralPath $CatalogDb -Destination $BackupDb -Force
$SourceHash = (Get-FileHash -LiteralPath $CatalogDb -Algorithm SHA256).Hash
$BackupHash = (Get-FileHash -LiteralPath $BackupDb -Algorithm SHA256).Hash

Write-Host "DB_SOURCE_SHA256=$SourceHash"
Write-Host "DB_BACKUP_SHA256=$BackupHash"
Write-Host "DB_BACKUP=$BackupDb"

if ($SourceHash -ne $BackupHash) { Fail "DATABASE BACKUP CHECKSUM MISMATCH" }

Step "04. VERIFY / INSTALL QT + ACQUISITION DEPENDENCIES"
Run-Native -File $Py -Arguments @(
    "-m", "pip", "install",
    "-r", (Join-Path $Catalog "requirements-qt6.txt")
)
Run-Native -File $Py -Arguments @(
    "-c",
    "import PySide6,httpx,protego,playwright; print('PYSIDE6=' + PySide6.__version__); print('HTTPX=' + httpx.__version__)"
)

Step "05. PLAYWRIGHT CHROMIUM SMOKE - STDIN SAFE"
$PlaywrightProbe = @'
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    print("PLAYWRIGHT_CHROMIUM=OK")
    browser.close()
'@

$Probe = Invoke-PythonStdin -Script $PlaywrightProbe
if ($Probe.Text) { Write-Host $Probe.Text }

if ($Probe.ExitCode -ne 0) {
    if ($Probe.Text -match "Executable doesn't exist|playwright install") {
        Write-Host "Chromium runtime is genuinely missing; installing Playwright Chromium..." -ForegroundColor Yellow
        Run-Native -File $Py -Arguments @("-m", "playwright", "install", "chromium")
        $Probe = Invoke-PythonStdin -Script $PlaywrightProbe
        if ($Probe.Text) { Write-Host $Probe.Text }
        if ($Probe.ExitCode -ne 0) {
            Fail "Playwright Chromium still cannot launch after browser installation"
        }
    } else {
        Fail "Playwright smoke failed for a reason other than missing Chromium. No blind reinstall was attempted."
    }
}

if ($Probe.Text -notmatch "PLAYWRIGHT_CHROMIUM=OK") {
    Fail "Playwright smoke marker missing"
}

Step "06. COMPILE QT42C + MATURE ACQUISITION"
Run-Native -File $Py -Arguments @(
    "-m", "compileall", "-q",
    (Join-Path $Catalog "qt6"),
    (Join-Path $Catalog "qt_launch.py"),
    (Join-Path $Catalog "app\classic_methods.py"),
    (Join-Path $Catalog "app\page_extractor.py"),
    (Join-Path $Catalog "app\phase49_3i16_resilient_acquisition.py"),
    (Join-Path $Catalog "app\phase49_3i38_crawl_ledger_stage_ai.py"),
    (Join-Path $Catalog "app\phase49_3i43_modern_acquisition_intelligence.py"),
    (Join-Path $Catalog "app\phase49_3i45_incremental_discovery_intelligence.py"),
    (Join-Path $Catalog "app\phase49_3c_image_pipeline.py"),
    (Join-Path $Catalog "tests\test_phase49_3i42c_acquisition_runtime.py"),
    (Join-Path $Catalog "tests\test_phase49_3i42c3_ai_crawl_parity.py"),
    (Join-Path $Catalog "tests\test_phase49_3i46_catalog_paging_parity.py"),
    (Join-Path $Catalog "tests\test_phase49_3i47_qt_workspace_image_bulk_ai.py"),
    (Join-Path $Catalog "tests\test_phase49_3i48_owner_filament_site_foundation.py"),
    (Join-Path $Catalog "tests\test_phase49_3i49_site_bulk_publish.py"),
    (Join-Path $Catalog "tests\test_phase49_3i51_windows_site_finalization.py"),
    (Join-Path $Catalog "tests\test_phase49_3i52b_bidirectional_site_sync.py"),
    (Join-Path $Catalog "app\phase49_3i49_site_publish.py"),
    (Join-Path $Catalog "app\ai_model_catalog.py")
)

Step "07. QT42C + ACQUISITION REGRESSIONS"
Push-Location $Catalog
try {
    Run-Native -File $Py -Arguments @(
        "-m", "unittest", "-v",
        "tests.test_phase49_3i42_qt6_foundation",
        "tests.test_phase49_3i42b_core_parity",
        "tests.test_phase49_3i42c_acquisition_runtime",
        "tests.test_phase49_3i42c3_ai_crawl_parity",
        "tests.test_phase49_3i46_catalog_paging_parity",
        "tests.test_phase49_3i47_qt_workspace_image_bulk_ai",
        "tests.test_phase49_3i48_owner_filament_site_foundation",
        "tests.test_phase49_3i49_site_bulk_publish",
        "tests.test_phase49_3i51_windows_site_finalization",
        "tests.test_phase49_3i52b_bidirectional_site_sync"
    )

    Run-Native -File $Py -Arguments @(
        "-m", "unittest", "-v",
        "tests.test_epic49_phase49_3i16_resilient_acquisition",
        "tests.test_phase49_3i38_crawl_ledger_stage_ai",
        "tests.test_phase49_3i43_modern_acquisition_intelligence",
        "tests.test_phase49_3i45_incremental_discovery_intelligence"
    )

    Run-Native -File $Py -Arguments @(
        "-m", "unittest", "-v",
        "tests.test_phase49_3i41_filament_library",
        "tests.test_phase49_3i34_profile_matrix",
        "tests.test_phase49_3i35_operator_workflow",
        "tests.test_phase49_3i36_stage_finalization",
        "tests.test_phase49_3i37_seven_stage_ai",
        "tests.test_phase49_3i39_professional_commerce",
        "tests.test_epic49_phase49_3i17_single_active_ai_runtime"
    )
} finally {
    Pop-Location
}

Step "08. QT + LEGACY VERIFY"
$OldQtPlatform = $env:QT_QPA_PLATFORM
$OldDataRoot = $env:CATALOG_DATA_ROOT
try {
    $env:QT_QPA_PLATFORM = "offscreen"
    $env:CATALOG_DATA_ROOT = $CatalogDataRoot

    Push-Location $Catalog
    try {
        $QtVerify = Invoke-NativeCapture -File $Py -Arguments @("qt_launch.py", "--verify-only")
        Write-Host $QtVerify
        foreach ($marker in @(
            "QT6_MAIN_WINDOW=ENABLED",
            "QT6_SINGLE_AI_CORE=ENABLED",
            "QT6_PRODUCT_ACQUISITION_ROUTE=ENABLED",
            "QT6_LEGACY_CRAWL_CONTROLS=ENABLED",
            "QT6_AI_MODEL_RANKING_COST=ENABLED",
            "QT6_AI_STRUCTURED_PROBE=ENABLED",
            "QT6_AI_COST_CONFIRM=ENABLED",
            "QT6_DIAGNOSTIC_DIALOG=ENABLED",
            "QT6_OPENROUTER_JSON_MODE=ENABLED",
            "QT6_SEMANTIC_TRANSLATION_GUARD=ENABLED",
            "QT6_IMAGE_FINAL_WEBP_PARITY=ENABLED",
            "QT6_PERSISTENT_CRAWL_INVENTORY=ENABLED",
            "QT6_PRODUCT_LIFECYCLE_BULK_ACTIONS=ENABLED",
            "QT6_PRODUCT_STATUS_BORDER_SEO=ENABLED",
            "QT6_SLIDER_DIRECT_INPUT_UX=ENABLED",
            "QT6_SEARCH_LINK_REVIEW_AI=ENABLED",
            "QT6_FILAMENT_BRAND_COLOR_REGISTRY=ENABLED",
            "QT6_PUBLISHED_REPUBLISH_UPDATE=ENABLED",
            "QT6_42B2_FULL_PARITY_VERIFY=OK"
        )) {
            if ($QtVerify -notmatch [regex]::Escape($marker)) {
                Fail "Missing Qt verify marker: $marker"
            }
        }

        $LegacyVerify = Invoke-NativeCapture -File $Py -Arguments @("launch.py", "--verify-only")
        Write-Host $LegacyVerify
        if ($LegacyVerify -notmatch "ACTIVE_RELEASE_VERIFIED=OK") {
            Fail "Legacy launcher verification marker missing"
        }
    } finally {
        Pop-Location
    }
} finally {
    if ($null -eq $OldQtPlatform) {
        Remove-Item Env:\QT_QPA_PLATFORM -ErrorAction SilentlyContinue
    } else {
        $env:QT_QPA_PLATFORM = $OldQtPlatform
    }

    if ($null -eq $OldDataRoot) {
        Remove-Item Env:\CATALOG_DATA_ROOT -ErrorAction SilentlyContinue
    } else {
        $env:CATALOG_DATA_ROOT = $OldDataRoot
    }
}

Step "09. FINAL GIT SAFETY"
Set-Location -LiteralPath $Root
$FinalHead = (& git rev-parse HEAD).Trim()
$FinalDirty = @(git status --porcelain --untracked-files=all)
$FinalRemoteLine = (& git ls-remote origin "refs/heads/$Branch")
if ($LASTEXITCODE -ne 0 -or -not $FinalRemoteLine) { Fail "final git ls-remote failed" }
$FinalRemoteHead = (($FinalRemoteLine -split "\s+")[0]).Trim()

Write-Host "FINAL_HEAD=$FinalHead"
Write-Host "FINAL_REMOTE_HEAD=$FinalRemoteHead"

if ($FinalHead -ne $LiveHeadAfter) { Fail "LOCAL HEAD CHANGED DURING QA" }
if ($ExpectedHead -and $FinalHead -ne $ExpectedHead) { Fail "FINAL EXPECTED HEAD MISMATCH" }
if ($FinalDirty.Count -gt 0) {
    $FinalDirty | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
    Fail "TESTS CHANGED WORKTREE"
}

Step "10. PHASE49.3I.52 AUTOMATED LOCAL GATE PASSED"
Write-Host "PHASE49_3I47_LOCAL_GATE=PASS" -ForegroundColor Green
Write-Host "PHASE49_3I50_LOCAL_GATE=PASS" -ForegroundColor Green
Write-Host "PHASE49_3I51_LOCAL_GATE=PASS" -ForegroundColor Green
Write-Host "PHASE49_3I52_LOCAL_GATE=PASS" -ForegroundColor Green
Write-Host "HEAD=$FinalHead" -ForegroundColor Green
Write-Host "CLASSIC_SEARCH_CONTINUATION=ENABLED" -ForegroundColor Green
Write-Host "HYBRID_HTTP_SITEMAP_BROWSER=ENABLED" -ForegroundColor Green
Write-Host "RICH_PRODUCT_EXTRACTION=ENABLED" -ForegroundColor Green
Write-Host "CATALOG_BACKUP=$BackupDb" -ForegroundColor Green
Write-Host "PRODUCTION_TOUCHED=NO" -ForegroundColor Yellow
Write-Host "HOST_TOUCHED=NO" -ForegroundColor Yellow

Write-Host ""
Write-Host "Foreground QA:" -ForegroundColor Cyan
Write-Host "1) Products: verify lifecycle tabs (active/published/archive/deleted), old local thumbnails, image count and description on cards."
Write-Host "2) Select TWO disposable Products and run the bulk full-content AI action in Saved Data mode; verify sequential progress and both Products refresh."
Write-Host "3) On one Product with 3+ images run full image/content completion; verify SEO WebPs are numbered -01/-02/-03 and all image SEO metadata is consistent."
Write-Host "4) Add Product/Crawl: default Inventory tab must show Products immediately; switch Large Icons <-> Details and verify title/description/image count."
Write-Host "5) Profile/Pricing editor: verify Profile, Production Weight/Time and Filament/Fixed Price are separate full-height tabs with all rows visible."
Write-Host "6) Receive tab: bounded Classic/Hybrid smoke only (5 Products / 5 images); Safe Stop and Failed reset must remain healthy."
Write-Host "7) Verify a MakerWorld URL auto-selects MakerWorld even if another Source was selected before paste."
Write-Host "8) Verify Product image cards are larger, multi-selection count is visible, and bulk delete/recover actions remain usable."
Write-Host "9) Verify Filament tabs are Filaments / Materials / Brands / Colors and editor identity fields are registry selections."
Write-Host "10) Verify a source-missing Product gets one explicit default Profile with owner defaults and PLA/PETG-family Filaments only."
Write-Host "11) Products: verify 'Receive Site Changes' can pull a newer clean Site revision and reports a conflict instead of overwriting dirty Local edits."
Write-Host "12) Verify a Site-only Product appears as a non-publishable Local mirror and cannot enter Batch publish until linked."
Write-Host "13) Site migrations are NOT applied by this gate. Production and Host remain out of scope."

if ($LaunchApp) {
    Step "11. START QT6 CATALOG CENTER"
    $env:CATALOG_DATA_ROOT = $CatalogDataRoot
    Start-Process -FilePath $Py -ArgumentList @("qt_launch.py") -WorkingDirectory $Catalog
    Write-Host "QT6_CATALOG_CENTER_LAUNCHED=YES" -ForegroundColor Green
}
