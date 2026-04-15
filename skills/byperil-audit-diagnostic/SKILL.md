---
name: byperil-audit-diagnostic
description: Run the ByPeril Homeowner Excel audit diagnostic test against one or more quote IDs to reproduce production audit mismatches. Use when investigating ByPerilHomeownerExcelQuoteAuditService.GenerateAuditDoc errors or verifying specific quote IDs against the Excel rater.
---

# ByPeril Audit Diagnostic

Runs `ByPerilQuoteAuditDiagnosticTests.ValidateQuoteAudit` against a list of quote GUIDs.
The test loads each quote from the DB, runs the Excel rater, and compares
`AnnualPremium + AnnualFeesTotal` against `FinalTotalPremium` — same comparison as
production `ByPerilHomeownerExcelQuoteAuditService`.

## Arguments

Comma-, semicolon-, or whitespace-separated list of quote GUIDs.

If no quote IDs are provided, ask the user for them.

## Preflight Checks

Run these BEFORE invoking the script. If any fails, HARD STOP.

### 1. appsettings.json points at a non-local, non-prod DB

Read `Swyfft.Common/appsettings.json` and check the `SwyfftCore` connection string's
`Data Source`:

| Server | Verdict |
|---|---|
| `yde2xj08jm.database.windows.net,1433` (dev or beta catalog) | OK |
| `swyfftsqleastus2.database.windows.net` (prod-copy, read-only) | OK |
| `localhost` or anything local | HARD STOP — prod quote GUIDs won't exist locally |
| `swyfftsqleastus.database.windows.net` (no `2` — that's real prod) | HARD STOP — refuse |

If not OK, tell the user to point appsettings at prod-copy or beta per
`~/.claude/rules/beta-prod-db.md` Scenario 2, and stop.

### 2. `[Trait(TestGroup, ByPerilTests)]` is on the diagnostic class

Read `Swyfft.Services.Excel.IntegrationTests/Homeowner/ByPerilQuoteAuditDiagnosticTests.cs`
and verify the trait attribute is on the class declaration.

If missing: the `dotnet test` pre-tool hook requires `TestGroup=ByPerilTests` to keep
runs scoped. Check whether PR #19915 has merged (it adds the trait permanently). If
merged, pull latest. If not, add the trait locally as a temporary measure and note
it so it gets reverted with `appsettings.json` when investigation ends.

## Run

After preflight passes:

```
pwsh -NoProfile -File "$HOME/.claude/scripts/Run-ByPerilAuditDiagnostic.ps1" -QuoteIds "<ids>"
```

Set the Bash timeout to at least 300000ms. Cold build + 34 quotes took ~75s; single
quote runs take ~5-10s after warmup.

The script:
- Normalizes the ID list (splits on comma/semicolon/whitespace, dedupes, validates GUID format)
- Sets `EXCEL_AUDIT_DIAGNOSTIC_TEST_QUOTE_IDS` and `GITHUB_ACTIONS=true` (bypasses the
  `GlobalPersistentCounter` write to `dbo.TestGlobalIds` so read-only DBs work)
- Tees output to `$env:TEMP\swyfft-tests\<OutputName>.txt`
- Writes a TRX report to `build/Debug/net10.0/TestResults/<OutputName>.trx`

## After the Run

1. Read the output file (path printed at script end).
2. Report:
   - Pass / fail counts
   - Per failure: quote ID, config (e.g., `TX.QBE.ByPeril.EAndS.V5`), DB premium, Excel
     premium, diff, tolerance, and the saved `.xlsm` path (grep for `Excel file:` in the
     output — each failing run writes its workbook to
     `%TEMP%\1\Swyfft\<NNNNNN>\HO_<AD|ES>_<CARRIER>_<STATE>_Rater_<ts>_<guid>.xlsm`).
3. If there are failures, the next investigation step is to open each `.xlsm` and
   compare premium/fee lines against DB values using `ReadExcel` / `DumpRater` /
   `ReadNamedRanges` console tasks (see `~/.claude/rules/tooling.md`).

## Cleanup

When investigation ends, remind the user to:
- Revert `Swyfft.Common/appsettings.json` to local defaults
- Revert any temporary `[Trait(TestGroup, ByPerilTests)]` add (if PR #19915 still open)

Don't commit connection string changes.
