---
paths:
  - "**/.claude/tickets/**/plan.md"
---
# Plan Mode

## Read repo files with the `Read` tool, code files above all

Read every repo file with the `Read` tool, code files first, while planning and executing. A `Read` or `Edit` loads that subtree's `AGENTS.md` and the matching path-scoped `.claude/rules/*.md`; a Bash read (`cat`, `sed`, `head`) loads nothing.

Part A covers planning with Eli, Part B what every plan file contains (`/eli--create-plan-from-ticket` enforces it), Part C executing the plan.

## FULL-COVERAGE MANDATE

Every plan reflects every rule in this file, not only the sections Part B lists: Part A's co-design, every Part B section (or `N/A — <reason>` for conditional ones), and every Part C rule that produces a step (the plan type's HARD STOP sequence, the code-complete audit, the PR-description audit, build-once-then-parallel test runs, reading every changed captured-assert file, the post-test-approval sequence). A plan that drops a rule is incomplete. `/eli--plan-audit` enforces this on every plan, skill-made or hand-written.

---

# Part A: How to PLAN

## Discuss Before Drafting

Plans are co-designed, never dumped as the first response. This is the most important rule in this file.

1. Present the numbered AC in a message of its own, extracted per `youtrack.md` § "The AC is whatever the ticket requires, wherever it says it" and § "Technical notes in a ticket are not the AC", each criterion naming its ticket source (description, comment N, attachment). End with `Plan against these? (y/n)`: a go-ahead, never a request for Eli to build or rework the list. Raise only a conflict the ticket can't settle, with its evidence. Later questions and the AC coverage map use these numbers.
2. Ask architectural questions one per message, foundational first, waiting for each answer.
3. Summarize decisions back briefly.
4. Draft the plan file only once the design is settled: concise outline first, full prose second.

If Eli pushes back on an in-flight plan, stop and discuss instead of silently re-drafting.

## No Deferred Decisions

A plan resolves every open question before execution. "TBD", "decide when we get there", "figure out later", "we'll see what makes sense" and "leave as an exercise" mark a punted decision: go back to Q&A. When a decision truly depends on something found during execution, either resolve the dependency now or add a HARD STOP at the discovery point naming the deferred decision.

## The smallest change that meets the AC (MANDATORY)

The plan implements the smallest change that meets the AC. A repo convention, a doc's taxonomy or another ticket's precedent never justifies more. When the ticket names the mechanism ("shall be soft declined; override: Override Fire Risk"), that mechanism is the design.

Every option in an architecture question states its size: files changed, classes and registrations added. The smallest option that meets the AC goes first and is the recommendation. A bigger one is recommended only when the smallest fails the AC, and the recommendation names how.

## Every question uses the mandated format (MANDATORY)

Every question while planning or executing takes the Question format in `talking-to-eli.md` § "Be concise — this is the top rule". A bare "y", "n" or number must answer it completely. Banned: open-ended asks ("Anything else?", "Good as-is, or want revisions?"), two questions in one message, and a choice described in prose with no question attached. Check each question against this section before sending it. When a reply fits none of the offered answers, re-ask in the mandated format; never infer.

## Other planner discipline

