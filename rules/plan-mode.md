---
paths:
  - "**/.claude/tickets/**/plan.md"
---
# Plan Mode

> Gate 1.5 applies here — see `core-behavior.md`.

This file is organized into three parts by lifecycle stage:

- **Part A: How to PLAN** — rules that apply while drafting a plan with the user
- **Part B: REQUIRED CONTENT in every plan file** — what must appear in the plan itself (the `/eli--create-plan-from-ticket` skill enforces this)
- **Part C: How to EXECUTE the plan** — rules that apply while working through the plan after it's drafted

## FULL-COVERAGE MANDATE — read before writing or executing ANY plan

**Every plan must incorporate EVERY rule in this file — Parts A, B, AND C — not merely the sections Part B enumerates.** A plan is not a document that happens to list some sections; it must *embody the entire ruleset*:

- **Part A** — the plan was co-designed via Q&A, with no deferred decisions and only genuine options.
- **Part B** — every mandated section is written into the file (or marked `N/A — <reason>` for the conditional ones).
- **Part C** — every execution rule is honored and, where it produces a step, written into the plan: the HARD STOP sequence matching the declared plan type, the comment self-audit, the ClosedSet self-audit, line-length, magic-number extraction, build-once-then-parallel test runs, "read every changed captured-assert file," and the post-test-approval sequence.

If a rule appears anywhere in this file, it must be reflected in the plan. A plan that silently drops any rule is incomplete — the same as a missing test or seeder override. This is exactly why the skill mandates re-reading the rules between every step: so nothing falls out of working memory and gets dropped after a couple of actions. `/eli--plan-audit` enforces this mandate. It runs on every plan before the plan counts as written, whether the plan came from `/eli--create-plan-from-ticket` or was written by hand.

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

See `~/.claude/rules/talking-to-eli.md` § "Don't Offer Anti-Pattern Options" — **especially relevant during planning Q&A**. When asking the user to pick between options, every option must be genuinely plausible. Don't pad questions with strawman options the ticket already rules out. If the ticket says do A, B, C, don't ask "do A, B, C or skip them entirely?" — confirm and proceed (or skip the question if the answer is obvious from the ticket).

Filler options during planning are particularly toxic: they slow the discussion, confuse the user into doubting their own reading of the ticket, and erode trust in subsequent genuine concerns.

## Stop Being Pedantic

See `~/.claude/rules/talking-to-eli.md` § "Stop being pedantic" — **especially relevant while reading a ticket and drafting a plan from it.** When you know what the author intended, that is the end of it: act on it and say nothing. It is blatantly obvious — a human reads it and immediately knows exactly what was meant, and it did not trip you up either. So the correction gains nothing and costs multiple turns, time, and tokens. Something that is genuinely wrong and confusing is a different thing — that gets raised.

## Other planner discipline

- Don't call ExitPlanMode while actively discussing — wait for conversation to conclude.
- Read docs/CLAUDE.md BEFORE running console tasks. Never guess parameters.
- **Verify script args before writing them in plans.** When a plan invokes a script (`~/.claude/scripts/Build-Solution.ps1`, `Run-Seed.ps1`, `~/.claude/scripts/Run-DotnetTest.ps1`, etc.), open the script and read its `param(...)` block before writing the flag. Don't pattern-match from a sibling script. A wrong flag in a plan file becomes re-injected as canonical context at every compact — and downstream "explanations" of where it came from are easy to fabricate. Same discipline applies when explaining where a stale arg came from: research before answering, don't speculate.
- DB queries and log searches are information-gathering — do them DURING planning, not after.
- Write plan prose with no ambiguous references — repeat the noun rather than leaving "it"/"this"/"that"/"they" for the reader to resolve. See `~/.claude/rules/talking-to-eli.md` § "No Ambiguous References".

---

# Part B — REQUIRED CONTENT in every plan file

The `/eli--create-plan-from-ticket` skill enforces this structure. Manual plan files must match the same shape.

## Ticket folder, plan, & artifacts

Each ticket's work lives in its own folder — `~/.claude/tickets/{ticket-ids}-{title-slug}/` —
keyed by ticket ID(s) with a readable title slug (single: `SW-52867-<title>`; multiple: all IDs
sorted ascending + a combined title, e.g. `SW-51860-SW-52867-<title>`; no "primary" ticket). The
folder holds:

- **`plan.md`** — the plan, opened with a header block listing every `SW-XXXXX` (with YouTrack
  links) and the title(s). Tracked in git.
- **`artifacts/`** — every dump the work produces (ticket dumps, test output, seed logs, SolarWinds
  dumps). Bulky dumps are gitignored; the small human-authored evidence — `artifacts/db-queries/`
  (query SQL + results) and `artifacts/pr/` (PR body files) — is tracked in git along with
  `plan.md`.

Never scatter artifacts loose or in sibling folders. The `/eli--create-plan-from-ticket` skill
creates this layout; the dump scripts (`read-ticket`, `Run-DotnetTest`, `Run-Seed`,
`Search-SolarWinds`, etc.) take the ticket folder name as a required argument and write into its
`artifacts/`, so everything for a ticket stays together.

