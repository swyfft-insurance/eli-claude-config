# Plan: SW-53770 — Commercial Excel validation + audit-doc tests: rebuild on shared infrastructure extracted from the HO tests

| Ticket | Title |
|---|---|
| [SW-53770](https://swyfft.myjetbrains.com/youtrack/issue/SW-53770) | Commercial Excel validation + audit-doc tests: rebuild on shared infrastructure extracted from the HO tests |

**Plan type: Feature** (per-commit cycle; see "HARD STOP sequence" below).

> **Execute steps in order. Never skip ahead, reorder, or deviate. If you encounter anything that prevents adherence to this plan, HARD STOP — explain the blocker and wait for instructions.**

> ### HARD RULE — never parse a rater `.xlsm` yourself
> To read anything out of a rater workbook — Versions-sheet values, named ranges, input options,
> factor tables, fees — there are exactly TWO sanctioned sources:
> 1. **HO:** the pre-dumped baselines under `Swyfft.Services.Excel.IntegrationTests/ExpectedResults/`.
> 2. **Any rater without a baseline (Commercial, or a brand-new file):** the `DumpRater` / `ReadExcel`
>    console task (`WorkbookJsonDump.cs`).
>
> **NEVER open the `.xlsm` yourself** — not with a Python/zip/XML parser, not by unzipping the OOXML
> and reading `sheetN.xml` / `sharedStrings.xml`, not with any ad-hoc script. Hand-rolled Excel
> parsing is banned: it silently mishandles shared strings, cached-vs-formula values, and
> defined-name scoping, and it reinvents tooling the repo already owns. When the sanctioned tool is
> heavyweight (DumpRater needs a console build/run), that cost is the price of correctness — pay it.
> "It was faster to parse it myself" is never a justification.

(Included because the sentinel-check feasibility checkpoint reads Commercial rater sheet layouts. Commercial has no baselines, so `DumpRater` is the only sanctioned read.)

## The AC (settled in the planning session — the ticket's original bug list was symptoms of this)

- **A. Shared infrastructure, HO shape as canon.** Commercial validation tests run on the same infrastructure HO's do. Wherever HO and CO have parallel machinery (validation test base, rater-service dispatcher, audit tests), a shared product-neutral base ALWAYS exists — extracted from HO's proven shape. CO's current test shape is the thing being refactored away; it is kept only where truly too hard to share.
- **B. Tests and the audit doc flow run the same code.** One dispatcher (on a shared dispatcher base) resolves the same concrete rater service for both the audit job and the validation tests, like HO. The audit doc flow is a validation flow over production data (never changes any quote/policy premium) — the repo docs misframing it as a peer production system were fixed during planning.
- **C. Every test actually runs against the config it claims to — by construction.** Quotes are created directly on the config under test and setup-asserted on every creation. The infra makes the old failure (claiming one config, rating another) impossible. That alone delivers the ticket.
- **D. Exposing latent bugs is expected and is the point.** Default handling: skip-override on the broken class + explicit `TODO (SW-53770 follow-up):` marker. Inline fix only when trivial.
- **E. MVP discipline.** DRY via OOP; long-term goal is CO stable like HO. Commercial captured-assert baselines shipped as their own PR (Part 3), which also retired the opt-in: the capture is now a `[Fact]` on the shared base that both products inherit.
- **F. Delivered as several PRs, each one green** (skips + TODOs count as green). Each PR carries `Part N` in its title, which keeps `youtrack-update-on-merge.yml` from moving SW-53770, so the story stays in Develop until the last part merges. Eli calls where each part ends. Work past the final part ships as follow-up tickets.

**TODO markers name the story that will actually do the work.** `TODO (SW-53770 follow-up)` is only for work a later stage of SW-53770 performs. A gap needing anything outside this story's scope gets its own user story first, and the TODO carries that story's ID. A TODO pointing at SW-53770 for work SW-53770 will never do is a dangling marker: the story closes and the marker survives with nothing behind it.

**`SW-ELI` is the placeholder ID, and no PR ships carrying one.** Several of these gaps are expected to
land in one story rather than a story each, so the story is written once the full set is known. Until
then the TODO reads `TODO (SW-ELI): <what is broken, one line>`. `SW-ELI` matches nothing else in the
repo, so `grep -rn "SW-ELI"` finds every outstanding one. Creating the story and replacing every
`SW-ELI` is a required step before the PR is opened.

## Pre-read (subsystem orientation) — all read during planning; re-read after any compaction

- `Swyfft.Services.Excel.IntegrationTests/CLAUDE.md` + `Homeowner/CLAUDE.md` + `Commercial/CLAUDE.md`
- `Swyfft.Services.Excel/CLAUDE.md` + `Swyfft.Services.Excel/Commercial/CLAUDE.md`
- `Swyfft.Services.Excel/Homeowner/ByPeril/Rater/CLAUDE.md` + `audit-and-debugging.md`
- `Swyfft.Seeding/ExcelLoaders/ByPeril/CLAUDE.md`
- `Swyfft.Services/Common/Commercial/CLAUDE.md`
- `Swyfft.Services.IntegrationTests/CLAUDE.md`, `Swyfft.TestUtilities/CLAUDE.md`
- `Swyfft.Console/CLAUDE.md`, `Swyfft.Common/SetDefinitions/CLAUDE.md`

## Step 0a — ticket stage

Done during planning: SW-53770 moved Ready for Dev → Develop; title/description rewritten to the session AC (both approved by Eli).

## Step 0b — branch (FIRST execution step)

`/create-branch`: `feature/ek/20260818_SW-53770_co-validation-audit-infra`, push with tracking (`git push -u origin <branch>`), verify `git branch -vv`.

The three AGENTS.md doc edits already applied to the working tree ride commit 1:
- `Swyfft.Seeding/ExcelLoaders/ByPeril/AGENTS.md` (audit = validation flow, premium generators named)
- `Swyfft.Services.Excel.IntegrationTests/Homeowner/AGENTS.md` (audit flags, never changes premium)
- `Swyfft.Services.Excel/Homeowner/ByPeril/Rater/audit-and-debugging.md` (validation-flow sentence)

## HARD STOP sequence (Feature type, applied per chunk of work)

For EACH chunk of work:
1. Make the stage's code changes.
2. Comment + ClosedSet self-audit (see Verification § "Code-complete self-audit").
3. **HARD STOP — code-complete.** Do not print the diff (Eli reviews in GitHub Desktop). Wait for approval before running tests.
4. Run the stage's green bar (see each stage). **HARD STOP — report results**, wait for approval.
5. Commit on approval (`SW-53770: <summary>`, message drafted for Eli first). Push only when Eli says.
Deviations, build failures, unexpected test failures: HARD STOP and explain (Gate 1.5). Skip-override + TODO decisions get reported at the test-results stop.

---

# Research record (planning-time snapshot of `development` before Part 1 — historical; where it disagrees with the Delivered / as-built sections, those win. Do not re-research after compaction)

## Test-infra facts

**HO chain:** `ByPerilValidationTestBase` (Swyfft.Services.Excel.IntegrationTests/Homeowner/ByPerilValidationTestBase.cs, 1390 lines) → `HomeownerRaterValidationTestBase` → `HomeownerExcelIntegrationTestBase` → `IntegrationTestBase`. One leaf per (state, carrier, ratingType) group. Key members to hoist into the shared base:
- `GetConfigsForGroup` (l.372-411): all configs for the group via `HomeownerStateConfig.GetAllValues()` filter; ≤5 → all; else oldest + midpoint + 3 newest + `AlwaysIncludedConfigs`.
- `RunTestForAllConfigs` (l.458-490): fresh `WorkbookInfo` per config (cross-config stale-cell prevention, see its remarks), per-config failure aggregation via `ByPerilExcelTestHelpers.ReportConfigFailures`, `SaveFailureWorkbook` (l.348-360).
- `ValidateElementOptionsForConfig` (l.1150-1183): 12 iterations, per-index aggregation.
- `PatchElementValues` (l.1189-1294): dynamic values from `GetDynamicElementValues` + `ElementTestValues` overrides + `ElementCombinationTestValues` mixed-radix walk + `ManualPremiumAdjustments`; **renewal term = index** (l.1261-1272, fake IMS `PolicyTerm`, then asserts `ratedModel.RenewalTerm == renewalTerm`); greppable `EACH_ELEMENT_OPTION_INPUTS` log.
- Sentinel machinery (l.802-932): `WriteSentinelsAndCollectUnwritten` scans a header-labeled column (`FindColumnHeader` rows 1-5, cols A-Z; `ColumnStartOverrides` for non-standard layouts); `InputSheet_AllInputCellsShouldBeWrittenByCSharp` (every unwritten cell fails), `VersionsSheet_AllVersionCellsShouldBeWrittenByCSharp` (non-V1 unwritten fails + Excel-default vs `config.LookupVersions.GetVersion` mismatch check).
- `RaterFileContents_ShouldMatchCaptured` (l.1311-1388): `[Trait(TestGroup, CapturedAssertTests)]`; canonical inputs via `SetExcelValues(evaluateFormulas: false)`, per-sheet `WorkbookJsonDump.SerializeSheet(omitFormulaValues: true)` + `_NamedRanges`, `SheetsExcludedFromCapture` = Input sheet.
- HO tests resolve the production dispatcher: ctor gets `ByPerilHomeownerExcelRaterService` via `Resolve<IByPerilHomeownerExcelRaterService>` then `GetConcreteRaterService(GroupState, GroupRatingType, GroupCarrier)` (l.227-230).

**CO chain:** `CommercialByPerilRaterValidationTestBase<TRaterService>` (Commercial/CommercialByPerilRaterValidationTestBase.cs) → `CommercialExistingQuoteIntegrationTestBase` (file: `CommerciaExistingQuotelIntegrationTestBase.cs`, typo'd name) → `CommercialIntegrationTestBase` → `IntegrationTestBase`. One hand-written leaf per config version, each with its own address key.
- Ctor (l.24-38): `ExcelSemaphore.Wait`, `RegisterSingleton<TRaterService>()` (test-only subclass instantiation), `FakeCommercialRiskProcessor`, registers `ICommercialEAndSExcelRaterService → CommercialEAndSExcelRaterService` base.
- `RunAndCheck` (l.46-215): one address (`AddressKey`), premium comparison incl. Commercial-specific totals; failure workbook saved to `{temp}\Swyfft\CommercialValidationTests\`.
- `EachElementOption` (l.278-298): `[Theory]` indices 0-18; `PatchModifiers` (l.322-340 base + per-leaf adds) with `PatchModifier<T>`/`CombinedPatchModifier` mixed-radix (l.348-369). E&S base adds many more modifiers (CommercialEAndSByPerilRaterValidationTestBase.cs). No renewal-term axis, no dynamic value discovery.
- One-off tests to SORT during rebuild (Eli: one-offs go to their child classes; do NOT conflate with EachElementOption variations): `MaxBuildingValue`, `ClaimHistory_FirstClaimIsFree`, `ClaimHistoryLookup_VerifyExcelRaterCanHandleFailure` (base, l.371-433), `PatchQuote_FslsoServiceFeeBoundary_ShouldBeExpected` (`CommercialEAndSByPerilRaterValidationFL.cs:68-84`), `AssertNonHurricaneWindAndHailAreZeroWhenExcluded` hook (l.231-251).
- Leaf inventory: FL Topa V6/V8/V9/V10/V12/V13/V14/V15/V16/V17 (older tagged `Legacy`), FLCbs, FLHsic, FLQbe, LA Topa/Hsic/QbeV1, TX Topa/Hsic/QbeV1, AL, MS, NYQbeV1, NCQbeV1, NJQbeV1, SCQbeV1, `...WithLwdAndWideDeductibles` mid-layers (FL/LA/TX); Admitted: IL/NY/WA on `CommercialAdmittedByPerilRaterValidationTestBase`. Unpinned-at-creation today: AL, MS, NCQbeV1, NJQbeV1, SCQbeV1 (verified by grep).
- `CommercialStateConfig` implements `IStateConfig`; keyed by `QuoteDefinitionId` (`Swyfft.Services/Common/Commercial/AGENTS.md`).

## Pinning / creation facts

- `SetCommercialQuoteDefinitionGetter(getter, applyAtQuoteCreation)` (`CommercialIntegrationTestBase.cs:162-174`); `OverriddenCommercialQuoteDefinitionRepository` (Swyfft.TestUtilities/Mocks/): `ApplyGetterAtQuoteCreation` flag (l.22), overrides `GetQuoteDefinitionsByStateCarrierRating` (l.27-49) + `GetQuoteDefinitionById`; does NOT override `TryGetQuoteDefinitionsByStateCarrierRating` — the untested hypothesis for the old AL V1→V2 landing bug (moot once the mechanism dies; no diagnosis owed, closed as "mechanism removed").
- Setup assert already in `CommercialIntegrationTestBase.RunTest` (l.286-298): pinned config must match `CarrierCode` and the created quote's config. The shared base carries this assert on EVERY creation.
- **Direct creation** (the new pattern): `CommercialQuoteGenerator.CreateCommercialQuote(addressKey, stateConfig)` (Swyfft.TestUtilities/Commercial/CommercialQuoteGenerator.cs:220-227) → `AssignQuoteDefinition` sets `qtx.QuoteDefinition = stateConfig.ToCommercialQuoteDefinition()` (l.155-159). HO equivalent: `CreateDefaultQuoteFromAddress(stateConfigNameOverride: config)`.
- Carrier-code latch bug: `CommercialIntegrationTestBase` ctor passes `new(() => CarrierCode)` as `Lazy<CarrierCode?>` (l.101-108) — latches at first evaluation; mid-class carrier switches never reach the generator.
- `CommercialPurchaseServiceTestsFL` (Swyfft.Services.IntegrationTests/Commercial/Purchase/): 4 vacuous `CbsVn_to_TopaVm_ShouldMatchPremiums` (l.161-190) via `CreateQuoteWithStateConfig` (l.239-248, uses `ResetCommercialQuoteDefinitionGetter` which never governs creation + the latch); `CbsV20_ShouldBecomeTopaV4_WhenAfterCutOffDate` (l.146-158) still carries V19/TopaV3 args (copy-paste).

## Audit-doc-flow facts

- Shared base: `ExcelQuoteAuditServiceBase<TQuote,TPremiumValues>` (Swyfft.Services.Excel/ExcelQuoteAuditServiceBase.cs): `GenerateAuditDoc` = re-rate via `excelRaterService.GetExcelPremiumForQuote` → store `.xlsm` + PDF in IMS → mark `AuditDocsGeneratedOn` (before comparing) → `ComparePremium` → Success/MisMatch/Failure/Skipped. Validation flow over prod data; never changes any premium.
- Product services: `ByPerilHomeownerExcelQuoteAuditService` (tolerance max(0.05%, $1); `IsPropertyModifiedAfterBind`; description incl. QuoteDef/PriorQuoteDef), `CommercialExcelQuoteAuditService` (0.05%, no floor), `HomeownerExcelQuoteAuditService` (ByPeril-only router). Console: `GenerateHomeownerAuditDocsTask` / `GenerateCommercialAuditDocsTask` → `GenerateAuditDocsTaskBase` → `SwyfftExcelTask`.
- **The DI split (the disease):** `SwyfftExcelTask` (Swyfft.Console.Base/SwyfftExcelTask.cs:23-34) registers `ICommercialEAndSExcelRaterService → CommercialEAndSExcelRaterService` (base) — the audit runs the base for every state. The five subclasses (`CommercialEAndSExcelRaterServiceNYQbe/TXTopa/SCQbe/NJQbe/NCQbe`, all with real overrides) are instantiated ONLY by validation tests via `<TRaterService>`. NYQbe example: own `FactorNames`/`CoverageNames`/`FeeNames`, `IncludeHurricane`, no-op `SetBuildingsInput` (base writes Buildings for QBE, `CommercialEAndSExcelRaterService.cs:320-327`).
- **HO's cure (the canon):** `ByPerilHomeownerExcelRaterService` = dispatcher with `(StateCode, RatingType, CarrierCode) → Lazy<concrete service>` dictionary + `GetConcreteRaterService` (Swyfft.Services.Excel/Homeowner/ByPeril/Rater/ByPerilHomeownerExcelRaterService.cs:117-130); production audit AND tests resolve it.
- Audit test coverage today: HO `HomeownerExcelQuoteAuditServiceTests` (integration: creates quote, fabricates `EFPolicy` + `ImsQuoteGuid`, runs `GenerateAuditDocs`, asserts result + marking incl. prod/non-prod IMS-missing split). Commercial: unit tests only (`CommercialExcelQuoteAuditServiceUnitTests`) + manual `CommercialExcelQuoteAuditDiagnosticTests` (shared diagnostic base already exists: `ExcelQuoteAuditDiagnosticTestBase`).

---

# Delivered (historical record; the as-built sections below are the authority)

Shared types (all landed): `ExcelRaterValidationTestBase` (shared validation base), `ExcelRaterServiceDispatcherBase` (shared dispatcher base), `CommercialExcelRaterServiceDispatcher`, `ExcelQuoteAuditServiceTestBase` (shared audit-test base), `CommercialRaterValidationTestBase` (CO validation base on the shared base). Shared types live product-neutral in their projects (`Swyfft.Services.Excel.IntegrationTests` root area; dispatcher base in `Swyfft.Services.Excel`).

- **Shared validation base** extracted from HO (config discovery/sampling over `IStateConfig`, `RunTestForAllConfigs`, creation setup-assert contract, `EachElementOption` engine, sentinel machinery cores, `RaterFileContents` capture hook behind an opt-in, CO off at this point; Part 3 retired the opt-in). HO re-parented; HO leaf classes and test names untouched.
- **Shared dispatcher** extracted from HO's; Commercial dispatcher over all 19 rater services; the audit job and the tests resolve it.
- **Shared audit-test base** + the first Commercial audit-doc end-to-end test.
- **CO validation rebuild**: one leaf per (state, carrier) incl. Admitted IL/NY/WA, HO sampling policy, direct creation + setup assert per quote, per-config leaf classes and the `<TRaterService>` generic deleted, pin mechanism deleted, `CommercialPurchaseServiceTestsFL` legs rewritten on direct creation.
- **Part 1 PR #22439** shipped all of the above, fully green; merged to development 2026-08-26.
- **CO sentinel checks** (commit `67430b6ebdf`). Two `[Fact]`s on
  `CommercialRaterValidationTestBase` delegating to the shared cores, with
  `SkipIfStateRetired()` first. What the checks found and how each finding was closed:
  - **Input writes added** where the rater has the defined name: `WritesWindMitigationTable` on nine
    services, new `WritesNamedStormDeductible` flag on `CommercialEAndSExcelRaterService` (true on
    the FL ISO chain, QBE NJ, QBE NY; SC already wrote it via its own setter),
    `WritesWindConstructionProgram` on AL.
  - **Version mappings added**: `WHDeductibleVersion` on `CommercialEAndSIsoRaterExcelRaterServiceFL`
    (closed the last `SW-53770 follow-up` TODO) and `WallsInCoverage` on LA. Both scenario-1: the
    lookup already named the rater's value, only the cell write was missing.
  - **`ExcludedInputLabels`** for cells with no defined name that no formula reads (verified by
    full-workbook `DumpRater` dumps): the territory trio on every rater outside the FL unified pair,
    `Named Storm Deductible` on FL Topa/LA/TX. Label constants on `CommercialEAndSValidationTestBase`
    use `ByPerilName.X.DisplayName` — `Value` is the C# member name, `DisplayName` is the sheet label.
  - **SW-53916 run-off Topa**: `RoofSystemsPaymentSchedule` excluded on the three Topa leaves
    (`ExcludedInputLabels` + `ExcludedVersionMismatchFactors`, the mechanism HO's Topa leaves use).
    Firm decision, no TODO.
  - Settled negative: `WritesMinimumPremiumInputs` on QBE NJ/SC, Topa AL, Dorchester MS did NOT
    surface — no minimum-premium input goes unwritten there.
  - Suite fully green: 149 total, 0 failed, 110 passed, 39 skipped (retired IL/NY/WA).
- **Wind/hail exclusion assert promoted to the shared comparison** (commit `4dd504f93a2`, scoped by
  `f7118e17bba`). `AssertNonHurricaneWindAndHailAreZeroWhenExcluded` moved out of three leaf
  overrides (QBE FL/NC/NY) into `CompareAdditionalPremiums`, so every leaf asserts it by default.
  Two configs legitimately keep wind premium under exclusion: `NJ.Qbe.ByPeril.EAndS.V1` and
  `TX.TOPA.ByPeril.EAndS.V2`. `CommercialEAndSByPerilPremiumGeneratorCombinedDeductible` and the TX
  Topa generator rate a quote as `CoverageType.Included` while the lookup holds
  `ByPerilName.WindHailExclusion` at `SwyfftVersion.V1` (gate shipped in #21881), and the rater
  agrees. **The trap, found by the pre-PR review:** keying the skip on that lookup version alone
  disabled the assert far wider than intended, because `GetVersion` returns V1 both for a factor at
  its version-1 vintage and for a factor a lookup never mentions. NC/NY/SC/FL QBE lookups never
  mention it, and those generators zero wind/hail regardless, so the assert silently stopped running
  where development had run it. Fix: new virtual `GeneratorKeepsWindPremiumOnV1Exclusion`, default
  false so the assert runs, true only on `CommercialEAndSValidationTestsTopaTX` and
  `CommercialEAndSValidationTestsQbeNJ`. The version check stays alongside the flag because TX Topa
  spans both vintages: its V6+ configs still assert, and a future NJ config bumping the factor
  re-arms automatically.
- **Homeowner-only helpers nested** (commit `dce82331184`). `CoverageBCDV1Skip` and
  `GetDynamicElementValues` moved verbatim into a nested `static class Homeowner` inside
  `ByPerilExcelTestHelpers`; 16 reference sites repointed. A separate-file variant was tried first
  and reverted on Eli's call. The file carries no Commercial-specific members, so no sibling
  `Commercial` nest exists. Green bar was compilation only, since the move is a compile-time
  relocation with no reflection or string lookup of either member.
- **Part 2 PR #22491** ships the three items above, branch tip `2697730f7ff`. Title carries
  `Part 2` so the merge workflow leaves SW-53770 in Develop. Copilot review raised one comment,
  two consecutive `<summary>` blocks on `GeneratorKeepsWindPremiumOnV1Exclusion`; the real defect
  underneath was that inserting that property between the SW-54466 docstring and the method it
  documents left the docstring on the property and the assert with none. Docstring moved back to
  the assert (`2697730f7ff`); zero unresolved threads.
- **CO captured-assert baselines** (commits `497f9823085`, `843614866b6`). 620 baseline files,
  133 MB, across all 19 CO leaves. The opt-in was retired rather than switched on: the capture core
  became the `[Fact]` itself on `ExcelRaterValidationTestBase`, Homeowner's leaf-side declaration
  was deleted, and `virtual` was dropped so no leaf can override the check away. `WorkbookJsonDump`'s
  docstring named `ByPerilValidationTestBase` as its captured-assert caller, stale since Part 1
  moved the capture to the shared base; it now names the shared base.
  - **Eli's ruling, overriding this plan's earlier text: the three retired Admitted leaves
    (ClearBlue IL, NY, WA) ARE baselined.** The capture dumps the rater workbook and compares no
    premium, so whether Swyfft still writes the state is irrelevant to it. There is no
    `SkipIfStateRetired()` on this fact, and the gate could not live there anyway since it is
    Commercial-specific while the fact is product-neutral. Known consequence, accepted: deleting a
    retired state's config or `.xlsm` later fails this test while its neighbours skip.
  - Generation 19/19. A second run with `UPDATE_TEST_EXPECTED_RESULTS` off also 19/19 with no file
    rewritten, so the baselines reproduce rather than recording one run's state. HO's 2,104
    baselines unmodified across both runs. All 620 files well-formed JSON, no Excel error token
    outside `_NamedRanges`, whose entries are pre-existing (27 of 38 HO baselines carry them; CO's
    four are Excel Solver leftovers on `Base_Rates`).
  - **Part 3 PR #22504**, base the Part 2 branch rather than `development`, so its diff carries
    only Part 3. Registered as GitHub **stack #22505** (#22491 bottom, #22504 top) via
    `gh stack link 22491 22504`, the `gh-stack` extension's no-local-tracking path, which leaves
    branches and bases alone. Use the extension for any future stacked PR here: basing a PR on
    another branch by hand is not a stack, and only a real stack gets the stack UI, bottom-up
    merge, and auto-retarget. Consequence: merging #22504 merges #22491 beneath it. To land Part 2
    alone, merge #22491 and #22504 rebases onto `development` on its own.

# Remaining work, ranked

Work proceeds in priority order; Eli may stop at any point. Each shipped chunk is a `Part N` PR of
[SW-53770](https://swyfft.myjetbrains.com/youtrack/issue/SW-53770).

Two items remain, and each gets its own PR (Eli, 2026-08-28). Item 1 is Part 4, in progress on
branch `feature/ek/20260828_SW-53770_co-validation-part4` (created 2026-08-28 off Part 3's tip; a
third stacked PR, so `gh stack link 22504 <new PR#>` when the PR goes up).
Item 2 ships in a later part; it is not in Part 4's scope.

**`development` was merged up the whole stack on 2026-08-28**, bottom first, since merging it into
Part 4 alone would have put 309 unrelated commits into Part 4's diff against its Part 3 base. All
three merges were conflict-free and all three branches are pushed: Part 2 at `069a1033653`, Part 3
at `d3d717dd891`, Part 4 at `e3a295ee68a`. Any future `development` merge goes up the stack the same
way while #22491 and #22504 are open. Part 4's tip is now `30d7ea4da1e`, pushed.

**A `development` merge can leave the local DB behind the code.** After the 2026-08-28 merge the
whole Commercial suite failed, 129 of 168, every one of them
`SqlException: Invalid column name 'BetterviewNowByAddressResponseId'` out of `EFCommercialQuote.Upsert`.
Migration `20260820140119_AddCommercialDefaultsApiSupport` adds that column, and six later migrations
had also not been applied. A full seed fixed it. Read a wall of identical SQL failures as a stale
schema before reading it as a code defect.

**Part 4's remaining scope, in order:** get both suites green (see the working notes); then fold
`ByPerilExcelTestConstants` into the test class hierarchy and delete the file. Done already: the
`PatchModifiers` deletion (commit `c24a3f9be9a`), the inspection-fee failure kind, the
wind-deductible one, and step 2's `ElementTestValues` conversion (commit `c99b919bef9`, which also
hoisted the offered-element gate into the shared engine).

**The `SW-ELI` placeholders are all resolved.** Four bugs were filed 2026-08-31 and every TODO in the
code now carries a real ID: SW-55583, SW-55584, SW-55585 and SW-55586. `grep -rn "SW-ELI"` comes back
empty, so the PR gate on it is satisfied. Any exclusion added from here follows the same rule:
placeholder first, real ticket before the PR.

1. **CO dynamic value discovery.** Outline settled with Eli 2026-08-28; the earlier "feasibility
   checkpoint" framing is superseded. Step 1 of 2 has shipped.

   **THE REQUIREMENT, ruled by Eli twice and binding on every step below: Homeowner's pre-change
   `EachElementOption` behavior IS the specification, and it becomes the behavior of both products,
   full stop.** No part of HO's behavior may be reclassified as incidental and changed during the
   hoist. Abstract methods exist ONLY where Commercial genuinely cannot execute HO's code because
   its element mechanics differ, and each Commercial implementation does the same thing HO's does,
   expressed through Commercial's mechanism. Any place Commercial behaves differently for any other
   reason is a bug in the new code, and the fix is always to make Commercial match Homeowner, never
   to let the shared code accommodate a difference.
   - **Step 1, delivered** (commit `ee654f0947a`, full-solution build green, no tests run yet).
     HO's engine moved from `ByPerilValidationTestBase.PatchElementValues` into
     `ExcelRaterValidationTestBase`: `ElementTestValues`, `ElementCombinationTestValues`,
     `ElementTestValuesSkipVersions`, `ApplyVersionSpecificOverrides`, `TestedElementValues`,
     `ManualPremiumAdjustments`, and the per-index walk (dynamic values, overrides, skip-versions,
     the modulo pick, the mixed-radix combination walk, renewal term = index, the
     `EACH_ELEMENT_OPTION_INPUTS` log). Four abstracts, each a point where Commercial cannot run
     HO's code: `GetDynamicElementValues` (CO elements are computed per quote by
     `ICommercialDefaultElementsHelper`, not stored on it), `ApplySelectedElementValues` (CO values
     ride quote columns, reached by the name-based reflection hop production uses at
     `CommercialQuotePatchRequest.cs:44-48`), `PrepareRenewalTerm` (CO's patch pipeline reloads from
     the DB, so the fabricated policy must be persisted), and `RateQuote`. Apply and rate are split
     so the engine emits the log between them, at HO's exact position. CO's `RateQuote` asserts the
     term via `GetPolicyTermFailOpenOnImsDown`, HO's guard through CO's mechanism. The element
     filter moved to `ByPerilExcelTestHelpers` with the exclusion list as a parameter;
     `ByPerilExcelTestConstants` keeps only HO's list. CO runs the sweep with an EMPTY exclusion
     list and no overrides or combinations, leaving its `PatchModifiers` lists in place but unread
     (deleted later, commit `c24a3f9be9a`).
   - **Step 1b, delivered** (commit `338cd6cea61`, Commercial suite 12 failed / 117 passed / 39
     skipped, zero baseline diff; artifact
     `artifacts/tests/…filter-trait-TestGroup=Commercial_inspection-write-from-term1_20260828-1610.txt`).
     The sweep is now sourced from the generators. Four things landed together:
     - **CO's exclusion list, 18 elements** on `CommercialRaterValidationTestBase.UnratedElements`,
       built from a throwaway reflection diagnostic run on a scratch branch, not by guessing. They
       are elements the generators offer that no rater rates: nine `Override*` risk flags plus
       `ManualDecline` (risk selection, which these tests replace with `FakeCommercialRiskProcessor`),
       three claim elements (`Claim_Type`, `Claim_IsFullyRepaired`, `LossHistoryClaimType`, all in
       `CommercialElementHelper.ExcludedElementNames` for having no quote column), plus `Eifs`,
       `FireExtinguishers`, `RoofCoverage`, `FloodZone`, `HurricaneDamageConfirmation`.
       `DistanceToCoast` is NOT on the list and must not be added: it is `ToAdminInfoElement`, so
       the type/access filter drops it before the list is consulted, exactly as HO relies on
       `ToHiddenElement` for the same element.
     - **Three combination groups**, identical on all 16 leaves:
       `EnableExtraAopDeductibleOptions`/`EquipmentBreakdownCoverage`/`Deductible`,
       `SprinklerSystem`/`FireProtectiveDevices`, and
       `TerrorismCoverage`/`PropertyBroadeningFormCoverage`/`PropertyBroadeningFormChoice`.
     - **`PrepareRenewalTerm` no longer fabricates an `EFPolicy`.** The policy set `Quote.PolicyId`,
       which is what `IsPurchased()` reads and `VerifyNotPurchasedOrFailActor` rejects on a Patch
       workflow, so every iteration after index 0 failed before it rated. `GetPolicyTerm` reads only
       `ImsQuoteGuid`, so the guid alone is enough. HO never hit this because it patches in RAM.
     - **The inspection fee.** The rater has no notion of the every-third-year cadence, so C# writes
       the charged fee, or zero on an off year, on every renewal term. New business is left alone so
       the rater still prices it from its own version table and C# is compared against it; the term-0
       test is that the charged fee is named `InspectionFee`, which `CommercialQuoteFees{ST}` charges
       at `PolicyAge - 1 == 0` only. `InspectionFeeEntry` makes the readback name follow the quote,
       since one rater cell serves both names. `ZeroesInspectionFeeWhenAbsent` and LA's separate
       zero-fee list are gone, folded into the shared base.
     - **The target-premium row is compared at term 0 only.** `CreateTargetQuoteIfNullOptionActor`
       nulls `TargetAnnualPremium` on renewal (SW-17628), so the backed-out target is meaningless on
       a renewal term, and the raters disagree with each other there anyway: FL deducts the charged
       fee, AL/MS/LA/TX/NJ/SC deduct their standard fee every term, NY/NC deduct nothing.
   - **The inspection-fee failure kind, diagnosed and fixed.** A rater totals its fees twice, once
     for the initial premium and once for the final, and each total has its own inspection cell.
     Only the final one carries the `InspectionFee` defined name, so the write that step 1b added
     reached the final total and left the initial one pricing an inspection out of the rater's own
     fee table every term. `InitialPremiumBeforeTax` reads the initial total, so on an off-year
     renewal the rater came out exactly one inspection fee above C#. Verified by tracing two saved
     workbooks: on LA Hsic the rater read 62818 against C#'s 62518 with `InitialInspectionFee` at
     `Rating_Algorithm!$B$55` holding `Fees!$C$5`, and on QBE TX an index that does charge the fee
     agreed on both totals at 24902. The gap is always the state's inspection amount for that
     config's version, which is why it showed up as 300, 250, 125 and 299: those are the switch arms
     in `CommercialQuoteFeesLA` and `CommercialQuoteFeesTX`.
     - **The fix**, Eli's call between writing the cell and skipping the comparison on renewals:
       `SetInspectionFee` writes the charged fee, or zero, into both cells. New constant
       `ByPerilCellNames.InitialInspectionFee`.
     - **Ten raters carry `InitialInspectionFee`** — MS Dorchester, AL Topa, LA Topa/Hsic/Qbe,
       TX Topa/Hsic/Qbe, NJ Qbe, SC Qbe — which is exactly the set that failed on this row. NC Qbe,
       NY Qbe and the three FL raters carry no such name, and `SetValueIfPresent` no-ops there.
       **FL Topa's `InitialInspectionFee` resolves to `#REF!`**, a broken defined name in the rater
       itself; writing through it neither threw nor moved FL Topa off green.
     - **The production audit never saw this.** `CommercialExcelQuoteAuditService.ComparePremium`
       compares only `FinalTotalPremium`, which reads `ByPerilName.FinalPremium`. That chain runs
       through the final fee total, so it always carried the C#-written value. On LA it read 62518,
       C#'s figure exactly.
   - **The wind-deductible failure kind, diagnosed and fixed** (commit `30d7ea4da1e`). The named
     storm deductible element offers 5% and 10% on QBE NC, NJ, NY and SC, all four riding
     `ConstraintCode.CommercialNamedStormDeductMin5`. The seeded
     `EFByPerilWindDeductibleByCoverageAFactors` rows for those four carry 1%, 2% and 5% only, so a
     10% quote finds no row and `.First()` throws `Sequence contains no elements` out of
     `CalculateFactorsAndRatesEAndSActor`. NC, NJ and SC surface it through the "wind deductible
     portion" lookup; NY through its own "Wind/Hail Deductible" percentage-and-building-value path.
     - **Development never fed 10%, deliberately.** `CommercialEAndSValidationTestBaseQbeIso` at
       `338cd6cea61^` narrowed the sweep to 2% and 5%: "These raters' deductible sheets carry no 10%
       wind rows." Step 1b's `PatchModifiers` deletion took the narrowing with it. Category 3 by the
       two questions: development pinned these configs and did not feed this input.
     - **The fix is a temporary exclusion, not a repair.** `ElementTestValues[HurricaneDeductible]`
       is pinned to 5% on `CommercialEAndSValidationTestBaseQbeIso`, carrying
       `TODO (SW-ELI)`. The real defect is that the element offers an option no rater prices, which
       is out of SW-53770's scope. None of the four configs is live: ids 103 NY, 104 NC, 105 NJ and
       106 SC all sit at the `1/1/3000` placeholder, active in local, dev and beta only through
       `EnvironmentFilters.CommercialOverrides`.
   - **Step 1b's remaining failure shapes, none diagnosed.** Attribution below is per test element
     from the TRX. The console log interleaves parallel output and misattributes.

     | Row | Where |
     |---|---|
     | `GlCoverage`, rater exactly $1 high | `HadronTX`, `QbeTX`, `TopaTX` |
     | `HiredNonOwnedAutoCoverage`, C# 0 against the rater's 140 | `QbeNC`, `QbeNY`, `QbeSC` |
   - **The `PatchModifiers` deletion, delivered** (commit `c24a3f9be9a`, 16 files, 792 deletions,
     zero insertions, full-solution build green). Step 1b left every `GetPatchModifiers` override
     reachable only from its own base chain, so the whole mechanism went: the `IPatchModifier`,
     `PatchModifier<T>` and `CombinedPatchModifier` types (`Commercial/CommercialPatchModifiers.cs`,
     file deleted), the abstract and `GetCommonPatchModifiers`, the fourteen overrides, the
     modifier-index constants a leaf used to replace an entry by position, the eleven
     modifier-factory helpers on the E and S base, and `IsAtOrAfter` and `IsTableVersionPastV1`,
     which only those overrides called. A sweep of every non-override, non-`[Fact]`/`[Theory]`
     member in the Commercial tree and the shared test bases found nothing else unreferenced.
     Behavior is unchanged and the twelve failing leaves fail identically.
   - **Step 2, not started: the `ElementTestValues` conversion.** The one bucket of HO's shape that
     Commercial still lacks. The deleted lists are the source material, recoverable with
     `git show 338cd6cea61 -- <file>`. The four/five split below is measured against the
     `DYNAMIC_ALL` lines of the step-1b diagnostic
     (`artifacts/tests/co-element-diag-full_20260828-1220.txt`, 32 config lines), not inferred from
     element types.
     - **Four of the nine base entries were choice-backed and the sweep already produces them**, so
       they needed no replacement: `ConstructionType` and `EquipmentBreakdownCoverage` on all 32
       config lines, `EmployeeBenefitsCoverage` and `HiredNonOwnedAutoCoverage` on 29. The three
       lines missing the latter two get a verdict during the conversion: either the config genuinely
       lacks the element, or it needs an override.
     - **Five appear on no `DYNAMIC_ALL` line, so nothing feeds them today** and each becomes an
       `ElementTestValues` entry with literal values, HO's Irpm/NumStories pattern: `BuildingValue`,
       `BusinessIncomeLimit`, `BusinessPersonalPropertyLimit`, `NumberOfStories`,
       `AdditionalPropertyPremium`.
     - **Each leaf's own appended modifiers sort the same way**, plus a third case the base had none
       of: an override kept because the rater's ratable set is narrower than the config's options
       (SW-53889 wide hurricane deductible, QBE FL's V1 roof composition, SC's two unratable
       constructions, crime-without-declined).
     - The index-replacement constants and `IsTableVersionPastV1` gates are expected to collapse into
       per-config element presence/choices — verified per entry, kept as overrides where they don't.

     Open, no decision made (2026-08-28): three rater inputs are written to the Input sheet and
     varied by nothing. `NumberOfBuildings` is `ToNumberElement`, so it has no `DefaultChoices` to
     enumerate; `ProtectionClass` and `DistanceToCoast` are `ToAdminInfoElement`, so the type/access
     filter drops them. `NumberOfBuildings` and `ProtectionClass` have writable patch-request
     properties; `DistanceToCoast` has none and is set from the SAR geo lookup
     (`ApplySarResultActor`). The list came from a static grep of `quote.<Member>` reads in
     `CommercialEAndSExcelRaterService` minus the measured modifier-covered set, so it is
     corroborated per element but not proven complete. What to do about any of them is undecided;
     ranked item 2 is the check that establishes the real list.
   - **Coverage effect:** CO flips to HO's blacklist model — every choice-bearing element the
     config's generator offers is swept unless excluded.
   - **Eli's decisions (2026-08-28):** the renewal-term axis (term = index) moves with the engine and
     runs for CO too, since the hoist is THE SAME CODE for both products with nothing optional.
     Iteration counts stay per-product as today (HO 12, CO 19).
   - *Green bar:* full Commercial suite; HO ByPeril suite (the engine moves under it); zero HO
     baseline diff; per-leaf old-vs-new sweep-value parity diff, reviewed, not committed.

