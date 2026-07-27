param(
    [string]$Branch = "feature/phase30-online-payment-gateway",
    [string]$Message = "Release phase 30 production source",
    [switch]$RunFullTests,
    [switch]$PrepareOnly,
    [switch]$SkipDependencyRepair
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$ProjectPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$RequirementsFile = Join-Path $PSScriptRoot "requirements.txt"

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [switch]$AllowFailure,
        [switch]$Capture
    )

    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $output = @(& git @Arguments 2>&1)
        $exitCode = [int]$LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }

    $text = ($output | ForEach-Object { "$_" }) -join [Environment]::NewLine
    if (-not $Capture -and $text) { Write-Host $text }
    if ($exitCode -ne 0 -and -not $AllowFailure) {
        throw ("git {0} failed with exit code {1}`n{2}" -f ($Arguments -join " "), $exitCode, $text)
    }
    return [pscustomobject]@{ ExitCode = $exitCode; Output = $text.Trim() }
}

function Invoke-ProjectPython {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    if (-not (Test-Path -LiteralPath $ProjectPython -PathType Leaf)) {
        throw "Project virtualenv Python was not found: $ProjectPython`nRun APPLY_PHASE30.ps1 once or create the project .venv before publishing."
    }

    & $ProjectPython @Arguments
    $exitCode = [int]$LASTEXITCODE
    if ($exitCode -ne 0) {
        throw ("Project Python command failed with exit code {0}: {1}" -f $exitCode, ($Arguments -join " "))
    }
}

function Test-RemoteBranch {
    param([string]$Name)
    $result = Invoke-Git -Arguments @("ls-remote", "--exit-code", "--heads", "origin", $Name) -AllowFailure -Capture
    if ($result.ExitCode -eq 0) { return $true }
    if ($result.ExitCode -eq 2) { return $false }
    throw ("Unable to check remote branch {0}:`n{1}" -f $Name, $result.Output)
}

Write-Host "[1/11] Verifying Git repository..."
[void](Invoke-Git -Arguments @("rev-parse", "--is-inside-work-tree"))

Write-Host "[2/11] Fetching remote refs and selecting release branch..."
[void](Invoke-Git -Arguments @("fetch", "origin", "--prune"))
$currentBranch = (Invoke-Git -Arguments @("branch", "--show-current") -Capture).Output
if ($currentBranch -ne $Branch) {
    $localBranch = Invoke-Git -Arguments @("show-ref", "--verify", "--quiet", "refs/heads/$Branch") -AllowFailure -Capture
    if ($localBranch.ExitCode -eq 0) {
        [void](Invoke-Git -Arguments @("switch", $Branch))
    }
    else {
        [void](Invoke-Git -Arguments @("switch", "-c", $Branch))
    }
}
else {
    Write-Host "Already on $Branch"
}

Write-Host "[3/11] Rebuilding the local release branch from clean origin/main..."
$remoteExists = Test-RemoteBranch -Name $Branch
if (-not $remoteExists) {
    $aheadResult = Invoke-Git -Arguments @("rev-list", "--count", "origin/main..HEAD") -Capture
    $aheadCount = [int]$aheadResult.Output
    if ($aheadCount -gt 0) {
        $oldHead = (Invoke-Git -Arguments @("rev-parse", "HEAD") -Capture).Output
        Write-Host "Discarding local-only commit history while preserving every working-tree file."
        Write-Host "Old local HEAD: $oldHead"
        [void](Invoke-Git -Arguments @("reset", "--mixed", "origin/main"))
        Write-Host "Local branch now starts from origin/main; current project files are preserved."
    }
}
else {
    Write-Host "Remote branch already exists; its history will not be rewritten automatically."
}

# Clear stale staging only. This never deletes local files.
[void](Invoke-Git -Arguments @("reset", "--quiet"))

Write-Host "[4/11] Selecting the 3DPrintHub project virtualenv..."
if (-not (Test-Path -LiteralPath $ProjectPython -PathType Leaf)) {
    throw "Wrong or missing environment. Expected project Python:`n$ProjectPython`nThe currently active shell environment is ignored intentionally."
}
Write-Host "Project Python: $ProjectPython"
Invoke-ProjectPython -Arguments @("-c", "import sys; print('PROJECT_PYTHON=' + sys.executable)")

Write-Host "[5/11] Checking project dependencies..."
$previousPreference = $ErrorActionPreference
try {
    $ErrorActionPreference = "Continue"
    $dependencyOutput = @(& $ProjectPython -c "import django, dotenv, requests; print('PROJECT_DEPENDENCIES=OK')" 2>&1)
    $dependencyExit = [int]$LASTEXITCODE
}
finally {
    $ErrorActionPreference = $previousPreference
}
$dependencyText = ($dependencyOutput | ForEach-Object { "$_" }) -join [Environment]::NewLine
if ($dependencyText) { Write-Host $dependencyText }

if ($dependencyExit -ne 0) {
    if ($SkipDependencyRepair) {
        throw "Project dependencies are incomplete and SkipDependencyRepair was selected."
    }
    if (-not (Test-Path -LiteralPath $RequirementsFile -PathType Leaf)) {
        throw "requirements.txt was not found: $RequirementsFile"
    }
    Write-Host "Repairing dependencies inside the 3DPrintHub .venv..."
    Invoke-ProjectPython -Arguments @("-m", "pip", "install", "-r", $RequirementsFile)
    Invoke-ProjectPython -Arguments @("-c", "import django, dotenv, requests; print('PROJECT_DEPENDENCIES=OK')")
}

