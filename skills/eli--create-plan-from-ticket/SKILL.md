---
name: eli--create-plan-from-ticket
description: Co-design an implementation plan from a YouTrack ticket via sustained interactive Q&A. Loads all rules, reads the ticket and subsystem docs, walks architectural and verification decisions one at a time, and writes the final plan to a per-ticket folder under ~/.claude/tickets/ only after the design is fully settled. Use this instead of drafting plans from memory.
---

# Create Plan From Ticket

This skill enforces the planning rules in `~/.claude/rules/plan-mode.md`. Its purpose is to **prevent the agent from dumping a long plan file as the first response to "plan this."** Plans are co-designed via Q&A, not generated.

> **The agent's strongest temptation is to skip Q&A and jump to the plan. Resist it. The whole point of this skill is the conversation BEFORE the plan file gets written.**

> **BETWEEN EVERY STEP — re-read `~/.claude/rules/plan-mode.md`.** Even if you "just read it" two minutes ago. Even if it appeared in a system reminder at session start. The rules drift out of working memory faster than recall suggests — most violations the agent commits during a step (dumping a plan blob, calling ExitPlanMode mid-discussion, skipping verification subsections, guessing at script args, deferring decisions, asking anti-pattern questions) are violations of rules already in `plan-mode.md`. The cost of re-reading is small; the cost of a rule violation is enormous user-facing frustration. Skipping with "I just read it" is the exact pattern this checkpoint exists to prevent. Re-read at every step transition, no exceptions.

## Invocation

```
/eli--create-plan-from-ticket SW-XXXXX
```

The ticket ID is **required**. If the user runs `/eli--create-plan-from-ticket` with no arg, stop and ask for the ticket ID — do not guess.

---

## Step 1 — Load all rules into memory

**Read every file in `~/.claude/rules/*.md` before doing anything else.** No skipping based on "I think I remember this one." The user has repeatedly been frustrated when the agent operates from partial recall of the rules. Load them all.

**The system reminder at session start does NOT count as "loaded".** Those reminders fade from working memory as Q&A and code reads pile on. You MUST call `Read` on each file in `~/.claude/rules/*.md` as the first action of skill invocation — even if the content appears verbatim in an earlier system reminder. The act of issuing the Read calls is what keeps the rules in recent context. Skipping with "they're already in my context" is the exact failure mode this step exists to prevent.

```bash
ls ~/.claude/rules/*.md
```

Then read each one with the `Read` tool.

**HARD STOP — `Read` `~/.claude/rules/plan-mode.md` before starting the next step. No exceptions. No "I just read it." No "I remember the rules."**

## Step 2 — Read the ticket

Invoke `/eli--read-ticket SW-XXXXX` to fetch the ticket's full content: description, all comments, custom fields, linked issues, and downloaded attachments. Walk through it carefully. Do NOT skim. Scope comes from the description, the comments, and the attachments together, never the description alone: see `~/.claude/rules/youtrack.md` § "A ticket is its description, comments, and attachments, together", which Step 1 already loaded.

After reading, perform plan **Step 0a** (per `plan-mode.md`) — if the ticket's Stage is earlier than Develop (Backlog, Ready for Dev), move it to Develop; leave it if already Develop or later.

**HARD STOP — `Read` `~/.claude/rules/plan-mode.md` before starting the next step. No exceptions. No "I just read it." No "I remember the rules."**

## Step 3 — Subsystem pre-reads

Auto-detect which subsystems the ticket touches by scanning the ticket body, ACs, and any file paths it mentions. Cross-reference against the "Namespace-Specific Documentation" table in the project root `CLAUDE.md`.

Then **present the detected list to the user** and ask: "Are these the subsystems we need to pre-read? Add/remove any?" Do NOT just read them silently — the user may know about a subsystem you missed, or want to drop one that's not really in scope.

Once confirmed, read each `CLAUDE.md` file in the agreed set.

**HARD STOP — `Read` `~/.claude/rules/plan-mode.md` before starting the next step. No exceptions. No "I just read it." No "I remember the rules."**

## Step 4 — Detect existing plan file

Check for an existing plan covering this ticket: look for a `~/.claude/tickets/*/plan.md` whose
folder name carries the ticket ID (folders are ID-keyed, e.g. `tickets/SW-52867-<title>/`). If
found, offer three options:

1. **Revise interactively** — load existing plan, then run focused Q&A about what's changed
2. **Overwrite from scratch** — discard existing, start fresh
3. **Abort** — exit without changes

