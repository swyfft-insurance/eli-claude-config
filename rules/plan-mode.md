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

## Verification Steps

Verification steps must be derived from the change, not a generic checklist. For each change, identify:
1. What behavior changed — write a targeted test if none exists. See `~/.claude/rules/testing.md` for TDD workflow and test writing patterns.
2. What captured assert tests need regeneration — see `~/.claude/rules/captured-asserts.md`
3. What existing tests serve as regression checks for unchanged callers — explain why each is relevant

Never list a test suite without explaining why it's relevant to this specific change.
