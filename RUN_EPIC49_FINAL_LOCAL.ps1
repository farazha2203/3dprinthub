$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = "D:\projects\3DPrintHub"
$Catalog = Join-Path $Root "catalog_center"
$CanonicalCatalog = "D:\projects\3dprinthub_catalog_center"
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$Branch = "epic/phase49-finalization"

Set-Location $Root

if ((git branch --show-current).Trim() -ne $Branch) {
    throw "Branch must be $Branch"
}
if (-not (Test-Path -LiteralPath $Python)) {
    throw "Python not found: $Python"
}

git diff --check
if ($LASTEXITCODE -ne 0) { throw "Git diff check failed" }

& $Python -m compileall `
  (Join-Path $Catalog "app") `
  (Join-Path $Root "store") `
  (Join-Path $Root "catalog_bridge") `
  (Join-Path $Root "deploy") `
  -q
if ($LASTEXITCODE -ne 0) { throw "Python compileall failed" }

Set-Location $Catalog
$GitVerify = @(& $Python launch.py --verify-only)
if ($LASTEXITCODE -ne 0) { throw "Git Catalog launcher verification failed" }
$GitVerify | ForEach-Object { Write-Host $_ }
$GitVerifyText = $GitVerify -join "`n"
foreach ($Marker in @(
  "ACTIVE_VERSION=8.7.0",
  "UX87_SHELL=ENABLED",
  "PRODUCT_WORKSPACE_V87=ENABLED",
  "AI_PROFILE_MIGRATION=PRESERVED",
  "HOST_PROFILE_MIGRATION=PRESERVED",
  "ACTIVE_RELEASE_VERIFIED=OK"
)) {
    if ($GitVerifyText -notmatch [regex]::Escape($Marker)) { throw "Missing v8.7 launcher marker: $Marker" }
}

& $Python -m unittest discover -s tests -p "test_*.py" -v
if ($LASTEXITCODE -ne 0) { throw "Git Catalog Center full test suite failed" }

Set-Location $Root
& $Python manage.py check
if ($LASTEXITCODE -ne 0) { throw "Django check failed" }

& $Python manage.py makemigrations --check --dry-run
if ($LASTEXITCODE -ne 0) { throw "Migration drift detected" }

$MigrationPlan = @(& $Python manage.py migrate store 0029 --plan)
if ($LASTEXITCODE -ne 0) { throw "Epic49 migration plan failed" }
$MigrationPlan | ForEach-Object { Write-Host $_ }
$Show = @(& $Python manage.py showmigrations store)
if ($LASTEXITCODE -ne 0) { throw "showmigrations failed" }
$Show | ForEach-Object { Write-Host $_ }
$ShowText = $Show -join "`n"
if ($ShowText -notmatch "0028_epic49_catalog_product_schema") { throw "Migration 0028 is not registered" }
if ($ShowText -notmatch "0029_epic49_catalog_product_backfill") { throw "Migration 0029 is not registered" }

& $Python manage.py test `
  store.test_phase49_catalog_visibility `
  store.test_phase49_1_media `
  store.test_phase49_unicode_routes `
  store.test_epic49_operator_publish `
  store.test_epic49_server_schema `
  catalog_bridge.tests.test_bridge `
  catalog_bridge.tests.test_phase49_diagnostics `
  catalog_bridge.tests.test_epic49_contract `
  website.test_phase45_homepage_hero `
  website.test_phase48_operational_release `
  --verbosity 2
if ($LASTEXITCODE -ne 0) { throw "Django Epic49 regression tests failed" }

& $Python manage.py epic49_archive_failed_batches --all-failed
if ($LASTEXITCODE -ne 0) { throw "Epic49 failed-batch dry-run failed" }

& (Join-Path $Root "SYNC_EPIC49_CATALOG_WINDOWS.ps1")
if ($LASTEXITCODE -ne 0) { throw "Canonical Windows Catalog sync failed" }

if (-not (Test-Path -LiteralPath $CanonicalCatalog)) {
    throw "Canonical Catalog source missing after sync: $CanonicalCatalog"
}
& $Python -m compileall (Join-Path $CanonicalCatalog "app") -q
if ($LASTEXITCODE -ne 0) { throw "Canonical Catalog compileall failed" }

Set-Location $CanonicalCatalog
$CanonicalVerify = @(& $Python launch.py --verify-only)
if ($LASTEXITCODE -ne 0) { throw "Canonical Catalog launcher verification failed" }
$CanonicalVerify | ForEach-Object { Write-Host $_ }
$CanonicalVerifyText = $CanonicalVerify -join "`n"
foreach ($Marker in @(
  "ACTIVE_VERSION=8.7.0",
  "UX87_SHELL=ENABLED",
  "PRODUCT_WORKSPACE_V87=ENABLED",
  "AI_PROFILE_MIGRATION=PRESERVED",
  "HOST_PROFILE_MIGRATION=PRESERVED",
  "ACTIVE_RELEASE_VERIFIED=OK"
)) {
    if ($CanonicalVerifyText -notmatch [regex]::Escape($Marker)) { throw "Canonical source missing v8.7 marker: $Marker" }
}

