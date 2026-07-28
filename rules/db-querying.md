# Database Querying

## sqlcmd on Windows
- Use `sqlcmd` if on PATH, otherwise locate via `where.exe SQLCMD.EXE`.
- Example: `pwsh -NoProfile -Command "& sqlcmd -S localhost -d SwyfftCore -E -Q \"...\" -s '|' -W"`

## Before Writing Any Query

1. **Query `INFORMATION_SCHEMA.COLUMNS`** on the LOCAL DB first. Never guess column names or types.
2. **Validate every query on localhost first.** Even if you expect 0 rows, the query must execute without errors. The user runs queries on dev/beta/prod-copy on your behalf — they should never be the first to discover a syntax error.

## Query Construction

- **Never hardcode IDs in queries.** Always JOIN to reference tables and filter by name/string. If you need to filter by a lookup value, JOIN to the table that defines it and match on the human-readable column. This is especially dangerous when validating on localhost and the query will be run in a different environment — the IDs may not match.
- **ALWAYS use JOINs** when the data can be joined. Never hardcode IDs from one query into another.
- **Multi-SELECT scripts: WAIT.** Multi-SELECT scripts are fine when a JOIN genuinely won't work (disjoint result shapes, different row counts, etc.) — but the user copy-pastes one result set at a time. After the first result set arrives, **STOP. Do not reason, do not search code, do not call tools.** Acknowledge receipt, then explicitly wait for the remaining result sets. Default to a JOIN whenever plausible; reach for multi-SELECT only when joining would contort the query.

## Save every query and its results to the ticket folder

When working a ticket, save each query's raw SQL and its results to the ticket's artifacts
(`~/.claude/tickets/<TicketFolder>/artifacts/db-queries/`) as they come back. The evidence trail
must survive the session; a query whose results live only in chat is lost on compact.

What earns saving is whether the result is *evidence about the data* — a no-rows result from a
well-formed query counts, because "this properly-scoped query found nothing" proves absence (and a
seemingly-dud query that actually establishes a fact, e.g. a join that comes back empty because the
join column is NULL on the subject row, counts too — save it with the explanation). Don't save a
query that returned nothing or garbage because the query itself was defective — wrong join, wrong
column, bad schema assumption; that result proves nothing about the data and pollutes the trail.

## Remote Database Queries

- Never connect directly to remote databases via sqlcmd.
- Draft and validate on localhost → present to user → user runs it on dev/beta/prod-copy.
- **Always specify which environment to run against** when presenting a query. Don't leave it to the user to figure out — state "Run this on prod-copy" or "Run this on beta" explicitly. See `beta-prod-db.md` for when to use which environment.
