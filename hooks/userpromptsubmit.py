#!/usr/bin/env python3
"""UserPromptSubmit hook: stop the session when the 5-hour usage window is spent.

A PreToolUse hook only ever sees a turn that calls a tool, so a conversation-only
session walks straight past it. This is the event that gates those turns.

Exit 0 = allow, exit 2 + stderr = block the prompt.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from rate_limit import block_message
except Exception:  # never block a prompt because this hook itself is broken
    sys.exit(0)


def main():
    blocked = block_message(
        "This prompt was not sent. Every turn re-reads the whole conversation, so talking "
        "costs usage too."
    )
    if blocked:
        print(blocked, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
