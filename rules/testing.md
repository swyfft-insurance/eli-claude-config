# Test Writing

## TDD Hard Stop
Bug fixes: write failing test → run → verify it FAILS → HARD STOP for approval → then fix.
Refactoring: write safety-net test → run → verify it PASSES → HARD STOP for approval → then refactor.

## Investigation & TDD
- Don't claim root cause is "confirmed" or "proven" until the TDD test reproduces it. Until then, it's a hypothesis — label it as such.
- When the bug manifests inside a real service (not at the boundary), use an integration test to reproduce — unit tests with mocked dependencies can't hit the real code path.
- Before planning a test, research the test infrastructure: which base class, what setup patterns exist, what test data/addresses are available. Don't guess.
- Use real data from the failing environment (DB queries, logs) to set up the test scenario. Don't invent synthetic data when you have the actual values.
- Prefer `[Theory]` with `[MemberData]` over `[Fact]` when testing multiple scenarios of the same behavior.
- Use the real closed set types (e.g., `AnswerYesNo`, `LimitedWaterDamage`) as theory parameters — never hardcode string values that a closed set represents.
- Use `GetAllValues().ToTheoryData()` to generate theory data from closed sets.

## Failure Aggregation

Tests that iterate over multiple inputs (configs, indices, sheets, theory rows) must NOT stop at the first failure. Collect every failure into a list, then throw `AggregateException` at the end so a single run surfaces ALL failures.

```csharp
var failures = new List<(string Label, Exception Error)>();
foreach (var item in items)
{
    try { AssertSomething(item); }
    catch (Exception ex) { failures.Add((item.Label, ex)); }
}
if (failures.Count > 0)
{
    var messages = failures.Select(f => $"{f.Label}: {f.Error}");
    throw new AggregateException(
        $"Failed {failures.Count}/{items.Count}:{Environment.NewLine}" +
        string.Join(Environment.NewLine + Environment.NewLine, messages),
        failures.Select(f => f.Error));
}
```

Existing examples: `ValidateElementOptionsForConfig`, `RunCoverageDAmountsForConfig` (both in `Swyfft.Services.Excel.IntegrationTests/Homeowner/ByPerilValidationTestBase.cs`).

## Test addresses — use the helper, never ask or hardcode

When a test needs a valid address for a state/carrier/rating-type, get it from
`TestAddressHelper.GetTestAddressesFiltered(...)` (`Swyfft.TestUtilities/ConstantsAndExpects/`).
It reflects over every `*GoodTestAddresses*` class and filters by product line, carrier, rating
type, state, and county, returning only addresses valid for that combination (and not already in
use). Never ask the user which address to use, and never eyeball one out of the address files.

```csharp
var address = TestAddressHelper.GetTestAddressesFiltered(
    productLine: ProductLine.Homeowner, carrierCode: CarrierCode.Qbe,
    ratingType: RatingType.EAndS, state: StateCode.NY).First();
```

## Setup asserts — verify the arrange before testing behavior

After arranging a test — especially when a helper/builder/factory creates the subject (a quote,
policy, etc.) — assert that the subject came out in the state the later assertions depend on,
before exercising any behavior: the subject was actually created, and the config/property/elements
those assertions read are populated the way this test needs.

Without these, a test fails confusingly deep in the act/assert phase — or passes vacuously — when
the real problem is that the helper never produced the required preconditions. A setup assert fails
loudly at "my arrange is wrong," which is far easier to diagnose. We repeatedly see tests break
because they never checked that the creation helper built the subject the way the later asserts
required.

Tie each setup assert to a later assertion — only assert preconditions the behavior asserts
actually rely on, not arbitrary setup details. If the test later reads an element value off the
created quote, the setup assert confirms the helper actually populated that element — not merely
that it returned a quote.
