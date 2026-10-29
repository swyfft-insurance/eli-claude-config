---
paths:
  - "**/.claude/tickets/**/plan.md"
---
# Plan Mode

## How this file is organized

Part A covers planning a ticket, Part B what every plan file contains, Part C executing the plan. Everything specific to one plan type is in its file in `~/.claude/plan-types/`.

# Part A: Planning a ticket

## Requirements come from the ticket

- **Requirements come only from the ticket or from questions asked directly of the product owners, never from Eli.** Eli never rules on the AC and never reads the plan file.

## Start, every type

1. **Read the ticket with `/eli--read-ticket` and move it to Develop (Step 0a).** If a hook blocks the move, stop and ask for that one action as a bare y/n.
2. **Pick the type by heading 1 of each file in `~/.claude/plan-types/`.** The more specific type wins. Confirm it with Eli.
3. **Read the subsystem docs, the type's file, and the ticket's existing plan if there is one.**

## Discovery: bugs, the LogMonitor types, the rater types

- **Before any plan exists, done the way the type's file says:** queries (prod-copy ones go to Eli), throwaway tests, log searches, or dropping in new raters and reading the diff. No plan file, no Q&A about method; `resume.md` carries it across compactions. A finding that ends the work ends it there.

## End, every type

4. **Settle the design from the ticket and what discovery found:**
   - **The smallest change that meets the AC.** A repo convention or another ticket's precedent never justifies more, and a mechanism the ticket names is the design.
   - **An open PR touching the same code never narrows scope or creates a dependency.** Build the full AC on its own base.
   - **Post-bind work, or work that straddles the line, is Eli's call to do or hand off.**
   - **A question goes to Eli only when the ticket's words support two readings that produce different code, or the ticket conflicts with the code or a rule.**
5. **One message to Eli:** what the ticket asks for, what discovery found, the outline, and the tests, one line each (the behavior in plain words; unit, integration or acceptance; the test class). Not grouped by AC; build, audits and review left out. It ends with a go-ahead.
6. **Write the plan from the outline Eli approved in step 5, run `/eli--plan-audit`, and ask "Execute now?"**

## Banned

- **A question the ticket, the rules, the code or a check answers.**
- **A concern nothing in hand supports, raised as a question, a query, a test or a design change.**
- **Changing an AC without evidence the ticket is wrong.**
- **Reopening Q&A because Eli asked a question.** Answer it.
- **A guard, branch or test case for a scenario outside the defect the ticket reports, such as a contrived combination of conditions or a case no production path reaches.** The code and tests cover the reported defect and its AC, and nothing more.

---

# Part B: REQUIRED CONTENT in every plan file

- **`/eli--plan-audit` checks every plan against this structure.**

## Ticket folder, plan, & artifacts

- **Each ticket's work lives in `~/.claude/tickets/{ticket-ids}-{title-slug}/`** (single: `SW-52867-<title>`; multiple: all IDs ascending plus a combined title, e.g. `SW-51860-SW-52867-<title>`; no primary ticket):

- **`plan.md`**: opens with a header listing every `SW-XXXXX` with its YouTrack link, and the title(s). Tracked in git.
- **`artifacts/`**: every dump the work produces. Bulky dumps are gitignored. `artifacts/db-queries/` (query SQL and results) and `artifacts/pr/` (PR body files) are tracked in git.

- **Nothing goes loose or in sibling folders.** The dump scripts (`read-ticket`, `Run-DotnetTest`, `Run-Seed`, `Search-SolarWinds`, etc.) take the ticket folder name and write into its `artifacts/`.

## Plan File Preamble

Every plan file begins with this block after the title and type:

> **Execute steps in order. Never skip ahead, reorder, or deviate. If you encounter anything that prevents adherence to this plan, HARD STOP — explain the blocker and wait for instructions.**

## Acceptance criteria (MANDATORY)

- **Directly under the preamble:** the numbered AC list from the ticket, each with its ticket source. The AC coverage map maps onto these numbers and nothing else.

## IMPORTANT: Step 0a: Confirm the ticket(s) are in Develop

First, before the pre-reads and the branch, for every ticket the plan covers, read its Stage:

- **Earlier than Develop (Backlog, Ready for Dev):** move it to Develop and tell Eli. No Gate 2 approval needed, same as the post-PR move to Review (`youtrack.md`).
- **Develop or later:** leave it. Never move a ticket backward.
- **YouTrack unreachable:** HARD STOP and ask.

