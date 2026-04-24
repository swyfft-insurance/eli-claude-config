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

## Remote Database Queries

- Never connect directly to remote databases via sqlcmd.
- Draft and validate on localhost → present to user → user runs it on dev/beta/prod-copy.
- See `beta-prod-db.md` for which environment to target and connection details.
