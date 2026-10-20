# Domain Reference: Swyfft Codebase

## Swyfft/Insurance Terminology

Every term below is reserved (`comments-docs-and-external-writing.md` § "Swyfft's lexicon is reserved").

- **Quote**: pre-bind price proposal. Has a rating config (e.g., `FL.BSIC.ByPeril.EAndS.V6`).
- **Policy**: post-bind contract, the result of binding a quote (separate EF entity from `EFQuote`).
- **Bind** (verb): converting a quote into a policy (`*Service.Bind(EFQuote quote) → PolicyNumber`, e.g. `NfipService.Bind`, `Hiscox*Service.Bind`, `VaveServiceBase.Bind`).
- **Bind** (noun): the binding event. Use it time-relatively ("at bind", "pre-bind", "post-bind") or for the operation's outcome ("the bind succeeded", "C# bind threw"), never as a name for the resulting policy or quote.
- **New business**: a quote or policy written for a first term, as against a renewal.
- **Product line**: Homeowner (HO), Commercial (CO), Flood, DBB.
- **Element**: an input on a quote that the agent answers. `EFQuoteElement` on the quote, `EFDefaultElement` for the config's set, named by `QuoteElementName`.
- **Config**: an `IStateConfig` implementer (§ "What identifies a config/IStateConfig"). A bare "config" means this. Any other kind (appsettings, a build configuration) is named as such.
- **Rating type**: E&S or Admitted (`RatingType`).
- **Calculation method**: ByPeril or Iso (`CalculationMethod`), a different axis from rating type.
- **Carrier**: the insurer the risk is written with (`CarrierCode`).
- **Hard decline**, **soft decline**, **time-sensitive soft decline**, **referral**: the four decline types, collectively "declines", defined in `Swyfft.Services/RiskSelection/AGENTS.md` § "Decline Type Hierarchy".
- **ClosedSet**: a strongly-typed enum-like class under `Swyfft.Common/SetDefinitions/` (`StateCode`, `CarrierCode`, `ConstraintCode`), with usage rules in `Swyfft.Common/SetDefinitions/AGENTS.md`. Never the ordinary phrase "closed set" for an exhaustive list.
- **Release**: the Friday deploy of `beta` to production. Never the Tuesday beta merge, when `beta` is cut from `development`. The YouTrack field `Release Stage` keeps its literal name.

Eli works pre-bind (quoting). The quote owns the rating config and the policy inherits it. `Swyfft.Services.PostBind` covers post-bind automation.

## HomeownerStateConfig
Declaration order is functional: `GetAllValuesWithSortOrder()` reads it by reflection, and `EnsureConfigOrderWithDatabase` checks it against DB order by `RenewalOn`. Add a new version at the end of its State/Carrier/RatingType group.

## What identifies a config/IStateConfig
State, carrier, calculation method and version identify a config. State, carrier and version alone are exact in practice: no Commercial configs collide, and the only Homeowner collision is ClearBlue under the deprecated Iso method, whose colliding versions were never live together.

## Generator and Lookup vs Config Versions
Config, element generator and `ByPerilVersionLookup` versions are independent numbering schemes in Homeowner and Commercial. A new element generator takes the next number after the newest generator for its state, carrier and rating type (in `HomeownerDefaultElementGeneratorFactory.cs` or `UnityHelper_CommercialDefaultElements.cs`), never the version of the config it serves. The config appears only in that factory mapping. A new `ByPerilVersionLookup` carrier class starts at V1 (`Swyfft.Services/Common/CLAUDE.md`).

## Unexpected patterns
Flag an unexpected pattern (`SkipEachElementOptionTest = true`, disabled validation, skipped tests), then stop and ask.

## Carrier Name Mappings
Ark = Hadron (legacy name). The class is named `Hsic` for FL/LA E&S.

## Branch-to-Environment Mapping
`development` → dev, `beta` → beta, `master` → production. A PR reached prod when its commits arrived on `origin/master`, not when it merged to `development`. The first merge commit after `<commit>` (typically a beta→master PR) is the approximate prod deploy time. Derive it; never call it uncertain.

```
git log origin/master --format="%h %ai %s" --ancestry-path <commit>^..origin/master | head -5
```
