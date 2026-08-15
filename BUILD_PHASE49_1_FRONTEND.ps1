$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = "D:\projects\3DPrintHub"
$Branch = "agent/phase49-1-media-frontend-cleanup"
$OutputRel = "static/css/tailwind-production.css"
Set-Location $Root

if ((git branch --show-current).Trim() -ne $Branch) {
    throw "Branch must be $Branch"
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw "node not found" }
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw "npm not found" }

git diff --cached --quiet
if ($LASTEXITCODE -ne 0) { throw "Safety stop: staged Git changes already exist." }

npm install --no-package-lock --no-audit --no-fund
if ($LASTEXITCODE -ne 0) { throw "npm install failed" }

npm run build:css
if ($LASTEXITCODE -ne 0) { throw "Tailwind build failed" }

$Output = Join-Path $Root "static\css\tailwind-production.css"
if (-not (Test-Path -LiteralPath $Output)) { throw "tailwind-production.css not generated" }
$Size = (Get-Item -LiteralPath $Output).Length
if ($Size -lt 20000) { throw "Tailwind output is unexpectedly small: $Size" }

git add -- $OutputRel
$Staged = @(git diff --cached --name-only)
if ($Staged.Count -eq 0) {
    Write-Host "TAILWIND_GIT=UNCHANGED"
} else {
    if ($Staged.Count -ne 1 -or $Staged[0] -ne $OutputRel) {
        git restore --staged -- $OutputRel
        throw "Safety stop: unexpected staged files: $($Staged -join ', ')"
    }
    git diff --cached --check
    if ($LASTEXITCODE -ne 0) {
        git restore --staged -- $OutputRel
        throw "Tailwind staged diff check failed"
    }
    git commit -m "Phase 49.1: build production Tailwind bundle"
    if ($LASTEXITCODE -ne 0) { throw "Tailwind commit failed" }
    git push origin $Branch
    if ($LASTEXITCODE -ne 0) { throw "Tailwind branch push failed" }
    Write-Host "TAILWIND_GIT_COMMIT=$((git rev-parse HEAD).Trim())"
}

Write-Host "TAILWIND_OUTPUT=$Output"
Write-Host "TAILWIND_OUTPUT_SIZE=$Size"
Write-Host "PHASE49_1_TAILWIND_BUILD=OK"