## Subsystem Pre-Reads: Required Before Step 0b

- **Above Step 0b, list as required pre-reads the governing `CLAUDE.md` of every subsystem the plan touches, matched by topic, not path (`Data/{State}/Homeowner/ByPeril/**/*.xlsm` is governed by `Swyfft.Seeding/ExcelLoaders/CLAUDE.md`, not `Data/CLAUDE.md`).** The root `CLAUDE.md` "Namespace-Specific Documentation" table is the index. Format:

> **Pre-read (subsystem orientation):**
> - `Swyfft.Seeding/ExcelLoaders/CLAUDE.md`
> - `Swyfft.Services.Excel.IntegrationTests/CLAUDE.md`

- **The pre-reads also list the plan's type file and every rules file and skill the work depends on, so the plan serves as the resume file in `compaction.md`.** A plan that adds or changes a test also lists `Swyfft.TestUtilities/AGENTS.md`, `Swyfft.TestUtilities/ConstantsAndExpects/AGENTS.md`, the target test project's `AGENTS.md` and `.claude/rules/dotnet-testing.md`, and names the test's base class and what it supplies.

## Creating a test's subject: two MANDATORY reads before the arrange

- **Each kind of test subject (quote, policy, claim) has one sanctioned creation path, never recalled from memory.** Before writing any arrange, and again before executing that step, read:

1. **The test-setup docs in full:** `Swyfft.TestUtilities/CLAUDE.md` (test types, base classes, § "Homeowner Quote Setup"), `Swyfft.TestUtilities/ConstantsAndExpects/CLAUDE.md` (test addresses), the target test project's `CLAUDE.md` (its test-data section names the creation helper), and `.claude/rules/dotnet-testing.md`. Listing them as pre-reads doesn't count.
2. **Existing tests for the same subject, matched on product line, carrier and config family.** Copy an arrange from those, never from a test of a different subject.

- **The plan carries the exact creation call and the doc sentence that prescribes it.** Without both, HARD STOP. The HARD STOP is the failure path, not an option: find the call while planning, from the docs or an existing test of the same subject on `development`, and never defer it to a stop during execution.

## IMPORTANT: Step 0b: Create a Branch

- **Every plan, before any step that writes code:** if the current branch is `development`, `beta`, `master` or another ticket's branch, create one with `/create-branch` and push it.

## The type's steps and stops

- **Every plan declares its type, which sets its workflow and HARD STOPs.** Stop at those boundaries, not between file edits within a phase. The type's steps and stops come from its file in `~/.claude/plan-types/`.

### Closing stops

Every type ends with these:

1. **HARD STOP: code complete.** Tell Eli the diff is ready for his review in GitHub Desktop, without printing it, and ask him nothing else in that message. Wait for him to say his review is done. Only then ask to run the tests.
2. **HARD STOP: tests complete.** Report results and wait for approval.
3. **HARD STOP: before irreversible actions** (push, PR, seeding, external posts). Wait for approval.

## Seeder Overrides: required for every new not-yet-live state config

- **A plan adding a `HomeownerStateConfig`, `FloodStateConfig`, `CommercialStateConfig` or `DbbStateConfig` with a future prod go-live carries a seeder override for each, with concrete `NewQuotesOn` and `RenewalOn` dates, never `(YYYY,M,D)` placeholders, computed per `quote-def-dates-and-ordering.md` § "Computing a new override's dates".**

- **MANDATORY: a plan adding a `HomeownerStateConfig`, `FloodStateConfig` or `DbbStateConfig` runs `/eli--quote-def-override-audit` during planning, before computing the new dates;** removing a predecessor's stale override changes the `RenewalOn` the new one must clear. Remove flagged overrides in the new overrides' product lines, or record why one stays. Leave other product lines alone. The audit doesn't cover Commercial (`quote-def-dates-and-ordering.md` § "Finding stale overrides").

## State-config changes: fold-vs-stack and version doc-comments (MANDATORY, every product line)

- **A plan making a version-gated change (a new version, a fold into a parked version, or an in-place edit to a not-yet-live V1) to any `IStateConfig` implementer covers both points below, or it is incomplete:** HARD STOP.

