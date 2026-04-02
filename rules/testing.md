# Testing Reference

## xUnit v3 MTP
- `dotnet test -- --list-tests` is BROKEN — use native runner: `"./Project/bin/Debug/net10.0/Project.exe" -list full`
- Trait filter: `-- --filter-trait "TestGroup=GroupName"` (NOT `--filter-class`)
- ByPeril Excel tests: ALWAYS use `-- --filter-trait "TestGroup=ByPerilTests"`. Unfiltered = 900+ tests (45 min).

## PreBind Captured Assert Tests
"Run pre-bind captured assert tests" = build `Swyfft.slnx` first, then 3 projects with `--no-build` in parallel:
```
dotnet test --no-build --project "Swyfft.Services.UnitTests" -- --filter-trait "TestGroup=PreBindResidentialCapturedAssertTests"
dotnet test --no-build --project "Swyfft.Services.IntegrationTests" -- --filter-trait "TestGroup=PreBindResidentialCapturedAssertTests"
dotnet test --no-build --project "Swyfft.Seeding.IntegrationTests" -- --filter-trait "TestGroup=PreBindResidentialCapturedAssertTests"
```

## Seeding — TWO DIFFERENT SCRIPTS
- "seed elements local" → `Seed-Elements-Local.ps1` (elements only, ~45s)
- "seed database local" → `Seed-Database-Local.ps1` (full reseed, minutes)
- NOT interchangeable. Both build the solution. Seeder tracks file HASHES — clear `EFSeedingHistories` when only C# changed.
- Exit code 0 = seed completed. Trust it. Never re-run because you "didn't see all the logs."

## Test Output
- Capture with pwsh Tee-Object (NOT bash tee): `pwsh -NoProfile -Command "dotnet test ... 2>&1 | Tee-Object -FilePath 'C:\Users\eli.koslofsky\AppData\Local\Temp\swyfft-tests\{project}-{filter}.txt'"`
- Create folder first if needed. Use WINDOWS paths. Name must include project + filter.
- Never `| tail -N` that discards error details. If tests fail, you already have the output — don't re-run.
- Single test suite: normal `dotnet test` (let it build). Multiple suites: build first, then `--no-build` in parallel.
- Never paper over test failures with ElementTestValues overrides or `SkipEachElementOptionTest = true`.

## TDD Hard Stop
Bug fixes: write failing test → run → verify it FAILS → HARD STOP for approval → then fix.
Refactoring: write safety-net test → run → verify it PASSES → HARD STOP for approval → then refactor.

## Investigation & TDD
- Don't claim root cause is "confirmed" or "proven" until the TDD test reproduces it. Until then, it's a hypothesis — label it as such.
- When the bug crashes inside a real service (not at the boundary), use an integration test to reproduce — unit tests with mocked dependencies can't hit the real crash path.
- Before planning a test, research the test infrastructure: which base class, what setup patterns exist, what test data/addresses are available. Don't guess.
- Use real data from the failing environment (DB queries, logs) to set up the test scenario. Don't invent synthetic data when you have the actual values.
