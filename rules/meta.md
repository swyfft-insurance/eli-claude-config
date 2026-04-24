# Meta: Rules Architecture

This file describes how Eli's personal Claude rules are structured. Read this before modifying any rules file, CLAUDE.md, or memory.

## Architecture

- **`~/.claude/CLAUDE.md`** is a POINTER FILE. It contains the captain/crew authority preamble and a reference table pointing to rules files. Do NOT add detailed rules directly to CLAUDE.md.
- **`~/.claude/rules/*.md`** contain the actual detailed rules, one topic per file.
- **`~/.claude/hooks/pretooluse.py`** injects the relevant rules file at the moment a matching command is detected. Rules are read from disk at runtime — never hardcoded in the hook.

## Loading Priority Order

CLAUDE.md files load in this order — **later = higher priority** (transformer recency bias):

1. Managed (`/etc/claude-code/CLAUDE.md`) — lowest priority
2. User (`~/.claude/CLAUDE.md` + `~/.claude/rules/*.md`)
3. Project (`.claude/CLAUDE.md`, `.claude/rules/*.md` — walks from root to CWD)
4. Local (`CLAUDE.local.md` in each directory) — **highest priority**

Personal behavioral rules live at the user level. Project coding standards live at the project level. If they conflict, project wins (higher priority).

## Where to put a new rule

1. **Behavioral correction for an existing category** → Edit the matching `~/.claude/rules/*.md` file.
2. **New category of rules** → Create a new `~/.claude/rules/<topic>.md` file, add a pointer row to the table in CLAUDE.md, and add trigger patterns to `pretooluse.py` if the rule maps to detectable tool calls.
3. **Change to the Gates** → Edit `~/.claude/rules/core-behavior.md`.

## What NOT to do

- Do NOT write behavioral rules to memory (`~/.claude/projects/*/memory/`). Memory is for project-specific facts that can't be derived from code. Rules belong in `~/.claude/rules/`.
- Do NOT add detailed content to CLAUDE.md. It's a pointer file. If you're adding more than 2 lines, it belongs in a rules file.
- Do NOT create a rules file without adding a corresponding pointer row in CLAUDE.md.
- Do NOT hardcode rule text in `pretooluse.py`. The hook reads from the .md files.
- Do NOT duplicate rules across files. Each rule lives in exactly one place.

## Memory vs Rules

Memory (`~/.claude/projects/*/memory/`) is for **project-specific facts** that can't be derived from code. Behavioral rules belong in `~/.claude/rules/`.

Memory system constraints:
- Relevance scanner only sees **filename + frontmatter description + type** — not file content. Vague descriptions like "project notes" will never get recalled. Be keyword-rich and specific.
- 4,096 byte cap per memory file when surfaced per turn
- Max 5 memory files injected per turn, 60KB session budget
- `autoDream` consolidates automatically after 24h / 5 sessions

## HTML Comments in Rules Files

HTML comments (`<!-- -->`) are stripped before injection — zero token cost. Use them for maintenance notes:

```markdown
<!-- Added 2026-03-31 after SW-49029 — Eli correction on PR comment research -->
- Before responding to any PR comment, research the claim in the codebase.
```

## Process for incorporating feedback

When the user corrects your behavior:
1. Read this file (meta.md) first.
2. Identify which existing rules file the correction belongs in.
3. If no existing file fits, propose a new rules file name and pointer.
4. Draft the change and show the user (Gate 2 — draft before posting).
5. After approval, make the edit to the rules file.