## Plan File Preamble

Every plan file must begin with this block after the title and type:

> **Execute steps in order. Never skip ahead, reorder, or deviate. If you encounter anything that prevents adherence to this plan, HARD STOP — explain the blocker and wait for instructions.**

## IMPORTANT: Step 0a — Confirm the ticket(s) are in Develop

**Every plan, every time, before anything else** — before the subsystem pre-reads and before the
branch. For every YouTrack ticket the plan covers:

1. Read the ticket's current Stage.
2. If the Stage is earlier than Develop (Backlog, Ready for Dev), move it to Develop and tell the
   user. This is a workflow-triggered transition — it does NOT need separate Gate 2 approval, the
   same way the post-PR move to Review doesn't (see `youtrack.md`).
3. If the Stage is already Develop or later (Review, Ready for Test, Done, Tested), leave the Stage
   untouched — never move a ticket backward.
4. If YouTrack is unreachable (VPN down, MCP failing), HARD STOP and ask — don't plan against a
   ticket whose Stage you can't read.

## Subsystem Pre-Reads — Required Before Step 0b

Every plan must list the governing `CLAUDE.md` files for the subsystems it
touches as required pre-reads, **above** Step 0b. Match by topic, not by path —
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

## IMPORTANT: Step 0b — Create a Branch

**Every plan, every time, no exceptions.** Before any step that writes code:
1. Check if the current branch is appropriate for this ticket. `development`, `beta`, and `master` are never appropriate. A branch for a different ticket is never appropriate.
2. If not, create a new branch with `/create-branch` and push it.

## Plan Types

Every plan must declare its type. The type determines the workflow and mandatory stops. Don't stop between individual file edits within the same phase — stop at the defined boundaries.

<!-- Restructured 2026-08-19 while planning SW-54482/SW-54691 — Eli: a bug plan can't be cemented
     before the defect is diagnosed AND proven, and the proof may disprove the bug. The old shape put
     Investigate/Reproduce inside execution, i.e. after the plan was already written. -->
### Bug Fix

Diagnose first, then plan the fix. There is no plan for the investigation. Writing one is ceremony
that delays the work.

1. Investigate. Whatever settles which mechanism fired: reading code, a log search, a SQL query, a
   diagnostic harness run, a throwaway test, or a test that becomes the regression guard. No form is
   privileged.
2. **HARD STOP** — Report the mechanism, its evidence, and a disposition: fix, spin off, not a
   defect, or already fixed. The last two end the work with no fix plan written. Wait for approval.
3. Write a **minimal** fix plan: what changes, the test that guards it, how it's verified. Part B's
   full apparatus does not apply to a bug. Include only what the fix actually touches.
4. **HARD STOP** — Fix plan approved. Wait before writing code.
5. Fix — write the code fix
6. **HARD STOP** — Code complete. Don't print the diff — Eli reviews diffs himself (GitHub Desktop). Announce code-complete and wait for approval before running tests.
7. **HARD STOP** — Tests complete. Report results. Wait for approval before continuing.
8. **HARD STOP** — Before irreversible actions (push/PR/seeding/external posts). Wait for approval.

#### What the diagnosis must establish

- **The defect**: the line or branch where behavior diverges from intent. Short of naming it, say so
  and name what would settle it.
- **Evidence per claim**, with hypothesis and proven labeled separately. An uncited causal chain is a
  story.
- **The proving test's fate**, if one was written: kept as the regression guard, or discarded.
- **Noticed, not diagnosed**: one line each for findings outside the defect. Never investigate one to
  decide whether it belongs, and never bolt one onto another finding as a caveat.

Scope is the mechanism the ticket reports plus whatever is reasonably part of that same defect; an
incomplete bug report doesn't narrow the defect. A diagnosis posted by someone else is where yours
starts, never where it ends: verify each claim against the code before building on it.

#### Code tracing is only evidence when a stack trace anchors it

With an explicit stack trace, code tracing is great evidence: the runtime named the path and the
line, so following the frames is fact rather than inference. A trivial cause is provable the same way.

Without either, it is a poor form of evidence and a waste of time. It also does not self-terminate:
each disproof spawns the next theory, so it loops, announcing a discovered cause every round. Don't
rely on noticing that happening. No stack trace and no trivial cause means the next action is
empirical, not another read.

Plenty of upfront research on a non-obvious bug is still wanted. It just has to be a log search, a
SQL query, or a test, whichever fits.

Never pair a discovery with a claim that the next thing will prove it. Say what the evidence would
rule out.

**What happened:** SW-54482 shipped a stack trace, and every conclusion inside those frames held up.
Four causes were then announced for why the census column was empty, which no frame covered, each
from tracing alone and each with a promise the next query would prove it. All four were wrong.

### Refactoring

