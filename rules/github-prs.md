# GitHub PRs

- PR description from TWO sources: YouTrack tickets (via get_issue) + actual diff (`git diff development...HEAD`). Never from memory or plan files.
- Treat as ONE combined diff, not commit-by-commit. Iterative commits are not logical units.
- No Review Guide unless commits were structured via `/logical-commits`.
- Never claim test status without running or checking — plan files go stale.
- Bot review comments (Copilot, Claude) get same seriousness as human comments.
- Before responding to any PR comment, research the claim in the codebase. Don't draft a reply until you've read the relevant code.
- Reply to threads → resolve every thread. Merge queue requires it.
- **Gate 2 applies to PR comments.** Draft reply text in your response and wait for explicit approval before posting. This includes thread replies, review comments, and PR body edits.
- Review style: only comment on fundamental bugs/red flags. No nits, no style comments.
- If YouTrack unavailable: STOP and ask about VPN. Don't guess ticket descriptions.
- GraphQL for resolving threads: query via `repository.pullRequest.reviewThreads`, NOT via `node(id:)` on PullRequestReviewComment (field doesn't exist).
- Never use `minimizeComment` — that hides, not resolves.
- **Inline comments only**: When a comment is about a specific file/line, post it as an inline review comment using `gh api` (not `gh pr review --comment`). Top-level review comments are for general feedback that doesn't target a specific location.
- **Multiline PR bodies**: The `block-prod-db.ps1` hook splits on newlines, so multiline `gh pr create --body "..."` or `gh pr edit --body "..."` triggers false positives. Use `--body-file` instead: write the body to a temp file, then pass it as a single-line command.
