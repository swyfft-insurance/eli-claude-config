# Excel Rater (ByPeril) — Commercial Implementation Tickets

This is the **Commercial** playbook for the **Excel Rater (ByPeril)** plan type (defined in `plan-mode.md` § "Plan Types"). It inherits every general rule in `plan-mode.md` — the Gates, Parts A/B/C, the Seeder-Override and state-config ticket-note requirements, and the full Verification structure — plus the shared rater conventions in `excel-rater-plans-common.md` (the HARD RULE, the dump tasks, the provisional-scope carve-out, the `version_history` caveat, seeder-first, and blast radius). Two general refactor rules it leans on hard live in `refactoring.md`: "don't cite a pattern you introduced earlier in the same branch as precedent" and "contain a shared-base change by construction."

Commercial rating is unusually hierarchy-heavy and shares one rater across carriers, so most of this file is about **not letting a change leak past the carriers/states it's meant for.**

## Commercial has no pre-dumped baselines — scope via `DumpRater`

The HO playbook scopes and verifies against the `RaterFileContents` captured baselines. **Commercial has none.** So the sanctioned way to read a Commercial rater is the `DumpRater` console task (see `excel-rater-plans-common.md` § "Running the Excel dump tasks"), and the scoping checkpoint compares a `DumpRater` dump of the old on-disk rater against a dump of the placed new rater — that diff is what hardens the provisional plan, the same role the baseline diff plays for HO.

## The scoping diff demands a verdict on EVERY sheet — none is presumed noise

When reconciling the old-vs-new rater diff (the step-4 checkpoint), enumerate every sheet the diff touches and record an explicit verdict for each — versioned-safe, inert, or break. Never let a sheet pass by omission: working from the ticket/changelog factor list and skimming the rest is how a break ships, because the parity leaves cannot catch an unversioned change the seeder mirrors into C# — the diff verdict is the only guard.

For a **seeded factor sheet** the bar is stricter: there is no innocent "layout" change to seeded data. If a seeded sheet's values differ at all, either (a) properly versioned rows were added (V1 = the prior values, new behavior on V2), or (b) the change is wrong — an unversioned value change on an existing tab is a backwards-compat break exactly like an unversioned new factor. Reference-shift noise exists only on formula sheets (`Rating_Algorithm` refs auto-shifting around inserted rows), never on data tabs.

- **What happened:** SW-52867 — the LA/TX `Ordinance_Law` values changed unversioned (1.15 on Fire+Hurricane only → 1.25/1.4/1.65 on all perils). The audit enumerated only the new factor sheets, so the change sat unflagged in the diff artifacts until TX validation failures exposed it; the in-force LA/TX books would have silently re-rated.

## Mandatory pre-reads — before authoring a Commercial rater plan

- **Implementation / component docs:** `Swyfft.Services/Common/CLAUDE.md` (ByPerilVersionLookup); `Swyfft.Services/Common/Commercial/CLAUDE.md` (CommercialStateConfig); `Swyfft.Services/Premium/CLAUDE.md` (ByPeril premium system **and** "Commercial: agent inputs rate via quote columns"); `Swyfft.Services/Elements/CLAUDE.md` (elements/constraint codes, and the Commercial "an element alone doesn't rate" note); `Swyfft.Seeding/ExcelLoaders/ByPeril/CLAUDE.md`; `Swyfft.Services.Excel/Commercial/CLAUDE.md` (rater-service subclasses are validation-test-only).
- **Excel test docs:** `Swyfft.Services.Excel.IntegrationTests/CLAUDE.md`; `~/.claude/rules/testing-execution.md` § "Validation surface is per product line" (the Commercial validation surface — do **not** default to the HO `/eli-prebind-validation` suite).

## Plan shape (every Commercial rater ticket)

