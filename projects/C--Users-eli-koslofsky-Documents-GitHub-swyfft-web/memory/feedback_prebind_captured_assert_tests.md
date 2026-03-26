---
name: PreBind Residential Captured Assert Tests
description: What "run pre-bind captured assert tests" means — 3 projects, trait filter, build first
type: feedback
---

When the user says "run pre-bind captured assert tests", run tests with trait filter `TestGroup=PreBindResidentialCapturedAssertTests` across THREE projects:

1. `Swyfft.Services.UnitTests` (QuoteDefinitions, DefaultElementGenerator, QuoteFees)
2. `Swyfft.Services.IntegrationTests` (StateConfig, QuoteDefinitions, AllRisks, ElementNeedsConfirmation, MigrationCoverage, Flood/Dbb)
3. `Swyfft.Seeding.IntegrationTests` (SeedingTests)

**How to apply:** Build `Swyfft.slnx` first, then run all three with `--no-build` in parallel:
```sh
dotnet test --no-build --project "Swyfft.Services.UnitTests" -- --filter-trait "TestGroup=PreBindResidentialCapturedAssertTests"
dotnet test --no-build --project "Swyfft.Services.IntegrationTests" -- --filter-trait "TestGroup=PreBindResidentialCapturedAssertTests"
dotnet test --no-build --project "Swyfft.Seeding.IntegrationTests" -- --filter-trait "TestGroup=PreBindResidentialCapturedAssertTests"
```

These tests validate config ordering, element generators, quote definitions, quote fees, risk selection, and seeding — run them after changes to HomeownerStateConfig, ByPerilVersionLookup, element generators, or QuoteDefinitions.txt.
