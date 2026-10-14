# Eli's Personal Rules

> **Eli is the captain. You are the crew. All orders are ORDERS — not to be ignored, not to be deviated from. If you cannot do what's ordered, you must explain why. If you are in "go-mode" and a new order disrupts your current focus, it doesn't matter — you drop everything to execute the order. No exceptions.**

## The Gates

The Gates, Stop Means Stop and Version Disambiguation are in `core-behavior.md`. They apply on every response, before any tool call.

---

Behavioral rules and detailed guidance live in `~/.claude/rules/`. Re-read the relevant file before acting.

| Section | File | Read before... |
|---------|------|----------------|
| Core Behavior | `core-behavior.md` | every action |
| Talking to Eli | `talking-to-eli.md` | composing any response |
| Git Safety | `git-safety.md` | any git push, commit, branch, merge, or rebase |
| Windows / Tooling | `windows-tooling.md` | using sed, tee, mv, printenv, or pwsh with Unix paths |
| Coding Standards | `coding-standards.md` | writing or modifying any C# |
| Refactoring Strategy | `refactoring.md` | changing a type, signature, member name, or access modifier |
| Comments, Docs & External Writing | `comments-docs-and-external-writing.md` | writing comments, docs, RCAs, Slack/YouTrack, PR descriptions, or any persisted/external prose |
| Slack | `slack.md` | sending any Slack message |
| YouTrack | `youtrack.md` | creating, updating, or reading YouTrack issues |
| PR Creation | `pr-creation.md` | creating a PR |
| Pre-PR Review | `pre-pr-review.md` | invoking `/review-pr` or launching any adversarial-review subagent |
| PR Review (theirs) | `pr-theirs-review.md` | reviewing someone else's PR |
| PR Feedback (mine) | `pr-mine-address-feedback.md` | replying to or resolving PR comments on my PR |
| Plan Mode | `plan-mode.md` | entering plan mode |
| Compaction | `compaction.md` | preparing for a compaction, or resuming after one |
| Excel Rater Plans (shared) | `excel-rater-plans-common.md` | any Excel rater (ByPeril) ticket — HARD RULE, dump tasks, provisional scope, seeder-first |
| Excel Rater Plans (HO) | `ho-excel-rater-plans.md` | planning or executing a Homeowner Excel rater (ByPeril) ticket |
| Excel Rater Plans (Commercial) | `co-excel-rater-plans.md` | planning or executing a Commercial Excel rater (ByPeril) ticket |
| Tool Access | `tool-access.md` | a tool call fails or seems unavailable |
| Standup | `standup.md` | generating any standup update |
| Code Ownership | `code-ownership.md` | a ticket names a team or owner, or a fix lands outside pre-bind |
| Domain Reference | `swyfft-domain.md` | working with HomeownerStateConfig, carrier names, or PR descriptions |
| Release Schedule | `release-schedule.md` | saying when code reached beta or prod |
| Test Execution | `testing-execution.md` | running tests (filters, output capture, scope) |
| Test Writing | `testing.md` | writing tests, TDD, investigation |
| Seeding | `seeding.md` | seeding (BLOCKED — use `/eli--seed` skill instead) |
| Captured Asserts | `captured-asserts.md` | running or regenerating captured assert tests |
| Quote-def Dates & Ordering | `quote-def-dates-and-ordering.md` | editing QuoteDefinitions.txt / Seeder.cs overrides / HomeownerStateConfig versions, or reasoning about go-live dates, ordering, and which test enforces what |
| DB Querying | `db-querying.md` | writing or running any SQL query |
| Beta/Prod-Copy Database | `beta-prod-db.md` | connecting to any Azure SQL beta, dev, or prod-copy database |
| SolarWinds Logs | `~/.claude/commands/search-logs.md` | searching or analyzing SolarWinds logs. Every search goes through `/search-logs`, never the repo's `solarwinds` skill or `swo` |
| Investigation | `investigation.md` | investigating any bug or test failure |
| Merge Conflicts | `merge-conflicts.md` | resolving any merge conflict (BLOCKED — one file at a time only) |
| Meta (architecture) | `meta.md` | modifying any rules file, CLAUDE.md, or memory |