If no existing file, proceed to Step 5.

**HARD STOP — `Read` `~/.claude/rules/plan-mode.md` before starting the next step. No exceptions. No "I just read it." No "I remember the rules."**

## Step 5 — Q&A — Architecture (the main event)

> **This is the most important step in the skill. Do not rush it. Do not call it done after 2-3 questions.**

### One thing at a time, every question carries its evidence (MANDATORY)

This governs all Q&A in Steps 5 and 6.

**Present exactly one item per message.** Never bundle a skill/process change with a question, or two questions together, into one blob. One decision, one message — wait for the answer before the next thing.

**Every question must carry its evidence inline**, because the user has no source material in front of them otherwise:
1. **Verbatim ticket text** — quote in full every part of the ticket you reference. The moment you name or allude to any ticket element (the title/summary, an acceptance criterion, the repro steps, a section heading), paste its actual text in the same message. Naming or paraphrasing is not enough — the user cannot see the ticket. If the decision is not ticket-derived, say so explicitly: "(not in the ticket — discovered in code)".
2. **The relevant code excerpt** with `file:line`, showing exactly what changes.
3. **The decision + numbered options**, each stated as a concrete consequence.

Prefer prose with numbered options over AskUserQuestion when the evidence is substantial (AskUserQuestion truncates it). A question without its evidence is incomplete — the user should never have to go read the ticket or grep the code to answer.

