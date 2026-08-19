param(
    [switch]$LaunchApp
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RunnerVersion = "49.3D.1"
$Root = "D:\projects\3DPrintHub"
$Catalog = Join-Path $Root "catalog_center"
$Py = Join-Path $Root ".venv\Scripts\python.exe"
$ExpectedBranch = "epic/phase49-unified-product-slider-sync"
$BackupBase = "D:\projects\3dprinthub-backups\phase49-3d"
$CatalogData = "D:\projects\3dprinthub-catalog-manager"
$LegacyCatalogData = "D:\projects\3dprinthub_catalog_center"

function Step([string]$Title) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Fail([string]$Message) {
    Write-Host ""
    Write-Host "PHASE49.3D LOCAL GATE FAILED" -ForegroundColor Red
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

Step "00. PHASE49.3D WINDOWS LOCAL GATE"
Write-Host "Runner    = $RunnerVersion"
Write-Host "Project   = $Root"
Write-Host "Catalog   = $Catalog"
Write-Host "Branch    = $ExpectedBranch"
Write-Host "Production= NOT TOUCHED" -ForegroundColor Yellow

if (-not (Test-Path $Root)) { Fail "Project root not found: $Root" }
if (-not (Test-Path $Catalog)) { Fail "Catalog Center not found: $Catalog" }
if (-not (Test-Path $Py)) { Fail "Virtualenv Python not found: $Py" }

Step "01. CHECK RUNNING PROJECT PROCESSES"
$projectProcesses = @()
try {
    $projectProcesses = @(
        Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
            $cmd = [string]$_.CommandLine
            $cmd -and (
                ($cmd -match [regex]::Escape($Root)) -and
                (($cmd -match "launch\.py") -or ($cmd -match "manage\.py\s+runserver"))
            )
        }
    )
} catch {
    $projectProcesses = @()
    Write-Host "Process inspection warning: $($_.Exception.Message)" -ForegroundColor Yellow
}
if (@($projectProcesses).Count -gt 0) {
    $projectProcesses | Select-Object ProcessId, Name, CommandLine | Format-Table -AutoSize
    Fail "Catalog Center or Django runserver is still running. Close it normally, then run this gate again."
}
Write-Host "No active Catalog Center/runserver process detected." -ForegroundColor Green

Step "02. VERIFY GIT SOURCE AND CLEAN WORKTREE"
Push-Location $Root
try {
    $origin = (& git remote get-url origin).Trim()
    if ($LASTEXITCODE -ne 0) { Fail "Cannot read git origin." }
    Write-Host "origin = $origin"
    if ($origin -notmatch "farazha2203/3dprinthub(\.git)?$") {
        Fail "Unexpected origin: $origin"
    }

    $dirty = @(git status --porcelain --untracked-files=all)
    if ($LASTEXITCODE -ne 0) { Fail "git status failed." }
    if ($dirty.Count -gt 0) {
        Write-Host "Working tree changes:" -ForegroundColor Yellow
        $dirty | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
        Fail "WORKTREE_NOT_CLEAN. Nothing was reset or deleted. Review these files first."
    }
    Write-Host "Working tree is clean." -ForegroundColor Green
} finally {
    Pop-Location
}

Step "03. CREATE LOCAL BACKUP BEFORE PULL"
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Backup = Join-Path $BackupBase $Stamp
New-Item -ItemType Directory -Force -Path $Backup | Out-Null
$Transcript = Join-Path $Backup "phase49-3d-local-gate.log"
Start-Transcript -Path $Transcript -Force | Out-Null

try {
    $projectDb = Join-Path $Root "db.sqlite3"
    if (Test-Path $projectDb) {
        Copy-Item $projectDb (Join-Path $Backup "django-db.sqlite3") -Force
        Write-Host "Backed up: $projectDb" -ForegroundColor Green
    }

    $catalogDb = Join-Path $CatalogData "catalog.sqlite3"
    if (Test-Path $catalogDb) {
        Copy-Item $catalogDb (Join-Path $Backup "catalog.sqlite3") -Force
        Write-Host "Backed up: $catalogDb" -ForegroundColor Green
    }

    $catalogConfig = Join-Path $CatalogData "config.json"
    if (Test-Path $catalogConfig) {
        Copy-Item $catalogConfig (Join-Path $Backup "catalog-config.json") -Force
        Write-Host "Backed up: $catalogConfig" -ForegroundColor Green
    }

    $projectEnv = Join-Path $Root ".env"
    if (Test-Path $projectEnv) {
        Copy-Item $projectEnv (Join-Path $Backup "project.env.local-backup") -Force
        Write-Host "Backed up local .env (not printed, not committed)." -ForegroundColor Green
    }

    foreach ($candidate in @($CatalogData, $LegacyCatalogData)) {
        if (Test-Path $candidate) {
            $metaFile = Join-Path $Backup ("PERSISTENT_PATH_" + ([IO.Path]::GetFileName($candidate)) + ".txt")
            "Persistent data preserved in place: $candidate" | Set-Content -Path $metaFile -Encoding UTF8
        }
    }

    Step "04. FETCH / SWITCH / FAST-FORWARD PULL"
    Push-Location $Root
    try {
        Run-Native -File "git" -Arguments @("fetch", "--prune", "origin")
        $ExpectedHead = (& git rev-parse "origin/$ExpectedBranch").Trim()
        if ($LASTEXITCODE -ne 0 -or -not $ExpectedHead) { Fail "Cannot resolve remote Epic HEAD." }
        Write-Host "REMOTE_HEAD = $ExpectedHead"
        Run-Native -File "git" -Arguments @("switch", $ExpectedBranch)
        Run-Native -File "git" -Arguments @("pull", "--ff-only", "origin", $ExpectedBranch)

        $Head = (& git rev-parse HEAD).Trim()
        if ($LASTEXITCODE -ne 0) { Fail "git rev-parse HEAD failed." }
        Write-Host "HEAD = $Head"
        if ($Head -ne $ExpectedHead) {
            Fail "Unexpected HEAD. Expected $ExpectedHead but received $Head. Stop before testing."
        }

        $dirty = @(git status --porcelain --untracked-files=all)
        if ($dirty.Count -gt 0) {
            $dirty | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
            Fail "Worktree became dirty immediately after pull."
        }
    } finally {
        Pop-Location
    }

    Step "05. DEPENDENCIES"
    Push-Location $Root
    try {
        Run-Native -File $Py -Arguments @("-m", "pip", "install", "-r", "requirements.txt")
    } finally {
        Pop-Location
    }

    Step "06. COMPILE PHASE49.3D / RELATED PYTHON"
    Push-Location $Root
    try {
        Run-Native -File $Py -Arguments @(
            "-m", "compileall", "-q",
            "catalog_center\app\phase49_3d_workflow_hardening.py",
            "catalog_center\app\phase49_3d_image_signature.py",
            "catalog_center\app\phase49_3d_ai_ui_cleanup.py",
            "catalog_center\app\phase49_3c_persian_content.py",
            "catalog_center\app\phase49_3c_persian_translate_guard.py",
            "catalog_center\app\phase49_3c_image_pipeline.py",
            "catalog_center\app\phase49_3c_operator_recovery.py",
            "catalog_center\app\openai_content.py",
            "catalog_center\app\ai_providers.py",
            "catalog_center\launch.py",
            "store\management\commands\phase37_import_catalog_center.py"
        )
    } finally {
        Pop-Location
    }

    Step "07. DJANGO CHECK / MIGRATION CONTRACT - NO APPLY"
    Push-Location $Root
    try {
        Run-Native -File $Py -Arguments @("manage.py", "check")
        Run-Native -File $Py -Arguments @("manage.py", "makemigrations", "--check", "--dry-run")
        Run-Native -File $Py -Arguments @("manage.py", "migrate", "--plan")
        Write-Host "Phase49.3D has no new Django migration. No migrate command was executed." -ForegroundColor Green
    } finally {
        Pop-Location
    }

    Step "08. TARGETED DJANGO RANGE / WINDOWS->BATCH->DJANGO E2E"
    Push-Location $Root
    try {
        Run-Native -File $Py -Arguments @(
            "manage.py", "test",
            "store.test_phase49_3d_price_range",
            "store.test_phase49_unified_import_e2e",
            "-v", "2"
        )
    } finally {
        Pop-Location
    }

    Step "09. WINDOWS CATALOG CENTER TARGETED REGRESSIONS"
    Push-Location $Catalog
    try {
        Run-Native -File $Py -Arguments @("-m", "unittest", "-v", "tests.test_epic49_phase49_3d_workflow_hardening")
        Run-Native -File $Py -Arguments @("-m", "unittest", "-v", "tests.test_epic49_phase49_3d_ai_ui_cleanup")
        Run-Native -File $Py -Arguments @("-m", "unittest", "-v", "tests.test_epic49_phase49_3c_image_signature")
        Run-Native -File $Py -Arguments @("-m", "unittest", "-v", "tests.test_epic49_phase49_3c_persian_content")
        Run-Native -File $Py -Arguments @("-m", "unittest", "-v", "tests.test_epic49_phase49_3c_persian_translate_guard")
        Run-Native -File $Py -Arguments @("-m", "unittest", "-v", "tests.test_epic49_phase49_3c_operator_recovery")
        Run-Native -File $Py -Arguments @("-m", "unittest", "-v", "tests.test_phase49_3b_ai_diagnostics")
        Run-Native -File $Py -Arguments @("-m", "unittest", "-v", "tests.test_phase49_3b_diagnostics_identity")
        Run-Native -File $Py -Arguments @("-m", "unittest", "-v", "tests.test_phase49_3b_guided_wizard")
    } finally {
        Pop-Location
    }

    Step "10. EPIC49 DISCOVERY"
    Push-Location $Catalog
    try {
        Run-Native -File $Py -Arguments @("-m", "unittest", "discover", "-s", "tests", "-p", "test_*epic49*.py", "-v")
    } finally {
        Pop-Location
    }

    Step "11. LAUNCHER VERIFY-ONLY + REQUIRED MARKERS"
    Push-Location $Catalog
    try {
        $verify = & $Py launch.py --verify-only 2>&1
        $rc = $LASTEXITCODE
        $verify | ForEach-Object { Write-Host $_ }
        if ($rc -ne 0) { Fail "launch.py --verify-only failed with exit code $rc." }

        $requiredMarkers = @(
            "ACTIVE_VERSION=8.7.1",
            "EPIC49_GUIDED_WIZARD_7_STAGE=ENABLED",
            "EPIC49_3C_PERSIAN_CONTENT_GUARD=ENABLED",
            "EPIC49_3C_PERSIAN_TRANSLATE_GUARD=ENABLED",
            "EPIC49_3D_WORKSPACE_LAYOUT_FIX=ENABLED",
            "EPIC49_3D_AI_MODEL_PICKER=ENABLED",
            "EPIC49_3D_ACTIVE_PROVIDER_PERSISTENCE=ENABLED",
            "EPIC49_3D_AI_LEGACY_ACTIVATE_REMOVED=ENABLED",
            "EPIC49_3D_AUTO_AI_PREPARE=ENABLED",
            "EPIC49_3D_LOCAL_PUBLISH_PREFLIGHT=ENABLED",
            "EPIC49_3D_PRICE_RANGE_CONTRACT=ENABLED",
            "EPIC49_3D_IMAGE_LIMIT_PRESERVED=ENABLED",
            "EPIC49_3D_SEMANTIC_IMAGE_SIGNATURE=ENABLED",
            "ACTIVE_RELEASE_VERIFIED=OK"
        )

        $verifyText = ($verify -join "`n")
        foreach ($marker in $requiredMarkers) {
            if ($verifyText -notmatch [regex]::Escape($marker)) {
                Fail "Required launcher marker missing: $marker"
            }
        }
        Write-Host "All required Phase49.3D markers found." -ForegroundColor Green
    } finally {
        Pop-Location
    }

    Step "12. FULL DJANGO SUITE"
    Push-Location $Root
    try {
        Run-Native -File $Py -Arguments @("manage.py", "test", "-v", "1")
    } finally {
        Pop-Location
    }

    Step "13. FINAL GIT / DATABASE SAFETY CHECK"
    Push-Location $Root
    try {
        $Head2 = (& git rev-parse HEAD).Trim()
        if ($Head2 -ne $ExpectedHead) {
            Fail "HEAD changed during tests: $Head2"
        }

        $dirtyAfter = @(git status --porcelain --untracked-files=all)
        if ($dirtyAfter.Count -gt 0) {
            Write-Host "Post-test worktree changes:" -ForegroundColor Yellow
            $dirtyAfter | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
            Fail "Tests left tracked/untracked project changes. Nothing was deleted."
        }
    } finally {
        Pop-Location
    }

    Step "14. AUTOMATED LOCAL GATE PASSED"
    Write-Host "HEAD     = $Head2" -ForegroundColor Green
    Write-Host "BACKUP   = $Backup" -ForegroundColor Green
    Write-Host "LOG      = $Transcript" -ForegroundColor Green
    Write-Host "PRODUCTION UNTOUCHED" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Manual QA next:" -ForegroundColor Cyan
    Write-Host "1) Product Workspace opens with NO pack/grid TclError."
    Write-Host "2) AI Center: Radio Provider -> Search model (CHATGPT/GPT/Claude/...) -> select raw model -> Save active Provider/Model."
    Write-Host "3) Restart app: same Provider/Model must remain active."
    Write-Host "4) Test Connection must report the selected Provider/Model and real model count."
    Write-Host "5) Auto AI Prepare: incomplete real product fills Persian title/content/use description/SEO once; reopen unchanged must not spend another request."
    Write-Host "6) Price min/max: save, close, reopen and confirm both values."
    Write-Host "7) Set image limit=5 and refetch; more than 5 images must not be accepted."
    Write-Host "8) Complete readiness and run ONLY Local Publish. Blockers must show an explicit dialog; stale image metadata should auto-finalize."
    Write-Host "9) Verify Local Django Product/Profile/Store List/Detail/Hero/Admin."
    Write-Host "10) DO NOT use Production Publish before explicit approval."

    if ($LaunchApp) {
        Step "15. START CATALOG CENTER FOR MANUAL QA"
        Start-Process -FilePath $Py -ArgumentList @("launch.py") -WorkingDirectory $Catalog
        Write-Host "Catalog Center started for manual QA." -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "To launch after this gate:" -ForegroundColor Cyan
        Write-Host "& `"$Py`" `"$Catalog\launch.py`""
    }
}
finally {
    try { Stop-Transcript | Out-Null } catch {}
}
