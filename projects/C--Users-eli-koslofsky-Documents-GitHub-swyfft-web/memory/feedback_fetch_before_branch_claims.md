---
name: fetch_before_branch_claims
description: Always git fetch before making claims about what's on remote branches — stale local branches lead to wrong conclusions
type: feedback
---

Always `git fetch origin <branch>` before claiming something does or doesn't exist on a remote branch.

**Why:** Used a stale local `master` to conclude NpoiWorksheetAdapter wasn't on prod, then built an entire wrong theory ("beta-only issue") and wasted the user's time with unnecessary environment-confusion questions. A single `git fetch` would have shown it was on `origin/master` all along.

**How to apply:** Before any claim like "X is/isn't on master/beta/prod", run `git fetch origin <branch>` first. Never trust local branch state for deployment questions. This is a specific case of Rule 1 (VERIFY before claiming).
