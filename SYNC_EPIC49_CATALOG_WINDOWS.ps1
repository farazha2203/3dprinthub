$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Repo = "D:\projects\3DPrintHub"
$SourceRoot = Join-Path $Repo "catalog_center"
$DestinationRoot = "D:\projects\3dprinthub_catalog_center"
$RuntimeRoot = "D:\projects\3dprinthub-catalog-manager"
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupRoot = Join-Path $RuntimeRoot "backups\epic49_sync_$Stamp"
$ExpectedBranch = "epic/phase49-finalization"

Set-Location $Repo

if ((git branch --show-current).Trim() -ne $ExpectedBranch) {
    throw "Branch must be $ExpectedBranch"
}
if (-not (Test-Path -LiteralPath $SourceRoot)) {
    throw "Git Catalog source not found: $SourceRoot"
}
if (-not (Test-Path -LiteralPath $DestinationRoot)) {
    New-Item -ItemType Directory -Path $DestinationRoot -Force | Out-Null
}
New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null

$Tracked = @(git ls-files -- "catalog_center")
if ($LASTEXITCODE -ne 0 -or $Tracked.Count -eq 0) {
    throw "Unable to enumerate tracked catalog_center files"
}

$Copied = 0
$BackedUp = 0
$Unchanged = 0
foreach ($RepoRelative in $Tracked) {
    if (-not $RepoRelative.StartsWith("catalog_center/")) { continue }
    $Relative = $RepoRelative.Substring("catalog_center/".Length).Replace("/", "\")
    if (-not $Relative) { continue }

    $Source = Join-Path $SourceRoot $Relative
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) { continue }
    $Destination = Join-Path $DestinationRoot $Relative
    $DestinationDir = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Path $DestinationDir -Force | Out-Null

    $Same = $false
    if (Test-Path -LiteralPath $Destination -PathType Leaf) {
        $SourceHash = (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash
        $DestinationHash = (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash
        if ($SourceHash -eq $DestinationHash) {
            $Same = $true
            $Unchanged++
        } else {
            $Backup = Join-Path $BackupRoot $Relative
            New-Item -ItemType Directory -Path (Split-Path -Parent $Backup) -Force | Out-Null
            Copy-Item -LiteralPath $Destination -Destination $Backup -Force
            $BackedUp++
        }
    }
    if (-not $Same) {
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
        $After = (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash
        $Expected = (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash
        if ($After -ne $Expected) {
            throw "Copy verification failed: $Relative"
        }
        $Copied++
    }
}

Write-Host "CATALOG_SOURCE=$SourceRoot"
Write-Host "CATALOG_DESTINATION=$DestinationRoot"
Write-Host "CATALOG_BACKUP=$BackupRoot"
Write-Host "TRACKED_FILES=$($Tracked.Count)"
Write-Host "COPIED=$Copied"
Write-Host "BACKED_UP=$BackedUp"
Write-Host "UNCHANGED=$Unchanged"
Write-Host "DELETE_FILES=NO"
Write-Host "RUNTIME_DB_TOUCHED=NO"
Write-Host "SECRETS_TOUCHED=NO"
Write-Host "EPIC49_WINDOWS_CATALOG_SYNC=OK"
