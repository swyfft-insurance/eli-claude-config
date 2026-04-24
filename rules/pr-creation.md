# PR Creation

> Gate 2 applies here — see `core-behavior.md`.

- **Read the ticket first**: Before creating a PR, invoke `/read-ticket` to read the YouTrack ticket(s) in the branch name.
- PR description from TWO sources: the ticket (already read above) + actual diff (`git diff development...HEAD`). Never from memory or plan files.
- Treat as ONE combined diff, not commit-by-commit. Iterative commits are not logical units.
- No Review Guide unless commits were structured via `/logical-commits`.
- Never claim test status without running or checking — plan files go stale.
- If YouTrack unavailable: STOP and ask about VPN. Don't guess ticket descriptions.
- **Multiline PR bodies**: The `block-prod-db.ps1` hook splits on newlines, so multiline `gh pr create --body "..."` or `gh pr edit --body "..."` triggers false positives. Use `--body-file` instead: write the body to a temp file, then pass it as a single-line command.
