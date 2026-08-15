$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = "D:\projects\3DPrintHub"
$Catalog = Join-Path $Root "catalog_center"
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
& $Python launch.py --verify-only
if ($LASTEXITCODE -ne 0) { throw "Catalog launcher verification failed" }

& $Python -m unittest discover -s tests -p "test_*.py" -v
if ($LASTEXITCODE -ne 0) { throw "Catalog Center full test suite failed" }

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

Write-Host "DATABASE_MIGRATE=NO"
Write-Host "DATABASE_DATA_WRITE=NO"
Write-Host "CATALOG_CENTER_FULL_SUITE=OK"
Write-Host "DJANGO_EPIC49_REGRESSION=OK"
Write-Host "BRIDGE_VERSION=1.2.0"
Write-Host "PUBLISH_CONTRACT=epic49-final"
Write-Host "PUBLIC_HTTP_ACCEPTANCE_CONTRACT=ENABLED"
Write-Host "EXISTING_PRODUCT_RESYNC=ENABLED"
Write-Host "FAILED_BATCH_ARCHIVE=DRY_RUN_OK"
Write-Host "EPIC49_LOCAL_QA=OK"
