# SolarWinds Observability Logs

## Draft Queries Before Executing

Before calling any SolarWinds search tool, **draft the exact query in your response** and wait for approval. Include:
- The `filter` string
- The `startTime` and `endTime`
- The `pageSize`

The user cannot see tool parameters after the fact. If you run a bad query silently and report "no results," the user has no way to know what you actually searched for.

## No Guessing Search Terms

Before ANY log search, identify the exact source of your search terms. Valid sources:
- **Ticket**: a SolarWinds URL or exact error text in the YouTrack description
- **Code**: the log message string from the C# code that writes the log
- **User**: the user gave you the exact terms to search for

If you cannot point to one of these sources, **STOP and ask the user**. Do not guess, do not "try a few variations", do not fire off speculative queries. Every failed guess wastes time and tokens.

## How to Search

Use the `/search-logs` skill. Do NOT use the MCP tool (`mcp__solarwinds__search_logs`) or curl directly.

The skill calls `~/.claude/scripts/Search-SolarWinds.ps1` which:
- Splits date ranges into single-day chunks (the REST API returns empty on wide ranges)
- Paginates through all results per day
- Writes all logs to a file in `$env:TEMP\swyfft-logs\`

## API Quirks

- **Wide date ranges return empty results.** The API fails silently on multi-week ranges. Always use the script, which handles this automatically.
- **`Invoke-RestMethod` does not work.** The script uses curl internally because PowerShell's `Invoke-RestMethod` silently returns empty for the same URLs that curl handles correctly.
- **Pagination:** Results are paginated via `skipToken`. The script handles this automatically. If searching manually, do not claim "no logs exist" based on a single page.