1. Branch.
2. **(You) place the rater(s).** Overwrite the canonical `Data/{State}/Commercial/EAndS/{Rater}.xlsm`. For a UnifiedRater, propagate byte-identical to each in-scope carrier file and hash-verify.
3. **Implement the seeder and reseed first** (see `excel-rater-plans-common.md` § "Implement the seeder first"). The seeder is where layout and non-opt-in-carrier breakage surfaces concretely; nothing downstream runs until a full reseed is green.
4. **Scoping checkpoint — HARD STOP.** `DumpRater` the old and new raters and diff the dumps. Reconcile against the provisional plan: diff ⊆ provisional → proceed; diff shows more → surface the delta and expand the plan before any further C#. **This is where provisional becomes verified.**
5. **Implement** the C# the diff dictates (map below).
6. **Verify.** Run the Commercial validation surface — the premium-parity tests `CommercialEAndSByPerilRaterValidation*` (`TestGroup=Commercial`) in `Swyfft.Services.Excel.IntegrationTests`, and the commercial captured asserts (`SeedingCoreBruteForceTest`'s `EFCommercialQuoteDefinition` case in `Swyfft.Seeding.IntegrationTests`). Confirm C# premium == Excel across all indices for every affected leaf.

> The full Commercial validation suite is 900+ tests (~45 min) and the pre-tool hook blocks an unscoped run. Scope to the affected state/carrier leaf via `-FilterNamespace` / `-FilterClass`.

## Versioning is mandatory — even with no live policies

Commercial rater changes that move premium or fees must be gated so existing quotes and policies keep their original values — this is the constraint in `Swyfft.Services/Premium/CLAUDE.md` § "Changes must not alter what existing quotes or policies are charged", and it holds for Commercial even where a carrier has no active book, because the ABQ re-rates historical policies. If a delivered rater adds an unversioned premium-affecting factor (or puts real values on V1), that's a backwards-compat break to fix at the rater before wiring the C#.

## Know the three parallel Commercial hierarchies before touching a shared base

The three layers do not share one inheritance shape:

- **Premium generators** cross-state inherit — the `TopaTX` subtree, with `QbeNC` / `QbeNJ` / `QbeSC` extending it.
- **Seeders** are state-contained — each carrier → its own state base → the E&S base.
- **Rater services** are state-contained — each subclass → the E&S base directly (and the subclasses are validation-test-only; see `Swyfft.Services.Excel/Commercial/CLAUDE.md`).

A change safe in one layer's hierarchy is unsafe in another's. Read the actual inheritance chain of the class you're editing before editing it.

## A Commercial E&S rater is shared across carriers — never change a shared base unconditionally

A state's Commercial E&S rater is shared by several carriers, and not every carrier gets a given ticket's update (in SW-52867, FL CBS kept its old rater). New behavior added to a shared base with no opt-out broke three layers for the non-opt-in carrier: the seeder read a sheet CBS lacked and crashed; the premium base wired factors CBS inherits and threw; the version-cell writes referenced cells CBS may not have. Discipline:

- **Guard every new read/write by sheet/cell presence** (`HasNamedCell`) so non-opt-in leaves skip automatically — and guard **every** entry point in a layer, not just some (in SW-52867 `SetInputs` was guarded but `SetVersions` was not).
- **Put opt-in-only behavior on a base shared only by the opt-in carriers.** In FL, Topa/Hadron/Qbe share `CommercialEAndSByPerilPremiumGeneratorTopaFL`, while CBS is a sibling under `CommercialEAndSByPerilPremiumGeneratorFL` — so opt-in factors belong on the Topa base, not the shared FL base.
- **When a per-carrier subclass already exists, put opt-in behavior there, not a `CarrierCode ==` branch in the shared base** (the QBE minimum-premium logic belonged in `CommercialEAndSByPerilPremiumGeneratorQbeFL`).

## Rated agent inputs ride quote columns — default them on create

A rated Commercial agent input's value rides a column on `EFCommercialQuote`, not the element model (full chain and checklist in `Swyfft.Services/Premium/CLAUDE.md` § "Commercial: agent inputs rate via quote columns"). Two traps:

- **Silently-inert input.** The element → patch-request hop matches by name with no compile or runtime check, so an input with an `EFDefaultElement` (a visible UI dropdown) but no same-named patch-request property is silently dropped — it never affects premium. Wire the whole chain, not just the element.
- **Undefaulted column throws for everyone.** If the premium generator `ThrowIfNull`s the column (as RSPS does), every quote through that generator — renewals and non-opt-in carriers included — throws until the column is defaulted on create. Scope the default by the right key: Commercial create-actor carrier bases are shared cross-state (the QBE create base serves FL/NY/NC/NJ/SC), so opt-in is a per-**state** decision — express it with a `StateCode.Switch` on the E&S create-actor base, not a carrier-base override (which leaks the default to non-opt-in states).

## Don't let one state inherit another state's generator — extract a shared base

When several states rate alike, having the look-alikes inherit one state's generator couples them: you can't update the inherited-from state's own rater without moving the others. Put shared behavior in a state-neutral base (no hardcoded state or carrier) that all of them inherit, and keep each state's specifics in its own generator. Note: extracting such a base is a **copy, not a rename** — the new file has no history on `development`, so a later `development` merge advances the original class but never the extracted copy, which then silently drifts. After merging `development` into a branch that extracted a base, reconcile the extracted base against `development`'s version of the class it came from.

## Surfaces a Commercial rater implementation can touch (non-exhaustive)

This is thorough — a rater rarely needs a surface not on it. But it isn't a closed set: the diff is the authority, so don't rule out an off-list surface just because it's absent here. A given ticket touches only a subset (scope-dependent). SW-52867 touched all of these except fees.

- **Rater file(s)** — `Data/{State}/Commercial/EAndS/{Rater}.xlsm`; propagate byte-identical to each in-scope carrier file for a UnifiedRater.
- **Seeder** — `ByPerilSeederCommercialEAndS{ST}.cs`.
- **State config** — a new `CommercialStateConfig` version.
- **Quote defs + activation** — `Data/Commercial/QuoteDefinitions.txt` row; NONPROD override in `EnvironmentFilters.cs` (`CommercialOverrides`).
- **Version lookups** — `ByPerilVersionLookupCommercial.cs`.
- **Premium generators** — `Swyfft.Services/Premium/Commercial/CommercialEAndSByPerilPremiumGenerator{...}.cs` + the generator factory.
- **Rated agent inputs (quote-column chain)** — `EFCommercialQuote` column (Core migration) → patch request/interface → create-actor default → `EFDefaultElement`/constraint code → generator read → rater service `SetInputs` (full checklist in `Swyfft.Services/Premium/CLAUDE.md`).
- **Elements** — `EFDefaultElement` / constraint codes / element loader (UI options + validation only).
- **Rater services** — `CommercialEAndSExcelRaterService.cs` (`SetInputs`, `SetVersions`, factor/coverage/fee name mappings); subclasses are validation-test-only.
- **Fees** — `Swyfft.Services/Premium/Commercial/CommercialQuoteFees{ST}.cs`.
- **Validation tests** — `CommercialEAndSByPerilRaterValidation*` (`TestGroup=Commercial`).
- **Captured asserts** — `SeedingCoreBruteForceTest`'s `EFCommercialQuoteDefinition` case.

## Component → Excel-signal map (Commercial)

The diff signal on the left tells you which component on the right must change:

| Rater signal in the diff | C# component to change | Key file(s) |
|---|---|---|
| A factor's version bumped on the `Versions` sheet | Bump that factor in the carrier `ByPerilVersionLookup` node (clone latest → `.SetVersion`) | `Swyfft.Services/Common/ByPerilVersionLookup/Commercial/ByPerilVersionLookupCommercial.cs` |
| Any new factor version now in use | New `CommercialStateConfig` version (`sourceConfig:` + new lookup versions) + `Data/Commercial/QuoteDefinitions.txt` row + a NONPROD override | `Swyfft.Services/Common/Commercial/CommercialStateConfig.cs`; `Data/Commercial/QuoteDefinitions.txt`; `Swyfft.Services/Helpers/EnvironmentFilters.cs` (`CommercialOverrides`, **not** `Seeder.cs`) |
| Factor sheet: new static rows / shifted layout | Commercial seeder reader params | `Swyfft.Seeding/ExcelLoaders/ByPeril/ByPerilSeederCommercialEAndS{ST}.cs` |
| `Input` sheet: new rated input/option | The full quote-column chain — `EFCommercialQuote` column (Core migration) → patch request → create-actor default → `EFDefaultElement`/constraint → premium generator → rater service `SetInputs` | see `Swyfft.Services/Premium/CLAUDE.md` § "Checklist — adding a NEW rated Commercial agent input" |
| Factor sheet: a new version is **formula-only** | Replicate the formula in the premium generator, version-branched, on the base shared only by the opt-in carriers | `Swyfft.Services/Premium/Commercial/CommercialEAndSByPerilPremiumGenerator{...}.cs` |
| A **newly versioned** factor appears on `Versions` | Add the `(ByPerilName, cellName)` mapping + version-cell write on the rater service, `HasNamedCell`-guarded | `Swyfft.Services.Excel/Commercial/CommercialEAndSExcelRaterService.cs` |
| `Rating_Algorithm`: new fee/tax row | `FeeNames` on the rater service + the Commercial fees | rater service; `Swyfft.Services/Premium/Commercial/CommercialQuoteFees{ST}.cs` |
| New config version needs different premium logic | Generator + the Commercial premium-generator factory mapping | `Swyfft.Services/Premium/Commercial/` |

Which rows apply is dictated entirely by the step-4 dump diff — a ticket touches only a subset, often one or two. The diff, not the ticket, tells you which.
