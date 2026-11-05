---
audited-by: [code-complete]
---

# Quote-def Dates: real vs override, and what gets seeded

## Real dates and override dates

Every quote def has two independent date pairs (`NewQuotesOn`, `RenewalOn`):
- **Real / prod**: in `QuoteDefinitions.txt`. Governs prod.
- **Override**: local/dev/beta only, for testing a config before its prod go-live. Each product line keeps its overrides only in its row's file below. `Seeder.cs`'s `SetQuoteDefOverrides` takes only a `HomeownerStateConfig`.

| Product line | Override location | Mechanism |
|---|---|---|
| Homeowner | `Swyfft.Seeding/Seeder.cs` → `CustomizeCoreLocalAndDevAndBeta()` | Mutates `core.HomeownerQuoteDefinitions` rows during seeding |
| Flood | `Swyfft.Services/Helpers/EnvironmentFilters.cs` → `FloodOverrides` (within `#if NONPROD`) | Runtime `Updated()` extension applied during `InitializeQuoteDefinitionsFlood` |
| Commercial | `Swyfft.Services/Helpers/EnvironmentFilters.cs` → `CommercialOverrides` (within `#if NONPROD`) | Same pattern as Flood |
| DBB | `Swyfft.Services/Helpers/EnvironmentFilters.cs` → `DbbOverrides` (within `#if NONPROD`) | Same pattern as Flood |

- A seeded DB (local/dev/beta) gets the override when one exists, else the `QuoteDefinitions.txt` date. Prod has no overrides.
- Activating a config (swapping its parked far-future placeholder for the real date) changes only `QuoteDefinitions.txt`. The override stays and still governs the seeded date, so a config's effective date is its override.
- A test that reads the seeded DB sees the override. One that reads `QuoteDefinitions.txt` or in-memory configs sees the real date.
- Ordering tests: `Swyfft.Services/Common/Homeowner/CLAUDE.md` §§ "QuoteDefinitions.txt Ordering" and "Seeder Override RenewalOn Must Be Monotonically Increasing".

## Computing a new override's dates

Every new config whose prod go-live is in the future gets an override. Skip it only when go-live is past.
- **`NewQuotesOn`**: today or earlier, unique in the family, and after the predecessor's effective `NewQuotesOn`. Homeowner new quotes go to each carrier's config with the latest `NewQuotesOn` (`HomeownerQuoteDefinitionRepository.GetQuoteDefinitionsForQuotePurchase`), so an earlier date leaves them on the predecessor.
- **`RenewalOn`**: strictly after the predecessor's effective `RenewalOn`, unique in the family. Equal to `NewQuotesOn` when the predecessor's `RenewalOn` is past, otherwise one day after the predecessor's.
- **Predecessor**: the config declared immediately before the new one in its State/Carrier/RatingType group. Its effective `RenewalOn` is its override if it has one, else its `QuoteDefinitions.txt` date.
- `HoQuoteDefs_DeclarationOrder_ShouldMatchRenewalOnOrder` enforces the `RenewalOn` order, and `HoQuoteDefs_WithNonProdOverrides_ShouldNotViolateUniqueIndexes` enforces uniqueness. `/eli--prebind-validation` runs both; don't hand-verify those. No test checks the `NewQuotesOn` order: check it against the predecessor's effective `NewQuotesOn` when computing the dates.

An override entry's comment is `// SW-XXXXX: <title>` and nothing else.

## Finding stale overrides
An override whose config's prod `NewQuotesOn` is past is a removal candidate. Find them with `/eli--quote-def-override-audit` (HO/Flood/DBB, report-only), never by hand-comparing against `QuoteDefinitions.txt`.

Removing a stale override puts its config back on its `QuoteDefinitions.txt` dates. When the next version in its family keeps an override whose `NewQuotesOn` or `RenewalOn` isn't after those dates, that override moves too, recomputed per § "Computing a new override's dates". Never keep a stale override to protect the next version's dates.
