---
name: eli--review-prs-parallel
description: Review multiple GitHub PRs in parallel using one subagent per PR. Use when the user wants you to review a batch of PRs (e.g., "review all these", "review the open PRs", a pasted list of PR titles/numbers). Enforces the hard caps from `~/.claude/rules/pre-pr-review.md` (5 min, 15 files, 1-level trace, 600 words, stop-early) so subagents don't burn unbounded tokens.
---

# Parallel PR Review

Fan out one `general-purpose` subagent per PR. Each agent reads its ticket, the base-branch versions of touched files, existing reviews/bot comments, and the diff — then reports Critical/Major findings only. The orchestrator (main session) synthesizes a table and drafts per-PR recommendations. **No posting happens until Eli approves.**

Authoritative rules — read these first if you haven't already:

- `~/.claude/rules/pr-theirs-review.md` — process, comment types, Review actions table.
- `~/.claude/rules/pre-pr-review.md` — hard caps and banned phrases for subagent prompts.

## Arguments

The user provides PR numbers (e.g., `/eli--review-prs-parallel 20570 20572 20576`) OR pastes a list of PR titles/numbers from the GitHub UI. If unclear, parse the user message for `#NNNNN` patterns. If none found, ask which PRs.

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
- Title, author, base ref, isDraft
- Ticket IDs parsed from the title (`SW-XXXXX` regex) or "no ticket" if the title has none

This avoids burning an agent turn on metadata.

**Do not capture or report `reviewDecision` / current approval state to Eli in pre-flight.** Approval status is irrelevant to whether or how rigorously to review — see the "Important" section below.

### 2. Fan out

Send a single message with one `Agent` (`general-purpose`) tool call per PR, in parallel. Use this prompt template — fill in `{NUM}`, `{TITLE}`, `{AUTHOR}`, `{TICKETS}`, and any `{DRAFT_NOTE}` flag:

```
Review PR #{NUM} on swyfft-insurance/swyfft_web for fundamental bugs and red flags only.

PR URL: https://github.com/swyfft-insurance/swyfft_web/pull/{NUM}
Title: {TITLE}
Author: {AUTHOR}
Ticket(s): {TICKETS or "No ticket — cleanup work"}
{DRAFT_NOTE: "This PR is in DRAFT — call out anything intentionally unfinished rather than buggy."}

Apply full review rigor regardless of any existing approvals or change-requests on the PR — Eli asked for your independent assessment.

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
1. Read the ticket(s) with the read-ticket script — full ticket (description, all comments, custom fields, attachments). The MCP get tools are blocked by the pretooluse hook; use the script:
   python ~/.claude/skills/eli--read-ticket/read-ticket.py {TICKET}
   It accepts the readable ID (SW-XXXXX) or the internal entity ID (2-XXXXX). Form a one-sentence understanding of each. Flag scope mismatch with the PR.

2. Fetch PR:
   gh pr view {NUM} --repo swyfft-insurance/swyfft_web --json files,additions,deletions,body,isDraft
   gh pr diff {NUM} --repo swyfft-insurance/swyfft_web

3. Fetch existing reviews/comments (don't duplicate already-flagged issues):
   gh pr view {NUM} --repo swyfft-insurance/swyfft_web --json reviews,comments
   gh api "repos/swyfft-insurance/swyfft_web/pulls/{NUM}/comments"

4. For touched files, read base-branch versions via `git show origin/development:...` and form a mental model of the change.

5. Assess only Critical (logic bugs, data loss, security) and Major (broken contracts, missed edges, regression risk) **in the CODE**. NO nits, NO style.

**REVIEW THE CODE AGAINST THE TICKET, NOT THE PR DESCRIPTION.** The ticket is the source of truth for what should be built; the code is what got built. Your scope-match check compares those two. The PR description is NOT under review — its only legitimate use is as a hint about where to look in the code (e.g., "the body says they changed X service" → go read that service). Do not compare the diff to the PR body. Do not flag body inaccuracies, "the body says X but the diff does Y", missing release-notes detail, or stale checkboxes. The author can write whatever they want in the body; we don't grade it. The only conceivable exception is a body that would actively mislead a reviewer into approving something dangerous (e.g., "no behavioral change" hiding a risk-rule deletion) — and even then, the underlying CODE finding is what matters, not the body discrepancy. Default position: zero PR-body findings.

OUTPUT FORMAT (<600 words):
PR #{NUM} — {one-line summary}
Ticket understanding: {one sentence per ticket}
Scope match: {yes / explain mismatch — compare the DIFF to the TICKET, not to the PR body}
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

When all agents complete, summarize in a single table (one row per PR). **EVERY row MUST include the author** — this is mandatory, no exceptions, in every presentation to Eli (summary tables, recommendation groupings, follow-up updates, restatements, anywhere a PR is named):

| PR | Author | Title | Ticket(s) | Pre-existing state | Findings | My rec |
|----|--------|-------|-----------|--------------------|----------|--------|

Then group recommendations:

- **Clean — Approve (plain)**: list PRs with "No critical/major findings". `pr-review.py approve {NUM}` only — no body text.
- **Has findings — Comment + inline**: list PRs with [Major]+ findings. Draft each inline comment as `file:line — finding text` so Eli can pick which to post.
- **Hold**: drafts, already-changes-requested PRs, or anything where the right move is "wait" rather than "act".

### 5. Gate 2 — WAIT for explicit approval

The user must reply with the actions to execute (e.g., "approve the clean four", "post the 3 inline on #20570, no approval", "hold #20426"). Acknowledgements, side-comments, or "thanks" are NOT approval. When in doubt, ask.

### 6. Execute approved actions

All posting goes through `~/.claude/scripts/pr-review.py` — raw `gh pr review` / `gh pr
comment` / `gh api ... POST .../reviews` are blocked by the pretooluse hook. The script
sends bodies verbatim via `gh api --input` (no `-f`/`-F` footgun, no hook newline-splitting)
and reads each one back to confirm it landed before reporting success.

**Plain approve (no body):**

```bash
python ~/.claude/scripts/pr-review.py approve {NUM}
```

**Comment-only review (no approval) with inline findings:**

Write the inline findings to a JSON array file, then post. Each element needs `path`,
`line`, `body` (`side` defaults to `RIGHT`). Bodies live in the JSON as plain strings —
write multi-line/Unicode text directly, no escaping gymnastics.

```bash
cat > /tmp/inline.json <<'JSON'
[
  {"path": "path/to/file.cs", "line": 42, "body": "Finding text…"},
  {"path": "path/to/other.cs", "line": 100, "body": "Second finding…"}
]
JSON

