# Stage or execute a batch of YouTrack actions under a single content-bound approval.
# All validation, rendering, and execution logic lives in ~/.claude/hooks/youtrack_batch.py
# (single source of truth shared with the pretooluse.py gate); this wrapper only routes
# arguments and supplies the API token.
#
# Usage:
#   & "$HOME/.claude/scripts/YouTrack-Batch.ps1" -Stage -File <batch.json>
#   & "$HOME/.claude/scripts/YouTrack-Batch.ps1" -Execute -Hash <hash>
param(
    [switch]$Stage,
    [switch]$Execute,
    [string]$File,
    [string]$Hash
)

$ErrorActionPreference = 'Stop'
$module = Join-Path $HOME '.claude/hooks/youtrack_batch.py'

if ($Stage) {
    if (-not $File) { throw '-Stage requires -File <batch.json>' }
    python $module stage --file $File
    exit $LASTEXITCODE
}

if ($Execute) {
    if (-not $Hash) { throw '-Execute requires -Hash <hash>' }
    $env:YOUTRACK_API_TOKEN = [Environment]::GetEnvironmentVariable('YOUTRACK_API_TOKEN', 'User')
    python $module execute --hash $Hash
    exit $LASTEXITCODE
}

throw 'Specify -Stage -File <batch.json> or -Execute -Hash <hash>'
