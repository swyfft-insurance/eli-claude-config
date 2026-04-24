# Reviewing Other People's PRs

## Before reading the diff

1. **Deeply understand the ticket**: Invoke `/read-ticket` to read the YouTrack ticket linked in the PR. If it's an epic or parent ticket, read the child/linked tickets to find the one this PR actually implements. You MUST be able to explain the ticket's purpose in your own words before touching the diff. If the PR doesn't obviously match the ticket's scope, investigate why — don't hand-wave it.
2. **Understand the existing code**: Use `git show development:path/to/file` to read the base branch version of files the PR touches — NEVER checkout another branch. Read callers and usages too. Understand the behavior and constraints as if you were going to implement the ticket yourself. Form your own mental model of the problem.
3. **Read existing comments/reviews**: Fetch all review comments and bot reviews on the PR. Note which points are valid, which are already addressed, and which you want to verify yourself.

## Reviewing the diff

- Only comment on fundamental bugs or red flags. No nits, no style comments.
- **Inline comments only**: When a comment is about a specific file/line, post it as an inline review comment using `gh api` (not `gh pr review --comment`). Top-level review comments are for general feedback that doesn't target a specific location.

## Posting the review

- **Gate 2 applies.** NEVER approve, request changes, or post comments without drafting your review and getting explicit approval first. Present your findings and recommendation, then wait.
- **Approvals don't need body text.** Once findings are presented and the user says to approve, just run `gh pr review --approve`. Don't draft "approval text" — the findings themselves are the review.

## Review actions (least to most severe)

| Action | Meaning | Merge impact |
|---|---|---|
| **Approve** (no body) | Clean, nothing to say | Counts toward required approvals |
| **Approve** + top-level comment | Approved, with an optional observation | Approved; comment is FYI only |
| **Approve** + inline comment | Approved overall, but this specific thing needs to be addressed | Approved, BUT inline thread blocks merge until resolved |
| **Comment only** | Not ready to approve — has concerns that need discussion | No approval counted, no hard block |
| **Request Changes** | Same spirit as Comment, but stronger — this PR is dangerous to merge as-is | Hard block — author must address and re-request review |

## Comment types

| Type | Blocking? | Use for |
|---|---|---|
| **Top-level** (body text) | No | Optional suggestions, general observations, FYI |
| **Inline** (on specific lines) | Yes — thread must be resolved before merge | Questions, issues, or suggestions that the author must address (not necessarily fix — they may resolve by explaining why no change is needed) |
