# Test Writing

## Eli's testing pyramid: the fewest tests that prove the code works

- **Fewest tests.** Write the fewest tests that prove the code works. Each test proves one behavior the change adds or fixes. No test re-proves what another test already proves, and none carries setup or data the code under test never reads.
- **Unit tests prove the behavior.** A test goes up a level only when unit tests alone can't prove the code works end to end, and the plan gives that reason.
- **Most wiring is already proven.** Most changes plug into a flow that existing tests already prove is wired, and those changes get unit tests only. A new or changed risk rule is the standing case: unit tests of its logic plus its product line's `*AllRisksTests` captured assert, which records which configs run it (`CommercialAllRisksTests` → `Data/Commercial/CommercialRules.txt`). An integration test that creates a quote to watch the rule fire re-proves the risk pipeline, which is established infrastructure.
- **Unproven wiring gets one integration test.** It runs one scenario through the wired-up code to make sure the full flow ties together as expected: the behavior the change adds, or the scenario a bug failed. It doesn't repeat the unit tests' cases.
- **Some code starts at integration.** When the code's behavior can only be proven wired up, testing starts with integration tests, and they cover the cases. Two examples: a query whose SQL translation a unit test can't run, and a bug inside a real service that a mocked unit test can't reach. Unit tests that mock that path add no value and aren't written.
- **Acceptance tests are very rare.**

## FIRST principles govern every test

A test that breaks one of these gets fixed before it lands.

- **Fast**: use the lowest test class that proves the behavior, so most coverage is unit tests. A unit test that touches a DB, the network or the filesystem is a violation. The class table and pyramid rule are in the repo's `.claude/rules/dotnet-testing.md` § "Cover new features across the testing pyramid".
- **Isolated**: no ordering dependency and no reliance on another test's state. Each test arranges the data it asserts on.
- **Repeatable**: the same result on any machine, timezone or date. Pin the clock with `Time.SetDateTime(...)` and write dates as literals, not offsets from now. Never `DateTime.UtcNow`, unseeded randomness, or a dependence on today's date.
- **Self-validating**: the test asserts its own pass or fail. Nothing to read off the console.
- **Timely**: written with or before the code (`~/.claude/plan-types/bug.md` and `refactoring.md`, § "Steps and stops").

## Never write a test that restates the code

A test earns its place by failing when behavior is wrong. Never write these, and decline a reviewer's request for one:
- **Change-detector tests**: they restate code or a declaration (a factory mapping, a config boundary list, a constant), so they fail on every intentional change and only detect that a change happened.
- **Tautological tests**: the expected value comes from the code under test.

Captured asserts are the exception: they detect change on purpose, and the diff review is the check.

## Investigation & TDD
- A root cause is a hypothesis, labeled as one, until a test reproduces it.
- Before planning a test, research the infrastructure: the base classes the target project declares (`grep "public abstract class .*Base"` over it, not a default to `UnitTestBase`/`IntegrationTestBase`), its setup patterns, and the available test data and addresses.
- Build the scenario from the failing environment's real data (DB queries, logs), not synthetic values.
- Prefer `[Theory]` with `[MemberData]` over `[Fact]` for several scenarios of one behavior.
- Theory parameters use the real ClosedSet types (e.g. `AnswerYesNo`), never the strings they represent. Generate them with `GetAllValues().ToTheoryData()`.

## Failure Aggregation

A test that iterates inputs (configs, indices, sheets, theory rows) collects every failure and throws one `AggregateException` at the end. It never stops at the first failure.

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

Examples: `ValidateElementOptionsForConfig`, `RunCoverageDAmountsForConfig` (`Swyfft.Services.Excel.IntegrationTests/Homeowner/ByPerilValidationTestBase.cs`).

## Test addresses

- **Unit tests** use `TestAddressHelper.GetTestAddressesFiltered(productLine:, carrierCode:, ratingType:, state:).First()`. A helper-selected address in a unit test is never a determinism or FIRST Repeatable finding, and never gets reverted to a hardcoded constant. The exception is an address attribute that is the input under test (county, distance to coast, year built, territory): filter or pin for it and say why.
- **Integration and acceptance tests** hardcode an address no other test class uses.
- **The address lists in `Swyfft.TestUtilities/ConstantsAndExpects/` are Laurel Nichols'.** Never add, retag or edit one to make a test pass. When a carrier has no address, the test neutralizes the unrelated declines it hits, as `QbeUpgradeConfirmationTests.NeutralizeUnrelatedDeclines` does, and says so in a comment.

## Setup asserts: verify the arrange before testing behavior

After arranging a test, especially when a helper or factory creates the subject (a quote, a policy), assert the subject exists and holds the state the later assertions depend on: the config, properties and elements they read. Assert only preconditions a later assertion relies on. If the test reads an element off the created quote, the setup assert confirms the helper populated that element, not merely that it returned a quote.

Setup asserts are mandatory in every test, a throwaway discovery test included. A throwaway test's result is evidence only when its setup asserts prove it built the scenario it claims to test: the subject matches the failing environment's data in every value the scenario depends on.