Write-Host "[6/11] Verifying Phase 30 application state..."
Invoke-ProjectPython -Arguments @("scripts/verify_phase30.py")
Invoke-ProjectPython -Arguments @("scripts/verify_phase30_runtime_assets.py")
Invoke-ProjectPython -Arguments @("manage.py", "makemigrations", "--check", "--dry-run")
Invoke-ProjectPython -Arguments @("manage.py", "check")
Invoke-ProjectPython -Arguments @("manage.py", "phase30_payment_audit")
if ($RunFullTests) {
    Invoke-ProjectPython -Arguments @("manage.py", "test", "--keepdb")
}

Write-Host "[7/11] Keeping private vendor assets and generated artifacts out of Git..."
$vendorTracked = (Invoke-Git -Arguments @(
    "ls-files", "--", "static/velzon", "static/velzon_master", "static/fonts", ".phase-backups"
) -Capture -AllowFailure).Output
if ($vendorTracked) {
    Write-Host "Removing private/vendor paths from Git tracking while preserving local files..."
    [void](Invoke-Git -Arguments @(
        "rm", "-r", "--cached", "--ignore-unmatch", "--",
        "static/velzon", "static/velzon_master", "static/fonts", ".phase-backups"
    ) -Capture)
}

Write-Host "[8/11] Staging only the production source allowlist..."
$releasePaths = @(
    ".env.example",
    ".env.production.example",
    ".gitignore",
    ".gitattributes",
    "README.md",
    "manage.py",
    "passenger_wsgi.py",
    "requirements.txt",
    "requirements-smartbase.txt",
    "config",
    "store",
    "website",
    "templates",
    "smartbase_admin_bridge",
    "tools",
    "scripts",
    "deploy",
    "docs",
    "static/admin",
    "static/css",
    "static/favicon",
    "static/img",
    "static/js",
    "static/sb_admin",
    "static/source",
    "static/store",
    "APPLY_PHASE30.ps1",
    "APPLY_PHASE30_SERVER.sh",
    "PUBLISH_PHASE30_GITHUB.ps1",
    "PHASE30_ONLINE_PAYMENT_GATEWAY_APPLIED.txt",
    "PHASE30_1_GITHUB_CPANEL_RELEASE_APPLIED.txt",
    "PHASE30_2_CLEAN_GITHUB_RELEASE_APPLIED.txt",
    "PHASE30_3_PROJECT_VENV_RELEASE_APPLIED.txt",
    "PHASE30_4_REBUILD_CLEAN_BRANCH_APPLIED.txt"
)
$existingPaths = @()
foreach ($path in $releasePaths) {
    if (Test-Path -LiteralPath (Join-Path $PSScriptRoot $path)) {
        $existingPaths += $path
    }
}
[void](Invoke-Git -Arguments (@("add", "-A", "--") + $existingPaths) -Capture)

Write-Host "[9/11] Scanning staged content for secrets and forbidden files..."
Invoke-ProjectPython -Arguments @("scripts/scan_staged_release.py")

$staged = (Invoke-Git -Arguments @("diff", "--cached", "--name-only", "--diff-filter=ACMR") -Capture).Output
if ($staged) {
    foreach ($relativePath in ($staged -split "`r?`n")) {
        if (-not $relativePath) { continue }
        $absolutePath = Join-Path $PSScriptRoot $relativePath
        if (Test-Path -LiteralPath $absolutePath -PathType Leaf) {
            $size = (Get-Item -LiteralPath $absolutePath).Length
            if ($size -gt 95MB) {
                throw "File exceeds the safe GitHub limit (95 MB): $relativePath"
            }
        }
    }
}

Write-Host "[10/11] Reviewing and committing the clean release..."
$stagedNames = @()
if ($staged) { $stagedNames = @($staged -split "`r?`n" | Where-Object { $_ }) }
Write-Host ("Staged files: {0}" -f $stagedNames.Count)
$stagedNames |
    ForEach-Object { ($_ -split "/")[0] } |
    Group-Object |
    Sort-Object Count -Descending |
    ForEach-Object { Write-Host ("  {0}: {1}" -f $_.Name, $_.Count) }
[void](Invoke-Git -Arguments @("diff", "--cached", "--stat"))

$hasChanges = (Invoke-Git -Arguments @("diff", "--cached", "--quiet") -AllowFailure -Capture).ExitCode -ne 0
if (-not $hasChanges) {
    Write-Host "No clean release changes remain to commit."
}
elseif ($PrepareOnly) {
    Write-Host "PrepareOnly selected. Clean changes are staged but not committed or pushed."
    exit 0
}
else {
    [void](Invoke-Git -Arguments @("commit", "-m", $Message))
}

Write-Host "[11/11] Pushing the clean branch to GitHub..."
[void](Invoke-Git -Arguments @("push", "-u", "origin", $Branch))

$commit = (Invoke-Git -Arguments @("rev-parse", "HEAD") -Capture).Output
Write-Host ""
Write-Host "Phase 30 clean release pushed successfully."
Write-Host "Branch: $Branch"
Write-Host "Commit: $commit"
Write-Host "Python used: $ProjectPython"
Write-Host "Private Velzon/font assets were intentionally excluded from the public repository."
