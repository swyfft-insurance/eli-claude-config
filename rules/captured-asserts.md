# Captured Assert Tests

## Running them

Run and regenerate them with `/eli--prebind-validation`.

## How captured-assert updates work: known, don't research it

Never investigate the compile symbol, `CapturedAssert` internals or env-var plumbing.

- Locally, running the captured-assert tests rewrites their expected-result files in place. `UPDATE_TEST_EXPECTED_RESULTS` is already set at User scope; pass `UPDATE_TEST_EXPECTED_RESULTS=true` inline on the test command too.
- CI runners don't set it, so a baseline that wasn't regenerated and committed fails there.
- Review the git diff and confirm it is the expected diff. That review is the verification.

## When to regenerate

Regenerate after adding HomeownerStateConfig versions, quote definitions, elements or constraint codes.

## What a quote-def captured-assert diff shows (dates)

Seeded captured asserts (`SeedingCoreBruteForceTest_EFHomeownerQuoteDefinitions…`, `GetQuoteDefinitionForQuotePurchase`/`…Renewal`) show the `Seeder.cs` override dates, not the `QuoteDefinitions.txt` prod dates. See `quote-def-dates-and-ordering.md`.

## Captured-assert merge conflicts: regenerate, never hand-merge

Resolve a conflicted expected-result file by regenerating it, inside the merge commit:

1. Resolve the hand-written conflicts. Leave the expected-result files untouched, markers and all.
2. Seed, then run the captured-assert tests. They overwrite each file whole.
3. Review the regenerated diff file by file.
4. Stage the expected-result files and commit the merge.

Conflict markers in an expected-result file block nothing. Never add a marker-clearing step, and never put the real values in a second commit (`git-safety.md`: merge commits are conflict resolution only).
