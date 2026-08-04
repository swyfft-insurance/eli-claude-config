#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Wraps Seed-Database-Local.ps1 / Seed-Elements-Local.ps1 with deterministic
    full-output capture to a file in the ticket's artifacts area
    (~/.claude/tickets/<TicketFolder>/artifacts/seed/).

    Always prints the log file path and the last 30 lines of the log so the
    caller can verify completion without re-running.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('database', 'elements')]
    [string]$Mode,

    [Parameter(Mandatory = $true)]
    [string]$TicketFolder
)

$ErrorActionPreference = 'Stop'

$logDir = Join-Path $HOME ".claude/tickets/$TicketFolder/artifacts/seed"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

$branch = (git branch --show-current 2>$null) -replace '[\\/]', '-'
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$logPath = Join-Path $logDir "$($branch)_$($Mode)_$timestamp.txt"

$scriptName = if ($Mode -eq 'database') { 'Seed-Database-Local.ps1' } else { 'Seed-Elements-Local.ps1' }

# Anchor to the repo root rather than the caller's working directory. The seed scripts live at the
# repo root and reference their own siblings relatively, so invoking them from anywhere else fails.
$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) {
    Write-Host "ERROR: not inside a git repository, so the repo root could not be resolved."
    exit 1
}

$repoRoot = $repoRoot.Trim() -replace '/', [IO.Path]::DirectorySeparatorChar
$script = Join-Path $repoRoot $scriptName

if (-not (Test-Path -LiteralPath $script)) {
    Write-Host "ERROR: seed script not found: $script"
    exit 1
}

Write-Host "Seed mode: $Mode"
Write-Host "Log:       $logPath"
Write-Host "Running:   $script"
Write-Host ""

# The seed scripts assume the repo root is the working directory.
Push-Location $repoRoot
try {
    # '*>&1' folds the error stream into output so the log captures everything - which also means a
    # terminating error arrives as text rather than an exception, so $? and $LASTEXITCODE are the only
    # signals left. Seed a sentinel so a script that never runs cannot look like a clean exit 0.
    $global:LASTEXITCODE = 0
    & $script *>&1 | Tee-Object -FilePath $logPath
    $seedSucceeded = $?
    $seedExitCode = $LASTEXITCODE
} finally {
    Pop-Location
}

if (-not $seedSucceeded -and $seedExitCode -eq 0) {
    Write-Host ""
    Write-Host "ERROR: the seed script failed without setting an exit code - reporting failure."
    $seedExitCode = 1
}

Write-Host ""
Write-Host "===== Last 30 lines of $logPath ====="
Get-Content -Path $logPath -Tail 30

Write-Host ""
Write-Host "Seed exit code: $seedExitCode"
Write-Host "Full log:       $logPath"

exit $seedExitCode
