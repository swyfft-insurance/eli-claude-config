# Captured Assert Tests

Use the `/eli--prebind-validation` skill to run and regenerate. It handles seeding checks, build, regeneration with `UPDATE_TEST_EXPECTED_RESULTS=true`, and diff review.

## How captured-assert updates work: known, don't research it

Settled and unchanging. **Never** investigate the compile symbol, `CapturedAssert` internals, or env-var plumbing to figure out how regen works. Every plan just knows:

- **Locally, running the captured-assert tests auto-updates their expected-result files.** Run them and the baselines rewrite in place. The var is set at the User env scope and inherited by agent tool shells, so it's already on, but still prefer passing `UPDATE_TEST_EXPECTED_RESULTS=true` inline on the test command too, to be extra sure.
- **CI test runners do *not* have the flag set.** That's where captured-assert tests *fail* if the committed baselines don't already match. That failure is the guard that forces you to commit updated asserts.
- **Local workflow:** run the captured asserts → they update → **review the git diff and confirm it's the expected diff.** The diff review is the verification, not confirming regen "engaged."

## When to regenerate

Adding new data (HomeownerStateConfig versions, quote definitions, elements, constraint codes) causes captured assert tests to pick up new entries. The skill walks through the full process.

## What a quote-def captured-assert diff shows (dates)

Seeded captured asserts (`SeedingCoreBruteForceTest_EFHomeownerQuoteDefinitions…`,
`GetQuoteDefinitionForQuotePurchase`/`…Renewal`) show the **`Seeder.cs` override** dates, not the
`QuoteDefinitions.txt` prod dates. For the full map of which dates live where, the file's global
ordering, and the tests that enforce each, see `~/.claude/rules/quote-def-dates-and-ordering.md`.
