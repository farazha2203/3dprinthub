param(
    [ValidateSet("auto","avalai","openai")][string]$Provider = "auto",
    [string]$ProjectRoot = "D:\projects\3DPrintHub",
    [string]$Model = ""
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "D:\projects\3DPrintHub\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { throw "Python venv not found: $Python" }
$env:PYTHONPATH = $Root
Write-Host "=== 3DPrintHub v8.4 live AI test ==="
& $Python "$Root\LIVE_AI_TEST.py" --provider $Provider --project-root $ProjectRoot --model $Model
if ($LASTEXITCODE -ne 0) { throw "Live AI test failed" }
