---
paths:
  - "**/Homeowner/ByPeril/**/*.xlsm"
  - "**/ByPerilSeederHomeowner*.cs"
  - "**/ByPerilHomeowner*ExcelRaterService*.cs"
  - "**/HomeownerStateConfig/**"
---
# Excel Rater (ByPeril) — Homeowner Implementation Tickets

This is the **Homeowner** playbook for the **Excel Rater (ByPeril)** plan type (defined in `plan-mode.md` § "Plan Types"). It inherits every general rule in `plan-mode.md`: the Gates, Parts A/B/C, the Seeder-Override and HomeownerStateConfig feature-doc requirements, and the full Verification structure.

It also inherits everything in `excel-rater-plans-common.md`, which is where the bulk of the rater workflow now lives: the HARD RULE, the dump tasks, the five-step plan shape, the baseline diff, the per-sheet diff verdict, config sampling, the element sweep, the sentinel checks, versioning, seeder-first, and blast radius. Homeowner and Commercial run the same test infrastructure, so a rule about that infrastructure is in the shared file, not here.

This file holds only what is Homeowner's own: pre-reads, the verification suites, renewal migrations, the surfaces list, and the component-to-Excel-signal map.

## Mandatory pre-reads — before authoring an Excel rater plan

A rater plan must not be authored — and the plan file must list as required pre-reads — without reading:

- **Implementation / component docs:** `Swyfft.Services/Common/CLAUDE.md` (ByPerilVersionLookup); `Swyfft.Services/Common/Homeowner/CLAUDE.md` (HomeownerStateConfig, QuoteDefinitions, seeder overrides, fold-vs-stack); `Swyfft.Services/Elements/CLAUDE.md` + `Elements/Homeowner/CLAUDE.md` (elements, constraint codes, generators, factory version fallback); `Swyfft.Services/Premium/CLAUDE.md` (element-model wiring); `Swyfft.Services/QuoteFees/CLAUDE.md` (fees); `Swyfft.Seeding/ExcelLoaders/ByPeril/CLAUDE.md` + its children `reading-rater-files.md`, `Homeowner/CLAUDE.md`, `Homeowner/rater-sheets-reference.md` (seeding + the sheet→component mapping); `Swyfft.Services.Excel/Homeowner/ByPeril/Rater/CLAUDE.md` + `audit-and-debugging.md` (rater-service overrides).
- **Excel test docs:** `Swyfft.Services.Excel.IntegrationTests/CLAUDE.md` + `Homeowner/CLAUDE.md` (ByPeril validation tests, debugging `#VALUE!`); `~/.claude/rules/captured-asserts.md` and the `/eli--prebind-validation` skill (the baseline regen flow).

Always read the seeding/sheet-mapping, rater-service, and validation-test docs — not just the ones the ticket seems to touch — because the scoping diff can implicate any component.

## The Homeowner verification surface

The shared five-step plan shape is in `excel-rater-plans-common.md`. These are the suites its steps 4
and 5 run for Homeowner:

- **Premium parity and baselines** — the `ByPerilEAndSValidationTests*` and
  `ByPerilAdmittedValidationTests*` classes in `Swyfft.Services.Excel.IntegrationTests`.
- **Config guards** — `/eli--prebind-validation`, which covers config ordering and the quote-def index
  guards.
- **Renewal migrations** — `MigrationCoverageTests`, on every rater ticket without exception. See the
  next section.

> Run the validation tests through `Run-DotnetTest.ps1` with `-FilterTrait "TestGroup=ByPerilTests"`.
> Omit the trait and the run also pulls the Commercial validation tests, which the pre-tool hook
> blocks. Scope to one state by adding `-FilterNamespace "*{ST}.EAndS"`, and remember that filter
> drops the state's Admitted leaves.

## Renewal migrations — always run the tests; cover changed option sets

When a rater ticket changes a rated input's option set between config versions, whether values are added, removed or renamed, in-force quotes hold old-set values and cross onto the new config at renewal. `Swyfft.Services/QuoteMigrations` translates element values across config boundaries. A plan that changes an option set MUST include the migration, or confirm an existing one covers the new boundary.

`MigrationCoverageTests` runs whether or not the plan believes an option set changed. The tests are the check on that belief.

## Surfaces an HO rater implementation can touch (non-exhaustive)

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

