param(
    [string]$ExpectedHead = "",
    [switch]$BuildExe,
    [switch]$LaunchApp
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = "D:\projects\3DPrintHub"
$Catalog = "$Root\catalog_center"
$Py = "$Root\.venv\Scripts\python.exe"
$Branch = "agent/phase49-3i18-operator-bulk-ai-rebuild"
$ExpectedVersion = "8.9.5"
$ExpectedBuild = "2026.08.27.7"

function Fail([string]$Message) {
    throw $Message
}

Set-Location $Root

Write-Host ""
Write-Host "=================================================="
Write-Host "3DPRINTHUB PHASE49.3I.31-37 / WINDOWS 8.9.5 GATE"
Write-Host "NO PRODUCTION / NO MIGRATION / NO RESET / NO STASH"
Write-Host "=================================================="

$Origin = (& git remote get-url origin).Trim()
$Dirty = @(git status --porcelain --untracked-files=all)
$CurrentBranch = (& git branch --show-current).Trim()
$Head = (& git rev-parse HEAD).Trim()
$Remote = (& git rev-parse "origin/$Branch").Trim()

Write-Host "ORIGIN=$Origin"
Write-Host "BRANCH=$CurrentBranch"
Write-Host "LOCAL_HEAD=$Head"
Write-Host "REMOTE_HEAD=$Remote"

if ($Origin -notmatch "farazha2203/3dprinthub(\.git)?$") { Fail "WRONG REPOSITORY" }
if ($Dirty.Count -gt 0) { Fail "WORKTREE DIRTY - inspect it; do not reset/stash/delete" }
if ($CurrentBranch -ne $Branch) { Fail "WRONG BRANCH" }
if ($Head -ne $Remote) { Fail "LOCAL/REMOTE HEAD MISMATCH - fetch/pull first" }
if ($ExpectedHead -and $Head -ne $ExpectedHead) { Fail "EXPECTED HEAD MISMATCH" }
if (-not (Test-Path -LiteralPath $Py)) { Fail "VENV PYTHON NOT FOUND: $Py" }

$Version = (& $Py -c "import sys; sys.path.insert(0, r'$Catalog'); from app.version import APP_VERSION; print(APP_VERSION)").Trim()
$Build = (& $Py -c "import sys; sys.path.insert(0, r'$Catalog'); from app.version import BUILD_ID; print(BUILD_ID)").Trim()
if ($LASTEXITCODE -ne 0) { Fail "VERSION/BUILD READ FAILED" }
if ($Version -ne $ExpectedVersion) { Fail "VERSION MISMATCH: $Version != $ExpectedVersion" }
if ($Build -ne $ExpectedBuild) { Fail "BUILD MISMATCH: $Build != $ExpectedBuild" }
Write-Host "APP_VERSION=$Version"
Write-Host "BUILD_ID=$Build"

Write-Host ""
Write-Host "===== PYTHON COMPILE ====="
& $Py -m py_compile `
    "$Catalog\app\phase49_3i36_stage_finalization.py" `
    "$Catalog\app\phase49_3i37_seven_stage_ai.py" `
    "$Catalog\app\phase49_3i35_operator_ledger.py" `
    "$Catalog\app\phase49_3i35_resilient_ai.py" `
    "$Catalog\app\phase49_3i35_readiness_review.py" `
    "$Catalog\app\phase49_3i34_profile_matrix.py" `
    "$Catalog\app\phase49_3i33_ai_core.py" `
    "$Catalog\app\phase49_3i33_operator_workflow.py" `
    "$Catalog\app\phase49_3i32_source_url_guard.py" `
    "$Catalog\app\phase49_3i31_smart_link_bulk_ai.py" `
    "$Catalog\app\phase49_3i29_windows_performance_ai.py" `
    "$Catalog\app\phase49_3i_pricing_modes.py" `
    "$Catalog\app\phase49_3i17_single_active_ai_runtime.py" `
    "$Catalog\app\phase49_3i18_operator_editing.py" `
    "$Catalog\app\phase49_3i25_product_first_workflow.py" `
    "$Catalog\tests\test_phase49_3i36_stage_finalization.py" `
    "$Catalog\tests\test_phase49_3i37_seven_stage_ai.py" `
    "$Catalog\tests\test_phase49_3i35_operator_workflow.py" `
    "$Catalog\tests\test_phase49_3i34_profile_matrix.py" `
    "$Catalog\tests\test_phase49_3i33_operator_workflow.py" `
    "$Catalog\tests\test_phase49_3i32_source_url_guard.py" `
    "$Catalog\launch.py" `
    "$Catalog\portable_entry.py" `
    "$Catalog\build_portable_exe.py"
if ($LASTEXITCODE -ne 0) { Fail "PY_COMPILE FAILED" }

Write-Host ""
Write-Host "===== SOURCE URL INVARIANT ====="
& $Py -c "import sys; sys.path.insert(0, r'$Catalog'); from app.phase49_3i32_source_url_guard import resolve_source_url_for_save as r; u='https://example.com/model/1'; assert r(u,'','') == u; assert r(u,u,'https://example.com/model/2').endswith('/2'); print('PHASE49_3I32_SOURCE_URL_GUARD=PASS')"
if ($LASTEXITCODE -ne 0) { Fail "SOURCE URL GUARD FAILED" }

Write-Host ""
Write-Host "===== FOCUSED REGRESSION ====="
Set-Location $Catalog
& $Py -m unittest -v `
    tests.test_phase49_3i36_stage_finalization `
    tests.test_phase49_3i37_seven_stage_ai `
    tests.test_phase49_3i35_operator_workflow `
    tests.test_phase49_3i34_profile_matrix `
    tests.test_phase49_3i33_operator_workflow `
    tests.test_phase49_3i32_source_url_guard `
    tests.test_phase49_3i31_smart_link_bulk_ai `
    tests.test_epic49_phase49_3i29_windows_performance_ai `
    tests.test_phase49_3i28_exact_link_contract `
    tests.test_phase49_3i27_category_provider_bridge `
    tests.test_phase49_3i26_operator_completion `
    tests.test_phase49_3i25_product_first_workflow `
    tests.test_phase49_3i24_runtime_observability `
    tests.test_phase49_3i23_avalai_chat_contract `
    tests.test_phase49_3i22_tk_thread_bridge `
    tests.test_phase49_3i21_observable_ai_link_refresh `
    tests.test_phase49_3i20_visible_operator_panels `
    tests.test_phase49_3i19_source_identity `
    tests.test_phase49_3i18_operator_editing `
    tests.test_epic49_phase49_3i17_single_active_ai_runtime `
    tests.test_portable_exe_contract `
    tests.test_v854_launcher
if ($LASTEXITCODE -ne 0) { Fail "FOCUSED REGRESSION FAILED" }

Write-Host ""
Write-Host "===== LAUNCHER VERIFY ====="
$LaunchOutput = (& $Py launch.py --verify-only 2>&1 | Out-String)
if ($LASTEXITCODE -ne 0) {
    Write-Host $LaunchOutput
    Fail "LAUNCH VERIFY FAILED"
}
Write-Host $LaunchOutput
foreach ($Marker in @(
    "ACTIVE_VERSION=8.9.5",
    "EPIC49_3I29_PRODUCTS_PAGE_PAGED_48=ENABLED",
    "EPIC49_3I29_DEFERRED_GLOBAL_REFRESH=ENABLED",
    "EPIC49_3I31_SMART_LINK_AI=ENABLED",
    "EPIC49_3I31_BATCH_SELECTED_PRODUCTS_AI=ENABLED",
    "EPIC49_3I31_AI_TITLE_TEXT_ONLY=ENABLED",
    "EPIC49_3I31_AI_SELECTED_IMAGE_SEO=ENABLED",
    "EPIC49_3I33_CONSOLIDATED_PRODUCT_AI=ENABLED",
    "EPIC49_3I33_LIVE_LINK_AI=ENABLED",
    "EPIC49_3I33_SAVED_DATA_AI=ENABLED",
    "EPIC49_3I33_SCREENSHOT_VISION_AI=ENABLED",
    "EPIC49_3I33_REPAIR_AI=ENABLED",
    "EPIC49_3I33_OPERATOR_MATERIAL_COLOR_ONLY=ENABLED",
    "EPIC49_3I33_EXPLICIT_PRODUCTS_REFRESH=ENABLED",
    "EPIC49_3I33_SINGLE_CARD_UPDATE=ENABLED",
    "EPIC49_3I33_IMAGE_FILE_METADATA=ENABLED",
    "EPIC49_3I33_RUNTIME_TELEMETRY=ENABLED",
    "EPIC49_3I34_PROFILE_MATRIX=ENABLED",
    "EPIC49_3I34_PROFILE_CLONE=ENABLED",
    "EPIC49_3I34_SIZE_WEIGHT_DEPENDENCY=ENABLED",
    "EPIC49_3I34_PROFILE_PRICE_AUTHORITY=ENABLED",
    "EPIC49_3I34_DESKTOP_STORE_SYNC=ENABLED",
    "EPIC49_3I35_OPERATOR_LEDGER=ENABLED",
    "EPIC49_3I35_BRAND_AWARE_FILAMENT_OFFERS=ENABLED",
    "EPIC49_3I35_RESILIENT_AI_RETRY_FAILOVER=ENABLED",
    "EPIC49_3I35_MANUAL_SEO_SOURCE_REVIEW=ENABLED",
    "EPIC49_3I35_LOCAL_PROFILE_SNAPSHOT_AUTHORITY=ENABLED",
    "EPIC49_3I36_SEVEN_STAGE_FINALIZATION=ENABLED",
    "EPIC49_3I36_AI_UNLOCKED_STAGE_ONLY=ENABLED",
    "EPIC49_3I36_LOCKED_PROFILE_COMMERCE_GUARD=ENABLED",
    "EPIC49_3I36_AI_STATE_NO_NETWORK_HYDRATION=ENABLED",
    "EPIC49_3I36_SEMANTIC_TITLE_GUARD=ENABLED",
    "EPIC49_3I37_SEVEN_STAGE_AI_ORCHESTRATOR=ENABLED",
    "EPIC49_3I37_PERSISTED_SOURCE_MODE=ENABLED",
    "EPIC49_3I37_SCREENSHOT_SELECTED_FOR_SITE=ENABLED",
    "EPIC49_3I37_STAGE_BY_STAGE_APPLY=ENABLED",
    "EPIC49_3I37_SEO_LANGUAGE_GUARD=ENABLED",
    "ACTIVE_RELEASE_VERIFIED=OK"
)) {
    if ($LaunchOutput -notmatch [regex]::Escape($Marker)) { Fail "MISSING LAUNCHER MARKER: $Marker" }
}

Set-Location $Root
$FinalHead = (& git rev-parse HEAD).Trim()
$FinalRemote = (& git rev-parse "origin/$Branch").Trim()
$FinalDirty = @(git status --porcelain --untracked-files=all)
if ($FinalHead -ne $FinalRemote) { Fail "FINAL LOCAL/REMOTE MISMATCH" }
if ($ExpectedHead -and $FinalHead -ne $ExpectedHead) { Fail "FINAL EXPECTED HEAD MISMATCH" }
if ($FinalDirty.Count -gt 0) { Fail "TESTS CHANGED WORKTREE" }

Write-Host ""
Write-Host "=================================================="
Write-Host "PHASE49_3I31_37_AUTOMATED_LOCAL_GATE=PASS"
Write-Host "HEAD=$FinalHead"
Write-Host "APP_VERSION=$ExpectedVersion"
Write-Host "BUILD_ID=$ExpectedBuild"
Write-Host "SOURCE_URL_GUARD=PASS"
Write-Host "PRODUCTION_TOUCHED=NO"
Write-Host "=================================================="

if ($BuildExe) {
    Set-Location $Catalog
    Write-Host ""
    Write-Host "===== PORTABLE EXE BUILD / SELF VERIFY ====="
    & $Py build_portable_exe.py --python $Py
    if ($LASTEXITCODE -ne 0) { Fail "PORTABLE EXE BUILD FAILED" }
    Write-Host "PHASE49_3I31_37_PORTABLE_BUILD=PASS"
}

if ($LaunchApp) {
    Start-Process -FilePath $Py -ArgumentList "launch.py" -WorkingDirectory $Catalog
    Write-Host "CATALOG_CENTER_LAUNCHED=YES"
}
