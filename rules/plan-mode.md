# Plan Mode

> Gate 1.5 applies here — see `core-behavior.md`.

This file is organized into three parts by lifecycle stage:

- **Part A: How to PLAN** — rules that apply while drafting a plan with the user
- **Part B: REQUIRED CONTENT in every plan file** — what must appear in the plan itself (the `/create-plan-from-ticket` skill enforces this)
- **Part C: How to EXECUTE the plan** — rules that apply while working through the plan after it's drafted

---

# Part A — How to PLAN

## Discuss Before Drafting

**This is the most important rule in this file.** Plans are co-designed, not generated. Do NOT dump a long plan file as the first response to "plan this." Long plan dumps look thorough but bury bad assumptions in volume — a wrong decision in 200 lines costs far more to unwind than the same decision caught after a single back-and-forth question.

Default workflow:
1. Ask the foundational architectural questions in tight clusters (2–3 related at a time). Wait for answers.
2. Summarize decisions back briefly so misunderstandings get caught before they're baked in.
3. Draft the plan file only after the design is settled — concise outline first, full prose second.

If the user pushes back on any part of an in-flight plan, STOP and discuss — don't silently re-draft the whole thing.

## No Deferred Decisions

A plan resolves open questions. It does not defer them.

Banned phrases that signal a punted decision:
- "decide when we get there"
- "figure out later"
- "TBD"
- "we'll see what makes sense"
- "leave as an exercise"

If you catch yourself writing any of these, STOP and go back to Q&A with the user. The whole point of planning is to resolve every open question BEFORE execution starts — a plan that punts decisions to execution is just a TODO list.