python ~/.claude/scripts/pr-review.py comment {NUM} --inline /tmp/inline.json
```

**Request changes** (only if Eli explicitly says so) — body required, inline optional:

```bash
python ~/.claude/scripts/pr-review.py request-changes {NUM} --body-file /tmp/body.txt --inline /tmp/inline.json
```

Notes:
- `--repo` defaults to `swyfft-insurance/swyfft_web`; pass `--repo OWNER/REPO` for others.
- The script aborts non-zero if a posted body doesn't read back verbatim — so a non-zero
  exit means nothing reliable landed; investigate, don't assume success.

### 7. Cleanup

Mark all PR-review tasks `completed`. Don't leave the task list with `in_progress` entries.

## Important

- **Approval status is irrelevant to the review.** If Eli asked you to review a PR, review it with full rigor regardless of whether it's already approved, has changes requested, or is in draft. Never flag "this is already approved" or "this already has changes requested" back to Eli in pre-flight as if it might change his mind — he picked these PRs knowing the state, and others can miss things he wouldn't. Approval status only matters at the action stage (which verb to use when posting), not at the review stage. Don't pass it into the agent prompt either — the agent reads existing reviews via `gh pr view --json reviews` to avoid duplicating findings, and that's sufficient.
- **Gate 1.5**: If a finding makes me question whether a PR should be approved at all, STOP and ask Eli. Don't pivot from "clean approve" to "comment-only" on my own.
- **Gate 2**: Every `pr-review.py` write (approve / comment / request-changes) waits for explicit approval. Acknowledgements aren't approval.
- **Don't fan out more than ~8 agents at once** — token cost on the user's session is real (`pre-pr-review.md`: "a runaway subagent burns tokens against their session budget").
- **Don't include banned phrases in agent prompts.** They license unbounded archaeology and burn time.
- **No mention of the deferred-tool ToolSearch step** unless the agent will actually need YouTrack MCP. If the PR has no ticket, skip the YouTrack step in the prompt entirely.
- **We do not review PR descriptions.** Code is reviewed against the TICKET (the source of truth for what should be built), never against the PR body. The body is a navigation hint — useful for figuring out where in the code to look — and nothing more. Drop every "body says X but diff does Y" finding by default. Drop "PR description misrepresents the diff" findings. Drop "missing disclosure" findings. The only exception is an active-misleading body that would cause a reviewer to approve something dangerous — and even then, the finding to surface is the underlying CODE issue, not the body discrepancy. If a subagent flags a body issue, strip it from the synthesis silently. Do not surface it as an "FYI", do not list it in a "notes" section, do not mention it parenthetically. Default: zero PR-body findings ever reach Eli.
- **ALWAYS name the author when presenting a PR.** Every time. Summary tables get an Author column. Recommendation groupings include the author next to each PR number (e.g., "#20760 (justinswyfft)"). Follow-up restatements include the author. Single-PR mentions include the author. This is non-negotiable — Eli needs the human context every time. If you find yourself listing PR numbers without authors, stop and rewrite the list. Capture authors during pre-flight (already done) and use them in every subsequent reference.
