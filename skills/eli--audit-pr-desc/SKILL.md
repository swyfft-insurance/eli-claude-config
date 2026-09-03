---
name: eli--audit-pr-desc
description: Audit a drafted PR description against every rule that governs it, recording a verdict per rule, then fact-check every claim in it against the diff. Fixes violations before reporting. Mandatory before the description is ever presented to Eli.
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

## 0. Establish the two sources — a printed gate, before anything else

`pr-creation.md` says a description comes from exactly two sources: the ticket, and the actual
content diff read at draft time. A `--stat` file list is not the diff, and neither are earlier
in-session reads. So prove both are in hand before auditing anything.

1. **The ticket(s).** Every `SW-XXXXX` the PR covers, read via `/eli--read-ticket`.
2. **The diff.** `/eli--diff branch`, read at audit time, every hand-written file's hunks. Split out
   and skip generated files per `pr-creation.md`, and say which you skipped.

Print this block, every field filled:

> **Body file:** …
> **Proposed title:** …
> **Tickets covered, and where each was read:** …
> **Diff read at audit time:** … (command run, hand-written files read, generated files skipped)

**HARD STOP, no verdict pass, when any of these holds:**

- the body file does not exist on disk
- no title was supplied
- the diff was not read in this turn

## 1. Read the rules, with actual Read calls, in this turn

Not from memory, not from the SessionStart injection, and **not skipped because the harness says a
file is already in context.** A dedupe notice means the content is available, not that the check
happened. If a `Read` is deflected, use the content that is there and record the rule rows anyway.
The deliverable is the verdict table, never the act of reading.

- `~/.claude/rules/pr-creation.md`, in full.
- `~/.claude/rules/comments-docs-and-external-writing.md`, in full. It governs this text completely.
- `~/.claude/rules/swyfft-domain.md` § "Generator and Lookup vs Config Versions", when any version
  number appears in the draft.
- The repo's `.github/pull_request_template.md`.
- Every rules file the draft's own content implicates.

Then read the body file, start to finish.

## 2. Verdict pass

Every rule gets its own row and its own verdict. A rule with no recorded verdict has not been
audited, and no pass may be summarized as "the rest are fine".

| Verdict | Means |
|---|---|
| **Satisfied** | Name the part of the draft that satisfies it. |
| **N/A** | State why. |
| **Violated** | Fix the draft, then re-record as Satisfied. |

### 2a. `pr-creation.md` — every rule, every time

Walk it top to bottom. The rules that fail most often, each still getting its own row alongside the
rest:

- **The word budget, counted rather than estimated.** Count the narrative words and write the number
  down. Intent and blast radius together get ~100. Each surprise gets up to 75, quotes included.
  Verification is exempt from the budget but not from brevity: one line per suite, nothing wrapping
  it. A draft over budget loses content; it is never reflowed to fit.
- **Surprise inflation.** Most PRs have zero or one surprise. Three is a lot. A one-line diff
  claiming two surprises is the shape that manufactures budget, so justify each against the test in
  `pr-creation.md`: would a reviewer actually stop and ask "why did they do that?"
- **Mechanism the diff already shows.** Cut it.
- **A section per file or per component.** Restructure by what is surprising.
- **Title.** Every ticket in the body's Ticket Link section appears in the title in its own
  brackets, the product line follows in parens, and `Part N` is present when the PR delivers part of
  a multi-PR ticket.
- **Links and citations.** Every ticket ID in the body is a markdown link. Prior code is cited by PR
  number as a bare auto-link, and a commit SHA appears only alongside its PR number.
- **Personal tooling.** No skill, script, or `~/.claude/` path is named anywhere.
- **Template shape.** Sections match `.github/pull_request_template.md`, and Reminders is deleted.

### 2b. `comments-docs-and-external-writing.md` — every rule, every time

A PR description is external written prose and the file applies in full. Walk it rule by rule. It
carries the word-slop rule, no em-dashes, causal connectors as claims, one sentence per subject and
moment, exact terms repeated rather than varied, scenarios as opener plus bullets, consistent bullet
granularity, no ambiguous references, and the tense map.

The tense map earns particular attention here, because a PR description is the archetypal case it
was written for: pre-change behavior takes past tense, post-change behavior takes present, and a
sentence mixing a durable fact with a fixed defect gets split rather than forced into one tense.

## 3. Claim audit

A separate pass over different objects. Step 2 asks whether the draft satisfies a rule; this asks
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

## 4. Fix, then report

Fix every violation in the body file first. Then report:

- the narrative word count, against the budget
- rules audited, plus the violations found and fixed
- claims verified, with what proved each
- claims deleted

Report nothing as audited that has no recorded verdict. Only after this report may the description
be presented to Eli.
