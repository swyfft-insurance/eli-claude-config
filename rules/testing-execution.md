# Test Execution

## Test Scope
- Match test scope to change scope. Changed one test file? Run that test. Changed production code? Run the tests that cover it. Don't default to running the full suite.
- The user will run CI themselves if needed.

## xUnit v3 MTP
- Trait filter (when RUNNING via `dotnet test` / `Run-DotnetTest.ps1`): `-- --filter-trait "TestGroup=GroupName"` (NOT `--filter-class`)
- ByPeril Excel tests: ALWAYS use `-- --filter-trait "TestGroup=ByPerilTests"`. Unfiltered = 900+ tests (45 min).

### Listing tests (read-only, no run)
- Use the wrapper's list mode — it never executes tests:
  `pwsh ~/.claude/scripts/Run-DotnetTest.ps1 -Project <P> -ListTests [-ListLevel full|classes|methods|tests|traits] [-FilterTrait "TestGroup=X"] [-NoBuild]`
- **Why not `dotnet test`:** `dotnet test` is the MTP integration and has **no** list capability — `dotnet test -- --list-tests` silently lists nothing ("Zero tests ran"). Listing is an xUnit v3 **native-CLI** feature, reached via **`dotnet run`**. The wrapper runs `dotnet run --project <P> -- -list <level>`, which locates the built assembly itself (no exe-path / `build/` output-dir guessing).
- `-ListLevel`: `full` = complete discovery data; `tests` = display names; `methods` = class+method (default in the PreBind list); also `classes`/`traits`.
- **Native-CLI filters are single-dash** `-trait "Name=Value"` / `-class` / `-method` / `-namespace` — NOT the MTP `--filter-*` flags. The wrapper translates `-FilterTrait`/`-FilterClass`/etc. for you in list mode. (`--filter-trait` is only for `dotnet test` when *running*.)
- Requires the project built first (`pwsh ~/.claude/scripts/Build-Solution.ps1`); pass `-NoBuild` to skip the incremental build.
- PreBind suite specifically: `pwsh ~/.claude/skills/prebind-captured-asserts/Run-PreBindCapturedAsserts.ps1 -ListTests` lists all three PreBind projects' tagged tests, grouped and prefixed by project.

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

Parameters: `-Project` or `-Solution` (one required), `-FilterTrait`, `-FilterClass`, `-FilterMethod`, `-FilterNamespace`, `-NoBuild`, `-Suffix`.

### Existing skills that use the script
- `/prebind-captured-asserts` — calls Run-DotnetTest.ps1 for each of 3 projects concurrently
- `/byperil-audit-diagnostic` — calls Run-DotnetTest.ps1 with `-FilterClass` and `-Suffix`

### `-Project` vs `-Solution`
- Use `-Project` for a `.csproj` path, `-Solution` for a `.slnx` file. They are mutually exclusive.
- Example: `Run-DotnetTest.ps1 -Solution "SwyfftCI.slnx" -NoBuild` runs the full CI suite.

### Other rules
- Never `| tail -N` that discards error details. If tests fail, you already have the output — don't re-run.
- Single test suite: let it build. Multiple suites: build first, then `-NoBuild` in parallel.
- Never paper over test failures with ElementTestValues overrides or `SkipEachElementOptionTest = true`.

## Seeding Before Tests
See `Swyfft.Seeding/CLAUDE.md` for which seed script to run and what each does step-by-step.
