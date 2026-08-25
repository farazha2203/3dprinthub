param(
    [switch]$LaunchApp
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Repo = "D:\projects\3DPrintHub"
$Catalog = Join-Path $Repo "catalog_center"
$Python = Join-Path $Repo ".venv\Scripts\python.exe"
$Branch = "agent/phase49-3i18-operator-bulk-ai-rebuild"

Set-Location $Repo

Write-Host ""
Write-Host "========================================"
Write-Host "PHASE49.3I.25 WINDOWS LOCAL GATE"
Write-Host "NO RESET / NO MIGRATION / NO PRODUCTION"
Write-Host "========================================"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Python venv not found: $Python"
}

$Origin = ([string](git remote get-url origin)).Trim()
if ($Origin -notmatch "farazha2203/3dprinthub(\.git)?$") {
    throw "Wrong repository origin: $Origin"
}

$Dirty = @(git status --porcelain --untracked-files=all)
if ($Dirty.Count -gt 0) {
    git status --short --branch
    throw "Worktree is dirty. Stop and inspect; nothing was reset or deleted."
}

git fetch --prune origin
if ($LASTEXITCODE -ne 0) { throw "git fetch failed" }

git switch $Branch
if ($LASTEXITCODE -ne 0) { throw "git switch failed" }

git pull --ff-only origin $Branch
if ($LASTEXITCODE -ne 0) { throw "git pull --ff-only failed" }

$Local = ([string](git rev-parse HEAD)).Trim()
$Remote = ([string](git rev-parse "origin/$Branch")).Trim()
if ($Local -ne $Remote) {
    throw "Local/remote HEAD mismatch: local=$Local remote=$Remote"
}

Write-Host "HEAD=$Local"

Set-Location $Catalog

& $Python -m py_compile `
    "app\phase49_3i25_product_first_workflow.py" `
    "app\phase49_3i_pricing_modes.py" `
    "app\phase49_diagnostics.py" `
    "app\runtime_logging.py" `
    "app\phase49_3i24_runtime_observability.py" `
    "app\phase49_3i23_avalai_chat_contract.py" `
    "app\phase49_3i22_tk_thread_bridge.py" `
    "app\phase49_3i21_observable_ai_link_refresh.py"
if ($LASTEXITCODE -ne 0) { throw "py_compile failed" }

& $Python -m unittest -v `
    tests.test_phase49_3i25_product_first_workflow `
    tests.test_phase49_3i23_avalai_chat_contract `
    tests.test_phase49_3i22_tk_thread_bridge `
    tests.test_phase49_3i21_observable_ai_link_refresh `
    tests.test_phase49_3i20_visible_operator_panels `
    tests.test_phase49_3i19_source_identity `
    tests.test_phase49_3i18_operator_editing
if ($LASTEXITCODE -ne 0) { throw "focused unittest gate failed" }

& $Python launch.py --verify-only
if ($LASTEXITCODE -ne 0) { throw "launcher verify failed" }

Set-Location $Repo
$DirtyAfter = @(git status --porcelain --untracked-files=all)
if ($DirtyAfter.Count -gt 0) {
    git status --short --branch
    throw "Tests changed the worktree. Stop and inspect."
}

Write-Host ""
Write-Host "PHASE49_3I25_AUTOMATED_LOCAL_GATE=PASS"
Write-Host "HEAD=$Local"
Write-Host "PRODUCTION_TOUCHED=NO"

if ($LaunchApp) {
    Set-Location $Catalog
    & $Python launch.py
}
