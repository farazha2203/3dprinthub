$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = "D:\projects\3DPrintHub"
$Branch = "agent/phase49-1-media-frontend-cleanup"
$Python = Join-Path $Root ".venv\Scripts\python.exe"
Set-Location $Root

if ((git branch --show-current).Trim() -ne $Branch) { throw "Branch must be $Branch" }
if (-not (Test-Path -LiteralPath $Python)) { throw "Python not found: $Python" }

& $Python manage.py check
if ($LASTEXITCODE -ne 0) { throw "Django check failed" }

& $Python manage.py makemigrations --check --dry-run
if ($LASTEXITCODE -ne 0) { throw "Migration drift detected" }

& $Python manage.py test `
  store.test_phase49_1_media `
  store.test_phase49_1_frontend_contract `
  store.test_phase49_catalog_visibility `
  store.test_phase49_unicode_routes `
  catalog_bridge.tests.test_phase49_diagnostics `
  store.test_phase48_presentation_resilience `
  website.test_phase48_operational_release `
  catalog_bridge.tests.test_bridge `
  --verbosity 2
if ($LASTEXITCODE -ne 0) { throw "Phase49.1 regression tests failed" }

& $Python manage.py phase49_1_media_audit
if ($LASTEXITCODE -ne 0) { throw "Local media dry-run audit failed" }

Write-Host "DATABASE_MIGRATE=NO"
Write-Host "DATABASE_DATA_WRITE=NO"
Write-Host "PHASE49_1_LOCAL_TESTS=OK"
