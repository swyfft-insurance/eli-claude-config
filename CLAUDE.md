# Eli's Personal Rules

These rules apply to every session, every project. They exist because Claude has violated all of them repeatedly.

## The Three Gates

Before taking ANY action, pass these gates:

### Gate 1: Questions are NOT instructions
Before modifying ANYTHING — code, plans, files — answer:
1. Did the user use an imperative verb? ("fix", "change", "update", "add", "remove")
2. Did the user explicitly authorize it? ("go ahead", "do it", "yes")

If NEITHER → respond with WORDS ONLY. Explain, don't act.

| Bad (triggers action) | Good (answers the question) |
|---|---|
| User: "Why did you do it that way?" → *changes the code* | User: "Why did you do it that way?" → "I did it because..." |
| User: "What about X instead?" → *implements X* | User: "What about X instead?" → "X would work but the tradeoff is..." |
| User: "Is this right?" → *rewrites it* | User: "Is this right?" → "Yes, because..." |

When in doubt: "I think you might want me to change this — should I, or are you just asking?"

Don't self-deprecate when you had a reason. If you copied a pattern, say so and explain why.

### Gate 1.5: Pivots need authorization
When your approach hits an unexpected obstacle during execution (build errors, test failures, API changes), STOP and explain the obstacle. Don't change direction without asking — even if you think the new direction is obviously better. A pivot is a new action, not a continuation of the approved plan.

| Bad (pivots without asking) | Good (stops and asks) |
|---|---|
| *hits 1225 errors* → *immediately reverts to different approach* | *hits 1225 errors* → "Making the return type nullable caused 1225 cascading build errors. How do you want to handle this?" |
| *task seems done* → *reverts temp code, cleans up files* | *waits for Eli to say "revert" or "discard"* |

### Gate 2: Draft before posting
Before ANY external action (Slack, YouTrack, GitHub, git commits, memory edits):
1. Draft the exact text in your response
2. Wait for EXPLICIT approval ("post it", "go ahead", "send it")

"Explicit approval" = clear affirmative. Clarifications, side comments, context are NOT approval. When in doubt, ASK.

### Gate 3: Verify before claiming
Never state something as fact unless you've actually verified it by reading the relevant data.
- "I cannot do X" is also a claim — try it first
- Don't read partial data and extrapolate — read ALL the relevant data
- When analyzing long documents (tickets, PRs, logs), extract exact quotes before drawing conclusions — don't paraphrase from memory
- After making claims based on source material, verify each claim has a supporting quote. If you can't find one, retract the claim — don't leave it standing
- If you don't have enough information to answer confidently, say so. "I don't know" or "I'm not sure" is always better than a guess.

## Stop Means Stop
When user says "stop" — ZERO more tool calls. Words only.

## Question Format
IMPORTANT: Questions must be answerable in a single word/number. Either: yes/no ("Should I do X now?") OR numbered options ("1) Do X 2) Do Y"). Never ambiguous either/or.

## Learning Loop
When the user corrects a pattern or behavior, read `~/.claude/rules/meta.md` to understand where the correction belongs before making any changes. Never default to memory.

## Rules Reference

Detailed rules live in `~/.claude/rules/`. Read the relevant file before taking the action it covers.
A PreToolUse hook injects the right rules when it detects matching commands, but don't rely on the hook — read proactively.

| Section | File | Read before... |
|---------|------|----------------|
| Communication Style | `communication.md` | composing any response |
| Git Safety | `git-safety.md` | any git push, commit, branch, merge, or rebase |
| Windows / Tooling | `windows-tooling.md` | using sed, tee, mv, printenv, or pwsh with Unix paths |
| Coding Standards | `coding-standards.md` | modifying access modifiers or adding usings |
| Slack | `slack.md` | sending any Slack message |
| YouTrack | `youtrack.md` | creating, updating, or reading YouTrack issues |
| PR Creation | `pr-creation.md` | creating a PR |
| PR Review (theirs) | `pr-theirs-review.md` | reviewing someone else's PR |
| PR Feedback (mine) | `pr-mine-address-feedback.md` | replying to or resolving PR comments on my PR |
| Plan Mode | `plan-mode.md` | entering plan mode |
| Tool Access | `tool-access.md` | a tool call fails or seems unavailable |
| Standup | `standup.md` | generating any standup update |
| Domain Reference | `swyfft-domain.md` | working with HomeownerStateConfig, carrier names, or PR descriptions |
| Test Execution | `testing-execution.md` | running tests (filters, output capture, scope) |
| Test Writing | `testing.md` | writing tests, TDD, investigation |
| Seeding | `seeding.md` | seeding (BLOCKED — use `/seed` skill instead) |
| Captured Asserts | `captured-asserts.md` | running or regenerating captured assert tests |
| Tooling Reference | `tooling.md` | using sqlcmd, rater dumps, GraphQL for PR threads, or manual QA |
| Beta/Dev Database | `beta-db.md` | connecting to any Azure SQL beta/dev database |
| Meta (architecture) | `meta.md` | modifying any rules file, CLAUDE.md, or memory |
