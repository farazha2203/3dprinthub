param(
    [string]$SshHost = "3dprinthub.ir",
    [string]$SshUser = "sfkilvrs",
    [int]$SshPort = 22,
    [string]$Branch = "feature/phase30-online-payment-gateway"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command ssh-keygen -ErrorAction SilentlyContinue)) {
    throw "OpenSSH Client نصب نیست. در Windows Optional Features آن را فعال کن."
}

$sshDir = Join-Path $HOME ".ssh"
$keyPath = Join-Path $sshDir "3dprinthub_ed25519"
New-Item -ItemType Directory -Force -Path $sshDir | Out-Null

if (-not (Test-Path -LiteralPath $keyPath -PathType Leaf)) {
    & ssh-keygen -t ed25519 -a 64 -f $keyPath -C "3dprinthub-vscode-deploy" -N ""
    if ($LASTEXITCODE -ne 0) { throw "ساخت کلید SSH ناموفق بود." }
}

$config = @"
@{
    SshHost = "$SshHost"
    SshUser = "$SshUser"
    SshPort = $SshPort
    PrivateKeyPath = "$keyPath"
    RemoteProjectDir = "/home/sfkilvrs/3dprinthub"
    RemoteVenvDir = "/home/sfkilvrs/virtualenv/3dprinthub/3.12"
    Branch = "$Branch"
    RunFullTests = `$true
    HealthUrls = @(
        "https://3dprinthub.ir/",
        "https://3dprinthub.ir/store/",
        "https://3dprinthub.ir/customer/login/"
    )
}
"@
Set-Content -LiteralPath (Join-Path $PSScriptRoot "DEPLOY_CONFIG.ps1") -Value $config -Encoding UTF8

$vscodeDir = Join-Path $PSScriptRoot ".vscode"
New-Item -ItemType Directory -Force -Path $vscodeDir | Out-Null

$tasks = @'
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "3DPrintHub: Test + Commit + Push + Deploy",
      "type": "shell",
      "command": "powershell.exe",
      "args": [
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "${workspaceFolder}\\PUBLISH_TEST_AND_DEPLOY.ps1"
      ],
      "options": { "cwd": "${workspaceFolder}" },
      "problemMatcher": [],
      "group": { "kind": "build", "isDefault": true },
      "presentation": { "reveal": "always", "panel": "dedicated", "clear": true }
    },
    {
      "label": "3DPrintHub: Deploy current GitHub commit only",
      "type": "shell",
      "command": "powershell.exe",
      "args": [
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "${workspaceFolder}\\PUBLISH_TEST_AND_DEPLOY.ps1",
        "-DeployOnly"
      ],
      "options": { "cwd": "${workspaceFolder}" },
      "problemMatcher": [],
      "presentation": { "reveal": "always", "panel": "dedicated", "clear": true }
    },
    {
      "label": "3DPrintHub: Build clean host ZIP",
      "type": "shell",
      "command": "powershell.exe",
      "args": [
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "${workspaceFolder}\\CLEAN_3DPRINTHUB_AND_BUILD_HOST_PACKAGE.ps1"
      ],
      "options": { "cwd": "${workspaceFolder}" },
      "problemMatcher": [],
      "presentation": { "reveal": "always", "panel": "dedicated", "clear": true }
    }
  ]
}
'@
Set-Content -LiteralPath (Join-Path $vscodeDir "tasks.json") -Value $tasks -Encoding UTF8

# Common SFTP extension configuration. Password is intentionally omitted; SSH key is used.
$privateKeyForJson = $keyPath.Replace("\", "/")
$sftp = @"
{
  "name": "3DPrintHub Host",
  "host": "$SshHost",
  "protocol": "sftp",
  "port": $SshPort,
  "username": "$SshUser",
  "privateKeyPath": "$privateKeyForJson",
  "remotePath": "/home/sfkilvrs/3dprinthub",
  "uploadOnSave": false,
  "useTempFile": true,
  "ignore": [
    ".vscode",
    ".git",
    ".venv",
    ".env",
    "db.sqlite3",
    "staticfiles",
    "media",
    "private_media",
    ".phase-backups",
    "*.zip",
    "__pycache__",
    "*.pyc"
  ],
  "syncOption": {
    "delete": false,
    "update": true
  }
}
"@
Set-Content -LiteralPath (Join-Path $vscodeDir "sftp.json") -Value $sftp -Encoding UTF8

$excludePath = Join-Path $PSScriptRoot ".git\info\exclude"
if (Test-Path (Split-Path $excludePath)) {
    $entries = @("DEPLOY_CONFIG.ps1", ".vscode/sftp.json", ".vscode/tasks.json")
    $existing = if (Test-Path $excludePath) { Get-Content $excludePath } else { @() }
    foreach ($entry in $entries) {
        if ($existing -notcontains $entry) { Add-Content -LiteralPath $excludePath -Value $entry -Encoding UTF8 }
    }
}

Write-Host ""
Write-Host "VSCODE_DEPLOY_SETUP=OK"
Write-Host "SSH private key: $keyPath"
Write-Host "SSH public key:  $keyPath.pub"
Write-Host ""
Write-Host "این کلید عمومی را در cPanel > SSH Access > Manage SSH Keys وارد و Authorize کن:"
Get-Content -LiteralPath "$keyPath.pub"
Write-Host ""
Write-Host "بعد از Authorize شدن کلید، در VS Code از Terminal > Run Task استفاده کن."
