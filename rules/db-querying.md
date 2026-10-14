# Database Querying

## sqlcmd on Windows
Use `sqlcmd` from PATH, else locate it with `where.exe SQLCMD.EXE`. Example: `pwsh -NoProfile -Command "& sqlcmd -S localhost -d SwyfftCore -E -Q \"...\" -s '|' -W"`

## Before Writing Any Query
Look up column names and types in the local `INFORMATION_SCHEMA.COLUMNS` first. Run every query on localhost without errors before presenting it, even when it should return 0 rows.

## Query Construction
- Never hardcode IDs, and never carry IDs from one query into another. JOIN to the table that defines a lookup value and filter on its human-readable column.
- Default to a JOIN. Use a multi-SELECT script only when a JOIN would contort the query (disjoint shapes, different row counts). The user pastes one result set at a time: after the first arrives, acknowledge it and wait for the rest, with no reasoning, code search or tool calls.

## Save every query and its results to the ticket folder
When working a ticket, save each query's SQL and results to `~/.claude/tickets/<TicketFolder>/artifacts/db-queries/` as they come back. Save any result that is evidence about the data, including an empty result from a well-formed query, with what it proves. Don't save the output of a defective query (wrong join, wrong column, bad schema assumption).

## Remote Database Queries
- Run read-only SELECTs yourself against dev, beta and IMS staging (`SwyfftImsStaging`) with `sqlcmd -Q` (the repo's `block-prod-db.ps1` allows them). Prod-copy is blocked for you, so Eli runs those. Choose the environment per `beta-prod-db.md` § "Data Availability", never by which one you can reach.
- A query for Eli to run goes in chat in a ```sql block, naming the environment ("Run this on prod-copy"). Only a query too long to paste (hundreds of VALUES rows) goes as a full clickable file path. Never just name a folder or file.
- Bulk results that feed a follow-up artifact come back as a file path, never through chat, and a script builds the artifact from the file. Never re-type or heredoc data that already exists in chat or on disk; ask for a file instead.
