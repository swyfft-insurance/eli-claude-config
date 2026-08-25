# Launches Claude Code with the always-on behavioral rules appended to the system prompt, so they
# sit above user-turn content and are never compacted away. The combined file is rebuilt on every
# launch, so edits to the source rules take effect the next time you start a session.
#
# Dot-source this from your PowerShell profile:
#   . "$HOME\.claude\scripts\Claude-Wrapper.ps1"

function claude {
    $systemDir = Join-Path $HOME '.claude\system'
    $generated = Join-Path $systemDir 'system-prompt.md'
    $sources = @(
        (Join-Path $HOME '.claude\rules\core-behavior.md'),
        (Join-Path $HOME '.claude\rules\talking-to-eli.md')
    )

    $missing = $sources | Where-Object { -not (Test-Path $_) }
    if ($missing) {
        Write-Warning "Claude wrapper: missing rule file(s), launching without them:`n$($missing -join "`n")"
        $sources = $sources | Where-Object { Test-Path $_ }
    }

    if (-not (Test-Path $systemDir)) {
        New-Item -ItemType Directory -Path $systemDir | Out-Null
    }

    if ($sources) {
        ($sources | ForEach-Object { Get-Content $_ -Raw }) -join "`n`n" |
            Set-Content -Path $generated -Encoding utf8NoBOM
        & "$HOME\.local\bin\claude.exe" --append-system-prompt-file $generated @args
    }
    else {
        & "$HOME\.local\bin\claude.exe" @args
    }
}
