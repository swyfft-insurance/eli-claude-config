---
name: eli--audit-pr-desc
description: Audit a drafted PR description against pr-creation.md and comments-docs-and-external-writing.md, then fact-check every claim against the code. Fixes violations in place and hands back the corrected description. Mandatory before the description is ever presented to Eli.
---

# PR Description Audit

Run this on every PR description before Eli sees it. This skill holds the procedure only. What a description says lives in `pr-creation.md` § "Writing the PR description".

## Invocation

    /eli--audit-pr-desc <path-to-body-file>

The body file is required and lives under the ticket's `artifacts/pr/`. Pass the proposed title with it. With either missing, stop and ask.

An `### After review` bullet, and any sentence it strikes and replaces, is audited alone, against its commit.

## 1. Read, with actual Read calls, this turn

- The ticket's plan, in its entirety, Progress included.
- `~/.claude/rules/pr-creation.md` and `~/.claude/rules/comments-docs-and-external-writing.md`, in full.
- The repo's `.github/pull_request_template.md`.
- The body file.

## 2. Check the description against the rules

Record one row per `##` heading of the two rule files in `artifacts/pr/body-audit.md`, with a verdict: Satisfied (naming the sentence that earns it), N/A (with the reason), or Violated (fixed, then re-recorded). Derive the headings when the skill runs:

    grep -n '^## ' ~/.claude/rules/pr-creation.md ~/.claude/rules/comments-docs-and-external-writing.md

The row for `pr-creation.md` § "Writing the PR description" walks every sentence of the description, one by one. Add rows for the word count before Verification (counted, written in the row), the title, and the template's sections (Reminders deleted).

## 3. Fact-check against the code

Every claim is verified against the code, the plan, or a command run this turn, or deleted. Check most of all:
- every test count and suite name, against the run's output file
- every symbol name and `file:line`, by opening it
- every claim that something is unaffected, with the check that proves it
- every ticket quote, verbatim
- every cited PR, by opening it

A failed claim is deleted, never rephrased.

## 4. Output

The corrected description, and nothing else: no findings, no counts, no mention that an audit ran. A hard stop (missing body file, title or plan) is the one thing that reaches Eli.
