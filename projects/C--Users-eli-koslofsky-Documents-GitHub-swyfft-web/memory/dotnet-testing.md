# .NET Testing Patterns

## ALWAYS List Tests Before Running
- `dotnet test -- --list-tests` is BROKEN with xUnit v3 MTP — always returns zero tests
- Use the native xunit runner instead:
  ```sh
  "./Project/bin/Debug/net10.0/Project.exe" -list classes
  "./Project/bin/Debug/net10.0/Project.exe" -list full
  "./Project/bin/Debug/net10.0/Project.exe" -list full -class "*ClassName*"
  ```
- ALWAYS verify filter matches tests BEFORE running `dotnet test`

## Test Group Traits
- Tests grouped with `[Trait(TestGroup, "GroupName")]` are NOT class names
- Filter: `-- --filter-trait "TestGroup=GroupName"` (NOT `--filter-class`)
- Test groups exist in BOTH unit and integration test projects — run both
- Constants in `Swyfft.Test.Base/SharedTestConstants.cs`

## ByPeril Excel Tests
- NEVER run full Excel integration test project without a filter
- ALWAYS use: `-- --filter-trait "TestGroup=ByPerilTests"`
- Unfiltered runs 900+ tests (45+ min) instead of ~186 ByPeril tests (~25 min)

## Seeding
- "seed elements local" → `pwsh ./Seed-Elements-Local.ps1` (elements only, fast ~45s)
- "seed database local" → `pwsh ./Seed-Database-Local.ps1` (full reseed, slow several minutes)
- These are TWO DIFFERENT scripts. Match the user's words to the right one. Do NOT substitute one for the other.
- **Single test suite**: Just run `dotnet test` normally — let it build. Do NOT add `--no-build`.
- **Multiple test suites in parallel**: Build first (`dotnet build Swyfft.slnx`), then run each with `--no-build` in parallel. This avoids file locking conflicts from parallel builds.
- `--no-build` is ONLY for the parallel case above. Never use it when running a single test suite.

## General Test Rules
- Prefer running builds, tests, and seeding as background tasks (`run_in_background`) so the user isn't blocked waiting.
- ALWAYS capture output using pwsh Tee-Object (NOT bash tee — it crashes on this machine):
  ```
  pwsh -NoProfile -Command "dotnet test ... 2>&1 | Tee-Object -FilePath 'C:\Users\eli.koslofsky\AppData\Local\Temp\swyfft-tests\{project}-{filter}.txt'"
  ```
  Create the folder first if needed: `pwsh -NoProfile -Command "New-Item -ItemType Directory -Force -Path 'C:\Users\eli.koslofsky\AppData\Local\Temp\swyfft-tests'"`
  Use WINDOWS paths — pwsh doesn't translate Unix paths like `/tmp/`.
  The name must include the test project and the filter so you can identify exactly what was run.
- NEVER use `| tail -N` that discards error details
- If tests fail, you ALREADY HAVE the output — do NOT re-run

## Do NOT Paper Over Test Failures
- NEVER add ElementTestValues overrides to exclude element options from Excel validation tests
- NEVER use `SkipEachElementOptionTest = true` without flagging it to the user
- If a test fails because the rater doesn't support certain options, that's a real bug
