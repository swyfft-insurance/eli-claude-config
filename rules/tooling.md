# Tooling Reference

## sqlcmd
- Windows executable: use `sqlcmd` if on PATH, otherwise locate via `where.exe SQLCMD.EXE`. Example: `pwsh -NoProfile -Command "& sqlcmd -S localhost -d SwyfftCore -E -Q \"...\" -s '|' -W"`
- ALWAYS query `INFORMATION_SCHEMA.COLUMNS` on LOCAL DB before writing any query. Never guess column names.
- Validate every query on localhost first — user runs queries on dev/beta/prod on your behalf.
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

For reproducing SolarWinds audit mismatches against specific quotes in beta/dev:

1. Point `Swyfft.Common/appsettings.json` at beta (see `beta-db.md` Scenario 2)
2. Set the env var and run (env var must be exported so dotnet test inherits it):
   ```bash
   export EXCEL_AUDIT_DIAGNOSTIC_TEST_QUOTE_IDS="GUID1,GUID2,GUID3"
   dotnet test --project "Swyfft.Services.Excel.IntegrationTests" -- --filter-class "*ByPerilQuoteAuditDiagnosticTests*"
   ```
4. REVERT appsettings.json when done

The test loads each quote from the DB, runs the Excel rater, and compares `AnnualPremium + AnnualFeesTotal` against `FinalTotalPremium` — same comparison as the production audit service.

## Manual Testing Prompts
When prompting user for manual QA: use AskUserQuestion tool, provide SPECIFIC test data (addresses, names, values), one action per prompt, give concrete response options, keep prompts flowing. Never use Playwright when plan says "manual test with prompts."
