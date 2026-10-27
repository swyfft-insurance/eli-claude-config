# YouTrack

## Batching YouTrack actions under one approval

Multi-action closeouts (comment, link, Stage, Release Stage) go through one batch approval. A lone action keeps the per-action flow.

1. Write a batch JSON, `{"actions": [...]}`. Action types, shapes and allowed values are defined in `~/.claude/hooks/youtrack_batch.py` (`ACTION_TYPES`). One batch can act on several issues.
2. Stage it: `& "$HOME/.claude/scripts/YouTrack-Batch.ps1" -Stage -File <batch.json>`. Staging is read-only and needs no approval. It prints a canonical block and a hash.
3. Paste the canonical block verbatim and ask for approval.
4. On a bare approval, run `& "$HOME/.claude/scripts/YouTrack-Batch.ps1" -Execute -Hash <hash>`.

A stage is single-use and records per-action results even on partial failure. To retry, restage only what failed and get a fresh approval.

## A ticket is its description, comments, and attachments, together

Comments and attachments routinely extend, narrow or override the description, and the later comment wins a disagreement. Read comments oldest to newest, and read each image where its marker sits in the text. Before acting on scope, state which requirements came from a comment or an attachment.

## The AC is whatever the ticket requires, wherever it says it

Most tickets have no "Acceptance Criteria" section. Extract the requirement however it is stated (a quoted email, a current-vs-wanted table, a Current/Expected Result pair, a comment) and present it as the AC. Never remark that the ticket lacks an AC section or that the AC is implied.

## Technical notes in a ticket are not the AC

A ticket's mechanism, technical-notes or code-pointer section is a lead to verify. For business-logic work it never adds or replaces a criterion, and a note that fails verification is a finding to raise. The exception is a ticket whose subject is the technical change itself (refactor, rename, migration).

## Reading tickets

- Read the ticket before exploring code, always through `/eli--read-ticket`, the only ticket-read path (`get_issue`, `get_issue_comments` and raw REST reads are blocked). It returns the description, comments, custom fields, attachments, `watchers`, each comment's `mentionedUsers`, and `fieldHistory` (Stage transitions, reassignments, priority changes).
- `search_issues` returns internal IDs (`2-XXXXX`). Pass them straight to `/eli--read-ticket`.
- Read every custom field (Carrier, USState, ProductLine, RatingType). They scope the work.
- A mention does not add a watcher. Check `watchers`.
- Convert API URLs (`.youtrack.cloud:443`) to `swyfft.myjetbrains.com/youtrack/` for user-facing links.

## Writing tickets

- User stories and behavioral features say what and why only: requirement, business reason, AC. No code, file paths, class names, mechanisms or named refactors.
- Bugs carry code pointers: file paths, methods, line numbers, SolarWinds queries.
- Technical refactor and implementation tickets carry code references.
- Use `create_issue`, never `create_draft_issue`.
- Attach every dump, log, output and screenshot a ticket relies on when filing it. Never point at a file on a dev machine. If something can't be attached yet, the ticket isn't ready to file.
- Never put an `@mention` in a heading. Put it on its own line below.
- A ticket never carries an open question. Resolve every question before drafting, from the source material, the code, a skill built for it (`/go-live-dates` turns an effective date into go-live dates), or Eli. A question only the business owner can answer goes to Eli first, and the draft waits for the answer.

## Tag Eli's tech debt tickets `technical debt`

A ticket Eli files for his own refactor, test-infrastructure or tooling work gets the `technical debt` tag at creation, listed in the create draft with the custom fields. His work views split on it (`tag: {technical debt}` and `tag: -{technical debt}`). A ticket filed for the business, such as one with a Business Owner, never gets it.

## Fields and stages

- The type field is `IssueType`. Values: Feature, Bug, Support, Epic, Inquiry. There is no "Task".
- After creating a PR, move its tickets to Review in the same turn without asking, unless they are already at Review or later.
- To close a ticket as not applicable or won't fix, set Stage to Done, then Release Stage to NA. Moving to Done auto-sets Release Stage to Production. The MCP `update_issue` rejects NA, so use the command API:
  ```
  YOUTRACK_TOKEN=$(powershell -NoProfile -Command "[System.Environment]::GetEnvironmentVariable('YOUTRACK_API_TOKEN', 'User')")
  curl -s -X POST -H "Authorization: Bearer $YOUTRACK_TOKEN" -H "Content-Type: application/json" \
    -d '{"query":"Release Stage NA","issues":[{"idReadable":"SW-XXXXX"}]}' \
    "https://swyfft.myjetbrains.com/youtrack/api/commands"
  ```
  HTTP 200 with an empty `{}` is success. The ticket then reads `Release Stage: None`, which is NA. A failure would read `Production`.
- Closing a ticket without doing its work (not applicable, won't fix, covered elsewhere) always comes with a comment saying why, linking the ticket or PR that covers it. The comment goes in the same batch as the Stage and Release Stage changes.

## Release Stage at PR creation

When putting up a PR, check Release Stage on each of its tickets.

- Release Stage should always be NA at PR creation.
- A second PR on a ticket also gets NA. Release Stage reflects the ticket's final PR reaching whatever stage.
- When a ticket's Release Stage isn't NA, call it out to Eli with the ticket and its current value. There may be exceptions, so set it to NA only after his y, using the command API call in § "Fields and stages".

## SolarWinds queries in tickets

Run a ticket's SolarWinds query verbatim: URL-decode it and run every term and scope exactly, including the full `program:(...)` list and the severity. Never paraphrase, narrow or substitute terms. Zero results from a modified query prove nothing. Propose a different query only after running the verbatim one, labeled as not the ticket's query.
