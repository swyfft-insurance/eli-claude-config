# Reviewing Other People's PRs

- **Read the ticket first**: Before reviewing, invoke `/read-ticket` to read the YouTrack ticket linked in the PR.
- Review style: only comment on fundamental bugs/red flags. No nits, no style comments.
- **Read existing comments/reviews** before starting your review.
- **Inline comments only**: When a comment is about a specific file/line, post it as an inline review comment using `gh api` (not `gh pr review --comment`). Top-level review comments are for general feedback that doesn't target a specific location.
