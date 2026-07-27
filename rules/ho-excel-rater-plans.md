# Excel Rater (ByPeril) — Homeowner Implementation Tickets

This is the **Homeowner** playbook for the **Excel Rater (ByPeril)** plan type (defined in `plan-mode.md` § "Plan Types"). It inherits every general rule in `plan-mode.md` — the Gates, Parts A/B/C, the Seeder-Override and HomeownerStateConfig feature-doc requirements, and the full Verification structure — plus the shared rater conventions in `excel-rater-plans-common.md` (the HARD RULE, the dump tasks, the provisional-scope carve-out, the `version_history` caveat, seeder-first, and blast radius). This file holds the HO-specific pieces below: pre-reads, the plan shape, and the component→Excel-signal map.

## Mandatory pre-reads — before authoring an Excel rater plan

A rater plan must not be authored — and the plan file must list as required pre-reads — without reading:

- **Implementation / component docs:** `Swyfft.Services/Common/CLAUDE.md` (ByPerilVersionLookup); `Swyfft.Services/Common/Homeowner/CLAUDE.md` (HomeownerStateConfig, QuoteDefinitions, seeder overrides, fold-vs-stack); `Swyfft.Services/Elements/CLAUDE.md` + `Elements/Homeowner/CLAUDE.md` (elements, constraint codes, generators, factory version fallback); `Swyfft.Services/Premium/CLAUDE.md` (element-model wiring); `Swyfft.Services/QuoteFees/CLAUDE.md` (fees); `Swyfft.Seeding/ExcelLoaders/ByPeril/CLAUDE.md` + its children `reading-rater-files.md`, `Homeowner/CLAUDE.md`, `Homeowner/rater-sheets-reference.md` (seeding + the sheet→component mapping); `Swyfft.Services.Excel/Homeowner/ByPeril/Rater/CLAUDE.md` + `audit-and-debugging.md` (rater-service overrides).
- **Excel test docs:** `Swyfft.Services.Excel.IntegrationTests/CLAUDE.md` + `Homeowner/CLAUDE.md` (ByPeril validation tests, debugging `#VALUE!`); `~/.claude/rules/captured-asserts.md` and the `/eli--prebind-validation` skill (the baseline regen flow).

Always read the seeding/sheet-mapping, rater-service, and validation-test docs — not just the ones the ticket seems to touch — because the step-3 diff can implicate any component.

## Plan shape (every rater ticket)

1. Branch.
2. **(You) place the rater(s).** Overwrite the canonical `Data/{State}/…/{Rater}.xlsm`. For a UnifiedRater (E&S HO ships one rater per state), propagate it byte-identical to each in-scope carrier file and hash-verify.
3. **Scoping checkpoint — HARD STOP.** Run the ByPeril Excel validation tests for the affected leaves; the `RaterFileContents` baselines auto-update locally on the run (captured-assert update behavior: see `~/.claude/rules/captured-asserts.md`). Read the `ExpectedResults/` diff and reconcile against the provisional plan: diff ⊆ provisional → proceed; diff shows more (another factor, new input, fee, layout) → surface the delta and expand the plan before any C#. **This is where provisional becomes verified.**
4. **Implement** the C# the diff dictates (map below).
5. **Verify.** Run the ByPeril Excel validation tests again (baselines auto-update on the run; review the diff) — now it also reflects the version wiring — plus `/eli--prebind-validation` and `MigrationCoverageTests` (always; see "Renewal migrations" below); confirm the final diff matches the scope with nothing unexpected, and the C# premium == Excel across all indices.

> Running the ByPeril Excel validation tests (the `ByPerilEAndSValidationTests*` classes in `Swyfft.Services.Excel.IntegrationTests`) through `Run-DotnetTest.ps1` **must** include `-FilterTrait "TestGroup=ByPerilTests"` — omit it and the run also pulls the Commercial validation tests (900+, ~45 min) and the pre-tool hook blocks it. Scope to one state by AND-ing `-FilterNamespace "*{ST}.EAndS"`.

## Renewal migrations — always run the tests; cover changed option sets

When a rater ticket changes a rated input's option set between config versions (values added, removed, or renamed), in-force quotes hold old-set values and cross onto the new config at renewal. HO's quote-migration system (`Swyfft.Services/QuoteMigrations`) translates element values across config boundaries; a plan that changes an option set MUST include the migration (or confirm an existing one covers the new boundary).

Every HO rater plan runs `MigrationCoverageTests` in verification regardless of whether the plan believes any option set changed — the tests are the check on that belief, and they must be green.

## Why the baseline diff, not `DumpRater`

`RaterFileContents_ShouldMatchCaptured` (SW-50657) writes canonical, code-controlled inputs via `SetExcelValues` before dumping, so it reflects only the rater's factors/formulas/structure — never the stray inputs someone left in the file from clicking around. A raw `DumpRater` of the on-disk file carries that drift; it's ad-hoc debugging only. The diff is the same drift-free mechanism at both step-3 scoping and step-5 verification.

## Researching rater structure — read the pre-dumped baselines

