# Eli's Personal Rules

Last modified: 2026-03-26

These rules apply to every session, every project. They exist because Claude has violated all of them repeatedly.

> **Maintenance note:** If this file grows past ~300 lines, split domain/tooling reference into separate files that this file points to.

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

## Learning Loop
When the user corrects a pattern or behavior, suggest adding it to this file so the correction persists across sessions.

## Communication Style

| Rule | Bad | Good | Why |
|---|---|---|---|
| Show means show | "I read the file, here's a summary..." | *prints full content in code block* | Tool output is invisible to user |
| No embellishment | `gh pr review --approve --body "Great work!"` | `gh pr review --approve` | Do exactly what's asked, nothing more |
| Never say "no-op" | "This is a no-op change" | "This change has no practical effect" | Overused jargon |
| Wait after AskUserQuestion rejection | *sends another AskUserQuestion* | *waits silently* | User is actively typing — don't interrupt |

## Git Safety

- After creating a branch: `git push -u origin <my-branch>` IMMEDIATELY. Never leave tracking on someone else's branch or `origin/development`.
  - **What happened:** Tracking left on Ken's branch → unreviewed code merged to development. Catastrophic.
- Before ANY push: `git branch -vv`. Tracking must be `origin/<my-branch>`. Anything else = DO NOT PUSH.
- `git fetch origin <branch>` before claiming what's on a remote branch. Never trust stale local state.
- Merge commits: ONLY conflict resolution. Never mix with fixes or PR feedback. Never `git add -A` after a merge.
- "Commit minus X" = don't stage X. NEVER `git checkout --` those files (that destroys changes).
- No `/logical-commits` unless user explicitly asks.
- Pre-push: `git branch -vv` → `git log <upstream>..HEAD` → push
- Pre-commit: `git branch` (not on development/master?) → `git diff --staged` → message starts with ticket ID
- Pre-PR: read every YouTrack ticket in branch name → `git diff development...HEAD` → read `.github/pull_request_template.md` → draft for approval

## Windows / Tooling

| Rule | Bad | Good | Why |
|---|---|---|---|
| Env vars with `=` | `printenv YOUTRACK_API_TOKEN` | `powershell -NoProfile -Command "[System.Environment]::GetEnvironmentVariable('YOUTRACK_API_TOKEN', 'User')"` | Bash silently truncates values containing `=` (common in base64 tokens) |
| Existing files | Use Write tool on existing `.cs` file | Use Edit tool | Write destroys CRLF line endings |
| New files | Write tool, walk away | Write tool, then fix CRLF: `python3 -c "..."` | Write creates LF-only, repo uses CRLF |
| No sed -i | `sed -i 's/foo/bar/' file.cs` | Use the Edit tool | Destroys CRLF on Windows |
| No bash tee | `dotnet test \| tee output.txt` | `pwsh -NoProfile -Command "dotnet test 2>&1 \| Tee-Object -FilePath 'C:\...\output.txt'"` | bash tee crashes on Windows |
| No tail on background | `dotnet test 2>&1 \| tail -40` with `run_in_background` | `dotnet test` with `run_in_background: true`, no pipe | tail buffers everything, hides progress |
| Safe file moves | `mv source dest` | `cp source dest && ls dest && rm source` | mv silently fails on Windows — lost untracked analysis file |
| Windows paths in pwsh | `pwsh -Command "... '/tmp/file.txt'"` | `pwsh -Command "... 'C:\Users\eli.koslofsky\AppData\Local\Temp\file.txt'"` | pwsh doesn't translate Unix paths |

## Coding Standards
- Fix access modifiers (`private` → `protected`) instead of rewriting logic to avoid the call. Never treat access modifiers as immutable.
- Never add global usings as a shortcut. Add `using` to each file individually.

## External Actions

### Slack
- Look up ALL user IDs via `slack_search_users` BEFORE composing. Never guess.
- Check thread vs channel before sending.
- Messages CANNOT be deleted. If wrong, ASK the user what to do — don't send a duplicate.
  - **What happened:** Duplicate message in group DM with CTO. Embarrassing.
