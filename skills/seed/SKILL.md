---
name: seed
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

## Step 3: Run the seed script

For elements:
```bash
pwsh -NoProfile -File "Seed-Elements-Local.ps1"
```
Timeout: 300000ms (~5 min).

For full database:
```bash
pwsh -NoProfile -File "Seed-Database-Local.ps1"
```
Timeout: 600000ms (~10 min).

## Step 4: Verify

- Exit code 0 = success. Trust it. Do NOT re-run because you "didn't see all the logs."
- If it fails, check the output for errors. A `"Seeding started on..."` sentinel in the history table means the seed was interrupted — it will auto-retry on the next run.

## Rules

- These two scripts are NOT interchangeable.
- Both scripts build the solution before seeding.
- Never seed when only named ranges or formulas changed in a rater file — tests open .xlsm files directly via COM interop.
