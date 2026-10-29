# Excel Rater (ByPeril) — Commercial Implementation Tickets

## What this playbook covers

- **The Commercial playbook for the Rater update and Rater bug plan types (`rater-update.md`, `rater-bug.md`).** It inherits all of `plan-mode.md` and `excel-rater-plans-common.md`, and holds only what is Commercial's own.

## Mandatory pre-reads — before authoring a Commercial rater plan

- **Excel rater docs:** `Swyfft.Services/Premium/AGENTS.md` (the hub), `Swyfft.Seeding/ExcelLoaders/AGENTS.md` (seeding), `Swyfft.Services.Excel/AGENTS.md` (rater service, audit service), `Swyfft.Services.Excel.IntegrationTests/AGENTS.md` (validation tests, reading a crash).
- **Component docs:** `Swyfft.Services/Common/CLAUDE.md` (ByPerilVersionLookup), `Swyfft.Services/Common/Commercial/CLAUDE.md` (CommercialStateConfig), `Swyfft.Services/Elements/CLAUDE.md` (elements, constraint codes, and the Commercial "an element alone doesn't rate" note).

## The Commercial verification surface

- **Premium parity and baselines:** the `CommercialEAndSValidationTests{Carrier}{State}` and `CommercialAdmittedValidationTests{Carrier}{State}` classes in `Swyfft.Services.Excel.IntegrationTests`.
- **Seeded quote-def captured assert:** `SeedingCoreBruteForceTest`'s `EFCommercialQuoteDefinition` case in `Swyfft.Seeding.IntegrationTests`.
- **Export captured asserts:** every `Export…_ShouldBeConsistent` test on `CommercialAllRisksTests` in `Swyfft.Console.IntegrationTests`, on every Commercial rater ticket.
- **Renewal boundary test:** whenever the change touches a rated input (next section).
- **Element golden files:** `DefaultElementGeneratorTests.GetDefaultElementsForState` (`Swyfft.Services.UnitTests`, in the `PreBindResidentialValidationTests` set, covers Commercial), whenever the change touches an element loader.

- **Run the validation tests through `Run-DotnetTest.ps1` with `-FilterTrait "TestGroup=Commercial"` and `-IsCommercial`.** The pre-tool hook blocks the run without the trait, and the guard blocks it without `-IsCommercial`.

## Renewals need a hand-written guard — Commercial has no migration system

- **`Swyfft.Services/QuoteMigrations/` covers only Flood and Homeowner, so every Commercial config crossing is hand-written or nothing.** Renewal is the path that moves a quote onto a newer config: `TryGetQuoteDefinitionForRenewal` picks the newest quote def whose `RenewalOn` is on or before the renewal effective date, and the same pipeline rates the quote immediately with whatever the expiring quote stored. `ICreateDefaultQuote` runs only in the Create actor collections, never in Copy, CopyTo or InitiateRenew, which shallow-copy every rated column, nulls included. No read may assume a column is populated because a create actor defaults it.

- **A Commercial plan that changes what a rated input may hold (an option added, removed or renamed, an input rated for the first time, a default changed) states how renewals onto the new config handle the stored value.** Without that, an in-force quote arrives with a value the new config can't rate, or a null. The handling is explicit code scoped to the new configs by name. SW-53711's shape: `UpdateTargetQuoteActor` resets the value to the create default for the configs in `QuoteFactoryHelper.RenewalRoofTypeResetConfigs`. The plan also adds a renewal boundary test following `CommercialRenewalRoofTypeTests`: purchase a quote on the prior config holding the old value, initiate renewal, and assert it lands on the expected config, rates above zero, and holds the expected value.

## Rated agent inputs ride quote columns — default them on create

- **A rated Commercial agent input's value rides a column on `EFCommercialQuote`, not the element model.** The chain is in `Swyfft.Services/Premium/AGENTS.md` § "Inputs: quote to rater".

- **Wire the whole chain.** The element-to-patch-request hop matches by name with no compile or runtime check, so an `EFDefaultElement` with no same-named patch-request property is silently dropped and never affects premium.
- **Default the column on create, scoped by state.** If the premium generator `ThrowIfNull`s the column, every quote through it throws until the column is defaulted on create, renewals and non-opt-in carriers included. Create-actor carrier bases are shared across states (`CreateDefaultEAndSQbeQuoteOptionActorBase` serves FL, LA, NC, NJ, NY, SC and TX), so opt-in is per state: use a `StateCode.Switch` on the E&S create-actor base, not a carrier-base override.

