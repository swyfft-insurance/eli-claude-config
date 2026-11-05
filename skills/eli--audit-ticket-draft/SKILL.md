---
name: eli--audit-ticket-draft
description: Audit a drafted YouTrack ticket (a new ticket, or a rewritten summary, description or fields) against every rule that governs it, recording a verdict per rule, then fact-check every claim against the ticket's source material. Fixes violations in place and hands back the corrected draft. Mandatory before a ticket draft is ever presented to Eli.
---

# Ticket Draft Audit

The ticket counterpart to `/eli--audit-pr-desc`.

**The draft is guilty until proven clean.** A rule with no recorded verdict has not been audited. If
the audit finds nothing, be suspicious of the audit.

This skill holds the procedure only. It restates no rule, because the passes below reach every rule
in the files they walk, and a local copy would both duplicate and go stale.

## Invocation

```
/eli--audit-ticket-draft <path-to-draft-file>
```

The draft file is required: the batch JSON under the ticket's `artifacts/youtrack/`, or a markdown
draft beside it. With no arg, stop and ask. Never audit a draft that exists only in a message.

## 0. Establish the source material, before anything else

Have the ticket's source material (`writing-tickets.md`) in hand, read in this turn.

**HARD STOP, no verdict pass, when any of these holds:**

- the draft file does not exist on disk
- the source material isn't in hand

A hard stop is the one thing that reaches Eli. Say what is missing, and nothing else.

## 1. Read the rules, with actual Read calls, in this turn

Not from memory, and not skipped because the harness says a file is already in context.

- `~/.claude/rules/writing-tickets.md`, in full.
- `~/.claude/rules/comments-docs-and-external-writing.md`, in full.
- `~/.claude/rules/updating-tickets.md` § "Fields and stages", for the `IssueType` values.

Then read the draft file, start to finish.

## 2. Necessity pass, before any rule is checked

Walk every sentence of the summary and of the description above `## Technical Details`, and every
custom field value. Record one row for each in `artifacts/youtrack/ticket-audit.md` beside the
draft, naming the line of the source material it comes from and the `writing-tickets.md` bullet
that allows it. A sentence or value whose row is missing either is deleted.

## 3. Verdict pass

One row per bullet and `##` heading of `writing-tickets.md`, and one row per `##` heading of
`comments-docs-and-external-writing.md`, derived when the skill runs:

```bash
grep -nE '^(## |- )' ~/.claude/rules/writing-tickets.md
grep -n '^## ' ~/.claude/rules/comments-docs-and-external-writing.md
```

| Verdict | Means |
|---|---|
| **Satisfied** | Name the part of the draft that satisfies it. |
| **N/A** | State why. |
| **Violated** | Fix the draft, then re-record as Satisfied. |

A row with no verdict fails the audit, and no pass may be summarized as "the rest are fine".

## 4. Claim audit

Verify every factual claim against the source material, the code or a command run in this turn. A
claim that fails gets `comments-docs-and-external-writing.md` § "Fixing a failed claim means
deleting it".

## 5. Fix

Fix every violation in the draft file. When the draft is a staged batch, restage the corrected JSON.
Then present the corrected draft and nothing else, per `auditing.md` § "An audit's only output is
the fixed artifact".
