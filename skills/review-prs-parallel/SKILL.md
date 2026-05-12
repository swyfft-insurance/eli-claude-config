---
name: review-prs-parallel
description: Review multiple GitHub PRs in parallel using one subagent per PR. Use when the user wants you to review a batch of PRs (e.g., "review all these", "review the open PRs", a pasted list of PR titles/numbers). Enforces the hard caps from `~/.claude/rules/pre-pr-review.md` (5 min, 15 files, 1-level trace, 600 words, stop-early) so subagents don't burn unbounded tokens.
---

# Parallel PR Review

Fan out one `general-purpose` subagent per PR. Each agent reads its ticket, the base-branch versions of touched files, existing reviews/bot comments, and the diff — then reports Critical/Major findings only. The orchestrator (main session) synthesizes a table and drafts per-PR recommendations. **No posting happens until Eli approves.**

Authoritative rules — read these first if you haven't already:

- `~/.claude/rules/pr-theirs-review.md` — process, comment types, Review actions table.
- `~/.claude/rules/pre-pr-review.md` — hard caps and banned phrases for subagent prompts.

## Arguments

The user provides PR numbers (e.g., `/review-prs-parallel 20570 20572 20576`) OR pastes a list of PR titles/numbers from the GitHub UI. If unclear, parse the user message for `#NNNNN` patterns. If none found, ask which PRs.

If the user says "review all the open ones that need review", resolve via:

```bash
gh pr list --repo swyfft-insurance/swyfft_web --search "is:open review:required draft:false" --json number,title,author,isDraft
```

Default repo is `swyfft-insurance/swyfft_web` unless the user names another.

## Steps

### 1. Pre-flight

```bash
# Confirm the local clone is fresh so subagents see current `origin/development`
git -C /c/Users/eli.koslofsky/Documents/GitHub/swyfft_web fetch origin development
```

For each PR, capture (in the main session, cheap):
- Title, author, base ref, isDraft, current approval state
- Ticket IDs parsed from the title (`SW-XXXXX` regex) or "no ticket" if the title has none

This avoids burning an agent turn on metadata.

### 2. Fan out

Send a single message with one `Agent` (`general-purpose`) tool call per PR, in parallel. Use this prompt template — fill in `{NUM}`, `{TITLE}`, `{AUTHOR}`, `{TICKETS}`, and any `{DRAFT_NOTE}` / `{APPROVED_NOTE}` flags:

```
Review PR #{NUM} on swyfft-insurance/swyfft_web for fundamental bugs and red flags only.

PR URL: https://github.com/swyfft-insurance/swyfft_web/pull/{NUM}
Title: {TITLE}
Author: {AUTHOR}
Ticket(s): {TICKETS or "No ticket — cleanup work"}
{DRAFT_NOTE: "This PR is in DRAFT — call out anything intentionally unfinished rather than buggy."}
{APPROVED_NOTE: "Already approved by another reviewer; Eli wants my independent review."}

HARD CAPS:
- 5-minute time budget. Stop and report what you have if approaching limit.
- Read at most 15 files.
- Trace callers/callees at most 1 level deep.
- Output under 600 words.
- Stop early if you find a Critical issue.

REPO (already fetched): /c/Users/eli.koslofsky/Documents/GitHub/swyfft_web
Read base-branch versions with: `git -C /c/Users/eli.koslofsky/Documents/GitHub/swyfft_web show origin/development:path/to/file`
NEVER `git checkout`.

PROCESS:
1. Read the ticket(s). YouTrack MCP tools are DEFERRED — load via ToolSearch with query "select:mcp__YouTrackNative__get_issue,mcp__YouTrackNative__get_issue_comments" then call mcp__YouTrackNative__get_issue for each ticket ID. On failure, fall back to curl:
   YOUTRACK_TOKEN=$(powershell -NoProfile -Command "[System.Environment]::GetEnvironmentVariable('YOUTRACK_API_TOKEN', 'User')")
   curl -s -H "Authorization: Bearer $YOUTRACK_TOKEN" "https://swyfft.myjetbrains.com/youtrack/api/issues/{TICKET}?fields=idReadable,summary,description,customFields(name,value(name))"
   Form a one-sentence understanding of each. Flag scope mismatch with the PR.

2. Fetch PR:
   gh pr view {NUM} --repo swyfft-insurance/swyfft_web --json files,additions,deletions,body,isDraft
   gh pr diff {NUM} --repo swyfft-insurance/swyfft_web

3. Fetch existing reviews/comments (don't duplicate already-flagged issues):
   gh pr view {NUM} --repo swyfft-insurance/swyfft_web --json reviews,comments
   gh api "repos/swyfft-insurance/swyfft_web/pulls/{NUM}/comments"

4. For touched files, read base-branch versions via `git show origin/development:...` and form a mental model of the change.

5. Assess only Critical (logic bugs, data loss, security) and Major (broken contracts, missed edges, regression risk). NO nits, NO style.

OUTPUT FORMAT (<600 words):
PR #{NUM} — {one-line summary}
Ticket understanding: {one sentence per ticket}
Scope match: {yes / explain mismatch}
Existing review state: {one sentence — bot findings, unresolved threads, prior approvals}
Findings:
- [Critical] {desc with file:line}
- [Major] {desc with file:line}
(or "No critical/major findings — recommend approve")

DO NOT POST ANYTHING (no gh pr review, no gh pr comment, no gh api ...replies). Return findings only.
```

