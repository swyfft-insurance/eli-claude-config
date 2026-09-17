# SW-56248 — QBE NY named storm deductible: add the missing 1% row to the rater

**Plan type: Excel Rater bug** (follows the Bug Fix HARD STOP sequence in `~/.claude/rules/plan-mode.md`).

### HARD RULE — never parse a rater `.xlsm` yourself
To read anything out of a rater workbook — Versions-sheet values, named ranges, input options,
factor tables, fees — there are exactly TWO sanctioned sources:
1. **The pre-dumped baselines** under `Swyfft.Services.Excel.IntegrationTests/ExpectedResults/`,
   which cover Homeowner and Commercial leaves alike.
2. **A rater with no baseline yet** (a brand-new file): the `DumpRater` / `ReadExcel`
   console task (`WorkbookJsonDump.cs`).

**NEVER open the `.xlsm` yourself** — not with a Python/zip/XML parser, not by unzipping the OOXML
and reading `sheetN.xml` / `sharedStrings.xml`, not with any ad-hoc script. Hand-rolled Excel
parsing is banned: it silently mishandles shared strings, cached-vs-formula values, and
defined-name scoping, and it reinvents tooling the repo already owns. When the sanctioned tool is
heavyweight (DumpRater needs a console build/run), that cost is the price of correctness — pay it.
"It was faster to parse it myself" is never a justification.

> **Execute steps in order. Never skip ahead, reorder, or deviate. If you encounter anything that prevents adherence to this plan, HARD STOP — explain the blocker and wait for instructions.**

## Tickets

