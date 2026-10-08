#!/usr/bin/env python3
"""UserPromptSubmit hook: stop the session when the 5-hour usage window is spent.

A PreToolUse hook only ever sees a turn that calls a tool, so a conversation-only
session walks straight past it. This is the event that gates those turns.

Exit 0 = allow, exit 2 + stderr = block the prompt.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from rate_limit import block_message
except Exception:  # never block a prompt because this hook itself is broken
    sys.exit(0)

GATE_1_PATTERN = r"^## Gate 1:.*?(?=^## )"


def gate_1_reminder_or_default(prompt):
    if "?" not in prompt:
        return None
    rules_path = os.path.expanduser("~/.claude/rules/core-behavior.md")
    with open(rules_path, encoding="utf-8-sig") as rules_file:
        match = re.search(GATE_1_PATTERN, rules_file.read(), re.S | re.M)
    return match.group(0) if match else None


def main():
    blocked = block_message(
        "This prompt was not sent. Every turn re-reads the whole conversation, so talking "
        "costs usage too."
    )
    if blocked:
        print(blocked, file=sys.stderr)
        sys.exit(2)

    try:
        reminder = gate_1_reminder_or_default(json.load(sys.stdin).get("prompt", ""))
        if reminder:
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": "Eli's message contains a question. Gate 1 applies:\n\n" + reminder,
                }
            }))
    except Exception:
        pass  # never block a prompt because this hook itself is broken

    sys.exit(0)


if __name__ == "__main__":
    main()
