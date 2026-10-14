# Merge Conflict Resolution

Never bulk-resolve conflicts: no `git checkout --ours` or `--theirs` across files, no batch operations.

## Process

One file at a time:

1. Read its conflict markers.
2. Work out what each side changed and why they conflict.
3. Write the correct combined result, which is often both changes.
4. Confirm no conflict markers remain.
5. `git add` only that file, then move to the next.

## Building during a merge

Building mid-merge is safe. `~/.claude/scripts/Build-Solution.ps1` still compiles, and its line-length gate skips itself while `MERGE_HEAD` exists.
