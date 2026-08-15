$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "D:\projects\3DPrintHub\.venv\Scripts\python.exe"
& $Python -m pip install -r "$Root\requirements.txt"
& $Python -m PyInstaller --noconfirm --clean --windowed --name "3DPrintHubCatalogIntelligence" `
  --distpath "$Root\dist" --workpath "$Root\build" --specpath "$Root" `
  --paths "$Root" `
  --add-data "$Root\assets;assets" `
  --icon "$Root\assets\brand_icon.png" `
  --hidden-import keyring.backends.Windows `
  "$Root\launch.py"
if ($LASTEXITCODE -ne 0) { throw "EXE build failed: $LASTEXITCODE" }
Write-Host "EXE=$Root\dist\3DPrintHubCatalogIntelligence\3DPrintHubCatalogIntelligence.exe"
