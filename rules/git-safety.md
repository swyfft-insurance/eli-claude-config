# Git Safety

- After creating a branch, `git push -u origin <my-branch>` immediately. Never leave tracking on someone else's branch or `origin/development`.
- Before any push: `git branch -vv` (tracking must be `origin/<my-branch>`, or don't push), then `git log <upstream>..HEAD`, then push.
- Every `git fetch` passes `--no-write-fetch-head` (enforced by `pretooluse.py`, no bypass). Fetch before claiming what's on a remote branch.
- Merge commits: ONLY conflict resolution. Never mix in fixes or PR feedback, and never `git add -A` after a merge.
- "Commit minus X" means don't stage X. Never `git checkout --` those files.
- No `/logical-commits` unless asked.
- Before any `gh stack` command, read the stacked-PR docs linked in `pr-creation.md`.
- `git stash` holds only uncommitted changes. Run `git stash show --stat` before filtering or cherry-picking from one.
- Before any commit: `git branch` (never `development` or `master`), and the message starts with the ticket ID.