## Opt-in behavior belongs on a base only the opt-in carriers share

A state's Commercial E&S rater is shared by its carriers, and not every carrier takes every update. Read the chain before picking the class:

- **Put opt-in-only behavior on a base only the opt-in carriers share,** never on the state base the non-opt-in carrier also inherits.
- **When a per-carrier subclass exists, put the behavior there** rather than a `CarrierCode ==` branch in the shared base.

## The layers do not share one inheritance shape

Read the actual chain of the class you edit. The layers aren't parallel:

- **Premium generators** inherit behavior-named bases, not states. `CommercialEAndSByPerilPremiumGeneratorQbeSC`, `CommercialEAndSByPerilPremiumGeneratorQbeNC`, `CommercialEAndSByPerilPremiumGeneratorQbeNJ` and `CommercialEAndSByPerilPremiumGeneratorTopaTX` inherit `CommercialEAndSByPerilPremiumGeneratorCombinedDeductible`. `CommercialEAndSByPerilPremiumGeneratorQbeNY` inherits `CommercialEAndSByPerilPremiumGeneratorSplitDeductible`.
- **Rater services** vary. FL, LA and TX have state mid-bases (`CommercialEAndSExcelRaterServiceFL` and siblings), while NC, NJ, NY and SC inherit `CommercialEAndSExcelRaterService` directly.

## Don't let one state inherit another state's generator — extract a shared base

- **When several states rate alike, put the shared behavior in a state-neutral base that hardcodes no state or carrier.** Never have one state inherit another's generator. Extracting the base is a copy with no history on `development`, so after any `development` merge, reconcile the extracted base against `development`'s version of the class it came from.

## Component → Excel-signal map (Commercial)

- **The diff signal on the left tells you which component on the right must change.** The map isn't exhaustive: the scoping diff decides which rows apply, and a surface missing from it isn't ruled out.

| Rater signal in the diff | C# component to change | Key file(s) |
|---|---|---|
| A factor's version bumped on the `Versions` sheet | Bump that factor in the carrier `ByPerilVersionLookup` node (clone latest → `.SetVersion`) | `Swyfft.Services/Common/ByPerilVersionLookup/Commercial/ByPerilVersionLookupCommercial.cs` |
| Any new factor version now in use | New `CommercialStateConfig` version (`sourceConfig:` + new lookup versions) + `Data/Commercial/QuoteDefinitions.txt` row + a NONPROD override | `Swyfft.Services/Common/Commercial/CommercialStateConfig.cs`; `Data/Commercial/QuoteDefinitions.txt`; `Swyfft.Services/Helpers/EnvironmentFilters.cs` (`CommercialOverrides`, **not** `Seeder.cs`) |
| Factor sheet: new static rows / shifted layout | Commercial seeder reader params | `Swyfft.Seeding/ExcelLoaders/ByPeril/ByPerilSeederCommercialEAndS{ST}.cs` |
| `Input` sheet: new rated input/option | The full quote-column chain — `EFCommercialQuote` column (Core migration) → patch request → create-actor default → `EFDefaultElement`/constraint → premium generator → rater service `SetInputs` | see `Swyfft.Services/Premium/CLAUDE.md` § "Checklist — adding a NEW rated Commercial agent input" |
| Factor sheet: a new version is **formula-only** | Replicate the formula in the premium generator, version-branched, on the base shared only by the opt-in carriers | `Swyfft.Services/Premium/Commercial/CommercialEAndSByPerilPremiumGenerator{...}.cs` |
| A **newly versioned** factor appears on `Versions` | Add the `(ByPerilName, cellName)` mapping + version-cell write on the rater service that serves that rater | `Swyfft.Services.Excel/Commercial/CommercialEAndSExcelRaterService.cs` |
| `Rating_Algorithm`: new fee/tax row | `FeeNames` on the rater service + the Commercial fees | rater service; `Swyfft.Services/Premium/Commercial/CommercialQuoteFees{ST}.cs` |
| New config version needs different premium logic | Generator + the Commercial premium-generator factory mapping | `Swyfft.Services/Premium/Commercial/` |

- **The audit job and the tests reach `CommercialEAndSExcelRaterService` and its state and carrier subclasses through `CommercialExcelRaterServiceDispatcher`.**
