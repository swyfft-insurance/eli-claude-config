# Test Execution

## Test Scope
- Match test scope to change scope. Changed one test file? Run that test. Changed production code? Run the tests that cover it. Don't default to running the full suite.
- The user will run CI themselves if needed.

## xUnit v3 MTP
- `dotnet test -- --list-tests` is BROKEN — use native runner: `"./Project/bin/Debug/net10.0/Project.exe" -list full`
- Trait filter: `-- --filter-trait "TestGroup=GroupName"` (NOT `--filter-class`)
- ByPeril Excel tests: ALWAYS use `-- --filter-trait "TestGroup=ByPerilTests"`. Unfiltered = 900+ tests (45 min).

## PreBind Captured Assert Tests
See `~/.claude/rules/captured-asserts.md` for commands and regeneration guidance.

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
  -Project "Swyfft.Services.Excel.IntegrationTests" \
  -FilterTrait "TestGroup=ByPerilTests"
```

Parameters: `-Project` (required), `-FilterTrait`, `-FilterClass`, `-FilterMethod`, `-FilterNamespace`, `-NoBuild`, `-Suffix`, `-ExtraArgs`.

### Existing skills that use the script
- `/prebind-captured-asserts` — calls Run-DotnetTest.ps1 for each of 3 projects concurrently
- `/byperil-audit-diagnostic` — calls Run-DotnetTest.ps1 with `-FilterClass` and `-Suffix`

### Other rules
- Never `| tail -N` that discards error details. If tests fail, you already have the output — don't re-run.
- Single test suite: let it build. Multiple suites: build first, then `-NoBuild` in parallel.
- Never paper over test failures with ElementTestValues overrides or `SkipEachElementOptionTest = true`.

## Seeding Before Tests
See `Swyfft.Seeding/CLAUDE.md` for which seed script to run and what each does step-by-step.
