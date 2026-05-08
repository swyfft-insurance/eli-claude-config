---
name: show
description: Display data in full — files, PR diffs, query results, logs, or any data the user can't see directly. Use when the user asks to see/read/view content. Prevents the "I have the info, here it is" anti-pattern where the agent reads data without printing it.
---

# Show

You read data. The user can't see it. Print it.

This skill exists because you have an insanely annoying habit of READING data and saying "here it is" / "I have the info" — when the user can't see anything until YOU print it in this conversation.

## What to show

The argument names the data the user wants to see.

**If you already have it in context from an earlier tool call, just print what you have. Do NOT re-fetch — that wastes tokens. The user wants to see what YOU see.**

If you don't have it yet, fetch once:

| Argument | How to fetch (only if not in context) |
|---|---|
| Path-like (`/`, `C:\`, `~`, has extension) | Read the file |
| `.md` filename only | Try `~/.claude/rules/{arg}`, `~/.claude/{arg}`, then CWD |
| "the code" / "the diff" | `gh pr diff <num>` for the PR under discussion |
| "the query results" / "the data" | Run the SQL query |
| "the logs" / "the log entries" | Run the log search |
| Unclear | Ask which data |

## Print rules

- Fenced code block with the right language tag (```diff, ```csharp, ```sql, ```markdown, etc.)
- **EVERYTHING.** No truncation, no excerpts, no "here are the key parts."
- **NO commentary before or after.** No "there it is". No recap. No summary. No findings. Just the code block.
