param(
    [string]$Message = "",
    [switch]$SkipFullTests,
    [switch]$DeployOnly,
    [switch]$NoHealthCheck
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Stop-WithError([string]$Message) {
    throw $Message
}

function Invoke-External {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [switch]$Capture
    )
    $oldPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $output = @(& $FilePath @Arguments 2>&1)
        $code = [int]$LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $oldPreference
    }
    $text = ($output | ForEach-Object { "$_" }) -join [Environment]::NewLine
    if (-not $Capture -and $text) { Write-Host $text }
    if ($code -ne 0) {
        throw ("Command failed ({0}): {1} {2}`n{3}" -f $code, $FilePath, ($Arguments -join " "), $text)
    }
    return $text.Trim()
}

$configPath = Join-Path $PSScriptRoot "DEPLOY_CONFIG.ps1"
if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
    Stop-WithError "DEPLOY_CONFIG.ps1 پیدا نشد. ابتدا SETUP_VSCODE_DEPLOY.ps1 را اجرا کن."
}
$config = & $configPath
if (-not ($config -is [hashtable])) {
    Stop-WithError "DEPLOY_CONFIG.ps1 باید یک Hashtable برگرداند."
}

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$publishScript = Join-Path $PSScriptRoot "PUBLISH_PHASE30_GITHUB.ps1"
$keyPath = [Environment]::ExpandEnvironmentVariables([string]$config.PrivateKeyPath)
$keyPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($keyPath)

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    Stop-WithError "Python پروژه پیدا نشد: $python"
}
if (-not (Test-Path -LiteralPath $publishScript -PathType Leaf)) {
    Stop-WithError "اسکریپت انتشار GitHub پیدا نشد: $publishScript"
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Stop-WithError "Git در PATH پیدا نشد."
}
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Stop-WithError "OpenSSH Client ویندوز نصب یا فعال نیست."
}
if (-not (Test-Path -LiteralPath $keyPath -PathType Leaf)) {
    Stop-WithError "کلید SSH پیدا نشد: $keyPath`nابتدا SETUP_VSCODE_DEPLOY.ps1 را اجرا و کلید عمومی را در cPanel Authorize کن."
}

$branch = [string]$config.Branch
$remote = "{0}@{1}" -f $config.SshUser, $config.SshHost
$sshBase = @("-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "-p", [string]$config.SshPort, "-i", $keyPath)

Write-Host "[1/8] Preflight Git and project checks..."
$inside = Invoke-External -FilePath "git" -Arguments @("rev-parse", "--is-inside-work-tree") -Capture
if ($inside -ne "true") { Stop-WithError "این مسیر Git repository نیست." }
$currentBranch = Invoke-External -FilePath "git" -Arguments @("branch", "--show-current") -Capture
if ($currentBranch -ne $branch) {
    Stop-WithError "Branch فعلی '$currentBranch' است؛ Branch مورد انتظار '$branch'."
}

if (-not $DeployOnly) {
    Write-Host "[2/8] Running verification and tests..."
    Invoke-External -FilePath $python -Arguments @("scripts/verify_phase30.py")
    if (Test-Path "scripts/verify_phase30_runtime_assets.py") {
        Invoke-External -FilePath $python -Arguments @("scripts/verify_phase30_runtime_assets.py")
    }
    Invoke-External -FilePath $python -Arguments @("manage.py", "makemigrations", "--check", "--dry-run")
    Invoke-External -FilePath $python -Arguments @("manage.py", "check")
    Invoke-External -FilePath $python -Arguments @("manage.py", "phase30_payment_audit")

    $runFull = [bool]$config.RunFullTests -and -not $SkipFullTests
    if ($runFull) {
        Invoke-External -FilePath $python -Arguments @("manage.py", "test", "--keepdb")
    }
    else {
        Invoke-External -FilePath $python -Arguments @(
            "manage.py", "test",
            "website.test_phase30_online_payment",
            "website.test_phase30_zarinpal_provider",
            "website.test_phase28_payment",
            "store.test_phase28",
            "store.test_phase29",
            "--keepdb"
        )
    }

    Write-Host "[3/8] Commit and push clean source..."
    if (-not $Message) {
        $Message = Read-Host "پیام Commit را وارد کن"
    }
    if (-not $Message.Trim()) {
        Stop-WithError "پیام Commit خالی است."
    }
    $publishArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $publishScript, "-Message", $Message)
    Invoke-External -FilePath "powershell.exe" -Arguments $publishArgs
}
else {
    Write-Host "[2/8] DeployOnly selected; local tests/commit/push skipped."
}

