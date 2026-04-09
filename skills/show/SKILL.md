---
name: show
description: Display a file's full contents. Use when the user asks to see a file, read rules, or view any text content. Prevents the "summarize instead of show" anti-pattern.
---

# Show File Contents

The user wants to SEE a file's contents printed in full. Do NOT summarize, excerpt, or describe — print the ENTIRE file in a fenced code block.

## Arguments

The user provides a filename or path (e.g., `/show github-prs.md`, `/show ~/.claude/CLAUDE.md`).

## Steps

### 1. Resolve the path

Try these in order until one matches:

1. **Absolute path**: If the argument starts with `/`, `C:\`, or `~` — use it directly (expand `~` to the home directory)
2. **Rules file**: If it ends in `.md`, check `~/.claude/rules/{argument}` — if it exists, use that
3. **Claude config file**: Check `~/.claude/{argument}` — if it exists, use that
4. **Project file**: Check the current working directory for `{argument}`
5. **Not found**: Tell the user the file wasn't found and list what you checked

### 2. Read the file

Use the Read tool to read the resolved path.

### 3. Print the FULL contents

Print the entire file contents inside a fenced code block with appropriate language syntax highlighting (e.g., ```markdown, ```python, ```csharp).

**Rules:**
- Print EVERYTHING — no truncation, no summarizing, no "here are the key parts"
- Use the correct language tag for syntax highlighting
- Do not add commentary before or after unless the user asked a question about the content
