# Reviewing Other People's PRs

- Review style: only comment on fundamental bugs/red flags. No nits, no style comments.
- Bot review comments (Copilot, Claude) get same seriousness as human comments.
- **Inline comments only**: When a comment is about a specific file/line, post it as an inline review comment using `gh api` (not `gh pr review --comment`). Top-level review comments are for general feedback that doesn't target a specific location.
