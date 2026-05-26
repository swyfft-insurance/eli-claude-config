<#
.SYNOPSIS
    Check that newly-added/modified .cs lines use the canonical "EAndS" capitalization
    instead of "E&S", "E&amp;S", "EandS", or other variants.

.DESCRIPTION
    Parses unified diff output (--unified=0) and reports any added line containing an
    "Excess and Surplus" reference that isn't a canonical form.

    Allowed forms:
      - "EAndS"  — PascalCase identifier; allowed anywhere (code and comments).
      - "eAndS"  — camelCase identifier; allowed only in the code portion of a line.

    Everything else ("E&S", "E&amp;S", "EandS", "EAnds", "eands", "EANDS", "e&s", ...)
    is flagged. The repo standard is to spell out "EAndS" — `&` is reserved in XML doc
    comments and unfriendly in identifiers (per project CLAUDE.md).

    Code-vs-comment split (best-effort; not a full C# parser):
      - Lines whose first non-whitespace char is `*` are treated as block-comment
        continuation (` * foo`) — entire line is a comment.
      - Otherwise the first `//` in the line starts the comment portion (catches both
        `//` line comments and `///` XML doc comments).

.PARAMETER Mode
    Required. "local" for uncommitted changes, "branch" for committed vs development.

.EXAMPLE
    pwsh -NoProfile -File "$HOME/.claude/scripts/Test-EAndSSpelling.ps1" -Mode local
    pwsh -NoProfile -File "$HOME/.claude/scripts/Test-EAndSSpelling.ps1" -Mode branch
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('local', 'branch')]
    [string]$Mode
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '_Diff-Helpers.ps1')

# Matches the "Excess and Surplus" family with case-insensitive middle/end so we can
# catch every wrong variant. Word boundaries prevent matching substrings of longer
# identifiers (e.g. nothing in "EAndStateConfig" matches because S is followed by 't').
$pattern = '\b[Ee](?:&amp;|&|[Aa][Nn][Dd])[Ss]\b'

# Case-sensitive allow-lists.
$codeAllowed    = @('EAndS', 'eAndS')   # PascalCase + camelCase identifiers
$commentAllowed = @('EAndS')            # only PascalCase in prose

function Split-CodeAndComment([string]$line) {
    # Block-comment continuation: " * foo" — treat the whole line as a comment.
    if ($line.TrimStart().StartsWith('*')) {
        return @{ Code = ''; Comment = $line }
    }

    # First `//` (catches `///` too) splits code from comment. No string-literal
    # awareness — `"//"` inside a string mis-classifies the tail, accepted tradeoff.
    $idx = $line.IndexOf('//')
    if ($idx -ge 0) {
        return @{ Code = $line.Substring(0, $idx); Comment = $line.Substring($idx) }
    }

    return @{ Code = $line; Comment = '' }
}

$violations = [System.Collections.ArrayList]::new()
foreach ($entry in Get-CSharpDiffLines -Mode $Mode) {
    $split = Split-CodeAndComment $entry.Content

    foreach ($m in [regex]::Matches($split.Code, $pattern)) {
        if ($m.Value -cnotin $codeAllowed) {
            [void]$violations.Add([PSCustomObject]@{
                File    = $entry.File
                Line    = $entry.Line
                Found   = $m.Value
                Where   = 'code'
                Content = $entry.Content
            })
        }
    }

    foreach ($m in [regex]::Matches($split.Comment, $pattern)) {
        if ($m.Value -cnotin $commentAllowed) {
            [void]$violations.Add([PSCustomObject]@{
                File    = $entry.File
                Line    = $entry.Line
                Found   = $m.Value
                Where   = 'comment'
                Content = $entry.Content
            })
        }
    }
}

if ($violations.Count -eq 0) {
    Write-Host "OK: all 'E and S' references use canonical 'EAndS' (or 'eAndS' in code)." -ForegroundColor Green
    exit 0
}

Write-Host "FAIL: $($violations.Count) non-canonical 'EAndS' spelling(s):" -ForegroundColor Red
foreach ($v in $violations) {
    $fix = if ($v.Where -eq 'comment') { "use 'EAndS'" } else { "use 'EAndS' or 'eAndS'" }
    Write-Host ("  {0}:{1} [{2}] -> '{3}' ({4})" -f $v.File, $v.Line, $v.Where, $v.Found, $fix) -ForegroundColor Red
    Write-Host ("    {0}" -f $v.Content) -ForegroundColor DarkGray
}
exit 1
