<#
.SYNOPSIS
    Appends one timestamped row to the Progress table in a ticket's plan.

.DESCRIPTION
    The caller supplies what happened. This script supplies the time. There is deliberately no
    time parameter: a timestamp typed by the caller is a timestamp the caller invented, because an
    agent's context carries the date but never the clock.

    Anchors on the '## Progress' heading and owns everything below it — creating the table when the
    section is still empty, then appending to it.
#>
[CmdletBinding(DefaultParameterSetName = 'Now')]
param(
    # Folder name under ~/.claude/tickets, e.g. SW-12345-some-title.
    [Parameter(Mandatory = $true)]
    [string]$TicketFolder,

    # Prose about the outcome: what completed, the result, any deviation from the plan.
    [Parameter(Mandatory = $true)]
    [string]$Entry,

    # A file the work wrote (test log, seed log, ticket dump). Its mtime is when the work happened,
    # which is what the row should say — not the clock at write-time.
    [Parameter(ParameterSetName = 'Artifact')]
    [string]$ArtifactPath,

    # A commit the work produced. Its author date is used.
    [Parameter(ParameterSetName = 'Commit')]
    [string]$CommitSha
)

$ErrorActionPreference = 'Stop'

$timeFormat = 'yyyy-MM-dd h:mm tt'
$headerRow = '| When | What happened |'
$separatorRow = '|---|---|'

$planPath = Join-Path $HOME ".claude/tickets/$TicketFolder/plan.md"
if (-not (Test-Path -LiteralPath $planPath)) {
    throw "No plan at $planPath. Check the ticket folder name."
}

# --- Resolve the timestamp -------------------------------------------------------------------

switch ($PSCmdlet.ParameterSetName) {
    'Artifact' {
        if (-not (Test-Path -LiteralPath $ArtifactPath)) {
            throw "No artifact at $ArtifactPath."
        }
        $stamp = (Get-Item -LiteralPath $ArtifactPath).LastWriteTime.ToString($timeFormat)
        $timeSource = "mtime of $(Split-Path $ArtifactPath -Leaf)"
    }
    'Commit' {
        $isoDate = & git log -1 --format=%aI $CommitSha 2>$null
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($isoDate)) {
            throw "Could not read commit $CommitSha. Run from inside the repo, and check the sha."
        }
        $stamp = ([datetimeoffset]$isoDate).LocalDateTime.ToString($timeFormat)
        $timeSource = "author date of $($CommitSha.Substring(0, [Math]::Min(11, $CommitSha.Length)))"
    }
    default {
        $stamp = (Get-Date).ToString($timeFormat)
        $timeSource = 'current local time'
    }
}

# --- Read the plan, preserving newline style and BOM ----------------------------------------

$rawBytes = [System.IO.File]::ReadAllBytes($planPath)
$hasBom = $rawBytes.Length -ge 3 -and $rawBytes[0] -eq 0xEF -and $rawBytes[1] -eq 0xBB -and $rawBytes[2] -eq 0xBF
$text = [System.Text.Encoding]::UTF8.GetString($rawBytes).TrimStart([char]0xFEFF)
$newline = if ($text.Contains("`r`n")) { "`r`n" } else { "`n" }

$lines = [System.Collections.Generic.List[string]]($text -split "`r`n|`n")

# --- Locate the Progress section -------------------------------------------------------------

$headingIndex = -1
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^##\s+Progress\s*$') {
        $headingIndex = $i
        break
    }
}
if ($headingIndex -lt 0) {
    throw "No '## Progress' heading in $planPath. Add the heading; this script owns the table below it."
}

# Walk forward to the last contiguous table row under the heading. Blank lines between the heading
# and the table are normal; a blank line after the table ends it.
$insertAt = -1
$sawTable = $false
for ($i = $headingIndex + 1; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\|.*\|\s*$') {
        $sawTable = $true
        $insertAt = $i
        continue
    }
    if ($sawTable) { break }
    if ($lines[$i] -match '^##\s') { break }
}

$createdTable = $false
if (-not $sawTable) {
    # Empty section: lay down the header and separator, then the row goes after them.
    $at = $headingIndex + 1
    if ($at -lt $lines.Count -and [string]::IsNullOrWhiteSpace($lines[$at])) { $at++ }
    $lines.Insert($at, $headerRow)
    $lines.Insert($at + 1, $separatorRow)
    $insertAt = $at + 1
    $createdTable = $true
}

$lines.Insert($insertAt + 1, "| $stamp | $Entry |")

# --- Write back ------------------------------------------------------------------------------

$outText = [string]::Join($newline, $lines)
$encoding = New-Object System.Text.UTF8Encoding($hasBom)
[System.IO.File]::WriteAllBytes($planPath, $encoding.GetBytes($outText))

Write-Host "Added to $planPath"
if ($createdTable) { Write-Host "  (created the Progress table — the section was empty)" }
Write-Host "  | $stamp | $Entry |"
Write-Host "  time source: $timeSource"
