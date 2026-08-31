---
name: eli--review-prs-parallel
description: Review multiple GitHub PRs in parallel using one subagent per PR. Use when the user wants you to review a batch of PRs (e.g., "review all these", "review the open PRs", a pasted list of PR titles/numbers). Enforces the hard caps from `~/.claude/rules/pre-pr-review.md` (5 min, 15 files, 1-level trace, 600 words, stop-early) so subagents don't burn unbounded tokens.
---

# Parallel PR Review

Fan out one `general-purpose` subagent per PR. Each agent reads its ticket, the base-branch versions of touched files, existing reviews/bot comments, and the diff — then reports Critical/Major findings only. The orchestrator (main session) then presents the results **one PR per message** (step 4) and drafts that PR's recommendation. **The reviews run in parallel; the presentations never do.** No posting happens until Eli approves.

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

### 1b. Detect stacked PRs — check every PR's base ref

Several Swyfft devs stack PRs routinely, Justin especially. A stacked PR's `baseRefName` is another
open PR's `headRefName` rather than `development`, and missing that wrecks the review: the base-branch
`git show origin/development:...` reads compare against the wrong tree, and the diff gets read as
though the parent PR's changes belong to the child.

Pre-flight already captures `baseRefName`. For any PR whose base is not `development`, resolve it:

```bash
gh pr list --repo swyfft-insurance/swyfft_web --search "head:<baseRefName>" --json number,title,author,state
```

Then, for each stacked PR:

- **Fetch the base ref** and tell that PR's agent to read base versions from it, not from
  `origin/development`:
  `git -C <repo> fetch origin <baseRefName>:<localname> -f`
- **Tell the agent in its prompt** that the PR is stacked, name the parent PR number, and say that
  `gh pr diff` already shows only the incremental change against that base.
- **Order the presentation parent-first.** Findings in the parent are often the real subject, and
  approving a child before its parent tells Eli nothing about merge order.
- **Say so when presenting**, in one sentence: which PR it is stacked on, and that the parent must
  merge first. That is merge-order context, not a review finding, so never write it up as one.

A large addition count on a stacked PR usually means a generated file, not the parent's content.
Confirm which before describing the size:

```bash
gh pr view <NUM> --repo swyfft-insurance/swyfft_web --json files --jq '.files[] | "\(.additions)	\(.path)"' | sort -rn | head
```

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
   python ~/.claude/skills/eli--read-ticket/read-ticket.py {TICKET} pr-review-{TICKET}
   The second argument is required here. These are other people's tickets being reviewed, not Eli's own work, so their dumps go in `pr-review-` prefixed folders. Without it every reviewed ticket creates a folder that looks identical to Eli's ticket work under `~/.claude/tickets/`.
   It accepts the readable ID (SW-XXXXX) or the internal entity ID (2-XXXXX). Form a one-sentence understanding of each. Flag scope mismatch with the PR.

2. Fetch PR:
   gh pr view {NUM} --repo swyfft-insurance/swyfft_web --json files,additions,deletions,body,isDraft
   gh pr diff {NUM} --repo swyfft-insurance/swyfft_web

