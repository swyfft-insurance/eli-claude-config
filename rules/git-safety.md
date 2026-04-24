# Git Safety

> Gate 2 applies here — see `core-behavior.md`.

- After creating a branch: `git push -u origin <my-branch>` IMMEDIATELY. Never leave tracking on someone else's branch or `origin/development`.
  - **What happened:** Tracking left on Ken's branch → unreviewed code merged to development. Catastrophic.
- Before ANY push: `git branch -vv`. Tracking must be `origin/<my-branch>`. Anything else = DO NOT PUSH.
- `git fetch origin <branch>` before claiming what's on a remote branch. Never trust stale local state.
- Merge commits: ONLY conflict resolution. Never mix with fixes or PR feedback. Never `git add -A` after a merge.
- "Commit minus X" = don't stage X. NEVER `git checkout --` those files (that destroys changes).
- No `/logical-commits` unless user explicitly asks.
- `git stash` only captures UNCOMMITTED changes. The stash never contains prior commits. Before filtering or cherry-picking from a stash, run `git stash show --stat` and verify — don't assume it contains more than it does.
- Pre-push: `git branch -vv` → `git log <upstream>..HEAD` → push
- Pre-commit: `git branch` (not on development/master?) → `git diff --staged` → message starts with ticket ID
- Pre-PR: read every YouTrack ticket in branch name → `git diff development...HEAD` → read `.github/pull_request_template.md` → draft for approval