2. **Input-coverage sentinel: every Input-sheet cell must be exercised by the sweep.** Its own PR,
   after Part 4 merges (Eli, 2026-08-28). Not in Part 4's scope. The two sentinel checks that exist prove
   every Input cell and every Versions cell is *written* by C#. Neither proves any of them is ever
   *varied*, so a rater input can sit at its create-time value through all 19 iterations and every
   test still passes. This check closes that gap, and it is what turns the unswept-input list from
   a grep result into something measured on every run.

   - **Where:** `ExcelRaterValidationTestBase`, so Homeowner and Commercial both get it, beside the
     two existing sentinel checks.
   - **Snapshots ride the existing sweep**, no separate run: the sweep already patches and
     populates the workbook once per index, so each iteration records the Input sheet's data column
     into a per-config map of label to the set of values seen. No extra patches, no added runtime.
   - **The assertion:** after a config's last index, any labeled cell whose set holds one distinct
     value is an input nothing drives. Fail listing them per config, aggregated like the other
     checks.
   - **The allow-list is virtual and EMPTY.** Everything flagged is fixed by making the sweep vary
     it. An entry earns its place only for an input no test can drive at all, and only with a
     verified reason recorded beside it. Pre-seeding an entry inverts the point of the check.
   - **Reuses** the header-finding and label-column logic of the existing checks (`FindColumnHeader`,
     `ColumnStartOverrides`) and the same `ExcludedInputLabels` for cells no formula reads.
   - **Expected first findings on Commercial:** `NumberOfBuildings`, `ProtectionClass`,
     `DistanceToCoast`, which a static grep predicted. The check confirms or corrects that list;
     the grep was never verified complete.
   - **Homeowner findings are unknown and likely a backlog**, which is why this is last rather than
     mixed into the conversion.

## Working notes for Part 4's remaining scope

**Start here after a compact.** The first bullet is the first action. Everything after it is
ordered by "Remaining work, ranked" above.

> **THE GOVERNING PRINCIPLE, and the one to reason from before anything else: the Commercial suite
> passed on `development`. The only thing this branch changed is the set of element values the sweep
> iterates over.** Every remaining failure therefore traces to a value the sweep now feeds that
> development never fed, and the temporary fix always lies in the element values, not in a tolerance,
> a skipped row, or a new exclusion hook. Find the value development did not feed before proposing
> anything. Do not reason forward from a premium mechanism to a guess about which element is
> responsible; compare the failing workbook's Input sheet against development's modifier lists and
> let the difference name the element.

- **FIRST ACTION: run BOTH suites.** Commit `c99b919bef9` changed the shared engine and Homeowner's
  apply, so Homeowner is in scope now, not just Commercial. Both projects are built as of that
  commit, so if nothing has changed on disk since, run them in parallel with `-NoBuild`; if anything
  has, let the first run build and pass `-NoBuild` only to the second.

  ```
  Run-DotnetTest.ps1 -TicketFolder SW-53770-co-excel-validation-audit-infra-rebuild
    -Project Swyfft.Services.Excel.IntegrationTests -FilterTrait "TestGroup=Commercial" -IsCommercial

  Run-DotnetTest.ps1 -TicketFolder SW-53770-co-excel-validation-audit-infra-rebuild
    -Project Swyfft.Services.Excel.IntegrationTests -FilterTrait "TestGroup=ByPerilTests"
  ```

  Commercial is roughly 14 minutes, Homeowner longer. Background both and do not poll. **Per-test
  attribution comes from the TRX, never the console log**, which interleaves parallel output and
  misattributes. The TRX can land under
  `Swyfft.Services.Excel.IntegrationTests/Commercial/EandS/TestResults/` rather than the repo-root
  `TestResults/`; the wrapper's own output names the path it wrote.

  Then `git status` on `Swyfft.Services.Excel.IntegrationTests/ExpectedResults/` must be CLEAN. A
  Homeowner baseline diff means the engine change moved Homeowner's capture, and is a HARD STOP.

- **What `c99b919bef9` changed, and what it is expected to do to the numbers.**
  - **Thirteen `ElementTestValues` entries** on `CommercialEAndSValidationTestBase`, restoring the
    rated inputs whose elements carry no choices for the sweep to enumerate, so each had been sitting
    at its create-time value for all 19 iterations while development varied every one:
    `BuildingValue`, `BusinessIncomeLimit`, `BusinessPersonalPropertyLimit`, `NumberOfStories`,
    `NumberOfUnits`, `SquareFootage`, `YearBuilt`, `RoofAge`, `IrpmTotal`, `TargetAnnualPremium`,
    `AdditionalPropertyPremium`, `AdditionalCrimePremium`, `AdditionalLiabilityPremium`. The wider
    `SquareFootage` and `NumberOfUnits` lists sit on `CommercialEAndSValidationTestBaseFL` and
    `CommercialEAndSValidationTestsQbeFL`.
  - **The offered-element gate hoisted into the engine.** Homeowner refused a selected value whose
    element the quote does not carry; Commercial did not, because the check lived inside Homeowner's
    implementation of a whole-method abstract. `PatchElementValues` now owns the whole apply: create
    the patch, drop a selection whose element the config's generators do not offer, fail loudly for a
    combination member, write, record. `ApplySelectedElementValues` is gone; the two abstracts left
    are `CreatePatch` and `WriteSelectedValue`.
  - **`DecoratePremiumComparisonFailure` is now the shared default**, so a Commercial premium failure
    finally names the element values that produced it instead of only the figures that disagreed.
  - **Expected effect on the Premium Tax failure below:** the restored `BusinessIncomeLimit` and
    `BusinessPersonalPropertyLimit` should lift the premium back over `MinimumPackagePremium`, which
    is the state the rater floors and C# does not. Unproven until the run.

- **Where the suite stood before this commit** (2026-08-31, artifact suffix
  `qbe-iso-construction-condo-exclusions_20260831-1455`): 168 total, 2 failed, 127 passed, 39
  skipped. Progression across that session: 7 failed, 6, 3, 2.

