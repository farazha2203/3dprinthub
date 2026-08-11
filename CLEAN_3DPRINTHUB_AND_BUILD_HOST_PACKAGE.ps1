param(
    [string]$ProjectDir = "D:\projects\3DPrintHub",
    [switch]$AuditOnly,
    [switch]$SkipHostPackage
)

$ErrorActionPreference = "Stop"

$ProjectDir = [System.IO.Path]::GetFullPath($ProjectDir)
$ProjectPython = Join-Path $ProjectDir ".venv\Scripts\python.exe"
$CleanupScript = Join-Path $ProjectDir "tools\cleanup_project.py"

if (-not (Test-Path -LiteralPath $ProjectPython -PathType Leaf)) {
    throw "Project Python not found: $ProjectPython"
}
if (-not (Test-Path -LiteralPath $CleanupScript -PathType Leaf)) {
    throw "Cleanup tool not found: $CleanupScript"
}

Write-Host "Project: $ProjectDir"
Write-Host "Python: $ProjectPython"
Write-Host "Tracked source files are always preserved."
Write-Host ".env, database, media, private_media, .venv and private runtime assets are protected."

$Arguments = @($CleanupScript, "--project", $ProjectDir)
if (-not $AuditOnly) {
    $Arguments += "--apply"
}
if (-not $SkipHostPackage) {
    $Arguments += "--build-host-package"
}

& $ProjectPython @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "Cleanup/build failed with exit code $LASTEXITCODE"
}

Write-Host ""
if ($AuditOnly) {
    Write-Host "Audit completed. Nothing was moved."
} else {
    Write-Host "Cleanup completed. Extra files were moved to a reversible quarantine outside the project."
}
if (-not $SkipHostPackage) {
    Write-Host "A clean host-upload ZIP was created under D:\projects\_3DPrintHub_host_releases."
}
