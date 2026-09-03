---
paths:
  - "**/Commercial/EAndS/**/*.xlsm"
  - "**/ByPerilSeederCommercialEAndS*.cs"
  - "**/CommercialEAndS*.cs"
  - "**/CommercialStateConfig.cs"
---
# Excel Rater (ByPeril) — Commercial Implementation Tickets

This is the **Commercial** playbook for the **Excel Rater (ByPeril)** plan type (defined in `plan-mode.md` § "Plan Types"). It inherits every general rule in `plan-mode.md`: the Gates, Parts A/B/C, the Seeder-Override and state-config ticket-note requirements, and the full Verification structure.

It also inherits everything in `excel-rater-plans-common.md`, which is where the bulk of the rater workflow now lives: the HARD RULE, the dump tasks, the five-step plan shape, the baseline diff, the per-sheet diff verdict, config sampling, the element sweep, the sentinel checks, versioning, seeder-first, and blast radius. Commercial and Homeowner run the same Excel test infrastructure, so a rule about that infrastructure is in the shared file, not here.

Two general refactor rules this playbook leans on hard live in `refactoring.md`: "don't cite a pattern you introduced earlier in the same branch as precedent" and "contain a shared-base change by construction."

This file holds only what is Commercial's own.

## Mandatory pre-reads — before authoring a Commercial rater plan

- **Implementation / component docs:** `Swyfft.Services/Common/CLAUDE.md` (ByPerilVersionLookup); `Swyfft.Services/Common/Commercial/CLAUDE.md` (CommercialStateConfig); `Swyfft.Services/Premium/CLAUDE.md` (ByPeril premium system **and** "Commercial: agent inputs rate via quote columns"); `Swyfft.Services/Elements/CLAUDE.md` (elements/constraint codes, and the Commercial "an element alone doesn't rate" note); `Swyfft.Seeding/ExcelLoaders/ByPeril/CLAUDE.md`; `Swyfft.Services.Excel/Commercial/CLAUDE.md`.
- **Excel test docs:** `Swyfft.Services.Excel.IntegrationTests/CLAUDE.md` and its `Commercial/CLAUDE.md` (diagnosing a failure by tracing the auto-saved failure workbook).

## The Commercial verification surface

The shared five-step plan shape is in `excel-rater-plans-common.md`. These are the suites its steps 4
and 5 run for Commercial:

- **Premium parity and baselines** — the `CommercialEAndSValidationTests{Carrier}{State}` and
  `CommercialAdmittedValidationTests{Carrier}{State}` classes in
  `Swyfft.Services.Excel.IntegrationTests`.
- **Seeded quote-def captured assert** — `SeedingCoreBruteForceTest`'s `EFCommercialQuoteDefinition`
  case in `Swyfft.Seeding.IntegrationTests`.
- **Export captured asserts** — every `Export…_ShouldBeConsistent` test on `CommercialAllRisksTests`
  in `Swyfft.Console.IntegrationTests`. Required on every Commercial rater ticket.
- **Renewal boundary test** — whenever the change touches a rated input. See the next section.
- **Element golden files** — `DefaultElementGeneratorTests.GetDefaultElementsForState`
  (`Swyfft.Services.UnitTests`), whenever the change touches an element loader. It sits in the
  `PreBindResidentialValidationTests` set and covers Commercial.

> Run the validation tests through `Run-DotnetTest.ps1` with `-FilterTrait "TestGroup=Commercial"`
> and `-IsCommercial`. Without the trait the pre-tool hook blocks the run, and without
> `-IsCommercial` the guard blocks it too.

## Renewals need a hand-written guard — Commercial has no migration system

Homeowner has an automatic safety net: `QuoteMigrations` translates element values when a quote
crosses a config boundary, and `MigrationCoverageTests` fails on a boundary it cannot migrate.
`Swyfft.Services/QuoteMigrations/` carries product directories for Flood and Homeowner only, and no
file under it mentions Commercial. Every Commercial crossing is hand-written or nothing at all.

Renewal is the path that matters, because it is the only one that moves a quote forward onto a newer
config. `TryGetQuoteDefinitionForRenewal` picks the newest quote def whose `RenewalOn` is on or before
the renewal effective date, and the same pipeline rates the quote immediately. Whatever the expiring
quote stored is what the new config rates.

So any rater change that changes what a rated input may hold, whether an option added, removed or
renamed, an input rated for the first time, or a default changed, needs an explicit renewal guard. An
in-force quote arrives carrying either a value the new config cannot rate (SW-53711, roof type) or a
null for a column that was never populated (SW-53916, Roof Systems Payment Schedule).

**A create-path default is never a guarantee.** `ICreateDefaultQuote` is wired only into the Create
actor collections, never into Copy, CopyTo, or InitiateRenew, and those paths shallow-copy every rated
column verbatim, nulls included. No read may assume a column is populated because a create actor
defaults it.

A Commercial plan that touches a rated input MUST state how renewals crossing onto the new config
handle the stored value, as explicit code scoped to the new configs by name. SW-53711's shape:
`UpdateTargetQuoteActor` resets the value to the create default for the configs listed in
`QuoteFactoryHelper.RenewalRoofTypeResetConfigs`. The plan MUST also include a renewal boundary test
following the `CommercialRenewalRoofTypeTests` pattern: purchase a quote on the prior config holding
the old value, initiate renewal, then assert it lands on the expected config, rates above zero, and
holds the expected value.

## Rated agent inputs ride quote columns — default them on create

