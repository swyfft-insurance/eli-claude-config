# Captured Assert Tests

Use the `/prebind-captured-asserts` skill to run and regenerate. It handles seeding checks, build, regeneration with `UPDATE_TEST_EXPECTED_RESULTS=true`, and diff review.

## When to regenerate

Adding new data (HomeownerStateConfig versions, quote definitions, elements, constraint codes) causes captured assert tests to pick up new entries. The skill walks through the full process.

## Baseline Isolation

For tickets that will change captured asserts, do the baseline regen BEFORE making code changes — see "Step 0.5 — Baseline Captured Asserts" in `plan-mode.md`. Baseline always uses `/seed database` (full DB reseed); the ticket's own seed at the end can be scoped to what the ticket changed.

If you're already mid-ticket and discover drift in the regen output, stash → full DB seed → baseline regen → commit → pop stash → ticket seed → ticket regen recovers the same outcome — but it's avoidable noise. Plan it up front.
