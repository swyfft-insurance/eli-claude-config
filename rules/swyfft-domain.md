# Domain Reference: Swyfft Codebase

## HomeownerStateConfig
- Declaration order has FUNCTIONAL SIGNIFICANCE — `GetAllValuesWithSortOrder()` uses reflection.
- `EnsureConfigOrderWithDatabase` test verifies declaration order matches DB order (by RenewalOn).
- When adding a new version: ALWAYS add at END of State/Carrier/RatingType group.
- Seeder overrides: new version's RenewalOn must be AFTER all previous versions.
  - **What happened:** NJ BSIC V8 override had RenewalOn before V7's → 426 test failures.

## Seeder Overrides — Purpose

**Why they exist**: Production go-live dates in `Data/QuoteDefinitions.txt` (HO/Commercial) and `Data/Flood/QuoteDefinitions.txt` (Flood) are the dates set by the carrier or regulator — often weeks or months in the future. Without overrides, dev/beta databases would seed those exact dates, meaning agents and QA could not test the new configs until the prod date arrives. Seeder overrides shift the local DB dates earlier so configs are testable in lower environments **immediately** after the code lands.

**Default rule for every new override**: `NewQuotesOn` should be **today or earlier** so the new config is the active version for new quotes the moment the override seeds. `RenewalOn` is constrained by the ordering rule (strictly > predecessor's effective DB RenewalOn) but should also be as early as possible — set it equal to `NewQuotesOn` if the predecessor's RenewalOn is in the past, or one day after the predecessor's RenewalOn if the predecessor's is in the future.

**Two separate mechanisms** — different product lines override in different files:

| Product line | Override location | Mechanism |
|---|---|---|
| Homeowner | `Swyfft.Seeding/Seeder.cs` → `CustomizeCoreLocalAndDevAndBeta()` | Mutates `core.HomeownerQuoteDefinitions` rows during seeding |
| Flood | `Swyfft.Services/Helpers/EnvironmentFilters.cs` → `FloodOverrides` (within `#if NONPROD`) | Runtime `Updated()` extension applied during `InitializeQuoteDefinitionsFlood` |
| Commercial | `Swyfft.Services/Helpers/EnvironmentFilters.cs` → `CommercialOverrides` (within `#if NONPROD`) | Same pattern as Flood |
| DBB | `Swyfft.Services/Helpers/EnvironmentFilters.cs` → `DbbOverrides` (within `#if NONPROD`) | Same pattern as Flood |

**Don't mix them up** — Homeowner overrides live ONLY in `Seeder.cs`; Flood/Commercial/DBB overrides live ONLY in `EnvironmentFilters.cs`. Don't try to add a Flood entry to `Seeder.cs:SetQuoteDefOverrides` (the param type is `HomeownerStateConfig`).

**Default: always add an override for every new config**. If you're adding a new state config that isn't already live in prod, the dev/beta database has no way to test it without an override — even if the prod go-live is "soon", QA still needs it earlier. Skip the override only when prod go-live is in the past.

## Generator and Lookup vs Config Versions
- Generator class version numbers (e.g., `DefaultElementGeneratorByPerilEAndSBenchmarkSpecialtyV6AL`) and `ByPerilVersionLookup` carrier class version numbers (e.g., `ByPerilVersionLookup.Homeowner.FL.EAndS.Hiscox.V1`) do NOT correspond to HomeownerStateConfig version numbers (e.g., `ALByPerilEAndSBenchmarkSpecialtyV6`). They are independent numbering schemes.
- Always check the factory mapping in `HomeownerDefaultElementGeneratorFactory.cs` to find which generator serves which config version.
- See `Swyfft.Services/Common/CLAUDE.md` for the detailed rule on `ByPerilVersionLookup` (including: when CREATING a new carrier lookup class, always start at V1).

## Comments and PR Descriptions
- Describe WHY and WHAT — not the debugging journey.
- Flag unexpected patterns: `SkipEachElementOptionTest = true`, disabled validation, skipped tests → STOP and ASK.

## Carrier Name Mappings
- Ark = Hadron (legacy name). Class named `Hsic` for FL/LA E&S.

## Branch-to-Environment Mapping

`development` → dev, `beta` → beta, `master` → **production**.

To determine when a PR deployed to prod, check when its commits arrived on `origin/master` (NOT the merge date of the feature PR into `development`):

```
git log origin/master --format="%h %ai %s" --ancestry-path <commit>^..origin/master | head -5
```

The first merge commit after `<commit>` on `origin/master` (typically a beta→master PR) is the approximate prod deploy timestamp. Don't say "deploy timing uncertain" — derive it.
