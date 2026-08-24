---
name: eli--plan-audit
description: Audit a written plan file against every rule that governs it, recording a verdict per rule, then fact-check every claim in it. Fixes violations before reporting. Mandatory at the end of every plan, like the comment and ClosedSet audits at code-complete.
---

# Plan Audit

Run this on every plan file before calling the plan written. It is the plan-file counterpart to the
comment and ClosedSet audits at code-complete: mandatory, never requested, and the plan is not done
until it passes.

**The plan is guilty until proven clean.** A rule with no recorded verdict has not been audited. If
the audit finds nothing, be suspicious of the audit.

This skill holds the procedure only. It restates no rule, because the passes below reach every rule in
the files they walk, and a local copy would both duplicate and go stale.

## Why it exists

A plan is re-injected as canonical context at every compact, so it governs the rest of the ticket. A
rule dropped from the plan is dropped for the whole ticket, and a wrong claim inside it gets believed
and acted on. Neither is something a hook can reliably block.

## Invocation

```
/eli--plan-audit <ticket-folder-name>
```

The ticket folder is required. With no arg, stop and ask. Never guess which plan to audit.

## 0. Resolve the declared type — a printed gate, before anything else

The declared type decides which playbooks get added in 2b, so a wrong or skipped type collapses that
part of the audit. Resolve it deterministically, and print the result. No later step begins until the
block below appears in the response.

1. **Read the plan file.** Extract the plan type **verbatim** as the plan declares it. Never infer the
   type from the ticket, the file paths, or what the work looks like.
2. **Derive the valid types from `plan-mode.md` at runtime.** Never a list written here or recalled:

   ```bash
   awk '/^## Plan Types/{f=1;next} /^## /{f=0} f && /^### /{sub(/^### /,"");print}' ~/.claude/rules/plan-mode.md
   ```

3. **Match the declared type against that output exactly.** Then read that type's own section in
   `plan-mode.md` and list every file and skill the section names.

Print this block, every field filled:

> **Declared type (verbatim from the plan):** …
> **Types found in `plan-mode.md`:** …
> **Match:** …
> **Files the type's section mandates:** … (write `none beyond plan-mode.md` when the section names no
> playbook, so "I looked and there are none" is distinguishable from "I didn't look")

**HARD STOP, no verdict pass, when any of these holds:**

- the plan declares no type
- the declared type matches nothing in the derived list
- the declared type matches more than one

Each means the plan is wrong or `plan-mode.md` moved. Report which, and wait.

## 1. Read the rules, with actual Read calls, in this turn

Not from memory, not from the SessionStart injection.

- `~/.claude/rules/plan-mode.md`, in full.
- Every file Step 0 resolved.
- Every rules file the plan's own steps name.

Then read the plan file, start to finish.

## 2. Verdict pass

Every rule gets its own row and its own verdict. A rule with no recorded verdict has not been audited,
and no pass may be summarized as "the rest are fine".

| Verdict | Means |
|---|---|
| **Satisfied** | Name the plan section that satisfies it. |
| **N/A** | State why, in the plan file, not only in the report. |
| **Violated** | Fix the plan, then re-record as Satisfied. |

### 2a. `plan-mode.md`, Parts A, B and C — every plan, every type

Walk it top to bottom. Every rule gets a row whether or not the plan mentions it.

**The declared type never narrows this pass.** Step 0 resolves which playbooks get *added* in 2b; it
subtracts nothing here. A type can reduce or exempt an individual rule, and Bug Fix reduces several,
but only that type's own section may grant the exemption. Read the section before recording an N/A,
and record the exemption's source. An N/A justified by "this is a rater ticket" rather than by text in
`plan-mode.md` is a violation wearing an N/A.

Two failure modes to watch. A rule mandating text physically in the plan is satisfied only by that
text being there, never by the plan honoring it in spirit. And "the plan doesn't mention this rule" is
never itself an N/A: silence is what the audit exists to catch.

### 2b. Every other governing file

Type-specific playbooks are the minority of what governs a plan. Derive the full candidate set at
runtime rather than from any list written here:

```bash
ls ~/.claude/rules/*.md
```

Every file in that output gets a one-line verdict: **applies** or **N/A with the reason**. Then walk
each applying file rule by rule, exactly as in 2a. The files Step 0 resolved are already in this set
and always apply.

Add to the same pass:

- the repo docs the plan's own subsystem pre-reads name, which carry mandatory conventions of their own
- every rules file the plan's own steps name

A file marked N/A without a reason counts as unaudited, the same as a rule with no verdict.

## 3. Claim audit

A separate pass over different objects. Step 2 asks whether the plan satisfies a rule; this asks
whether a sentence in the plan is true. A rule row can read "Satisfied, the plan cites its evidence"
without anyone having opened what it cites. This is the pass that opens it.

Every factual claim in the plan is **verified**, **flagged provisional**, or **deleted**. There is no
fourth disposition, and "the ticket said so" is not one of the three. A verified claim carries its
evidence in the plan: the `file:line`, the command run, the query, the block read.

Claims a plan gets wrong most often, each verified individually and never on trust:

- **Every file path the plan names.** `find` or `ls` it. A path pattern-matched from a sibling state or
  product line is wrong often enough to be worthless.
- **Every command and flag the plan will run.** Read the source of what it invokes.
- **Every prior-art citation**, the ticket's included. Open the `file:line` and confirm it shows what
  the plan says it shows.
- **Every claim inherited from the ticket.** Tickets are drafts, often AI-authored, and their own
  footers often say so. A ticket claim that survives verification is recorded with your own evidence,
  never as "per ticket".

Flagging provisional is permitted only where the declared type's own rules permit it, and never for a
fact readable while authoring. Labeling a verified item provisional drains the flag of meaning at the
items that depend on it.

## 4. Fix, then report

Fix every violation in the plan file first. Then report:

- rules audited, plus the violations found and fixed
- files from 2b marked N/A, with the reason each
- claims verified, with what proved each
- claims flagged provisional, and the checkpoint that resolves each
- claims deleted

Report nothing as audited that has no recorded verdict.
