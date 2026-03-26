---
name: Safe file moves — copy then delete
description: Never use mv for file moves — use cp first, verify destination, then rm source. Lost an untracked analysis file by mv-ing it to a path that silently failed.
type: feedback
---

Never use `mv` to move files. Use `cp` first, then `ls` the destination to verify the copy landed, then `rm` the source. A silent `mv` failure destroyed an untracked file (`version-history-config-mapping.md`) that had no backup in git — hours of analysis work lost.

**Why:** `mv` in bash on Windows can silently fail (report success but not actually move the file). The file disappears from the source but never arrives at the destination. There is no recovery.

**How to apply:** Any time the user asks to move a file:
1. `cp source destination`
2. `ls destination` — confirm it exists
3. Only then `rm source`
