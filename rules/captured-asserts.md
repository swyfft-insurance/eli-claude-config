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

## Captured-assert merge conflicts: regenerate, never hand-merge

A merge conflict in an expected-result file is resolved by regenerating it, not by editing it. The
file's correct merged content is whatever the code produces from the merged inputs, so reconciling
the two sides by hand means guessing at output the tests compute exactly.

The regenerated content belongs in the merge commit itself:

1. Resolve the hand-written conflicts (real code, data files). Leave the expected-result files
   untouched, conflict markers and all.
2. Seed, then run the captured-assert tests. They overwrite each file wholesale.
3. Review the regenerated diff file by file.
4. Stage the expected-result files and commit the merge.

**Conflict markers in an expected-result file block nothing.** The file never compiles, and nothing
reads it before the test replaces it whole. Never invent a marker-clearing step to "make the tree
committable." That lands placeholder content in the merge commit and pushes the real values into a
second commit, which breaks `git-safety.md`'s "Merge commits: ONLY conflict resolution" and leaves a
commit in history carrying wrong baselines.