1. Write safety-net test — covers the behavior being refactored
2. **HARD STOP** — TDD checkpoint. Test passes. Wait for approval before refactoring.
3. Refactor — make the changes
4. **HARD STOP** — Code complete. Don't print the diff — Eli reviews diffs himself (GitHub Desktop). Announce code-complete and wait for approval before running tests.
5. **HARD STOP** — Tests complete. Report results. Wait for approval before continuing.
6. **HARD STOP** — Before irreversible actions (push/PR/seeding/external posts). Wait for approval.

### Feature

1. Make code changes
2. **HARD STOP** — Code complete. Don't print the diff — Eli reviews diffs himself (GitHub Desktop). Announce code-complete and wait for approval before running tests.
3. **HARD STOP** — Tests complete. Report results. Wait for approval before continuing.
4. **HARD STOP** — Before irreversible actions (push/PR/seeding/external posts). Wait for approval.

### Excel Rater (ByPeril)

A distinct plan type for rater-update tickets: actuarial delivers a new rater `.xlsm` and the C# is brought into agreement with it. The change can land on any sheet — base rates, any factor table, inputs, fees, optional coverages, layout. The ticket gives a general outline of what's changing, but the precise footprint isn't pinned down until you diff the placed file. Almost always declared `Feature` in YouTrack, but distinct enough to call out here. It **follows the Feature HARD STOP sequence above, plus one added HARD STOP**: a scoping checkpoint after the rater is placed and before any C#, reconciling the regenerated-baseline diff against the provisional scope.

