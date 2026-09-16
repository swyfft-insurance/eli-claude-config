<#
.SYNOPSIS
    Safe git diff wrapper. Prevents conflating uncommitted vs committed diffs, and never drops
    untracked files.

.PARAMETER Mode
    Required.
      local  - uncommitted changes (working tree vs HEAD), including untracked files.
      branch - committed changes on this branch vs development.
      all    - everything the branch carries vs development: committed, uncommitted and untracked.

.PARAMETER Path
    Optional file or directory path to scope the diff.

.PARAMETER StatOnly
    Show only --stat summary, not full diff.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('local', 'branch', 'all')]
    [string]$Mode,

    [string]$Path,

    [switch]$StatOnly
)

$ErrorActionPreference = 'Stop'

# Local 'development' is routinely stale on a machine that lives on feature branches, so the
# remote-tracking ref is the baseline whenever it exists.
function Get-DevelopmentRef {
    git rev-parse --verify --quiet origin/development 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { return 'origin/development' }
    return 'development'
}

# git diff shows tracked files only. Files created on the branch are untracked until staged, so
# every mode that reads the working tree renders them as full additions.
function Show-UntrackedFiles {
    param([string]$ScopePath, [switch]$Stat)

    $untracked = @(git ls-files --others --exclude-standard)
    if ($ScopePath) {
        $normalized = $ScopePath.TrimEnd('/', '\').Replace('\', '/')
        $untracked = @($untracked | Where-Object { $_ -eq $normalized -or $_.StartsWith("$normalized/") })
    }
    if (-not $untracked) { return }

    Write-Host ""
    Write-Host "=== UNTRACKED (new, not yet added) files, shown as full additions ===" -ForegroundColor Cyan
    foreach ($file in $untracked) {
        # safecrlf=false silences the "LF will be replaced by CRLF" warning a not-yet-added file emits.
        $gitArgs = @('-c', 'core.safecrlf=false', 'diff', '--no-index')
        if ($Stat) { $gitArgs += '--stat' }
        $gitArgs += @('--', '/dev/null', $file)
        # --no-index exits 1 whenever the files differ, which here is always.
        & git @gitArgs
    }
}

function Show-TrackedDiff {
    param([string]$Range, [string]$ScopePath, [switch]$Stat)

    $gitArgs = @('diff', $Range)
    if ($Stat) { $gitArgs += '--stat' }
    if ($ScopePath) { $gitArgs += '--'; $gitArgs += $ScopePath }
    & git @gitArgs
}

switch ($Mode) {
    'local' {
        Write-Host "=== DIFF: Uncommitted changes (working tree vs last commit) ===" -ForegroundColor Cyan
        Show-TrackedDiff -Range 'HEAD' -ScopePath $Path -Stat:$StatOnly
        Show-UntrackedFiles -ScopePath $Path -Stat:$StatOnly
    }
    'branch' {
        # Preflight: warn about uncommitted changes
        $dirty = git status --porcelain 2>&1
        if ($dirty) {
            Write-Host "WARNING: Uncommitted changes exist. They will NOT appear in this diff." -ForegroundColor Yellow
            Write-Host "Use '/eli--diff local' for uncommitted changes, or '/eli--diff all' for both." -ForegroundColor Yellow
            Write-Host ""
        }

        $devRef = Get-DevelopmentRef
        Write-Host "=== DIFF: Committed changes on this branch vs $devRef ===" -ForegroundColor Cyan
        Show-TrackedDiff -Range "$devRef...HEAD" -ScopePath $Path -Stat:$StatOnly
    }
    'all' {
        # The merge base is where this branch left development. Working tree vs that point covers
        # every commit on the branch plus every uncommitted edit in one diff.
        $devRef = Get-DevelopmentRef
        $mergeBase = (git merge-base $devRef HEAD).Trim()
        Write-Host "=== DIFF: Everything on this branch vs $devRef (committed + uncommitted + untracked) ===" -ForegroundColor Cyan
        Show-TrackedDiff -Range $mergeBase -ScopePath $Path -Stat:$StatOnly
        Show-UntrackedFiles -ScopePath $Path -Stat:$StatOnly
    }
}
