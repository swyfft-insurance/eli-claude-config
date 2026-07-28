#!/usr/bin/env python3
"""SessionStart hook: inject the full ruleset into context.

Fires on every SessionStart source — startup, resume, clear, and compact —
so the rules are present in a fresh context and rebuilt immediately after a
compaction drops them.

Delivered via hookSpecificOutput.additionalContext, which lands in the
conversation context itself. This is NOT the PreToolUse systemMessage channel
removed in 5c86bd38e4de: that one attached a rules file to an already-allowed
tool call, where it changed nothing.
"""

import json
import sys
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
POINTER_FILE = CLAUDE_DIR / "CLAUDE.md"
RULES_DIR = CLAUDE_DIR / "rules"

# Read first so the authority preamble and the Gates lead the injection.
PRIORITY_ORDER = ["core-behavior.md", "talking-to-eli.md"]

HEADER = (
    "The complete ruleset below is injected at session start and after every "
    "compaction. These are standing orders, not reference material — follow "
    "them for the remainder of the session."
)


def read_text(path):
    """Return a file's text, or None if it is missing or unreadable."""
    try:
        return path.read_text(encoding="utf-8-sig")
    except (FileNotFoundError, OSError):
        return None


def rule_files():
    """Return every rules file, priority ones first, then the rest alphabetically."""
    if not RULES_DIR.is_dir():
        return []
    all_files = sorted(RULES_DIR.glob("*.md"), key=lambda p: p.name)
    by_name = {p.name: p for p in all_files}
    ordered = [by_name.pop(name) for name in PRIORITY_ORDER if name in by_name]
    ordered.extend(p for p in all_files if p.name in by_name)
    return ordered


def build_context():
    """Assemble the pointer file and every rules file into one context blob."""
    sections = []

    pointer = read_text(POINTER_FILE)
    if pointer:
        sections.append(f"=== ~/.claude/CLAUDE.md ===\n{pointer}")

    for path in rule_files():
        content = read_text(path)
        if content:
            sections.append(f"=== ~/.claude/rules/{path.name} ===\n{content}")

    if not sections:
        return None
    return HEADER + "\n\n" + "\n\n".join(sections)


def main():
    try:
        json.load(sys.stdin)  # utf8-ok: stdin JSON from Claude Code, never a file/BOM
    except Exception:
        pass

    context = build_context()
    if not context:
        sys.exit(0)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
