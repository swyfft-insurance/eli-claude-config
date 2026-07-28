---
name: eli--byperil-audit-diagnostic
description: Run the Excel audit diagnostic test against one or more quote IDs to reproduce production audit mismatches — Homeowner (ByPerilQuoteAuditDiagnosticTests) by default, Commercial (CommercialQuoteAuditDiagnosticTests) with the Commercial flag. Use when investigating ByPerilHomeownerExcelQuoteAuditService/CommercialExcelQuoteAuditService GenerateAuditDoc errors or verifying specific quote IDs against the Excel rater.
---

# ByPeril Audit Diagnostic

Runs `ByPerilQuoteAuditDiagnosticTests.ValidateQuoteAudit` (Homeowner) or
`CommercialQuoteAuditDiagnosticTests.ValidateQuoteAudit` (Commercial — pass `-Commercial` to the
script) against a list of quote GUIDs.
For each quote the test does a **three-way comparison** and prints per-factor diffs:

- **DB(bind)** — stored `AnnualPremium + AnnualFeesTotal`, what the customer was charged.
- **Excel(now)** — `FinalTotalPremium` from the current rater. `Excel ≠ DB` is the production
  audit failure — the diagnostic calls the audit service's own `ComparePremium`
  (`ByPerilHomeownerExcelQuoteAuditService` / `CommercialExcelQuoteAuditService`).
- **Recompute(now)** — current C# premium via an in-RAM clone reprice; supplementary.

For interpreting the output (which column moved, the Hurricane clone-artifact, etc.), see the
`eli--audit-doc-mismatch-investigation` skill.

## Arguments

Comma-, semicolon-, or whitespace-separated list of quote GUIDs.

If no quote IDs are provided, ask the user for them.

## Preflight & DB Setup

These quote GUIDs never exist locally, so a **localhost** connection is the *expected default*
state of appsettings — NOT a surprise to error on. The quotes can live in beta OR in prod-copy
depending on which environment the ticket's errors came from and how recently the quote was
created, so the environment is a real choice the user must make.

Read `Swyfft.Common/appsettings.json` and check the `SwyfftCore` connection string's
`Data Source`:

| Server | Action |
|---|---|
| `yde2xj08jm.database.windows.net,1433` (dev or beta catalog) | Already remote — confirm it's the env the user wants, then proceed |
| `swyfftsqleastus2.database.windows.net` (prod-copy, read-only) | Already remote — confirm, then proceed |
| `localhost` / anything local / anything else | Ask which env (below), then repoint |
| `swyfftsqleastus.database.windows.net` (no `2` — that's real prod) | **HARD STOP — refuse** |

### Ask which environment — reference the ticket's environment

Before repointing, **ask the user which environment to point at**, and frame the question with
the ticket's own environment context so the choice is informed:

- Pull the environment(s) from the ticket — for a LogMonitor ticket the body lists them (e.g.
  `Environments: Console.Beta, Console.Prod`); otherwise infer from the `Found in Stage` /
  custom fields.
- Present the env choice referencing that: e.g. *"This ticket's errors are from Console.Beta and
  Console.Prod. Which DB should I point at — beta, or prod-copy?"*
- Decision guidance to include: quotes from prod errors → **prod-copy**
  (`swyfftsqleastus2.database.windows.net`, read-only, `master` branch) by default — it's real
  prod data, which is exactly what prod-copy is for. **Beta** (`beta` branch) only when the
  ticket's errors are from the beta environment; note beta is a weekly Monday snapshot, so it
  only has records that predate the most recent Monday copy. See
  `~/.claude/rules/beta-prod-db.md` § "Data Availability".

### Repoint to the chosen environment

Rewrite all four connection strings — `SwyfftCore`, `SwyfftCoreSecondary`, `SwyfftRating`,
`SwyfftRatingSecondary` — using the template in `~/.claude/rules/beta-prod-db.md` Scenario 2
(only `Data Source`, `Initial Catalog`, and the
`Authentication=Active Directory Default;User ID=placeholder;` auth pair change):

| Env | Deployment branch | Server | Core / Rating catalogs |
|---|---|---|---|
| Beta | `beta` | `yde2xj08jm.database.windows.net,1433` | `SwyfftCoreBeta` / `SwyfftRatingBeta` |
| Prod-copy | `master` | `swyfftsqleastus2.database.windows.net` | `SwyfftCoreProd` / `SwyfftRatingProd` |
| Dev | `development` | `yde2xj08jm.database.windows.net,1433` | `SwyfftCoreDev` / `SwyfftRatingDev` |

Prereqs for the connection to authenticate: **VPN connected** and **Azure AD signed in**
(Visual Studio or `az login`). If the run fails with a login/connection error, that's the
likely cause — surface it, don't silently retry.

A run that fails while loading the quote (before any diagnostic comparison) with a
schema-mismatch error — `IndexOutOfRangeException: <ColumnName>`, `SqlException: Invalid column
name` / `Invalid object name`, or any other schema-shaped failure — means the current branch's
migrations are out of sync with the environment's schema. Check out the environment's deployment
branch (table above), rebuild, and re-run. See `~/.claude/rules/beta-prod-db.md` § "Branch vs
environment schema".

If the chosen env turns out to be missing the quote (beta snapshot too old), tell the user and
offer to repoint to prod-copy and re-run.

## Run

After preflight passes:

```
pwsh -NoProfile -File "$HOME/.claude/scripts/Run-ByPerilAuditDiagnostic.ps1" -TicketFolder "<SW-XXXXX-title>" -QuoteIds "<ids>"
```

Add `-Commercial` for Commercial quotes (runs `CommercialQuoteAuditDiagnosticTests` and passes
the `-IsCommercial` opt-in through to `Run-DotnetTest.ps1`).

Set the Bash timeout to at least 300000ms. Cold build + 34 quotes took ~75s; single
quote runs take ~5-10s after warmup.

The script:
- Normalizes the ID list (splits on comma/semicolon/whitespace, dedupes, validates GUID format)
- Sets `EXCEL_AUDIT_DIAGNOSTIC_TEST_QUOTE_IDS` and `GITHUB_ACTIONS=true` (bypasses the
  `GlobalPersistentCounter` write to `dbo.TestGlobalIds` so read-only DBs work)
- Calls `Run-DotnetTest.ps1` with `-FilterClass '*ByPerilQuoteAuditDiagnosticTests'`
- Output uses deterministic naming: `{branch}_{project}_{filters}_{suffix}_{timestamp}.txt`

## After the Run

1. Read the output file (path printed at script end).
2. Report:
   - Pass / fail counts
   - Per failure: quote ID, config (e.g., `TX.QBE.ByPeril.EAndS.V5`), the three totals
     (DB / Excel / Recompute), diff, tolerance, the diverging by-peril factor(s) the test
     names, and the saved `.xlsm` path (grep for `Excel file:` in the output — each failing
     run writes its workbook to
     `%TEMP%\1\Swyfft\<NNNNNN>\HO_<AD|ES>_<CARRIER>_<STATE>_Rater_<ts>_<guid>.xlsm`).
3. If there are failures, the test has already named the diverging factor — go to the
   `eli--audit-doc-mismatch-investigation` skill (Step 2 interpretation gotchas, Step 3 source trace).
   Don't hand-compare the `.xlsm` first; that's a Step 3 fallback, not the starting point.

## Cleanup

When investigation ends, remind the user to:
- Revert `Swyfft.Common/appsettings.json` to local defaults
- Revert any temporary `[Trait(TestGroup, ByPerilTests)]` add (if PR #19915 still open)

Don't commit connection string changes.