1. **Prefer folding over stacking**, only when the ticket is silent. When the ticket or epic dictates fold or stack, follow it without justifying it or calling it a deviation. Detail: `Swyfft.Services/Common/Homeowner/CLAUDE.md`.
2. **Tag every touched config with its ticket**, new or not (a re-pointed lookup or an in-place V1 edit counts), with the one-line `///` breadcrumb per `Swyfft.Services/Common/CLAUDE.md` § "Tag Each Config Version With Its Ticket", and fix any stale "Based on Vn" pointer the change invalidates.
   - **Editing a config:** add your line; don't replace.
   - **Creating a config:** put your line in its comment.
   - **A config's ticket lines name the stories that go live with its quote def.** A shipped story's line stays even when a later story on the same quote def changes or reverts it; the later story adds its own line, and the "delete a false claim" rule in `comments-docs-and-external-writing.md` doesn't apply. A story that moved to another config before this quote def went live has its line moved to that config.

- **The plan (a) lists every touched config with its exact `///` note and (b) reproduces the "Tag Each Config Version With Its Ticket" convention verbatim at the top of the plan file, read fresh each time.** Without both, HARD STOP.

## Versioned or unversioned: every plan says which

- **A change is unversioned when it lands on a live quote def with no new config version gating it (an element added or removed, a choice added or dropped, a range moved, a type changed).** When the ticket says whether it's versioned, and gives go-live dates if so, the plan records that without relitigating. When the ticket is silent, the plan states which and why.

## Unversioned changes: the plan must test quotes created before the change (MANDATORY)

- **Every test helper builds from the current config, so no existing test exercises a pre-change quote.** When the change can put an existing quote, or its policy, out of step with its config, the plan names the test and how it builds the pre-change quote; otherwise HARD STOP. Examples: the config no longer generates an element the quote holds, generates one it lacks, replaced the default element the quote's element is bound to, no longer offers the quote's value, or runs a risk rule that would decline it.

Only two skips:

- **An existing quote could be created identically today.** Decide from the config: could a quote built under the old config be built, unchanged, under the new one?
- **The carrier/state has never launched in prod.** A line with any live config never qualifies, even when the change lands only on a parked version.

- **Whether a change may be unversioned is a separate question;** an unversioned change still must not break pre-change quotes and policies. Every plan says which holds: the test, a skip, or a trigger that never fired.

## Manual QA, when applicable

- **Manual QA applies to every change a tester can see:** anything that changes what a quote, policy, document, page or fee shows or does. The only exceptions are a refactor, a test-only change and a tooling change. A plan that claims one of those exceptions names it.

- **When manual QA applies, the plan says how manual QA will test the change, and the design makes the change testable on beta.** The plan's last step, after the PR, posts that as a YouTrack comment on the story.

- **A rater change is covered by the rater validation tests in `Swyfft.Services.Excel.IntegrationTests`, which run more scenarios than a tester could.** Its comment asks manual QA only for a smoke test that a quote gets a premium, and says the validation tests cover the rest.

## Mandatory sections that live in repo docs: copied VERBATIM into the plan

- **When a triggered mandatory convention lives in a repo doc, the plan copies its text verbatim at the top of the plan file, as with the Excel-rater HARD RULE.** This file names only the trigger and the source.

## Keep a Progress record in the plan (MANDATORY)

- **The plan's Progress section records, at each step boundary, what completed, the outcome, and any deviation (a reused version, a scope change, a discovered constraint).** Bring a stale one current before continuing. Every entry is timestamped in local 12-hour time (e.g. `2026-08-12 2:47 PM`) and goes through the `eli--generate-progress-entry` skill, which reads the clock or the artifact's timestamp and appends the row. Never hand-write a row or type a timestamp. The plan supplies only the `## Progress` heading.

## Verification Section Structure

- **Verification is derived from the change:** one block at the end of the plan, never split into "Test plan" plus "Verification", implementer-facing flow first and reference material after.

### Execution sequence (before pushing)

- **Numbered steps in order, from the AC and the checklist.** Each `Run-DotnetTest.ps1` line names the test artifact it exercises.

### Tests to add or modify

- **Each new or extended test file:** filename, base class, and a case table (input → expected, one row per scenario). Tests follow `~/.claude/rules/testing.md`, conform to FIRST (`testing.md` § "FIRST principles govern every test"; a date-dependent test names its pinned clock date and uses literal dates), and aggregate failures across iterated inputs (`testing.md` § "Failure Aggregation").