- **The four exclusions in place, each with its bug.** Every one is an `ElementTestValues` pin
  carrying a `TODO (SW-555xx)`, and each ticket names the pin its fix must remove.
  - [SW-55583](https://swyfft.myjetbrains.com/youtrack/issue/SW-55583) named storm deductible offers
    an unratable 10%. `HurricaneDeductible` pinned to 5% on `CommercialEAndSValidationTestBaseQbeIso`.
  - [SW-55584](https://swyfft.myjetbrains.com/youtrack/issue/SW-55584) TX general liability truncates
    the retail square footage, `(int)(Quote.SquareFootage / Quote.NumberOfStories.Value)`, so the
    retail class prices $1 under the rater. `BuildingType` pinned to the non-retail occupancies on
    `CommercialEAndSValidationTestBaseTX`.
  - [SW-55585](https://swyfft.myjetbrains.com/youtrack/issue/SW-55585) hired non-owned auto and
    employee benefits are charged by the rater when general liability is declined. Both pinned false
    on `CommercialEAndSValidationTestsQbeNC`, `...QbeNY` and `...QbeSC`.
  - [SW-55586](https://swyfft.myjetbrains.com/youtrack/issue/SW-55586) the SC rater cannot look up
    Fire Resistive or Modified Fire Resistive on the non-Fire perils. `ConstructionType` pinned to the
    four covered constructions on `CommercialEAndSValidationTestsQbeSC`.

- **The open failure at that point: `Premium Tax` on `QbeNC` and `QbeNY`, indices 6, 10 and 18 of
  19.** The tolerance on that row is 0.25 and the gaps run 0.72 to 4.80.

  **What the failing indices are, established from the per-index `EACH_ELEMENT_OPTION_INPUTS` lines
  in the TRX:** exactly the intersection of `ConstructionType` in {Fire Resistive, Modified Fire
  Resistive} and `FireProtectiveDevices` in {Direct, Central}. Cheapest construction plus the best
  fire-alarm credit, together, and nothing else in the set. Development reached that same pair at its
  own indices 10 and 11 and passed, so the pair is not new coverage.

  **Verified, by tracing `CO_ES_QBE_NC_Rater_2026.08.31.06.59.09.020.xlsm` with `DumpRater`** (dumps
  in `artifacts/rater-dumps/`, `ptax-qbenc-rating.json`, `ptax-qbenc-fees.json`,
  `minpkg-qbenc-idx6-input.json`):
  - `Rating_Algorithm!B46 Initial Premium before Fees` is `MAX(SUM(B42:B44), MinimumPackagePremium)`.
    Rows 42-44 sum to 13,638; the minimum is 13,750, so the minimum binds.
  - Rows 60-62 rebuild property, liability and crime and land back at 13,638 at row 64. The minimum
    is not re-applied there.
  - Row 70 computes the taxable base as `InitialPremiumBeforeFeesTaxes + FeeTotals`, taking the
    floored 13,750 plus 375 of fees. Row 71 is `PremiumBeforeTaxes * TaxRate`, 14,125 x 0.05 = 706.25.
  - C#'s figure divided by the 0.05 rate is 13,638 + 375, so C# taxes the rebuilt premium.
  - The failing workbook holds Building Value 2,500,000 with Business Income at 50,000 and Personal
    Property at 150,000, the create-time defaults. Development set both to 66 percent of building
    value at the two indices where it hit this pair, and never combined a low limit with Fire
    Resistive at all: its limits cycled mod 7 and construction mod 6, so within 0-18 the smallest
    limit it paired with Fire Resistive or Modified Fire Resistive was 10 percent.

  **Not established:** whether restoring the two limits actually clears the minimum. That is what the
  first run answers. If the failure survives, the tax-base disagreement is a genuine defect and earns
  its own ticket then. A ticket was created and deleted once already (Eli, 2026-08-31), so do not
  re-file without the run's evidence.

  **One loose end in the trace:** on index 6 the two tax bases differ by 96, while the recorded floor
  lift is 13,750 - 13,638 = 112. Those do not reconcile, so either a recorded row is off or something
  beyond the floor differs. Worth resolving only if the failure survives the run.

- **The throwaway modifier-skip diagnostic**, which produced the thirteen-input list, is committed on
  scratch branch `scratch/ek/co-exclude-list-diagnostic` at `78028d58b41` (off `ee654f0947a`, the last
  commit carrying both the modifier lists and the sweep). It never merges. That commit's modifier
  definitions were verified identical to `origin/development`'s across all 15 modifier-carrying files.
  Its output is `artifacts/tests/modifier-skip-diag_20260831-1729_extracted.txt`, 424 rows over 16
  leaves and 32 configs. Three elements it flagged were deliberately NOT restored, per Eli: dev fed
  `OptionalSinkhole`, `RoofMaterialsPaymentSchedule` and `WindConstructionProgram`, all NoAccess or
  Info, so no agent can set them and dev was testing an unreachable state.

- **Folding in `ByPerilExcelTestConstants`.** It holds only Homeowner's explicit exclusion list. That
  list, and the exclusion members generally, belong in the test class hierarchy rather than a
  separate helper class, so fold it in and delete the file.
- **The exclusion-list diagnostic is stashed, not lost.** Written on scratch branch
  `scratch/ek/co-exclude-list-diagnostic` (off Part 4's `ee654f0947a`) and stashed there as
  `stash@{0}` "SW-53770 throwaway CO element diagnostic". It is a `[Fact]` on
  `CommercialRaterValidationTestBase` that prints, per leaf and per config, the generator-offered
  elements, the patch-request properties each `PatchModifier` writes (recovered by probing, since a
  modifier carries only a setter lambda), the gap between them, and the combination groups. Its
  output is in `artifacts/tests/co-element-diag-full_20260828-1220.txt`. Throwaway: it never ships
  on the Part 4 branch, but restoring it is cheaper than rebuilding it.

`AssertCarrierSpecificPremiums` remains as the leaf hook for checks the shared comparison cannot
reach. Only `CommercialEAndSValidationTestsQbeFL` still overrides it, for the hurricane-zeroed-at-
base-rate guard. Eli's standing note holds for any future entry: the hook is a stopgap, and an
assert that applies to every carrier belongs in the shared comparison instead.

**Skip-override convention:** override the relevant test/hook in the broken leaf (or `Assert.Skip` guard) + comment `// TODO (SW-53770 follow-up): <what is broken, one line>`. Greppable by `SW-53770 follow-up`.

---

# As-built record — shared validation base (commit 73d02c554ff; partially superseded — the CO validation rebuild as-built below reshaped `ExcelRaterValidationTestBase` to six generics and is the current authority)

Both new types live in the `Swyfft.Services.Excel.IntegrationTests` project root, namespace
`Swyfft.Services.Excel.IntegrationTests`.

**`ExcelIntegrationTestBase : IntegrationTestBase`** — carries `[Trait(Category, "ExcelTests")]`;
ctor = `DisableLoggedErrorsCheck()` + `ExcelSemaphore.Wait(TestRunId)`; `Dispose` =
`ExcelSemaphore.GcCollectAndRelease(TestRunId)`; static ctor touches `AssemblyFixture.Current`.
Children: `ExcelRaterValidationTestBase<TConfig>` and `HomeownerExcelIntegrationTestBase` (which
now holds ONLY the internal static `RegisterExcelServices(IDependencyContainer)` + a ctor call to
it; its children `HomeownerExcelQuoteAuditServiceTests` + `ByPerilAdmittedFormAuditTestsBenchmarkTX`
are untouched). A second new layer beyond the plan's named types; Eli reviewed and kept it.

**`ExcelRaterValidationTestBase<TConfig> : ExcelIntegrationTestBase where TConfig : class, IStateConfig`** —
members the CO rebuild implements or calls:
- Abstract: `GroupState`/`GroupRatingType`/`GroupCarrier`; `GetAllConfigsForGroup()` (ordered
  oldest→newest); `GetLatestConfig()`; `GetGroupWorkbookInfo()`;
  `ReleaseWorkbookAndGetFileName(wi, getFilePath, getFileContent)`; `FailureSubDirectory`;
  `PopulateWorkbookWithCanonicalInputs(wi, config)` (create quote on config +
  SetExcelValues(evaluateFormulas: false)); `GetVersionCellMappings()` returning
  `IEnumerable<(ByPerilName TableName, string CellName)>`.
- Virtual knobs: `AlwaysIncludedConfigs`, `EachElementOptionStartingFrom`, `ExcludedInputLabels`
  (default: "Policy Number"), `ExcludedVersionLabels`, `ColumnStartOverrides`,
  `ExcludedVersionMismatchFactors` (`ImmutableHashSet<ByPerilName>`), `SheetsExcludedFromCapture`
  (default: MainInput, OrdinalIgnoreCase).
- Protected machinery: `GetConfigsForGroup(startingFrom)` (HO sampling policy);
  `SaveFailureWorkbook(wi)`; `RunTestForAllConfigs(testName, configs, testAction)` (fresh workbook
  per config, `ByPerilExcelTestHelpers.ReportConfigFailures` — now generic);
  `RunItemsForConfig<TItem>(config, wi, items, itemsNoun, passLabel, failureLabel, runItem)`
  (per-item AggregateException aggregation); `static GetMixedRadixIndices(index, lengths)`;
  `RunInputSheetSentinelCheck()`; `RunVersionsSheetSentinelCheck()`; `RunRaterFileContentsCapture()`
  (capture core; Part 3 later renamed it `RaterFileContents_ShouldMatchCaptured` and made it the
  `[Fact]` itself, retiring the per-product opt-in);
  `static AssertQuoteCreatedOnConfig(expectedConfig, actualConfig)`.

HO wiring: `HomeownerRaterValidationTestBase : ExcelRaterValidationTestBase<HomeownerStateConfig>`
(ctor calls `HomeownerExcelIntegrationTestBase.RegisterExcelServices`; `RunAndCheck` asserts via
`AssertQuoteCreatedOnConfig` when `stateConfigOverride` is passed). `ByPerilValidationTestBase`
keeps all HO value sourcing + every [Fact] name; its facts delegate to the shared cores; it
implements the abstracts (`GetGroupWorkbookInfo` = `ExcelRaterService.Value.GetWorkbookInfo((GroupState, GroupCarrier))`,
`GetVersionCellMappings` = the rater service's internal method, etc.).

---

# As-built record — the shared dispatcher (commit e294e133e5e)

**`ExcelRaterServiceDispatcherBase<TQuote, TPremiumValues, TService>`**
(`Swyfft.Services.Excel/ExcelRaterServiceDispatcherBase.cs`, namespace `Swyfft.Services.Excel`; no
base class; implements `IExcelRaterServiceBase<TQuote, TPremiumValues>`; `TService : class,
IExcelRaterServiceBase<TQuote, TPremiumValues>`):
- Abstract: `IReadOnlyDictionary<(StateCode, RatingType, CarrierCode), Lazy<TService>>
  RaterServiceByStateAndRatingType`; `ByPerilRaterType GetRaterType(TQuote quote)`.
- Public: `TService GetConcreteRaterService(StateCode, RatingType, CarrierCode)` (dictionary hit →
  throw `InvalidOperationException("No Excel Rater Service registered for (…)")`; the
  `FallbackRaterService` virtual this commit added was removed later — zero references in current
  code, grep-verified 2026-08-27);
  `Task<TPremiumValues> GetExcelPremiumForQuote(quote, getFilePath, getFileContent)` (keys off
  `GetRaterType`, delegates to the resolved service).

**HO wiring:** `ByPerilHomeownerExcelRaterServiceDispatcher` (renamed from
`ByPerilHomeownerExcelRaterService` during the rebuild; class at
`Swyfft.Services.Excel/Homeowner/ByPeril/Rater/ByPerilHomeownerExcelRaterServiceDispatcher.cs:22`)
`: ExcelRaterServiceDispatcherBase<EFHomeownerQuote,
ByPerilHomeownerExcelPremiumValues, ByPerilHomeownerExcelRaterServiceBase>,
IByPerilHomeownerExcelRaterService` — 38-entry dictionary
unchanged (value type now the concrete
base, cast dropped); `GetRaterType` = `quote.ToRaterType()`; no fallback (throws). Behavior note:
the unregistered-key exception message from `GetExcelPremiumForQuote` changed to the base's
"registered for" form; nothing asserts on either message (grep-verified).

**CO wiring (current, re-verified 2026-08-27):** `CommercialExcelRaterServiceDispatcher`
(`Swyfft.Services.Excel/Commercial/CommercialExcelRaterServiceDispatcher.cs`): 19 entries — 16 E&S
(AL Topa; FL Topa/CBS/Qbe/Hadron; LA Topa/Hadron/Qbe; TX Topa/Hadron/Qbe; MS Dorchester;
NY/NC/NJ/SC Qbe) + 3 Admitted (IL/NY/WA ClearBlue); no fallback, an unmapped key throws;
`GetRaterType` = `quote.GetConfig().ToRaterType()`. The retired Admitted configs
`CAByPerilAdmittedClearBlueV1` and `NJByPerilAdmittedClearBlueV1/V2/V3` (all
`[Obsolete(RetiredMessage)]`, SW-53216) have no dispatcher entry.

**DI (current):** `ICommercialExcelRaterService` → `CommercialExcelRaterServiceDispatcher` at
`Swyfft.Console.Base/SwyfftExcelTask.cs:30` (production audit) and
`CommercialRaterValidationTestBase.cs:79` (validation tests). Both stale AGENTS.md
warnings about the old DI split were rewritten (`Swyfft.Services.Excel/Commercial/AGENTS.md`,
`Swyfft.Services.Excel.IntegrationTests/AGENTS.md`).

---

# As-built record — the shared audit-test base (commit a9a96f259b6)

**`ExcelQuoteAuditServiceTestBase : ExcelIntegrationTestBase`**
(`Swyfft.Services.Excel.IntegrationTests` project root, namespace
`Swyfft.Services.Excel.IntegrationTests`):
- Abstract: `Task<List<AuditResult>> GenerateAuditDocs(IList<QuoteId> quoteIds)` — each leaf
  forwards to its product's audit service with `AuthAdmin.Value`.
- Protected: `AttachPolicyAndImsQuoteGuid(quoteId, productLine, ratingType)` (writes
  `EFPolicy` — Bound, NonRenewed, `PolicyTermDays`=365 expiry — plus `ImsQuoteGuid` directly to
  `ctx.Quotes`; no purchase pipeline); `AssertAuditDocsMarked(quoteId, expectMarked)`;
  `RunGenerateAuditDocsSuccessTest(quoteId)` (single `AuditResult.Success` + marked).

**HO wiring:** `HomeownerExcelQuoteAuditServiceTests : ExcelQuoteAuditServiceTestBase` — ctor
registers the env mock (IsProd), calls `HomeownerExcelIntegrationTestBase.RegisterExcelServices`,
registers `IQuoteProcessor`. Dropped as redundant during the re-parent: the leaf's duplicate
`IHomeownerExcelQuoteAuditService` registration (RegisterExcelServices carries it) and the
`[Trait("Category", "ExcelTests")]` (inherited via `ExcelIntegrationTestBase`). Both test names
unchanged; the success fact now also asserts the marking (the success path marks before comparing,
so this cannot newly fail); the IMS-missing env-split theory is behavior-identical.

**CO wiring:** `CommercialExcelQuoteAuditServiceTests : ExcelQuoteAuditServiceTestBase`
(`Commercial/`) — registrations (current, read 2026-08-27, lines 23-28): `IExcelRaterService`,
`ICommercialExcelRaterService → CommercialExcelRaterServiceDispatcher`,
`ICommercialExcelQuoteAuditService`, `ICommercialRiskProcessor → FakeCommercialRiskProcessor`.
Builds its own
`CommercialQuoteGenerator` via `GetCommercialQuoteGeneratorInfo` (Topa/EAndS) — the commercial
creation machinery is reachable from `IntegrationTestBase`/`LiveDataTestBase` without
`CommercialIntegrationTestBase`, the same composition the CO validation rebuild uses. Arrange:
`ResetCommercialAddressKey` → `CreateCommercialQuote(addressKey, config)` (direct creation) →
setup asserts (config identity + `RawAnnualPremium` positive) → `AttachPolicyAndImsQuoteGuid`.
Creates on `CommercialStateConfig.FLByPerilEAndSTopaV17` at
`CommercialGoodTestAddressesFL.GoodTestAddressFL041` (grep-verified unreferenced by any other
test). At this commit the FL Topa quote rated through the dispatcher's then-fallback; the current
dispatcher maps (FL, EAndS, Topa) to `CommercialEAndSTopaExcelRaterServiceFL`.

**Running these classes:** the pretooluse guard's allowlist names only the
`(Homeowner|Commercial)ExcelQuoteAuditDiagnosticTests` classes, so runs need the `-IsCommercial`
opt-in; `Run-DotnetTest.ps1` leaves an explicit `-FilterClass` untouched when the flag is passed:
`-FilterClass "*ExcelQuoteAuditServiceTests" -IsCommercial`.

**Green bar (run, passed):** 4/4 in 18s — the Commercial audit flow's first end-to-end test run
(dispatcher fallback rater, PDF leg, Success + marked). No skip+TODO needed.

---

# Verification

## Execution sequence (per stage; before pushing)

1. **One suite: let the run build it. Never a standalone `Build-Solution.ps1` first.** `Run-DotnetTest.ps1`
   builds by default, so a separate build compiles everything twice and wastes the minutes twice.
   `-NoBuild` is only for the second and later suites of a parallel batch, after one of them has built.
   A standalone `Build-Solution.ps1` is right in exactly one case: verifying compilation when no test
   run follows. It carries the line-length gate, so line length is never a separate step either.
2. Stage's green bar via `~/.claude/scripts/Run-DotnetTest.ps1 -TicketFolder SW-53770-co-excel-validation-audit-infra-rebuild`, each `run_in_background: true`, no `| tail`. For a parallel batch, the first run builds and the rest pass `-NoBuild`:
   - Commercial: `-Project Swyfft.Services.Excel.IntegrationTests -FilterTrait "TestGroup=Commercial" -IsCommercial` (never unscoped — the hook blocks it; `-IsCommercial` is required or the pretooluse guard blocks the run).
   - HO ByPeril: ONE backgrounded run, `-FilterTrait "TestGroup=ByPerilTests"` and no namespace filter. Do NOT split it per state with `-FilterNamespace "*{ST}.EAndS"`. Two reasons. The test tree is `Homeowner/{ST}/EAndS/` and `Homeowner/{ST}/Admitted/`, so an `*{ST}.EAndS` filter silently drops every HO Admitted validation class, which rides the same shared base. And `RootTestBase.ExcelSemaphore` is a static sized `min(ProcessorCount, 32)`, so it caps Excel instances per process, not per machine: ten per-state processes each claim a full core count's worth of slots.
   - Purchase tests: `-Project Swyfft.Services.IntegrationTests -FilterClass "*CommercialPurchaseServiceTestsFL"`.
   - Audit tests: `-Project Swyfft.Services.Excel.IntegrationTests -FilterClass "*ExcelQuoteAuditServiceTests" -IsCommercial`.
   - Excel unit tests: `-Project Swyfft.Services.UnitTests -FilterNamespace "*UnitTests.Excel"`.
3. Code-complete self-audit (below) before each stage's code-complete HARD STOP.
4. Captured-assert check whenever the HO chain is touched: `git status` on `Swyfft.Services.Excel.IntegrationTests/ExpectedResults/` must be CLEAN (zero diff — negative confirmation the re-parent didn't move the HO capture). If any baseline diffs: HARD STOP, read every changed file individually (no sampling), explain.

## Tests to add or modify

| Artifact | Base | Cases |
|---|---|---|
| `ExcelRaterValidationTestBase` (+ re-parented HO classes) | n/a (infra) | Safety: existing HO leaf tests unchanged and green; zero baseline diff |
| Rebuilt CO leaves (one per state/carrier) | `CommercialRaterValidationTestBase` (via the E&S/Admitted mid-bases) | per sampled config × `EachElementOption` index → C# == Excel; setup assert per creation |
| `CommercialExcelQuoteAuditServiceTests` | `ExcelQuoteAuditServiceTestBase` | purchased/fabricated-policy quote → `AuditResult.Success` + `AuditDocsGeneratedOn` set |
| Re-parented `HomeownerExcelQuoteAuditServiceTests` | `ExcelQuoteAuditServiceTestBase` | existing cases unchanged (success; IMS-missing prod/non-prod split) |
| Rewritten `CbsVn_to_TopaVm_ShouldMatchPremiums` ×4 | `CommercialPurchaseServiceTestsBase` | leg configs (CbsV17→TopaV1, V18→V2, V19→V3, V20→V4): per-leg config assert + premium match |
| Fixed `CbsV20_ShouldBecomeTopaV4_WhenAfterCutOffDate` | same | create on CbsV20 → purchase after cutover → lands TopaV4 |
| CO sentinel tests (delivered, `67430b6ebdf`) | shared base | unwritten Input cell → fail; unwritten non-V1 Version cell → fail; Excel default ≠ lookup → fail |
| Wind/hail exclusion assert in `CompareAdditionalPremiums` (delivered, `4dd504f93a2` + `f7118e17bba`) | `CommercialRaterValidationTestBase` | wind-excluded quote → `PerilPremiumNonHurricaneWind` and `PerilPremiumHail` both 0, on every leaf except the two whose generator gates on lookup V1 |
| `RaterFileContents_ShouldMatchCaptured` (delivered, `497f9823085` + `843614866b6`) | `ExcelRaterValidationTestBase`, inherited by both products | every non-excluded sheet plus `_NamedRanges` of the latest config's rater → matches its committed baseline; 19 CO leaves, 38 HO leaves |
| `EachElementOption_ShouldBeExpected` on the shared engine (Part 4 step 1 delivered, `ee654f0947a`) | engine on `ExcelRaterValidationTestBase`; four abstracts implemented per product | HO: existing 12 indices, values and behavior unchanged. CO: 19 indices now sourced from the config's element generators rather than `PatchModifiers` |

Failure aggregation: the shared base keeps HO's per-config/per-index `AggregateException` pattern (never stop at first failure).

Test pyramid: every artifact above is an integration test, which is the exception plan-mode.md allows for behavior that only exists wired up. What is under test is a real rater `.xlsm` evaluated through NPOI against a premium the C# generator computed from seeded data, so there is no unit-level seam that proves it. No combination coverage is pushed into these suites beyond the per-config and per-index sweep the comparison itself requires.

## Captured asserts

- HO `RaterFileContents` baselines: **zero diff** expected (the negative-confirmation guard on the re-parent).
- CO capture: 620 baselines generated and committed in Part 3, across all 19 CO leaves including
  the three retired Admitted ones. Regenerating any of them is a full rerun of the capture fact
  with `UPDATE_TEST_EXPECTED_RESULTS=true`, scoped by
  `-FilterTrait "TestGroup=Commercial" -FilterMethod "*RaterFileContents_ShouldMatchCaptured"`.
- Commercial quote-def / export captured asserts (`SeedingCoreBruteForceTest` `EFCommercialQuoteDefinition`, `CommercialAllRisksTests` exports): not run — no quote defs, configs, or rater data change.

## Existing tests as regression checks (no edits expected)

- HO ByPeril validation suites — their base chain is re-parented; green proves behavior unchanged.
- `Swyfft.Services.UnitTests` Excel folder — audit services + `OverriddenCommercialQuoteDefinitionRepository` change underneath them.
- `CommercialExcelQuoteAuditDiagnosticTests` / `HomeownerExcelQuoteAuditDiagnosticTests` — compile-level only (manual theories skip without the env var); their DI wiring moves to the dispatcher.

## Code-complete self-audit (comments + ClosedSets) — REQUIRED before every stage's code-complete HARD STOP

Re-read `~/.claude/rules/comments-docs-and-external-writing.md` and `Swyfft.Common/SetDefinitions/CLAUDE.md` (actual Reads, not recall); walk every comment and every ClosedSet usage the stage's diff adds/changes, verdict each (keep/trim/delete; parameters typed as sets, `.Value` only at boundaries, `.Switch()` forms). Magic numbers/strings extracted to named constants; 120-char line cap on all touched `.cs` lines.

## AC coverage map

| AC | Delivered / proven by |
|---|---|
| A — shared infra, HO canon | Delivered record + as-built sections; HO suites green + zero baseline diff |
| B — tests and audit run same code | The shared dispatcher (audit DI + tests resolve it); the audit tests |
| C — tests run the claimed config | Direct creation + per-creation setup assert in the shared base; suites green |
| D — latent bugs exposed → skip+TODO | Every gap the checks found was closed rather than deferred, so zero `SW-53770 follow-up` markers remain in the repo (grep, 2026-08-27). The exclusions that stand are firm decisions with a business reason, not TODOs: SW-53916 run-off Topa, and the two lookup-V1 wind/hail configs |
| E — MVP, captured asserts as their own PR | Part 3 (#22504) shipped the CO baselines and retired the opt-in; CO shape kept only where unshared (PatchModifiers) |
| F — Part N PRs, each green, stop anywhere | Per-chunk HARD STOP cycle; the ranked remaining-work list |
| Ticket symptoms (5 unpinned leaves, MS carrier, AL landing, vacuous CBS/Topa, V20→V4) | All by C + the CO validation rebuild (MS already fixed by SW-54468; AL closed as "mechanism removed") |

## N/A sections (required conditionals)

- **Seeder overrides:** N/A — no new state configs or quote definitions.
- **State-config fold-vs-stack + ticket doc-comments:** N/A — no `IStateConfig` implementer touched.
- **Quote-def dates/ordering:** N/A — no quote-def or date changes.
- **Seeding:** N/A — no rater files, elements, quote defs, or migrations change.
- **Solution files:** N/A — no new projects. **DB queries / remote env / appsettings:** N/A.
- **`/eli--prebind-validation`:** skipped — no elements, state configs, generators, or quote definitions change; HO coverage comes from the ByPeril suites above.

## Transition out of verification

Verification ends when all stage green bars pass and Eli explicitly agrees we're done (or calls the cut). `grep -rn "SW-ELI"` must then come back empty: every placeholder TODO gets its real story ID before the PR is drafted (see the AC section's `SW-ELI` rule). Then plan-mode Part C § Post-Test-Approval Sequence: one approval to commit+push → `/review-pr` (once; discuss findings, at most one fix commit, no second review) → `Read ~/.claude/rules/pr-creation.md` → PR description draft (title `[SW-53770] (CO) Part N …` — the `Part N` keeps the merge workflow from moving SW-53770, per AC F) → HARD STOP for sign-off → `gh pr create --body-file` (body in `artifacts/pr/`; pass an absolute path, since the pretooluse hook reads the file itself and does not expand `$HOME`). SW-53770 moves to Review only with the final part (per AC F the story stays in Develop until the last part merges).

A part that builds on an unmerged part is a **stacked PR**, and stacking is done with the `gh-stack` extension, never by hand. Create the PR with `--base <the branch below>`, then register it: `gh stack link <lower PR#> <higher PR#>` (bottom to top). That path needs no local tracking and does not touch branches or bases. Basing a PR on another branch without linking it is not a stack, and only a real stack gets the stack UI, bottom-up merge, and auto-retarget when the lower PR merges.

---

# As-built record — CO validation rebuild + shared rating pipeline (the review-round rework)

Commit 4 grew far beyond the original plan text during Eli's live review. The plan's premise (AC A:
HO's shape becomes the shared base wherever machinery is parallel) was applied to the **rater
services** and then repeatedly deeper into the **test bases**. Decisions were Eli's, made in review.

## Rater services (`Swyfft.Services.Excel`)

- **`ExcelRaterServiceBase<TQuote, TPremiumValues, TKey, TContext>`** (was 3 generics) now owns the
  whole rate pipeline: `GetExcelPremiumForQuote` (create context → open workbook by key → rate →
  release with audit-save on failure), `GetExcelPremium(wi, context, writeComments = true)`
  (PrepareContext → SetExcelValues → ReadPremiumValues → comments gate), internal
  `SetExcelValues(wi, context, evaluateFormulas = true)` (RunWorkbookSetters → SetVersions →
  evaluate), the unconditional `SetVersions` mapping loop (writes
  `config.LookupVersions.GetVersion(t).ToString()`; `SetAdditionalVersionCells` hook), and
  `GetWorkbookFilesByStateAndCarrier`. Contracts: `RatingType`, `CreateRatingContext`,
  `GetWorkbookKey`, `GetStateConfig`, `GetQuoteLineContainer`, `RunWorkbookSetters`,
  `ReadPremiumValues`, `GetVersionCellMappings(context)`, virtual `PrepareContext`.
- **HO** (`ByPerilHomeownerExcelRaterServiceBase`): new `public sealed record
  ByPerilHomeownerRatingContext(IByPerilQuoteElementModel ElementModel, QuoteLineContainer
  QuoteLines)`; its 3-arg `WorkbookSetters` property and all ~38 subclasses untouched; internal
  4-arg `GetExcelPremium`/`SetExcelValues` adapters keep the HO test signatures; cap-prior version
  cells in `SetAdditionalVersionCells`; FIGA/UW-fee pruning in `ReadPremiumValues`.
- **CO** (`CommercialExcelRaterServiceBase`): new `public sealed record
  CommercialRatingContext(EFCommercialQuote Quote, QuoteLineContainer QuoteLines)`; gains abstract
  `WorkbookSetters` (`IEnumerable<Action<WorkbookInfo, CommercialRatingContext>>`); public
  convenience `GetExcelPremium(wi, quote, writeComments = true)`; internal
  `GetVersionCellMappingsForState(stateCode)`.
- **E&S service**: `SetExcelValues` monolith → three setters (`SetInputValues`,
  `SetClaimHistoryValues`, `SetTerritoryAndSarValues`). **Admitted**: same conversion.
  **SCQbe**: override → one appended NamedStormDeductible setter. **NJQbe**: override → one
  prepended formula-freeze setter.
- **NEW `CommercialEAndSExcelRaterServiceFLCbs`**, registered in the dispatcher at
  (FL, EAndS, ClearBlueSpecialty): carries the 12 pre-SW-52867 FL version-cell mappings (derived
  from `git show 40aab3529bc^` — the FL block before SW-52867; CBS kept that rater). This replaces
  the `HasNamedCell` guard, which was DELETED from the version loop (Eli: a mapping must describe
  its rater; a silent skip is the data model lying). The old `writeComments` threading through
  `SetExcelValues` was reverted in favor of the pipeline gate.
- **Known deltas accepted by Eli ("lean on HO's shape")**: CO version text now
  `ByPerilVersions.ToString()` (was `.SingleVersion.ToString()` — identical for single-version
  lookups, which is all CO has); CO versions write after inputs; CO comments write after readback;
  CO container derivation before workbook open; CO quote-line derivation inside the evaluated try.

## Test bases (`Swyfft.Services.Excel.IntegrationTests`)

- **`ExcelRaterValidationTestBase<TConfig, TRated, TRaterService, TQuote, TPremiumValues,
  TContext>`** (was `<TConfig>`) — constraints: `TConfig : class, IStateConfig`, `TRated : class`,
  `TRaterService : ExcelRaterServiceBase<TQuote, TPremiumValues, (StateCode, CarrierCode),
  TContext>`, `TPremiumValues : ByPerilPremiumValues, IExcelPremiumValuesBase`. Now owns:
  - abstract `ExcelRaterService` property (fully typed per product);
  - config discovery: abstract `GetAllConfigs()`; shared `GetAllConfigsForGroup()` (4-way
    IStateConfig filter incl. ByPeril, minus `ExcludedConfigs`), `GetLatestConfig() => [^1]`,
    `GetConfigsForGroup` sampling; virtual `ExcludedConfigs` (inverse of `AlwaysIncludedConfigs`);
  - `GetGroupWorkbookInfo`, `ReleaseWorkbookAndGetFileName` (one-liners over the property);
  - `RunAndCheck(config, wi, customizeFunc?, createQuote?)` — create → customize (null = fail) →
    re-assert config → `ComparePremiums`;
  - `ComparePremiums(wi, rated)` template — `GetExcelPremium(writeComments: false)` →
    `CompareByPerilPremiumValues(GetSwyfftPremiumValues, AcceptablePremiumDifference,
    GetComparisonContext, GetIgnoredRisks)` → `CompareAdditionalPremiums` → catch: write Comments
    sheet (guarded) + `DecoratePremiumComparisonFailure` → rethrow;
  - `RunEachElementOptionSweep(testName, customizeForIndex)` using abstract
    `EachElementOptionIterationCount`;
  - `CreateCanonicalRatingContext(config)` abstract + private
    `PopulateWorkbookWithCanonicalInputs` (context → `SetExcelValues(evaluateFormulas: false)`);
  - virtual `AcceptablePremiumDifference` (1.0M default; CO overrides 2.0M).
- **`ByPerilExcelTestHelpers` moved to the project root** (namespace
  `Swyfft.Services.Excel.IntegrationTests`) — it holds shared infra (`CompareByPerilPremiumValues`
  engine, `ByPerilComparisonContext`, `GetMixedRadixIndices` (moved off the generic base),
  `ReportConfigFailures`) plus HO-only members (`CoverageBCDV1Skip`, `GetDynamicElementValues`);
  15 HO leaf references resolve via enclosing-namespace lookup. HO-only members splitting out to a
  Homeowner-ns class is a candidate follow-up nicety, deferred for context budget.
- **HO**: `HomeownerRaterValidationTestBase` binds the six generics
  (`…, HomeownerQuoteAndContext, ByPerilHomeownerExcelRaterServiceBase, EFHomeownerQuote,
  ByPerilHomeownerExcelPremiumValues, ByPerilHomeownerRatingContext`); `TestAddress` moved up to it
  from `ByPerilValidationTestBase`; creation extracted to `CreateRatedQuote(address, livingSpace,
  configOverride, riskSelection)`; the knobbed legacy `RunAndCheck(address, …, wi)` keeps its
  signature — delegates to the shared skeleton when it has wi + configOverride (knobs via
  `createQuote`), keeps the own-workbook/no-config path itself. `TestWorkbook` DELETED — dissolved
  into hooks in `ByPerilValidationTestBase`: `GetRatingContext`, `GetSwyfftPremiumValues`,
  `GetComparisonContext`, `CompareAdditionalPremiums` (the fee-total check),
  `DecoratePremiumComparisonFailure` (TestedElementValues wrap); `GetIgnoredRisks` (SAR hurricane)
  on `HomeownerRaterValidationTestBase`. HO `EachElementOption_ShouldBeExpected` now rides
  `RunEachElementOptionSweep` (count 12); `ValidateElementOptionsForConfig` deleted.
- **CO**: binds the six generics; `CommercialRatedQuote(Context, Quote)` record; hooks implemented;
  `GetIgnoredRisks` is now CLASS-BASED, no runtime switch: shared default `[]`; E&S base →
  `EAndSIgnoredRisks` (WaterWeather/Theft/Liability/Sinkhole/Hurricane); `…FLBase` → `[]` (shared
  FL rater rates every peril; covers TopaFL + ClearBlueSpecialtyFL); `…QbeFL` → back to
  `EAndSIgnoredRisks` (ISO rater; HadronFL inherits); Admitted base → its 6.
  `DumpPremiumComparison`/`DumpValue`/`DumpRiskValues` DELETED (failure workbook + Comments sheet
  are the diagnostics). `IPatchModifier`/`PatchModifier<T>`/`CombinedPatchModifier` un-nested to
  `Commercial/CommercialPatchModifiers.cs` (public, namespace-level; the whole file was deleted
  later in Part 4, commit `c24a3f9be9a`). CO sweep count 19.
- Eli process ruling, repeated and binding: **he is the product owner of this refactor; design
  decisions go through him; when HO and CO differ, lean on HO's shape unless it genuinely cannot
  work for CO.**

# Notes from Eli (durable, carry into follow-ups)

- **`AssertCarrierSpecificPremiums` is a stopgap, not a design.** The asserts currently routed
  through it should eventually apply to ALL carriers. The infrastructure is good to have, but Eli
  created it so he could test things on specific carriers without uncovering the other states,
  which may be hiding latent bugs. Follow-up direction: promote its asserts to the shared
  comparison as the other states get uncovered.

- **A retired state is not an exclusion.** `SkipReason` says Swyfft sells nothing in that state, so
  there is nothing to validate. It is permanent and owes no ticket. An exclusion says the test is
  correct and would fail. Never count the two together or describe them with the same word.

- **Every failure sorts into one of three categories before anything is done about it.**
  1. **A defect in the test infrastructure.** The test feeds the rater a value it cannot rate, or
     compares the wrong thing. Production is fine. Fix the test. This never earns an exclusion.
  2. **A defect in production the test rightfully exposes.** The rater file, the rater service, or
     the premium generator genuinely disagree. Fix production, or exclude with a
     `TODO (SW-53770 follow-up)` when the fix is out of scope for this ticket. This is AC D.
  3. **Coverage this branch newly reaches.** Development never exercised it, so a defect that was
     always present surfaces for the first time. Handled like category 2. New coverage reaching a
     new defect is not a regression.

- **An exclusion is temporary or permanent, and says which.** Temporary holds a known disagreement
  until it is fixed and names its ticket. Permanent covers a config old enough that its rater no
  longer supports it, which we accept. HO already does the permanent kind:
  `ByPerilAdmittedValidationTestsClearBlueAL` and `ByPerilAdmittedValidationTestsClearBlueFL` set
  `EachElementOptionStartingFrom` to V5 and V23, dropping every earlier config with no ticket.

- **The bar for every failing config is development's exact coverage, no less.** An exclusion is
  scoped to precisely what development did not exercise: the option, the factor, the peril. Two
  questions per failure. Did development pin this config? Did development feed the input that now
  fails? Yes to both puts the failure in category 1 or 2 and it gets fixed. No to either puts it in
  category 3.

- **The three exclusion hooks this branch invented were removed, not banned.** `ExcludedConfigs`,
  `ExcludedFactors` and `ExcludedFees` had no counterpart on development. Each entry was written on
  the belief it held a pre-existing latent bug, none had been sorted into the three categories
  above, so none had earned its place. `ExcludedFactors` was also structurally unsound: rates are
  cumulative, so excluding a factor row leaves its discrepancy running down every later row. A
  similar hook is welcome again once a failure is confirmed category 2 or 3.

## Progress

Every entry goes through the `eli--generate-progress-entry` skill, which runs
`~/.claude/scripts/Add-ProgressEntry.ps1`. Never hand-write a row and never type a timestamp:
the script reads the clock, or the mtime of the artifact the entry describes, or a commit's
author date, and appends the row itself. This section supplies only the heading; the script
owns the table under it.

| When | What happened |
|---|---|
| 2026-08-18 4:17 PM | Planning complete. Record of the session: ticket read (11:03 AM dump); Stage → Develop; full HO/CO test-infra + audit-doc-flow research (see Research record); Q&A decisions Q1-Q8 (HO canon shared base; HO-style dispatcher with shared dispatcher base; direct creation kills pin-at-creation; HO sampling; shared EachElementOption engine with CO `PatchModifiers` + later dynamic-discovery commit; shared audit-test base; Feature type; sentinels + dynamic discovery planned in); three AGENTS.md audit-framing doc edits applied to working tree (uncommitted, on `development`); ticket title/description rewritten and posted; folder renamed to `SW-53770-co-excel-validation-audit-infra-rebuild`; plan written. Execution not started — branch not yet created. |
| 2026-08-18 4:29 PM | Step 0b done. Branch `feature/ek/20260818_SW-53770_co-validation-audit-infra` created from `origin/development` (988328044c2), pushed, tracking verified via `git branch -vv`. The three doc edits carried over onto the branch (uncommitted, ride commit 1). Commit 1 (shared validation base) started. |
| 2026-08-18 5:02 PM | Commit 1 code-complete. New `ExcelIntegrationTestBase` (semaphore/fixture/dispose/ExcelTests trait; a second new layer beyond the plan's named types — Eli reviewed the reasoning in chat and said "fine") and new `ExcelRaterValidationTestBase<TConfig>` (sampling, RunTestForAllConfigs, RunItemsForConfig + GetMixedRadixIndices, sentinel cores, capture core, AssertQuoteCreatedOnConfig). Re-parented `HomeownerExcelIntegrationTestBase` (keeps HO DI only) and `HomeownerRaterValidationTestBase` (onto the shared generic base; RunAndCheck uses the shared setup-assert). `ByPerilValidationTestBase` slimmed to HO-specific machinery + five overrides; facts delegate to shared cores, names unchanged. `ReportConfigFailures` genericized. Build was green after one fix (missing `using Swyfft.Services.Premium;` for `ByPerilName` — 16 errors, one root cause). Comment + ClosedSet self-audit done: six authored comments fixed (unverified causal claim, false "every" claim, HO-specific mechanism claim in shared contract, em-dashes); ClosedSet usages clean. Doc-comment-only fixes landed after the green build. Awaiting approval to run the commit-1 green bar (HO ByPeril suites + zero-diff baselines). |
| 2026-08-18 5:12 PM | Stage 1 COMMITTED: `73d02c554ff` "SW-53770: Extract shared Excel validation test base from the HO ByPeril chain" (9 files; includes the three audit-framing doc edits). NOT pushed. **Green-bar deviation (Eli's call):** the stage-1 HO suite run was replaced with a `-ListTests` discovery check — running the suites now had no clean signal (no known-green pre-change baseline on this machine); suites are deferred to commit 2's one-state smoke and a full sweep before push. Discovery result: 38 classes carry each of the six inherited facts (matches the pre-refactor "38 leaves" in the CoverageBCDDictCaps tolerance comment); traits (Category=ExcelTests via the new layer, ByPerilTests, State/Carrier) all present; 626 test methods in the project. **Next: stage 1 item 2 (shared dispatcher)** — extract `ExcelRaterServiceDispatcherBase` from `ByPerilHomeownerExcelRaterService` (Swyfft.Services.Excel/Homeowner/ByPeril/Rater/, dictionary + GetConcreteRaterService at l.117-130 pre-refactor), add `CommercialEAndSExcelRaterServiceDispatcher : ICommercialEAndSExcelRaterService` over the five subclasses with base fallback, re-point `SwyfftExcelTask` (Swyfft.Console.Base/SwyfftExcelTask.cs:31) + `CommercialExcelQuoteAuditDiagnosticTests` + validation-test DI at the dispatcher. See "As-built record" section for the stage-1 API. |
| 2026-08-18 5:32 PM | Commit 2 (shared dispatcher) code-complete. New `ExcelRaterServiceDispatcherBase<TQuote, TPremiumValues, TService>` (`Swyfft.Services.Excel/` root): abstract `RaterServiceByStateAndRatingType` dictionary + `GetRaterType(quote)`, virtual `FallbackRaterService` (null default = throw), public `GetConcreteRaterService(state, ratingType, carrier)` + `GetExcelPremiumForQuote`. `ByPerilHomeownerExcelRaterService` re-parented onto it (dictionary value type now `Lazy<ByPerilHomeownerExcelRaterServiceBase>`, cast dropped, both methods deleted; behavior note: the unregistered-key exception message from `GetExcelPremiumForQuote` changed from "No Excel Rater Service setup for {raterType}." to the base's "registered for ({state}, {ratingType}, {carrier})" form — nothing asserts on either, verified by grep). New `CommercialEAndSExcelRaterServiceDispatcher : ICommercialEAndSExcelRaterService` over the five subclasses (NYQbe/TXTopa/SCQbe/NJQbe/NCQbe) with the shared `CommercialEAndSExcelRaterService` as fallback; key from `quote.ToRaterTypeUnsafe()`. Three DI re-points to the dispatcher: `SwyfftExcelTask.cs:31`, `CommercialExcelQuoteAuditDiagnosticTests`, `CommercialByPerilRaterValidationTestBase`. Two AGENTS.md warnings about the old DI split rewritten to describe the dispatcher (`Swyfft.Services.Excel/Commercial/AGENTS.md`, `Swyfft.Services.Excel.IntegrationTests/AGENTS.md`). Build green (one line-length fix). Comment + ClosedSet self-audit done: 2 overstated claims trimmed (CO validation tests still rate via `<TRaterService>` until commit 4, so "tests run the same concrete service" was deleted), 1 doc restating a signature deleted, 3 em-dashes/ambiguous-"it" fixed. Awaiting approval to run the commit-2 green bar (Excel unit tests + one-state smoke of both validation suites). |
| 2026-08-18 5:40 PM | Stage 1 item 2 COMMITTED: `e294e133e5e` "SW-53770: Extract shared rater-service dispatcher; route Commercial audit through it" (8 files: 2 new, 4 C# edits, 2 AGENTS.md rewrites). NOT pushed. **Green-bar deviation (Eli's call, same rationale as stage 1):** no test run at this stage — no known-green baseline to attribute failures against; the build (0 errors) is the stage's signal. Suites accumulate to commit 4's full Commercial run and the pre-push full sweep. See "As-built record — stage 1 item 2" for the dispatcher API. **Next: stage 1 item 3 (shared audit-test base)** — extract `ExcelQuoteAuditServiceTestBase` (abstract quote-with-policy arrange; shared `GenerateAuditDocs` success + `AuditDocsGeneratedOn` marking asserts), re-parent `HomeownerExcelQuoteAuditServiceTests` (child of `HomeownerExcelIntegrationTestBase`, `Swyfft.Services.Excel.IntegrationTests/Homeowner/`), add new `CommercialExcelQuoteAuditServiceTests`. Green bar per plan: both audit test classes (subject to Eli's per-stage call). |
| 2026-08-18 6:35 PM | Commit 3 (shared audit-test base) code-complete. New `ExcelQuoteAuditServiceTestBase : ExcelIntegrationTestBase` (`Swyfft.Services.Excel.IntegrationTests` root): abstract `GenerateAuditDocs(IList<QuoteId>)`; shared `AttachPolicyAndImsQuoteGuid(quoteId, productLine, ratingType)` (the direct-DB policy + `ImsQuoteGuid` fabrication hoisted from the HO test; `PolicyTermDays` const extracted); `AssertAuditDocsMarked(quoteId, expectMarked)`; `RunGenerateAuditDocsSuccessTest(quoteId)` (single Success result + marked). `HomeownerExcelQuoteAuditServiceTests` re-parented onto it (calls `HomeownerExcelIntegrationTestBase.RegisterExcelServices` in its own ctor; dropped its duplicate `IHomeownerExcelQuoteAuditService` registration and the `[Trait("Category", "ExcelTests")]` now inherited via `ExcelIntegrationTestBase`; both test names unchanged; the success fact now also asserts the marking via the shared core; the IMS-missing theory unchanged in behavior). New `CommercialExcelQuoteAuditServiceTests`: same registration block as `CommercialExcelQuoteAuditDiagnosticTests` (dispatcher included) + `FakeCommercialRiskProcessor`; builds its own `CommercialQuoteGenerator` via `GetCommercialQuoteGeneratorInfo` (Topa/EAndS); direct creation on `CommercialStateConfig.FLByPerilEAndSTopaV17` at `CommercialGoodTestAddressesFL.GoodTestAddressFL041` (verified unreferenced by any other test); setup asserts (config identity + `RawAnnualPremium` positive); the FL Topa quote reaches the rater through the dispatcher's fallback (shared `CommercialEAndSExcelRaterService`). Build green (one fix: `TestAddressWithCarrier.AddressKey` is already an `AddressKey`, dropped a stray `.ToAddressKey()`). Comment + ClosedSet self-audit done: class-summary and two doc comments trimmed, one unverified comment replaced with the sibling sites' verbatim wording, one comment deleted as duplicating the adjacent `because` strings, `PolicyTermDays` extracted; ClosedSet usages clean. Awaiting approval at the code-complete HARD STOP (green bar per plan: both audit test classes, subject to Eli's per-stage call). |
| 2026-08-18 6:52 PM | Commit 3 green bar PASSED: both audit test classes (`-FilterClass "*ExcelQuoteAuditServiceTests"` + `-IsCommercial -NoBuild`; the `-IsCommercial` opt-in is required because the pretooluse guard's allowlist names only the diagnostic classes, and the wrapper leaves an explicit class filter untouched). 4/4 passed in 18s: the 3 re-parented HO tests and the new `CommercialExcelQuoteAuditServiceTests` success test — the Commercial audit flow's first end-to-end test run (dispatcher fallback rater, PDF leg, Success + marked). No skip+TODO needed. Output in `artifacts/tests/…filter-class-ExcelQuoteAuditServiceTests_20260818-1800.txt`. Awaiting approval to commit. |
| 2026-08-18 7:00 PM | Commit 4 (CO validation rebuild) code-complete. Build green; NOT committed, NOT pushed. **24 new files, 26 deleted, 4 edited.** - **New chain:** `CommercialByPerilValidationTestBase` (`Commercial/`) on `ExcelRaterValidationTestBase<CommercialStateConfig>` → `CommercialEAndSByPerilValidationTestBase` / `CommercialAdmittedByPerilValidationTestBase` → per-state bases (`...FLBase`, `...LABase`, `...TXBase`, `...QbeIsoBase`) → 19 leaves, one per (state, carrier): E&S TopaFL/ClearBlueSpecialtyFL/QbeFL/HadronFL, TopaLA/HadronLA/QbeLA, TopaTX/HadronTX/QbeTX, TopaAL, DorchesterMS, QbeNY/QbeNC/QbeNJ/QbeSC; Admitted ClearBlueIL/ClearBlueNY/ClearBlueWA. - **Root base API:** abstract `TestAddress`, `ResolveRaterService()`, `GetPatchModifiers(config)`; `CreateQuoteOnConfig(config)` (ResetCommercialAddressKey → `CreateCommercialQuote(addressKey, config)` → `AssertQuoteCreatedOnConfig`); `RunAndCheck(config, wi, customizeFunc)` which re-asserts the config after patching and compares premiums on the caller's workbook; `RunForAllConfigs(testName, customizeFunc)`; `EachElementOption_ShouldBeExpected` (sampled configs × 19 indices via `RunTestForAllConfigs` + `RunItemsForConfig`); the three shared one-offs (`MaxBuildingValue`, `ClaimHistory_FirstClaimIsFree`, `ClaimHistoryLookup_VerifyExcelRaterCanHandleFailure`) now run across every sampled config; `SkipReason`/`SkipIfStateRetired()` replacing the old `SkipTests`/`TrySkip` (guard is called before the aggregation, since a skip raised inside it would be collected as a failure). - **Version variance is config-gated, not class-per-version:** `IsAtOrAfter(config, first)` over `CommercialStateConfig.StartingWith`. LA gains Walls In at `LAByPerilEAndSTopaV3` and LWD + wide deductibles + the 19-item roof set at `V9`; TX at `TXByPerilEAndSTopaV7` / `V15`; FL Topa gains LWD + wide wind deductible + Walls In at `FLByPerilEAndSTopaV17`. A new config version now needs no new test class. - **Modifier positions are named:** `ConstructionTypeModifierIndex` (root), `HurricaneDeductibleModifierIndex` / `RoofTypeModifierIndex` / `CrimeCoverageModifierIndex` (E&S base), replacing bare `PatchModifiers[6]/[10]/[17]/[25]`. Index mapping confirmed against the old leaves' own comments. - **Two production accessors added** (`Swyfft.Services.Excel/Commercial/CommercialExcelRaterServiceBase.cs`): `SetExcelInputs(wi, quote)` and `GetVersionCellMappings(stateCode)`, both pure accessors over existing protected members. Needed to implement the shared base's abstracts; `GetVersionCellMappings` is also what commit 5's sentinel checks will read. - **Pin mechanism removed:** `applyAtQuoteCreation`, `ApplyGetterAtQuoteCreation`, the `GetQuoteDefinitionsByStateCarrierRating` override, and `RunTest`'s pin assert are all deleted. `SetCommercialQuoteDefinitionGetter` survives for its one remaining consumer, `CommercialCensusSnapshot2020IntegrationTests`, which never used the creation flag. - **`CommercialPurchaseServiceTestsFL`:** the four `CbsVn_to_TopaVm_ShouldMatchPremiums` legs now create directly via `CreateCommercialQuote(addressKey, stateConfig)` with a per-leg config assert; `CbsV20_ShouldBecomeTopaV4_WhenAfterCutOffDate`'s copy-pasted V19/TopaV3 args corrected to V20/TopaV4; misleading `quoteCbsV18`/`quoteTopaV2` locals in the V17→V1 leg renamed. - **Build history:** three failed builds before green. (1) line-length gate, 24 added lines — the occupancy tuple rows now go through a shared `Occupancy(...)` factory on the E&S base, which also removed QBE FL's duplicate `Habitational` helper. (2) nine compile errors from three missing usings (`Swyfft.Services.Excel.IntegrationTests.Homeowner` for the shared comparison helper, `Swyfft.TestUtilities.Mocks`, `Swyfft.TestUtilities.Commercial` in four leaves) plus a `decimal?`→`decimal` mismatch in the tolerance forwarding. (3) IDE0060 unused `wi` — a real defect: `ComparePremiums` was opening its own workbook instead of the caller's, so a failing iteration would have saved a workbook that never rated. Now uses the passed workbook and leaves its lifecycle to the caller. - **Self-audit done.** Reverted three paraphrases to the original wording (the ignored-perils explanation had lost "their base rates are 0"; the GL dependent-coverage note). Deleted four invented claims: that the FSLSO fee "changed on 7/1/2026", that the LA SLIP fee did likewise, that "TX rates changed at the start of 2024" (all inferred from boundary dates, none in the source), and a rationale about showing agents a declined-coverage price. Trimmed an inferred claim that office/retail occupancies rate off square footage. ClosedSets: two `.Value` calls inside interpolation removed; parameters typed as sets; rating-type branch uses `.Switch()`. - **Two expected breakages to watch at the green bar** (AC D → skip+TODO if they fail): TX Hadron and TX Qbe previously rated through `CommercialEAndSExcelRaterServiceTXTopa` by class inheritance and now get the shared service via the dispatcher, which has no (TX, EAndS, Hadron/Qbe) entry; and the CBS-vs-Topa premium parity has never actually been exercised, since the old tests created both legs on the same config. - **Deliberate loss to flag:** the CO validation leaves no longer inherit `CommercialIntegrationTestBase`, so its `CriticalCommercialTests` fixture check no longer runs as part of this suite. - **Green bar per plan (awaiting approval to run):** full Commercial validation suite (`TestGroup=Commercial`) + `CommercialPurchaseServiceTestsFL`. |
| 2026-08-18 7:02 PM | Stage 1 item 3 COMMITTED: `a9a96f259b6` "SW-53770: Extract shared audit-test base; add Commercial audit-doc test" (3 files: new `ExcelQuoteAuditServiceTestBase`, re-parented `HomeownerExcelQuoteAuditServiceTests`, new `CommercialExcelQuoteAuditServiceTests`). NOT pushed — nothing on the branch is pushed yet (`73d02c554ff`, `e294e133e5e`, `a9a96f259b6` all local-only). Green bar run and passed this stage (4/4; see the 6:52 PM entry). **Stage 1 is complete.** See "As-built record — stage 1 item 3" for the audit-test-base API and the `-IsCommercial` run recipe. **Next: stage 2, commit 4 (CO validation rebuild)** — new `CommercialByPerilValidationTestBase` on `ExcelRaterValidationTestBase<CommercialStateConfig>`; one leaf per (state, carrier) incl. Admitted IL/NY/WA; HO sampling policy via `GetConfigsForGroup`; direct creation (`CreateCommercialQuote(addressKey, stateConfig)`) + setup assert per quote; `EachElementOption` on the shared engine with CO values from `PatchModifiers`; one-offs (`MaxBuildingValue`, `ClaimHistory_FirstClaimIsFree`, `ClaimHistoryLookup_VerifyExcelRaterCanHandleFailure`, `PatchQuote_FslsoServiceFeeBoundary_ShouldBeExpected`, `AssertNonHurricaneWindAndHailAreZeroWhenExcluded`) sorted into their child classes; per-config leaves + `<TRaterService>` generic deleted; `CommercialPurchaseServiceTestsFL` CBS/Topa legs rewritten on direct creation (V20→V4 args corrected); with the last pin consumers gone, delete `applyAtQuoteCreation` + `ApplyGetterAtQuoteCreation`. Green bar per plan: full Commercial validation suite (`TestGroup=Commercial`) + `CommercialPurchaseServiceTestsFL`; exposed breakage → skip+TODO. |
| 2026-08-19 12:35 PM | Commit 4 + the shared rating-pipeline rework: **build GREEN, committed, NOT pushed.** 46 files. See "As-built record — CO validation rebuild + shared rating pipeline" above for the full shape; that section is the authority, not the original commit-stage text. **The five suites (superseded as a next-step marker by the 6:40 PM entry above, which points here for these commands).** Background each, `-NoBuild`, build is current: - `Run-DotnetTest.ps1 -TicketFolder SW-53770-co-excel-validation-audit-infra-rebuild -Project Swyfft.Services.Excel.IntegrationTests -FilterTrait "TestGroup=Commercial" -IsCommercial -NoBuild` (the `-IsCommercial` flag is REQUIRED — the pretooluse guard blocks the run without it) - HO ByPeril, one run covering every state and both rating types: `-Project Swyfft.Services.Excel.IntegrationTests -FilterTrait "TestGroup=ByPerilTests" -NoBuild` — **mandatory this round**: the HO rater service and HO test bases were both re-parented, so HO is no longer a bystander. No `-FilterNamespace` (see the execution sequence above for why per-state scoping is wrong). - `-Project Swyfft.Services.IntegrationTests -FilterClass "*CommercialPurchaseServiceTestsFL" -NoBuild` - `-Project Swyfft.Services.Excel.IntegrationTests -FilterClass "*ExcelQuoteAuditServiceTests" -IsCommercial -NoBuild` - `-Project Swyfft.Services.UnitTests -FilterNamespace "*UnitTests.Excel" -NoBuild` - HO `ExpectedResults/` baselines must show **ZERO diff** (`git status` on that folder) — the negative-confirmation guard that the HO re-parent moved nothing. Known-expected findings to triage rather than panic over: the merge-region crash should be gone (comments are no longer written per-rate); TX Hadron/TX Qbe now resolve the shared E&S service instead of the TXTopa subclass via inheritance; the CBS-vs-Topa parity legs are newly real. Exposed breakage → skip-override + `// TODO (SW-53770 follow-up):` per AC D. |
| 2026-08-19 6:40 PM | Commercial rater services rebuilt on HO's shape, then renamed to HO's naming. **Build GREEN, working tree clean, three commits, none pushed: `95b9aec1d41` (the rebuild, 44 files), `2c20fb43184` (the renames, 54 files), `86e02fe130a` (two carrier names the rename pass had abbreviated).** Seven commits on the branch now. **NO TEST HAS RUN against any of this.**<br><br>**The five suites (superseded as a next step by the 2026-08-21 entry above, which runs Commercial only).** Triage per AC D (skip-override plus a `// TODO (SW-53770 follow-up):` marker; inline fix only when trivial). The commands and the `-IsCommercial` requirement are unchanged; the class names in any failure output are the new ones.<br><br>What changed since the last test run, so a failure can be attributed: - **One class per rater, 19 leaves**, each declaring its own rater's factor rows, coverages, fees, and version cells. `FactorNames`, `CoverageNames`, `FeeNames`, `IncludeHurricane`, and `GetAdditionalPremiumValues` take no state or carrier argument any more. - **One dispatcher**, `CommercialExcelRaterService`, keyed `(StateCode, RatingType, CarrierCode)` over both rating types, with **no fallback**. An unregistered leaf throws. This replaced the E&S-only dispatcher and the old `CommercialExcelRaterService` runtime `.Switch(...)` router; `ICommercialEAndSExcelRaterService` and `ICommercialAdmittedExcelRaterService` are gone, leaving `ICommercialExcelRaterService`. - **Every `HasNamedCell` guard is gone** from the Commercial rater services. A rater now declares what it carries: `WritesTerritoryCodes`, `WritesWindMitigationTable`, `WritesProtectionClass`, `WritesWindConstructionProgram`, `WritesNumberOfBuildings`, `WritesEffectiveDate`, `WritesMinimumPremiumInputs`, `WritesCoverageInputs`, `ZeroesInspectionFeeWhenAbsent`, `RatesWallsInCoverage`, `RatesRoofMaterialsPaymentSchedule`, `ReadsLiability`, `HurricanePremiumCellName`, `SetTerritoryValues`. Admitted has `RatesEarthquake`, `RatesWindDeductible`, `RatesStopGap`, `RatesMinOwnerOccupied`. **Each flag was set from the named-range dumps in `artifacts/rater-dumps/`, to reproduce today's writes exactly.** A wrong flag now throws where the guard used to skip, so a `Could not find cell with name X` failure means a flag is set on a rater that lacks the cell. - **FL Qbe and FL Hadron** declare the 10 version cells their ISO rater actually has. That is what the deleted guard was skipping to, so their writes are unchanged and Finding 2's throw is gone. - **A failing validation iteration writes its own `Comments index N` sheet**, so each saved failure workbook carries the quote lines of the rating that failed. `Warning: Failed to write Comments sheet` should no longer appear. - **Renames.** `CommercialEAndS{Carrier}ExcelRaterService{State}`, `CommercialEAndSUnifiedRaterExcelRaterServiceFL`, `CommercialEAndSIsoRaterExcelRaterServiceFL`, `CommercialAdmittedClearBlueExcelRaterService{IL,NY,WA}`, `CommercialEAndSValidationTests{Carrier}{State}`, `CommercialRaterValidationTestBase`, `CommercialEAndSValidationTestBase`, `CommercialAdmittedValidationTestBase`. No HO file changed.<br><br>Findings 3 and 4 from the pre-rework run are untouched and expected to recur: the `EFByPerilRoofAgeFactor` lookup failures on LA Qbe, LA Hadron, TX Qbe, TX Hadron, and FL CBS V0, and the FL Topa V15/V16 Policy Fee difference of 300 against 400. Both are AC D skip-plus-TODO candidates. TX Topa V1 already carries its exclusion.<br><br>One TODO is already in the tree, on `CommercialEAndSIsoRaterExcelRaterServiceFL`: the FL ISO raters' `WHDeductibleVersion` cell reads V2 and C# never writes it. |
| 2026-08-21 12:50 PM | Merged `development`, ran the five suites, triaged twice, and finished a comment-provenance audit. **Build GREEN, tree clean. Two new commits: `6ea2e487f32` (the gate and declaration fixes) and `ae8690c03bc` (the dispatcher rename plus comment restorations). Origin is at `6ea2e487f32`, so only `ae8690c03bc` is unpushed.**<br><br>**(Superseded as a next step by the 2026-08-21 3:10 PM entry above. That run happened; its results are recorded there. The command and the HO-not-needed reasoning below still hold.) Run the Commercial suite ONLY:** `Run-DotnetTest.ps1 -TicketFolder SW-53770-co-excel-validation-audit-infra-rebuild -Project Swyfft.Services.Excel.IntegrationTests -FilterTrait "TestGroup=Commercial" -IsCommercial -NoBuild`<br><br>**Do NOT re-run HO ByPeril, the audit tests, the purchase tests, or the Excel unit tests** (Eli's call, verified). Nothing since the last full run can move them: `ae8690c03bc` is identifiers and comment text, and the build proves the rename is consistent. `6ea2e487f32`'s only shared change is the `ExcludedFactors` / `ExcludedFees` plumbing, whose defaults are empty with all three overrides on CO Topa leaves, so HO's comparison is unchanged.<br><br>**The merge.** 358 `development` commits. One conflict, `CommercialEAndSByPerilRaterValidationMS.cs`, deleted here and modified there; resolved by accepting the deletion and carrying development's stale `// TODO: JRH 20231203` cleanup onto the leaf that replaced it, `CommercialEAndSValidationTestsDorchesterMS`. Merge commit `7c235ade6d6` holds nothing else. Development brings SW-52308 (#22289, the audit reprice grace window) into `ExcelQuoteAuditServiceBase`, `CommercialExcelQuoteAuditService`, and new `Swyfft.Services.UnitTests/Excel` tests. Zero file overlap with this branch's commits.<br><br>**Five-suite run (pre-fix).** HO ByPeril 366/0/17 with `ExpectedResults` zero-diff. Excel unit tests 94/94, which includes SW-52308's new tests. Audit doc tests 4/4. `CommercialPurchaseServiceTestsFL` 16 passed with 1 skip that is dev's own `[Fact(Skip = "Re-enable on June 5 2023")]`; all four `CbsVn_to_TopaVm_ShouldMatchPremiums` legs passed, so the parity the plan flagged as never-exercised holds and owes no TODO. Commercial 47/31/33.<br><br>**Commercial triage, first pass (31 failures).** Two were flag bugs from deleting the `HasNamedCell` guards: `Carrier` missing on FL ClearBlueSpecialty and `Buildings` on NC Qbe, both confirmed absent from those raters' named-range dumps. `EFByPerilRoofAgeFactor` missing rows on Hadron LA/TX, Qbe LA/TX and CBS FL. Policy Fee 300 vs 400 on FL Topa V15/V16 (the plan's Finding 4, one index). `LimitedWaterDamage` factor mismatches on LA Topa V9 and TX Topa V15.<br><br>**Commercial triage, second pass (14 failures).** Fixing the first two cells unmasked two more: `LimitedWaterDamage` on CBS FL and `OrdinanceOrLawRow` on NC Qbe, whose rater carries `OrdinanceOrLawARow` like the passing NY Qbe sibling.<br><br>**The root cause behind the LA/TX Hadron and Qbe failures.** `IsAtOrAfter(config, first)` is `first.StartingWith.Contains(config)`, and `StartingWith` filters on RatingMethod, which includes CarrierCode — so comparing a Hadron or Qbe config against a Topa boundary can never be true. Those four leaves silently lost all five modifiers development gave them by inheriting `…WithLwdAndWideDeductibles`: Walls In, LWD, the wide hurricane and AOP deductible bands, and the 19-item `CommercialRoofTypeV1` roof set. Losing the roof set is what produced the `EFByPerilRoofAgeFactor` errors — V2 roof names fed to a rater that rates the V1 names. Now each option set is gated on the config's own lookup version via `IsTableVersionPastV1(config, lookupName)`, which is `config.GetTableVersion(name) >= SwyfftVersion.V2`. That answers correctly for every carrier because LA Hadron/Qbe `_v1` clone `LA.Topa.V7` and TX Hadron/Qbe `_v1` clone `TX.Topa.V14`, inheriting all five bumps. `IsAtOrAfter` survives for its one remaining caller, FL Topa's gate, left alone because FL's `_v1` already sets `WindDeductible` to V2.<br><br>**New targeted exclusion hooks.** `ExcludedFactors(config)` and `ExcludedFees(config)` on `ExcelRaterValidationTestBase` skip only the value comparison, so a missing or extra row or fee still fails and everything else on that config still rates. Three entries, each with a follow-up TODO: `LimitedWaterDamage` on LA Topa V9 (rater 1, generator 0.422) and TX Topa V15 (rater 0.803, generator 1), and `PolicyFee` on FL Topa V15/V16. `ExcludedConfigs` keeps only TX Topa V1, whose rater errors out of four sheets. Eli's ruling: whole-config exclusion is the last resort; prefer the targeted hooks.<br><br>**Design corrections Eli caught in review, all applied.** An `OnCurrentStateRater &#124;&#124;` escape hatch bolted onto both gates (one switch for several features) was replaced, then its `RatesWallsIn` / `RatesLwdAndWideDeductibles` successor was also dropped, because a leaf has exactly one rater so a per-config predicate about "this leaf's rater" is incoherent — the config's lookup version is the thing that varies. `params string[] ignoreRisks` with optional parameters in front of it was reordered, since optional-before-params silently re-binds existing positional calls. `.Value ==` comparisons became `Contains` for factors and `QuoteFeeName.ParseOrDefault` for fees. Several comments restating adjacent code were deleted.<br><br>**Comment-provenance audit.** 982 comment lines added on this branch, 541 removed, 434 added with no match on development. Of 251 removed lines that exist nowhere in the tree, exactly one was a genuine loss: NC Qbe's Ordinance or Law Coverage A note, now restored. The rest were either narration development shouldn't have had, docs whose code was deleted (the pin mechanism), or rewordings and reflows that kept the meaning — line-level matching cannot tell those from deletions, which is why the raw count is misleading. Separately, seven comments were invented or truncated in this refactor and are now cut back to development's wording: the three Admitted rater-service leaves, the CBS validation leaf, the Admitted validation base, the CBS rater-service class summary, and QbeFL's ignored-perils comment restored verbatim. Artifacts: `artifacts/branch.diff`, `artifacts/novel-comments.txt`, `artifacts/removed-comments.txt`, `artifacts/lost-dev-comments.txt`, `artifacts/all-comments-now.txt`.<br><br>**The dispatcher rename.** `CommercialExcelRaterService` and `ByPerilHomeownerExcelRaterService` hold only the key dictionary, `GetConcreteRaterService`, and a `GetExcelPremiumForQuote` that resolves and delegates; all rating lives in the `ExcelRaterServiceBase` tree. Both are now `…ExcelRaterServiceDispatcher`, matching `ExcelRaterServiceDispatcherBase`. Interfaces untouched, so the DI contracts are unchanged. Both tree roots implement `IExcelRaterServiceBase<TQuote, TPremiumValues>`, whose single method is `GetExcelPremiumForQuote` — that shared contract is what lets a dispatcher stand in for a concrete rater service.<br><br>**Machine crash, 12:14 PM.** A Python loop spawning one `git grep` per removed comment line (~540 processes) was running when the machine bugchecked `0x1A` MEMORY_MANAGEMENT (`C:\WINDOWS\Minidump\082126-63453-01.dmp`). The same audit is answerable in one pass: dump every comment line with a single `git grep`, then set-difference in memory. Never spawn a subprocess per item on this repo. |
| 2026-08-21 3:10 PM | Ran the Commercial suite, traced the biggest failure group, fixed one production defect, and removed all three exclusion hooks. **Build GREEN, tree clean. New commit `a39367e29ab` (6 files, 17 insertions, 103 deletions), NOT pushed. Origin is at `ae8690c03bc`.**<br><br>**NEXT STEP: re-run the Commercial suite with no exclusions.** `Run-DotnetTest.ps1 -TicketFolder SW-53770-co-excel-validation-audit-infra-rebuild -Project Swyfft.Services.Excel.IntegrationTests -FilterTrait "TestGroup=Commercial" -IsCommercial -NoBuild` **It will be red.** Only one of the six failure groups below is fixed. That is intended: the exclusions are gone so the run gives an honest baseline, and each failure then gets sorted into the three categories in "Notes from Eli" before anything is done about it.<br><br>**Branch state at session start.** HEAD was on `feature/ek/20260821_SW-55008_sc-bic-installment-fee`, not this branch. Switched, rebuilt, ran.<br><br>**The run (26 failed, 52 passed, 33 skipped of 111, 13m 15s).** Six distinct causes across nine leaves. Output in `artifacts/tests/…filter-trait-TestGroup=Commercial_20260821-1316.txt`.<br><br><table><tr><th>Cause</th><th>Configs</th><th>Tests</th><th>Fixed</th></tr><tr><td>Limited Water Damage factor, rater discounts Water Non-Weather and the generator does not</td><td>LA Qbe V1, LA Hadron V1, TX Qbe V1, TX Hadron V1</td><td>12</td><td>pending the re-run</td></tr><tr><td>`OrdinanceOrLaw` Rates carrying that same discount downstream</td><td>LA Topa V9, TX Topa V15</td><td>8</td><td>pending the re-run</td></tr><tr><td>`Coverages.Count` 7 from the rater, 8 from C#</td><td>NC Qbe V1</td><td>4</td><td>no</td></tr><tr><td>`EFByPerilRoofAgeFactor` has no row for Asphalt Shingles / age 10 / V1</td><td>FL ClearBlueSpecialty V0</td><td>1</td><td>no</td></tr><tr><td>`MinimumPremium` 1000 or 1500 from the rater, ~23,300 from C#</td><td>TX Qbe V1</td><td>inside the above</td><td>no</td></tr><tr><td>Florida State Tax 770.68 vs 775.62, diff 4.94 against a 0.25 tolerance</td><td>FL Topa V15, V16</td><td>1</td><td>no</td></tr></table><br><br>**The Limited Water Damage change (the only fix).** `CommercialEAndSExcelRaterService.SetCoverageInputs` skipped the write when `quote.LimitedWaterDamage` was null. It now writes unconditionally, defaulting to `LimitedWaterDamage.No`. Verified by tool, not inferred: - `CommercialEAndSByPerilPremiumGenerator.GetLimitedWaterDamageRiskFactors` returns factor 1 for both null and `No`, so "No" is what the generator already treats a null column as. - `DumpRater` on the pristine `Data/LA/Commercial/EAndS/CO_ES_QBE_LA_Rater.xlsm`, Input row 58: D = "No", E = "Limited Water Damage", F = 250000. The saved failure workbook is identical, so nothing carried over between tests and test ordering is irrelevant. - Development's version of the method had the same null skip plus a `HasNamedCell` guard.<br><br>**NOT verified, and previously asserted in error.** That F58 is the cell the rater's Limited Water Damage lookup reads (the formula was never traced); that the rater's 0.636 derives from 250000; that the audit job is affected; why development's suite passed against the same null skip. The re-run is what settles whether the change fixes the group.<br><br>**`ExcludedConfigs`, `ExcludedFactors` and `ExcludedFees` all deleted**, hooks and plumbing, along with their four entries. Reasoning is in "Notes from Eli". Development coverage was checked for each entry: dev pins `TXByPerilEAndSHsicV1`, `TXByPerilEAndSQbeV1`, `LAByPerilEAndSHsicV1`, `LAByPerilEAndSQbeV1` and `TXByPerilEAndSTopaV15` with the full seven-value LWD sweep via `…WithLwdAndWideDeductibles`, and pins `FLByPerilEAndSTopaV15`/`V16` with `PolicyFee` in the fee readback. `TXByPerilEAndSTopaV1` is the exception: dev pins V2 through V15 and never covers V1.<br><br>**Coverage this branch gives up relative to development, beyond any exclusion:** config sampling. `GetConfigsForGroup` takes at most five per group where dev ran one class per config. TX Topa 14→5, FL Topa 10→5, LA Topa 9→5. Eli's call: keep it, note it in the PR description. `AcceptablePremiumDifference` is 2.0 on Commercial, matching dev, so it is not a reduction. |
| 2026-08-21 4:35 PM | Found the Limited Water Damage root cause. **It is a regression this branch introduced, in production code, and it is why the LWD group fails.**<br><br>**`WritesCoverageInputs` defaults to `false` and only FL turns it on.** On `CommercialEAndSExcelRaterService` the flag is `protected virtual bool WritesCoverageInputs => false`, `CommercialEAndSExcelRaterServiceFL` overrides it to `true`, and `CommercialEAndSClearBlueSpecialtyExcelRaterServiceFL` back to `false`. Nothing else overrides it, so LA and TX never call `SetCoverageInputs` and never write the Limited Water Damage input. Development had no such flag: it wrote the input for any rater carrying the named cell, guarded by `HasNamedCell(ByPerilName.LimitedWaterDamage) && quote.LimitedWaterDamage is { }`.<br><br>**Proven from the saved failure workbooks, not from reading code.** `DumpRater` on the `Input` sheet of both LA Qbe failures shows row 58 `F = 250000`, the rater's own shipped sample, in both. One of those two workbooks is a sweep iteration where C# expected 0.422 from a patched sublimit, so the cell was never written. Dumps in `artifacts/rater-dumps/lwd-maxbuildingvalue-input.json` and `lwd-sweep-input.json`.<br><br>**Why Excel returned two different factors from one unwritten cell.** The rater divides the sublimit by Building Value. `MaxBuildingValue` sets Building Value to 20,000,000 (`F5`), giving 0.636; the sweep iteration used 2,485,000, giving 1. Both from the same constant 250000. The apparent inversion between the one-off tests and the sweep was Building Value moving, never anything about LWD itself.<br><br>**The `?? LimitedWaterDamage.No` change in `a39367e29ab` is inert** for LA and TX, because the whole `SetCoverageInputs` call is gated off for them. That is why the run's 29 distinct factor pairs were identical to the previous run's.<br><br>**Blast radius: this is not test-only.** The audit job resolves the same rater services through the dispatcher, so LA and TX audit documents rate Limited Water Damage off the rater's shipped sample too.<br><br>**Two process failures on the way here, both mine, both avoidable.** 1. Eli stated repeatedly that the whole Commercial suite passes on development. That statement was treated as a hypothesis and re-proven with a full `development` build plus a `CommercialEAndSByPerilRaterValidationLAQbeV1` run (25 passed, 0 failed, artifact `…_dev-baseline_20260821-1620.txt`). It cost a 10-minute build and a 40 GB worktree to confirm something already known. A user's factual statement about the repo is a given, not a claim to verify. 2. `Swyfft.Services.Excel.IntegrationTests/Commercial/AGENTS.md` opens with "Diagnosing a failure — trace the saved workbook, do NOT guess", and Eli said the same thing directly. Many turns went into deducing the cause from source anyway, producing several wrong theories. The `DumpRater` dump answered it in one command. Trace the workbook first, always. |
| 2026-08-21 5:20 PM | Limited Water Damage fixed, committed and pushed. **Commit `d4f2b3161e7` (5 files, 36 insertions, 13 deletions). Origin and the branch are both at `d4f2b3161e7`; nothing is unpushed.** The 3:10 PM entry's claim that `a39367e29ab` was unpushed was stale by the time of this push: origin already held it.<br><br>**The fix.** `WritesCoverageInputs` gated two unrelated inputs behind one flag and only FL set it. Replaced by one flag per rater cell, `WritesRoofSystemsPaymentSchedule` and `WritesLimitedWaterDamage`, with `SetCoverageInputs` split into `SetRoofSystemsPaymentScheduleInput` and `SetLimitedWaterDamageInput`. Values come from the named-range dumps, not from inference: the nine FL, LA and TX raters (Topa, Hadron, Qbe) carry `LimitedWaterDamage` and `RoofSystemsPaymentSchedule`; CBS FL, Dorchester MS, Qbe NC/NJ/NY/SC and Topa AL carry neither. Every rater that has one has both, so the two flags hold equal values today.<br><br>**Result: 26 failures to 16, 52 passes to 62, none new.** `HadronLA`, `HadronTX`, `QbeLA` and `TopaLA` fully pass. Zero `LimitedWaterDamage` mismatches remain. `TX.TOPA.V15` and `LA.TOPA.V9`, the two configs the deleted `ExcludedFactors` hook had entries for, now pass unaided. Nothing surfaced from the waterfall rows below LWD that the first-failure abort had been masking. Artifact: `artifacts/tests/…_split-flags_20260821-1702.txt`.<br><br>**Remaining 16, four causes, none yet categorised except TX Topa V1:**<br><br><table><tr><th>Config</th><th>Cause</th></tr><tr><td>`TX.TOPA.V1` (17/19)</td><td>`GlCoverageOutput` `#VALUE!` cascade, roots on Input I6/I8. Category 3, permanent-exclusion profile</td></tr><tr><td>`NC.Qbe.V1` (19/19)</td><td>rater readback 7 coverages, C# 8</td></tr><tr><td>`FL.CBS.V0` (11/19)</td><td>C# throws before Excel: `EFByPerilRoofAgeFactor` has no row for `Asphalt Shingles` or `Clay/Concrete Tile`</td></tr><tr><td>`TX.Qbe.V1` (19/19)</td><td>`MinimumPremium` rater 1000-1500, C# ~23,300</td></tr><tr><td>`FL.TOPA.V15`, `V16` (1/19 each)</td><td>Policy Fee rater 300, C# 400, tolerance 0.25</td></tr></table><br><br>LWD turned out to be a declared-flag miss introduced by this branch, so `NC.Qbe`'s coverage count and `FL.CBS`'s roof set are the two most likely to be the same class of regression. The method that found it is the one to repeat: dump the saved failure workbook, then compare the branch's declarations against development's `HasNamedCell` behaviour for that rater.<br><br>**Worktree.** Work happened in `.claude/worktrees/agent-af99f06943b746476` because Eli's checkout was on another branch. It is detached at `d4f2b3161e7` so the branch is free. Eli's instruction: keep one worktree and reuse it by detaching, never spawn a second. Disk is tight, roughly 31 GB free with the worktree occupying 40 GB, and a second worktree failed to create for that reason. |
| 2026-08-21 6:05 PM | Two more lost declarations found and fixed. **Commit `f272614de90` (2 files, 23 insertions), pushed. Branch and origin both at `f272614de90`.**<br><br>**Suite: 16 failures to 8, 62 passes to 70, none new.** `QbeNC` and `QbeTX` fully pass, and `TX.TOPA.V15` clears as well, leaving `TopaTX` failing only on V1. Artifact: `artifacts/tests/…_nc-tx-fixes_20260821-1745.txt`.<br><br>**NC QBE, terrorism property.** The rebuilt `CommercialEAndSQbeExcelRaterServiceNC` dropped development's `GetAdditionalPremiumValues`, which reads the `TerrorismProperty` cell and charges it as `Coverages[ByPerilName.Terrorism]`. That key is distinct from the `TerrorismCoverage` in `CoverageNames`, so the readback held 7 coverages against the generator's 8 and every NC test failed on the count, constant across all iterations. Restored to match `CommercialEAndSQbeExcelRaterServiceNY`, which still carries it.<br><br>**TX, minimum-premium inputs.** `SetMinimumPremiumInputs` writes `Carrier`, `County` and `DistanceToCoast`, and the named-range dumps show both TX raters carry all three, but `WritesMinimumPremiumInputs` was true only on FL. TX priced its minimum off the workbook's sample values, 1000 or 1500 against the generator's ~23,300. Set true on `CommercialEAndSExcelRaterServiceTX`. LA and CBS FL carry none of the three and stay false; NC's `DistanceToCoast` is a `#REF!`, so NC stays false too.<br><br>**Four regressions now found, all one pattern.** The rebuild replaced development's runtime `HasNamedCell` checks with hand-declared flags and per-leaf overrides, and each time a rater was missed the rater silently kept the sample value the workbook ships with: Limited Water Damage on LA and TX, Roof Systems Payment Schedule on LA and TX, minimum-premium inputs on TX, terrorism property on NC. All four are production code the audit job runs through the dispatcher, not test-only. Any remaining failure should be checked against this pattern first.<br><br>**Remaining 8, three causes.**<br><br><table><tr><th>Config</th><th>Tests</th><th>Status</th></tr><tr><td>`TX.TOPA.V1`</td><td>6</td><td>Category 3. Development pins V2 through V15, never V1. `GlCoverageOutput` `#VALUE!` rooted on Input I6/I8</td></tr><tr><td>`FL.CBS.V0`</td><td>1 (11/19)</td><td>Category 3. Development's Excel tests pin only V18, V20 and V21; `git grep` finds no reference to `FLByPerilEAndSClearBlueSpecialtyV0`. Seeded roof-age data has no row for the roof types the sweep feeds</td></tr><tr><td>`FL.TOPA.V15`, `V16`</td><td>1 (1/19 each)</td><td>Open. Policy Fee rater 300, C# 400. Not a lost declaration: FL's version map matches development's entry for entry, and development pins both configs</td></tr></table><br><br>Both category 3 cases come from `GetConfigsForGroup` sampling the oldest config in a group, which development never covered. Both fit a permanent exclusion in HO's `EachElementOptionStartingFrom` style rather than a temporary one carrying a ticket. |
| 2026-08-21 7:10 PM | **SESSION CLOSE (superseded: the newest row carries the current next step).**<br><br>**State: branch and origin both at `aaf512f3fd7`. Build green. Nothing uncommitted, nothing unpushed.** Three commits landed this session: `d4f2b3161e7`, `f272614de90`, `aaf512f3fd7`.<br><br>## NEXT STEP WHEN ELI RETURNS<br><br>Run the Commercial suite **in Eli's own checkout**, not a worktree. The agent worktree used all session was deleted at close, so any path under `.claude/worktrees/` no longer exists.<br><br>1. Check out `feature/ek/20260818_SW-53770_co-validation-audit-infra` in the main checkout, `C:\Users\eli.koslofsky\Documents\GitHub\swyfft_web`. 2. Full build first. That checkout has never built this branch, so expect roughly 10 minutes: `pwsh ~/.claude/scripts/Build-Solution.ps1` (background it, and do not pipe it to `tail` or the script's exit code is lost). 3. Then, roughly 13 minutes: `Run-DotnetTest.ps1 -TicketFolder SW-53770-co-excel-validation-audit-infra-rebuild -Project Swyfft.Services.Excel.IntegrationTests -FilterTrait "TestGroup=Commercial" -IsCommercial -NoBuild`<br><br>**Expected: 8 failures down to 1.** The two starting-from floors added in `aaf512f3fd7` should clear TX Topa's six tests and FL ClearBlueSpecialty's one, leaving only FL Topa's Policy Fee.<br><br>## The one open failure<br><br>`FL.TOPA.ByPeril.EAndS.V15` and `V16`, 1 of 19 iterations each. Policy Fee: rater 300, C# 400, tolerance 0.25. Not a lost declaration: FL's version-cell map matches development's entry for entry, and development pins both configs and passes. Input-dependent, since only one iteration of nineteen fails. Undiagnosed.<br><br>## Four production regressions found and fixed, all one pattern<br><br>This branch replaced development's runtime `HasNamedCell` checks with hand-declared per-rater flags and per-leaf overrides. Every rater missed by a declaration silently kept the sample value its workbook ships with. All four are production code the audit job runs through the dispatcher, so each was mispricing or misreporting outside the tests too. **Check any future failure against this pattern first.**<br><br><table><tr><th>Lost declaration</th><th>Raters</th><th>Effect</th></tr><tr><td>Limited Water Damage input</td><td>LA, TX</td><td>Rater rated LWD off the $250,000 sample in the workbook</td></tr><tr><td>Roof Systems Payment Schedule input</td><td>LA, TX</td><td>Same gate, same miss</td></tr><tr><td>Minimum-premium inputs (`Carrier`, `County`, `DistanceToCoast`)</td><td>TX</td><td>Minimum came out 1000 or 1500 against the generator's ~23,300</td></tr><tr><td>Terrorism-property coverage readback</td><td>NC Qbe</td><td>Readback held 7 coverages against the generator's 8</td></tr></table><br><br>**How the Limited Water Damage one was proved**, since the method is the one to repeat: `DumpRater` on the `Input` sheet of two saved failure workbooks showed row 58 `F = 250000` in both, including a sweep iteration that had patched a real sublimit. So the cell was never written. The apparent inversion between test types (rater discounting when C# did not, and the reverse) was Building Value moving between 20,000,000 and 2,485,000 against that one constant, nothing to do with LWD.<br><br>## The three commits<br><br>- **`d4f2b3161e7`** — split `WritesCoverageInputs` into `WritesRoofSystemsPaymentSchedule` and `WritesLimitedWaterDamage`, split `SetCoverageInputs` to match, set both per rater from the named-range dumps. Nine raters (FL, LA, TX by Topa, Hadron, Qbe) carry both cells; CBS FL, Dorchester MS, Qbe NC/NJ/NY/SC and Topa AL carry neither. **26 failures to 16.** - **`f272614de90`** — restored NC Qbe's `GetAdditionalPremiumValues` reading `TerrorismProperty` into `Coverages[ByPerilName.Terrorism]`, matching the NY Qbe sibling that still had it; set `WritesMinimumPremiumInputs => true` on TX. **16 failures to 8.** `TX.TOPA.V15` cleared as well. - **`aaf512f3fd7`** — deleted `RunForAllConfigs`; made `RunTestForAllConfigs` virtual; Commercial overrides it to call `SkipIfStateRetired()` before the base; twelve call sites now pass their own config list; `Customize` widened to `protected static`; new `CommercialScenarioTestsStartingFrom`; floors set on two leaves. **Not yet run.**<br><br>## Why `RunForAllConfigs` went away<br><br>It wrapped the shared `RunTestForAllConfigs` but hardcoded `GetConfigsForGroup()` with no argument, so no Commercial test could choose a config range the way every Homeowner site already does. The name was wrong twice: it did not run all configs, since `GetConfigsForGroup` samples at most five, and it sat one word away from the shared runner it wrapped.<br><br>Homeowner's pattern is per-test starting-from (`EachElementOptionStartingFrom`, `CheckRoofAreaStartingFrom`, `FortifiedRoofReplacementStartingFrom`) with the config list passed at each site. Commercial now matches. There is deliberately **no** single leaf-wide floor.<br><br>`SkipIfStateRetired()` was left in place at the top of `EachElementOption_ShouldBeExpected` even though the override makes it redundant. It runs before `RunEachElementOptionSweep`'s `Assert.Fail("No configs found for this test group")`, so for a retired state whose group has no configs it is the difference between a skip and a failure. The three retired leaves (ClearBlue IL, NY, WA) all still have configs today, so removing it would be safe now and would drop that guard.<br><br>## The two starting-from floors<br><br><table><tr><th>Leaf</th><th>Property</th><th>Config</th><th>Basis</th></tr><tr><td>`CommercialEAndSValidationTestsTopaTX`</td><td>both, via a shared `OldestSupported` field</td><td>`TXByPerilEAndSTopaV2`</td><td>development pins V2 through V15, never V1; V1's rater errors out of four sheets</td></tr><tr><td>`CommercialEAndSValidationTestsClearBlueSpecialtyFL`</td><td>`EachElementOptionStartingFrom` only</td><td>`FLByPerilEAndSClearBlueSpecialtyV18`</td><td>development pins V18, V20, V21 and nothing older; V0's seeded roof-age data has no rows for the roof types fed</td></tr></table><br><br>Both verified by grepping development's Excel test project for every config name in each group.<br><br>**Known cost, flagged and accepted:** CBS's floor at V18 drops V0 through V17, which includes a mid-range config the sampling had been running and passing. Nothing in that span is covered on development either, so Eli's bar of no-less-than-development is met. Dropping V0 alone would mean a floor at `FLByPerilEAndSClearBlueSpecialtyV1WithoutMasonry`.<br><br>## Run history<br><br><table><tr><th>Artifact suffix</th><th>Failed / Passed / Skipped</th><th>Note</th></tr><tr><td>`…TestGroup=Commercial_20260821-1516`</td><td>26 / 52 / 33</td><td>exclusions removed, LWD write change inert</td></tr><tr><td>`…_split-flags_20260821-1702`</td><td>16 / 62 / 33</td><td>after `d4f2b3161e7`</td></tr><tr><td>`…_nc-tx-fixes_20260821-1745`</td><td>8 / 70 / 33</td><td>after `f272614de90`</td></tr><tr><td>`…_dev-baseline_20260821-1620`</td><td>0 / 25 / 0</td><td>`CommercialEAndSByPerilRaterValidationLAQbeV1` on development</td></tr></table><br><br>No run ever produced a newly failing test. The 33 skips are the retired-state guards, unrelated.<br><br>## Two process failures worth not repeating<br><br>1. Eli stated repeatedly that the Commercial suite passes on development. That was treated as a hypothesis and re-proven with a full `development` build plus a test run. A user's factual statement about the repo is a given, not a claim to verify. 2. `Swyfft.Services.Excel.IntegrationTests/Commercial/AGENTS.md` opens with "trace the saved workbook, do NOT guess", and Eli said the same directly. Many turns went into deducing the cause from source anyway, producing several wrong theories in sequence. One `DumpRater` command answered it. **Trace the workbook first, always.**<br><br>## Worktree<br><br>Deleted at session close and not needed again. All work happened in `.claude/worktrees/agent-af99f06943b746476` because Eli's checkout was on another branch. Eli's standing instruction: keep one worktree and reuse it by detaching, never spawn a second. Disk is tight, and a second worktree failed to create for exactly that reason. Note that `git worktree remove --force` on a built worktree exceeds a 2-minute foreground timeout, so background it. |
| 2026-08-24 10:11 AM | Merged `development` into the branch before the pending suite run. **Merge commit `9616f9f05f7`, 326 commits, no conflicts, tree clean, NOT pushed.** Switched the main checkout from `feature/ek/20260821_SW-55072_SW-55074_remove-mep-bsic-sc-and-direct-repair-es` (clean) onto this branch; the worktree is gone, so all remaining work happens in the main checkout.<br><br>**The merge cannot move the Commercial suite.** Scoped `git log aaf512f3fd7..origin/development` shows the only `development` commits touching `Swyfft.Services.Excel`, `Swyfft.Services.Excel.IntegrationTests` or `Swyfft.Console.Base` are SW-54939's ZenDesk-to-IMS ticket archiving backfill, and none at all touching `Swyfft.Services/Premium/Commercial`, `Swyfft.Services/Common/Commercial` or `Data/Commercial`. A failure in the coming run is still attributable to `aaf512f3fd7`.<br><br>**Next: full build, then the Commercial suite.** Expected 8 failures down to 1. |
| 2026-08-25 10:28 AM | Merged `development` again before the still-pending suite run. **Merge commit `0e49074a2a0`, 122 commits, no conflicts, tree clean, NOT pushed.** The prior day's merge `9616f9f05f7` is on origin. Switched the main checkout from `feature/ek/20260824_SW-55130_SW-55163_qbe-es-cov-a-and-year-built` (clean) back onto this branch.<br><br>**This merge cannot move the Commercial suite either.** Scoped `git log 9616f9f05f7..origin/development` found two commits in relevant paths, both inert here: SW-55077 (#b379d185e21) touched only `Swyfft.Console.Base/CommandLineSettings.cs`, adding command-line options, nothing in the Excel rating path; SW-43116 (#15a1c6ac4bb) touched `CopyQuoteToActor.cs` and its unit tests, which the validation tests never reach since they create quotes directly through `CommercialQuoteGenerator.CreateCommercialQuote`. Nothing landed in `Swyfft.Services/Premium/Commercial`, `Swyfft.Services/Common/Commercial` or `Data/Commercial`.<br><br>**Next: full build, then the Commercial suite.** Expected 8 failures down to 1. |
| 2026-08-25 10:50 AM | Ran the Commercial suite after the second `development` merge. Build green, 0 errors. **1 failed / 77 passed / 33 skipped of 111, 11m 51s — down from 8 failures, none new.** HEAD is merge commit `0e49074a2a0`, unpushed. Artifact: `artifacts/tests/…_filter-trait-TestGroup=Commercial_post-dev-merge_20260825-1038.txt`.<br><br>**Both starting-from floors from `aaf512f3fd7` worked.** TX Topa's six tests and FL ClearBlueSpecialty's one are green, and the twelve rewritten `RunTestForAllConfigs` call sites produced no new failure.<br><br>**The sole survivor is the known Policy Fee failure**, unchanged in shape: `CommercialEAndSValidationTestsTopaFL.EachElementOption_ShouldBeExpected`, 2 of 5 configs (`FL.TOPA.ByPeril.EAndS.V15` and `V16`), index 16 of 19 on each. Excel reads Policy Fee 300, C# charges 400, against a 0.25 tolerance. Still undiagnosed. Failure workbooks in `%TEMP%\1\Swyfft\CommercialValidationTests\`: `CO_ES_TOPA_FL_Rater_2026.08.25.02.48.52.458.xlsm` (V15 index 16) and `CO_ES_TOPA_FL_Rater_2026.08.25.02.49.53.871.xlsm` (V16 index 16).<br><br>**Next: trace those two workbooks with `DumpRater` before reading any code.** Index 16 is the only failing iteration of nineteen, so the input that iteration feeds is what to find. |
| 2026-08-25 10:55 AM | **DIAGNOSED the FL Topa Policy Fee failure. Awaiting a disposition decision.**<br><br>Traced from the two saved failure workbooks with `DumpRater`, per the Commercial AGENTS.md, before reading any code. Dumps in `artifacts/rater-dumps/policyfee-v1{5,6}-idx16-{fees,rating}.json`. The two workbooks' `Fees` sheets are byte-identical, so V15 and V16 are one case, not two.<br><br>**Neither side failed, and one of them is wrong.** No Excel error, no lookup miss, no exception: each side followed the rule written into it and produced a number, and the rules put the 15,000 boundary in different places. Premium before fees and tax is 15000.775 on both (`Rating_Algorithm!B74`), and `PolicyFee_Version` reads V4.<br><br><table><tr><th>Side</th><th>Rule applied to 15000.775</th><th>Fee</th></tr><tr><td>C# `CommercialQuoteFeesEAndS.GetScalingPolicyFeeV3`</td><td>`<= 15_000M` is false, so the next arm `<= 25_000M` wins</td><td>400</td></tr><tr><td>Rater `Fees!C12` then `Fees!F6`</td><td>approximate `VLOOKUP` over band **start** values 0 / 5001 / 15001 / 25001 … picks 5001, and `VLOOKUP("V4"&5001, I3:M23, 5)` reads the 5001–15000 band</td><td>300</td></tr></table><br><br>**The rater's band table contradicts itself for fractional premiums.** Its `B15:C21` bucket table declares the band as 5001 through 15000, yet the approximate `VLOOKUP` keyed on start values puts a 15000.775 premium inside it, because the next start, 15001, is greater than the premium. Every premium strictly between a band's declared end and the next band's start hits this: (15000, 15001), and likewise (5000, 5001), (25000, 25001), (50000, 50001), (100000, 100001), (200000, 200001). C# bands on `<=` boundaries with no gap, so C# always takes the higher band there.<br><br>**Not test-only.** The audit job runs this same rater through the dispatcher against this same C#, so a purchased FL Topa quote whose premium lands in one of those gaps produces an audit-doc fee mismatch of 100 or more.<br><br>**Category 2 reached through category 3 coverage.** The test fed a valid input and both sides rated, so it is not a test-infrastructure defect. `RawAnnualPremium` is a `decimal` and neither side rounds it; Flood's calculator does round (`FloodQuoteFeesCalculatorBase` uses `RawAnnualPremium.RoundTo(0)`), Commercial's does not. |
| 2026-08-25 12:35 PM | **FULL COMMERCIAL SUITE GREEN. 111 total: 0 failed, 78 passed, 33 skipped, 12m 16s.** Artifact: `artifacts/tests/…_filter-trait-TestGroup=Commercial_addr-FL036_20260825-1223.txt`. The 33 skips are the three retired states (ClearBlue IL, NY, WA). Progression across the branch: 26 failures, 16, 8, 0. HEAD is still the `development` merge `0e49074a2a0`; the two changes below are uncommitted.<br><br>**The FL Topa Policy Fee failure was a test-address artifact, and the ticket for it was deleted.** SW-55253 was created for the band mismatch and then deleted (`DELETE /api/issues/SW-55253` → 200; a read-back returns 404). Eli's ruling: FL Topa is renewal-only with one policy still renewing, so a sub-dollar band edge on it does not earn a ticket.<br><br>**What the failure actually was.** Development gave every FL Topa config its own address (`CommercialEAndSByPerilRaterValidationFLTopa.cs`: V15 → `GoodTestAddressFL036`, V16 → `GoodTestAddressFL039`, V17 → `GoodTestAddressFL040`, and so on for ten configs). This branch has one leaf per carrier, so one address covers every sampled config, and it was set to `GoodTestAddressFL040`, development's V17 address. At that address V15 and V16 rated to a premium before fees of 15000.775, which sits in a one-dollar gap the two sides resolve differently:<br><br>- The rater's `Fees!C12` is `VLOOKUP(PremiumBeforeFeesTaxes,B15:C21,1,TRUE)`, which takes the largest band **start** not exceeding the premium. The starts are 0, 5001, 15001, 25001, 50001, 100001, 200001, so 15000.775 resolves to 5001 and `Fees!F6` gives 300. - `CommercialQuoteFeesEAndS.GetScalingPolicyFeeV3` switches on upper bounds, so 15000.775 exceeds `<= 15_000M` and `<= 25_000M` wins, giving 400.<br><br>Neither side rounds, and the fee amounts are identical band for band. Only the breakpoints differ, by one dollar. Both sides are byte-identical to development (`GetScalingPolicyFeeV3` bands match; the FL Topa rater is the same git blob `2bea33c48bf88c795858918fb1c17e3041b47573`), so the mismatch exists on development too. Development never hit it because its V15 and V16 addresses produced premiums outside the gap.<br><br>**Proven by experiment, at Eli's direction.** Setting `CommercialEAndSValidationTestsTopaFL`'s `TestAddress` to `GoodTestAddressFL036`, development's V15 address, with nothing else changed, turned the leaf green (6/6, artifact `…_addr-FL036-experiment_20260825-1212.txt`). That address is now the permanent value with no comment on the line: any valid address works, and the dev tests already use this one.<br><br>**One address per test class is a hard floor, not a preference.** `CommercialTestHelpers.ResetCommercialAddressKey` states "only a single reset throughout a test run session is allowed as otherwise we will have a race condition", and enforces it by recording the first test class to reset each key and throwing for any other class that resets the same key. Hoisting `TestAddress` onto a state base to share one address across carrier leaves would make the first leaf pass and the rest throw. Addresses scale with test classes, not configs, which is why development needed ten FL Topa addresses and this branch needs one.<br><br>**`EAndSIgnoredRisks` TODO removed.** The five-peril ignore list is exactly what development does: its `CommercialByPerilRaterValidationTestBase` ignores the same five for E&S, with the same carve-out returning `Array.Empty<string>()` for FL configs that are not on the ISO rater. The branch reproduces that class-based: E&S base gets the five, `CommercialEAndSValidationTestBaseFL` gets `[]`, `CommercialEAndSValidationTestsQbeFL` goes back to the five and `…HadronFL` inherits it. The TODO claimed the list "may hide more than it needs to" and that nobody had rechecked it since SW-10397; both were unverified. The summary now carries development's explanation instead.<br><br>**One `TODO (SW-53770 follow-up)` left on the branch:** `CommercialEAndSIsoRaterExcelRaterServiceFL.cs:44`, the FL ISO rater's `WHDeductibleVersion` cell reads V2 and C# never writes it. `VersionsSheet_AllVersionCellsShouldBeWrittenByCSharp` in stage 3 commit 5 is what would catch it, and stage 3 is inside the cut rule, so it needs its own ticket if the PR is called full at the end of stage 2.<br><br>**Uncommitted:** the FL Topa `TestAddress` change and the `EAndSIgnoredRisks` comment rewrite. |
| 2026-08-25 12:49 PM | Converted the Progress section to the table `Add-ProgressEntry.ps1` owns, per Eli's ruling. `# Progress` became `## Progress`, all 23 prose entries became rows sorted oldest first so the script's appends land at the bottom, nested tables became inline HTML and code fences became `<pre>`. Verified: entry count, per-entry content identity after normalization, and no stray pipes. Three entries had been hand-written with a bare date; their times now come from real sources, the two `development` merge commits' author dates and a rater dump's mtime. From here every entry goes through this script. |
| 2026-08-25 1:04 PM | **Part 1 PR created: #22439** (`feature/ek/20260825_SW-53770_co-validation-part1` at `fc9fb446434`, base development). Title carries Part 1, so the merge workflow leaves SW-53770 in Develop, per the approved description. Body in `artifacts/pr/part1-body.md`. The branch was cut fresh off the merge commit `0e49074a2a0`'s parent state because the original commit message was rejected; the old branch `feature/ek/20260818_SW-53770_co-validation-audit-infra` was deleted locally and on origin. Adversarial review ran pre-PR: no HO regression found; its one Major (unverified `WritesMinimumPremiumInputs` on QBE NJ/SC, Topa AL, Dorchester MS) is deliberately left to stage 3's Input sentinel check, which fails on any unwritten cell by construction. Next: the remaining stages (sentinel checks, dynamic value discovery) as follow-up Part N PRs. |
| 2026-08-25 2:15 PM | Restructured the plan for the multi-PR model, compact-ready. The commit-stages section became a Delivered historical record plus a **Remaining work, ranked** list (1 sentinel checks, 2 CO captured-assert baselines as their own Part N PR, 3 dynamic value discovery, 4 promote AssertCarrierSpecificPremiums, 5 split ByPerilExcelTestHelpers' HO-only members). Every forward-looking stage/commit number is gone from the plan body; Progress rows and git SHAs stay as history. Work proceeds in priority order and Eli may stop at any point; each shipped chunk is a Part N PR. NEXT ON RETURN: remaining-work item 1, CO sentinel checks, opening with the DumpRater feasibility checkpoint on CO Input/Versions layouts. Branch: feature/ek/20260825_SW-53770_co-validation-part1 at fc9fb446434, clean, pushed; PR #22439 open. |
| 2026-08-25 2:44 PM | Addressed all three Copilot comments on PR #22439; every thread replied to and resolved. Declined the `Value[^2..]` slicing comment (Eli's ruling: a policy number is never under two characters, and a throw there would be correct); fixed the other two: token-less `SaveChangesAsync()` under the xUnit1051 pragma in `ExcelQuoteAuditServiceTestBase`, and the unused Homeowner using dropped from `CommercialPatchModifiers`. Build green; audit tests 4/4. **Commit `822eb46e30f`, pushed.** No unresolved feedback remains on the PR. |
| 2026-08-27 11:31 AM | Remaining-work item 1 (CO sentinel checks) complete and COMMITTED: 67430b6ebdf (21 files, 147 insertions, 5 deletions) on branch feature/ek/20260825_SW-53770_co-validation-part2, NOT pushed. Suite fully green: 149 total, 0 failed, 110 passed, 39 skipped (retired IL/NY/WA), 13m 22s. Artifact: artifacts/tests/...TestGroup=Commercial_exclusions-displayname_20260827-1116.txt. Delivered: the two sentinel [Fact]s on CommercialRaterValidationTestBase (SkipIfStateRetired first); input writes where the rater names the cell (WritesWindMitigationTable on 9 services, WritesNamedStormDeductible flag on the E and S base with true on the FL ISO chain/NJ/NY, WritesWindConstructionProgram on AL); version mappings WHDeductibleVersion on the FL ISO service (closes the last SW-53770 follow-up TODO) and WallsInCoverage on LA; ExcludedInputLabels for the unnamed-and-unread cells (territory trio, Named Storm Deductible on FL Topa/LA/TX) via .DisplayName constants on CommercialEAndSValidationTestBase; SW-53916 run-off Topa RoofSystemsPaymentSchedule excluded on the three Topa leaves via ExcludedVersionMismatchFactors, HO's mechanism. Key facts learned: ByPerilName Value is the member name and DisplayName is the sheet label; formulas reference Input cells only via defined names on these raters (verified by full-workbook dumps); territory-code Input rows are unnamed and unread on every rater outside the FL unified pair. NEXT: Eli calls whether this ships as the Part 2 PR or work continues to ranked item 2 (CO captured-assert baselines). |
| 2026-08-27 11:36 AM | Plan made compact-ready after the sentinel commit: the CO sentinel work moved from Remaining work into Delivered (full as-built detail there), the ranked list renumbered to 1 captured-assert baselines, 2 dynamic value discovery, 3 promote AssertCarrierSpecificPremiums, 4 split ByPerilExcelTestHelpers. Eli's ruling: the Part 2 PR gets MORE than the sentinel work before it ships. State: branch feature/ek/20260825_SW-53770_co-validation-part2 at 67430b6ebdf, clean, NOT pushed; origin still at 822eb46e30f; PR #22439 (Part 1) open. NEXT ON RETURN: re-read the plan in full plus the mandated pre-reads, then start ranked item 1, CO captured-assert baselines: declare the RaterFileContents capture [Fact] on the CO side (the core RunRaterFileContentsCapture exists on ExcelRaterValidationTestBase, opt-in by declaring the fact), generate baselines, review them, and run with UPDATE_TEST_EXPECTED_RESULTS off to prove stability. |
| 2026-08-27 12:09 PM | Plan cleanup per Eli's order: deleted the whole Unverified items section (the renewal-term item named Commercial plumbing that does not exist - GetPolicyTermFailOpenOnImsDown has no Commercial caller and RenewalTerm lives on ResidentialQuoteFeesData; the five-subclassed-states item was never actionable; the other two were resolved by delivered work). Deleted the research-record sibling line about prod audit outcomes. Corrected the dispatcher as-built to current shape: FallbackRaterService removed from code (grep: zero references), CommercialExcelRaterServiceDispatcher has 19 entries and throws on a miss, DI is ICommercialExcelRaterService -> dispatcher at SwyfftExcelTask.cs:30 and CommercialRaterValidationTestBase.cs:79. Recorded Part 1 PR #22439 merged 2026-08-26. Retired Admitted configs CAByPerilAdmittedClearBlueV1 and NJByPerilAdmittedClearBlueV1/V2/V3 have no dispatcher entry (noted in the as-built, no action). |
| 2026-08-27 12:17 PM | Plan audit (eli--plan-audit) run against current rules; type gate passed (Feature). Fixes: research-record header now labeled planning-time snapshot superseded by Delivered/as-built; 73d02c554ff as-built header marked partially superseded by the rebuild; HO dispatcher renamed in as-built to ByPerilHomeownerExcelRaterServiceDispatcher (class read at :22-26); CO audit-test as-built registrations replaced with the current four (file lines 23-28) and the FL-Topa-via-fallback claim re-tensed with the current (FL, EAndS, Topa) -> CommercialEAndSTopaExcelRaterServiceFL mapping; tests-table base fixed to CommercialRaterValidationTestBase (old name matches no class, grep empty); transition step de-staled (Part-1 flag instruction removed, title format now Part N, Review move scoped to the final part per AC F); duplicate merged-PR line removed; Eli's 2026-08-27 rulings recorded on ranked items (1 and 2 own PRs; 3 and 4 candidate Part 2 riders, discussion pending). Verified clean: no deferred-decision phrases, all 13 pre-read paths exist, ExcludedInputLabels default is Policy Number, CommercialPurchaseServiceTestsFL exists, Run-DotnetTest flags match prior green runs. |
| 2026-08-27 1:01 PM | Ranked item 3 (promote AssertCarrierSpecificPremiums) complete and COMMITTED: 4dd504f93a2 (4 files, +13/-9) on feature/ek/20260825_SW-53770_co-validation-part2, NOT pushed. AssertNonHurricaneWindAndHailAreZeroWhenExcluded now runs in the shared CompareAdditionalPremiums (helper narrowed to private); QBE NC/NY overrides deleted; QBE FL's override keeps only the hurricane guard. First run uncovered 2 failures (NJ.Qbe.ByPeril.EAndS.V1 and TX.TOPA.ByPeril.EAndS.V2, even sweep indices, wind/hail premiums non-zero under exclusion); root: the generators' explicit gate rates WindHailExclusion-lookup-V1 configs as Included (CommercialEAndSByPerilPremiumGeneratorCombinedDeductible + TopaTX, from SW-52867/SW-51860 commit 4dac189a5fa), rater agrees (comparison green). Disposition per Eli 1a: assert skips when quote.GetConfig().LookupVersions.GetVersion(ByPerilName.WindHailExclusion).SingleVersion == SwyfftVersion.V1, mirroring the production gate. Reruns green: QbeNJ 6/6, TopaTX 8/8 (artifacts ...windhail-gate-nj/-topatx_20260827). Known coverage give-up: LA Topa's generator zeroes ungated, so LA configs at lookup V1 skip an assert that would pass. NEXT: item 4, HomeownerByPerilExcelTestHelpers split (name approved 1a), then Eli calls the Part 2 cut. |
| 2026-08-27 1:23 PM | Ranked item 4 complete and COMMITTED: dce82331184 (17 files, +124/-115), NOT pushed. Shape changed from the plan's separate-class idea per Eli: CoverageBCDV1Skip and GetDynamicElementValues moved verbatim into a nested static Homeowner class inside ByPerilExcelTestHelpers (a first separate-file attempt was abandoned mid-edit on Eli's order and fully reverted). 16 reference sites repointed to ByPerilExcelTestHelpers.Homeowner. The file has no Commercial-specific members (grep: zero Commercial references), so no Commercial nest exists. Process fix that mattered: earlier sed/python passes stripped BOMs and flipped line endings, rendering diffs as whole-file rewrites in GitHub Desktop; byte-identity outside real changes was restored (BOM-fixed 15 files) and the final diff is three hunks, 103/95 on the shared file. Green bar per Eli's ruling: compilation only (pure compile-time relocation, no reflection or string lookup of the members) - Build-Solution green, 0 errors. Branch now holds 3 unpushed commits: 67430b6ebdf sentinels, 4dd504f93a2 wind/hail promotion, dce82331184 nesting. NEXT: all four ranked items done or dispositioned (1 and 2 own PRs); Eli calls the Part 2 cut and the post-test-approval sequence follows. |
| 2026-08-27 2:23 PM | Part 2 PR created: #22491 (feature/ek/20260825_SW-53770_co-validation-part2 at f7118e17bba, base development). Adversarial review ran pre-PR and found one Major: the wind/hail V1-exclusion skip (commit 4dd504f93a2) keyed only on the lookup version, which returns V1 both for a factor at its true version-1 vintage AND for a factor the lookup never mentions at all - so it silently disabled the assert on NC/NY/FL/SC/NJ, carriers whose generators zero wind/hail unconditionally and where the assert had run since SW-54466. Fixed in f7118e17bba: added GeneratorKeepsWindPremiumOnV1Exclusion (default false, assert runs), true only on CommercialEAndSValidationTestsTopaTX and CommercialEAndSValidationTestsQbeNJ, the two families whose generators actually gate on that lookup version. Reruns green: QbeNJ 6/6, TopaTX 8/8. One post-review fix commit, no second review, per plan-mode. PR body drafted, fact-check-writing audited (3 passes, corrected a production-audit-job misframing per this ticket's own AC B), approved, posted. SW-53770 Stage left at Develop - Part 2 is not marked final in the title, so per AC F the story does not move to Review yet. NEXT: SW-53770 Part 2 is done pending Eli's PR review / CI. Items 1 (CO captured-assert baselines) and 2 (CO dynamic value discovery) remain as their own future PRs, not started. |
| 2026-08-27 4:35 PM | Plan made compact-ready after the Part 2 PR. Ranked items 3 and 4 moved from Remaining work into Delivered, since both shipped in #22491: the wind/hail exclusion assert promotion (4dd504f93a2 scoped by f7118e17bba, including the full record of the review-found trap where GetVersion returns V1 both for a version-1 vintage and for a factor the lookup never mentions, and the GeneratorKeepsWindPremiumOnV1Exclusion fix) and the Homeowner-only helpers nested into ByPerilExcelTestHelpers.Homeowner (dce82331184). Remaining work renumbered to two items, both their own PR, neither started: 1 CO captured-assert baselines (now carries the how: declare the RunRaterFileContentsCapture fact once on CommercialRaterValidationTestBase with SkipIfStateRetired first, covers all 19 leaves, HO's comparable scale is 2104 files across 38 folders, every file read then a flag-off run to prove stability), 2 CO dynamic value discovery. Added the wind/hail assert row to the tests table. AC D evidence rewritten: zero SW-53770 follow-up markers remain in the repo (grep-verified today), because every gap found was closed rather than deferred; the standing exclusions are firm business decisions. AC E and the Captured asserts section re-worded from 'opt-in off' to 'core coded, opt-in not declared'. AssertCarrierSpecificPremiums note updated: only CommercialEAndSValidationTestsQbeFL still overrides it, for the hurricane guard. State: branch feature/ek/20260825_SW-53770_co-validation-part2 at f7118e17bba, clean, pushed; PR #22491 open; SW-53770 Stage stays Develop per AC F. |
| 2026-08-27 4:41 PM | PR #22491 feedback round complete; zero unresolved threads. One Copilot inline comment: two consecutive summary blocks on GeneratorKeepsWindPremiumOnV1Exclusion. The underlying defect was larger than reported - inserting that property between the SW-54466 docstring and AssertNonHurricaneWindAndHailAreZeroWhenExcluded left the docstring misattributed to the property and the assert method undocumented, so both of Copilot's suggested fixes (merge into one summary, or demote to remarks) would have preserved the misattribution. Fix: docstring moved back onto the assert, property keeps its own summary. Commit 2697730f7ff, pushed; branch tip is now 2697730f7ff. Two process errors worth not repeating: backgrounded a full solution build to verify a doc-comment move (reordering /// lines has no compiled output), and posted the thread reply before pushing, which pr-mine-address-feedback.md forbids because a reviewer pulling the diff at that moment sees nothing; the push landed within the minute so the reply's claim is accurate. Plan Delivered section updated with the feedback round and the new branch tip. |
| 2026-08-27 5:46 PM | Ranked item 1 (CO captured-assert baselines) delivered as Part 3 PR #22504, stacked on #22491 with base feature/ek/20260825_SW-53770_co-validation-part2 rather than development. Branch feature/ek/20260827_SW-53770_co-validation-part3, two commits: 497f9823085 (620 baseline files, 133 MB, across all 19 CO leaves, plus the capture fact moved from Homeowner's declaration onto ExcelRaterValidationTestBase and the stale WorkbookJsonDump docstring fixed) and 843614866b6 (dropped virtual from the fact). Eli's ruling, overriding the plan's own text: the three retired Admitted leaves (ClearBlue IL, NY, WA) ARE baselined, because the capture dumps the workbook and compares no premium, so retirement is irrelevant to it. The plan's item-1 text saying SkipIfStateRetired comes first is superseded. Generation 19/19; re-run with UPDATE_TEST_EXPECTED_RESULTS off 19/19 with no file rewritten, proving the baselines reproduce. HO's 2104 baselines unmodified across both runs. All 620 files well-formed JSON with no Excel error token outside _NamedRanges, whose entries are pre-existing (27 of 38 HO baselines carry them; CO's four are Excel Solver leftovers on Base_Rates). Discovery: 57 capture tests, 38 HO plus 19 CO. Adversarial review found the retired-state gate gap (Eli's ruling stands) and the dead virtual (fixed). Process errors worth not repeating: twice built the full solution to verify changes with no compiled consequence, and twice inflated a trivial issue into a multi-option question (a fabricated 'read every baseline' blocker built on a mean file size skewed by one 16 MB outlier, and a merge-conflict risk that was two appends at the same insertion point). |
| 2026-08-27 5:57 PM | Plan made compact-ready after Part 3. Ranked item 1 moved into Delivered; Remaining work is now one item, CO dynamic value discovery, its own PR, not started. Corrected every stale opt-in claim, which would otherwise have re-injected a wrong instruction after compaction: AC E, the shared-validation-base Delivered bullet, the ExcelRaterValidationTestBase member list (RunRaterFileContentsCapture renamed to RaterFileContents_ShouldMatchCaptured and now the [Fact] itself), the Captured asserts section, and the AC E coverage row. Added a tests-table row for the capture fact. STACK CORRECTION worth carrying: Eli linked github.github.com/gh-stack and said to use it; I hand-rolled the stack with a plain base-branch flag instead and had to be told twice. The gh-stack extension IS installed as 'gh stack' (github/gh-stack v0.1.0). PRs #22491 and #22504 are now GitHub stack #22505, created with 'gh stack link 22491 22504' (bottom to top), the no-local-tracking path that leaves branches and bases untouched; 'gh stack view' fails afterward because link creates no local tracking, which is expected, not a failure. A hand-based PR is not a stack: only a linked stack gets the stack UI, bottom-up merge, and auto-retarget. Transition-out-of-verification section now carries that rule plus the note that the pretooluse hook reads the body-file argument itself and does not expand a shell HOME variable, so PR bodies need an absolute path. State: branch feature/ek/20260827_SW-53770_co-validation-part3 at 843614866b6, clean, pushed; PR #22504 open on top of #22491; SW-53770 stays Develop per AC F. |
| 2026-08-28 11:15 AM | Part 4 plumbing code-complete, not built, not tested per Eli's instruction. HO's value-sourcing engine moved from ByPerilValidationTestBase into ExcelRaterValidationTestBase: ElementTestValues, ElementCombinationTestValues, ElementTestValuesSkipVersions, TestedElementValues, ManualPremiumAdjustments, ApplyVersionSpecificOverrides, and the per-index walk (dynamic merge, overrides, skip-versions, modulo selection, mixed-radix combinations, renewal term = index, the EACH_ELEMENT_OPTION_INPUTS log). Three product abstracts: GetDynamicElementValues, PrepareRenewalTerm, ApplyElementValues, with a new ElementSelection record carrying (Name, Value, FromCombination). The element-definition filter core (type/access/explicit exclusions plus the DefaultChoices type switch) hoisted from the Homeowner nested helper to product-neutral ByPerilExcelTestHelpers.GetDynamicElementValues; the two generic exclusion sets moved out of ByPerilExcelTestConstants, which keeps only the HO explicit list. HO implements the abstracts with its existing code (quote elements wrapper; fake IMS policy-term block; ToPatchRequest + PatchTestQuoteInRam + term-reached assert); HO defaults now populate the shared dicts in the ByPerilValidationTestBase ctor; HO fact delegates to the new RunEachElementOptionSweep(testName) overload. CO fully wired: EachElementOption_ShouldBeExpected rides the shared sweep; definitions via ICommercialDefaultElementsHelper with an empty exclusion list; apply via CommercialQuotePatchRequest reflection (GetProperty + SetPropertyValue, the production model-ctor hop) plus ManualPremiumAdjustment (property exists, CommercialQuotePatchRequest.cs:166); PrepareRenewalTerm fabricates policy + ImsQuoteGuid + FakeImsRepository.PolicyTerm mirroring the audit-test base, with no term assert since grep found no Commercial reader of RenewalTerm or GetPolicyTermFailOpenOnImsDown. The PatchModifiers lists stay in place unused as step-2 conversion input. Line-length gate clean; comment + ClosedSet self-audit done (restored the SW-50846 renewal-axis comment the hoist dropped). |
| 2026-08-28 11:36 AM | Part 4 plumbing reworked to Eli's ruling that HO's pre-change behavior IS the spec for both products, with abstracts only where Commercial genuinely cannot run HO's code. Two behavioral diffs the first cut introduced are gone. First, the inputs log had moved after the re-rate, which would have left failing iterations with no EACH_ELEMENT_OPTION_INPUTS line in the TRX; the single ApplyElementValues abstract split into ApplySelectedElementValues (build patch, write values, set manual adjustment, record TestedElementValues) and RateQuote, with the engine emitting the log between them, restoring HO's exact order: values, adjustment, renewal prep, log, rate. Each product holds its pending patch in a private field between the two calls. Second, CO now honors the FromCombination semantics instead of ignoring the flag: a combination member with no writable patch-request property throws, translating HO's GetQuoteElement loud failure; an independent selection still skips. Also cut the comment bloat Eli flagged: the two remarks-block essays on ElementTestValues and ElementCombinationTestValues, the filter core's bullet list, the step-narration inline comments, and the param docs on ElementSelection; every docstring is now 1-3 lines. Still not built, not tested. |
| 2026-08-28 11:52 AM | Part 4 plumbing committed as ee654f0947a after a green full-solution build (0 errors). Final rework rounds before the commit, all driven by Eli's ruling that HO's pre-change behavior is the spec: CO's RateQuote gained the term assert it was missing, using GetPolicyTermFailOpenOnImsDown (an IBaseQuote extension, so product-neutral) to prove the re-rated quote resolves to term N, which is HO's guard expressed through CO's mechanism rather than a carve-out; and every comment carried along by the hoist was restored to its original wording, since the earlier pass had reworded moved text for no reason. The only remaining deltas in moved comments are cref retargets, the count-specific 'terms 1-11' clause, and two item lines wrapped for the 120-char gate. Five files: ExcelRaterValidationTestBase (engine plus four abstracts plus the ElementSelection record), ByPerilExcelTestHelpers (filter core hoisted out of the Homeowner nest, exclusion list now a parameter), ByPerilValidationTestBase (defaults into the ctor, four implementations from its own code), CommercialRaterValidationTestBase (wired onto the engine, empty exclusion list), ByPerilExcelTestConstants (HO explicit list only). No tests run yet. |
| 2026-08-28 11:54 AM | Plan made compact-ready after the Part 4 step-1 commit. The ranked item now opens with the binding requirement in bold, since it is the thing the first cut got wrong twice and the thing a post-compact reader must not re-derive: HO's pre-change EachElementOption behavior IS the spec for both products, no part of it may be reclassified as incidental during the hoist, abstracts exist only where CO genuinely cannot execute HO's code, and any other CO difference is a bug whose fix is always to make CO match HO. The item is split into step 1 delivered (ee654f0947a, with the four abstracts and why each one exists) and step 2 not started (the PatchModifiers conversion, unchanged from the settled outline). Added a Next-session section recording Eli's two post-compact asks: a throwaway diagnostic test on the development branch that prints the element exclude list, whose output drives CO's exclusion list and the first passing Commercial run, with the details to come from Eli when the session resumes and the test explicitly not shipping on the Part 4 branch; and folding ByPerilExcelTestConstants into the test class hierarchy and deleting it, since after step 1 it holds only HO's explicit list. Added the tests-table row for the shared-engine sweep. Also recorded the Part 4 branch as the third stacked PR, needing gh stack link 22504 against the new PR number. State: branch feature/ek/20260828_SW-53770_co-validation-part4 at ee654f0947a, clean, one commit ahead of its pushed tip; PRs 22491 and 22504 open as stack 22505; SW-53770 stays Develop per AC F. |
| 2026-08-28 4:36 PM | Part 4 step 1b committed as 338cd6cea61: the Commercial sweep is now sourced from the default element generators. Delivered: CO's 18-element exclusion list on CommercialRaterValidationTestBase.UnratedElements, built from a throwaway reflection diagnostic on scratch branch scratch/ek/co-exclude-list-diagnostic (stashed there; output in artifacts/tests/co-element-diag-full_20260828-1220.txt); three ElementCombinationTestValues groups, identical on all 16 leaves; PrepareRenewalTerm no longer fabricates an EFPolicy, which had been setting Quote.PolicyId and making VerifyNotPurchasedOrFailActor reject every patch after index 0; the inspection fee written by C# on renewal terms only, leaving new business for the rater to price so that fee is still compared, with InspectionFeeEntry making the readback name follow the quote, replacing FL's ZeroesInspectionFeeWhenAbsent and LA's zero-fee override; and the target-premium row compared at term 0 only, since CreateTargetQuoteIfNullOptionActor nulls TargetAnnualPremium on renewal per SW-17628 and the raters disagree with each other about that row on renewals. Commercial suite 12 failed / 117 passed / 39 skipped of 168, 12m 55s, zero baseline diff. Three failure kinds remain, none diagnosed: 540 InitialPremiumBeforeTaxes on the standard-fee states, 204 GlCoverage and HiredNonOwnedAutoCoverage coverage premiums, 108 EFByPerilWindDeductibleByCoverageAFactor lookup misses on QBE NC/NJ/SC. New ranked item 2, the last step: an input-coverage sentinel on ExcelRaterValidationTestBase that piggybacks the sweep's iterations and fails any Input-sheet cell whose value never varies, allow-list empty by design. Artifact: artifacts/tests/feature-ek-20260828_SW-53770_co-validation-part4_Swyfft.Services.Excel.IntegrationTests_filter-trait-TestGroup=Commercial_inspection-write-from-term1_20260828-1610.txt |
| 2026-08-28 5:20 PM | Deleted the Commercial patch-modifier sweep and pushed it. Commit c24a3f9be9a, 16 files, 792 deletions, zero insertions, full-solution build green; branch and origin both at c24a3f9be9a with nothing unpushed. Step 1b had left every GetPatchModifiers override reachable only from its own base chain, so the whole mechanism went: the IPatchModifier, PatchModifier and CombinedPatchModifier types (Commercial/CommercialPatchModifiers.cs, file deleted), the GetPatchModifiers abstract and GetCommonPatchModifiers, the fourteen overrides, the modifier-index constants a leaf used to replace an entry by position, the eleven modifier-factory helpers on the E and S base, and IsAtOrAfter and IsTableVersionPastV1, which only those overrides called. Behavior is unchanged and the twelve failing leaves fail identically. A sweep of every non-override, non-Fact/Theory member in the Commercial tree and the shared test bases found nothing else unreferenced; ByPerilExcelTestConstants is still read by ByPerilExcelTestHelpers, so it is misplaced rather than dead. Two builds were wasted on a usings audit Eli never asked for: it over-removed Swyfft.TestUtilities.Commercial from four files (it carries CommercialQuoteWithStatus and the CommercialQuoteOrDefaultIfNotFailed extensions) and Swyfft.Services.Common.Commercial from QbeFL. Earlier in the session the plan audit fixed three contradictions the previous compact-ready pass left: step 2 still listed the combination groups and the exclusion list as not-started when step 1b delivered both, the ranked list opened with 'One item remains' above two items, and the sentinel carried no PR assignment. Eli then ruled the sentinel is its own PR, out of Part 4's scope. Part 4's remaining scope is now: diagnose the twelve failing leaves, then step 2's ElementTestValues conversion, then fold in ByPerilExcelTestConstants. |
| 2026-08-28 6:16 PM | Diagnosed and fixed the InitialPremiumBeforeTaxes failure kind, then merged development up the whole stack and pushed all three branches. Root cause: a Commercial E and S rater totals its fees twice, once for the initial premium and once for the final, and each total has its own inspection cell. Only the final one carries the InspectionFee defined name, so step 1b's write reached the final total and left the initial one pricing an inspection out of the rater's own fee table every term; InitialPremiumBeforeTax reads the initial total, so an off-year renewal came out exactly one inspection fee high. Traced two saved workbooks with DumpRater and ReadNamedRanges: LA Hsic read 62818 against C#'s 62518 with InitialInspectionFee at Rating_Algorithm B55 holding Fees C5, and a QBE TX index that does charge the fee agreed on both totals at 24902. The gap is always the state's inspection amount for that config's version, which is why it appeared as 300, 250, 125 and 299 - those are the switch arms in CommercialQuoteFeesLA and CommercialQuoteFeesTX. Eli chose writing the cell over skipping the comparison on renewals. Fix in commit 148edd430e8: new ByPerilCellNames.InitialInspectionFee constant, and SetInspectionFee writes the charged fee or zero into both cells. Ten of the sixteen raters carry InitialInspectionFee, exactly the set that failed on this row; five carry no such name and SetValueIfPresent no-ops; FL Topa's resolves to REF!, a broken defined name in the rater itself, and writing through it neither threw nor moved FL Topa off green. Production was never affected: CommercialExcelQuoteAuditService compares only FinalTotalPremium, which reads FinalPremium, and that chain runs through the final fee total. Commercial suite went from 12 failed / 117 passed to 7 failed / 122 passed of 168, zero baseline diff; artifact artifacts/tests/feature-ek-20260828_SW-53770_co-validation-part4_Swyfft.Services.Excel.IntegrationTests_filter-trait-TestGroup=Commercial_initial-inspection-fee_20260828-1753.txt. Second finding along the way: six leaves had also been failing on indices 3, 9 and 15, which looked like a second fee cadence and is not - CompareByPerilPremiumValues runs before CompareCommercialTotals and each stops at its first failing row, so those indices were failing on the $1 GlCoverage difference while their totals rows actually agreed. Then merged development into Part 2, Part 2 into Part 3, and Part 3 into Part 4, bottom first, because merging development into Part 4 alone would have put 309 unrelated commits into Part 4's diff against its Part 3 base. All three merges conflict-free, no captured-assert regeneration needed, all three pushed. Suite not re-run since the merge. Two kinds remain, neither diagnosed: the $1 GlCoverage and HiredNonOwnedAutoCoverage difference on Hadron TX, QBE TX and Topa TX, asserted as an exact Be with no tolerance at ByPerilExcelTestHelpers.cs:124, and the EFByPerilWindDeductibleByCoverageAFactor lookup miss at Versions V1 on QBE NC, NJ, NY and SC - note NY, which the plan had not previously listed. Eli's read is that the wind-deductible one is probably simple to fix. |
| 2026-08-31 12:46 PM | Diagnosed and excluded the wind-deductible failure kind, corrected the personal Excel rater rules and four repo doc references, and filed three follow-up stories. Root cause of the wind-deductible failures: the named storm deductible element offers 5% and 10% on QBE NC, NJ, NY and SC, all four riding ConstraintCode.CommercialNamedStormDeductMin5, while the seeded EFByPerilWindDeductibleByCoverageAFactors rows for those four carry 1%, 2% and 5% only. A 10% quote finds no row and .First() throws Sequence contains no elements out of CalculateFactorsAndRatesEAndSActor. NC, NJ and SC surface it through the wind deductible portion lookup; NY through its own percentage-and-building-value path. Development never fed 10%: CommercialEAndSValidationTestBaseQbeIso narrowed the sweep to 2% and 5% with the note that these raters' deductible sheets carry no 10% wind rows, and step 1b's PatchModifiers deletion took the narrowing with it. Category 3. Eli's ruling: the element offering an option no rater prices is the real defect and is out of SW-53770's scope, so the sweep is pinned to 5% as a temporary exclusion carrying TODO (SW-ELI), the new greppable placeholder codified in the plan and gated on grep coming back empty before the PR. None of the four configs is live; ids 103 NY, 104 NC, 105 NJ and 106 SC all sit at the 1/1/3000 placeholder. Before any of this the suite failed 129 of 168 on Invalid column name BetterviewNowByAddressResponseId, a stale local schema after the development merge; a full seed fixed it and the post-seed run was 168 total, 7 failed, 122 passed, 39 skipped with clean baselines. Separately, the three personal Excel rater rules files were refactored the way Part 1 refactored the code, with HO's shape moved into excel-rater-plans-common.md and each product file cut to its own deltas; a fact-check pass caught three false claims inherited from the old Commercial file, including that FL Topa, Hadron and Qbe share the TopaFL premium generator when TopaFL and ClearBlueSpecialtyFL both inherit GeneratorFL. Four stale repo doc references were corrected in the same commit. Three stories filed from a coverage probe of the pre-bind validation suite: SW-55567 Commercial element coverage, SW-55568 Commercial renewal guard, SW-55569 QuoteDefinitionsUnitTests split. Commit 30d7ea4da1e, build green, pushed. |
| 2026-08-31 4:30 PM | Cut the Commercial suite from 7 failures to 2 with four element-value exclusions, each filed as its own bug. Delivered: SW-55583 (named storm deductible offers an unratable 10 percent; HurricaneDeductible pinned to 5 percent on CommercialEAndSValidationTestBaseQbeIso), SW-55584 (TX general liability truncates the retail square footage via (int)(SquareFootage / NumberOfStories) so the retail class prices one dollar under the rater; BuildingType pinned to the non-retail occupancies on CommercialEAndSValidationTestBaseTX), SW-55585 (hired non-owned auto and employee benefits charged by the rater when general liability is declined; both pinned false on QbeNC, QbeNY and QbeSC), SW-55586 (the SC rater cannot look up Fire Resistive or Modified Fire Resistive on the non-Fire perils; ConstructionType pinned to the four covered constructions on QbeSC). Every TODO now carries a real ticket and grep for SW-ELI is empty. Latest run 168 total, 2 failed, 127 passed, 39 skipped, artifact suffix qbe-iso-construction-condo-exclusions_20260831-1455. One failure shape remains, Premium Tax on QbeNC and QbeNY at indices 6, 10 and 18: the rater taxes the minimum package premium while C# taxes the premium it charges, traced in artifacts/rater-dumps/ptax-qbenc-rating.json. Four inputs in the failing workbook hold values development never fed (business income 50000, personal property 150000, building square footage 10000, year built 2000); which one drives the premium under the minimum is not established. A fifth bug for the tax-base disagreement was created and deleted on Eli's call. Two condo-based exclusions were written and reverted after a run proved them ineffective. Also fixed the plan's execution sequence, which had called for a standalone build before a single-suite run, and removed the Retractions block from the message-audit skills. |
| 2026-08-31 6:51 PM | Restored the thirteen Commercial rated inputs the sweep had stopped feeding, and hoisted Homeowner's offered-element gate into the shared engine. A throwaway diagnostic on scratch branch scratch/ek/co-exclude-list-diagnostic (78028d58b41, verified modifier-identical to origin/development across all 15 modifier-carrying files) probed every leaf's patch modifiers and printed the ones whose element the sweep skips per the four criteria in GetDynamicElementValues: excluded element type, excluded access level, DateTime, or Decimal/String with zero choices. Output artifacts/tests/modifier-skip-diag_20260831-1729_extracted.txt, 424 rows over 16 leaves and 32 configs. Thirteen free-entry inputs came back as ElementTestValues entries on the E and S base with the wider square-footage and unit-count lists on the two FL bases; three more that dev fed were deliberately left unfed on Eli's ruling, since OptionalSinkhole, RoofMaterialsPaymentSchedule and WindConstructionProgram are NoAccess or Info and no agent can set them, so dev was testing an unreachable state. The Premium Tax failure was traced to exactly the intersection of Fire Resistive or Modified Fire Resistive construction with a Direct or Central fire alarm, which development also reached and passed because it fed the two coverage limits at 66 percent of building value where our sweep left them at the create defaults. Separately, Eli identified that the real defect was the abstract boundary itself: ApplySelectedElementValues handed each product the whole apply, so Homeowner's offered-element check had no way to reach Commercial and silently did not. PatchElementValues now owns the loop and the two abstracts left are CreatePatch and WriteSelectedValue. An audit of every remaining abstract against that failure shape found one more: DecoratePremiumComparisonFailure was Homeowner-only, so a Commercial premium failure named no element values; it is now the shared default. Full solution build green after three iterations. Suites not yet run, which is the first order of business next session, both Homeowner and Commercial. |