**MANDATORY before presenting ANY question — `Read` `~/.claude/rules/talking-to-eli.md` § "Don't Offer Anti-Pattern Options" (don't work from memory).** Every option must be genuinely plausible. You must NEVER present "follow the acceptance criteria" vs "violate them" as a choice — implement the AC. A ticket-deviating path is raised only as an evidenced concern, never as a neutral A/B. Offering a fake choice confuses the user and burns trust for when a real concern surfaces.

Two interleaved passes:

### Pass 1 — Ticket-derived questions (do this FIRST)

Read the ticket content carefully. For every architectural decision implied by the ticket — where new code lives, what its public shape is, how it integrates with existing code, etc. — surface it explicitly:

> "The ticket says X. That means we need to decide Y. Here are the options I see, with tradeoffs..."

This is real engagement with the ticket content, not template-filling. If Pass 1 is shallow, Pass 2 will become the de facto Pass 1 and the whole exercise turns into template-fill.

**When weighing approaches, `Read` `~/.claude/rules/coding-standards.md` § "We own this code" (don't work from memory).** Never let the *current* shape of the code — an access modifier, a signature, where a value is computed — narrow the options you present. We can change existing code as part of the work; design the clean approach, not the one that avoids touching anything.

### Pass 2 — Category-coverage sweep

After Pass 1 feels exhausted, sweep the canonical category checklist as a final guard against blind spots. For each category, ask: "Have we discussed how this applies?"

| Category | Always relevant for | Typical questions |
|---|---|---|
| Code location | Feature, Refactoring | What project / folder / namespace? |
| Public API shape | Feature, Refactoring | Interfaces, method signatures, who can call it? |
| Reuse vs duplication | All | What existing helpers/services/base classes do we reuse? |
| Test infrastructure | All | Which base class? What test pattern? |
| Data shape / determinism | Feature with data output | Deterministic ordering, canonical inputs? |
| Failure modes | All | What happens when X fails? How is it surfaced? |
| Backward compat / rollout | Feature, Refactoring | Migration path? Phased rollout? Baseline commit? |
| Root cause analysis | Bug Fix | Why did this happen? What's the actual defect? |

Plan-type-conditional. Bug Fix plans don't need API-shape questions; Refactoring plans need safety-net coverage questions; Feature plans need all of these.

### Asking the plan type

During this phase, ask the user explicitly: **"What plan type is this — Bug Fix, Refactoring, or Feature?"** Each type has a different HARD STOP sequence (per plan-mode.md Part B § Plan Types).

### Hard rule: "Ready to outline?" defaults to NO

After each cluster of questions, you may ask "ready to draft the outline?" — but the default answer is **NO**. Only proceed when the user explicitly says "yes" or equivalent. If the user gives any answer other than explicit yes (including silence, "let me think", clarifying questions about your last answer), continue Q&A.

### Banned in Q&A

- Rushing to outline after 2-3 questions — must be sustained discussion
- Filler / strawman / anti-pattern options (see `talking-to-eli.md` § "Don't Offer Anti-Pattern Options"). Every option you present must be genuinely plausible.
- Asking questions whose answers are obvious from the ticket — just confirm and proceed
- Letting Pass 2 do most of the work because Pass 1 was lazy

**HARD STOP — `Read` `~/.claude/rules/plan-mode.md` before starting the next step. No exceptions. No "I just read it." No "I remember the rules."**

## Step 6 — Q&A — Verification

Build the verification section by asking, item by item. Two sub-passes:

### Sub-pass A — Per-AC walk-through

For each AC in the ticket, ask:

> "How do we verify AC #N specifically? What command, test, or file-check proves it passes?"

The user's answer becomes a concrete verification step. Do this AC by AC. Do not batch.

### Sub-pass B — Canonical generic-verification checklist

Walk through every item in the checklist below and ask "does this apply to this plan?" Skip nothing. Even items that obviously apply still get the explicit yes.

**Always candidates:**

| Item | Trigger to mark "yes" |
|---|---|
| Build solution (`pwsh ~/.claude/scripts/Build-Solution.ps1` — runs `Test-LineLength.ps1 -Mode local` internally as a pre-build gate; do NOT list line-length as a separate step) | Any `.cs` change |
| Targeted tests on touched project via `Run-DotnetTest.ps1` | Any production code change |
| Comment + ClosedSet self-audit (re-read `comments-docs-and-external-writing.md` + `SetDefinitions/CLAUDE.md`; audit every comment & ClosedSet usage the diff adds/changes — before the code-complete diff) | Always |
| Adversarial review (`/review-pr`) | Always |
| YouTrack stage → Review after PR creation | Always |

**Conditional candidates:**

| Item | Trigger |
|---|---|
| `/eli--prebind-validation` regen + per-file diff review | Touches elements, state configs, generators, rating-adjacent code, quote definitions |
| Seed local DB (`/eli--seed`) | Touches Excel raters, quote definitions, seeder code, EF migrations |
| Solution file consistency (all 5 `.slnx`) | New module or kernel project |
| DB query review (validate on localhost first) | New or modified SQL |
| Revert `appsettings.json` to local | Plan involved pointing at remote DB |
| Full project unit-test sweep (no filter) | Refactor that could ripple beyond touched files |

After AC walk + checklist sweep, ask the user: **"Anything else specific to this change that should be verified?"** — to catch verification needs that fit neither bucket.

**HARD STOP — `Read` `~/.claude/rules/plan-mode.md` before starting the next step. No exceptions. No "I just read it." No "I remember the rules."**

## Step 7 — Iterative outline loop

Draft a **concise outline** in chat (not the full plan). The outline shows section structure and key decisions, not full prose, not all the research details.

Then ask: **"Outline good as-is, or want revisions?"**

- If the user requests changes → iterate, redraft, ask again
- Default behavior = continue iterating, not "done"
- Loop ends only when the user explicitly says "good as-is" / "write it" / equivalent
- **Banned:** declaring the outline "done" without explicit user approval. Outlines may take multiple drafts.

**HARD STOP — `Read` `~/.claude/rules/plan-mode.md` before starting the next step. No exceptions. No "I just read it." No "I remember the rules."**

## Step 7.5 — Re-read `plan-mode.md` before writing the plan file

By the time the outline has been iterated, the structural requirements from `plan-mode.md` (concise-outline-vs-full-prose rule, required Verification subsections, AC coverage map, failure aggregation pattern, "no deferred decisions") have been pushed out of working memory by Q&A and codebase reads. Don't rely on recall.

`Read` `~/.claude/rules/plan-mode.md` again, then proceed to Step 8.

**HARD STOP — `Read` `~/.claude/rules/plan-mode.md` before starting the next step. No exceptions. No "I just read it." No "I remember the rules."**

## Step 8 — Write the full plan to file

Path: `~/.claude/tickets/{ticket-ids}-{title-slug}/plan.md` — one folder per ticket's work.

**Folder naming — ticket ID(s) + a title slug.**
- **Single ticket:** `SW-XXXXX-{title-slug}` — the ID, then the ticket's YouTrack title slugified
  (lowercase, hyphenated), truncated to a reasonable length (~60 chars) if long.
- **Multiple tickets:** all IDs (sorted ascending) + a slug capturing the combined work, e.g.
  `SW-51860-SW-52867-{title-slug}`. There is no "primary" ticket — list them all.
- The ID prefix makes the folder keyable (the dump scripts route output by the folder name); the
  title makes it readable. Never a free-form or conversation-seeded name.

**Everything for this ticket's work lives in the folder** — `plan.md` plus an `artifacts/`
subfolder holding every dump the work produces (ticket dumps, test output, seed logs, SolarWinds
dumps). `plan.md`, `artifacts/db-queries/`, and `artifacts/pr/` are tracked in git; the bulky dump subfolders are gitignored. Never scatter artifacts loose or
in sibling folders.

**Open `plan.md` with a header block** listing every associated `SW-XXXXX` (with YouTrack links)
and the ticket title(s) — the readable record, independent of the folder name.

The full plan is the outline structure + all technical research details accumulated during Q&A:

- File:line references for every code location discussed
- Current code excerpts where they inform the plan
- Existing patterns being followed (with file:line citations)
- Exact, verified commands (don't pattern-match — read script `param()` blocks per plan-mode.md Part A)
- All architectural decisions resolved during Q&A — no "TBD", no "decide when we get there"

**Why the full research belongs in the plan file:** the user often `/compact`s after planning is complete. The plan must be self-contained so post-compact execution doesn't waste tokens re-researching what was already known.

### Required content

The plan file must contain every section defined in `plan-mode.md` Part B, in the order that
file specifies — including § Plan Types for the HARD STOP sequence matching the chosen plan type.
Read Part B and follow it directly; don't restate the structure here — it drifts.

### Mandatory full-coverage verification gate — the plan is NOT "written" until this passes

Per `plan-mode.md` § "FULL-COVERAGE MANDATE", every plan must incorporate EVERY rule in that file —
Parts A, B, AND C — not just Part B's section list. After writing the plan, **re-read
`plan-mode.md` in full** and verify the plan reflects all three parts. Confirm each item below is
present (or `N/A — <reason>` for conditional ones); any gap means the plan is not done — go back
and add it before proceeding to Step 9:

- **Part A honored:** co-designed via Q&A; no deferred-decision phrases; options were genuine.
- **Part B sections present (written in):** Preamble block · Step 0a (→Develop) · Subsystem
  pre-reads · Step 0b (branch) · Plan type + matching HARD STOP sequence · Seeder overrides (or
  N/A + reason) · HomeownerStateConfig fold-vs-stack + feature-doc list (or N/A + reason) ·
  Verification: execution sequence · tests to add/modify · captured asserts · existing-test
  regressions · **code-complete self-audit (comments + ClosedSets)** · AC coverage map · transition
  out of verification.
- **Part C reflected:** HARD STOP sequence matches the plan type; the comment + ClosedSet
  self-audit is a written step before the code-complete diff; line-length, magic-number extraction,
  build-once-then-parallel test runs, "read every changed captured-assert file," and the
  post-test-approval sequence are all honored where they apply.

A plan that silently drops any plan-mode.md rule is incomplete — treat it exactly like a missing
test or seeder override.

### Banned in plan files

No deferred-decision phrases ("TBD", "decide when we get there", etc.) — see `plan-mode.md`
Part A § "No Deferred Decisions" for the full list. If any appear in your draft, STOP and go
back to Q&A.

**HARD STOP — `Read` `~/.claude/rules/plan-mode.md` before starting the next step. No exceptions. No "I just read it." No "I remember the rules."**

## Step 9 — Ask "execute now?"

After writing the plan file, prompt:

> **Plan written to `~/.claude/tickets/{ticket-ids}-{title-slug}/plan.md`. Execute now? (y/n)**

- `y` → execute the plan from its first step, honoring its HARD STOPs (plan-mode.md Part C)
- `n` → exit. User will decide later when/whether to execute

**HARD STOP — `Read` `~/.claude/rules/plan-mode.md` before plan execution (Part C) begins. No exceptions. No "I just read it." No "I remember the rules."**

---

## Quick reference — rules this skill enforces

- `plan-mode.md` Part A (How to PLAN): Discuss Before Drafting; No Deferred Decisions; Q&A Options Must Be Genuine
- `plan-mode.md` Part B (Required Content): Plan File Preamble; Subsystem Pre-Reads; the plan-file Step sequence; Plan Types; Seeder Overrides; Verification Section Structure
- `talking-to-eli.md`: Don't Offer Anti-Pattern Options; Question format (single-word/number answers)
- `core-behavior.md`: Gates 1, 1.5, 2, 3 throughout