It **inherits every other rule in this file** — the Gates, Parts A/B/C, the Seeder-Override and HomeownerStateConfig ticket-note requirements, and the full Verification structure. The **one** carve-out: scope stays provisional until the rater diff exists at execution (you can't see the change while authoring). When this is the ticket's plan type, reading the matching playbook in full is **MANDATORY** — `~/.claude/rules/ho-excel-rater-plans.md` for Homeowner or `~/.claude/rules/co-excel-rater-plans.md` for Commercial, plus the shared `~/.claude/rules/excel-rater-plans-common.md`. Together they hold the complete playbook (pre-reads, the plan shape, the component→Excel-signal map).

### Audit-Doc LogMonitor (catch-all)

For LogMonitor tickets on audit-doc generation failures (`GenerateAuditDocs - GenerateAuditDoc` signatures, HO or Commercial). These tickets are catch-alls: the LogMonitor matches the error *signature*, not specific quotes or root causes, so one ticket covers every quote currently failing the audit — often several distinct root causes at once. A failing quote re-fires on every audit run until an actual fix lands (failed audits are never marked audited); it never stops failing on its own.

**Non-prod (beta) mismatches on not-yet-launched configs are often expected, not defects.** A config that hasn't launched (no prod book — e.g. still on V1) takes premium-bearing changes **in place** — changes that would normally require a new version get applied directly to the existing quote def, because beta is a sandbox (the in-place convention is documented with the state-config versioning rules). Consequence: a beta quote purchased before such an in-place change re-rates differently after it, so its audit shows DB(bind) ≠ Excel/Recompute(now) by design. Before treating a beta audit mismatch on an unlaunched config as a defect, verify the timeline: if a premium-bearing in-place change landed on the config after the quote was purchased, the mismatch is expected fallout, not a bug.

The defense-in-depth model: the ByPeril Excel integration tests are the first line of defense — they're supposed to catch C#-vs-rater problems before anything ships. The production audit-doc job is the second line. So any failure that surfaces in audit docs is, by definition, a failure that got past the Excel tests — meaning the work on an audit-doc bug isn't done at "diagnose and fix the defect." It must also answer: why didn't the Excel integration tests catch this scenario? And where coverage is possible, extending the tests to cover that scenario class is part of the fix — so the same class of failure gets caught at the first line next time. The carve-out: some scenario classes genuinely can't be covered by the Excel tests — the ghost reprice, for example, is post-bind data mutation, not anything a rater-vs-C# comparison harness can exercise — so "when possible" is a real qualifier, not a loophole.

#### "The errors stopped" is not a diagnosis — resolve which outcome it was

`GenerateAuditDoc` has four outcomes and only one keeps logging. Read them off `ExcelQuoteAuditServiceBase.GenerateAuditDoc` before interpreting any gap in the logs:

| Outcome | `AuditDocsGeneratedOn` | Logs every run? | Live defect? |
|---|---|---|---|
| **Failure** — exception thrown | left NULL | yes — hourly, forever | yes |
| **MisMatch** — premium differs | **marked** | no — logs once, then never re-selected | **yes** |
| **Success** — premium matches | marked | no | no |
| **Skipped** — IMS record gone | marked | warns once | no |

The marking happens **before** the premium comparison, so a MisMatch counts as marked. A signature that stops firing therefore means only that the crash stopped — it does **not** mean the audit passed. A quote can leave the queue still mis-priced: a defect that needs a fix and will never re-announce itself.

Never write "the audit succeeded" or "this is fixed" from an absence of logs. Separate the outcomes with evidence: a MisMatch logs its own error carrying the quote id, so a quote-id-scoped search across the full window distinguishes MisMatch from Success-or-no-longer-selected; `AuditDocsGeneratedOn` plus the stored premium settles the remainder.

**A quote can walk through several outcomes as code ships.** The table above is not a fixed property of a quote — the same quote can crash for days, then stop crashing once a fix lands and instead record a MisMatch (which marks it, ending the hourly errors), and then have the mismatch cause fixed later with nothing ever re-running to say so.

The logs tell you history. A marked quote is never re-audited, so log reading won't establish whether a quote audits correctly now — run `/eli--byperil-audit-diagnostic` for that, since it executes the audit service's own `ComparePremium` against the live rater.

Plan shape:
1. **SolarWinds first** — search the ticket's own search-link terms, from the ticket's filing date ("First seen") to now. The ticket was filed for the quotes in its description, but the "still occurring" comments mean the ticket is still the catch-all for this signature right now — even if the quotes that got it filed have since been fixed. The work list is whatever the search shows still failing.
2. **Group the current set by distinct failure** (config / state / error shape) and diagnose each group — `/eli--byperil-audit-diagnostic` per quote group, interpreted per the `eli--audit-doc-mismatch-investigation` skill.
3. **Post an RCA on the ticket for every distinct failure** — including the description's quotes when they no longer fail: that RCA states they now pass, and identifies when/what fixed them where findable (a bonus, not required).
4. **Spin-off is dealer's choice** — distinct failures may be split into separate tickets (per-failure or per-QuoteDef: SW-48603 → SW-49434…SW-49439) or RCA'd in place on the umbrella ticket (SW-51664's three RCAs). Ask.
5. The ticket is done only when every failure in the current set has an RCA and a disposition — fix shipped, spun off, or no-action-with-reason.

Any code fix that emerges follows the Bug Fix HARD STOP sequence.

## Seeder Overrides — Required for every new not-yet-live state config

Whenever a plan adds a new `HomeownerStateConfig`, `FloodStateConfig`, `CommercialStateConfig`, or `DbbStateConfig` whose production go-live date is in the future, the plan MUST include a corresponding seeder override entry — concrete `NewQuotesOn` and `RenewalOn` dates, never `(YYYY,M,D)` placeholders — for every new config. The planner is responsible for computing dates that satisfy the strict-monotonic ordering rule. Skip this step only when prod go-live is in the past.

**Computing the dates** — overrides exist to activate the new quote defs in local/dev/beta *earlier* than their real prod go-live (in `QuoteDefinitions.txt`), so the configs are testable before launch. Set `NewQuotesOn` to today or yesterday so the config is the active version on merge. Set `RenewalOn` to a date strictly after the predecessor's effective `RenewalOn` and not shared with any other config's `RenewalOn` in the family — the predecessor being the config declared immediately before the new one in its State/Carrier/RatingType group (the current latest version in that family, usually what you `sourceConfig:` from), using its own override if it has one else its `QuoteDefinitions.txt` value (go read it). `RenewalOn` may equal `NewQuotesOn` or fall later, and `NewQuotesOn` must likewise be unique among the family's `NewQuotesOn`s. Both constraints are enforced by `EnsureConfigOrderWithDatabase` (orders each State/Carrier/RatingType group by `RenewalOn`) and `HoQuoteDefs_WithNonProdOverrides_ShouldNotViolateUniqueIndexes` (composite unique indexes on `NewQuotesOn` and `RenewalOn`), both run by `/eli--prebind-validation` — don't hand-verify.

See `~/.claude/rules/swyfft-domain.md` § "Seeder Overrides — Purpose" for the date defaults, the four override mechanisms (HO uses `Seeder.cs`; Flood/Commercial/DBB use `EnvironmentFilters.cs:#if NONPROD`), and the common traps.

**MANDATORY — run the override audit BEFORE computing new overrides.** Any plan that adds a new `HomeownerStateConfig`, `FloodStateConfig`, or `DbbStateConfig` MUST run `/eli--quote-def-override-audit` during planning, before the new override dates are computed. Remove flagged overrides in the same product line(s) as the new overrides, or record why one stays. Leave flagged overrides in other product lines alone. Removing a predecessor's stale override changes the predecessor's effective `RenewalOn` back to its prod date, which changes what the new override's `RenewalOn` must clear — so auditing after the overrides are written forces recomputing them. (Commercial overrides aren't covered by the audit.) The audit deterministically diffs every HO/Flood/DBB override against `QuoteDefinitions.txt` and lists the ones whose config is already live — don't hand-compare. See `~/.claude/rules/quote-def-dates-and-ordering.md` § "Finding stale overrides".

## State-config changes — fold-vs-stack and version doc-comments (MANDATORY, every product line)

**Every plan that makes a version-gated change to ANY state config — `HomeownerStateConfig`, `CommercialStateConfig`, `FloodStateConfig`, or `DbbStateConfig` (every `IStateConfig` implementer) — MUST address both principles below. No exceptions.** A version-gated change is any change confined to specific config versions — a new version, a fold into a parked version, or in-place on a not-yet-live V1. This is a required, reviewed checkpoint: if a plan touches a gated config and doesn't explicitly cover both points, it is incomplete — HARD STOP and fix it before execution.

1. **Prefer folding over stacking — *only* as a default when the ticket is silent on version structure.** When the ticket or epic explicitly dictates fold vs stack, follow the ticket — it takes precedence, and you do NOT justify the choice or label it a "deviation" in code, doc comments, or the plan. You're implementing the requirement, not departing from a rule. (Fold-vs-stack detail lives in `Swyfft.Services/Common/Homeowner/CLAUDE.md`.)
2. **Tag every touched config with its ticket** (always required, independent of fold vs stack, and independent of product line). Add the one-line `///` ticket breadcrumb per the canonical convention — `Swyfft.Services/Common/CLAUDE.md` § "Tag Each Config Version With Its Ticket". This covers **every config the change touches, not just new ones** — a re-pointed lookup or an in-place edit to a not-yet-live V1 is a gated change too, so annotate those and fix any stale "Based on Vn" pointer the change invalidates.
   - **Editing an existing config:** add (don't replace) your ticket line to its comment.
   - **Creating a new config:** put your ticket line in the new config's comment.

**MANDATORY, NON-NEGOTIABLE — the ticket-note convention is a physical plan artifact.** Any plan that adds, edits, re-points, or otherwise touches ANY `IStateConfig` implementer MUST (a) list every config it touches with the exact `///` ticket note each will carry, and (b) reproduce the "Tag Each Config Version With Its Ticket" convention (canonical in `Swyfft.Services/Common/CLAUDE.md`) VERBATIM at the top of the plan file. This has been missed before; it must never be missed again. A plan touching a config without this block physically inserted is incomplete — HARD STOP.

The convention text and examples are canonical in `Swyfft.Services/Common/CLAUDE.md` § "Tag Each Config Version With Its Ticket" — read it every time; don't work from memory. Treat a missing ticket note the same as a missing seeder override or a missing test — the plan is not done without it.

## Mandatory sections that live in repo docs — copied VERBATIM into the plan

When a mandatory convention lives in a repo doc (a `CLAUDE.md`, etc.), do NOT duplicate its text into this rules file — the repo doc is the single source of truth. Instead, every plan that triggers the convention MUST copy the convention's text VERBATIM into the plan file itself, physically inserted at the top (the same way the Excel-rater HARD RULE is inserted). This rule names the trigger and points to the source; the plan carries the actual text. Applies to every mandatory section that lives in a repo doc.

## Keep a Progress record in the plan (MANDATORY)

Every plan carries a **Progress** section recording, as execution proceeds, which steps are complete and what actually happened — outcomes and any deviation from the plan (a reused version, a scope change, a discovered constraint). Update it at each step boundary, not at the end. A plan with executed steps but a stale Progress record is out of date — fix it before continuing. This is what lets a post-compact or fresh reader know the real state without re-deriving it.

Every Progress entry carries a **timestamp in the user's local time, 12-hour format** (e.g.
`2026-08-12 2:47 PM`). A bare date is not enough — most tickets complete within a single day, so
the date alone cannot order the entries or show where time went.

**Every entry goes through the `eli--generate-progress-entry` skill. Never hand-write a row, and
never type a timestamp.** Your context carries the date but never the clock, so a time that merely
looks right is invented. The skill's script reads the clock, or reads the timestamp off the artifact
the entry describes, and appends the row itself — it exposes no time parameter, so there is nothing
to fill in. The plan supplies only the `## Progress` heading; the script owns the table under it.

A timestamp is the easiest field in a plan to fabricate: it reads as metadata rather than as a claim,
it fails no build and no test, and nobody re-reads it. The specific failure is continuing the
sequence — once one row is real, the next feels like arithmetic instead of a fact.

## Verification Section Structure

Verification steps must be derived from the change, not a generic checklist. The Verification section is one cohesive block at the end of the plan — don't split it into "Test plan" + "Verification" (creates duplication and dangling sections). Order so the implementer-facing flow comes first, with the rest as labeled reference material.

**The planner MUST drive verification via Q&A, item by item.** Walk through every AC in the ticket and ask "how do we verify this specifically? what command/test/file-check proves AC #N passes?" Then walk through the canonical generic-verification checklist (in `/eli--create-plan-from-ticket` skill) and ask "does X apply here?" for each. Nothing is auto-included; nothing is assumed.

### Execution sequence (before pushing)
Numbered steps in order, derived from the AC walk-through and canonical-checklist answers. Each `Run-DotnetTest.ps1` line should cross-reference the test artifact it's exercising (defined in the sections below).

### Tests to add or modify
List each new/extended test file with: filename, base class, and a case table (input → expected). One row per scenario. See `~/.claude/rules/testing.md` for TDD workflow and test-writing patterns.

Tests that iterate over multiple inputs (configs, indices, sheets, theory rows) must aggregate failures into a list and throw `AggregateException` at the end — never stop at the first failure. See `testing.md` § "Failure Aggregation".

**Distribute tests per the pyramid — unit tests carry the load.** When planning a feature's tests,
exhaustive assertion of business logic (every element value, age, config version, quote purpose,
and their combinations) belongs in unit tests. Integration and acceptance tests are smoke tests:
one happy path each, proving the wired-up end-to-end behavior, never re-asserting the combos the
unit tests already cover. Pick the lowest test class that proves each behavior — the class table
and the pyramid rule live in the repo's `.claude/rules/dotnet-testing.md` § "Cover new features
across the testing pyramid". Occasionally the lowest class that proves a behavior is an
integration test (the behavior only exists wired up — real DB, real pipeline); that's legitimate,
just uncommon — default to unit tests. A verification section that proposes combo coverage in an
integration or acceptance test is mis-planned — push the combos down to units.

### Captured asserts to regenerate
List the expected diffs by file, including which files should have **zero** diff (these are the negative-confirmation guards). The actual `/eli--prebind-validation` invocation lives in the execution sequence — this section just describes what the diffs should look like. See `~/.claude/rules/captured-asserts.md`.

Locally, running the captured asserts auto-updates the expected files — the workflow is run → review the diff. CI runners don't set the flag, so unupdated baselines fail there (the guard). This is fixed — don't research the mechanism; see `~/.claude/rules/captured-asserts.md`.

When a plan changes quote-def go-live dates, adds/recomputes seeder overrides, or inserts new `QuoteDefinitions.txt` rows, see `~/.claude/rules/quote-def-dates-and-ordering.md` — which dates live where (prod file vs seeded override; seeded vs in-memory asserts), the file's global `NewQuotesOn` ordering, and every test that enforces each. Don't re-derive these per ticket.

### Existing tests as regression checks
Tests that should still pass without edits — list with a one-line "why this is relevant to this change". Never list a test suite without a reason.

### Code-complete self-audit (comments + ClosedSets) — REQUIRED in EVERY plan
A written step in the execution sequence, before the code-complete HARD STOP, to re-read `~/.claude/rules/comments-docs-and-external-writing.md` and `Swyfft.Common/SetDefinitions/CLAUDE.md` and audit every comment and ClosedSet usage the diff adds or changes. This audit is already mandatory at execution time (Part C §§ "Comments", "ClosedSets") — it MUST ALSO appear as an explicit written step here so it is never invisible in the plan. Non-optional: a plan missing this step is incomplete, exactly like a missing test or seeder override.

### AC coverage map
Table mapping every AC from the ticket → which subsection covers it. Surfaces gaps and proves AC #N didn't get forgotten.

### Transition out of verification

Verification ends when (a) all agreed-upon tests pass and (b) the user explicitly agrees we're "done". The post-test-approval sequence (commit + push → adversarial review → PR draft → PR creation) is **not part of verification** and is governed by Part C § "Post-Test-Approval Sequence".

## `/eli--prebind-validation` is the default for most plans

The skill began as captured-assert-only but its scope has grown to be "the standard suite of tests Eli wants run on most PRs." Treat it as default verification for the majority of tickets, not just ones touching pre-bind / element generators. Any plan that affects elements, state configs, generators, or rating-adjacent code should include `/eli--prebind-validation` in the execution sequence.

**This default is Homeowner/residential.** `/eli--prebind-validation` is the residential suite
(`PreBindResidentialValidationTests`). For Commercial (or other non-HO) work it is the wrong
surface — use the commercial validation instead. See `testing-execution.md` § "Validation surface
is per product line — don't default to the HO suite".

### Never list a test a verification skill already runs

Before naming any individual test (or adding a standalone `Run-DotnetTest.ps1` line) in the verification, confirm it isn't already covered by a test-running skill already in the plan. **List the skill's tests — don't guess from memory.** `/eli--prebind-validation` runs everything tagged `TestGroup=PreBindResidentialValidationTests` across `Swyfft.Services.UnitTests`, `Swyfft.Services.IntegrationTests`, and `Swyfft.Seeding.IntegrationTests` — which already includes `EnsureConfigOrderWithDatabase` and `QuoteDefinitionsUnitTests`, among others. Listing those separately is duplication and overstates the verification.

Check coverage with the list mode (no execution, no regeneration):
- `pwsh ~/.claude/skills/eli--prebind-validation/Run-PreBindValidation.ps1 -TicketFolder <SW-XXXXX-title> -ListTests` — the full PreBind set.
- `pwsh ~/.claude/scripts/Run-DotnetTest.ps1 -TicketFolder <SW-XXXXX-title> -Project <P> -ListTests [-ListLevel full|classes|methods|tests|traits] [-FilterTrait <t>]` — any project/trait.

A test belongs in the plan as a *separate* line only when it's outside every skill the plan already runs (e.g. the ByPeril Excel validation tests in `Swyfft.Services.Excel.IntegrationTests`, which `/eli--prebind-validation` does not cover).

---

# Part C — How to EXECUTE the plan

## ALWAYS FOLLOW THE PLAN

Execute steps in order. Never skip ahead, reorder, or deviate. If a step depends on a previous step, that's a hard stop — don't proceed until the dependency is satisfied. If you encounter anything that prevents you from adhering to the plan, **HARD STOP** — explain the blocker and wait for instructions. Deviation and disobedience are not allowed.

## Reacting to Surprises

**HARD STOP** — If a build fails, a test fails unexpectedly, or anything doesn't match the plan — stop and explain before pivoting. (This is Gate 1.5, applied to plan execution.)

## Build Once, Run Tests in Parallel

When a verification step runs multiple test suites, **build the solution ONCE** with `pwsh ~/.claude/scripts/Build-Solution.ps1` — **backgrounded** (`run_in_background: true`, no `| tail`) — then invoke each test runner in parallel with its `-NoBuild` flag (single message, multiple Bash tool calls). The build is a long-running step just like the suites: a foreground build blocks the whole turn and forces the user to background it manually, so background it, wait for the completion notification, and only then launch the suites.

**Parallel verification test runs MUST be backgrounded — no exceptions.** Every test invocation in the parallel block MUST be launched with `run_in_background: true` and with **no** `| tail` pipe (tail buffers all output until the process exits, hiding progress — see `windows-tooling.md`). Running them in the foreground during verification is forbidden: a foreground run blocks the whole turn, so the user cannot communicate with you or interrupt while a long suite runs, and it forces the user to manually background each one. Launch each suite as its own background task and collect results from the completion notifications.

**This applies to every test invocation in the parallel block** — `Run-DotnetTest.ps1`, test-running skills like `/eli--prebind-validation`, or any wrapper script. **Before adding any invocation to a parallel block, verify its build behavior** — `Read` its SKILL.md / script `param(...)` block. If it builds by default, pass `-NoBuild` (or equivalent skip-build flag).

Don't:
- Let any invocation build implicitly when others are also running — multiplies build time AND causes build contention (parallel builds fight over output files/locks).
- Assume a skill/script doesn't build because its description doesn't mention building. Verify by reading the source.
- Run independent test suites sequentially.

See `~/.claude/rules/testing-execution.md` § "Test Output — Run-DotnetTest.ps1" for `-NoBuild` parameter details.

## Post-Test-Approval Sequence

Picks up where verification ends (tests pass + user agrees we're "done"). The sequence is fixed.
**Do NOT use the project `/create-pr` command — it autonomously fixes Critical/Major review findings,
which violates step 4's discuss-first rule. Create the PR by hand, following these steps.**

1. Ask once for approval to commit and push (single action — no separate ask for each).
2. Commit (`SW-XXXXX: <summary>` per `git-safety.md` / project CLAUDE.md) and push (verify tracking via `git branch -vv` first).
3. Run `/review-pr` against the pushed state.
4. **Discuss `/review-pr` findings with the user.** Don't autonomously start fixing. `/review-pr` is the first reviewer of completed work, not a safety net — plan for it to find nothing.
5. If findings warrant action: push ONE additional commit. **Do not run a second `/review-pr` after that commit.** One adversarial review per branch, full stop.
6. **MANDATORY: `Read` `~/.claude/rules/pr-creation.md` before drafting the PR description.** No exceptions. No "I just read it." No "I remember the rules." Then draft the PR description following those rules, present it to the user, and iterate until they explicitly approve the text. **HARD STOP — do not proceed until the description is signed off.**
7. **HARD STOP** — wait for approval, then create the PR by hand (`gh pr create --body-file` per `pr-creation.md`). Never route through `/create-pr`.
8. **After the PR is created, move the YouTrack ticket Stage to Review** (if currently Backlog, Ready for Dev, or Develop; leave it if already Review or later). The work isn't done until the ticket reflects the PR.

## Captured Asserts: Read Every Changed File

When a captured-assert regen produces diffs, you MUST individually open and assess every changed file before committing or moving on. No sampling. No "I checked 3 of 28 and the rest looked similar." The captured-assert system exists precisely because each file encodes information your mental model can't reliably predict — sampling defeats its purpose and reintroduces exactly the bugs the system was built to surface.

If a regen touches 30+ files, that's 30+ individual reads. There is no shortcut. Skipping this step is a Gate 3 violation by another name (extrapolating from partial data).

This is the inverse of `pr-creation.md` § "Skip generated files by default." There the baselines are
noise around the change; here the regenerated baselines are the change under review.

## Line Length

C# code lines must stay at or below **120 characters** including leading indent. This is a hard rule — wrap longer lines at natural punctuation: after commas, before operators, between method-chain links, or after the opening paren of a method call. Applies to `.cs` files only (production code AND tests). Markdown, `.txt` data files, JSON, YAML, etc. are exempt — prose and config wrap differently than code. No exceptions for "readability" within `.cs` — if the line is over, it gets wrapped.

When a wrapped construct has multiple peer items (e.g., theory data rows, parameter lists, collection initializers), pick ONE wrapping pattern and apply it to ALL peers — don't mix single-line and multi-line entries in the same group. Inconsistent wrapping is the worst of both worlds and will be flagged.

This applies only to lines newly written or modified by the current change. Pre-existing long lines that aren't being touched stay as-is — don't hijack the diff to reformat unrelated code.

**Verification**: `~/.claude/scripts/Test-LineLength.ps1 -Mode local` (or `-Mode branch`) scans the unified diff for added/modified `.cs` lines and exits non-zero if any exceed 120 chars. `~/.claude/scripts/Build-Solution.ps1` runs this as a pre-build gate (and aborts the build on failure), so a plan that already builds does NOT need a separate line-length verification step — call it out standalone only when the plan doesn't build (e.g. markdown-only changes) or as a pre-build self-check. The script is a backstop, not a substitute for writing it correctly the first time — self-check while editing rather than relying on the post-hoc gate.

## Magic Numbers / Strings

Hardcoded numeric / string literals must be extracted to named constants. Even sentinels like `int.MaxValue` used to mean "no limit" get a named alias — the name encodes intent the value alone doesn't. Applies to plan code excerpts AND executed code.

Bad: `RenderSheet(ws, int.MaxValue, 64, lines.Add);`

Good:
```csharp
const int allRows = int.MaxValue;
const int maxColumnsToCapture = 64;
RenderSheet(ws, allRows, maxColumnsToCapture, lines.Add);
```

## Comments

When implementing non-trivial business logic, add an intent/business-reason comment per
`~/.claude/rules/comments-docs-and-external-writing.md` § "How to write one" — explain in plain language what the code
is *trying to achieve* for the person who wrote the requirement, not what it mechanically does. This
is a default habit, not an afterthought.

### Mandatory comment self-audit at code-complete

Before the code-complete HARD STOP, re-read `~/.claude/rules/comments-docs-and-external-writing.md`
(don't work from memory) and audit every comment the diff adds or changes. This is real work. It is
not a checklist to skim and declare passed, and reporting the audit as done without having deleted
anything is the most common way it gets faked.

**Walk every added or changed comment one at a time and record a verdict for each: keep, trim, or
delete.** No sampling, no "the rest are fine". A comment with no recorded verdict has not been
audited.

**Question 1 is always "should this comment exist at all?", and the default answer is no.** Ask it
before judging the wording, because a well-worded comment that shouldn't exist still gets deleted.
Delete on sight:
- Anything restating what the adjacent code already says.
- Anything a nearby assertion message, `because` string, test name, or method name already says.
- Any second or third statement of one fact inside the same file. Repetition across separate code
  sites is correct (§ "Sibling-as-substitute" in the writing rules); repetition stacked inside one
  file, class, or method is slop.

**Only then judge the survivors** against the writing rules: business reason rather than mechanism,
no plan-scoped framing, no intra-PR commit references, no jargon or notation, and one or two plain
sentences. A comment running past two sentences is over budget and gets cut down, not excused.

**Verify a comment's claims the way you would verify prose.** A comment asserting "never", "always",
"only", or "every" is a factual claim: confirm it against the code or delete the quantifier. A
confident false comment is worse than no comment.

**Never argue a duplicate into staying.** Reaching for a rule to justify keeping a comment is the
tell that it should go. Deleting is always available and never introduces an error.

Fix every violation *before* announcing code-complete. This audit is part of reaching code-complete,
never a step the user has to request, and it applies to every code change, not only plan-driven
work. The diff should already be clean before Eli opens it.

**A comment-only change never justifies a build or a test run.** Comments, XML docs, and
encoding fixes cannot change behavior, so re-running tests to "confirm" them proves nothing.
After a comment-audit pass, check whether the diff since the last green run contains a single
executable change. If it does not, the prior run still stands — say so and move on. If it does,
run only the suites that executable change can affect.

## ClosedSets

ClosedSets are pervasive in this codebase and carry strict usage rules — parameter typing,
comparisons, `.Value`, `.ToString()`, `.Switch()`, implicit string conversion, and
ModelBinder/JsonConverter at boundaries — all defined in `Swyfft.Common/SetDefinitions/CLAUDE.md`.
Reviewers (human and bot) reject PRs for violating them.

**Mandatory read before writing ClosedSet code.** Before you write or modify any C# that touches a
ClosedSet — typing a parameter, comparing values, calling `.Value`/`.ToString()`/`.Switch()`, or
crossing a UI/API boundary — read `Swyfft.Common/SetDefinitions/CLAUDE.md` in full. Don't work from
memory: having read it earlier in the session — even having *edited* it — does NOT keep its rules
active while you later write unrelated code.

**Mandatory ClosedSet self-audit at code-complete.** Before the code-complete HARD
STOP, re-read `Swyfft.Common/SetDefinitions/CLAUDE.md` (don't work from memory) and audit every
ClosedSet usage the diff adds or changes against it. Confirm in particular: new method parameters
are typed as the ClosedSet, not `string`/`int`; `.Value` appears only at true system boundaries
(external APIs, IMS, raw storage), never in internal calls that already accept the ClosedSet;
comparisons and `.Switch()` follow the documented forms. Fix every violation before announcing
code-complete. This audit is part of reaching code-complete — not a step the user should ever have to request.

