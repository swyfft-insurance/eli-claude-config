---
name: Exclude from commit means don't stage, not revert
description: When asked to commit "minus" or "excluding" certain files, only skip staging them — never git checkout/revert them
type: feedback
---

When the user says to commit changes "minus" or "excluding" certain files, that means: don't `git add` those files. Do NOT `git checkout --` them. That discards the changes entirely, which is destructive and not what was asked.

**Why:** Lost valid ExpectedResults file changes by reverting instead of just not staging. Those changes needed to be regenerated.

**How to apply:** To exclude files from a commit, simply don't add them to the staging area. They stay as unstaged changes in the working directory.
