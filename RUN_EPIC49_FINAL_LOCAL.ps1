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

# First QA the exact Git source. Canonical Windows files are touched only after this suite is green.
Set-Location $Catalog
& $Python launch.py --verify-only
if ($LASTEXITCODE -ne 0) { throw "Git Catalog launcher verification failed" }

& $Python -m unittest discover -s tests -p "test_*.py" -v
if ($LASTEXITCODE -ne 0) { throw "Git Catalog Center full test suite failed" }

Set-Location $Root
& $Python manage.py check
if ($LASTEXITCODE -ne 0) { throw "Django check failed" }

& $Python manage.py makemigrations --check --dry-run
if ($LASTEXITCODE -ne 0) { throw "Migration drift detected" }

& $Python manage.py test `
  store.test_phase49_catalog_visibility `
  store.test_phase49_1_media `
  store.test_phase49_unicode_routes `
  catalog_bridge.tests.test_bridge `
  catalog_bridge.tests.test_phase49_diagnostics `
  catalog_bridge.tests.test_epic49_contract `
  website.test_phase48_operational_release `
  --verbosity 2
if ($LASTEXITCODE -ne 0) { throw "Django Epic49 regression tests failed" }

# Read-only locally. Failed production batches are archived only on the host after acceptance.
& $Python manage.py epic49_archive_failed_batches --all-failed
if ($LASTEXITCODE -ne 0) { throw "Epic49 failed-batch dry-run failed" }

# Only after Git-side QA passes, sync tracked Catalog source into the actual Windows application source.
& (Join-Path $Root "SYNC_EPIC49_CATALOG_WINDOWS.ps1")
if ($LASTEXITCODE -ne 0) { throw "Canonical Windows Catalog sync failed" }

if (-not (Test-Path -LiteralPath $CanonicalCatalog)) {
    throw "Canonical Catalog source missing after sync: $CanonicalCatalog"
}
& $Python -m compileall (Join-Path $CanonicalCatalog "app") -q
if ($LASTEXITCODE -ne 0) { throw "Canonical Catalog compileall failed" }

Set-Location $CanonicalCatalog
& $Python launch.py --verify-only
if ($LASTEXITCODE -ne 0) { throw "Canonical Catalog launcher verification failed" }

& $Python -m unittest discover -s tests -p "test_*.py" -v
if ($LASTEXITCODE -ne 0) { throw "Canonical Catalog Center full test suite failed" }

# Every approved QA run produces a fresh, verified, single-file portable EXE.
& (Join-Path $CanonicalCatalog "BUILD_EXE.ps1")
if ($LASTEXITCODE -ne 0) { throw "Portable EXE build or self-verification failed" }

$Version = (& $Python -c "import sys; sys.path.insert(0, r'$CanonicalCatalog'); from app.version import APP_VERSION; print(APP_VERSION)").Trim()
$ReleaseDir = Join-Path $CanonicalCatalog ("release\" + $Version)
$VersionedExe = Join-Path $ReleaseDir ("3DPrintHub-CatalogCenter-v" + $Version + ".exe")
$StableExe = Join-Path $ReleaseDir "3DPrintHub-CatalogCenter.exe"
$ReleaseManifest = Join-Path $ReleaseDir "release-manifest.json"
if (-not (Test-Path -LiteralPath $VersionedExe)) { throw "Versioned portable EXE missing: $VersionedExe" }
if (-not (Test-Path -LiteralPath $StableExe)) { throw "Stable portable EXE missing: $StableExe" }
if (-not (Test-Path -LiteralPath $ReleaseManifest)) { throw "Release manifest missing: $ReleaseManifest" }

Set-Location $Root
Write-Host "DATABASE_MIGRATE=NO"
Write-Host "DATABASE_DATA_WRITE=NO"
Write-Host "GIT_CATALOG_FULL_SUITE=OK"
Write-Host "WINDOWS_CATALOG_SYNC=OK"
Write-Host "WINDOWS_CATALOG_FULL_SUITE=OK"
Write-Host "DJANGO_EPIC49_REGRESSION=OK"
Write-Host "BRIDGE_VERSION=1.2.0"
Write-Host "PUBLISH_CONTRACT=epic49-final"
Write-Host "PUBLIC_HTTP_ACCEPTANCE_CONTRACT=ENABLED"
Write-Host "EXISTING_PRODUCT_RESYNC=ENABLED"
Write-Host "FAILED_BATCH_ARCHIVE=DRY_RUN_OK"
Write-Host "PORTABLE_EXE=$VersionedExe"
Write-Host "PORTABLE_EXE_LATEST=$StableExe"
Write-Host "PORTABLE_EXE_RELEASE_MANIFEST=$ReleaseManifest"
Write-Host "PORTABLE_EXE_BUILD=OK"
Write-Host "EPIC49_LOCAL_QA=OK"