**Banned phrases in the prompt** (per `pre-pr-review.md`): "be thorough", "trace 2-3 levels", "look hard", "read enough surrounding context", "question your assumptions". Don't add them.

### 3. Track and abandon runaways

Create a `TaskCreate` entry per PR review and one for "Synthesize findings" blocked by all of them. Mark each `in_progress` when the agent launches and `completed` on the task-completion notification.

If any agent exceeds **1.5× the 5-minute budget** (i.e., >7.5 min wall-clock), abandon it via `TaskStop` immediately. No rationalizing, no "still plausible". Drop that PR from the batch and tell Eli so he can re-launch with a tighter scope.

### 4. Synthesize and draft

When all agents complete, summarize in a single table (one row per PR):

| PR | Title | Ticket(s) | Pre-existing state | Findings | My rec |
|----|-------|-----------|--------------------|----------|--------|

Then group recommendations:

- **Clean — Approve (plain)**: list PRs with "No critical/major findings". `gh pr review --approve` only — no body text.
- **Has findings — Comment + inline**: list PRs with [Major]+ findings. Draft each inline comment as `file:line — finding text` so Eli can pick which to post.
- **Hold**: drafts, already-changes-requested PRs, or anything where the right move is "wait" rather than "act".

### 5. Gate 2 — WAIT for explicit approval

The user must reply with the actions to execute (e.g., "approve the clean four", "post the 3 inline on #20570, no approval", "hold #20426"). Acknowledgements, side-comments, or "thanks" are NOT approval. When in doubt, ask.

### 6. Execute approved actions

**Plain approve (no body):**

```bash
gh pr review {NUM} --approve --repo swyfft-insurance/swyfft_web
```

**Comment-only review (no approval) with inline findings:**

Get the head commit SHA, then post a review with `comments[]`:

```bash
HEAD_SHA=$(gh pr view {NUM} --repo swyfft-insurance/swyfft_web --json headRefOid -q .headRefOid)

gh api repos/swyfft-insurance/swyfft_web/pulls/{NUM}/reviews \
  -X POST \
  -F commit_id="$HEAD_SHA" \
  -F event="COMMENT" \
  -f "comments[][path]=path/to/file.cs" \
  -F "comments[][line]=42" \
  -f "comments[][side]=RIGHT" \
  -f "comments[][body]=Finding text…" \
  -f "comments[][path]=path/to/other.cs" \
  -F "comments[][line]=100" \
  -f "comments[][side]=RIGHT" \
  -f "comments[][body]=Second finding…"
```

Notes:
- `event="COMMENT"` for has-findings-but-not-blocking. `event="REQUEST_CHANGES"` if Eli explicitly says so.
- `event="APPROVE"` with `comments[]` for approve-with-inline (rare — usually approve plain instead).
- For multiline-string bodies, prefer writing the body to a temp file and `-F "comments[][body]=@/tmp/body.txt"` — the `block-prod-db.ps1` hook splits on newlines and false-positives on inline multiline `-f` args.

Confirm each post with `gh pr view {NUM} --json reviews -q '.reviews[-3:]'` and check the latest entry shows `eli-swyfft`.

### 7. Cleanup

Mark all PR-review tasks `completed`. Don't leave the task list with `in_progress` entries.

## Important

- **Gate 1.5**: If a finding makes me question whether a PR should be approved at all, STOP and ask Eli. Don't pivot from "clean approve" to "comment-only" on my own.
- **Gate 2**: Every `gh pr review`, every `gh api ...reviews` POST waits for explicit approval. Acknowledgements aren't approval.
- **Don't fan out more than ~8 agents at once** — token cost on the user's session is real (`pre-pr-review.md`: "a runaway subagent burns tokens against their session budget").
- **Don't include banned phrases in agent prompts.** They license unbounded archaeology and burn time.
- **No mention of the deferred-tool ToolSearch step** unless the agent will actually need YouTrack MCP. If the PR has no ticket, skip the YouTrack step in the prompt entirely.
