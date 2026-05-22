#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Wraps Seed-Database-Local.ps1 / Seed-Elements-Local.ps1 with deterministic
    full-output capture to a file in $env:TEMP\swyfft-seed\.

    Always prints the log file path and the last 30 lines of the log so the
    caller can verify completion without re-running.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('database', 'elements')]
    [string]$Mode
)

$ErrorActionPreference = 'Stop'

$logDir = Join-Path $env:TEMP 'swyfft-seed'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

$branch = (git branch --show-current 2>$null) -replace '[\\/]', '-'
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$logPath = Join-Path $logDir "$($branch)_$($Mode)_$timestamp.txt"

$script = if ($Mode -eq 'database') { './Seed-Database-Local.ps1' } else { './Seed-Elements-Local.ps1' }

Write-Host "Seed mode: $Mode"
Write-Host "Log:       $logPath"
Write-Host "Running:   $script"
Write-Host ""

& $script *>&1 | Tee-Object -FilePath $logPath
$seedExitCode = $LASTEXITCODE

Write-Host ""
Write-Host "===== Last 30 lines of $logPath ====="
Get-Content -Path $logPath -Tail 30

Write-Host ""
Write-Host "Seed exit code: $seedExitCode"
Write-Host "Full log:       $logPath"

exit $seedExitCode