A rated Commercial agent input's value rides a column on `EFCommercialQuote`, not the element model.
The full chain and checklist are in `Swyfft.Services/Premium/CLAUDE.md` § "Commercial: agent inputs
rate via quote columns". Two traps:

- **Silently-inert input.** The element to patch-request hop matches by name with no compile or
  runtime check, so an input with an `EFDefaultElement` (a visible UI dropdown) but no same-named
  patch-request property is silently dropped and never affects premium. Wire the whole chain, not
  just the element.
- **Undefaulted column throws for everyone.** If the premium generator `ThrowIfNull`s the column, as
  Roof Systems Payment Schedule does, every quote through that generator throws until the column is
  defaulted on create, renewals and non-opt-in carriers included. Scope the default by the right key.
  Commercial create-actor carrier bases are shared cross-state: `CreateDefaultEAndSQbeQuoteOptionActorBase`
  serves a per-state actor for FL, LA, NC, NJ, NY, SC and TX. Opt-in is therefore a per-**state**
  decision. Express it with a `StateCode.Switch` on the E&S create-actor base rather than a
  carrier-base override, which would leak the default to non-opt-in states.

## Quote-def activation lives in `EnvironmentFilters`, not `Seeder.cs`

A new Commercial config needs a `Data/Commercial/QuoteDefinitions.txt` row for the production
go-live date, plus a NONPROD override in `EnvironmentFilters.CommercialOverrides` so the config is
testable in local, dev and beta before that date. `Seeder.cs` overrides are Homeowner only, and its
parameter type rejects a `CommercialStateConfig` outright.

## Opt-in behavior belongs on a base only the opt-in carriers share

A state's Commercial E&S rater is shared by its carriers, and not every carrier takes a given
ticket's update. New behavior added to a base the non-opt-in carrier also inherits breaks that
carrier's quotes.

- **Put opt-in-only behavior on a base shared only by the opt-in carriers**, never on the state base
  the non-opt-in carrier also inherits. Read the chain before picking the class.
- **When a per-carrier subclass already exists, put the behavior there rather than a `CarrierCode ==`
  branch in the shared base.**

## The layers do not share one inheritance shape

Read the actual chain of the class you are editing. A change that is safe in one layer's hierarchy is
unsafe in another's, and the shapes are not parallel:

- **Premium generators** inherit from behavior-named bases rather than by state.
  `CommercialEAndSByPerilPremiumGeneratorQbeSC`, `…QbeNC` and `…QbeNJ` inherit
  `CommercialEAndSByPerilPremiumGeneratorCombinedDeductible`, as does
  `CommercialEAndSByPerilPremiumGeneratorTopaTX`. `…QbeNY` inherits
  `CommercialEAndSByPerilPremiumGeneratorSplitDeductible`. They are siblings, not a state subtree.
- **Rater services** vary. FL, LA and TX have state mid-bases (`CommercialEAndSExcelRaterServiceFL`
  and siblings), while NC, NJ, NY and SC inherit `CommercialEAndSExcelRaterService` directly.

## Don't let one state inherit another state's generator — extract a shared base

When several states rate alike, having the look-alikes inherit one state's generator couples them: the inherited-from state's rater cannot be updated without moving the others. Put the shared behavior in a state-neutral base that hardcodes no state or carrier, and keep each state's specifics in its own generator.

Extracting such a base is a **copy, not a rename**. The new file has no history on `development`, so a later `development` merge advances the original class and leaves the extracted copy behind. After any such merge, reconcile the extracted base against `development`'s version of the class it came from.

## Surfaces a Commercial rater implementation can touch (non-exhaustive)

- **Rater file(s)** — `Data/{State}/Commercial/EAndS/{Rater}.xlsm`; propagate byte-identical to each in-scope carrier file.
- **Seeder** — `ByPerilSeederCommercialEAndS{ST}.cs`.
- **State config** — a new `CommercialStateConfig` version.
- **Quote defs + activation** — `Data/Commercial/QuoteDefinitions.txt` row; NONPROD override in `EnvironmentFilters.cs` (`CommercialOverrides`).
- **Version lookups** — `ByPerilVersionLookupCommercial.cs`.
- **Premium generators** — `Swyfft.Services/Premium/Commercial/CommercialEAndSByPerilPremiumGenerator{...}.cs` + the generator factory.
- **Rated agent inputs (quote-column chain)** — `EFCommercialQuote` column (Core migration) → patch request/interface → create-actor default → `EFDefaultElement`/constraint code → generator read → rater service `SetInputs` (full checklist in `Swyfft.Services/Premium/CLAUDE.md`).
- **Elements** — `EFDefaultElement` / constraint codes / element loader (UI options + validation only).
- **Rater services** — `CommercialEAndSExcelRaterService.cs` (`SetInputs`, `SetVersions`, factor/coverage/fee name mappings) and its state and carrier subclasses, all of which the audit job and the tests reach through `CommercialExcelRaterServiceDispatcher`.
- **Fees** — `Swyfft.Services/Premium/Commercial/CommercialQuoteFees{ST}.cs`.
- **Validation tests** — `CommercialEAndSValidationTests{Carrier}{State}` and `CommercialAdmittedValidationTests{Carrier}{State}`.
- **Captured asserts** — the `RaterFileContents` baselines, `SeedingCoreBruteForceTest`'s `EFCommercialQuoteDefinition` case, and every `Export…_ShouldBeConsistent` test on `CommercialAllRisksTests`.

## Component → Excel-signal map (Commercial)

The diff signal on the left tells you which component on the right must change:

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
