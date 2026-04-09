# Addressing Feedback on My PRs

- Bot review comments (Copilot, Claude) get same seriousness as human comments.
- **PR comment replies are real work.** Research thoroughly, write clearly, don't rush to push them out. A sloppy reply to a reviewer is worse than a slow one.
- Before responding to any PR comment, research the claim in the codebase. Don't draft a reply until you've read the relevant code.
- **Quote-then-reply format**: Always quote the reviewer's text with `>` blockquotes, then reply below each quote. For top-level comments with multiple points, quote each point and reply individually. For inline comments, quote the specific portion you're addressing. Never use `#1`, `#2` etc. as labels — GitHub renders those as issue/PR links.

  Example:
  ```markdown
  > **FL Benchmark Admitted** — not in the 21 updated rater files AND not in the 14 leaf classes with skip overrides. Please confirm this was intentionally excluded.

  Intentional. The rater already has 0% rows in its Coverage B/C/D V1 lookup tables. Test passes all 12 indices.

  > **MS and NY E&S** — same situation. Please confirm these have no V1 configs.

  Both confirmed safe:
  - MS: V1 HomeownerStateConfig starts with V2 for Coverage B/C/D. No V1 gap.
  - NY QBE: Coverage B/D start at V2. Coverage C starts at V1, but the rater handles it.
  ```
- Reply to threads → resolve every thread. Merge queue requires it.
- **Gate 2 applies to PR comments.** Draft reply text in your response and wait for explicit approval before posting. This includes thread replies, review comments, and PR body edits.
- GraphQL for resolving threads: query via `repository.pullRequest.reviewThreads`, NOT via `node(id:)` on PullRequestReviewComment (field doesn't exist).
- Never use `minimizeComment` — that hides, not resolves.
