param(
    [switch]$LaunchApp
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RunnerVersion = "49.3F.0"
$Root = "D:\projects\3DPrintHub"
$Catalog = Join-Path $Root "catalog_center"
$Py = Join-Path $Root ".venv\Scripts\python.exe"
$ExpectedBranch = "epic/phase49-unified-product-slider-sync"
$BaseGate = Join-Path $Root "RUN_PHASE49_3E_LOCAL_GATE.ps1"
$BackupBase = "D:\projects\3dprinthub-backups\phase49-3f"
$CatalogData = "D:\projects\3dprinthub-catalog-manager"

function Step([string]$Title) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Fail([string]$Message) {
    Write-Host ""
    Write-Host "PHASE49.3F LOCAL GATE FAILED" -ForegroundColor Red
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

Step "00. PHASE49.3F WINDOWS LOCAL GATE"
Write-Host "Runner     = $RunnerVersion"
Write-Host "Project    = $Root"
Write-Host "Catalog    = $Catalog"
Write-Host "Branch     = $ExpectedBranch"
Write-Host "Production = NOT TOUCHED" -ForegroundColor Yellow

if (-not (Test-Path $Root)) { Fail "Project root not found: $Root" }
if (-not (Test-Path $Catalog)) { Fail "Catalog Center not found: $Catalog" }
if (-not (Test-Path $Py)) { Fail "Virtualenv Python not found: $Py" }
if (-not (Test-Path $BaseGate)) { Fail "Phase49.3E base gate not found: $BaseGate" }

Step "01. RUN FULL PHASE49.3E -> 49.3D BASE GATES"
& $BaseGate
if ($LASTEXITCODE -ne 0) {
    Fail "Phase49.3E base gate failed. Phase49.3F stopped before migrations."
}

Step "02. VERIFY BRANCH / REMOTE HEAD / CLEAN WORKTREE"
Push-Location $Root
try {
    $branch = (& git branch --show-current).Trim()
    if ($branch -ne $ExpectedBranch) { Fail "Unexpected branch: $branch" }
    $localHead = (& git rev-parse HEAD).Trim()
    $remoteHead = (& git rev-parse "origin/$ExpectedBranch").Trim()
    if ($localHead -ne $remoteHead) {
        Fail "Local HEAD is not the exact remote Epic HEAD. local=$localHead remote=$remoteHead"
    }
    $dirty = @(git status --porcelain --untracked-files=all)
    if ($dirty.Count -gt 0) {
        $dirty | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
        Fail "Worktree is not clean. Nothing was reset or deleted."
    }
    Write-Host "HEAD = $localHead" -ForegroundColor Green
} finally {
    Pop-Location
}

Step "03. PHASE49.3F PRE-MIGRATION BACKUP"
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Backup = Join-Path $BackupBase $Stamp
New-Item -ItemType Directory -Force -Path $Backup | Out-Null
$Transcript = Join-Path $Backup "phase49-3f-local-gate.log"
Start-Transcript -Path $Transcript -Force | Out-Null

try {
    $projectDb = Join-Path $Root "db.sqlite3"
    if (Test-Path $projectDb) {
        Copy-Item $projectDb (Join-Path $Backup "django-db.sqlite3") -Force
        Write-Host "Django DB backup = $Backup\django-db.sqlite3" -ForegroundColor Green
    }
    $catalogDb = Join-Path $CatalogData "catalog.sqlite3"
    if (Test-Path $catalogDb) {
        Copy-Item $catalogDb (Join-Path $Backup "catalog.sqlite3") -Force
        Write-Host "Catalog DB backup = $Backup\catalog.sqlite3" -ForegroundColor Green
    }
    $catalogConfig = Join-Path $CatalogData "config.json"
    if (Test-Path $catalogConfig) {
        Copy-Item $catalogConfig (Join-Path $Backup "catalog-config.json") -Force
    }
    @(
        "Backup created before Phase49.3F migration apply.",
        "Project=$Root",
        "PersistentCatalog=$CatalogData",
        "Production=UNTOUCHED"
    ) | Set-Content -Path (Join-Path $Backup "BACKUP_CONTEXT.txt") -Encoding UTF8

    Step "04. VERIFY REQUIRED PHASE49.3F FILES"
    $requiredFiles = @(
        "store\phase49_3f_pricing.py",
        "store\phase49_3f_pricing_finalize.py",
        "store\phase49_3f_admin.py",
        "store\migrations\0033_phase49_3f_pricing_intelligence.py",
        "website\migrations\0023_phase49_3f_material_runtime_rates.py",
        "catalog_center\app\phase49_3f_gemini_provider.py",
        "catalog_center\app\phase49_3f_ai_experience.py",
        "catalog_center\app\phase49_3f_selected_image_ai.py",
        "catalog_center\app\phase49_3f_product_intelligence.py",
        "catalog_center\app\phase49_3f_runtime_trace.py",
        "catalog_center\app\phase49_3f_workspace.py",
        "catalog_center\app\phase49_3f_source_refresh_guard.py",
        "store\test_phase49_3f_pricing.py",
        "catalog_center\tests\test_phase49_3f_product_intelligence.py"
    )
    foreach ($relative in $requiredFiles) {
        if (-not (Test-Path (Join-Path $Root $relative))) {
            Fail "Required Phase49.3F file missing: $relative"
        }
    }
    Write-Host "Required Phase49.3F source/test files found." -ForegroundColor Green

    Step "05. COMPILE PHASE49.3F SURFACES"
    Push-Location $Root
    try {
        Run-Native -File $Py -Arguments @(
            "-m", "compileall", "-q",
            "store\phase49_3f_pricing.py",
            "store\phase49_3f_pricing_finalize.py",
            "store\phase49_3f_admin.py",
            "catalog_center\app\phase49_3f_gemini_provider.py",
            "catalog_center\app\phase49_3f_ai_experience.py",
            "catalog_center\app\phase49_3f_selected_image_ai.py",
            "catalog_center\app\phase49_3f_product_intelligence.py",
            "catalog_center\app\phase49_3f_runtime_trace.py",
            "catalog_center\app\phase49_3f_workspace.py",
            "catalog_center\app\phase49_3f_source_refresh_guard.py",
            "catalog_center\launch.py"
        )
    } finally {
        Pop-Location
    }

    Step "06. DJANGO CHECK + MIGRATION SAFETY BEFORE APPLY"
    Push-Location $Root
    try {
        Run-Native -File $Py -Arguments @("manage.py", "check")
        Run-Native -File $Py -Arguments @("manage.py", "makemigrations", "--check", "--dry-run")
        Run-Native -File $Py -Arguments @("manage.py", "migrate", "--plan")

        $migrationFiles = @(
            "store\migrations\0033_phase49_3f_pricing_intelligence.py",
            "website\migrations\0023_phase49_3f_material_runtime_rates.py"
        )
        $forbidden = "DeleteModel|RemoveField|RunSQL|RunPython|SeparateDatabaseAndState|DROP\s+TABLE|TRUNCATE|DELETE\s+FROM"
        foreach ($migration in $migrationFiles) {
            $text = Get-Content -Raw -Path (Join-Path $Root $migration)
            if ($text -match $forbidden) {
                Fail "Destructive migration marker detected in $migration"
            }
            if ($text -notmatch "migrations\.AddField") {
                Fail "Expected additive AddField migration contract missing in $migration"
            }
        }
        Write-Host "PHASE49_3F_MIGRATION_SAFETY=ADD_FIELD_ONLY" -ForegroundColor Green
    } finally {
        Pop-Location
    }

    Step "07. APPLY ONLY PHASE49.3F ADDITIVE MIGRATIONS"
    Push-Location $Root
    try {
        Run-Native -File $Py -Arguments @("manage.py", "migrate", "store", "0033_phase49_3f_pricing_intelligence")
        Run-Native -File $Py -Arguments @("manage.py", "migrate", "website", "0023_phase49_3f_material_runtime_rates")
        $storeMigrations = (& $Py manage.py showmigrations store 2>&1) -join "`n"
        $websiteMigrations = (& $Py manage.py showmigrations website 2>&1) -join "`n"
        if ($LASTEXITCODE -ne 0) { Fail "showmigrations failed." }
        if ($storeMigrations -notmatch "\[X\]\s+0033_phase49_3f_pricing_intelligence") {
            Fail "Store 0033 is not applied."
        }
        if ($websiteMigrations -notmatch "\[X\]\s+0023_phase49_3f_material_runtime_rates") {
            Fail "Website 0023 is not applied."
        }
        Write-Host "PHASE49_3F_MIGRATIONS_APPLIED=OK" -ForegroundColor Green
    } finally {
        Pop-Location
    }

    Step "08. PHASE49.3F DJANGO PRICING / PUBLIC UX / ADMIN TESTS"
    Push-Location $Root
    try {
        Run-Native -File $Py -Arguments @(
            "manage.py", "test",
            "store.test_phase49_3f_pricing",
            "store.test_phase49_unified_import_e2e",
            "store.test_epic49_operator_publish",
            "-v", "2"
        )
    } finally {
        Pop-Location
    }

    Step "09. PHASE49.3F WINDOWS AI / PRIVACY / TRACE / SOURCE GUARD TESTS"
    Push-Location $Catalog
    try {
        Run-Native -File $Py -Arguments @("-m", "unittest", "-v", "tests.test_phase49_3f_product_intelligence")
        Run-Native -File $Py -Arguments @("-m", "unittest", "-v", "tests.test_epic49_phase49_3e_ai_task_center")
        Run-Native -File $Py -Arguments @("-m", "unittest", "discover", "-s", "tests", "-p", "test_*epic49*.py", "-v")
    } finally {
        Pop-Location
    }

    Step "10. LAUNCHER VERIFY + PHASE49.3F MARKERS"
    Push-Location $Catalog
    try {
        $verify = & $Py launch.py --verify-only 2>&1
        $rc = $LASTEXITCODE
        $verify | ForEach-Object { Write-Host $_ }
        if ($rc -ne 0) { Fail "launch.py --verify-only failed with exit code $rc." }
        $verifyText = ($verify -join "`n")
        $requiredMarkers = @(
            "EPIC49_3F_SELECTED_IMAGE_TEXT_ONLY_AI=ENABLED",
            "EPIC49_3F_UNSELECTED_IMAGE_METADATA_PRESERVED=ENABLED",
            "EPIC49_3F_AI_PROGRESS_TIMEOUT=ENABLED",
            "EPIC49_3F_SCROLLABLE_AI_CENTER=ENABLED",
            "EPIC49_3F_GOOGLE_GEMINI_DIRECT=ENABLED",
            "EPIC49_3F_RUNTIME_TRACE=ENABLED",
            "EPIC49_3F_SOURCE_GROUNDED_TECHNICAL_AI=ENABLED",
            "EPIC49_3F_DYNAMIC_PRICING=ENABLED",
            "ACTIVE_RELEASE_VERIFIED=OK"
        )
        foreach ($marker in $requiredMarkers) {
            if ($verifyText -notmatch [regex]::Escape($marker)) {
                Fail "Required Phase49.3F launcher marker missing: $marker"
            }
        }
        Write-Host "PHASE49_3F_LAUNCH_MARKERS=OK" -ForegroundColor Green
    } finally {
        Pop-Location
    }

    Step "11. FULL DJANGO REGRESSION SUITE"
    Push-Location $Root
    try {
        Run-Native -File $Py -Arguments @("manage.py", "test", "-v", "1")
    } finally {
        Pop-Location
    }

    Step "12. FINAL DJANGO / MIGRATION / GIT SAFETY"
    Push-Location $Root
    try {
        Run-Native -File $Py -Arguments @("manage.py", "check")
        Run-Native -File $Py -Arguments @("manage.py", "makemigrations", "--check", "--dry-run")
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

    Step "13. PHASE49.3F AUTOMATED LOCAL GATE PASSED"
    Write-Host "Runner     = $RunnerVersion" -ForegroundColor Green
    Write-Host "Backup     = $Backup" -ForegroundColor Green
    Write-Host "Log        = $Transcript" -ForegroundColor Green
    Write-Host "Production = UNTOUCHED" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Manual QA after automated PASS:" -ForegroundColor Cyan
    Write-Host "1) AI Center: scroll vertically/horizontally; sticky Provider/Model + Save/Test/Log buttons remain visible."
    Write-Host "2) Google Gemini Direct: enter/store AI Studio key, fetch models, search Gemini Flash-Lite/Lite, select and save active model."
    Write-Host "3) Test active AI: UI must show connecting -> connected/failed; connection timeout is 30 seconds."
    Write-Host "4) Image SEO: select only 1-2 product images; AI must edit only those selected image metadata records and must not send images/URLs."
    Write-Host "5) Unselect another image with existing metadata; confirm it remains unchanged after Image SEO/finalize."
    Write-Host "6) Open Runtime Log folder and confirm operator/workstation/session/product/provider/model/timing/error records exist with no API secret."
    Write-Host "7) Technical intelligence: use source refresh + AI; AI must run only after last_refetched_at changes and show operator review before save."
    Write-Host "8) Pricing: enter material kg price, print hourly rate, supervision rate, part/support weights, support multiplier, quality durations, assembly fee."
    Write-Host "9) Dynamic preview example: PLA 2,600,000/kg + 100g part + 50g support x2 + 3h x150,000 + 3h x50,000 = 1,120,000 Toman before extras/shipping."
    Write-Host "10) LOCAL PUBLISH ONLY one real product. Site must show Persian product/availability labels, no Username attribution, compact title/summary, technical summary and transparent price breakdown."
    Write-Host "11) Add selected variant to Cart; Cart/Checkout unit price must equal Product Detail calculated price."
    Write-Host "12) Do NOT use Production Publish in this QA. Production remains untouched until explicit approval."

    if ($LaunchApp) {
        Step "14. START CATALOG CENTER FOR PHASE49.3F MANUAL QA"
        Start-Process -FilePath $Py -ArgumentList @("launch.py") -WorkingDirectory $Catalog
        Write-Host "Catalog Center started." -ForegroundColor Green
    }
} finally {
    try { Stop-Transcript | Out-Null } catch {}
}
