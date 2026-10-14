# Reviewing Other People's PRs

## Before reading the diff

1. Read the PR's ticket with `/eli--read-ticket`. For an epic or parent, find the child this PR implements. Be able to state the ticket's purpose before touching the diff, and investigate any mismatch between the PR and the ticket's scope.
2. Read the base version of every touched file with `git show development:path/to/file` (never check out another branch), plus callers and usages, until you understand the problem well enough to implement it yourself.
3. Read every existing review comment and bot review, noting which points are valid, already addressed, or worth verifying.

## Reviewing the diff

- Comment only on fundamental bugs or red flags. No nits, no style.
- A finding about a specific file/line is an inline comment (`pr-review.py comment --inline`). Top-level comments are for feedback with no location.
- A subagent doing any part of the review gets the hard caps in `pre-pr-review.md`.

## Presenting PRs to Eli

Name the author every time a PR is mentioned: tables (an Author column), groupings ("#20760 (justinswyfft)"), prose, follow-up restatements, standups.

## Posting the review

- All posting goes through `~/.claude/scripts/pr-review.py` (`approve [--inline <json>]` / `comment --inline <json>` / `request-changes --body-file <f>`). Raw `gh pr review`, `gh pr comment` and `gh api ... POST .../reviews|/comments` are blocked; reads are not. A non-zero exit means nothing reliable posted.
- Approvals carry no body text. Once Eli says approve, run `pr-review.py approve <PR#>`.

## Review actions (least to most severe)

| Action | Meaning | Merge impact |
|---|---|---|
| **Approve** (no body) | Clean, nothing to say | Counts toward required approvals |
| **Approve** + top-level comment | Approved, with an optional observation | Approved; comment is FYI only |
| **Approve** + inline comment | Approved overall, but this specific thing needs to be addressed | Approved, but the inline thread blocks merge until resolved |
| **Comment only** | Not ready to approve; has concerns that need discussion | No approval counted, no hard block |
| **Request Changes** | Like Comment, but this PR is dangerous to merge as-is | Hard block: author must address and re-request review |

## Comment types

| Type | Blocking? | Use for |
|---|---|---|
| **Top-level** (body text) | No | Optional suggestions, general observations, FYI |
| **Inline** (on specific lines) | Yes, the thread must be resolved before merge | Questions, issues or suggestions the author must address, by fixing or by explaining why no change is needed |
