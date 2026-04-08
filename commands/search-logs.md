Search SolarWinds Observability logs.

## Required Arguments

The user must provide:
- **Search terms** — either directly, or a YouTrack ticket ID (from which you extract the SolarWinds query field)
- **Date or date range** — a single day or start/end range

## Rules

1. **No guessing search terms.** Terms must come from: the ticket, the C# code that writes the log, or the user. If you don't have terms, ask.
2. **Draft the query before executing.** Show the user the exact `Filter`, `StartDate`, `EndDate` and wait for approval.
3. **Do not use the MCP tool or curl directly.** Always use the PowerShell script.

## Execution

After the user approves the query, run:

```
pwsh -NoProfile -File "$HOME/.claude/scripts/Search-SolarWinds.ps1" -Filter "SEARCH_TERMS" -StartDate "YYYY-MM-DD" -EndDate "YYYY-MM-DD"
```

The script:
- Splits ranges into single-day chunks (the API returns empty on wide ranges)
- Paginates through all results per day
- Writes all logs to a file in `$env:TEMP\swyfft-logs\`
- Prints a per-day summary to the console

## After Execution

1. Read the output file to answer the user's question
2. Report: how many logs found, which days, and the key content
3. Do NOT summarize or paraphrase log messages — show exact quotes
