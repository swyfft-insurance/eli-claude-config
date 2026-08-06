#Requires -Version 7
<#
.SYNOPSIS
    Reports what is on disk under ~/.claude/tickets/, oldest first. Read-only.
.DESCRIPTION
    For each ticket folder: when work started and when it was last touched, total size, how much
    of that size is reclaimable (everything git does not track), and whether a plan exists.
    Never modifies anything.
.PARAMETER Json
    Emit objects instead of a formatted table, for further filtering.
#>
[CmdletBinding()]
param(
    [switch] $Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ticketsRoot = Join-Path $HOME '.claude/tickets'
if (-not (Test-Path $ticketsRoot)) {
    Write-Host "No tickets directory at $ticketsRoot."
    return
}

function Format-Size {
    param([long] $Bytes)
    if ($Bytes -ge 1GB) { return '{0:N1} GB' -f ($Bytes / 1GB) }
    if ($Bytes -ge 1MB) { return '{0:N1} MB' -f ($Bytes / 1MB) }
    if ($Bytes -ge 1KB) { return '{0:N0} KB' -f ($Bytes / 1KB) }
    return "$Bytes B"
}

# Only these paths are tracked by .gitignore. Everything else in a ticket folder is reclaimable,
# so reclaimable size is computed by subtraction rather than by naming dump folders. An enumerated
# list silently undercounts any subfolder nobody thought to add (artifacts/bsod, for one).
function Get-TrackedBytes {
    param([string] $FolderPath)

    $tracked = [long]0

    $planPath = Join-Path $FolderPath 'plan.md'
    if (Test-Path $planPath) {
        $tracked += (Get-Item -LiteralPath $planPath).Length
    }

    $artifactsPath = Join-Path $FolderPath 'artifacts'
    foreach ($name in @('db-queries', 'pr')) {
        $path = Join-Path $artifactsPath $name
        if (Test-Path $path) {
            $files = Get-ChildItem -LiteralPath $path -Recurse -File -Force -ErrorAction SilentlyContinue
            if ($files) {
                $tracked += [long](($files | Measure-Object -Property Length -Sum).Sum)
            }
        }
    }

    return $tracked
}

$now = Get-Date
$rows = foreach ($dir in Get-ChildItem -LiteralPath $ticketsRoot -Directory -Force) {
    $files = Get-ChildItem -LiteralPath $dir.FullName -Recurse -File -Force -ErrorAction SilentlyContinue

    # Age comes from the creation time of the oldest file, which is when work on the ticket
    # actually started. Write times move whenever a file is rewritten, and the newest file is
    # worse still: re-reading a ticket drops a fresh dump into an otherwise dormant folder.
    if ($files) {
        $created = ($files | Measure-Object -Property CreationTime -Minimum).Minimum
        $totalBytes = [long](($files | Measure-Object -Property Length -Sum).Sum)
    }
    else {
        $created = $dir.CreationTime
        $totalBytes = [long]0
    }

    $trackedBytes = Get-TrackedBytes -FolderPath $dir.FullName

    # A bare SW number says nothing about what the folder holds. The title is already on disk in
    # the newest ticket dump, so read it from there rather than calling YouTrack.
    $title = ''
    $dumpRoot = Join-Path $dir.FullName 'artifacts\ticket-dumps'
    if (Test-Path $dumpRoot) {
        $latestDump = Get-ChildItem -LiteralPath $dumpRoot -Directory -ErrorAction SilentlyContinue |
            Sort-Object Name |
            Select-Object -Last 1
        if ($latestDump) {
            $jsonPath = Join-Path $latestDump.FullName 'ticket.json'
            if (Test-Path $jsonPath) {
                try {
                    $title = (Get-Content -LiteralPath $jsonPath -Raw -Encoding UTF8 | ConvertFrom-Json).summary
                }
                catch {
                    $title = ''
                }
            }
        }
    }

    [pscustomobject]@{
        Folder       = $dir.Name
        Title        = $title
        AgeDays      = [int]($now - $created).TotalDays
        Created      = $created
        Bytes        = $totalBytes
        TrackedBytes = $trackedBytes
        Plan         = (Test-Path (Join-Path $dir.FullName 'plan.md'))
        IsPrReview   = $dir.Name.StartsWith('pr-review-')
    }
}

if (-not $rows) {
    Write-Host "No ticket folders under $ticketsRoot."
    return
}

$sorted = $rows | Sort-Object -Property AgeDays -Descending

if ($Json) {
    $sorted | ConvertTo-Json -Depth 3
    return
}

# Fixed-width rendering rather than Format-Table. AutoSize divides the console width among the
# columns, and the long folder names starve Title down to a few characters.
$wTitle = 62
$wFolder = 42

function Format-Cell {
    param([string] $Text, [int] $Width)
    if ($null -eq $Text) { $Text = '' }
    if ($Text.Length -gt $Width) { return $Text.Substring(0, $Width - 1) + '…' }
    return $Text.PadRight($Width)
}

function Show-Section {
    param([object[]] $Rows, [string] $Heading)

    if (-not $Rows) { return }
    Write-Host ''
    Write-Host $Heading
    Write-Host ('{0} {1} {2} {3} {4} {5}' -f `
        (Format-Cell 'Title' $wTitle), 'Age  ', 'Created   ', 'Size     ', 'Plan', (Format-Cell 'Folder' $wFolder))
    Write-Host ('{0} {1} {2} {3} {4} {5}' -f `
        ('-' * $wTitle), '-----', '----------', '---------', '----', ('-' * $wFolder))

    foreach ($r in $Rows) {
        Write-Host ('{0} {1} {2} {3} {4} {5}' -f `
            (Format-Cell $r.Title $wTitle),
            "$($r.AgeDays)d".PadRight(5),
            $r.Created.ToString('yyyy-MM-dd'),
            (Format-Size $r.Bytes).PadLeft(9),
            $(if ($r.Plan) { 'yes ' } else { 'no  ' }),
            (Format-Cell $r.Folder $wFolder))
    }
}

$own = @($sorted | Where-Object { -not $_.IsPrReview })
$reviews = @($sorted | Where-Object { $_.IsPrReview })

Show-Section -Rows $own -Heading 'YOUR TICKET WORK'
Show-Section -Rows $reviews -Heading "PR REVIEW DUMPS (other people's tickets, byproduct of /eli--review-prs-parallel)"

$totalBytes = [long](($sorted | Measure-Object -Property Bytes -Sum).Sum)
$totalTracked = [long](($sorted | Measure-Object -Property TrackedBytes -Sum).Sum)

Write-Host ''
Write-Host ("{0} folders, {1} total, of which {2} is git-tracked." -f `
        $sorted.Count, (Format-Size $totalBytes), (Format-Size $totalTracked))
if ($reviews) {
    $reviewBytes = [long](($reviews | Measure-Object -Property Bytes -Sum).Sum)
    Write-Host ("{0} of those are PR review dumps ({1})." -f $reviews.Count, (Format-Size $reviewBytes))
}
Write-Host "Age is from the creation date of the oldest file in the folder."
