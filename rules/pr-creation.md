# PR Creation

> Gate 2 applies here — see `core-behavior.md`.

- **Read the ticket first**: Before creating a PR, invoke `/eli--read-ticket` to read the YouTrack ticket(s) in the branch name.
- PR description from TWO sources: the ticket (already read above) + actual diff (`git diff development...HEAD`). Never from memory or plan files.
- **"Actual diff" means the full content diff, read at draft time.** A `--stat`/`-StatOnly` file list is NOT the diff — it names files without showing a single change. Earlier-in-session content reads are not the diff either: investigation reads are scoped to what that investigation needed, and every file not re-read ends up described from memory or the plan — exactly what this rule exists to prevent. Pull `/eli--diff branch` fresh and read every file's hunks before drafting; only binaries and generated files (`*Designer.cs`, `*_Generated.cs`, LFS pointers) may be skipped.
- Treat as ONE combined diff, not commit-by-commit. Iterative commits are not logical units.
- No Review Guide unless commits were structured via `/logical-commits`.
- Never claim test status without running or checking — plan files go stale.
- If YouTrack unavailable: STOP and ask about VPN. Don't guess ticket descriptions.
- **Multiline PR bodies**: The `block-prod-db.ps1` hook splits on newlines, so multiline `gh pr create --body "..."` or `gh pr edit --body "..."` triggers false positives. Use `--body-file` instead: write the body to the ticket's artifacts (`~/.claude/tickets/<TicketFolder>/artifacts/pr/`), then pass that file as a single-line command. Never a scratchpad/temp file — the PR body is ticket work product and stays with the ticket.
- **Always hyperlink ticket refs; always cite the PR for prior code; prefer PRs over commits.** In every PR description: (a) every YouTrack ticket ID mentioned in the body must be a markdown link to the YouTrack issue (e.g., `[SW-49577](https://swyfft.myjetbrains.com/youtrack/issue/SW-49577)`); (b) every reference to *prior code* — an earlier fix, a previous commit's behavior, the code being reverted, etc. — must cite the GitHub PR number that introduced it via bare auto-link (e.g., `#19959`); (c) **prefer PR references over commit SHAs**. Only reference a specific commit when the PR alone isn't enough (e.g., one commit out of a multi-commit PR), and in that case cite BOTH — the commit SHA as a bare auto-link (`235a80eda15`, which GitHub auto-links) AND the PR number it came from (`#19959`).
- **Version ambiguity**: PR descriptions referencing "V1"/"V2" must qualify the numbering scheme (state config vs lookup vs generator). See `swyfft-domain.md` § "Generator and Lookup vs Config Versions".
