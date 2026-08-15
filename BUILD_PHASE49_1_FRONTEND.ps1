$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = "D:\projects\3DPrintHub"
$Branch = "agent/phase49-1-media-frontend-cleanup"
$OutputRel = "static/css/tailwind-production.css"
$Output = Join-Path $Root "static\css\tailwind-production.css"
$Python = Join-Path $Root ".venv\Scripts\python.exe"
Set-Location $Root

if ((git branch --show-current).Trim() -ne $Branch) { throw "Branch must be $Branch" }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw "node not found" }
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw "npm not found" }
if (-not (Test-Path -LiteralPath $Python)) { throw "Python not found: $Python" }

git diff --quiet
if ($LASTEXITCODE -ne 0) { throw "Safety stop: tracked working-tree changes already exist." }
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) { throw "Safety stop: staged Git changes already exist." }

npm install --no-package-lock --no-audit --no-fund
if ($LASTEXITCODE -ne 0) { throw "npm install failed" }

npm run build:css
if ($LASTEXITCODE -ne 0) { throw "Tailwind build failed" }
if (-not (Test-Path -LiteralPath $Output)) { throw "tailwind-production.css not generated" }
$Size = (Get-Item -LiteralPath $Output).Length
if ($Size -lt 20000) { throw "Tailwind output is unexpectedly small: $Size" }

try {
    & $Python tools\phase49_1_finalize_tailwind.py
    if ($LASTEXITCODE -ne 0) { throw "Tailwind template finalization failed" }

    & $Python manage.py check
    if ($LASTEXITCODE -ne 0) { throw "Django check failed after Tailwind finalization" }

    & $Python manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw "Migration drift after Tailwind finalization" }

    & $Python manage.py test `
      store.test_phase49_1_media `
      store.test_phase49_1_frontend_contract `
      store.test_phase49_catalog_visibility `
      store.test_phase49_unicode_routes `
      catalog_bridge.tests.test_phase49_diagnostics `
      store.test_phase48_presentation_resilience `
      website.test_phase48_operational_release `
      catalog_bridge.tests.test_bridge `
      --verbosity 1
    if ($LASTEXITCODE -ne 0) { throw "Regression tests failed after Tailwind finalization" }

    git diff --check
    if ($LASTEXITCODE -ne 0) { throw "Working-tree diff check failed" }

    git add -- $OutputRel templates
    $Staged = @(git diff --cached --name-only)
    if ($Staged.Count -eq 0) {
        Write-Host "TAILWIND_GIT=UNCHANGED"
    } else {
        $Unexpected = @($Staged | Where-Object { $_ -ne $OutputRel -and -not $_.StartsWith("templates/") })
        if ($Unexpected.Count -gt 0) {
            git restore --staged -- $OutputRel templates
            throw "Safety stop: unexpected staged files: $($Unexpected -join ', ')"
        }
        git diff --cached --check
        if ($LASTEXITCODE -ne 0) {
            git restore --staged -- $OutputRel templates
            throw "Tailwind staged diff check failed"
        }
        git commit -m "Phase 49.1B: replace Tailwind CDN with production bundle"
        if ($LASTEXITCODE -ne 0) { throw "Tailwind commit failed" }
        git push origin $Branch
        if ($LASTEXITCODE -ne 0) { throw "Tailwind branch push failed" }
        Write-Host "TAILWIND_GIT_COMMIT=$((git rev-parse HEAD).Trim())"
    }
}
catch {
    git restore -- templates 2>$null
    git restore --staged -- $OutputRel templates 2>$null
    if (Test-Path -LiteralPath $Output) { Remove-Item -LiteralPath $Output -Force }
    throw
}

Write-Host "TAILWIND_OUTPUT=$Output"
Write-Host "TAILWIND_OUTPUT_SIZE=$Size"
Write-Host "TAILWIND_CDN=REMOVED_AFTER_TESTS"
Write-Host "PHASE49_1_TAILWIND_BUILD=OK"
