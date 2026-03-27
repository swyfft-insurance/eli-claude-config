#!/usr/bin/env python3
"""PreToolUse hook: enforce deterministic rules from CLAUDE.md.

Receives JSON on stdin with tool_name and tool_input.
Exit 0 = allow, exit 2 + stderr = block.
"""

import json
import re
import sys

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name == "Bash":
        check_bash(tool_input.get("command", ""))
    elif tool_name == "Write":
        check_write(tool_input.get("file_path", ""))


def warn(msg):
    """Warn via stdout JSON systemMessage (non-blocking)."""
    print(json.dumps({"systemMessage": msg}))
    sys.exit(0)


def check_bash(cmd):
    if re.search(r"sed\s+-i", cmd):
        warn(
            "REMINDER: sed -i destroys CRLF line endings on Windows. "
            "Use the Edit tool instead."
        )

    if re.search(r"\|\s*tee\s", cmd):
        warn(
            "REMINDER: bash tee crashes on Windows. "
            "Use: pwsh -NoProfile -Command \"... 2>&1 | Tee-Object -FilePath 'C:\\...\\output.txt'\""
        )

    if re.search(r"git\s+checkout\s+--", cmd):
        warn(
            "REMINDER: git checkout -- destroys uncommitted changes. "
            "If this is a 'commit minus X' situation, use git reset HEAD <file> to unstage instead."
        )

    if re.search(r"\bprintenv\b", cmd):
        warn(
            "REMINDER: printenv silently truncates values containing '='. "
            "Use: powershell -NoProfile -Command \"[System.Environment]::GetEnvironmentVariable('VAR_NAME', 'User')\""
        )

    if re.search(r"--filter-class", cmd):
        warn(
            "REMINDER: --filter-class does not work with xUnit v3 MTP. "
            "Use: -- --filter-trait \"TestGroup=GroupName\""
        )

    if re.search(r"\bmv\s+", cmd):
        warn(
            "WARNING: mv silently fails on Windows. Use the safe pattern: "
            "cp source dest && ls dest && rm source"
        )

    if re.search(r"git\s+add\s+(-A|--all|\.)\b", cmd):
        warn(
            "WARNING: Never git add -A/--all/. after a merge. "
            "Stage files individually by name."
        )

    if re.search(r"\|\s*tail\s+-", cmd):
        warn(
            "WARNING: Piping to tail hides progress with run_in_background. "
            "Run the command directly, read the output file afterwards."
        )

    if re.search(r"pwsh.*(/tmp/|'/tmp/)", cmd):
        warn(
            "WARNING: pwsh does not translate Unix /tmp/ paths. "
            "Use: C:\\Users\\eli.koslofsky\\AppData\\Local\\Temp\\"
        )

    if re.search(r"git\s+push", cmd):
        warn(
            "WARNING: Before pushing, run git branch -vv first. "
            "Tracking must show origin/<your-branch>."
        )


def check_write(file_path):
    if re.search(r"\.cs$", file_path, re.IGNORECASE):
        warn(
            "WARNING: Write destroys CRLF line endings on .cs files. "
            "Use the Edit tool for existing files. "
            "If this is a NEW file, fix CRLF afterwards."
        )


if __name__ == "__main__":
    main()
