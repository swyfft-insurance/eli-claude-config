# Merge Conflict Resolution

**NEVER bulk-resolve conflicts.** No `git checkout --ours` or `git checkout --theirs` across multiple files. No batch operations. Each conflict is unique and requires understanding both sides.

## Process

For each conflicted file, one at a time:
1. **Read the file** — look at the actual conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
2. **Understand both sides** — what did upstream change? What did our branch change? Why do they conflict?
3. **Determine the correct resolution** — often both changes are needed, not one OR the other
4. **Apply the resolution** — edit the file to include the correct combined result
5. **Verify** — confirm no conflict markers remain in the file
6. **Stage the file** — `git add` only that one file
7. **Move to the next file**

## Common mistakes
- Taking `--ours` or `--theirs` for all files — destroys one side's changes entirely
- Assuming conflicts are the same across files — each file may conflict for different reasons
- Rushing through conflicts to "get it done" — this is delicate work, slow down
- Not reading the conflict markers — you MUST understand what both sides changed before resolving
