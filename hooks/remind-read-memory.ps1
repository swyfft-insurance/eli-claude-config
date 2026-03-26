$context = @"
STOP — Before making ANY changes, read your memory files:
- tooling-gotchas.md (Write tool destroys CRLF — use Edit for existing files)
- core-rules.md (verify before claiming, ask before acting, questions are not instructions)
You have forgotten these rules repeatedly. READ THEM NOW.
"@

$result = @{
    hookSpecificOutput = @{
        hookEventName = "PostToolUse"
        additionalContext = $context
    }
} | ConvertTo-Json -Depth 3

Write-Output $result
