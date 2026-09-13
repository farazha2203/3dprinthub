[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidateRange(1024, 65535)][int]$Port,
    [string]$Command,
    [string]$Cwd,
    [ValidateRange(1, 1200)][int]$Timeout = 120,
    [switch]$Health
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$BaseUri = "http://127.0.0.1:$Port"

$Token = [Environment]::GetEnvironmentVariable('OPERATOR_BRIDGE_TOKEN', 'Process')
if ([string]::IsNullOrWhiteSpace($Token) -or $Token -notmatch '^[0-9A-Fa-f]{64}$') {
    throw 'Set process environment variable OPERATOR_BRIDGE_TOKEN to the 64-hex session token.'
}

$Headers = @{ Authorization = "Bearer $Token" }
if ($Health) {
    Invoke-RestMethod -Method Get -Uri "$BaseUri/health" -Headers $Headers
    return
}
if ([string]::IsNullOrWhiteSpace($Command)) {
    throw 'Command is required unless -Health is used.'
}

$Payload = @{
    command = $Command
    timeout = $Timeout
}
if (-not [string]::IsNullOrWhiteSpace($Cwd)) {
    $Payload.cwd = $Cwd
}

$Body = $Payload | ConvertTo-Json -Compress
$Result = Invoke-RestMethod -Method Post -Uri "$BaseUri/exec" -Headers $Headers -ContentType 'application/json' -Body $Body

if ($Result.stdout) { [Console]::Out.Write($Result.stdout) }
if ($Result.stderr) { [Console]::Error.Write($Result.stderr) }
if (-not $Result.ok) {
    Write-Error "Remote command failed with return code $($Result.returncode)."
}
$Result
