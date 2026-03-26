---
name: Never mix merge commits with other changes
description: Merge commits must ONLY contain merge resolution — never combine with unrelated fixes or PR feedback
type: feedback
---

Never combine merge conflict resolution with other changes (PR feedback, fixes, refactoring) in the same commit.

**Why:** Mixing merge resolution with unrelated changes makes the merge unreviewable and the history incomprehensible. If something goes wrong, you can't cleanly revert the merge without also losing the other changes.

**How to apply:**
1. Merge commit: ONLY conflict resolution, nothing else
2. Separate commit: PR feedback, fixes, or any other changes
3. Never `git add -A` after a merge — stage only the conflicted files
