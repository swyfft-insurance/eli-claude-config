# Plan Mode

- Don't call ExitPlanMode while actively discussing — wait for conversation to conclude.
- Follow plans exactly. Don't skip, substitute, add, or omit steps. When blocked, ask.
- **Hard stop after each step.** Complete one step, show what you did, and wait for approval before starting the next. Don't batch multiple steps or skip ahead. The plan itself must include explicit hard stops between steps.
- Read docs/CLAUDE.md BEFORE running console tasks. Never guess parameters.
- DB queries and log searches are information-gathering — do them DURING planning, not after.

## Verification Steps

Verification steps must be derived from the change, not a generic checklist. For each change, identify:
1. What behavior changed — write a targeted test if none exists. See `~/.claude/rules/testing.md` for TDD workflow and test writing patterns.
2. What captured assert tests need regeneration — see `~/.claude/rules/captured-asserts.md`
3. What existing tests serve as regression checks for unchanged callers — explain why each is relevant

Never list a test suite without explaining why it's relevant to this specific change.