3. Fetch existing reviews/comments (don't duplicate already-flagged issues):
   gh pr view {NUM} --repo swyfft-insurance/swyfft_web --json reviews,comments
   gh api "repos/swyfft-insurance/swyfft_web/pulls/{NUM}/comments"

4. For touched files, read base-branch versions via `git show origin/development:...` and form a mental model of the change.

5. Assess only Critical (logic bugs, data loss, security) and Major (broken contracts, missed edges, regression risk) **in the CODE**. NO nits, NO style.

**Ask of every candidate finding: does the code fail to do what the author was trying to do?**

- **Yes** — report it. A logic error, an unhandled case that defeats the author's own stated goal, a contract the change breaks. Authors write broken code all the time and this is the entire job. That the line was written deliberately means nothing: they meant it to *work*.
- **No** — the code does what they meant, and you disagree with what they meant. That is not a finding. Kill it.

The second branch is where fake findings come from, because disagreeing with a choice produces prose that reads exactly like reporting a defect. Three shapes to recognize:

- **Second-guessing an authored choice.** A test asserting more than the ticket asked, a deletion that goes further than the ticket said, a design picked among alternatives. The code is the author's intent, so "did you mean this?" costs them a round trip and tells them you did not read their work.
- **"This could break later."** A passing test some future third-party change might turn red. Read "regression risk" above as regression *this change introduces now*, not risk that the world changes someday.
- **Anything the body, ticket, or a code comment already addresses.** Same failure wearing a different coat: treating a settled decision as an accident.

Findings that survive usually live outside the diff, or in the gap between the diff and a requirement nobody acknowledged deviating from. Those are what the author had no way to see.

**THE DIFF IS PRESUMED DELIBERATE.** Every line in it is a line the author chose to write, so "did you mean to do this?" is never a finding. It costs the author a round trip and tells them you did not read their work. Before any finding ships, name what the author could not have known: a caller they did not see, a file the PR does not touch, a stated requirement they never addressed. If the honest answer is "they wrote it and probably meant it", the finding is dead.

This kills three shapes that otherwise look like findings:
- **Second-guessing an authored choice.** A test asserting more than the ticket asked, a deletion that goes further than the ticket said, a design the author picked among alternatives. The author's intent is the code.
- **"This could break later."** A passing test that a future third-party change might turn red, a pattern that would not scale. Speculative future failure is not a defect. Read "regression risk" above as regression *this change introduces now*, not risk that something changes someday.
- **Anything the body, the ticket, or a code comment already addresses.** Covered by the body-read rule above, and it is the same failure: treating a decision as an accident.

The real ones live outside the diff, or in the gap between the diff and a requirement nobody acknowledged deviating from. Those are the ones the author had no way to see.

**READ THE PR BODY IN FULL. Then review the code against the TICKET, not against the body.** Those are two separate rules and collapsing them is the known failure mode. All three of the following apply:

1. **Reading the body is mandatory, every PR, before you draft anything.** The body is where the author records deliberate deviations from the ticket, decisions already argued out with someone else, and the reasoning behind whatever looks surprising in the diff. Skip it and you produce findings the author answered before you started.
2. **Check every finding against the body before you report it.** If the author discloses the thing, explains it, or states it was decided deliberately, the finding is DEAD. Drop it. A finding that re-asks a question the body already answers is worse than no finding at all.
3. **The body is never itself under review.** Do not flag body inaccuracies, "the body says X but the diff does Y", missing release-notes detail, or stale checkboxes. The author can write whatever they want in the body; we don't grade it. Default position: zero PR-body findings.

Your scope-match check compares the DIFF to the TICKET. When the diff deviates from the ticket and the body discloses that deviation with reasoning, that is not a finding: report it in one line as "deviation, disclosed in body" so the orchestrator knows it was already handled.

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

### 3b. A task notification is not a turn — emit NOTHING

A subagent-completion notification is not a message from Eli, so it never earns a reply. While a
PR presentation sits awaiting his decision, every notification that arrives produces **zero
user-facing output**. No acknowledgement, no queue count, no "holding this until you decide", no
"all six are in", not one word. Mark the task completed, keep the report for its turn in the walk,
and stop.

Reports arriving out of order changes nothing. Agents finish in whatever order they finish, and a
report that lands early simply waits. Even when every agent has reported and nothing is left to
run, the answer is still silence until Eli's next real message.

Each of those status lines scrolls the pending question off his screen, so he has to hunt back
through the transcript to find what he was being asked. That is the same harm the one-PR-at-a-time
rule in step 4 exists to prevent, arriving by a different door: step 4 stops several PRs sharing
one message, and this rule stops one PR's question being buried under narration of the others.

### 4. Present ONE PR AT A TIME — mandatory, never a batch

**Never present more than one PR per message.** Not a summary table of all of them, not a
grouped recommendation list, not "here are all three." One PR, one message, then stop and wait
for Eli's decision on that PR before mentioning the next one. This is not a preference to weigh
against concision — a batch presentation forces Eli to hold several unrelated code reviews in his
head at once and to answer several decisions in one reply, which is exactly what he does not want.

Order the PRs however the batch was given to you and walk them in that order.

Each PR's message contains, and contains only:

1. **A heading with the PR number, the author, and the title.** The author appears every time,
   in every message, in every restatement — no exceptions.
2. **Two or three sentences of context**: scope match against the ticket, and the existing review
   state (bot findings, prior approvals, unresolved threads).
3. **The findings for that PR that survived step 4b**, each drafted as the exact inline comment
   text you would post, with its `file:line` anchor verified against the PR head ref.
4. **Your recommendation** for that PR: plain approve, comment-only with inlines, or hold.
5. **One closing question** asking what to do with this PR.

Then stop. Do not preview the next PR, do not say how many remain, do not carry findings forward.

Never hand Eli a finding with a caveat that you did not verify part of it. Verifying it is step 4b's
job, and an unverified claim shipped behind a hedge is the thing this whole step exists to stop.

When every PR has been presented and decided, you may post a single short closing line listing
what was executed. That closing line is the only place more than one PR may appear together.

### 4b. Fact-check that PR's findings BEFORE presenting them — mandatory

A subagent's findings are unverified claims. They are produced under a 5-minute cap, a 15-file cap,
and a 1-level trace cap, so they routinely rest on a premise the agent never checked. Presenting
them raw wastes Eli's turn on claims that do not survive first contact with the code.

**Step one, before any of the rest: read that PR's body in full** (`gh pr view <NUM> --repo
swyfft-insurance/swyfft_web --json body --jq '.body'`). Read the whole thing, Reviewer Notes
included, and kill every finding the author already discloses, explains, or records as deliberate.
This runs first because it is the cheapest filter in the whole skill: one read against one document
that routinely answers the finding outright, and no amount of code verification afterwards
substitutes for it. A finding that survives code verification but re-asks a question the body
answered is still a wasted turn, and it reads to the author as a reviewer who did not read the PR.

**Then invoke `/eli--fact-check-writing` on that PR's drafted findings.** One invocation per PR, run
at the moment you are about to present that PR, never a single batched invocation covering all of
them. Pass it the drafted inline comment text and tell it to check every predicate against the code
at that PR's head ref. Note what that skill does and does not cover: it audits the prose and the
code predicates, so it will not catch a finding whose real defect is that the body already answered
it. The body read above is the only thing that catches that.

The audit's job here is to kill the finding, not to polish it. Expect that:

- A finding whose premise fails is **retracted**, not rewritten. A retracted finding can flip the
  recommendation from comment-only to plain approve, and that flip is the correct outcome, not a
  failure of the review.
- The most common failure is a finding that describes intended, tested behavior as a defect. Before
  claiming a code path violates an invariant, find the test that covers that path and read what it
  asserts. A test named for the exact behavior in question settles it.
- The second most common failure is a citation that does not say what the finding claims: a test
  whose setup uses a different code path, a doc comment about a neighboring operation, a line number
  off by one or two.

**Then check the fix you are proposing, separately from the problem you are reporting.** A finding
has two halves and they fail independently: the problem ("X is broken") is a claim with a source,
and the fix ("worth doing Y") is a proposal with none. Verifying the problem tells you nothing about
the fix, and a fix whose nouns all point at real things reads as verified when nobody checked it.
For every "should / worth / consider / the fix is", answer three questions before it ships: does the
proposed change actually produce the outcome you named, is that outcome already produced without it,
and if the proposal joins two changes with "and", does each half stand on its own?

An unsound fix is deleted, not softened into a question. Report the problem and let the author pick
the remedy. That is always available, it is shorter, and it is what the author would rather have.

Verify every line number against the PR head ref before drafting an anchor. Never carry a subagent's
line number through unchecked.

Present only what survives. If nothing survives for a PR, present that plainly and recommend approve.

### 5. Gate 2 — WAIT for explicit approval, per PR

Eli must reply with the action for the PR just presented (e.g., "post it", "skip the second
inline", "approve", "hold"). Acknowledgements, side-comments, or "thanks" are NOT approval. When
in doubt, ask.

**Waiting means emitting nothing.** The presented PR's question must be the last thing on his
screen when he answers it. Task notifications arriving during the wait get no output at all, per
step 3b. Execute that PR's approved action (step 6) before presenting the next PR, or batch
the executions at the end — either is fine, but the *presentations* are never batched.

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
- **One PR per message, always.** The parallelism belongs to the subagents, not to the presentation. A summary table covering several PRs, a grouped recommendation list, or any message naming more than one PR's findings violates step 4. This gets corrected every time it happens — do not reinvent the batch table because it looks tidier.
- **A subagent finding is a hypothesis, not a result.** Step 4b's fact-check is not optional and not a formality: findings from a capped 5-minute review fail verification often, most often by describing intended and already-tested behavior as a defect. Retract rather than rewrite, and never present a finding with a hedge about the part you did not check.
- **Check every PR's base ref for stacking (step 1b).** Several Swyfft devs stack PRs routinely, Justin especially. A base that is not `development` changes which tree the agent must read, changes the presentation order to parent-first, and is merge-order context Eli needs stated in a sentence. It is never a review finding.
- **Silence is the whole behavior while a presentation is pending.** A background-task
  notification is a system event, not a turn, and answering one costs Eli the question he was
  reading. Never narrate agent arrivals, queue depth, or that the fan-out has finished. Step 3b
  has the full rule.
- **Gate 1.5**: If a finding makes me question whether a PR should be approved at all, STOP and ask Eli. Don't pivot from "clean approve" to "comment-only" on my own.
- **Gate 2**: Every `pr-review.py` write (approve / comment / request-changes) waits for explicit approval. Acknowledgements aren't approval.
- **Don't fan out more than ~8 agents at once** — token cost on the user's session is real (`pre-pr-review.md`: "a runaway subagent burns tokens against their session budget").
- **Don't include banned phrases in agent prompts.** They license unbounded archaeology and burn time.
- **No mention of the deferred-tool ToolSearch step** unless the agent will actually need YouTrack MCP. If the PR has no ticket, skip the YouTrack step in the prompt entirely.
- **Read every PR body before drafting anything. Never write a finding about the body.** These are two rules, not one, and collapsing them into "ignore the body" costs a whole review cycle. Reading is mandatory: the body is where the author records deliberate deviations from the ticket and decisions already settled with someone else, so a review that skips it generates findings that were answered before the review started. **Before any finding reaches Eli, check it against the body. If the author discloses it, explains it, or marks it deliberate, the finding is dead: drop it.** Separately, and independently, the body is never itself the subject of a finding: drop "body says X but diff does Y", "PR description misrepresents the diff", and "missing disclosure" findings, and when a subagent flags a body issue, strip it without mentioning it, not even parenthetically. Two defaults, both absolute: zero PR-body findings ever reach Eli, and zero findings the body already answered.
  - **What happened:** #22458's Reviewer Notes disclosed the SW-48019 deviation, named the exact manual quote-creation flow at risk, and recorded that removing it was confirmed deliberate after an adversarial review raised that same risk. The subagent's report said the author disclosed it. That line was stripped as a "body finding", the body was never read, and both drafted inlines re-asked what the Reviewer Notes already answered.
- **ALWAYS name the author when presenting a PR.** Every time. The per-PR heading names the author. Follow-up restatements name the author. The closing execution summary names the author beside each PR number (e.g., "#20760 (justinswyfft)"). This is non-negotiable — Eli needs the human context every time. If you find yourself listing PR numbers without authors, stop and rewrite the list. Capture authors during pre-flight (already done) and use them in every subsequent reference.
