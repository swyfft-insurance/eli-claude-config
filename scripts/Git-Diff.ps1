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

.PARAMETER Base
    Optional ref that `branch` and `all` compare against instead of origin/development. For a branch
    in a gh stack, pass the branch below it (origin/<branch>) so the diff holds only this layer.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('local', 'branch', 'all')]
    [string]$Mode,

    [string]$Path,

    [switch]$StatOnly,

    [string]$Base
)

$ErrorActionPreference = 'Stop'

# git ls-files lists only the current directory, while git diff always covers the repo. Running from
# the repo root keeps both halves, and -Path, relative to the same place.
$RepoRoot = 'C:\Users\eli.koslofsky\Documents\GitHub\swyfft_web'
Set-Location $RepoRoot

. (Join-Path $PSScriptRoot '_Diff-Helpers.ps1')

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

$baseRef = if ($Base) {
    git rev-parse --verify --quiet $Base | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Base ref '$Base' does not exist. Fetch it first." }
    $Base
} else { Get-DevelopmentRef }

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

        Write-Host "=== DIFF: Committed changes on this branch vs $baseRef ===" -ForegroundColor Cyan
        Show-TrackedDiff -Range "$baseRef...HEAD" -ScopePath $Path -Stat:$StatOnly
    }
    'all' {
        # The merge base is where this branch left development. Working tree vs that point covers
        # every commit on the branch plus every uncommitted edit in one diff.
        $mergeBase = (git merge-base $baseRef HEAD).Trim()
        Write-Host "=== DIFF: Everything on this branch vs $baseRef (committed + uncommitted + untracked) ===" -ForegroundColor Cyan
        Show-TrackedDiff -Range $mergeBase -ScopePath $Path -Stat:$StatOnly
        Show-UntrackedFiles -ScopePath $Path -Stat:$StatOnly
    }
}
