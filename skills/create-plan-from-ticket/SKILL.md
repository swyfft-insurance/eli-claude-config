---
name: create-plan-from-ticket
description: Co-design an implementation plan from a YouTrack ticket via sustained interactive Q&A. Loads all rules, reads the ticket and subsystem docs, walks architectural and verification decisions one at a time, and writes the final plan to ~/.claude/plans/ only after the design is fully settled. Use this instead of drafting plans from memory.
---

# Create Plan From Ticket

This skill enforces the planning rules in `~/.claude/rules/plan-mode.md`. Its purpose is to **prevent the agent from dumping a long plan file as the first response to "plan this."** Plans are co-designed via Q&A, not generated.

> **The agent's strongest temptation is to skip Q&A and jump to the plan. Resist it. The whole point of this skill is the conversation BEFORE the plan file gets written.**

## Invocation

```
/create-plan-from-ticket SW-XXXXX
```

The ticket ID is **required**. If the user runs `/create-plan-from-ticket` with no arg, stop and ask for the ticket ID — do not guess.

---

## Step 1 — Load all rules into memory

**Read every file in `~/.claude/rules/*.md` before doing anything else.** No skipping based on "I think I remember this one." The user has repeatedly been frustrated when the agent operates from partial recall of the rules. Load them all.

```bash
ls ~/.claude/rules/*.md
```

Then read each one with the `Read` tool.

## Step 2 — Read the ticket

Invoke `/read-ticket SW-XXXXX` to fetch the ticket's full content: description, all comments, custom fields, linked issues, and downloaded attachments. Walk through it carefully — do NOT skim. The ticket is the source of truth for ACs, scope, and most architectural decisions.

## Step 3 — Subsystem pre-reads

Auto-detect which subsystems the ticket touches by scanning the ticket body, ACs, and any file paths it mentions. Cross-reference against the "Namespace-Specific Documentation" table in the project root `CLAUDE.md`.

Then **present the detected list to the user** and ask: "Are these the subsystems we need to pre-read? Add/remove any?" Do NOT just read them silently — the user may know about a subsystem you missed, or want to drop one that's not really in scope.

Once confirmed, read each `CLAUDE.md` file in the agreed set.

## Step 4 — Detect existing plan file

Check for `~/.claude/plans/{ticket-id-lowercase}-*.md`. If found, offer three options:

1. **Revise interactively** — load existing plan, then run focused Q&A about what's changed
2. **Overwrite from scratch** — discard existing, start fresh
3. **Abort** — exit without changes

If no existing file, proceed to Step 5.

## Step 5 — Q&A — Architecture (the main event)

> **This is the most important step in the skill. Do not rush it. Do not call it done after 2-3 questions.**

Two interleaved passes:

### Pass 1 — Ticket-derived questions (do this FIRST)

Read the ticket content carefully. For every architectural decision implied by the ticket — where new code lives, what its public shape is, how it integrates with existing code, etc. — surface it explicitly:

> "The ticket says X. That means we need to decide Y. Here are the options I see, with tradeoffs..."

This is real engagement with the ticket content, not template-filling. If Pass 1 is shallow, Pass 2 will become the de facto Pass 1 and the whole exercise turns into template-fill.

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
- Filler / strawman / anti-pattern options (see `communication.md` § "Don't Offer Anti-Pattern Options"). Every option you present must be genuinely plausible.
- Asking questions whose answers are obvious from the ticket — just confirm and proceed
- Letting Pass 2 do most of the work because Pass 1 was lazy

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
| Build solution (`pwsh ./Build-Solution.ps1`) | Any `.cs` change |
| Line length check (`Test-LineLength.ps1 -Mode local`) | Any `.cs` change |
| Targeted tests on touched project via `Run-DotnetTest.ps1` | Any production code change |
| Adversarial review (`/review-pr`) | Always |
| YouTrack stage → Review after PR creation | Always |

**Conditional candidates:**

| Item | Trigger |
|---|---|
| `/prebind-captured-asserts` regen + per-file diff review | Touches elements, state configs, generators, rating-adjacent code, quote definitions |
| Seed local DB (`/seed`) | Touches Excel raters, quote definitions, seeder code, EF migrations |
| Solution file consistency (all 5 `.slnx`) | New module or kernel project |
| DB query review (validate on localhost first) | New or modified SQL |
| Revert `appsettings.json` to local | Plan involved pointing at remote DB |
| Full project unit-test sweep (no filter) | Refactor that could ripple beyond touched files |

After AC walk + checklist sweep, ask the user: **"Anything else specific to this change that should be verified?"** — to catch verification needs that fit neither bucket.

## Step 7 — Iterative outline loop

Draft a **concise outline** in chat (not the full plan). The outline shows section structure and key decisions, not full prose, not all the research details.

Then ask: **"Outline good as-is, or want revisions?"**

- If the user requests changes → iterate, redraft, ask again
- Default behavior = continue iterating, not "done"
- Loop ends only when the user explicitly says "good as-is" / "write it" / equivalent
- **Banned:** declaring the outline "done" without explicit user approval. Outlines may take multiple drafts.

## Step 8 — Write the full plan to file

Path: `~/.claude/plans/{ticket-id-lowercase}-{slug}.md`

The full plan is the outline structure + all technical research details accumulated during Q&A:

- File:line references for every code location discussed
- Current code excerpts where they inform the plan
- Existing patterns being followed (with file:line citations)
- Exact, verified commands (don't pattern-match — read script `param()` blocks per plan-mode.md Part A)
- All architectural decisions resolved during Q&A — no "TBD", no "decide when we get there"

**Why the full research belongs in the plan file:** the user often `/compact`s after planning is complete. The plan must be self-contained so post-compact execution doesn't waste tokens re-researching what was already known.

### Required content (per plan-mode.md Part B)

Every plan file must include, in order:

1. Title + plan type declaration
2. Plan File Preamble blockquote
3. Subsystem Pre-Reads block listing the confirmed CLAUDE.md files
4. Step 0 — Create Branch (boilerplate)
5. Steps 1..N (substantive work)
6. Seeder Overrides section (if plan adds new state configs)
7. Verification section with subsections:
   - Execution sequence (before pushing)
   - Tests to add or modify
   - Captured asserts to regenerate (if applicable)
   - Existing tests as regression checks
   - AC coverage map

Follow plan-mode.md Part B § Plan Types for the HARD STOP sequence matching the plan type the user chose.

### Banned in plan files

Phrases that signal a deferred decision (per plan-mode.md Part A § "No Deferred Decisions"):

- "decide when we get there"
- "figure out later"
- "TBD"
- "we'll see what makes sense"
- "leave as an exercise"

If any of these appear in your draft, STOP and go back to Q&A.

## Step 9 — Ask "execute now?"

After writing the plan file, prompt:

> **Plan written to `~/.claude/plans/{filename}.md`. Execute now? (y/n)**

- `y` → proceed to Step 0 of the plan (`/create-branch`) and walk through the plan honoring its HARD STOPs (plan-mode.md Part C)
- `n` → exit. User will decide later when/whether to execute

---

## Quick reference — rules this skill enforces

- `plan-mode.md` Part A (How to PLAN): Discuss Before Drafting; No Deferred Decisions; Q&A Options Must Be Genuine
- `plan-mode.md` Part B (Required Content): Plan File Preamble; Subsystem Pre-Reads; Step 0; Plan Types; Seeder Overrides; Verification Section Structure
- `communication.md`: Don't Offer Anti-Pattern Options; Question format (single-word/number answers)
- `core-behavior.md`: Gates 1, 1.5, 2, 3 throughout
