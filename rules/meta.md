# Meta: Rules Architecture

This file describes how Eli's personal Claude rules are structured. Read this before modifying any rules file, CLAUDE.md, or memory.

## Architecture

- **`~/.claude/CLAUDE.md`** is a POINTER FILE (~80-90 lines). It contains the Three Gates inline and a reference table pointing to rules files. Do NOT add detailed rules directly to CLAUDE.md.
- **`~/.claude/rules/*.md`** contain the actual detailed rules, one topic per file.
- **`~/.claude/hooks/pretooluse.py`** injects the relevant rules file at the moment a matching command is detected. Rules are read from disk at runtime — never hardcoded in the hook.

## Where to put a new rule

1. **Behavioral correction for an existing category** → Edit the matching `~/.claude/rules/*.md` file.
2. **New category of rules** → Create a new `~/.claude/rules/<topic>.md` file, add a pointer row to the table in CLAUDE.md, and add trigger patterns to `pretooluse.py` if the rule maps to detectable tool calls.
3. **Change to the Gates themselves** → Edit CLAUDE.md directly (these stay inline).

## What NOT to do

- Do NOT write behavioral rules to memory (`~/.claude/projects/*/memory/`). Memory is for project-specific facts that can't be derived from code. Rules belong in `~/.claude/rules/`.
- Do NOT add detailed content to CLAUDE.md. It's a pointer file. If you're adding more than 2 lines, it belongs in a rules file.
- Do NOT create a rules file without adding a corresponding pointer row in CLAUDE.md.
- Do NOT hardcode rule text in `pretooluse.py`. The hook reads from the .md files.
- Do NOT duplicate rules across files. Each rule lives in exactly one place.

## Process for incorporating feedback

When the user corrects your behavior:
1. Read this file (meta.md) first.
2. Identify which existing rules file the correction belongs in.
3. If no existing file fits, propose a new rules file name and pointer.
4. Draft the change and show the user (Gate 2 — draft before posting).
5. After approval, make the edit to the rules file.
