$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "D:\projects\3DPrintHub\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { throw "Python venv not found: $Python" }
$env:PYTHONPATH = $Root
Write-Host "=== Compile all v8.5.4 Python ==="
& $Python -m compileall -q "$Root\app" "$Root\server" "$Root\tests" "$Root\LIVE_AI_TEST.py"
if ($LASTEXITCODE -ne 0) { throw "Python compileall failed" }
Write-Host "=== Catalog Intelligence v8.5.4 unit/contract tests ==="
Push-Location $Root
try {
    & $Python -m unittest discover -s tests -p "test_*.py" -v
    if ($LASTEXITCODE -ne 0) { throw "v8.5.4 tests failed" }
    Write-Host "=== Absolute launcher shadow-path regression ==="
    & $Python "$Root\launch.py" --verify-only
    if ($LASTEXITCODE -ne 0) { throw "v8.5.4 launcher verification failed" }
    Write-Host "=== Real Tk UI startup smoke ==="
    & $Python "$Root\tests\ui_smoke_runner.py"
    if ($LASTEXITCODE -ne 0) { throw "v8.5.4 UI startup smoke failed" }
    Write-Host "=== Clipboard + 25-image gallery smoke ==="
    & $Python "$Root\tests\ui_behavior_smoke_runner.py"
    if ($LASTEXITCODE -ne 0) { throw "v8.5.4 gallery smoke failed" }
    Write-Host "=== Product Studio + 25-image editing + category smoke ==="
    & $Python "$Root\tests\ui_v83_studio_smoke_runner.py"
    if ($LASTEXITCODE -ne 0) { throw "v8.5.4 Product Studio smoke failed" }
} finally {
    Pop-Location
}
Write-Host "CATALOG_INTELLIGENCE_V8_5_4_SELF_TEST=OK"
Write-Host "LIVE_AI_TEST is intentionally separate because it uses your real API credit."
