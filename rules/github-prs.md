# GitHub PRs

- PR description from TWO sources: YouTrack tickets (via get_issue) + actual diff (`git diff development...HEAD`). Never from memory or plan files.
- Treat as ONE combined diff, not commit-by-commit. Iterative commits are not logical units.
- No Review Guide unless commits were structured via `/logical-commits`.
- Never claim test status without running or checking — plan files go stale.
- Bot review comments (Copilot, Claude) get same seriousness as human comments.
- Before responding to any PR comment, research the claim in the codebase. Don't draft a reply until you've read the relevant code.
- Reply to threads → resolve every thread. Merge queue requires it.
- Review style: only comment on fundamental bugs/red flags. No nits, no style comments.
- If YouTrack unavailable: STOP and ask about VPN. Don't guess ticket descriptions.
- GraphQL for resolving threads: query via `repository.pullRequest.reviewThreads`, NOT via `node(id:)` on PullRequestReviewComment (field doesn't exist).
- Never use `minimizeComment` — that hides, not resolves.