- Don't call ExitPlanMode while still discussing.
- Never guess a script flag or console-task parameter. Before writing one into a plan, read its definition (a script's `param(...)` block, e.g. `~/.claude/scripts/Build-Solution.ps1`, `Run-Seed.ps1`, `~/.claude/scripts/Run-DotnetTest.ps1`), never a sibling's. When explaining where a stale arg came from, research before answering.
- Run DB queries and log searches during planning, not after.
- `talking-to-eli.md` § "Don't Offer Anti-Pattern Options" and § "Stop being pedantic" govern every planning question.
- Settle ownership during Q&A. A ticket assigned to Eli is usually pre-bind, but not always. When the work is post-bind or straddles the line, doing it or handing it off is Eli's call (`~/.claude/rules/code-ownership.md`).

---

# Part B: REQUIRED CONTENT in every plan file

`/eli--create-plan-from-ticket` enforces this structure. Hand-written plans match it.

## Ticket folder, plan, & artifacts

Each ticket's work lives in `~/.claude/tickets/{ticket-ids}-{title-slug}/` (single: `SW-52867-<title>`; multiple: all IDs ascending plus a combined title, e.g. `SW-51860-SW-52867-<title>`; no primary ticket):

- **`plan.md`**: opens with a header listing every `SW-XXXXX` with its YouTrack link, and the title(s). Tracked in git.
- **`artifacts/`**: every dump the work produces. Bulky dumps are gitignored. `artifacts/db-queries/` (query SQL and results) and `artifacts/pr/` (PR body files) are tracked in git.

Nothing goes loose or in sibling folders. The dump scripts (`read-ticket`, `Run-DotnetTest`, `Run-Seed`, `Search-SolarWinds`, etc.) take the ticket folder name and write into its `artifacts/`.

## Plan File Preamble

Every plan file begins with this block after the title and type:

> **Execute steps in order. Never skip ahead, reorder, or deviate. If you encounter anything that prevents adherence to this plan, HARD STOP — explain the blocker and wait for instructions.**

## Acceptance criteria (MANDATORY)

Directly under the preamble: the numbered AC list confirmed in Q&A, each with its ticket source. The AC coverage map maps onto these numbers and nothing else.

## IMPORTANT: Step 0a: Confirm the ticket(s) are in Develop

First, before the pre-reads and the branch, for every ticket the plan covers, read its Stage:

- Earlier than Develop (Backlog, Ready for Dev): move it to Develop and tell Eli. No Gate 2 approval needed, same as the post-PR move to Review (`youtrack.md`).
- Develop or later: leave it. Never move a ticket backward.
- YouTrack unreachable: HARD STOP and ask.

## Subsystem Pre-Reads: Required Before Step 0b

Above Step 0b, list as required pre-reads the governing `CLAUDE.md` of every subsystem the plan touches, matched by topic, not path (`Data/{State}/Homeowner/ByPeril/**/*.xlsm` is governed by `Swyfft.Seeding/ExcelLoaders/CLAUDE.md`, not `Data/CLAUDE.md`). The root `CLAUDE.md` "Namespace-Specific Documentation" table is the index. Format:

> **Pre-read (subsystem orientation):**
> - `Swyfft.Seeding/ExcelLoaders/CLAUDE.md`
> - `Swyfft.Services.Excel.IntegrationTests/CLAUDE.md`

The pre-reads also list every rules file and skill the work depends on, so the plan serves as the resume file in `compaction.md`. A plan that adds or changes a test also lists `Swyfft.TestUtilities/AGENTS.md`, `Swyfft.TestUtilities/ConstantsAndExpects/AGENTS.md`, the target test project's `AGENTS.md` and `.claude/rules/dotnet-testing.md`, and names the test's base class and what it supplies.

## Creating a test's subject: two MANDATORY reads before the arrange

Each kind of test subject (quote, policy, claim) has one sanctioned creation path, never recalled from memory. Before writing any arrange, and again before executing that step, read:

1. The test-setup docs in full: `Swyfft.TestUtilities/CLAUDE.md` (test types, base classes, § "Homeowner Quote Setup"), `Swyfft.TestUtilities/ConstantsAndExpects/CLAUDE.md` (test addresses), the target test project's `CLAUDE.md` (its test-data section names the creation helper), and `.claude/rules/dotnet-testing.md`. Listing them as pre-reads doesn't count.
2. Existing tests for the same subject, matched on product line, carrier and config family. Copy an arrange from those, never from a test of a different subject.

The plan carries the exact creation call and the doc sentence that prescribes it. Without both, HARD STOP.

## IMPORTANT: Step 0b: Create a Branch

Every plan, before any step that writes code: if the current branch is `development`, `beta`, `master` or another ticket's branch, create one with `/create-branch` and push it.

## Plan Types

Every plan declares its type, which sets its workflow and HARD STOPs. Stop at those boundaries, not between file edits within a phase.

**Closing stops.** Every type ends with these:

1. **HARD STOP: code complete.** Don't print the diff; Eli reviews it in GitHub Desktop. Wait for approval before running tests.
2. **HARD STOP: tests complete.** Report results and wait for approval.
3. **HARD STOP: before irreversible actions** (push, PR, seeding, external posts). Wait for approval.

### Picking the type: the YouTrack IssueType is not the classifier

Ask whether the code does what it was written to do. If yes and someone wants it to do something else, it's a Feature, even when YouTrack says Bug: a missed requirement or a disliked behavior is not a defect, and `IssueType: Bug`, a Current/Expected Result template, Found-in-Stage Beta or a QA reporter don't show a malfunction. If it diverges from its own intent, it's a Bug Fix.

### Bug Fix

Diagnose first. No plan is written for the investigation.

1. Investigate with whatever settles which mechanism fired: code reading, a log search, SQL, a diagnostic harness, a throwaway test, or a test that becomes the regression guard.
2. **HARD STOP:** report the mechanism, its evidence, and a disposition: fix, spin off, not a defect, or already fixed. The last two end the work with no fix plan.
3. Write a minimal fix plan: what changes, the guarding test, how it's verified. Part B applies in full; untouched sections are marked `N/A` with the reason, never omitted.
4. **HARD STOP:** fix plan approved.
5. Write the fix, then the closing stops.

#### What the diagnosis must establish

- **The defect:** the line or branch where behavior diverges from intent. Short of that, say so and name what would settle it.
- **Evidence per claim**, hypothesis and proven labeled separately.
- **The proving test's fate**, if one was written: kept as the guard, or discarded.
- **Noticed, not diagnosed:** one line per finding outside the defect. Never investigate one to decide whether it belongs, and never bolt one onto another finding as a caveat.

Scope is the reported mechanism plus whatever is part of the same defect; an incomplete report doesn't narrow it. Someone else's diagnosis is a starting point: verify each claim against the code.

#### Code tracing is only evidence when a stack trace anchors it

Code tracing is evidence only along an explicit stack trace's frames, or for a trivial cause. Otherwise the next action is empirical (a log search, SQL query or test), not another read; upfront research on a non-obvious bug takes that form. Never pair a discovery with a claim that the next step will prove it. Say what the evidence would rule out.

### Refactoring

1. Write a safety-net test covering the behavior being refactored.
2. **HARD STOP:** TDD checkpoint. The test passes; wait for approval.
3. Refactor, then the closing stops.

### Feature

1. Make the code changes, then the closing stops.

### Excel Rater (ByPeril)

For rater-update tickets: actuarial delivers a new rater `.xlsm`, on any sheet, and the C# is brought into agreement with it. Usually a YouTrack Feature.

The entire plan is provisional until the diff has run. The requirement is the diff between the delivered rater and the captured baselines, which doesn't exist until the raters are placed and the validation tests regenerate the baselines. The ticket, the `version_history` sheet and the on-disk rater don't substitute for it. The plan has two parts:

- **Part 1, written now:** branch, place the raters, regenerate the baselines, scoping checkpoint, versioning check. No code, seeder included.
- **Part 2, written at the checkpoint from the diff:** every sheet's verdict, the C# change list, configs, version lookups, quote defs, tests, Verification. Implementation starts here, seeder first (`excel-rater-plans-common.md` § "Implement the seeder first"). Part B is satisfied here, not before.

The Gates and Parts A and C apply throughout. Before the diff:

- No architecture Q&A. `/eli--create-plan-from-ticket` Step 5 doesn't run.
- No reading ahead into the C# to check the ticket's technical notes.
- No provisional C# change list. Don't transcribe the technical notes as steps.
- Reaching the outline in a couple of exchanges is correct.

It follows the Feature sequence, with the scoping checkpoint and the versioning check as added HARD STOPs before any C#. Reading the matching playbook in full is MANDATORY: `~/.claude/rules/ho-excel-rater-plans.md` (Homeowner) or `~/.claude/rules/co-excel-rater-plans.md` (Commercial), plus `~/.claude/rules/excel-rater-plans-common.md`.

**Every Excel Rater (ByPeril) plan carries a "Rater defect found during execution" section. MANDATORY**, whether or not a defect is suspected; `/eli--plan-audit` fails a plan without it. When a defect small enough to fix ourselves surfaces, HARD STOP and prepare the edit to the standard in `excel-rater-plans-common.md` § "Rater edits — when warranted, and the SharePoint flow" before anything downstream runs. The section also carries the channel message, per `excel-rater-plans-common.md` § "What a message to the channel is for".

### Excel Rater bug

A defect in a rater already on disk, or in C#-vs-rater parity, with no new rater delivered. It follows the Bug Fix sequence and inherits the rater playbooks in full: reading `~/.claude/rules/excel-rater-plans-common.md` plus `ho-excel-rater-plans.md` or `co-excel-rater-plans.md` is MANDATORY (HARD RULE header, pre-reads, seeder-first, versioning, verification surface, rater-edit flow). Only the two-part authoring drops: with no delivery there is no baseline diff, so the plan is written whole and has no scoping checkpoint.

When the fix is the rater, `excel-rater-plans-common.md` § "Rater edits — when warranted, and the SharePoint flow" governs the fix step, and the plan carries the prepared edit before it counts as written. `Read` that section when writing the step and again when executing it.

**The product's parity suite is the guard. Never write a unit test for a rater-parity defect.**

### Audit-Doc LogMonitor (catch-all)

For LogMonitor tickets on audit-doc generation failures (`GenerateAuditDocs - GenerateAuditDoc` signatures, HO or Commercial). The ticket matches an error signature, so it covers every quote currently failing, often with several root causes. A failing quote re-fires every audit run until a fix lands.

- **Beta mismatches on unlaunched configs are often expected.** An unlaunched config (no prod book, e.g. still V1) takes premium-bearing changes in place, so a beta quote bought before such a change audits as DB(bind) ≠ Excel/Recompute(now). Check that timeline before calling it a defect.
- **A Commercial copy can be audited before its first recalculation.** `CopyActorCollection` saves the copy without recalculating (`CopyQuote`, `SaveQuote`, `UpdateQuoteDefinitionByQuoteIdOrFail`), and `CopyQuoteToActor.CopyTo` doesn't copy quote lines. If the copy is a policy's current quote, the audit can select it in that window and crash reading a required quote line (SW-53573: `LossRatio`, in `CommercialEAndSExcelRaterService.SetExcelValues`). In the quote id's logs: a `CommercialQuoteCopyService` result followed by the audit, with no `CommercialQuoteRecalculationService` result between them.
- **Every audit-doc failure got past the ByPeril Excel integration tests.** The work also answers why those tests missed it, and extends them to cover the scenario class where a rater-vs-C# comparison can. Post-bind data mutation, like the ghost reprice, can't be covered.

#### "The errors stopped" is not a diagnosis

`ExcelQuoteAuditServiceBase.GenerateAuditDoc` has four outcomes. Read them off the code before interpreting a gap in the logs:

| Outcome | `AuditDocsGeneratedOn` | Logs every run? | Live defect? |
|---|---|---|---|
| **Failure**: exception thrown | left NULL | yes, hourly, forever | yes |
| **MisMatch**: premium differs | **marked** | no, logs once, then never re-selected | **yes** |
| **Success**: premium matches | marked | no | no |
| **Skipped**: IMS record gone | marked | warns once | no |

Marking happens before the premium comparison, so a signature that stops firing means only that the crash stopped; the quote can leave the queue still mis-priced. Never write "the audit succeeded" or "this is fixed" from absent logs. A MisMatch logs its own error with the quote id, so a quote-id-scoped search across the full window separates MisMatch from Success-or-no-longer-selected; `AuditDocsGeneratedOn` plus the stored premium settles the rest. One quote can move through several outcomes as fixes ship. Logs give history only: to know whether a quote audits correctly now, run `/eli--byperil-audit-diagnostic`, which executes the audit's own `ComparePremium` against the live rater.

Plan shape:

1. **SolarWinds first:** search the ticket's own search-link terms from its filing date ("First seen") to now. The work list is whatever still fails, not the quotes the ticket was filed for.
2. **Group by distinct failure** (config, state, error shape) and diagnose each group with `/eli--byperil-audit-diagnostic`, interpreted per the `eli--audit-doc-mismatch-investigation` skill.
3. **Post an RCA per distinct failure**, including the description's quotes when they now pass. When and what fixed them is a bonus.
4. **Ask** whether to spin failures off (per failure or per QuoteDef: SW-48603 → SW-49434…SW-49439) or RCA them in place on the umbrella ticket (SW-51664's three RCAs).
5. Done when every current failure has an RCA and a disposition: fix shipped, spun off, or no action with reason.

A code fix follows the Bug Fix sequence. A rater fix takes the Excel Rater bug type for that group.

## Seeder Overrides: required for every new not-yet-live state config

A plan adding a `HomeownerStateConfig`, `FloodStateConfig`, `CommercialStateConfig` or `DbbStateConfig` with a future prod go-live carries a seeder override for each, with concrete `NewQuotesOn` and `RenewalOn` dates, never `(YYYY,M,D)` placeholders, computed per `quote-def-dates-and-ordering.md` § "Computing a new override's dates".

**MANDATORY:** a plan adding a `HomeownerStateConfig`, `FloodStateConfig` or `DbbStateConfig` runs `/eli--quote-def-override-audit` during planning, before computing the new dates; removing a predecessor's stale override changes the `RenewalOn` the new one must clear. Remove flagged overrides in the new overrides' product lines, or record why one stays. Leave other product lines alone. The audit doesn't cover Commercial (`quote-def-dates-and-ordering.md` § "Finding stale overrides").

## State-config changes: fold-vs-stack and version doc-comments (MANDATORY, every product line)

A plan making a version-gated change (a new version, a fold into a parked version, or an in-place edit to a not-yet-live V1) to any `IStateConfig` implementer covers both points below, or it is incomplete: HARD STOP.

1. **Prefer folding over stacking**, only when the ticket is silent. When the ticket or epic dictates fold or stack, follow it without justifying it or calling it a deviation. Detail: `Swyfft.Services/Common/Homeowner/CLAUDE.md`.
2. **Tag every touched config with its ticket**, new or not (a re-pointed lookup or an in-place V1 edit counts), with the one-line `///` breadcrumb per `Swyfft.Services/Common/CLAUDE.md` § "Tag Each Config Version With Its Ticket", and fix any stale "Based on Vn" pointer the change invalidates.
   - Editing a config: add your line; don't replace.
   - Creating a config: put your line in its comment.
   - A config's ticket lines name the stories that go live with its quote def. A shipped story's line stays even when a later story on the same quote def changes or reverts it; the later story adds its own line, and the "delete a false claim" rule in `comments-docs-and-external-writing.md` doesn't apply. A story that moved to another config before this quote def went live has its line moved to that config.

The plan (a) lists every touched config with its exact `///` note and (b) reproduces the "Tag Each Config Version With Its Ticket" convention verbatim at the top of the plan file, read fresh each time. Without both, HARD STOP.

## Versioned or unversioned: every plan says which

A change is unversioned when it lands on a live quote def with no new config version gating it (an element added or removed, a choice added or dropped, a range moved, a type changed). When the ticket says whether it's versioned, and gives go-live dates if so, the plan records that without relitigating. When the ticket is silent, the plan states which and why.

## Unversioned changes: the plan must test quotes created before the change (MANDATORY)

Every test helper builds from the current config, so no existing test exercises a pre-change quote. When the change can put an existing quote, or its policy, out of step with its config, the plan names the test and how it builds the pre-change quote; otherwise HARD STOP. Examples: the config no longer generates an element the quote holds, generates one it lacks, replaced the default element the quote's element is bound to, no longer offers the quote's value, or runs a risk rule that would decline it.

Only two skips:

- **An existing quote could be created identically today.** Decide from the config: could a quote built under the old config be built, unchanged, under the new one?
- **The carrier/state has never launched in prod.** A line with any live config never qualifies, even when the change lands only on a parked version.

Whether a change may be unversioned is a separate question; an unversioned change still must not break pre-change quotes and policies. Every plan says which holds: the test, a skip, or a trigger that never fired.

## Mandatory sections that live in repo docs: copied VERBATIM into the plan

When a triggered mandatory convention lives in a repo doc, the plan copies its text verbatim at the top of the plan file, as with the Excel-rater HARD RULE. This file names only the trigger and the source.

## Keep a Progress record in the plan (MANDATORY)

The plan's **Progress** section records, at each step boundary, what completed, the outcome, and any deviation (a reused version, a scope change, a discovered constraint). Bring a stale one current before continuing. Every entry is timestamped in local 12-hour time (e.g. `2026-08-12 2:47 PM`) and goes through the `eli--generate-progress-entry` skill, which reads the clock or the artifact's timestamp and appends the row. Never hand-write a row or type a timestamp. The plan supplies only the `## Progress` heading.

## A PR whose base isn't `development` gets its reviewers requested by hand (MANDATORY)

`.github/workflows/auto_request_review.yml` runs only on PRs based on `development`, so every PR above the bottom of a stack gets none of its reviewers. A plan creating such a PR adds a step right after `gh pr create` (and `gh stack link`, for a stack): `gh pr edit <PR> --add-reviewer <logins>`, naming logins derived while planning from `.github/auto_request_review.yml`:

- the `per_author` entry for `eli-swyfft`, each group expanded to its members, minus the author
- every group or login assigned by a `files` glob the PR's diff matches

The step is its own gated write, asked as one bare-yes question, and ends by confirming the requests with the `reviewRequests` GraphQL query.

## Verification Section Structure

Verification is derived from the change: one block at the end of the plan, never split into "Test plan" plus "Verification", implementer-facing flow first and reference material after.

The planner proposes the whole verification in one message: for every AC, the test, command or check that proves it, plus each applicable item from the generic checklist in `/eli--create-plan-from-ticket`, each saying what it proves. Nothing goes in by default. End with `Verify as proposed? (y/n)`. On any objection, re-present the whole revised proposal. Never walk the ACs or the checklist one item per message.

### Execution sequence (before pushing)

Numbered steps in order, from the AC walk-through and checklist answers. Each `Run-DotnetTest.ps1` line names the test artifact it exercises.

### Tests to add or modify

Each new or extended test file: filename, base class, and a case table (input → expected, one row per scenario). Tests follow `~/.claude/rules/testing.md`, conform to FIRST (`testing.md` § "FIRST principles govern every test"; a date-dependent test names its pinned clock date and uses literal dates), and aggregate failures across iterated inputs (`testing.md` § "Failure Aggregation").

Unit tests carry the load. Exhaustive business-logic combinations (element values, ages, config versions, quote purposes) go in unit tests. Integration and acceptance tests are one happy path each, never re-asserting those combinations. Pick the lowest test class that proves each behavior (the repo's `.claude/rules/dotnet-testing.md` § "Cover new features across the testing pyramid"); an integration test is right only when the behavior exists only wired up.

### Captured asserts to regenerate

List the expected diffs by file, including the files that must show zero diff. The `/eli--prebind-validation` run lives in the execution sequence (`~/.claude/rules/captured-asserts.md`). For go-live dates, seeder overrides or new `QuoteDefinitions.txt` rows, use `~/.claude/rules/quote-def-dates-and-ordering.md`; don't re-derive.

### Existing tests as regression checks

Tests that should pass unedited, each with a one-line reason it's relevant to this change.

### Code-complete audit (REQUIRED in EVERY plan)

A written step before the code-complete HARD STOP runs `/eli--code-complete-audit <ticket-folder>` (Part C § "Code-complete audit"). A plan without it is incomplete.

### PR-description audit (REQUIRED in EVERY plan)

A written step in the post-verification sequence runs `/eli--audit-pr-desc` on the drafted body file before the description is presented (Part C § "Post-Test-Approval Sequence" step 6). A plan without it is incomplete.

### AC coverage map

A table mapping every AC to the subsection that covers it.

### UI acceptance criteria need a screenshot

When an AC is about what an agent sees (a new or moved element, changed wording, a layout change), the plan opens the running site, confirms it, and screenshots it for the PR description; a captured assert doesn't prove the screen. A change to which rules fire, shown through the quote page's existing decline and premium display, gets no screenshot.

Create the subject with a throwaway integration test, not the site's create flow, that calls the product's quote generator with the config pinned and prints the quote id. Commercial: `CommercialQuoteGenerator.CreateCommercialQuote(addressKey, stateConfig)` via the `QuoteGenerator` property on `CommercialIntegrationTestBase`. Homeowner: `HomeownerQuoteTestBuilder` via `HoBuilder`. Both are in `Swyfft.TestUtilities/AGENTS.md`. Use the target carrier's own good address from `Swyfft.TestUtilities/ConstantsAndExpects/` (Vave FL: `CommercialGoodAddressKeyVaveFL000`); another carrier's address soft-declines. Confirm zero premium errors before opening. The throwaway test stays until Eli says to remove it.

Build with `~/.claude/scripts/Build-Solution.ps1`, then start the site with `pwsh ./RunSwyfftWeb.ps1` from the repo root, in the background (it runs `--no-build`). It's up when `https://localhost:5001` answers. A Commercial quote opens at `/commercial/<quoteId>/customize`. Stop the site before the next build; a running `Swyfft.Web` locks `Swyfft.Web\bin`.

## `/eli--prebind-validation` is the default for most plans

Include it in the execution sequence of any plan that affects elements, state configs, generators or rating-adjacent code. For Commercial rating work, the validation surface is in `testing-execution.md` § "Validation surface is per product line".

### Never list a test a verification skill already runs

Before naming a test or adding a standalone `Run-DotnetTest.ps1` line, list the plan's skills' tests with `-ListTests` (`testing-execution.md` § "Listing tests") and confirm none already runs it. `/eli--prebind-validation` runs everything tagged `TestGroup=PreBindResidentialValidationTests` across `Swyfft.Services.UnitTests`, `Swyfft.Services.IntegrationTests` and `Swyfft.Seeding.IntegrationTests`, including `EnsureConfigOrderWithDatabase` and `QuoteDefinitionsUnitTests`. A separate line is only for a test outside every skill in the plan, e.g. the ByPeril Excel validation tests in `Swyfft.Services.Excel.IntegrationTests`.

---

# Part C: How to EXECUTE the plan

## ALWAYS FOLLOW THE PLAN

Execute steps in order. Never skip ahead, reorder or deviate. A step waits on its dependencies. Anything that prevents adherence is a HARD STOP: explain the blocker and wait.

## Build Once, Run Tests in Parallel

When a verification step runs several suites, build once with `pwsh ~/.claude/scripts/Build-Solution.ps1`, wait for it to finish, then launch every suite in one message with `-NoBuild`. The build and every suite run in the background with no `| tail` (`core-behavior.md` § "Other", `windows-tooling.md`). Before adding a runner (`Run-DotnetTest.ps1`, `/eli--prebind-validation`, any wrapper) to the parallel block, read its `param(...)` block or SKILL.md, and pass its skip-build flag if it builds by default. Never run independent suites sequentially.

## Post-Test-Approval Sequence

Verification ends when the agreed tests pass and Eli explicitly says it's done. Then this fixed order runs. Never use the project `/create-pr` command; it auto-fixes review findings, against step 4.

1. Ask once for approval to commit and push.
2. Commit (`SW-XXXXX: <summary>`, per `git-safety.md`) and push, checking tracking with `git branch -vv` first.
3. Run `/review-pr` against the pushed state.
4. Discuss its findings with Eli. Never start fixing on your own.
5. If findings warrant action, push one more commit. Never run a second `/review-pr`.
6. Draft and audit the PR description:
   1. **MANDATORY: `Read` `~/.claude/rules/pr-creation.md`.** A dedupe notice that it's already in context is not permission to skip the rules; use the content that is there.
   2. Write the draft to a body file under the ticket's `artifacts/pr/`.
   3. Run `/eli--audit-pr-desc <body-file>`, every time.
   4. Present only the audited description. Eli never sees the pre-audit draft.
   5. Iterate until Eli explicitly approves the text. **HARD STOP** until he does.
7. **HARD STOP**, then create the PR by hand (`gh pr create --body-file` per `pr-creation.md`).
8. Move the YouTrack ticket to Review if its Stage is Backlog, Ready for Dev or Develop.

## Captured Asserts: Read Every Changed File

When a captured-assert regen produces diffs, open and assess every changed file individually before committing or moving on, however many there are. No sampling. Here the regenerated baselines are the change under review, the inverse of `pr-creation.md` § "Skip generated files by default."

## Code-complete audit

The last step before the code-complete HARD STOP is one `/eli--code-complete-audit <ticket-folder>` pass over the whole diff. It checks the diff against `coding-standards.md`, `comments-docs-and-external-writing.md`, `testing.md` and `refactoring.md` and fixes what it finds. Unplanned work gets the same pass at its own code-complete. Every plan points at `~/.claude/rules/coding-standards.md` § "Identifier names must be self-documenting", and every identifier in its code excerpts obeys it.
