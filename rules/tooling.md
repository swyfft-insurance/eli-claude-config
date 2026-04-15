# Tooling Reference

## sqlcmd
- Windows executable: use `sqlcmd` if on PATH, otherwise locate via `where.exe SQLCMD.EXE`. Example: `pwsh -NoProfile -Command "& sqlcmd -S localhost -d SwyfftCore -E -Q \"...\" -s '|' -W"`
- ALWAYS query `INFORMATION_SCHEMA.COLUMNS` on LOCAL DB before writing any query. Never guess column names.
- Validate every query on localhost first — user runs queries on dev/beta/prod-copy on your behalf (see `beta-prod-db.md` for the prod-copy server).
- ALWAYS use JOINs. Never ask user to run 2 separate queries. Never hardcode IDs across environments.
- `ByPerilRaterTypeId` is numeric (e.g., 10203001), not a string.

## Rater File Comparisons
- `git show` corrupts binary Excel files. Use: stash new → dump old → pop stash → dump new → diff.
- Console tasks: `ReadExcel` (interactive, console output), `DumpRater` (full dump, requires `-o:"path"`), `ReadNamedRanges` (list ranges, `-RegexFilter`).
- Read `Swyfft.Seeding/ExcelLoaders/ByPeril/CLAUDE.md` before running these.

## GitHub PR Thread Resolution (GraphQL)
```
# Get thread IDs:
gh api graphql -f query='query { repository(owner:"swyfft-insurance",name:"swyfft_web") { pullRequest(number:PR) { reviewThreads(first:20) { nodes { id isResolved comments(first:1) { nodes { databaseId } } } } } } }'
# Resolve each:
gh api graphql -f query='mutation { resolveReviewThread(input:{threadId:"THREAD_ID"}) { thread { isResolved } } }'
```

## ByPeril Quote Audit Diagnostic Test

Use the `byperil-audit-diagnostic` skill. It checks appsettings.json is pointed at beta/dev/prod-copy (not localhost, not prod), checks the `[Trait(TestGroup, ByPerilTests)]` attribute is present, then invokes `~/.claude/scripts/Run-ByPerilAuditDiagnostic.ps1 -QuoteIds "<csv>"`.

The test loads each quote from the DB, runs the Excel rater, and compares `AnnualPremium + AnnualFeesTotal` against `FinalTotalPremium` — same comparison as production audit service. REVERT appsettings.json when done.

## Manual Testing Prompts
When prompting user for manual QA: use AskUserQuestion tool, provide SPECIFIC test data (addresses, names, values), one action per prompt, give concrete response options, keep prompts flowing. Never use Playwright when plan says "manual test with prompts."