Write-Host "[4/8] Verifying pushed commit..."
$localHead = Invoke-External -FilePath "git" -Arguments @("rev-parse", "HEAD") -Capture
$remoteLine = Invoke-External -FilePath "git" -Arguments @("ls-remote", "origin", "refs/heads/$branch") -Capture
$remoteHead = ($remoteLine -split "\s+")[0]
if ($localHead -ne $remoteHead) {
    Stop-WithError "HEAD محلی با Branch روی GitHub یکی نیست.`nLocal: $localHead`nRemote: $remoteHead"
}
Write-Host "Commit confirmed: $localHead"

Write-Host "[5/8] Testing SSH connection..."
Invoke-External -FilePath "ssh" -Arguments ($sshBase + @($remote, "printf 'SSH_OK\\n'"))

Write-Host "[6/8] Deploying GitHub commit on cPanel host..."
$projectDir = [string]$config.RemoteProjectDir
$venvDir = [string]$config.RemoteVenvDir
$quotedBranch = $branch.Replace("'", "'\"'\"'")
$quotedProject = $projectDir.Replace("'", "'\"'\"'")
$quotedVenv = $venvDir.Replace("'", "'\"'\"'")
$remoteCommand = @"
set -Eeuo pipefail
cd '$quotedProject'
git fetch origin --prune
git show 'origin/$quotedBranch:deploy/cpanel/DEPLOY_PHASE30_CPANEL.sh' > /tmp/3dprinthub-deploy.sh
chmod +x /tmp/3dprinthub-deploy.sh
PROJECT_DIR='$quotedProject' VENV_DIR='$quotedVenv' BRANCH='$quotedBranch' bash /tmp/3dprinthub-deploy.sh
"@
Invoke-External -FilePath "ssh" -Arguments ($sshBase + @($remote, $remoteCommand))

Write-Host "[7/8] Confirming deployed commit..."
$remoteCommit = Invoke-External -FilePath "ssh" -Arguments ($sshBase + @($remote, "cd '$quotedProject' && git rev-parse HEAD")) -Capture
if ($remoteCommit.Trim() -ne $localHead.Trim()) {
    Stop-WithError "Commit روی هاست با Commit محلی یکی نیست.`nLocal: $localHead`nHost: $remoteCommit"
}
Write-Host "Host commit confirmed: $remoteCommit"

Write-Host "[8/8] Public health checks..."
if (-not $NoHealthCheck) {
    foreach ($url in @($config.HealthUrls)) {
        try {
            $response = Invoke-WebRequest -Uri $url -Method Get -MaximumRedirection 3 -TimeoutSec 20 -UseBasicParsing
            Write-Host ("OK {0} -> HTTP {1}" -f $url, [int]$response.StatusCode)
        }
        catch {
            $status = $_.Exception.Response.StatusCode.value__
            if ($status -and $status -in @(301, 302, 303, 307, 308)) {
                Write-Host ("OK {0} -> HTTP {1} redirect" -f $url, $status)
            }
            else {
                throw "Health check failed for $url`n$($_.Exception.Message)"
            }
        }
    }
}
else {
    Write-Host "Health checks skipped."
}

Write-Host ""
Write-Host "DEPLOYMENT=OK"
Write-Host "Branch: $branch"
Write-Host "Commit: $localHead"
Write-Host "Host: $remote"
