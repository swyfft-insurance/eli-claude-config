---
name: eli--diff
description: Show git diffs safely, untracked files included. Required arg: "local" (uncommitted), "branch" (committed vs origin/development) or "all" (everything the branch carries vs origin/development).
---

# Git Diff

**You MUST use this skill for all git diffs. Raw `git diff` is blocked by the pretooluse hook.**

## Arguments

One required argument: `local`, `branch` or `all`. No default — you must choose.

- `/eli--diff local` — What have I changed but not yet committed? Includes untracked (new) files.
- `/eli--diff branch` — What has this branch committed, compared to `origin/development`?
- `/eli--diff all` — Everything this branch carries vs `origin/development`: committed, uncommitted and untracked. The one to use when the question is "what does this branch change", such as the code-complete audit or a PR description.

If no argument is provided, STOP and ask the user which one they want.

Optional flags after the mode:
- `-StatOnly` — show `--stat` summary only
- `-Path "path/to/file"` — scope to a specific file

## Run

```bash
pwsh -NoProfile -File "$HOME/.claude/scripts/Git-Diff.ps1" -Mode <local|branch|all> # via-diff-skill
```

With options:
```bash
pwsh -NoProfile -File "$HOME/.claude/scripts/Git-Diff.ps1" -Mode branch -StatOnly # via-diff-skill
pwsh -NoProfile -File "$HOME/.claude/scripts/Git-Diff.ps1" -Mode local -Path "Swyfft.Services.UnitTests/SomeFile.cs" # via-diff-skill
```

**IMPORTANT:** Append `# via-diff-skill` to bypass the pretooluse hook block.

## What each mode shows

| Mode | Compares | Includes uncommitted? | Includes committed? | Includes untracked? |
|------|----------|----------------------|-------------------|-------------------|
| `local` | Working tree vs HEAD | Yes | No | Yes |
| `branch` | HEAD vs `origin/development` | No | Yes | No |
| `all` | Working tree vs the branch's merge base with `origin/development` | Yes | Yes | Yes |

`branch` and `all` baseline on `origin/development`, never the local `development` ref, which is stale on a machine that lives on feature branches. Fetch first if the remote-tracking ref might be behind.

## Rules

- NEVER run raw `git diff` — the hook will block you.
- NEVER guess which mode to use. Think about what you actually need to see.
- The `branch` mode runs a preflight check for uncommitted changes and warns you if any exist.
