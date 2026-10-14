# Test Execution

## Test Scope
Match test scope to change scope: a changed test file runs that test, and changed production code runs the tests that cover it. Never default to the full suite.

## xUnit v3 MTP
- Run by trait with `-- --filter-trait "TestGroup=GroupName"` (not `--filter-class`).
- ByPeril Excel tests always run with `-- --filter-trait "TestGroup=ByPerilTests"`. Unfiltered is 900+ tests (45 min).

### ByPeril Excel validation: never split the whole suite into per-state runs

A change touching a few states runs those states' suites concurrently, one `Run-DotnetTest.ps1` call per state. When those states make up all or nearly all of the suite (compare with `-ListTests -ListLevel classes`), run the suite once with `-FilterTrait "TestGroup=ByPerilTests"` and no namespace filter.

### Listing tests: read-only discovery (`-ListTests`)

`-ListTests` enumerates a project's tests without running any: no DB, no seeding, no captured results. Use it to see what a skill or trait covers, to check a filter before a real run, and to avoid listing in a plan a test a skill already runs (plan-mode § "Never list a test a verification skill already runs").

- Any project or trait: `Run-DotnetTest.ps1 -TicketFolder <SW-XXXXX-title> -Project <P> -ListTests [-ListLevel full|classes|methods|tests|traits] [-FilterTrait "TestGroup=X"] [-NoBuild]`
- The PreBind (residential) set, grouped by project: `Run-PreBindValidation.ps1 -TicketFolder <SW-XXXXX-title> -ListTests`
- `-ListLevel`: `full` (complete discovery data), `tests` (display names), `methods` (class and method, the default), `classes`, `traits`.
- Pass `-NoBuild` when the project is built and unchanged; the list is then instant. Otherwise omit it so the project builds first, and run it in the background.

`dotnet test` can't list (`--list-tests` silently lists nothing). Listing is xUnit's native CLI (`dotnet run --project <P> -- -list <level>`, single-dash filters), which the wrapper drives for you.

## Validation surface is per product line: don't default to the HO suite

| Product line | Validation surface |
|---|---|
| Homeowner / residential | `/eli--prebind-validation`: captured asserts, config-ordering, quote-def index guards |
| Commercial | premium-parity tests `CommercialEAndSValidationTests{Carrier}{State}` and `CommercialAdmittedValidationTests{Carrier}{State}` in `Swyfft.Services.Excel.IntegrationTests` (`TestGroup=Commercial`); commercial captured asserts via `SeedingCoreBruteForceTest`'s `EFCommercialQuoteDefinition` case (`Swyfft.Seeding.IntegrationTests`, `CapturedAssertTests`) and every `Export…_ShouldBeConsistent` test on `CommercialAllRisksTests` (`Swyfft.Console.IntegrationTests`, `CapturedAssertTests`) |

`/eli--prebind-validation` runs `TestGroup=PreBindResidentialValidationTests`, tests curated for most non-Commercial changes. Many of them also cover Commercial: `DefaultElementGeneratorTests.GetDefaultElementsForState` (`Swyfft.Services.UnitTests`) takes the newest config in every product line, carrier, state and rating type group across Flood, Homeowner, Commercial, HoDbb and CoDbb. List a suite and read what it covers before ruling it in or out for a product line.

## Test Output: Run-DotnetTest.ps1

All test runs go through `~/.claude/scripts/Run-DotnetTest.ps1`; the pretooluse hook blocks raw `dotnet test`.

```bash
pwsh -NoProfile -File "$HOME/.claude/scripts/Run-DotnetTest.ps1" \
  -TicketFolder "SW-XXXXX-title" \
  -Project "Swyfft.Services.Excel.IntegrationTests" \
  -FilterTrait "TestGroup=ByPerilTests"
```

Parameters: `-TicketFolder` (required; output lands in `~/.claude/tickets/<TicketFolder>/artifacts/tests/`), `-Project` (a `.csproj`) or `-Solution` (a `.slnx`), exactly one, `-FilterTrait`, `-FilterClass`, `-FilterMethod`, `-FilterNamespace`, `-NoBuild`, `-Suffix`. The full CI suite: `Run-DotnetTest.ps1 -TicketFolder SW-XXXXX-title -Solution "SwyfftCI.slnx" -NoBuild`.

- Never pipe test output through `| tail -N`. If tests fail, read the output you have; don't re-run.
- One suite: let it build. Several suites: build once, then run them in parallel with `-NoBuild`.
- Never paper over failures with `ElementTestValues` overrides or `SkipEachElementOptionTest = true`.