Every ByPeril HO rater's full structure is already captured on disk by
`RaterFileContents_ShouldMatchCaptured`, under
`Swyfft.Services.Excel.IntegrationTests/ExpectedResults/{TestClass}/` — `_NamedRanges.txt` (every
named cell and its target), `Fees.txt`, `Rating_Algorithm.txt`, and the per-sheet dumps. To
research a rater's current shape (does a named range exist? what's the inspection-fee cell and its
formula? which fees are wired?), **read these dumps — never open the `.xlsm`**. It's drift-free
(canonical inputs written before the dump), needs no Excel/COM, and covers every state/carrier
leaf. Use it both to scope a change and to find which raters already have or lack a given named
range (e.g. grep the `_NamedRanges.txt` files for a cell name across all leaves at once).

## Surfaces an HO rater implementation can touch (non-exhaustive)

This is thorough — a rater rarely needs a surface not on it. But it isn't a closed set: the diff is the authority, so don't rule out an off-list surface just because it's absent here. A given ticket touches only a subset. Inferred from the HO docs.

- **Rater file(s)** — `Data/{State}/Homeowner/ByPeril/.../{Rater}.xlsm`.
- **Seeder** — `ByPerilSeederHomeowner{...}.cs`.
- **State config** — a new `HomeownerStateConfig` version.
- **Quote defs + activation** — `Data/QuoteDefinitions.txt` row; seeder override in `Seeder.cs` (`CustomizeCoreLocalAndDevAndBeta`).
- **Version lookups** — `ByPerilVersionLookup/Homeowner/...`.
- **Premium generators** — `HomeownerByPerilPremiumGenerator.cs` (+ carrier subclass) + the generator factory.
- **Rated agent inputs (element model)** — element loader → constraint code → generator → `IByPerilQuoteElementModel`/`ByPerilQuoteElementModel` → `ByPerilElementService` → `ByPerilName` → rater service `WorkbookSetters`.
- **Rater services** — `ByPerilHomeowner{RT}ExcelRaterService{ST}.cs` (+ `ByPerilCellNames`, version-cell mapping, `FeeNames`, factor/coverage names).
- **Fees** — `QuoteFees/Homeowner/...` + `StateQuoteFeeFactoryHelper.cs`.
- **Validation tests + baselines** — `ByPerilEAndSValidationTests*` + the `RaterFileContents` baselines.
- **Captured asserts / config guards** — `/eli--prebind-validation` (config ordering, quote-def index guards).

## Component → Excel-signal map

The diff signal on the left tells you which component on the right must change:

| Rater signal in the diff | C# component to change | Key file(s) |
|---|---|---|
| A factor's version bumped on the `Versions` sheet | Bump that factor in the carrier `ByPerilVersionLookup` class (clone latest → `.SetVersion`) | `Swyfft.Services/Common/ByPerilVersionLookup/Homeowner/{ST}/{Calc}/…{Carrier}{ST}.cs` |
| Any new factor version now in use | New `HomeownerStateConfig` version (`sourceConfig:` + new `lookupVersions:`) + `QuoteDefinitions.txt` row + seeder override | `…/Common/Homeowner/HomeownerStateConfig/ByPeril/…`; `Data/QuoteDefinitions.txt`; `Swyfft.Seeding/Seeder.cs` |
| Factor sheet: new static rows / shifted header rows | Seeder reader params (`startRow`/`startCol`/`versionOffset`; `.SetLength(N)` if static rows now mix with formula rows) | `Swyfft.Seeding/ExcelLoaders/ByPeril/Homeowner/ByPerilSeederHomeowner…` |
| Factor sheet: a new version is **formula-only** | Replicate the formula in the premium generator, version-branched | `Swyfft.Services/Premium/Homeowner/HomeownerByPerilPremiumGenerator.cs` (+ carrier subclass) |
| `Input` sheet: new input/option | Element loader + constraint code → generator → `ByPerilQuoteElementModel`/`ByPerilElementService` → `ByPerilName`; then write it via the rater service `WorkbookSetters` | `ElementLoader_Homeowner_ByPeril.cs`, `ConstraintCode.cs`, generator + `HomeownerDefaultElementGeneratorFactory.cs`, `ByPerilQuoteElementModel.cs`, `ByPerilElementService`, `ByPerilName.cs` |
| A **newly versioned** factor appears on `Versions` | Add `(ByPerilName, cellName)` to the rater service `TableNameToExcelCellVersionName` (+ `ByPerilCellNames`) | `…/Rater/{ST}/ByPerilHomeowner{RT}ExcelRaterService{ST}.cs`, `ByPerilCellNames.cs` |
| `Rating_Algorithm`: new fee/tax row | `FeeNames` on the rater service + the QuoteFees service/values | rater service; `…/QuoteFees/Homeowner/…`, `StateQuoteFeeFactoryHelper.cs` |
| `Rating_Algorithm`: new factor / optional-coverage row | `GetFactorAndRateNames` / `CoverageNames` / `FactorsToSetNames` on the rater service | rater service |
| New config version needs different premium logic | Generator + `HomeownerByPerilPremiumGeneratorFactory` mapping (falls back to lower version if unmapped) | `…/Premium/Homeowner/HomeownerByPerilPremiumGeneratorFactory.cs` |

Which rows apply is dictated entirely by the step-3 diff — a ticket touches only a subset of these rows, often just one or two. The diff, not the ticket, tells you which.