- Slack uses `mrkdwn`: code blocks need blank line after ```, no markdown tables, test in DM first.

### YouTrack
- Use `create_issue`, never `create_draft_issue`. Drafts cause duplicates.
- Read ALL custom fields (Carrier, USState, ProductLine, RatingType) — they scope the work.
- Read tickets FIRST before exploring code. Bug tickets contain error messages with the root cause.
  - **What happened:** Wasted 20+ min exploring code when ticket description had the exact error.
- `IssueType` field (not `Type`). Valid values: Feature, Bug, Support, Epic, Inquiry. No "Task".
- API returns `.youtrack.cloud:443` URLs — always convert to `swyfft.myjetbrains.com/youtrack/` for user-facing links.
- Use `youtrack-write-ticket` skill before writing ticket content.
- search_issues returns INTERNAL IDs (2-XXXXX). Call get_issue to get idReadable (SW-XXXXX).

### GitHub PRs
- PR description from TWO sources: YouTrack tickets (via get_issue) + actual diff (`git diff development...HEAD`). Never from memory or plan files.
- Treat as ONE combined diff, not commit-by-commit. Iterative commits are not logical units.
- No Review Guide unless commits were structured via `/logical-commits`.
- Never claim test status without running or checking — plan files go stale.
- Bot review comments (Copilot, Claude) get same seriousness as human comments.
- Reply to threads → resolve every thread. Merge queue requires it.
- Review style: only comment on fundamental bugs/red flags. No nits, no style comments.
- If YouTrack unavailable: STOP and ask about VPN. Don't guess ticket descriptions.
- GraphQL for resolving threads: query via `repository.pullRequest.reviewThreads`, NOT via `node(id:)` on PullRequestReviewComment (field doesn't exist).
- Never use `minimizeComment` — that hides, not resolves.

## Plan Mode
- Don't call ExitPlanMode while actively discussing — wait for conversation to conclude.
- Follow plans exactly. Don't skip, substitute, add, or omit steps. When blocked, ask.
- Read docs/CLAUDE.md BEFORE running console tasks. Never guess parameters.

## Tool Access
- YouTrack and Slack MCP tools are DEFERRED — must use ToolSearch to load before calling.
- NEVER tell the user you don't have access. You DO. YouTrack via MCP, GitHub via `gh` CLI.
- If a tool call fails, use ToolSearch to load it. If still failing, ASK — don't give up.

## Standup Notes
- GitHub username: `eli-swyfft`, YouTrack login: `eli.koslofsky`
- Slack #standup channel ID: `C06ALP0GTHV`
- YouTrack custom field is "Stage" (not "State") — values: Develop, Review, Ready for Test, Done, Tested
- Attribute work to the day it ACTUALLY happened (commit timestamps, ET timezone)
- EXACTLY TWO sections: last working day and Today. Never a third section.
- Don't reference internal epic labels/dates — just describe the work
- Only report actual work (commits, PRs, code). Ticket assignments by others are NOT work. But YOU moving tickets to Develop IS work (check `author` field on activities).
- After gathering data, re-read the standup skill instructions before writing output — large tool results push formatting rules out of working memory.

## Domain Reference: Swyfft Codebase

### HomeownerStateConfig
- Declaration order has FUNCTIONAL SIGNIFICANCE — `GetAllValuesWithSortOrder()` uses reflection.
- `EnsureConfigOrderWithDatabase` test verifies declaration order matches DB order (by RenewalOn).
- When adding a new version: ALWAYS add at END of State/Carrier/RatingType group.
- Seeder overrides: new version's RenewalOn must be AFTER all previous versions.
  - **What happened:** NJ BSIC V8 override had RenewalOn before V7's → 426 test failures.

### Comments and PR Descriptions
- Describe WHY and WHAT — not the debugging journey.
- Flag unexpected patterns: `SkipEachElementOptionTest = true`, disabled validation, skipped tests → STOP and ASK.

### Carrier Name Mappings
- Ark = Hadron (legacy name). Class named `Hsic` for FL/LA E&S.

## Testing Reference

### xUnit v3 MTP
- `dotnet test -- --list-tests` is BROKEN — use native runner: `"./Project/bin/Debug/net10.0/Project.exe" -list full`
- Trait filter: `-- --filter-trait "TestGroup=GroupName"` (NOT `--filter-class`)
- ByPeril Excel tests: ALWAYS use `-- --filter-trait "TestGroup=ByPerilTests"`. Unfiltered = 900+ tests (45 min).

### PreBind Captured Assert Tests
"Run pre-bind captured assert tests" = build `Swyfft.slnx` first, then 3 projects with `--no-build` in parallel:
```
dotnet test --no-build --project "Swyfft.Services.UnitTests" -- --filter-trait "TestGroup=PreBindResidentialCapturedAssertTests"
dotnet test --no-build --project "Swyfft.Services.IntegrationTests" -- --filter-trait "TestGroup=PreBindResidentialCapturedAssertTests"
dotnet test --no-build --project "Swyfft.Seeding.IntegrationTests" -- --filter-trait "TestGroup=PreBindResidentialCapturedAssertTests"
```

### Seeding — TWO DIFFERENT SCRIPTS
- "seed elements local" → `Seed-Elements-Local.ps1` (elements only, ~45s)
- "seed database local" → `Seed-Database-Local.ps1` (full reseed, minutes)
- NOT interchangeable. Both build the solution. Seeder tracks file HASHES — clear `EFSeedingHistories` when only C# changed.
- Exit code 0 = seed completed. Trust it. Never re-run because you "didn't see all the logs."

### Test Output
- Capture with pwsh Tee-Object (NOT bash tee): `pwsh -NoProfile -Command "dotnet test ... 2>&1 | Tee-Object -FilePath 'C:\Users\eli.koslofsky\AppData\Local\Temp\swyfft-tests\{project}-{filter}.txt'"`
- Create folder first if needed. Use WINDOWS paths. Name must include project + filter.
- Never `| tail -N` that discards error details. If tests fail, you already have the output — don't re-run.
- Single test suite: normal `dotnet test` (let it build). Multiple suites: build first, then `--no-build` in parallel.
- Never paper over test failures with ElementTestValues overrides or `SkipEachElementOptionTest = true`.

### TDD Hard Stop
Bug fixes: write failing test → run → verify it FAILS → HARD STOP for approval → then fix.
Refactoring: write safety-net test → run → verify it PASSES → HARD STOP for approval → then refactor.

## Tooling Reference

### sqlcmd
- Windows executable: use `sqlcmd` if on PATH, otherwise locate via `where.exe SQLCMD.EXE`. Example: `pwsh -NoProfile -Command "& sqlcmd -S localhost -d SwyfftCore -E -Q \"...\" -s '|' -W"`
- ALWAYS query `INFORMATION_SCHEMA.COLUMNS` on LOCAL DB before writing any query. Never guess column names.
- Validate every query on localhost first — user runs queries on prod on your behalf.
- ALWAYS use JOINs. Never ask user to run 2 separate queries. Never hardcode IDs across environments.
- `ByPerilRaterTypeId` is numeric (e.g., 10203001), not a string.

### Rater File Comparisons
- `git show` corrupts binary Excel files. Use: stash new → dump old → pop stash → dump new → diff.
- Console tasks: `ReadExcel` (interactive, console output), `DumpRater` (full dump, requires `-o:"path"`), `ReadNamedRanges` (list ranges, `-RegexFilter`).
- Read `Swyfft.Seeding/ExcelLoaders/ByPeril/CLAUDE.md` before running these.

### GitHub PR Thread Resolution (GraphQL)
```
# Get thread IDs:
gh api graphql -f query='query { repository(owner:"swyfft-insurance",name:"swyfft_web") { pullRequest(number:PR) { reviewThreads(first:20) { nodes { id isResolved comments(first:1) { nodes { databaseId } } } } } } }'
# Resolve each:
gh api graphql -f query='mutation { resolveReviewThread(input:{threadId:"THREAD_ID"}) { thread { isResolved } } }'
```

### Manual Testing Prompts
When prompting user for manual QA: use AskUserQuestion tool, provide SPECIFIC test data (addresses, names, values), one action per prompt, give concrete response options, keep prompts flowing. Never use Playwright when plan says "manual test with prompts."

## Beta/Dev Database Testing

When pointing local tests at beta/dev Azure SQL:
1. Checkout branch matching target environment (`git checkout beta`)
2. Edit `Swyfft.Common/appsettings.json` connection strings:
   - Server: `yde2xj08jm.database.windows.net,1433`
   - Beta: `SwyfftCoreBeta` / `SwyfftRatingBeta`; Dev: `SwyfftCoreDev` / `SwyfftRatingDev`
   - Must include: `Authentication=Active Directory Default` + `User ID=placeholder`
   - `User ID=placeholder` is a dummy value — it satisfies the connection string parser, not a real credential. Bypasses `CachedAzureAdAuthTokenRequirements` (otherwise: `Login failed for user ''`)
3. Requires VPN + Visual Studio signed in with Azure AD
4. REVERT when done. Don't commit connection string changes.
