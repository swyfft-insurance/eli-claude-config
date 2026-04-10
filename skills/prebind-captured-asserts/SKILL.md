---
name: prebind-captured-asserts
description: Run PreBind Captured Assert tests and regenerate expected results. Use after adding new HomeownerStateConfig versions, quote definitions, elements, or constraint codes.
---

# PreBind Captured Assert Tests

## Step 1: Determine if seeding is needed

Some captured assert tests compare against DB state. If you changed data that's seeded into the database, seed first.

| What changed | Seed needed? | Script |
|---|---|---|
| QuoteDefinitions.txt, seeder overrides | Yes | `Seed-Database-Local.ps1` |
| ElementLoader files, constraint codes, element descriptions | Yes | `Seed-Elements-Local.ps1` |
| HomeownerStateConfig (new versions) + QuoteDefinitions | Yes | `Seed-Database-Local.ps1` |
| Visibility logic, runtime filtering, helper methods only | No | — |

If seeding is needed, use the `/seed` skill first.

## Step 2: Run the script

The script builds, then runs all 3 projects concurrently with output saved to `$env:TEMP\swyfft-tests\`.

```bash
pwsh -NoProfile -File "$HOME/.claude/skills/prebind-captured-asserts/Run-PreBindCapturedAsserts.ps1"
```

Timeout: 600000ms.

## Step 3: Review the diffs

After regeneration, check what changed in the expected result files:

```bash
git diff --stat -- "**/*ExpectedResults*"
```

Then review the actual diffs to verify:
- Only your new data appears (new configs, new elements, etc.)
- No unexpected changes to existing entries
- No entries disappeared

Show the diff summary to the user for approval before proceeding.
