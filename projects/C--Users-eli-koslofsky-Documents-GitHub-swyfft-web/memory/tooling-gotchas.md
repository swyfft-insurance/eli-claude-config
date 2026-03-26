# Tooling Gotchas

## sqlcmd
- Windows executable — ALWAYS run via `pwsh -NoProfile -Command`
- CORRECT: `pwsh -NoProfile -Command "& 'C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn\SQLCMD.EXE' -S localhost -d SwyfftCore -E -Q \"...\" -s '|' -W"`
- WRONG: Running sqlcmd directly from bash (not in PATH, `&` is PowerShell syntax)

## SQL Queries
- ALWAYS query `INFORMATION_SCHEMA.COLUMNS` on the LOCAL DB before writing ANY query — do NOT guess column names. EVER.
- The user runs queries against production on your behalf. You MUST validate every query on localhost first. Getting it wrong wastes the user's time and is unacceptable.
- ALWAYS use JOINs to combine data from multiple tables — NEVER ask the user to run 2 separate queries when a single query with JOINs will do. This wastes the user's time.
- NEVER use hardcoded IDs (like QuoteDefinitionId) across environments — they're auto-incremented and differ between local/prod. Always JOIN from a known stable key (like QuoteId).
- `ByPerilRaterTypeId` is numeric (e.g., 10203001), NOT a string
- Look up rater type IDs: `SELECT * FROM EFByPerilRaterTypes WHERE StateCode = 'AL' AND RatingType = 'EAndS'`
- When a query returns 0 rows, verify the query is correct FIRST

## sed / File Editing
- NEVER use `sed -i` on Windows/Git Bash — destroys CRLF line endings
- ALWAYS use the Edit tool for find-and-replace operations
- Also applies to `awk`, `perl -i`, etc.

## Line Endings (VERY COMMON MISTAKE)
- All repo files use **CRLF** line endings
- **The Write tool ALWAYS creates LF-only files.** After using Write to create ANY new file, immediately fix line endings:
  `python3 -c "with open('FILE','rb') as f: c=f.read()\nwith open('FILE','wb') as f: f.write(c.replace(b'\\r\\n',b'\\n').replace(b'\\n',b'\\r\\n'))"`
- **The Write tool also converts existing CRLF files to LF** when used to rewrite them. Prefer the Edit tool for modifying existing files.
- When appending a new line via python `open(..., 'w')`, Python defaults to the OS line ending — but bash/Write may use LF
- **ALWAYS verify line endings after creating/rewriting files**: `python3 -c "with open('file','rb') as f: c=f.read(); print(c.count(b'\\r\\n'), c.count(b'\\n')-c.count(b'\\r\\n'))"`
- This mistake causes noisy diffs that obscure real changes and trips up code reviewers
- **What happened (2026-03-18)**: Created a new .cs file with Write tool, and rewrote an existing .cs file with Write tool. Both had LF-only endings. User caught it in GitHub Desktop diff ("This diff contains a change in line endings from 'LF' to 'CRLF'").

## Slack Formatting
- Slack uses `mrkdwn`, NOT standard markdown
- Code blocks: ``` on own line, then BLANK LINE, then code, then ``` on own line
- Markdown tables (pipe syntax) DO NOT WORK — use ASCII tables in code blocks
- Messages CANNOT be edited or deleted once sent
- Test code blocks by sending to your own DM first (user ID `U07C1JLR0BY`)

## Slack Pre-Send Checklist (MANDATORY before every slack_send_message)
1. **Look up ALL user IDs** — run `slack_search_users` for every @mention BEFORE sending. Never guess.
2. **Thread vs channel** — read the recent channel messages to see if the conversation is in-channel or threaded. Match the flow.
3. **One shot** — messages cannot be deleted. If you send a wrong message, you cannot fix it by sending another. Ask the user what to do.

## GitHub PR Review Threads
- NEVER use `minimizeComment` — that HIDES, not resolves
- When posting replies via `gh api`, backticks get interpreted by bash — use heredoc or temp file
- **To reply**: `gh api repos/OWNER/REPO/pulls/PR/comments/COMMENT_ID/replies -f body="..."`
- **To resolve threads** (two-step):
  1. Get thread IDs: `gh api graphql -f query='query { repository(owner:"OWNER",name:"REPO") { pullRequest(number:PR) { reviewThreads(first:20) { nodes { id isResolved comments(first:1) { nodes { databaseId } } } } } } }'`
  2. Resolve each: `gh api graphql -f query='mutation { resolveReviewThread(input:{threadId:"THREAD_ID"}) { thread { isResolved } } }'`
