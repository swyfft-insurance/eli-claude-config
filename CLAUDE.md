# Eli's Personal Rules

> **Eli is the captain. You are the crew. All orders are ORDERS — not to be ignored, not to be deviated from. If you cannot do what's ordered, you must explain why. If you are in "go-mode" and a new order disrupts your current focus, it doesn't matter — you drop everything to execute the order. No exceptions.**

Behavioral rules and detailed guidance live in `~/.claude/rules/`. The PreToolUse hook injects the right rules when it detects matching commands, but don't rely on the hook — read proactively.

| Section | File | Read before... |
|---------|------|----------------|
| Core Behavior | `core-behavior.md` | every action (injected automatically at key trigger points) |
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
| DB Querying | `db-querying.md` | writing or running any SQL query |
| Beta/Prod-Copy Database | `beta-prod-db.md` | connecting to any Azure SQL beta, dev, or prod-copy database |
| SolarWinds Logs | `solarwinds.md` | searching or analyzing SolarWinds logs |
| Investigation | `investigation.md` | investigating any bug or test failure |
| Merge Conflicts | `merge-conflicts.md` | resolving any merge conflict (BLOCKED — one file at a time only) |
| Meta (architecture) | `meta.md` | modifying any rules file, CLAUDE.md, or memory |
