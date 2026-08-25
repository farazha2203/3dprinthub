param(
    [string]$ExpectedHead = "",
    [switch]$LaunchApp
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = "D:\projects\3DPrintHub"
$Catalog = "$Root\catalog_center"
$Py = "$Root\.venv\Scripts\python.exe"
$Branch = "agent/phase49-3i18-operator-bulk-ai-rebuild"

function Fail([string]$Message) {
    throw $Message
}

Set-Location $Root

Write-Host ""
Write-Host "=============================================="
Write-Host "3DPRINTHUB PHASE49.3I.28 LOCAL GATE"
Write-Host "NO PRODUCTION / NO MIGRATION / NO RESET"
Write-Host "=============================================="

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
if ($Dirty.Count -gt 0) { Fail "WORKTREE DIRTY - inspect it; do not reset/delete" }
if ($CurrentBranch -ne $Branch) { Fail "WRONG BRANCH" }
if ($Head -ne $Remote) { Fail "LOCAL/REMOTE HEAD MISMATCH - fetch/pull first" }
if ($ExpectedHead -and $Head -ne $ExpectedHead) { Fail "EXPECTED HEAD MISMATCH" }
if (-not (Test-Path -LiteralPath $Py)) { Fail "VENV PYTHON NOT FOUND: $Py" }

Write-Host ""
Write-Host "===== PYTHON COMPILE ====="
& $Py -m py_compile `
    "$Catalog\app\phase49_3i27_category_provider_bridge.py" `
    "$Catalog\app\phase49_3i26_operator_completion.py" `
    "$Catalog\app\phase49_3i26_runtime_patch.py" `
    "$Catalog\app\phase49_3i25_product_first_workflow.py" `
    "$Catalog\app\phase49_3i_pricing_modes.py" `
    "$Catalog\app\phase49_3h_image_limits.py"
if ($LASTEXITCODE -ne 0) { Fail "PY_COMPILE FAILED" }

Write-Host ""
Write-Host "===== FOCUSED REGRESSION ====="
Set-Location $Catalog
& $Py -m unittest -v `
    tests.test_phase49_3i28_exact_link_contract `
    tests.test_phase49_3i27_category_provider_bridge `
    tests.test_phase49_3i26_operator_completion `
    tests.test_phase49_3i25_product_first_workflow `
    tests.test_phase49_3i23_avalai_chat_contract `
    tests.test_phase49_3i22_tk_thread_bridge `
    tests.test_phase49_3i21_observable_ai_link_refresh `
    tests.test_phase49_3i20_visible_operator_panels `
    tests.test_phase49_3i19_source_identity `
    tests.test_phase49_3i18_operator_editing
if ($LASTEXITCODE -ne 0) { Fail "FOCUSED REGRESSION FAILED" }

Write-Host ""
Write-Host "===== LAUNCHER VERIFY ====="
& $Py launch.py --verify-only
if ($LASTEXITCODE -ne 0) { Fail "LAUNCH VERIFY FAILED" }

Set-Location $Root
$FinalHead = (& git rev-parse HEAD).Trim()
$FinalRemote = (& git rev-parse "origin/$Branch").Trim()
$FinalDirty = @(git status --porcelain --untracked-files=all)
if ($FinalHead -ne $FinalRemote) { Fail "FINAL LOCAL/REMOTE MISMATCH" }
if ($ExpectedHead -and $FinalHead -ne $ExpectedHead) { Fail "FINAL EXPECTED HEAD MISMATCH" }
if ($FinalDirty.Count -gt 0) { Fail "TESTS CHANGED WORKTREE" }

Write-Host ""
Write-Host "=============================================="
Write-Host "PHASE49_3I28_AUTOMATED_LOCAL_GATE=PASS"
Write-Host "HEAD=$FinalHead"
Write-Host "PRODUCTION_TOUCHED=NO"
Write-Host "=============================================="

if ($LaunchApp) {
    Start-Process -FilePath $Py -ArgumentList "launch.py" -WorkingDirectory $Catalog
    Write-Host "CATALOG_CENTER_LAUNCHED=YES"
}