- **Do NOT use** `node(id: "COMMENT_NODE_ID") { ... on PullRequestReviewComment { pullRequestReviewThread { id } } }` — the field `pullRequestReviewThread` does not exist on `PullRequestReviewComment`. Always query via `repository.pullRequest.reviewThreads` instead.

## Git Branch Tracking and Pushing — CRITICAL, HAS CAUSED SERIOUS DAMAGE
- After creating ANY branch, IMMEDIATELY push to own remote: `git push -u origin <my-branch-name>`. This sets tracking correctly.
- Tracking must point to YOUR OWN remote branch (`origin/feature/ek/...`). NOT `origin/development` (GitHub Desktop would push directly to dev). NOT someone else's branch.
- "Base off branch X" = use X as starting point, then immediately `git push -u origin <my-branch-name>` to create own remote and fix tracking.
- **Before ANY push**: `git branch -vv`. Tracking must be `origin/<my-branch-name>`. Anything else = DO NOT PUSH.
- **What happened (2026-03-13)**: Tracking was left on `origin/feature/ks/...` after branching from Ken's branch. `git push` sent commits there. Code merged to development unreviewed with known test failures. Catastrophic.
- **What almost happened (2026-03-16)**: Tracking was set to `origin/development`. GitHub Desktop showed "Push origin/devel..." which would have pushed directly to development bypassing PRs.

## Seeding — TWO DIFFERENT SCRIPTS, DO NOT CONFUSE THEM
- **`Seed-Elements-Local.ps1`**: Only DefaultElements, ElementConstraints, ElementDescriptions. Use when asked to "seed elements local".
- **`Seed-Database-Local.ps1`**: Full reseed including QuoteDefinitions. Use when asked to "seed database local".
- These are NOT interchangeable. "seed elements local" means `Seed-Elements-Local.ps1`. Period.
- Both scripts build the solution — don't `dotnet build` first
- Seeder tracks file HASHES, not code changes — clear `EFSeedingHistories` when only C# code changed

## CRITICAL: Seed scripts FAIL LOUDLY — never assume they didn't complete
- Both scripts use `$ErrorActionPreference = 'Stop'` + `Invoke-WithFailureNotification` wrapping
- Any failure inside throws an exception → non-zero exit code → Slack failure notification sent
- **Exit code 0 = seed completed successfully. Full stop. Trust it.**
- NEVER re-run a seed because you "didn't see all the logs" or "aren't sure it completed"
- NEVER claim the seed didn't run when the task shows exit code 0
- If the seed failed, you'll know: non-zero exit code in the task output

## YouTrack Links
- The YouTrack API (`add_issue_comment`, `get_issue`, etc.) returns URLs with the domain `swyfft.youtrack.cloud:443`
- The correct user-facing URL domain is `swyfft.myjetbrains.com/youtrack/`
- When linking to YouTrack in external messages (GitHub PRs, Slack), ALWAYS use `https://swyfft.myjetbrains.com/youtrack/issue/SW-XXXXX` — NOT the `.youtrack.cloud` URL from the API response
- Include the issue slug in the URL path for readability: `https://swyfft.myjetbrains.com/youtrack/issue/SW-48463/Remove-numbering-from-comparison-element-ordering`

## YouTrack Issue Creation
- The field is `IssueType`, NOT `Type`
- Valid values: Feature, Bug, Support, Epic, Inquiry — there is NO "Task" type
- ALWAYS use `youtrack-write-ticket` skill before writing ticket content
- ALWAYS read memory before creating tickets (or doing anything external)

## Comparing Old vs New Rater Files
- `git show` corrupts binary Excel files — do NOT use it
- Stash new raters → dump old → pop stash → dump new → diff
- Console tasks: `ReadExcel` and `DumpRater` in Swyfft.Console (use `-t:ReadExcel` / `-t:DumpRater`)

## Carrier Name Mappings
- Ark = Hadron (legacy name). In version lookups the class is named `Hsic` (for FL/LA E&S).
