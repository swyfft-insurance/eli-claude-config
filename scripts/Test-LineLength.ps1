<#
.SYNOPSIS
    Check that newly-added/modified lines in the diff don't exceed a max line length.

.DESCRIPTION
    Parses unified diff output (--unified=0) and reports any added line longer than
    -MaxLength characters. Pre-existing long lines that aren't being touched are ignored.

.PARAMETER Mode
    Required. "local" for uncommitted changes, "branch" for committed vs development.

.PARAMETER MaxLength
    Maximum allowed line length. Default 120.

.EXAMPLE
    pwsh -NoProfile -File "$HOME/.claude/scripts/Test-LineLength.ps1" -Mode local
    pwsh -NoProfile -File "$HOME/.claude/scripts/Test-LineLength.ps1" -Mode branch -MaxLength 120
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('local', 'branch')]
    [string]$Mode,

    [int]$MaxLength = 120
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '_Diff-Helpers.ps1')

$violations = [System.Collections.ArrayList]::new()
foreach ($entry in Get-CSharpDiffLines -Mode $Mode) {
    if ($entry.Content.Length -gt $MaxLength) {
        [void]$violations.Add([PSCustomObject]@{
            File    = $entry.File
            Line    = $entry.Line
            Length  = $entry.Content.Length
            Content = $entry.Content
        })
    }
}

if ($violations.Count -eq 0) {
    Write-Host "OK: no added lines over $MaxLength chars." -ForegroundColor Green
    exit 0
}

Write-Host "FAIL: $($violations.Count) added line(s) over $MaxLength chars:" -ForegroundColor Red
foreach ($v in $violations) {
    Write-Host ("  {0}:{1} ({2} chars)" -f $v.File, $v.Line, $v.Length) -ForegroundColor Red
    Write-Host ("    {0}" -f $v.Content) -ForegroundColor DarkGray
}
exit 1