If a decision genuinely cannot be made until something is discovered during execution (e.g., the right filter depends on a method name we haven't picked), either:
1. Resolve the dependent decision NOW (pick the method name during Q&A), OR
2. Add an explicit HARD STOP at the discovery point, with the deferred decision called out as the reason for stopping.

No silent punts.

## Q&A Options Must Be Genuine

See `~/.claude/rules/communication.md` § "Don't Offer Anti-Pattern Options" — **especially relevant during planning Q&A**. When asking the user to pick between options, every option must be genuinely plausible. Don't pad questions with strawman options the ticket already rules out. If the ticket says do A, B, C, don't ask "do A, B, C or skip them entirely?" — confirm and proceed (or skip the question if the answer is obvious from the ticket).

Filler options during planning are particularly toxic: they slow the discussion, confuse the user into doubting their own reading of the ticket, and erode trust in subsequent genuine concerns.

## Other planner discipline

- Don't call ExitPlanMode while actively discussing — wait for conversation to conclude.
- Read docs/CLAUDE.md BEFORE running console tasks. Never guess parameters.
- **Verify script args before writing them in plans.** When a plan invokes a script (`Build-Solution.ps1`, `Run-Seed.ps1`, `Run-DotnetTest.ps1`, etc.), open the script and read its `param(...)` block before writing the flag. Don't pattern-match from a sibling script. A wrong flag in a plan file becomes re-injected as canonical context at every compact — and downstream "explanations" of where it came from are easy to fabricate. Same discipline applies when explaining where a stale arg came from: research before answering, don't speculate.
- DB queries and log searches are information-gathering — do them DURING planning, not after.

---

# Part B — REQUIRED CONTENT in every plan file

The `/create-plan-from-ticket` skill enforces this structure. Manual plan files must match the same shape.

## Plan File Preamble

Every plan file must begin with this block after the title and type:

> **Execute steps in order. Never skip ahead, reorder, or deviate. If you encounter anything that prevents adherence to this plan, HARD STOP — explain the blocker and wait for instructions.**

## Subsystem Pre-Reads — Required Before Step 0

Every plan must list the governing `CLAUDE.md` files for the subsystems it
touches as required pre-reads, **above** Step 0. Match by topic, not by path —
the relevant doc often lives in a sibling directory (e.g.,
`Data/{State}/Homeowner/ByPeril/**/*.xlsm` is governed by
`Swyfft.Seeding/ExcelLoaders/ByPeril/CLAUDE.md`, not `Data/CLAUDE.md`).

Use the project-root `CLAUDE.md` "Namespace-Specific Documentation" table as
the index. Format inside the plan:

> **Pre-read (subsystem orientation):**
> - `Swyfft.Seeding/ExcelLoaders/ByPeril/CLAUDE.md`
> - `Swyfft.Services.Excel.IntegrationTests/CLAUDE.md`

A plan that omits these gets caught mid-execution by oddities the docs would
have explained — that's a planner discipline failure.

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

## Seeder Overrides — Required for every new not-yet-live state config

Whenever a plan adds a new `HomeownerStateConfig`, `FloodStateConfig`, `CommercialStateConfig`, or `DbbStateConfig` whose production go-live date is in the future, the plan MUST include a corresponding seeder override entry — concrete `NewQuotesOn` and `RenewalOn` dates, never `(YYYY,M,D)` placeholders — for every new config. The planner is responsible for computing dates that satisfy the strict-monotonic ordering rule. Skip this step only when prod go-live is in the past.

See `~/.claude/rules/swyfft-domain.md` § "Seeder Overrides — Purpose" for the date defaults, the four override mechanisms (HO uses `Seeder.cs`; Flood/Commercial/DBB use `EnvironmentFilters.cs:#if NONPROD`), and the common traps.

## Verification Section Structure

Verification steps must be derived from the change, not a generic checklist. The Verification section is one cohesive block at the end of the plan — don't split it into "Test plan" + "Verification" (creates duplication and dangling sections). Order so the implementer-facing flow comes first, with the rest as labeled reference material.

**The planner MUST drive verification via Q&A, item by item.** Walk through every AC in the ticket and ask "how do we verify this specifically? what command/test/file-check proves AC #N passes?" Then walk through the canonical generic-verification checklist (in `/create-plan-from-ticket` skill) and ask "does X apply here?" for each. Nothing is auto-included; nothing is assumed.

### Execution sequence (before pushing)
Numbered steps in order, derived from the AC walk-through and canonical-checklist answers. Each `Run-DotnetTest.ps1` line should cross-reference the test artifact it's exercising (defined in the sections below).

### Tests to add or modify
List each new/extended test file with: filename, base class, and a case table (input → expected). One row per scenario. See `~/.claude/rules/testing.md` for TDD workflow and test-writing patterns.

Tests that iterate over multiple inputs (configs, indices, sheets, theory rows) must aggregate failures into a list and throw `AggregateException` at the end — never stop at the first failure. See `testing.md` § "Failure Aggregation".

### Captured asserts to regenerate
List the expected diffs by file, including which files should have **zero** diff (these are the negative-confirmation guards). The actual `/prebind-captured-asserts` invocation lives in the execution sequence — this section just describes what the diffs should look like. See `~/.claude/rules/captured-asserts.md`.

### Existing tests as regression checks
Tests that should still pass without edits — list with a one-line "why this is relevant to this change". Never list a test suite without a reason.

### AC coverage map
Table mapping every AC from the ticket → which subsection covers it. Surfaces gaps and proves AC #N didn't get forgotten.

### Transition out of verification

Verification ends when (a) all agreed-upon tests pass and (b) the user explicitly agrees we're "done". The post-test-approval sequence (commit + push → adversarial review → PR draft → PR creation) is **not part of verification** and is governed by Part C § "Post-Test-Approval Sequence".

## `/prebind-captured-asserts` is the default for most plans

The skill name reflects its origin (PreBind captured asserts), but its scope has grown to be "the standard suite of tests Eli wants run on most PRs." Treat it as default verification for the majority of tickets, not just ones touching pre-bind / element generators. Any plan that affects elements, state configs, generators, or rating-adjacent code should include `/prebind-captured-asserts` in the execution sequence.

---

# Part C — How to EXECUTE the plan

## ALWAYS FOLLOW THE PLAN

Execute steps in order. Never skip ahead, reorder, or deviate. If a step depends on a previous step, that's a hard stop — don't proceed until the dependency is satisfied. If you encounter anything that prevents you from adhering to the plan, **HARD STOP** — explain the blocker and wait for instructions. Deviation and disobedience are not allowed.

## Reacting to Surprises

**HARD STOP** — If a build fails, a test fails unexpectedly, or anything doesn't match the plan — stop and explain before pivoting. (This is Gate 1.5, applied to plan execution.)

## Build Once, Run Tests in Parallel

When a verification step runs multiple test suites, **build the solution ONCE** with `pwsh ./Build-Solution.ps1`, then invoke each test runner in parallel with its `-NoBuild` flag (single message, multiple Bash tool calls).

**This applies to every test invocation in the parallel block** — `Run-DotnetTest.ps1`, test-running skills like `/prebind-captured-asserts`, or any wrapper script. **Before adding any invocation to a parallel block, verify its build behavior** — `Read` its SKILL.md / script `param(...)` block. If it builds by default, pass `-NoBuild` (or equivalent skip-build flag).

Don't:
- Let any invocation build implicitly when others are also running — multiplies build time AND causes build contention (parallel builds fight over output files/locks).
- Assume a skill/script doesn't build because its description doesn't mention building. Verify by reading the source.
- Run independent test suites sequentially.

See `~/.claude/rules/testing-execution.md` § "Test Output — Run-DotnetTest.ps1" for `-NoBuild` parameter details.

## Post-Test-Approval Sequence

Picks up where verification ends (tests pass + user agrees we're "done"). The sequence to PR is fixed:

1. Ask once for approval to commit and push (single action — no separate ask for each).
2. Commit (`SW-XXXXX: <summary>` per `git-safety.md` / project CLAUDE.md) and push (verify tracking via `git branch -vv` first).
3. Run `/review-pr` against the pushed state.
4. **Discuss `/review-pr` findings with the user.** Don't autonomously start fixing. `/review-pr` is the first reviewer of completed work, not a safety net — plan for it to find nothing.
5. If findings warrant action: push ONE additional commit. **Do not run a second `/review-pr` after that commit.** One adversarial review per branch, full stop.
6. **MANDATORY: `Read` `~/.claude/rules/pr-creation.md` before drafting the PR description.** No exceptions. No "I just read it." No "I remember the rules." Then draft the PR description following those rules.
7. **HARD STOP** — wait for approval, then create the PR.

## Captured Asserts: Read Every Changed File

When a captured-assert regen produces diffs, you MUST individually open and assess every changed file before committing or moving on. No sampling. No "I checked 3 of 28 and the rest looked similar." The captured-assert system exists precisely because each file encodes information your mental model can't reliably predict — sampling defeats its purpose and reintroduces exactly the bugs the system was built to surface.

If a regen touches 30+ files, that's 30+ individual reads. There is no shortcut. Skipping this step is a Gate 3 violation by another name (extrapolating from partial data).

## Line Length

C# code lines must stay at or below **120 characters** including leading indent. This is a hard rule — wrap longer lines at natural punctuation: after commas, before operators, between method-chain links, or after the opening paren of a method call. Applies to `.cs` files only (production code AND tests). Markdown, `.txt` data files, JSON, YAML, etc. are exempt — prose and config wrap differently than code. No exceptions for "readability" within `.cs` — if the line is over, it gets wrapped.

When a wrapped construct has multiple peer items (e.g., theory data rows, parameter lists, collection initializers), pick ONE wrapping pattern and apply it to ALL peers — don't mix single-line and multi-line entries in the same group. Inconsistent wrapping is the worst of both worlds and will be flagged.

This applies only to lines newly written or modified by the current change. Pre-existing long lines that aren't being touched stay as-is — don't hijack the diff to reformat unrelated code.

**Verification**: `~/.claude/scripts/Test-LineLength.ps1 -Mode local` (or `-Mode branch`) scans the unified diff for added/modified `.cs` lines and exits non-zero if any exceed 120 chars. Run this before declaring "code complete" on any plan. The script is a backstop, not a substitute for writing it correctly the first time — self-check while editing rather than relying on the post-hoc gate.

## Magic Numbers / Strings

Hardcoded numeric / string literals must be extracted to named constants. Even sentinels like `int.MaxValue` used to mean "no limit" get a named alias — the name encodes intent the value alone doesn't. Applies to plan code excerpts AND executed code.

Bad: `RenderSheet(ws, int.MaxValue, 64, lines.Add);`

Good:
```csharp
const int allRows = int.MaxValue;
const int maxColumnsToCapture = 64;
RenderSheet(ws, allRows, maxColumnsToCapture, lines.Add);
```
