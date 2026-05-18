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
- **Version ambiguity in replies**: when a "V1"/"V2" reference could mean either a state config or a lookup, qualify with the class-prefixed shorthand. See `swyfft-domain.md` § "Generator and Lookup vs Config Versions".
- **Gate 2 applies to PR comments.** Draft reply text in your response and wait for explicit approval before posting. This includes thread replies, review comments, and PR body edits.
- GraphQL for resolving threads: query via `repository.pullRequest.reviewThreads`, NOT via `node(id:)` on PullRequestReviewComment (field doesn't exist).
- Never use `minimizeComment` — that hides, not resolves.

## Order of operations: push before replying

NEVER post a PR comment reply before the code it describes is on the remote. A reply
that says "Fixed X" or "Dropped Y" must be backed by a commit already pushed to the PR
branch — otherwise the reviewer reads the claim, pulls the diff, and sees nothing.

Required order:
1. Make code changes
2. Build + run affected tests
3. Commit (one commit or several — doesn't matter, just must exist locally)
4. **Push to the PR branch**
5. Verify push succeeded (`git push` exit code 0, NOT rejected by branch protection)
6. THEN run `pr-feedback reply ...` for each thread
7. THEN resolve each thread

If the PR is locked (merge queue, etc.) and the push is rejected, STOP. Do not post
replies until the branch can accept the push — replies posted against unpushed code
will mislead the reviewer.

## GraphQL Commands

```
# Get thread IDs:
gh api graphql -f query='query { repository(owner:"swyfft-insurance",name:"swyfft_web") { pullRequest(number:PR) { reviewThreads(first:20) { nodes { id isResolved comments(first:1) { nodes { databaseId } } } } } } }'
# Resolve each:
gh api graphql -f query='mutation { resolveReviewThread(input:{threadId:"THREAD_ID"}) { thread { isResolved } } }'
```