- **Which tests to write, and at which level:** `~/.claude/rules/testing.md` § "Eli's testing pyramid: the fewest tests that prove the code works".

### Captured asserts to regenerate

- **List the expected diffs by file, including the files that must show zero diff.** The `/eli--prebind-validation` run lives in the execution sequence (`~/.claude/rules/captured-asserts.md`). For go-live dates, seeder overrides or new `QuoteDefinitions.txt` rows, use `~/.claude/rules/quote-def-dates-and-ordering.md`; don't re-derive.

### Existing tests as regression checks

- **Tests that should pass unedited, each with a one-line reason it's relevant to this change.**

### Code-complete audit (REQUIRED in EVERY plan)

- **A written step before the code-complete HARD STOP runs `/eli--code-complete-audit <ticket-folder>` (Part C § "Code-complete audit").** A plan without it is incomplete.

### PR-description audit (REQUIRED in EVERY plan)

- **A written step in the post-verification sequence runs `/eli--audit-pr-desc` on the drafted body file before the description is presented (Part C § "Post-Test-Approval Sequence" step 6).** A plan without it is incomplete.

### AC coverage map

- **A table mapping every AC to the subsection that covers it.**

### Checklist

#### Always candidates

| Item | Trigger to mark "yes" |
|---|---|
| Build solution (`pwsh ~/.claude/scripts/Build-Solution.ps1` — runs `Test-LineLength.ps1 -Mode local` internally as a pre-build gate; do NOT list line-length as a separate step) | Any `.cs` change |
| Targeted tests on touched project via `Run-DotnetTest.ps1` | Any production code change |
| Code-complete audit (`/eli--code-complete-audit`, before the code-complete HARD STOP) | Always |
| Adversarial review (`/review-pr`) | Always |
| YouTrack stage → Review after PR creation | Always |

#### Conditional candidates

| Item | Trigger |
|---|---|
| `/eli--prebind-validation` regen + per-file diff review | Touches elements, state configs, generators, rating-adjacent code, quote definitions |
| Seed local DB (`/eli--seed`) | Touches Excel raters, quote definitions, seeder code, EF migrations |
| Solution file consistency (all 5 `.slnx`) | New module or kernel project |
| DB query review (validate on localhost first) | New or modified SQL |
| Revert `appsettings.json` to local | Plan involved pointing at remote DB |

## `/eli--prebind-validation` is the default for most plans

- **Include it in the execution sequence of any plan that affects elements, state configs, generators or rating-adjacent code.** For Commercial rating work, the validation surface is in `testing-execution.md` § "Validation surface is per product line".

### Never list a test a verification skill already runs

- **Before naming a test or adding a standalone `Run-DotnetTest.ps1` line, list the plan's skills' tests with `-ListTests` (`testing-execution.md` § "Listing tests") and confirm none already runs it.** `/eli--prebind-validation` runs everything tagged `TestGroup=PreBindResidentialValidationTests` across `Swyfft.Services.UnitTests`, `Swyfft.Services.IntegrationTests` and `Swyfft.Seeding.IntegrationTests`, including `EnsureConfigOrderWithDatabase` and `QuoteDefinitionsUnitTests`. A separate line is only for a test outside every skill in the plan, e.g. the ByPeril Excel validation tests in `Swyfft.Services.Excel.IntegrationTests`.

## A PR whose base isn't `development` gets its reviewers requested by hand (MANDATORY)

- **`.github/workflows/auto_request_review.yml` runs only on PRs based on `development`, so every PR above the bottom of a stack gets none of its reviewers.** A plan creating such a PR adds a step right after `gh pr create` (and `gh stack link`, for a stack): `gh pr edit <PR> --add-reviewer <logins>`, naming logins derived while planning from `.github/auto_request_review.yml`:

- **the `per_author` entry for `eli-swyfft`, each group expanded to its members, minus the author**
- **every group or login assigned by a `files` glob the PR's diff matches**

- **The step is its own gated write, asked as one bare-yes question, and ends by confirming the requests with the `reviewRequests` GraphQL query.**

## No Deferred Decisions

- **A plan resolves every open question before execution.** "TBD", "decide when we get there", "figure out later", "we'll see what makes sense" and "leave as an exercise" mark a punted decision: settle it now. When a decision truly depends on something found during execution, either resolve the dependency now or add a HARD STOP at the discovery point naming the deferred decision.

