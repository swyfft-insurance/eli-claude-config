---
name: eli--audit-pr-desc
description: Audit a drafted PR description against every rule that governs it, recording a verdict per rule, then fact-check every claim in it against the diff. Fixes violations in place and hands back the corrected description. Mandatory before the description is ever presented to Eli.
---

# PR Description Audit

Run this on every PR description before showing it to Eli. It is the PR-description counterpart to
`/eli--plan-audit`: mandatory, never requested, and the description does not get presented until it
passes.

**The draft is guilty until proven clean.** A rule with no recorded verdict has not been audited. If
the audit finds nothing, be suspicious of the audit.

This skill holds the procedure only. It restates no rule, because the passes below reach every rule
in the files they walk, and a local copy would both duplicate and go stale.

## Why it exists

Having the rules in context does not produce a description that follows them. The word budget in
`pr-creation.md` has been blown by more than double on a one-line diff while the file sat in context
the whole time. Reading the rules again does not fix that, because the failure is not ignorance of
the rule, it is never checking the draft against it. This skill is that check, and it is separate
from writing so it cannot be skipped by feeling done.

The gate is on **presenting**, not on drafting. Showing Eli a description this skill has not passed
is the violation.

## Invocation

```
/eli--audit-pr-desc <path-to-body-file>
```

The body file is required, and it is a real file on disk under the ticket's
`artifacts/pr/` (per `pr-creation.md`, the body travels as `--body-file`). With no arg, stop and ask.
Never audit a description that exists only in a draft message: the thing audited must be the thing
posted, byte for byte.

The proposed **title** is audited too. Pass it in the same invocation or state it in the response
before starting, because several rules govern the title alone.

## 0. Establish the two sources, before anything else

`pr-creation.md` says a description comes from exactly two sources: the ticket, and the actual
content diff read at draft time. A `--stat` file list is not the diff, and neither are earlier
in-session reads. So prove both are in hand before auditing anything.

1. **The ticket(s).** Every `SW-XXXXX` the PR covers, read via `/eli--read-ticket`.
2. **The diff.** `/eli--diff branch`, read at audit time, every hand-written file's hunks. Split out
   and skip generated files per `pr-creation.md`, and say which you skipped.

Both are established silently. Nothing about establishing them is reported.

**HARD STOP, no verdict pass, when any of these holds:**

- the body file does not exist on disk
- no title was supplied
- the diff was not read in this turn

A hard stop is the one thing that does reach Eli, because it asks him for something. Say what is
missing, and nothing else.

## 1. Read the rules, with actual Read calls, in this turn

Not from memory, not from the SessionStart injection, and **not skipped because the harness says a
file is already in context.** A dedupe notice means the content is available, not that the check
happened. If a `Read` is deflected, use the content that is there and audit against it anyway.
The deliverable is the corrected description, never the act of reading.

- `~/.claude/rules/pr-creation.md`, in full.
- `~/.claude/rules/comments-docs-and-external-writing.md`, in full. It governs this text completely.
- `~/.claude/rules/swyfft-domain.md` § "Generator and Lookup vs Config Versions", when any version
  number appears in the draft.
- The repo's `.github/pull_request_template.md`.
- Every rules file the draft's own content implicates.

Then read the body file, start to finish.

## 2. Necessity pass, before any rule is checked

A description can be true in every sentence, fit every rule and the budget, and still be mostly
content the reviewer gets from the diff. The rule passes below cannot catch that: they check that a
sentence is allowed, never that it is needed. So this pass runs first and deletes before anything
else is judged.

Walk every narrative sentence (everything outside Ticket Link and Verification) and record one row
per sentence in `artifacts/pr/body-audit.md`: does the diff, or a comment or doc the diff adds, already
tell the reviewer this? Name where. **Yes means delete.** The sentence survives only when the row
names the specific question a reviewer would ask that neither the diff nor its comments answer.
Examples of survivors: a fix that lives in a binary the diff cannot show, a ruling from the ticket or
Slack that explains code that looks wrong, a deviation from the ticket's stated scope.

Fewer sentences than the budget allows is the expected result. The budget is a ceiling.

