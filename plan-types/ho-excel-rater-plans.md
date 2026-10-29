# Excel Rater (ByPeril) — Homeowner Implementation Tickets

## What this playbook covers

- **The Homeowner playbook for the Rater update and Rater bug plan types (`rater-update.md`, `rater-bug.md`).** It inherits all of `plan-mode.md` and `excel-rater-plans-common.md`, and holds only what is Homeowner's own.

## Mandatory pre-reads — before authoring an Excel rater plan

Read these before authoring, and list them as the plan's required pre-reads, whatever the ticket seems to touch:

- **Excel rater docs:** `Swyfft.Services/Premium/AGENTS.md` (the hub), `Swyfft.Seeding/ExcelLoaders/AGENTS.md` (seeding), `Swyfft.Services.Excel/AGENTS.md` (rater service, audit service), `Swyfft.Services.Excel.IntegrationTests/AGENTS.md` (validation tests, reading a crash).
- **Component docs:** `Swyfft.Services/Common/CLAUDE.md` (ByPerilVersionLookup), `Swyfft.Services/Common/Homeowner/CLAUDE.md` (HomeownerStateConfig, QuoteDefinitions, seeder overrides, fold-vs-stack), `Swyfft.Services/Elements/CLAUDE.md` and `Elements/Homeowner/CLAUDE.md` (elements, constraint codes, generators, factory version fallback), `Swyfft.Services/QuoteFees/CLAUDE.md` (fees).
- **Test regen:** `~/.claude/rules/captured-asserts.md` and the `/eli--prebind-validation` skill.

## The Homeowner verification surface

- **Premium parity and baselines:** the `ByPerilEAndSValidationTests*` and `ByPerilAdmittedValidationTests*` classes in `Swyfft.Services.Excel.IntegrationTests`.
- **Config guards:** `/eli--prebind-validation` (config ordering, quote-def index guards).
- **Renewal migrations:** `MigrationCoverageTests`, on every rater ticket that changes production code.

- **Run the validation tests through `Run-DotnetTest.ps1` with `-FilterTrait "TestGroup=ByPerilTests"`.** Without the trait the run also pulls in the Commercial validation tests, which the pre-tool hook blocks. `-FilterNamespace "*{ST}.EAndS"` scopes to one state but drops its Admitted leaves.

## Renewal migrations — always run the tests; cover changed option sets

- **A plan that changes a rated input's option set between config versions (values added, removed or renamed) includes the `Swyfft.Services/QuoteMigrations` migration, or confirms an existing one covers the new boundary.** `MigrationCoverageTests` runs on every rater ticket that changes production code, whatever the plan believes about option sets. A ticket that changes only test code and rater files skips it.

## Component → Excel-signal map

- **The diff signal on the left tells you which component on the right must change.** The map isn't exhaustive: the scoping diff decides which rows apply, and a surface missing from it isn't ruled out.

| Rater signal in the diff | C# component to change | Key file(s) |
|---|---|---|
| A factor's version bumped on the `Versions` sheet | Bump that factor in the carrier `ByPerilVersionLookup` class (clone latest → `.SetVersion`) | `Swyfft.Services/Common/ByPerilVersionLookup/Homeowner/{ST}/{Calc}/…{Carrier}{ST}.cs` |
| Any new factor version now in use | New `HomeownerStateConfig` version (`sourceConfig:` + new `lookupVersions:`) + `QuoteDefinitions.txt` row + seeder override | `…/Common/Homeowner/HomeownerStateConfig/ByPeril/…`; `Data/QuoteDefinitions.txt`; `Swyfft.Seeding/Seeder.cs` |
| Factor sheet: new static rows / shifted header rows | Seeder reader params (`startRow`/`startCol`/`versionOffset`; `.SetLength(N)` if static rows now mix with formula rows) | `Swyfft.Seeding/ExcelLoaders/ByPeril/Homeowner/ByPerilSeederHomeowner…` |
| Factor sheet: a new version is **formula-only** | Replicate the formula in the premium generator, version-branched | `Swyfft.Services/Premium/Homeowner/HomeownerByPerilPremiumGenerator.cs` (+ carrier subclass) |
| `Input` sheet: new input/option | Element loader + constraint code → generator → `IByPerilQuoteElementModel`/`ByPerilQuoteElementModel`/`ByPerilElementService` → `ByPerilName`; then write it via the rater service `WorkbookSetters` | `ElementLoader_Homeowner_ByPeril.cs`, `ConstraintCode.cs`, generator + `HomeownerDefaultElementGeneratorFactory.cs`, `ByPerilQuoteElementModel.cs`, `ByPerilElementService`, `ByPerilName.cs` |
| A **newly versioned** factor appears on `Versions` | Add `(ByPerilName, cellName)` to the rater service `TableNameToExcelCellVersionName` (+ `ByPerilCellNames`) | `…/Rater/{ST}/ByPerilHomeowner{RT}ExcelRaterService{ST}.cs`, `ByPerilCellNames.cs` |
| `Rating_Algorithm`: new fee/tax row | `FeeNames` on the rater service + the QuoteFees service/values | rater service; `…/QuoteFees/Homeowner/…`, `StateQuoteFeeFactoryHelper.cs` |
| `Rating_Algorithm`: new factor / optional-coverage row | `GetFactorAndRateNames` / `CoverageNames` / `FactorsToSetNames` on the rater service | rater service |
| New config version needs different premium logic | Generator + `HomeownerByPerilPremiumGeneratorFactory` mapping (falls back to lower version if unmapped) | `…/Premium/Homeowner/HomeownerByPerilPremiumGeneratorFactory.cs` |
