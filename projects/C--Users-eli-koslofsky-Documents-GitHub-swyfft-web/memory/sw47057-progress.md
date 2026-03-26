# SW-47057: Fix InvalidOperationException in ByPerilHomeownerExcelQuoteAuditService.GenerateAuditDoc

## Status: Implementation In Progress

## What's Done

### Step 2: DoesRateModeling() extension method — DONE
- Added to `Swyfft.Services\Helpers\HomeownerQuoteHelper.cs` (after `GetTableVersion`)
- ```csharp
  public static bool DoesRateModeling(this HomeownerStateConfig config) =>
      config.GetTableVersion(ByPerilName.RateModeling) > SwyfftVersion.V1;
  ```

### Step 2b: Updated 3 existing callers — DONE
- `Swyfft.Services\Premium\Homeowner\HomeownerPremiumService.cs:107` — `stateConfig.DoesRateModeling()`
- `Swyfft.Services\Quotes\Homeowner\HomeownerCreateQuoteService.cs:419` — `qtx.GetConfig(quote).DoesRateModeling()`
- `Swyfft.Services.Excel.IntegrationTests\Homeowner\ByPerilValidationTestBase.cs:379` — `c.DoesRateModeling()`

### Step 3: GetSarHurricanePremiumValue static method — DONE
- Added to `Swyfft.Services.Excel\Homeowner\ByPeril\Rater\ByPerilHomeownerExcelRaterServiceBase.cs`
- `internal static` method, takes `QuoteLineContainer ql` and `HomeownerStateConfig config`
- Uses a `private static MasterLogger StaticLogger` declared at top of class with other properties
- Logic: if `RawSarHurricanePremium` quote line exists → return it directly; else fall back to `PerilPremiumHurricane`, and if config `DoesRateModeling()`, reverse-compute by dividing by `HurricaneFactor`
- Has TODO comment: `EK 2026-06-01 SW-47057` for removal once fallback is no longer needed

### Step 3b: InternalsVisibleTo — DONE
- Added `[assembly: InternalsVisibleTo(Net5.SwyfftServicesUnitTestsName)]` to `Swyfft.Services.Excel\!_InternalVisibility.cs`
- Added `using Swyfft.Services.Helpers;` to the rater base file

### Step 4: Updated all 15 rater files — DONE
All replaced `ql.QuoteLines.GetRequiredValue(ByPerilName.RawSarHurricanePremium)` with `GetSarHurricanePremiumValue(ql, em.Config)`. Lambda params changed from `(wi, _, ql)` to `(wi, em, ql)` where needed.

Files updated:
- `AL\Admitted\ByPerilHomeownerAdmittedBenchmarkExcelRaterServiceAL.cs` — 2 call sites (line 24 and line 33). Line 35 `"Cap_" + ByPerilName.RawSarHurricanePremium` left as-is (cap variant).
- `AL\EAndS\ByPerilHomeownerEAndSExcelRaterServiceAL.cs`
- `CA\EAndS\ByPerilHomeownerEAndSTopaExcelRaterServiceCA.cs`
- `FL\Adequacy\ByPerilHomeownerAdequacyClearBlueExcelRaterServiceFL.cs`
- `FL\EAndS\ByPerilHomeownerEAndSExcelRaterServiceFL.cs`
- `LA\EAndS\ByPerilHomeownerEAndSExcelRaterServiceLA.cs`
- `MA\Admitted\ByPerilHomeownerAdmittedBenchmarkExcelRaterServiceMA.cs`
- `MA\EAndS\ByPerilHomeownerEAndSExcelRaterServiceMA.cs`
- `MS\EAndS\ByPerilHomeownerEAndSDorchesterExcelRaterServiceMS.cs`
- `NC\EAndS\ByPerilHomeownerEAndSExcelRaterServiceNC.cs`
- `NJ\EAndS\ByPerilHomeownerEAndSExcelRaterServiceNJ.cs`
- `NY\EAndS\ByPerilHomeownerEAndSExcelRaterServiceNY.cs`
- `SC\Admitted\ByPerilHomeownerAdmittedExcelRaterServiceSC.cs`
- `SC\EAndS\ByPerilHomeownerEAndSExcelRaterServiceSC.cs`
- `TX\ByPerilHomeownerExcelRaterServiceTX.cs`

Total: 15 files (NOT 16 as the plan said). Verified with grep — zero remaining `GetRequiredValue(ByPerilName.RawSarHurricanePremium)` calls except in the TODO comment.

## What's Remaining

### Step 5: Unit tests — BLOCKED on real prod data

- Test file exists at `Swyfft.Services.UnitTests\Excel\GetSarHurricanePremiumValueTests.cs` but has **WRONG placeholder data**
- **DO NOT GUESS string values.** Query real prod data to get actual QuoteLineDto/ByPerilQuoteLineDto values.
- Tests should use `[Theory]` with member data, not separate `[Fact]` methods
- User explicitly said to query real prod data for example quote lines

### NEXT STEP: Query prod for real test data

**I cannot query prod directly** (DB access restriction). Ask the user to run these queries or provide the data.

Need 2 example quotes from prod (purchased before 2026-02-28, no `RawSarHurricanePremium` in stored quote lines):

1. **Non-RateModeling quote** — get the stored `QuoteLineContainer` JSON to see:
   - What `DisplayName` string is stored for the hurricane premium quote line
   - The actual decimal value

2. **RateModeling quote** — get the stored `QuoteLineContainer` JSON to see:
   - What `DisplayName` string is stored for the hurricane premium quote line
   - What `DisplayName` string is stored for the ByPeril RateModeling line in `ByPerilQuoteLines`
   - The actual `HurricaneFactor` value stored on the `ByPerilQuoteLineDto`
   - The actual decimal values

This will tell us the exact strings to use in tests (not guesses about implicit conversions).

### Step 6: Rewrite tests with real data
- Use `[Theory]` with `[MemberData]` for the 4 test cases
- Use the exact string values from prod query results
- 4 cases: {NoRateModeling, RateModeling} × {MissingRawSar, HasRawSar}

### Step 7: Build and verify
- `dotnet build Swyfft.slnx` — check compilation across all 15 raters + tests
- Run unit tests: `dotnet test --project "Swyfft.Services.UnitTests" -- --filter-class "*GetSarHurricanePremiumValueTests"`
- Run full CI: `pwsh RunTests-AllUnit.ps1`

## Key Technical Decisions Made This Session

1. **Method is `internal static`** (not `protected` instance) — easier to test, no need for concrete subclass. All rater classes are in same assembly so `internal` works.
2. **No logger parameter** — method uses `private static MasterLogger StaticLogger` declared at class level. Callers (lambdas) don't have logger access anyway.
3. **`StaticLogger` not `SarLogger`** — "Sar" would be misleading, sounds like it's for the SAR service.
4. **StaticLogger declared at top of class** with other properties, not buried next to the method.
5. **Tests in `Swyfft.Services.UnitTests\Excel\`** — alongside existing `ExcelExtensionTests.cs`. Required `InternalsVisibleTo` for `SwyfftServicesUnitTestsName` in the Excel project.
6. **Tests should be `[Theory]` with member data**, not separate `[Fact]` methods.
7. **DO NOT guess at string values for test data.** Query real prod quote lines to get exact DisplayName strings, ByPeril DisplayName strings, and decimal values. Both `ByPerilName` and `QuoteElementName` use `CallerMemberName` for `Value` (implicit string conversion), but what's actually stored in the DB as `QuoteLineDto.DisplayName` must be verified from real data.
