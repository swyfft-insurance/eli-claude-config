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
