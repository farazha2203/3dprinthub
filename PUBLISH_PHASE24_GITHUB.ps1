$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".git")) {
    throw "This folder is not a Git repository. Clone the repository and copy this patch into the clone first."
}

$branch = "feature/phase24-async-link-analysis-queue"
$commitMessage = "Add async link analysis queue and retry workflow"
$paths = @(
    "PHASE24_ASYNC_LINK_ANALYSIS_QUEUE_APPLIED.txt",
    "APPLY_PHASE24.ps1",
    "RUN_PHASE24_WORKER.ps1",
    "PUBLISH_PHASE24_GITHUB.ps1",
    "docs/PHASE24_ASYNC_LINK_ANALYSIS_QUEUE_FA.md",
    "scripts/verify_phase24_link_queue.py",
    "static/css/phase24-link-queue.css",
    "static/js/phase24-link-queue.js",
    "store/admin.py",
    "store/forms.py",
    "store/link_analysis_queue.py",
    "store/link_intelligence.py",
    "store/management/commands/phase24_link_queue_audit.py",
    "store/management/commands/process_link_analysis_queue.py",
    "store/management/commands/run_phase10_automation.py",
    "store/migrations/0017_phase24_async_link_analysis_queue.py",
    "store/models.py",
    "store/test_phase23.py",
    "store/test_phase24.py",
    "store/urls.py",
    "store/views.py",
    "templates/store/base.html",
    "templates/store/customer_link_analyses.html",
    "templates/store/external_link_analysis.html"
)

git checkout -B $branch
if ($LASTEXITCODE -ne 0) { throw "Could not create or switch branch." }

git add -- $paths
if ($LASTEXITCODE -ne 0) { throw "Could not stage Phase 24 files." }

git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "No new Phase 24 changes to commit." -ForegroundColor Yellow
} else {
    git commit -m $commitMessage
    if ($LASTEXITCODE -ne 0) { throw "Commit failed." }
}

git push -u origin $branch
if ($LASTEXITCODE -ne 0) { throw "Push failed. Check GitHub authentication and remote access." }

Write-Host "Published branch: $branch" -ForegroundColor Green
