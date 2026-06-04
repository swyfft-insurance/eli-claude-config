# Captured Assert Tests

Use the `/prebind-captured-asserts` skill to run and regenerate. It handles seeding checks, build, regeneration with `UPDATE_TEST_EXPECTED_RESULTS=true`, and diff review.

## When to regenerate

Adding new data (HomeownerStateConfig versions, quote definitions, elements, constraint codes) causes captured assert tests to pick up new entries. The skill walks through the full process.
