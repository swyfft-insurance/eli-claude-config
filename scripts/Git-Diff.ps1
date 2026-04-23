<#
.SYNOPSIS
    Safe git diff wrapper. Prevents conflating uncommitted vs committed diffs.

.PARAMETER Mode
    Required. "local" for uncommitted changes, "branch" for committed vs development.

.PARAMETER Path
    Optional file path to scope the diff.

.PARAMETER StatOnly
    Show only --stat summary, not full diff.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('local', 'branch')]
    [string]$Mode,

    [string]$Path,

    [switch]$StatOnly
)

$ErrorActionPreference = 'Stop'

if ($Mode -eq 'local') {
    Write-Host "=== DIFF: Uncommitted changes (working tree vs last commit) ===" -ForegroundColor Cyan
    $args = @('diff', 'HEAD')
    if ($StatOnly) { $args += '--stat' }
    if ($Path) { $args += '--'; $args += $Path }
    & git @args
}
elseif ($Mode -eq 'branch') {
    # Preflight: warn about uncommitted changes
    $dirty = git status --porcelain 2>&1
    if ($dirty) {
        Write-Host "WARNING: Uncommitted changes exist. They will NOT appear in this diff." -ForegroundColor Yellow
        Write-Host "Use '/diff local' to see uncommitted changes, or commit first." -ForegroundColor Yellow
        Write-Host ""
    }

    Write-Host "=== DIFF: Committed changes on this branch vs development ===" -ForegroundColor Cyan
    $args = @('diff', 'development...HEAD')
    if ($StatOnly) { $args += '--stat' }
    if ($Path) { $args += '--'; $args += $Path }
    & git @args
}