| Ticket | Title |
|---|---|
| [SW-56248](https://swyfft.myjetbrains.com/youtrack/issue/SW-56248) | [ExcelTest] Homeowner- ByPerilEAndSValidationTestsQbeNY.EachElementOption_ShouldBeExpected: EachElementOption_ShouldBeExpected failed for 3/3 configs: |

Related, not covered by this plan: [SW-52948](https://swyfft.myjetbrains.com/youtrack/issue/SW-52948)
added the 1% option and is the origin of the defect. It is Done and released; nothing about it is
reverted here.

## Diagnosis (approved)

The QBE NY Homeowner E&S rater cannot rate a 1% named storm deductible, which the product offers.

- `Swyfft.Seeding/DefaultElements/ElementLoader_Homeowner_ByPeril.cs:979-984` offers
  `[Percent_1, Percent_2, Percent_3, Percent_5, Percent_10]` for `ConstraintCode.QbeNY`.
- The rater's `NamedStorm_Deductible` tab holds only `V1` rows for 0.02, 0.03, 0.05 and 0.1, and
  `Versions!B14` holds `V1`. Its row-2 lookups are
  `INDEX(C$6:C$9,MATCH(1,($A$6:$A$9=NamedStormDeductibleVersion)*($B$6:$B$9=NamedStormDeductible),0),1)`,
  so a 1% quote returns `#N/A` across all ten perils.
- The error propagates to `Rating_Algorithm` row 17, then `Subtotal` at `B42`, then `Fees!C11` and
  the `Input!I4`/`I7` echo cells. Every errored cell in the saved failure workbook was traced through
  `DumpRater`; nothing upstream of `NamedStorm_Deductible!C2:L2` is in error.
- `ByPerilPremiumGenerator.cs:573-582` never performs this lookup and returns a factor of 1 for any
  deductible, so the C# rates 1% correctly and only the rater fails.
- QBE NC, NJ and SC each carry the `V1 / 0.01` row. NY is the only QBE E&S state that offers 1%
  without it.

Reproduced on `development` at `111903a595d` against a freshly seeded local database: 8 tests,
1 failed, the same three configs and the same two of nineteen iterations as the ticket reports.

Per `Swyfft.Services/Premium/AGENTS.md` § "The rater is the acceptance criteria", a lookup that
cannot resolve a valid input is a rater defect and the rater is what changes.

**The sweep is not narrowed.** `excel-rater-plans-common.md` § "The element sweep is sourced from the
generators" rules out the alternative fix: excluding `NamedStormDeductible` from the sweep, or pinning
it with `ElementTestValues`, would hide a live production defect rather than fix it. Agents can select
1% today on any NY risk more than five miles from the coast, and the audit service re-rates purchased
quotes through this same rater, so a quote bound at 1% fails its audit doc exactly as the test does.

## Versioned or unversioned

**Unversioned, and no new config version.** The change adds a lookup row for a key the tab never
held; it changes no existing row. Every factor on the tab is 1 across all ten perils in all four QBE
E&S states, and `GetNamedStormRiskFactors` returns 1 without reading the table, so no quote or policy
re-rates. `excel-rater-plans-common.md` § "Versioning is mandatory, even with no live policies"
applies to a change that moves premium or fees; this one moves neither.

**Pre-change quotes (`plan-mode.md` § "Unversioned changes")**: the second skip applies in substance
and is recorded here explicitly. No element option is added, removed or renamed, no config generates
a different element set, and no risk rule changes, so an existing NY QBE quote could be created
identically today. The only behavior that changes is that the rater stops erroring on an input the
product already accepted.

## Pre-read (subsystem orientation)

- `Swyfft.Services/Premium/AGENTS.md` — the Excel rater hub
- `Swyfft.Seeding/ExcelLoaders/AGENTS.md` — seeding a rater into the DB
- `Swyfft.Services.Excel/AGENTS.md` — the rater service and the audit service
- `Swyfft.Services.Excel.IntegrationTests/AGENTS.md` — the validation tests and reading a crash
- `Swyfft.Services/Common/AGENTS.md` — `ByPerilVersionLookup`
- `Swyfft.Services/Common/Homeowner/AGENTS.md` — `HomeownerStateConfig`, quote defs, seeder overrides
- `Swyfft.Services/Elements/AGENTS.md` and `Swyfft.Services/Elements/Homeowner/AGENTS.md` — elements and generators
- `Swyfft.Services/QuoteFees/AGENTS.md` — fees
- `~/.claude/rules/captured-asserts.md` — the baseline regen flow
- `~/.claude/rules/excel-rater-plans-common.md` § "Rater edits — when warranted, and the SharePoint flow"

## Sections that do not apply

- **Seeder overrides** — N/A. No new `HomeownerStateConfig`, `FloodStateConfig`,
  `CommercialStateConfig` or `DbbStateConfig`, so there is nothing to override and the override audit
  has no trigger.
- **State-config ticket notes and fold-vs-stack** — N/A. No `IStateConfig` implementer is added,
  edited or re-pointed, so the "Tag Each Config Version With Its Ticket" convention has no trigger.
- **Tests to add or modify** — N/A by rule. `plan-mode.md` § "Excel Rater bug": "The product's parity
  suite is the guard. Never write a unit test for a rater-parity defect." A unit test would assert C#
  against C#; `EachElementOption_ShouldBeExpected` already asserts C# against the rater and is the
  test that fails today.
- **Creating a test's subject** — N/A. No test is added or changed, so nothing arranges a quote,
  policy or claim and there is no creation helper to establish.
- **Scoping checkpoint** — N/A. No rater is delivered by the actuaries, so scope is not provisional.
  The baseline diff is still reviewed, as step 5.
- **Seeder changes** — N/A, verified rather than assumed. `ByPerilSeederHomeownerEAndSNY.cs:87`
  reads `NamedStormDeductible` from `A(6)` with no `.SetLength(N)`, and
  `ByPerilSeederHomeownerEAndSNJ.cs:75` is identical while NJ's tab already carries five rows. A
  fifth contiguous row therefore seeds with no reader change. Seeder-first still governs the
  ordering: the reseed in step 3 must be green before anything downstream runs.
- **UI acceptance criteria / screenshot** — N/A. Nothing renders differently; the 1% option is
  already on the quote today.

## Steps

### Step 0a — Ticket in Develop
Done 2026-09-17. SW-56248 moved from Ready for Dev to Develop.

### Step 0b — Branch
Create and push, from `development`:

```
bug/ek/20260917_SW-56248_qbe-ny-named-storm-1pct
```

Then `git push -u origin bug/ek/20260917_SW-56248_qbe-ny-named-storm-1pct` immediately, and confirm
`git branch -vv` tracks that branch and not `origin/development`.

### Step 1 — Eli makes the rater edit on SharePoint
The agent prepares the edit and never applies one. Programmatic edits of rater `.xlsm` files are
banned. The actuaries' SharePoint copy is the source of truth; the repo `Data/` copy is not.

Source file: `https://swyfft2.sharepoint.com/sites/swyfft-developmentsite/Shared%20Documents/By-Peril/NY`

Before starting, `NamedStorm_Deductible!C2` reads
`INDEX(C$6:C$9,MATCH(1,($A$6:$A$9=NamedStormDeductibleVersion)*($B$6:$B$9=NamedStormDeductible),0),1)`
and `A10:L10` is empty. If either differs, it is the wrong workbook.

`HO_ES_QBE_NY_Rater.xlsm`

Sheet: NamedStorm_Deductible

1. Select `A7:L7`, Insert Cells, Shift cells down. Not a whole-row insert: columns N through Q on
   these rows hold the separate DTC minimum named storm table, which a row insert would drag down.
2. Select `A6`, then paste the contents of this file:
```
C:\Users\eli.koslofsky\.claude\tickets\SW-56248-byperil-qbe-ny-each-element-option\artifacts\rater-edits\NamedStorm_Deductible-A6-L7.txt
```

Sheet: version_history

3. Add a row with:
```
9/17/2026 | NamedStorm_Deductible gained a 1% row (V1, factor 1 on all ten perils). The product has offered a 1% named storm deductible for QBE NY since July 2026, but the tab's lookup covered only 2%, 3%, 5% and 10%, so a 1% quote rated #N/A and the error carried through to the premium. The row-2 lookups were extended from $6:$9 to $6:$10. | Eli
```

This follows `excel-rater-plans-common.md` § "Adding a row to a lookup table". Row 7 is chosen for
the range expansion, not because 1% belongs there: inserting strictly inside `$6:$9` makes Excel
rewrite the ten row-2 lookups to `$6:$10` by itself, where inserting at row 6 would slide them to
`$7:$10` and leave the new row outside the lookup. 1% belongs first, so the paste covers two rows,
putting 0.01 on row 6 and the displaced 0.02 on row 7. Rows 8, 9 and 10 keep 0.03, 0.05 and 0.1
untouched, and the tab ends up ascending, matching QBE NC, NJ and SC.

The new row stays contiguous with the rest of the table, which is what lets the seeder's reader pick
it up (`ByPerilSeederHomeownerEAndSNY.cs:87` reads `NamedStormDeductible` from `A(6)`).

Scoping the insert to `A7:L7` is what keeps the DTC minimum named storm table out of it. That second
table shares these rows from columns N through Q (`P5`, `P6:Q6`, `P7:Q7`, `P9:Q9`, `P10:Q25` and
`O27:Q27`), and a whole-row insert would shift all of it down one, moving `Q27`'s
`VLOOKUP($P$10:$Q$25,…)` and the `$P$7`/`$Q$7` references with it. Nothing outside columns A to L
should differ in the baseline diff.

**HARD STOP** — wait for the edited workbook, downloaded from SharePoint.

### Step 2 — Place the rater in the repo
Copy the downloaded workbook over `Data/NY/Homeowner/ByPeril/EAndS/HO_ES_QBE_NY_Rater.xlsm`.

NY has one Homeowner E&S rater and one carrier on it, so there is no sibling carrier file to
propagate to. Confirm that before copying: `Data/NY/Homeowner/ByPeril/EAndS/` holds exactly this one
`.xlsm`. Raters are Git LFS objects.

### Step 3 — Reseed
Seeder first: nothing downstream runs until a full reseed is green.

```
/eli--seed
```
Full database mode. The rater file hash changes, so the seeder re-runs this rater without clearing
`EFSeedingHistories`. Exit code 0 is the signal; do not re-run on a hunch.

### Step 4 — Code-complete audit
```
/eli--code-complete-audit SW-56248-byperil-qbe-ny-each-element-option
```
The diff is a binary rater file plus regenerated baselines, so the audit has little to chew on, but
it runs on every change without exception.

**HARD STOP** — code complete. Do not print the diff. Wait for approval before running tests.

### Step 5 — Verification
See the Verification section below.

**HARD STOP** — tests complete. Report results and wait for approval.

### Step 6 — Post-test-approval sequence
Governed by `plan-mode.md` Part C § "Post-Test-Approval Sequence". Ask once for approval to commit
and push, commit as `SW-56248: <summary>`, push, then `/review-pr`, discuss findings, draft the PR
description into `artifacts/pr/`, run `/eli--audit-pr-desc` on it before Eli sees it, and create the
PR by hand with `gh pr create --body-file` and `--reviewer swyfft-insurance/dev`. Never route through
`/create-pr`.

**HARD STOP** — before every irreversible action.

### Step 7 — Move SW-56248 to Review
Immediately after the PR is created, not asked for.

### Step 8 — Send the parked Slack message
Last step, after the PR is up. The draft is at
`artifacts/slack/dev-analytics-rater-handoff-draft.md`, for `#dev-analytics-rater-handoff`
(`C06V258BWHJ`), tagging Ehren Weerheim and Dan Melson. Eli reviews it again before it goes, and it
needs updating from "making the edit" to the finished state, with the PR link.

## Rater defect found during execution

If the parity suite or the baseline diff surfaces a further defect in this rater, HARD STOP. Do not
work around it in C# and do not edit the workbook. Prepare the edit to the standard in
`~/.claude/rules/excel-rater-plans-common.md` § "Rater edits — when warranted, and the SharePoint
flow", read that section again at the time rather than from memory, and present the discrepancy, the
config's live status, and both reconciliation options. NY QBE E&S is live in prod on all three
configs, so the live-config branch applies and the choice is Eli's.

## Verification

### Execution sequence

1. Build once, backgrounded:
   `pwsh ~/.claude/scripts/Build-Solution.ps1`
   The line-length gate runs inside it, so no separate line-length step.
2. Then, in parallel, each backgrounded and each with `-NoBuild`:
   - `pwsh ~/.claude/scripts/Run-DotnetTest.ps1 -TicketFolder SW-56248-byperil-qbe-ny-each-element-option -Project Swyfft.Services.Excel.IntegrationTests -FilterTrait "TestGroup=ByPerilTests" -FilterClass "*ByPerilEAndSValidationTestsQbeNY" -NoBuild`
   - `pwsh ~/.claude/skills/eli--prebind-validation/Run-PreBindValidation.ps1 -TicketFolder SW-56248-byperil-qbe-ny-each-element-option -NoBuild`
     (its `param(...)` block declares `-NoBuild`, and it passes that flag through to each project's
     `Run-DotnetTest.ps1` call)
3. Read every changed expected-result file individually. No sampling.

`ExcelRaterValidationTestBase.GetConfigsForGroup` samples at most five configs per state, carrier and
rating-type group. NY QBE E&S has exactly three, so V1, V2 and V3 are all exercised and no version
needs naming in `AlwaysIncludedConfigs`.

Verification ends when every test above passes and Eli says we are done. The commit, push, review and
PR that follow are not part of it; they are step 6.

### What the baseline diff should show

Every sheet the diff touches gets a verdict; none is presumed noise.

| File | Expected change | Verdict |
|---|---|---|
| `ExpectedResults/ByPerilEAndSValidationTestsQbeNY/NamedStorm_Deductible.txt` | Row 2's ten formulas repointed from `$6:$9` to `$6:$10`, and rows 6 to 10 reading `0.01, 0.02, 0.03, 0.05, 0.1` with ten factors of 1 each. Columns N through Q unchanged on every row | The change itself |
| `ExpectedResults/ByPerilEAndSValidationTestsQbeNY/version_history.txt` | One new row logging the edit | The change itself |
| Every other sheet of that leaf | **Zero diff** | Negative-confirmation guard. Any other sheet differing means the wrong workbook was placed, or the actuaries' copy carries changes nobody asked for. HARD STOP and reconcile before proceeding. |
| Every other test class's baselines | **Zero diff** | No other rater is touched |

A seeded factor sheet gets the stricter bar, and the insert shifts rows rather than leaving them
alone, so the check is on the set rather than on row numbers: the deductible keys the tab offers must
be exactly the previous four plus `0.01`, and every factor must still be `1` on all ten perils. Any
existing key gaining a factor other than 1 would re-rate the in-force NY QBE book.

The C2 check is the one that catches a mis-placed insert. If those formulas still read `$6:$9` after
the edit, the insert landed on an edge and the new row is outside the lookup, which the paste would
hide.

### Captured asserts to regenerate

`SeedingRatingBruteForceTest` covers the Rating DB and will pick up the one new
`EFByPerilWindDeductibleFactor` row for NY QBE named storm at 0.01. `SeedingCoreBruteForceTest`
covers Core and should show **zero diff**, since no quote definition, element or config changes.
Both run inside `/eli--prebind-validation`; neither is listed separately in the execution sequence.
Locally the expected files rewrite themselves on the run, so the workflow is run, then review the
diff.

### Existing tests as regression checks

- `ByPerilEAndSValidationTestsQbeNY.EachElementOption_ShouldBeExpected` — the failing test. It is
  the regression guard for this defect, and it must pass all nineteen iterations on all three
  configs.
- `ByPerilEAndSValidationTestsQbeNY.RaterFileContents_ShouldMatchCaptured` — proves the placed
  workbook is the edited one and nothing else moved in it.
- `ByPerilEAndSValidationTestsQbeNY.InputSheet_AllInputCellsShouldBeWrittenByCSharp` and
  `VersionsSheet_AllVersionCellsShouldBeWrittenByCSharp` — prove the edit did not leave an Input or
  Versions cell that C# no longer writes.
- `ByPerilEAndSValidationTestsQbeNY.CountyMinimumPremium_ShouldMatchExcel`,
  `CoverageBCDDictCaps_ShouldMatchRater` and `RateModeling_ShouldBeExpected` — the rest of the leaf,
  proving the workbook still rates as it did.
- `/eli--prebind-validation`, 42 tests across three projects. Relevant here because it carries
  `MigrationCoverageTests.Migration_AllSourceElementValues_ShouldProduceValidTargetElements`, which
  `ho-excel-rater-plans.md` requires on every rater ticket without exception, and both seeding
  brute-force captured asserts.

### Code-complete audit — step 4 above.

### PR-description audit — `/eli--audit-pr-desc` on the body file, inside step 6, before Eli sees the description.

### AC coverage map

The ticket is auto-filed and states no acceptance criteria. Its Actual Result is the test failure,
so the single implicit criterion is that the failure stops.

| Criterion | Covered by |
|---|---|
| `EachElementOption_ShouldBeExpected` passes for `NY.QBE.ByPeril.EAndS` V1, V2 and V3 | Execution sequence step 2, first run |
| The fix does not re-rate the in-force NY QBE book | "What the baseline diff should show", rows 6 to 9 byte-identical, plus `RateModeling_ShouldBeExpected` and `CountyMinimumPremium_ShouldMatchExcel` |
| Nothing else in the rater moved | "What the baseline diff should show", zero-diff rows |
| No other rater or product line is affected | "What the baseline diff should show", final row, plus `/eli--prebind-validation` |

## Progress

| When | What happened |
|---|---|
| 2026-09-17 11:02 AM | Step 0a and 0b complete. SW-56248 moved to Develop. Branch bug/ek/20260917_SW-56248_qbe-ny-named-storm-1pct created from origin/development at 111903a595d and pushed with its own tracking. Diagnosis reproduced on a freshly seeded local DB and approved: the NY QBE rater's NamedStorm_Deductible tab has no 1% row, so a 1% quote rates #N/A and the error carries through to the premium. Awaiting the SharePoint rater edit (Step 1). |
| 2026-09-17 11:33 AM | Steps 1 and 2 complete. Eli edited the rater on SharePoint. The first attempt used a whole-row insert, which shifted the DTC minimum named storm table in columns N through Q down a row; he redid it scoped so those columns are byte-identical to the original. Verified via DumpRater before placing: the ten row-2 lookups read 6:10, rows 6 to 10 read 0.01, 0.02, 0.03, 0.05, 0.1 with a factor of 1 on all ten perils, and version_history row 21 carries the note. Placed over Data/NY/Homeowner/ByPeril/EAndS/HO_ES_QBE_NY_Rater.xlsm. Full reseed running. |
| 2026-09-17 11:59 AM | Step 3 and 4 complete. Full reseed exited 0, and a localhost query confirmed the seeder picked up the new row: NY QBE E&S named storm now has five V1 rows, 0.01 through 0.1, every factor 1 (artifacts/db-queries/ny-qbe-named-storm-seeded-factors.md). Code-complete audit found nothing to fix; the branch carries one file, the rater's LFS pointer, so every wave is N/A and the line-length gate passes on both branch and local. |
Entries are appended by `/eli--generate-progress-entry`. Never hand-write a row or type a timestamp.
