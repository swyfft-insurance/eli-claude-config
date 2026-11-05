---
audited-by: []
---

# Updating Tickets

## Batching YouTrack actions under one approval

Multi-action closeouts (comment, link, Stage, Deployed To) go through one batch approval. A lone action keeps the per-action flow.

1. Write a batch JSON, `{"actions": [...]}`. Action types, shapes and allowed values are defined in `~/.claude/hooks/youtrack_batch.py` (`ACTION_TYPES`). One batch can act on several issues.
2. Stage it: `& "$HOME/.claude/scripts/YouTrack-Batch.ps1" -Stage -File <batch.json>`. Staging is read-only and needs no approval. It prints a canonical block and a hash.
3. Paste the canonical block verbatim and ask for approval.
4. On a bare approval, run `& "$HOME/.claude/scripts/YouTrack-Batch.ps1" -Execute -Hash <hash>`.

A stage is single-use and records per-action results even on partial failure. To retry, restage only what failed and get a fresh approval.

## Fields and stages

- The type field is `IssueType`. Values: Feature, Bug, Support, Epic, Inquiry. There is no "Task".
- After creating a PR, move its tickets to Review in the same turn without asking, unless they are already at Review or later.
- To close a ticket as not applicable or won't fix, set Stage to Done, then Deployed To to NA. Moving to Done auto-sets Deployed To to Production. The MCP `update_issue` rejects NA, so use the command API:
  ```
  YOUTRACK_TOKEN=$(powershell -NoProfile -Command "[System.Environment]::GetEnvironmentVariable('YOUTRACK_API_TOKEN', 'User')")
  curl -s -X POST -H "Authorization: Bearer $YOUTRACK_TOKEN" -H "Content-Type: application/json" \
    -d '{"query":"Deployed To NA","issues":[{"idReadable":"SW-XXXXX"}]}' \
    "https://swyfft.myjetbrains.com/youtrack/api/commands"
  ```
  HTTP 200 with an empty `{}` is success. The ticket then reads `Deployed To: None`, which is NA. A failure would read `Production`. On `None`, don't re-run the command or report a failure.
- Closing a ticket without doing its work (not applicable, won't fix, covered elsewhere) always comes with a comment saying why, linking the ticket or PR that covers it. The comment goes in the same batch as the Stage and Deployed To changes.

## Deployed To at PR creation

When putting up a PR, check Deployed To on each of its tickets.

- Deployed To should always be NA at PR creation.
- A second PR on a ticket also gets NA. Deployed To reflects the ticket's final PR reaching whatever stage.
- When a ticket's Deployed To isn't NA, call it out to Eli with the ticket and its current value. There may be exceptions, so set it to NA only after his y, using the command API call in § "Fields and stages".
