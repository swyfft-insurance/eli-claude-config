# Reading Tickets

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

## SolarWinds queries in tickets

Run a ticket's SolarWinds query verbatim: URL-decode it and run every term and scope exactly, including the full `program:(...)` list and the severity. Never paraphrase, narrow or substitute terms. Zero results from a modified query prove nothing. Propose a different query only after running the verbatim one, labeled as not the ticket's query.
