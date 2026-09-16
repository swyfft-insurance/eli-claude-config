---
name: eli--code-complete-audit
description: Audit a code diff against every personal coding, comment, testing and refactoring rule, one rule section per wave, recording a verdict per object and fixing violations in place. Hands back the corrected code.
---

# Code-Complete Audit

Audits the diff whole. **The diff is guilty until proven clean.** A rule section with no recorded
verdict has not been audited. If a wave finds nothing, be suspicious of the wave.

This skill holds the procedure only. It restates no rule, because the waves reach every section of
the files they walk, and a local copy would both duplicate and go stale.

## Invocation

```
/eli--code-complete-audit <ticket-folder>
```

The ticket folder is required. With no arg, stop and ask.

## 0. Pull the diff

Run `/eli--diff all`: everything the branch carries against `origin/development`, committed,
uncommitted and untracked alike. The waves walk every added or changed line, comment, identifier
and test in it.

## 1. Derive the waves at run time

The governing files, in this order:

```
~/.claude/rules/coding-standards.md
~/.claude/rules/comments-docs-and-external-writing.md
~/.claude/rules/testing.md
~/.claude/rules/refactoring.md
```

One wave per `##` section of each file, derived when the skill runs, never from a list written here:

```bash
grep -n '^## ' ~/.claude/rules/coding-standards.md ~/.claude/rules/comments-docs-and-external-writing.md ~/.claude/rules/testing.md ~/.claude/rules/refactoring.md
```

Only these four files. Nothing under the repo (`AGENTS.md`, `.claude/rules/`, subsystem docs) is
read by this skill; where a personal rule points at a repo document, the pointer stays for the human
reader and this skill does not follow it.

## 2. Run the waves

For each wave, in order:

1. `Read` that section of its file, with an actual Read call, immediately before walking. Not from
   memory, not from the SessionStart injection, not from having read it for an earlier wave.
2. Decide whether the section states a property the diff can satisfy or violate. A section that
   describes a workflow rather than the code (a HARD STOP sequence, a TDD ordering) gets the verdict
   **N/A** with the reason and the wave ends.
3. Otherwise walk every object in the diff the section governs and record a verdict for each:
   **Satisfied**, or **Violated** with the fix applied. No sampling, no "the rest are fine". An
   object with no verdict has not been audited.
4. Fix every violation in this wave before starting the next, so later waves see the corrected
   code. A fix that would change an approved design, or that the rule leaves to Eli, is a hard
   stop, not a silent edit.
5. Re-read this skill file before the next wave.

Within `comments-docs-and-external-writing.md`, the section holding the comment self-audit runs first
(its question 1, "should this comment exist at all?", deletes before anything else judges wording);
the remaining sections then run over the surviving comments.

## 3. Terminate

After the last wave, run the line-length gate (`~/.claude/scripts/Test-LineLength.ps1 -Mode branch`,
then `-Mode local` for anything uncommitted) and re-walk any wave whose fixes touched code. Stop when a full pass records zero
violations.

## 4. Output

The corrected code is the output. Findings are never shown to Eli: no verdict table, no counts, no
list of what was violated or fixed, no mention that the audit ran.

Two things still reach him:

- **A hard stop**, when a fix would change an approved design or the rule leaves the call to him.
  Say what is blocked, nothing else.
- **The build or test consequence**, in one line: whether the fixes contain an executable change,
  since a comment-only or rename-only pass never justifies a re-run.
