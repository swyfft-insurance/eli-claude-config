# Test Execution

## Test Scope
- Match test scope to change scope. Changed one test file? Run that test. Changed production code? Run the tests that cover it. Don't default to running the full suite.
- The user will run CI themselves if needed.

## xUnit v3 MTP
- Trait filter (when RUNNING via `dotnet test` / `Run-DotnetTest.ps1`): `-- --filter-trait "TestGroup=GroupName"` (NOT `--filter-class`)
- ByPeril Excel tests: ALWAYS use `-- --filter-trait "TestGroup=ByPerilTests"`. Unfiltered = 900+ tests (45 min).

### ByPeril Excel validation tests run in parallel — no COM, no contention
The ByPeril Excel validation tests (`ByPerilEAndSValidationTests*` in
`Swyfft.Services.Excel.IntegrationTests`) do NOT use Excel COM interop, and each leaf exercises a
different rater `.xlsm`, so there is no shared-file or COM contention. Run the per-state suites
concurrently — separate `Run-DotnetTest.ps1` calls in one message, one per state. The "Acceptance
Tests: Serial Execution Required" rule in the project's `.claude/rules/dotnet-testing.md` applies
ONLY to document-validation and IMS *acceptance* tests — never generalize it to these integration
tests. Don't invent an execution constraint from a generic "Excel COM isn't thread-safe" prior;
verify against the docs/code first.

### Listing tests — read-only discovery (`-ListTests`)

**What it does:** enumerates the tests in a project — by class, method, trait, or full display
name — **without executing any of them.** No DB, no seeding, no side effects, no captured results.
It's how you see what a suite or skill actually covers before you run it or rely on it.

**When to use it:**
- Discover what a validation skill or trait actually covers (is my change's test in this set?).
- Verify a `-FilterTrait`/`-FilterClass` matches what you expect before a real run.
- Avoid listing in a plan a test a skill already runs (see plan-mode § "Never list a test a
  verification skill already runs").

**How to run it:**
- Any project/trait: `Run-DotnetTest.ps1 -TicketFolder <SW-XXXXX-title> -Project <P> -ListTests [-ListLevel full|classes|methods|tests|traits] [-FilterTrait "TestGroup=X"] [-NoBuild]`
- The PreBind (residential) set across its three projects, grouped by project:
  `Run-PreBindValidation.ps1 -TicketFolder <SW-XXXXX-title> -ListTests`
- `-ListLevel`: `full` = complete discovery data; `tests` = display names; `methods` = class+method
  (default); also `classes`, `traits`.
- `-NoBuild`: use it when the project is already built and unchanged since — the list is then
  instant and read-only, no need to background. If the project isn't built or its sources changed,
  omit `-NoBuild` so it builds first, and background it (that build contends with anything else in
  flight).

**Why the wrapper, not `dotnet test`:** listing is an xUnit v3 **native-CLI** feature reached via
`dotnet run --project <P> -- -list <level>`; `dotnet test` has no list capability (`--list-tests`
there silently lists nothing). Native-CLI filters are single-dash (`-trait`, `-class`, `-method`,
`-namespace`) — the wrapper translates `-FilterTrait`/`-FilterClass`/etc. for you and locates the
built assembly itself.

## PreBind Validation Tests
See `~/.claude/rules/captured-asserts.md` for commands and regeneration guidance.

## Validation surface is per product line — don't default to the HO suite

`/eli--prebind-validation` runs `TestGroup=PreBindResidentialValidationTests`, a curated list of
tests to run for most non-Commercial changes, especially Homeowner. Match the surface to the
product line before validating a change:

| Product line | Validation surface |
|---|---|
| Homeowner / residential | `/eli--prebind-validation` — captured asserts, config-ordering, quote-def index guards |
| Commercial | premium-parity tests `CommercialEAndSValidationTests{Carrier}{State}` and `CommercialAdmittedValidationTests{Carrier}{State}` in `Swyfft.Services.Excel.IntegrationTests` (`TestGroup=Commercial`); commercial captured asserts via `SeedingCoreBruteForceTest`'s `EFCommercialQuoteDefinition` case (`Swyfft.Seeding.IntegrationTests`, `CapturedAssertTests`) and every `Export…_ShouldBeConsistent` test on `CommercialAllRisksTests` (`Swyfft.Console.IntegrationTests`, `CapturedAssertTests`) |

Never assume a skill applies across product lines because it's the one you usually reach for.

### The trait says these tests are relevant for residential, not that they exclusively cover it

`PreBindResidentialValidationTests` is a curated list of tests to run for most non-Commercial
changes. Many of those tests also cover Commercial. A set being relevant for Homeowner and Flood
does not mean its surfaces exclusively cover those products, so read what a test covers before
ruling the suite out for another product line.

`DefaultElementGeneratorTests.GetDefaultElementsForState` (`Swyfft.Services.UnitTests`) is one. It
builds its config list from Flood, Homeowner, Commercial, HoDbb and CoDbb, taking the most recent
config in each product line, carrier, state and rating type group.

### Discover a suite's coverage before relying on it
Unsure what a suite covers, or which surface applies to your product line? List it first (see
§ "Listing tests — read-only discovery" above), read the result, then find the equivalent for your
line. Never assume a skill covers your work because it's the one you usually reach for.

## Test Output — Run-DotnetTest.ps1

**All test execution must go through `~/.claude/scripts/Run-DotnetTest.ps1`.** The pretooluse hook blocks raw `dotnet test` commands.

The script enforces: Tee-Object, `--output Detailed`, `--report-trx`, and deterministic filenames.

### Filename format
```
{branch}_{project}_{filters}_{timestamp}.txt
```

Example:
```
feature-ek-20260421_SW-49862_consolidate_Swyfft.Services.Excel.IntegrationTests_filter-trait-TestGroup=ByPerilTests_20260421-1430.txt
```

On development:
```
development_Swyfft.Services.UnitTests_filter-class-QuoteServiceTests_20260421-1500.txt
```

### How to call

```bash
pwsh -NoProfile -File "$HOME/.claude/scripts/Run-DotnetTest.ps1" \
  -TicketFolder "SW-XXXXX-title" \
  -Project "Swyfft.Services.Excel.IntegrationTests" \
  -FilterTrait "TestGroup=ByPerilTests"
```

Parameters: `-TicketFolder` (REQUIRED — the ticket work-folder name under `~/.claude/tickets/`; output lands in its `artifacts/tests/`), `-Project` or `-Solution` (one required), `-FilterTrait`, `-FilterClass`, `-FilterMethod`, `-FilterNamespace`, `-NoBuild`, `-Suffix`.

### Existing skills that use the script
- `/eli--prebind-validation` — calls Run-DotnetTest.ps1 for each of 3 projects concurrently
- `/eli--byperil-audit-diagnostic` — calls Run-DotnetTest.ps1 with `-FilterClass` and `-Suffix`

### `-Project` vs `-Solution`
- Use `-Project` for a `.csproj` path, `-Solution` for a `.slnx` file. They are mutually exclusive.
- Example: `Run-DotnetTest.ps1 -TicketFolder SW-XXXXX-title -Solution "SwyfftCI.slnx" -NoBuild` runs the full CI suite.

### Other rules
- Never `| tail -N` that discards error details. If tests fail, you already have the output — don't re-run.
- Single test suite: let it build. Multiple suites: build first, then `-NoBuild` in parallel.
- Never paper over test failures with ElementTestValues overrides or `SkipEachElementOptionTest = true`.

## Seeding Before Tests
See `Swyfft.Seeding/CLAUDE.md` for which seed script to run and what each does step-by-step.
