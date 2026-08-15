$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "D:\projects\3DPrintHub\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    $Python = "python"
}
& $Python (Join-Path $Root "VERIFY_PACKAGE.py")
if ($LASTEXITCODE -ne 0) { throw "VERIFY_FAILED" }
