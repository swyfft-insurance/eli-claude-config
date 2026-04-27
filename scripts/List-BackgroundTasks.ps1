<#
.SYNOPSIS
    Lists background task output files for Claude Code sessions.

.DESCRIPTION
    Scans the Claude temp directory for task output files. By default shows
    only the most recent session per CWD. Use -All for all sessions.

    Status logic:
    - Non-zero file size -> "done" (output was written)
    - Zero-byte in the most recent session -> "RUNNING?" (probably still active)
    - Zero-byte in an older session -> "no output" (agent completed but didn't persist)

.PARAMETER Cwd
    Override CWD for session lookup. Defaults to showing all CWDs.

.PARAMETER All
    Show tasks from all sessions, not just the most recent per CWD.

.PARAMETER SessionId
    Target a specific session UUID.
#>
param(
    [string]$Cwd,
    [switch]$All,
    [string]$SessionId
)

# Resolve the real temp path — bash /tmp != pwsh /tmp on Windows
$tmpBase = Join-Path ([System.IO.Path]::GetTempPath()) "claude"
if (-not (Test-Path $tmpBase)) {
    Write-Output "No Claude task directory found at $tmpBase"
    exit 0
}

# Encode CWD to match Claude's directory naming: C:\Users\foo -> C--Users-foo
function Encode-Cwd([string]$path) {
    $path = $path -replace '/', '\'
    if ($path -match '^([A-Za-z]):\\(.*)$') {
        $drive = $Matches[1]
        $rest = $Matches[2] -replace '\\', '-'
        return "$drive--$rest"
    }
    return ($path -replace '/', '-').TrimStart('-')
}

# Resolve target CWD directories
if ($Cwd) {
    $encoded = Encode-Cwd $Cwd
    $cwdDirs = @(Join-Path $tmpBase $encoded)
} else {
    $cwdDirs = Get-ChildItem -Path $tmpBase -Directory | Select-Object -ExpandProperty FullName
}

$results = @()

foreach ($cwdDir in $cwdDirs) {
    if (-not (Test-Path $cwdDir)) { continue }

    $cwdName = Split-Path $cwdDir -Leaf

    # Get session directories sorted by recency
    $allSessions = Get-ChildItem -Path $cwdDir -Directory | Sort-Object LastWriteTime -Descending
    $latestSessionName = if ($allSessions.Count -gt 0) { $allSessions[0].Name } else { $null }

    if ($SessionId) {
        $sessions = $allSessions | Where-Object { $_.Name -eq $SessionId }
    } elseif (-not $All) {
        $sessions = $allSessions | Select-Object -First 1
    } else {
        $sessions = $allSessions
    }

    foreach ($session in $sessions) {
        $tasksDir = Join-Path $session.FullName "tasks"
        if (-not (Test-Path $tasksDir)) { continue }

        $isLatest = $session.Name -eq $latestSessionName
        $taskFiles = Get-ChildItem -Path $tasksDir -Filter "*.output" | Sort-Object LastWriteTime -Descending

        foreach ($tf in $taskFiles) {
            $size = $tf.Length
            if ($size -gt 0) {
                $status = "done"
            } elseif ($isLatest) {
                $status = "RUNNING?"
            } else {
                $status = "no output"
            }

            $results += [PSCustomObject]@{
                CWD       = $cwdName
                Session   = $session.Name.Substring(0, 8) + "..."
                TaskId    = $tf.BaseName
                Status    = $status
                Size      = if ($size -eq 0) { "0 B" } elseif ($size -lt 1024) { "$size B" } else { "$([math]::Round($size / 1024, 1)) KB" }
                Timestamp = $tf.LastWriteTime.ToString("HH:mm:ss")
            }
        }
    }
}

if ($results.Count -eq 0) {
    Write-Output "No background tasks found."
} else {
    $results | Format-Table -AutoSize -Property TaskId, Status, Size, Timestamp, Session, CWD
    $running = @($results | Where-Object Status -eq 'RUNNING?').Count
    Write-Output "Total: $($results.Count) tasks ($running possibly still running)"
}