## Never guess a script flag

- **Never guess a script flag or console-task parameter.** Before writing one into a plan, read its definition (a script's `param(...)` block, e.g. `~/.claude/scripts/Build-Solution.ps1`, `Run-Seed.ps1`, `~/.claude/scripts/Run-DotnetTest.ps1`), never a sibling's. When explaining where a stale arg came from, research before answering.

## FULL-COVERAGE MANDATE

- **Every plan reflects every rule in this file, not only the sections Part B lists:** the type file's rules, every Part B section (or `N/A — <reason>` for conditional ones), and every Part C rule that produces a step (the plan type's HARD STOP sequence, the code-complete audit, the PR-description audit, build-once-then-parallel test runs, reading every changed captured-assert file, the post-test-approval sequence). A plan that drops a rule is incomplete. `/eli--plan-audit` enforces this on every plan, skill-made or hand-written.

---

# Part C: How to EXECUTE the plan

## ALWAYS FOLLOW THE PLAN

- **Execute steps in order.** Never skip ahead, reorder or deviate. A step waits on its dependencies. Anything that prevents adherence is a HARD STOP: explain the blocker and wait.

## Read repo files with the `Read` tool, code files above all

- **Read every repo file with the `Read` tool, code files first, while planning and executing.** A `Read` or `Edit` loads that subtree's `AGENTS.md` and the matching path-scoped `.claude/rules/*.md`; a Bash read (`cat`, `sed`, `head`) loads nothing.

## Build Once, Run Tests in Parallel

- **When a verification step runs several suites, build once with `pwsh ~/.claude/scripts/Build-Solution.ps1`, wait for it to finish, then launch every suite in one message with `-NoBuild`.** The build and every suite run in the background with no `| tail` (`core-behavior.md` § "Other", `windows-tooling.md`). Before adding a runner (`Run-DotnetTest.ps1`, `/eli--prebind-validation`, any wrapper) to the parallel block, read its `param(...)` block or SKILL.md, and pass its skip-build flag if it builds by default. Never run independent suites sequentially.

## Captured Asserts: Read Every Changed File

- **When a captured-assert regen produces diffs, open and assess every changed file individually before committing or moving on, however many there are.** No sampling. Here the regenerated baselines are the change under review, the inverse of `pr-creation.md` § "Skip generated files by default."

## Code-complete audit

- **The last step before the code-complete HARD STOP is one `/eli--code-complete-audit <ticket-folder>` pass over the whole diff.** It checks the diff against `coding-standards.md`, `comments-docs-and-external-writing.md`, `testing.md` and `refactoring.md` and fixes what it finds. Unplanned work gets the same pass at its own code-complete. Every plan points at `~/.claude/rules/coding-standards.md` § "Identifier names must be self-documenting", and every identifier in its code excerpts obeys it.

## Post-Test-Approval Sequence

- **Verification ends when the agreed tests pass and Eli explicitly says it's done.** Then this fixed order runs. Never use the project `/create-pr` command; it auto-fixes review findings, against step 4.

1. **Ask once for approval to commit and push.**
2. **Commit (`SW-XXXXX: <summary>`, per `git-safety.md`) and push, checking tracking with `git branch -vv` first.**
3. **Run `/review-pr` against the pushed state.**
4. **Discuss its findings with Eli.** Never start fixing on your own.
5. **If findings warrant action, push one more commit.** Never run a second `/review-pr`.
6. **Draft and audit the PR description:**
   1. **MANDATORY: `Read` `~/.claude/rules/pr-creation.md`.** A dedupe notice that it's already in context is not permission to skip the rules; use the content that is there.
   2. **Write the draft to a body file under the ticket's `artifacts/pr/`.**
   3. **Run `/eli--audit-pr-desc <body-file>`, every time.**
   4. **Present only the audited description.** Eli never sees the pre-audit draft.
   5. **Iterate until Eli explicitly approves the text.** **HARD STOP** until he does.
7. **HARD STOP**, then create the PR by hand (`gh pr create --body-file` per `pr-creation.md`).
8. **Move the YouTrack ticket to Review if its Stage is Backlog, Ready for Dev or Develop.**
9. **When the plan has a manual-QA section, post it as a YouTrack comment on the story.**
