---
name: diff
description: Show git diffs safely. Prevents conflating uncommitted changes with committed branch diffs. Required arg: "local" (working tree) or "branch" (committed vs development).
---

# Git Diff

**You MUST use this skill for all git diffs. Raw `git diff` is blocked by the pretooluse hook.**

## Arguments

One required argument: `local` or `branch`. No default — you must choose.

- `/diff local` — What have I changed but not yet committed?
- `/diff branch` — What does this branch look like compared to development?

If no argument is provided, STOP and ask the user which one they want.

Optional flags after the mode:
- `-StatOnly` — show `--stat` summary only
- `-Path "path/to/file"` — scope to a specific file

## Run

```bash
pwsh -NoProfile -File "$HOME/.claude/scripts/Git-Diff.ps1" -Mode <local|branch> # via-diff-skill
```

With options:
```bash
pwsh -NoProfile -File "$HOME/.claude/scripts/Git-Diff.ps1" -Mode branch -StatOnly # via-diff-skill
pwsh -NoProfile -File "$HOME/.claude/scripts/Git-Diff.ps1" -Mode local -Path "Swyfft.Services.UnitTests/SomeFile.cs" # via-diff-skill
```

**IMPORTANT:** Append `# via-diff-skill` to bypass the pretooluse hook block.

## What each mode shows

| Mode | Compares | Includes uncommitted? | Includes committed? |
|------|----------|----------------------|-------------------|
| `local` | Working tree vs HEAD | Yes | No |
| `branch` | HEAD vs development | No | Yes |

## Rules

- NEVER run raw `git diff` — the hook will block you.
- NEVER guess which mode to use. Think about what you actually need to see.
- The `branch` mode runs a preflight check for uncommitted changes and warns you if any exist.