- **What happened:** a description for four placed raters passed every rule row at 95 of ~100 words
  and three tagged surprises. Three of the four bold blocks restated seeder, generator and baseline
  changes the diff showed and a doc comment the diff added.

## 3. Verdict pass

Every rule gets its own row and its own verdict, and the rows are written down. The table lives at
`artifacts/pr/body-audit.md` beside the body, one row per `##` heading of the two rule files, with
the verdict and the sentence of the draft that earns it. The file is never shown to Eli; it exists
so a skipped section is visible as a missing row. A heading with no row fails the audit, and no
pass may be summarized as "the rest are fine".

| Verdict | Means |
|---|---|
| **Satisfied** | Name the part of the draft that satisfies it. |
| **N/A** | State why. |
| **Violated** | Fix the draft, then re-record as Satisfied. |

### 3a. Derive the rows at run time

The rows come from the rule files when the skill runs, never from a list written here:

```bash
grep -n '^## ' ~/.claude/rules/pr-creation.md ~/.claude/rules/comments-docs-and-external-writing.md
```

For `pr-creation.md`, the bullet list above its first `##` is one row per bullet as well. Walk each
file top to bottom and give every heading its row before moving to the next file.

### 3b. Rows every PR description gets on top of the headings

- **The word budget, counted rather than estimated.** Count the narrative words and write the number
  in the row. Intent and blast radius together get ~100. Each surprise gets up to 75, quotes included.
  These are ceilings on what survived the necessity pass, never an allowance to fill.
  Verification is exempt from the budget but not from brevity: one line per suite, nothing wrapping
  it. A draft over budget loses content; it is never reflowed to fit.
- **One row per surprise, naming its kind.** `pr-creation.md` allows three kinds: a deviation from
  the ticket, an unrelated change riding along, a decision with a non-obvious alternative. The row
  names which one, in those words, and the reviewer question from the necessity pass that the block
  answers. A kind with no unanswered question is not a surprise. A block that implements the AC is
  none of the three and is deleted. A block whose subject is a conflict between two sources quotes both sources verbatim.
- **Title.** Every ticket in the body's Ticket Link section appears in the title in its own
  brackets, the product line follows in parens, and `Part N` is present when the PR delivers part of
  a multi-PR ticket.
- **Template shape.** Sections match `.github/pull_request_template.md`, and Reminders is deleted.

The tense map in `comments-docs-and-external-writing.md` earns particular attention, because a PR
description is the archetypal case it was written for: pre-change behavior takes past tense,
post-change behavior takes present, and a sentence mixing a durable fact with a fixed defect gets
split rather than forced into one tense.

## 4. Claim audit

A separate pass over different objects. Step 3 asks whether the draft satisfies a rule; this asks
whether a sentence in it is true.

Every factual claim is **verified** or **deleted**. There is no third disposition, and "the ticket
said so" is not one of the two. A verified claim was checked against the diff, the code, or a
command run in this turn.

Claims a PR description gets wrong most often:

- **Every test count and every suite name.** Read the run's output file. A count recalled from
  earlier in the session is not verified, and a suite that was never run does not appear.
- **Every `file:line` and every symbol name.** Open it. A symbol pattern-matched from a sibling is
  wrong often enough to be worthless.
- **Every claim about what the change does not affect.** An absence claim carries the check that
  proved it, per `core-behavior.md` Gate 3.
- **Every quote from a ticket or Slack.** Verbatim, or cut.
- **Every prior-art citation.** Open the PR or commit and confirm it shows what the draft says.

A claim that fails is **deleted**, never rephrased. A rewrite is a new unverified claim wearing the
banner of a fix, per `comments-docs-and-external-writing.md` § "Fixing a failed claim means deleting
it".

## 5. Fix

Fix every violation in the body file, then present the corrected description and nothing else.

**The audit's findings are never shown to Eli** — no verdict table, no counts, no list of what was
violated or fixed, no mention that an audit ran. He already knows the first pass broke the rules,
which is why this skill exists. Surfacing the wreckage costs him time and tells him nothing he
wants.