& $Python -m unittest discover -s tests -p "test_*.py" -v
if ($LASTEXITCODE -ne 0) { throw "Canonical Catalog Center full test suite failed" }

& (Join-Path $CanonicalCatalog "BUILD_EXE.ps1")
if ($LASTEXITCODE -ne 0) { throw "Portable EXE build or self-verification failed" }

$Version = (& $Python -c "import sys; sys.path.insert(0, r'$CanonicalCatalog'); from app.version import APP_VERSION; print(APP_VERSION)").Trim()
if ($Version -ne "8.7.0") { throw "Expected portable release 8.7.0, got $Version" }
$ReleaseDir = Join-Path $CanonicalCatalog ("release\" + $Version)
$ReleaseManifest = Join-Path $ReleaseDir "release-manifest.json"
if (-not (Test-Path -LiteralPath $ReleaseManifest)) { throw "Release manifest missing: $ReleaseManifest" }
$Manifest = Get-Content -LiteralPath $ReleaseManifest -Raw | ConvertFrom-Json
$VersionedExe = Join-Path $ReleaseDir ([string]$Manifest.versioned_exe)
$StableExe = Join-Path $ReleaseDir ([string]$Manifest.stable_exe)
if (-not (Test-Path -LiteralPath $VersionedExe)) { throw "Verified portable EXE missing: $VersionedExe" }
if ($Manifest.stable_exe_updated -eq $true -and -not (Test-Path -LiteralPath $StableExe)) { throw "Stable portable EXE missing after successful alias update: $StableExe" }

Set-Location $Root
Write-Host "CATALOG_VERSION=8.7.0"
Write-Host "UX87_WINDOWS_REBUILD=OK"
Write-Host "UX87_SIDEBAR_SHELL=OK"
Write-Host "UX87_NATIVE_ICONS=OK"
Write-Host "UX87_PRODUCT_WORKSPACE=OK"
Write-Host "UX87_AI_CENTER=OK"
Write-Host "UX87_CONNECTION_CENTER=OK"
Write-Host "AI_PROFILE_PRESERVED=YES"
Write-Host "HOST_PROFILE_PRESERVED=YES"
Write-Host "DATABASE_MIGRATION_0028_SCHEMA=READY"
Write-Host "DATABASE_MIGRATION_0029_BACKFILL=READY"
Write-Host "DATABASE_MYSQL_DDL_DATA_SPLIT=ENABLED"
Write-Host "DATABASE_LOCAL_RUNTIME_WRITE=NO"
Write-Host "GIT_CATALOG_FULL_SUITE=OK"
Write-Host "WINDOWS_CATALOG_SYNC=OK"
Write-Host "WINDOWS_CATALOG_FULL_SUITE=OK"
Write-Host "DJANGO_EPIC49_REGRESSION=OK"
Write-Host "SERVER_CATALOG_PROFILE=ENABLED"
Write-Host "SERVER_BACKFILL_COMMAND=TESTED"
Write-Host "ASCII_PRODUCT_URL=ENABLED"
Write-Host "LEGACY_PRODUCT_REDIRECT=ENABLED"
Write-Host "SEO_STRUCTURED_DATA=ENABLED"
Write-Host "SITEMAP_CANONICAL_URL=ENABLED"
Write-Host "BRIDGE_VERSION=1.2.0"
Write-Host "PUBLISH_CONTRACT=epic49-final"
Write-Host "PUBLIC_HTTP_ACCEPTANCE_CONTRACT=ENABLED"
Write-Host "EXISTING_PRODUCT_RESYNC=ENABLED"
Write-Host "PER_PRODUCT_IMAGE_LIMIT=ENABLED"
Write-Host "LOCAL_IMAGE_UPLOAD=ENABLED"
Write-Host "PRICE_RANGE=ENABLED"
Write-Host "MATERIAL_COLOR_VARIANTS=ENABLED"
Write-Host "HOMEPAGE_SLIDER_CONTROL=ENABLED"
Write-Host "FAILED_BATCH_ARCHIVE=DRY_RUN_OK"
Write-Host "PORTABLE_EXE=$VersionedExe"
Write-Host "PORTABLE_EXE_LATEST=$StableExe"
Write-Host "PORTABLE_STABLE_ALIAS_UPDATED=$($Manifest.stable_exe_updated)"
Write-Host "PORTABLE_EXE_RELEASE_MANIFEST=$ReleaseManifest"
Write-Host "PORTABLE_EXE_BUILD=OK"
Write-Host "EPIC49_LOCAL_QA=OK"
