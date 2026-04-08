# Test Execution

## Test Scope
- Match test scope to change scope. Changed one test file? Run that test. Changed production code? Run the tests that cover it. Don't default to running the full suite.
- The user will run CI themselves if needed.

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

## Test Output
- Capture with pwsh Tee-Object (NOT bash tee): `pwsh -NoProfile -Command "dotnet test ... 2>&1 | Tee-Object -FilePath 'C:\Users\eli.koslofsky\AppData\Local\Temp\swyfft-tests\{project}-{filter}.txt'"`
- Create folder first if needed. Use WINDOWS paths. Name must include project + filter.
- Never `| tail -N` that discards error details. If tests fail, you already have the output — don't re-run.
- Single test suite: normal `dotnet test` (let it build). Multiple suites: build first, then `--no-build` in parallel.
- Never paper over test failures with ElementTestValues overrides or `SkipEachElementOptionTest = true`.
