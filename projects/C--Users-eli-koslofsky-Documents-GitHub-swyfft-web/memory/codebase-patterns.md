# Codebase-Specific Patterns

## HomeownerStateConfig Declaration Order
- Declaration order has FUNCTIONAL SIGNIFICANCE — `GetAllValuesWithSortOrder()` uses reflection
- `EnsureConfigOrderWithDatabase` test verifies declaration order matches DB order (by RenewalOn)
- DB order uses LOCAL dates (after seeder overrides), not production dates
- When adding a new version: ALWAYS add at END of State/Carrier/RatingType group
- When writing seeder overrides: new version's RenewalOn must be AFTER all previous versions
- What happened (2026-03-02): NJ BSIC V8 override had RenewalOn before V7's → 426 test failures
- See `Swyfft.Services/Common/Homeowner/CLAUDE.md`

## Comments and PR Descriptions
- Describe WHY the code exists and WHAT it does — not the debugging journey
- Good: explains domain problem, invariant, non-obvious behavior
- Bad: explains what you tried, references "the old approach", narrates debugging process

## Flag Unexpected Patterns
- When encountering `SkipEachElementOptionTest = true`, disabled validation, or skipped tests: STOP and ASK
- New ByPeril version test classes inherit from parent — check if parent has skip flags
- Known: QBE V1 classes for NC, SC, NY, NJ have `SkipEachElementOptionTest => true`
