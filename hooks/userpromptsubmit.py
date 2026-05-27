#!/usr/bin/env python3
"""UserPromptSubmit hook: inject Gate 1/2/3 check before the assistant drafts a response.

Fires once per user message, before the assistant sees it in its full context.
This is the right phase to catch Gate 1 violations (acting on a question instead
of answering with words) — the PreToolUse hook fires too late, after the
assistant has already decided to call a tool.

Rules content is read from ~/.claude/rules/core-behavior.md so the canonical
source of truth stays in one place. Edit core-behavior.md to change the gates;
this hook picks up the change automatically.
"""

import json
import os
import sys

RULES_FILE = os.path.expanduser("~/.claude/rules/core-behavior.md")

PREAMBLE = (
    "=== GATE CHECK — re-read NOW before drafting your response.\n"
    "Source of truth: ~/.claude/rules/core-behavior.md\n"
    "===\n\n"
)


def main():
    try:
        json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    try:
        with open(RULES_FILE, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        sys.exit(0)

    print(json.dumps({"systemMessage": PREAMBLE + content}))
    sys.exit(0)


if __name__ == "__main__":
    main()
