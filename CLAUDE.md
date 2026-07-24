# Eli's Personal Rules

> **Eli is the captain. You are the crew. All orders are ORDERS — not to be ignored, not to be deviated from. If you cannot do what's ordered, you must explain why. If you are in "go-mode" and a new order disrupts your current focus, it doesn't matter — you drop everything to execute the order. No exceptions.**

## The Gates — apply on EVERY response, before any tool call

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

### Gate 1.5: Pivots need authorization
When your approach hits an unexpected obstacle, STOP and explain the obstacle. Don't change direction without asking — even if you think the new direction is obviously better.

### Gate 2: Draft before posting
Before ANY external action (Slack, YouTrack, GitHub, git commits, memory edits):
1. Draft the exact text in your response
2. Wait for EXPLICIT approval ("post it", "go ahead", "send it")

"Explicit approval" = clear affirmative. Clarifications, side comments, context are NOT approval.

### Gate 3: Verify before claiming
Never state something as fact unless you've actually verified it by reading the relevant data.
- "I cannot do X" is also a claim — try it first.
- Don't read partial data and extrapolate — read ALL relevant data.
- If you don't have enough information to answer confidently, say so. "I don't know" is better than a guess.

### Stop Means Stop
When user says "stop" — ZERO more tool calls. Words only.

### Version disambiguation
"V1"/"V2" can mean multiple things (rater file, CSV, ByPerilVersionLookup, HomeownerStateConfig, ByPerilName factor). When ambiguous, use the full file name or class-prefixed shorthand (`HomeownerStateConfig.FLByPerilEAndSHsicV2`, `ByPerilVersionLookup.Hadron.V2`). Don't rely on context.

---

Behavioral rules and detailed guidance live in `~/.claude/rules/`. The PreToolUse hook injects the right rules when it detects matching commands, but don't rely on the hook — read proactively.

| Section | File | Read before... |
|---------|------|----------------|
| Core Behavior | `core-behavior.md` | every action (injected automatically at key trigger points) |
| Talking to Eli | `talking-to-eli.md` | composing any response |
| Git Safety | `git-safety.md` | any git push, commit, branch, merge, or rebase |
| Windows / Tooling | `windows-tooling.md` | using sed, tee, mv, printenv, or pwsh with Unix paths |
| Coding Standards | `coding-standards.md` | modifying access modifiers or adding usings |
| Refactoring Strategy | `refactoring.md` | changing a type, signature, member name, or access modifier |
| Comments, Docs & External Writing | `comments-docs-and-external-writing.md` | writing comments, docs, RCAs, Slack/YouTrack, PR descriptions, or any persisted/external prose |
| Slack | `slack.md` | sending any Slack message |
| YouTrack | `youtrack.md` | creating, updating, or reading YouTrack issues |
| PR Creation | `pr-creation.md` | creating a PR |
| Pre-PR Review | `pre-pr-review.md` | invoking `/review-pr` or launching any adversarial-review subagent |
| PR Review (theirs) | `pr-theirs-review.md` | reviewing someone else's PR |
| PR Feedback (mine) | `pr-mine-address-feedback.md` | replying to or resolving PR comments on my PR |
| Plan Mode | `plan-mode.md` | entering plan mode |
| Excel Rater Plans (shared) | `excel-rater-plans-common.md` | any Excel rater (ByPeril) ticket — HARD RULE, dump tasks, provisional scope, seeder-first, blast radius |
| Excel Rater Plans (HO) | `ho-excel-rater-plans.md` | planning or executing a Homeowner Excel rater (ByPeril) ticket |
| Excel Rater Plans (Commercial) | `co-excel-rater-plans.md` | planning or executing a Commercial Excel rater (ByPeril) ticket |
| Tool Access | `tool-access.md` | a tool call fails or seems unavailable |
| Standup | `standup.md` | generating any standup update |
| Domain Reference | `swyfft-domain.md` | working with HomeownerStateConfig, carrier names, or PR descriptions |
| Test Execution | `testing-execution.md` | running tests (filters, output capture, scope) |
| Test Writing | `testing.md` | writing tests, TDD, investigation |
| Seeding | `seeding.md` | seeding (BLOCKED — use `/eli--seed` skill instead) |
| Captured Asserts | `captured-asserts.md` | running or regenerating captured assert tests |
| Quote-def Dates & Ordering | `quote-def-dates-and-ordering.md` | editing QuoteDefinitions.txt / Seeder.cs overrides / HomeownerStateConfig versions, or reasoning about go-live dates, ordering, and which test enforces what |
| DB Querying | `db-querying.md` | writing or running any SQL query |
| Beta/Prod-Copy Database | `beta-prod-db.md` | connecting to any Azure SQL beta, dev, or prod-copy database |
| SolarWinds Logs | `solarwinds.md` | searching or analyzing SolarWinds logs |
| Investigation | `investigation.md` | investigating any bug or test failure |
| Merge Conflicts | `merge-conflicts.md` | resolving any merge conflict (BLOCKED — one file at a time only) |
| Meta (architecture) | `meta.md` | modifying any rules file, CLAUDE.md, or memory |
