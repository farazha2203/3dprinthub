param(
    [switch]$LaunchApp
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RunnerVersion = "49.3H.0"
$Root = "D:\projects\3DPrintHub"
$Catalog = Join-Path $Root "catalog_center"
$Py = Join-Path $Root ".venv\Scripts\python.exe"
$BaseGate = Join-Path $Root "RUN_PHASE49_3G_LOCAL_GATE.ps1"

function Step([string]$Title) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Fail([string]$Message) {
    Write-Host ""
    Write-Host "PHASE49.3H LOCAL GATE FAILED" -ForegroundColor Red
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

Step "00. PHASE49.3H WINDOWS LOCAL GATE"
Write-Host "Runner     = $RunnerVersion"
Write-Host "Project    = $Root"
Write-Host "Catalog    = $Catalog"
Write-Host "Production = NOT TOUCHED" -ForegroundColor Yellow

if (-not (Test-Path $Root)) { Fail "Project root not found: $Root" }
if (-not (Test-Path $Catalog)) { Fail "Catalog Center not found: $Catalog" }
if (-not (Test-Path $Py)) { Fail "Virtualenv Python not found: $Py" }
if (-not (Test-Path $BaseGate)) { Fail "Phase49.3G base gate not found: $BaseGate" }

Step "01. VERIFY OPERATIONAL DOCUMENTATION"
$requiredDocs = @(
    "AGENTS.md",
    "docs\CURRENT_STATE.md",
    "docs\ROADMAP.md",
    "docs\PATHS.md",
    "docs\ERRORS.md",
    "docs\HOST_CONSTRAINTS.md",
    "docs\REQUESTS.md",
    "docs\phases\PHASE49_3H_SEO_EXECUTION_COST_IMAGE_LIMIT.md"
)
foreach ($relative in $requiredDocs) {
    if (-not (Test-Path (Join-Path $Root $relative))) {
        Fail "Required project documentation missing: $relative"
    }
}
Write-Host "PHASE49_3H_DOCS=OK" -ForegroundColor Green

Step "02. RUN FULL PHASE49.3G BASE GATE"
& $BaseGate
if ($LASTEXITCODE -ne 0) {
    Fail "Phase49.3G base gate failed. Phase49.3H stopped."
}

Step "03. VERIFY PHASE49.3H SOURCE EXISTS"
$requiredFiles = @(
    "catalog_center\app\phase49_3h_image_limits.py",
    "catalog_center\app\phase49_3h_cost_ledger.py",
    "catalog_center\app\phase49_3h_seo_execution.py",
    "catalog_center\tests\test_epic49_phase49_3h_image_limits.py",
    "catalog_center\tests\test_epic49_phase49_3h_cost_ledger.py",
    "catalog_center\tests\test_epic49_phase49_3h_seo_execution.py"
)
foreach ($relative in $requiredFiles) {
    if (-not (Test-Path (Join-Path $Root $relative))) {
        Fail "Required Phase49.3H file missing: $relative"
    }
}
Write-Host "Phase49.3H source/test files found." -ForegroundColor Green

Step "04. COMPILE PHASE49.3H"
Push-Location $Root
try {
    Run-Native -File $Py -Arguments @(
        "-m", "compileall", "-q",
        "catalog_center\app\phase49_3h_image_limits.py",
        "catalog_center\app\phase49_3h_cost_ledger.py",
        "catalog_center\app\phase49_3h_seo_execution.py",
        "catalog_center\launch.py"
    )
} finally {
    Pop-Location
}

Step "05. PHASE49.3H DEDICATED + PRIVACY/PROVENANCE TESTS"
Push-Location $Catalog
try {
    Run-Native -File $Py -Arguments @(
        "-m", "unittest", "-v",
        "tests.test_epic49_phase49_3h_image_limits",
        "tests.test_epic49_phase49_3h_cost_ledger",
        "tests.test_epic49_phase49_3h_seo_execution",
        "tests.test_epic49_phase49_3g_workspace_usability",
        "tests.test_epic49_phase49_3g_commerce_provenance",
        "tests.test_epic49_phase49_3c_image_signature"
    )
} finally {
    Pop-Location
}

Step "06. VERIFY PHASE49.3H LAUNCH MARKERS"
Push-Location $Catalog
try {
    $verifyText = Invoke-NativeCapture -File $Py -Arguments @("launch.py", "--verify-only")
    Write-Host $verifyText
    $requiredMarkers = @(
        "EPIC49_3H_SEO_EXECUTION_CONSOLE=ENABLED",
        "EPIC49_3H_RESULT_ERROR_DRAWER=ENABLED",
        "EPIC49_3H_AI_COST_LEDGER=ENABLED",
        "EPIC49_3H_PUBLISH_COST_RECEIPT=ENABLED",
        "EPIC49_3H_IMAGE_LIMIT_DEFAULT_10=ENABLED",
        "EPIC49_3H_IMAGE_LIMIT_HARD_MAX_20=ENABLED",
        "EPIC49_3H_PERSISTED_IMAGE_CAP=ENABLED",
        "EPIC49_3F_SELECTED_IMAGE_TEXT_ONLY_AI=ENABLED",
        "EPIC49_3G_MANUAL_OVERRIDE_GUARD=ENABLED",
        "ACTIVE_RELEASE_VERIFIED=OK"
    )
    foreach ($marker in $requiredMarkers) {
        if ($verifyText -notmatch [regex]::Escape($marker)) {
            Fail "Required Phase49.3H marker missing: $marker"
        }
    }
    Write-Host "PHASE49_3H_LAUNCH_MARKERS=OK" -ForegroundColor Green
} finally {
    Pop-Location
}

Step "07. DJANGO MIGRATION SAFETY"
Push-Location $Root
try {
    Run-Native -File $Py -Arguments @("manage.py", "makemigrations", "--check", "--dry-run")
    Write-Host "PHASE49_3H_DJANGO_MIGRATION=NONE" -ForegroundColor Green
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

Step "09. PHASE49.3H AUTOMATED LOCAL GATE PASSED"
Write-Host "Runner     = $RunnerVersion" -ForegroundColor Green
Write-Host "Production = UNTOUCHED" -ForegroundColor Yellow
Write-Host ""
Write-Host "Manual QA:" -ForegroundColor Cyan
Write-Host "1) In Scan/Direct Link, image limit defaults to 10 and cannot exceed 20."
Write-Host "2) Product Refetch image limit accepts 1..20; legacy 60/100 displays/executes as 20 maximum."
Write-Host "3) Test a source with >20 candidates: persisted/selected/downloaded images must not exceed chosen 10/20."
Write-Host "4) Run Product AI/SEO: progress shows connection, send, response, validation/save stages."
Write-Host "5) Successful operation closes transient progress and leaves result/log drawer visible in related section."
Write-Host "6) Force a safe error (e.g. invalid provider setting without exposing key): error/result stays visible with log/retry guidance."
Write-Host "7) Result shows Provider/Model, elapsed time, request IDs/tokens and known/unknown cost truthfully."
Write-Host "8) Product Publish area shows aggregate internal AI/SEO cost and freezes pre-publish cost receipt."
Write-Host "9) Image SEO remains selected-only + text-only; no image URL/file/bytes reach AI."
Write-Host "10) 49.3G manual override/AI-disable still protects operator fields."
Write-Host "11) Do LOCAL PUBLISH ONLY after visual/data QA. Do not use Production Publish."

if ($LaunchApp) {
    Step "10. START CATALOG CENTER FOR PHASE49.3H MANUAL QA"
    Start-Process -FilePath $Py -ArgumentList @("launch.py") -WorkingDirectory $Catalog
    Write-Host "Catalog Center started." -ForegroundColor Green
}
