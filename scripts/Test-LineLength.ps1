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

if ($Mode -eq 'local') {
    $diffArgs = @('diff', '--unified=0', 'HEAD')
}
else {
    $diffArgs = @('diff', '--unified=0', 'development...HEAD')
}

$diff = & git @diffArgs
if (-not $diff) {
    Write-Host "No diff to check." -ForegroundColor Green
    exit 0
}

$violations = [System.Collections.ArrayList]::new()
$currentFile = $null
$lineNum = 0

foreach ($line in $diff) {
    # File header: +++ b/path/to/file
    if ($line -match '^\+\+\+ b/(.+)$') {
        $currentFile = $Matches[1]
        continue
    }

    # Only check .cs files — line-length rule is C#-specific.
    if ($currentFile -and -not $currentFile.EndsWith('.cs')) {
        continue
    }

    # Hunk header: @@ -X,Y +Z,W @@  (W is optional, defaults to 1)
    if ($line -match '^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@') {
        $lineNum = [int]$Matches[1] - 1
        continue
    }

    # Added line (excludes the +++ header which we matched above)
    if ($line.StartsWith('+')) {
        $lineNum++
        $content = $line.Substring(1)
        if ($content.Length -gt $MaxLength) {
            [void]$violations.Add([PSCustomObject]@{
                File    = $currentFile
                Line    = $lineNum
                Length  = $content.Length
                Content = $content
            })
        }
    }
    # `-` removed line — does NOT advance new-file counter, skip
    # context line — never appears with --unified=0
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
