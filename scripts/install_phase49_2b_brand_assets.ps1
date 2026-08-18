param(
    [Parameter(Mandatory=$true)][string]$LogoPath,
    [string]$FontsArchivePath = ''
)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$ExpectedLogoSha256 = '97ec202678e386387fa9ebe2c6055fa45967d1f341d40dbc5f2d9e980b873cec'

if (!(Test-Path $LogoPath)) { throw "Logo not found: $LogoPath" }
$actual = (Get-FileHash -Algorithm SHA256 $LogoPath).Hash.ToLowerInvariant()
if ($actual -ne $ExpectedLogoSha256) { throw "Wrong logo selected. Expected SHA256=$ExpectedLogoSha256, actual=$actual" }

$brandDir = Join-Path $Root 'static\img\brand'
New-Item -ItemType Directory -Force -Path $brandDir | Out-Null
$brandTarget = Join-Path $brandDir '3dprinthublogo.png'
Copy-Item -LiteralPath $LogoPath -Destination $brandTarget -Force
$copiedHash = (Get-FileHash -Algorithm SHA256 $brandTarget).Hash.ToLowerInvariant()
if ($copiedHash -ne $ExpectedLogoSha256) { throw "Copied logo hash mismatch: $copiedHash" }

$fontDir = Join-Path $Root 'static\fonts\iransans'
New-Item -ItemType Directory -Force -Path $fontDir | Out-Null
$wanted = @(
    'IRANSansWeb_FaNum_UltraLight.woff',
    'IRANSansWeb_FaNum_Light.woff',
    'IRANSansWeb_FaNum.woff',
    'IRANSansWeb_FaNum_Medium.woff',
    'IRANSansWeb_FaNum_Bold.woff',
    'IRANSansWeb_FaNum_Black.woff'
)

function Test-RequiredFontsPresent {
    foreach ($name in $wanted) {
        $path = Join-Path $fontDir $name
        if (!(Test-Path $path)) { return $false }
        if ((Get-Item $path).Length -le 0) { return $false }
    }
    return $true
}

$reusedExistingFonts = Test-RequiredFontsPresent
if (-not $reusedExistingFonts) {
    if ([string]::IsNullOrWhiteSpace($FontsArchivePath) -or !(Test-Path $FontsArchivePath)) {
        throw 'Required IRANSans FaNum fonts are missing and no valid FontsArchivePath was provided.'
    }

    $candidates = @()
    if ($env:ProgramFiles) { $candidates += (Join-Path $env:ProgramFiles '7-Zip\7z.exe') }
    if (${env:ProgramFiles(x86)}) { $candidates += (Join-Path ${env:ProgramFiles(x86)} '7-Zip\7z.exe') }
    $cmd7z = Get-Command 7z.exe -ErrorAction SilentlyContinue
    if ($cmd7z) { $candidates += $cmd7z.Source }
    $sevenZip = $candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
    if (!$sevenZip) {
        throw 'Required fonts are missing and 7-Zip was not found. Install 7-Zip only if font extraction is actually needed.'
    }

    $tmp = Join-Path $env:TEMP ("p49_fonts_" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    try {
        & $sevenZip x "-o$tmp" -y $FontsArchivePath | Out-Host
        if ($LASTEXITCODE -ne 0) { throw "7-Zip extraction failed with exit code $LASTEXITCODE" }
        foreach ($name in $wanted) {
            $src = Get-ChildItem -Path $tmp -Recurse -File -Filter $name | Select-Object -First 1
            if (!$src) { throw "Required font missing from archive: $name" }
            Copy-Item $src.FullName (Join-Path $fontDir $name) -Force
        }
    } finally {
        if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
    }
}

if (-not (Test-RequiredFontsPresent)) { throw 'IRANSans FaNum verification failed after installation.' }

Write-Host "BRAND_LOGO_SHA256=$actual" -ForegroundColor Green
Write-Host "BRAND_LOGO=$brandTarget" -ForegroundColor Green
if ($reusedExistingFonts) {
    Write-Host 'IRANSANS_SOURCE=existing-project-files' -ForegroundColor Green
} else {
    Write-Host 'IRANSANS_SOURCE=archive-extraction' -ForegroundColor Green
}
Write-Host 'IRANSANS_FANUM_WEIGHTS=6' -ForegroundColor Green
Write-Host 'PHASE49_2B_BRAND_ASSETS_READY=OK' -ForegroundColor Green
