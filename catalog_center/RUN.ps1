param(
    [switch]$VerifyOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$QtRunner = Join-Path $Root "RUN_QT.ps1"

if (-not (Test-Path -LiteralPath $QtRunner)) { throw "Qt operator launcher not found: $QtRunner" }

Write-Host "3DPrintHub Catalog Center - Qt 6 (DEFAULT)" -ForegroundColor Cyan
& $QtRunner -VerifyOnly:$VerifyOnly
