---
name: eli--seed
description: Seed the local database. Determines what changed, picks the right script (elements vs full), clears seeding history when needed, and runs it. Use when you need to seed after changing rater files, elements, or seeder C# code.
---

# Seed Local Database

## Step 1: Determine what needs seeding

Look at the current git diff (staged + unstaged) and recent context to classify the change:

| What changed | Script | Clear history? |
|---|---|---|
| Element definitions only (`ElementLoader*.cs`, `ElementDescription.txt`, constraint codes) | `Seed-Elements-Local.ps1` | No |
| Rater Excel files (`Data/**/*.xlsm`) | `Seed-Database-Local.ps1` | No (file hash changed, seeder re-runs automatically) |
| Seeder C# code (`Swyfft.Seeding/**/*.cs`) but NOT the rater file | `Seed-Database-Local.ps1` | **Yes** — seeder tracks file hashes, not code changes |
| Both elements and rater/seeder code | `Seed-Database-Local.ps1` (full reseed includes elements) | Only if seeder C# changed without rater file change |
| Only a named range or formula change in a rater (no factor data change) | **No seeding needed** — tests open the .xlsm directly | N/A |

If you cannot determine the change type from context, ask the user.

## Step 2: Clear seeding history (if needed)

Only when seeder C# code changed but the rater file did NOT:

```sql
-- Identify the state/ratingtype from the changed seeder file path
-- e.g., Swyfft.Seeding/ExcelLoaders/ByPeril/Homeowner/AL/EAndS/ → AL, EAndS
DELETE FROM EFSeedingHistories WHERE FileName LIKE '{STATE}\HOMEOWNER\BYPERIL\{RATINGTYPE}\%'
```

Run via sqlcmd against localhost:
```bash
pwsh -NoProfile -Command "& sqlcmd -S localhost -d SwyfftRating -E -Q \"DELETE FROM EFSeedingHistories WHERE FileName LIKE '{STATE}\HOMEOWNER\BYPERIL\{RATINGTYPE}\%'\" -W"
```

## Step 3: Run via the Run-Seed.ps1 wrapper

The wrapper captures full output to a deterministic file in the ticket's `artifacts/seed/` area (`~/.claude/tickets/<TicketFolder>/artifacts/seed/`) and prints the tail + exit code so you can verify completion without re-running. Direct invocation of `Seed-*-Local.ps1` is blocked by the pretooluse hook.

For elements:
```bash
pwsh -NoProfile -File "$HOME/.claude/scripts/Run-Seed.ps1" -Mode elements -TicketFolder "<SW-XXXXX-title>"
```
Timeout: 300000ms (~5 min).

For full database:
```bash
pwsh -NoProfile -File "$HOME/.claude/scripts/Run-Seed.ps1" -Mode database -TicketFolder "<SW-XXXXX-title>"
```
Timeout: 600000ms (~10 min).

## Step 4: Verify

The wrapper exits with the seed script's exit code. That's the authoritative signal:
- Exit 0 = seed completed. Done.
- Non-zero = seed failed. Read more of the log (`Get-Content -Path <full log path printed by wrapper> -Tail 200`) and diagnose. Do NOT pattern-match log text to second-guess the exit code — fix the script if its exit code is wrong.

A `Seeding started on...` row in `EFSeedingHistories` without a corresponding completion row means a seed was interrupted; the next seed run will auto-retry.

## Rules

- These two scripts are NOT interchangeable.
- Both scripts build the solution before seeding.
- Never seed when only named ranges or formulas changed in a rater file — tests open .xlsm files directly via COM interop.
