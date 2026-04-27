# Plan Mode

> Gate 1.5 applies here — see `core-behavior.md`.

- Don't call ExitPlanMode while actively discussing — wait for conversation to conclude.
- **ALWAYS FOLLOW THE PLAN.** Execute steps in order. Never skip ahead, reorder, or deviate. If a step depends on a previous step, that's a hard stop — don't proceed until the dependency is satisfied. If you encounter anything that prevents you from adhering to the plan, **HARD STOP** — explain the blocker and wait for instructions. Deviation and disobedience are not allowed.
- Read docs/CLAUDE.md BEFORE running console tasks. Never guess parameters.
- DB queries and log searches are information-gathering — do them DURING planning, not after.

## Plan File Preamble

Every plan file must begin with this block after the title and type:

> **Execute steps in order. Never skip ahead, reorder, or deviate. If you encounter anything that prevents adherence to this plan, HARD STOP — explain the blocker and wait for instructions.**

## IMPORTANT: Step 0 — Create a Branch

**Every plan, every time, no exceptions.** The first step in every plan, before any step that writes code:
1. Check if the current branch is appropriate for this ticket. `development`, `beta`, and `master` are never appropriate. A branch for a different ticket is never appropriate.
2. If not, create a new branch with `/create-branch` and push it.

## Step 0.5 — Baseline Captured Asserts (when applicable)

**If the ticket is expected to change captured asserts** (touches `ElementLoader*.cs`, `ConstraintCode.cs`, `HomeownerStateConfig.cs`, `QuoteDefinitions.txt`, or anything captured by `GetDefaultElementsForState` / `GetQuoteDefinitionForQuotePurchase`), do this BEFORE any code changes:

1. Invoke `/seed database`. Full DB reseed is required for the baseline — element-only seed doesn't update `QuoteDefinitions`, state configs, or rater data, so the baseline regen would reflect a stale local DB instead of current development.
2. Invoke `/prebind-captured-asserts`.
3. Commit the resulting diff as a baseline catch-up commit:
   ```
   {TICKET}: Regenerate {test name} expected results

   Catch-up commit for the {date} {what} that landed in development
   before this branch. Pure regeneration — no functional changes —
   kept as a separate commit so the {TICKET} diff stays limited to
   {ticket scope}.
   ```
4. Now start making ticket changes. The ticket's own captured-assert regen at the end can be scoped to whatever the ticket changed (`/seed elements` if you only touched element loaders) — you don't need a full DB reseed again.

If the ticket doesn't touch any of the listed surfaces, skip this step.

## Plan Types

Every plan must declare its type. The type determines the workflow and mandatory stops. Don't stop between individual file edits within the same phase — stop at the defined boundaries.

### Bug Fix

1. Investigate — read ticket, logs, code to form a hypothesis
2. Reproduce — write a failing test that proves the hypothesis
3. **HARD STOP** — TDD checkpoint. Test fails as expected. Wait for approval before writing the fix.
4. Fix — write the code fix
5. **HARD STOP** — Code complete. Show the full diff. Wait for approval before running tests.
6. **HARD STOP** — Tests complete. Report results. Wait for approval before continuing.
7. **HARD STOP** — Before irreversible actions (push/PR/seeding/external posts). Wait for approval.

### Refactoring

1. Write safety-net test — covers the behavior being refactored
2. **HARD STOP** — TDD checkpoint. Test passes. Wait for approval before refactoring.
3. Refactor — make the changes
4. **HARD STOP** — Code complete. Show the full diff. Wait for approval before running tests.
5. **HARD STOP** — Tests complete. Report results. Wait for approval before continuing.
6. **HARD STOP** — Before irreversible actions (push/PR/seeding/external posts). Wait for approval.

### Feature

1. Make code changes
2. **HARD STOP** — Code complete. Show the full diff. Wait for approval before running tests.
3. **HARD STOP** — Tests complete. Report results. Wait for approval before continuing.
4. **HARD STOP** — Before irreversible actions (push/PR/seeding/external posts). Wait for approval.

## Reacting to Surprises

**HARD STOP** — If a build fails, a test fails unexpectedly, or anything doesn't match the plan — stop and explain before pivoting. (This is Gate 1.5, applied to plan execution.)

## Verification Section Structure

Verification steps must be derived from the change, not a generic checklist. The Verification section is one cohesive block at the end of the plan — don't split it into "Test plan" + "Verification" (creates duplication and dangling sections). Order so the implementer-facing flow comes first, with the rest as labeled reference material:

### Execution sequence (before pushing)
Numbered steps in order: build → seed (if data changed, see `~/.claude/rules/seeding.md`) → `/prebind-captured-asserts` + diff review → targeted tests via `Run-DotnetTest.ps1` → `/review-pr`. Each `Run-DotnetTest.ps1` line should cross-reference the test artifact it's exercising (defined in the sections below).

### Tests to add or modify
List each new/extended test file with: filename, base class, and a case table (input → expected). One row per scenario. See `~/.claude/rules/testing.md` for TDD workflow and test-writing patterns.

### Captured asserts to regenerate
List the expected diffs by file, including which files should have **zero** diff (these are the negative-confirmation guards). The actual `/prebind-captured-asserts` invocation lives in the execution sequence — this section just describes what the diffs should look like. See `~/.claude/rules/captured-asserts.md`.

### Existing tests as regression checks
Tests that should still pass without edits — list with a one-line "why this is relevant to this change". Never list a test suite without a reason.

### AC coverage map
Table mapping every AC from the ticket → which subsection covers it. Surfaces gaps and proves AC #N didn't get forgotten.

## /prebind-captured-asserts is a misnomer

The skill name reflects its origin (PreBind captured asserts), but its scope has grown to be "the standard suite of tests Eli wants run on most PRs." Treat it as default verification for the majority of tickets, not just ones touching pre-bind / element generators. Any plan that affects elements, state configs, generators, or rating-adjacent code should include `/prebind-captured-asserts` in the execution sequence.
