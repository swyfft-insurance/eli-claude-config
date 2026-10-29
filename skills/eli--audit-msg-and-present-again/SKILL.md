---
name: eli--audit-msg-and-present-again
description: Audit my most recent message by running every audit that applies to it (word slop, facts, tense, question format, the artifact's own audit, and a heading-by-heading rules pass), then re-present it corrected or retract it. Use when my last message needs checking against the rules instead of Eli having to type "read the rules" himself.
---

# Audit Message: run every audit that applies, then say it right or retract it

When invoked, do this and nothing else. The subject is the last message you sent before this skill was invoked. Each step runs on the text the step before it produced. A skill invoked here skips its own "present" step, and its output feeds the next step.

## 1. Word slop

Invoke `/eli--word-slop`. It rewrites the message from scratch around what Eli asked, so it runs first, and every later step checks its output.

## 2. Facts

Invoke `/eli--fact-check-writing` on the text. A claim that fails is deleted. A claim that can be checked gets checked now, with real tool calls in this turn.

## 3. Tense

Invoke `/eli--tense-audit` on the text.

## 4. Questions

When the text asks Eli anything, or leaves a decision he has to make unasked, invoke `/eli--ask-properly` on it.

## 5. The artifact's own audit

When the message carries one of these drafts, invoke its audit:
- a PR description: `/eli--audit-pr-desc` (its body file must exist on disk)
- a standup: `/eli--audit-standup-draft`
- a plan: `/eli--plan-audit`

## 6. Rules pass, heading by heading

`Read`, with actual Read calls this turn, `~/.claude/rules/core-behavior.md`, `~/.claude/rules/talking-to-eli.md` and `~/.claude/rules/comments-docs-and-external-writing.md`. Add the topical files the content matches: `slack.md`, `youtrack.md` or `pr-creation.md` for a draft of posted text, `swyfft-domain.md` for version references, `investigation.md` for findings, and `plan-mode.md` plus the plan type's file in `~/.claude/plan-types/` for any message sent while working a ticket. Every question in such a message is checked against `plan-mode.md` § "Banned" and the type file's ban list. A dedupe notice is not a read: use the content it points to.

The rows are the `##` headings of those files, derived when the skill runs:

    grep -n '^## ' ~/.claude/rules/core-behavior.md ~/.claude/rules/talking-to-eli.md ~/.claude/rules/comments-docs-and-external-writing.md

plus the headings of any topical file added. Every heading gets a verdict: **Satisfied** with the sentence that earns it, **N/A** with the reason, or **Violated** with the fix applied. The table goes in `msg-audit.md` in the session scratchpad and is never shown to Eli.

## 7. Present: one of two outcomes

Never write a Retractions block, and never quote a failed claim back at Eli. Deleted claims leave no trace in the output.

- **The message survives**: present the full corrected message and nothing else. Every fix is made silently.
- **The message does not survive** (its core point fails verification, or it shouldn't have been sent): don't re-present it. Say in one or two sentences that it was wrong, state what is true with its evidence, and re-ask any question that still stands.

## 8. Constraints

- Audit only the last message. Don't expand scope, continue the underlying work, or answer your own questions.
- An audit that finds nothing is suspect, not the message's credit.
- Steps 1, 2, 3 and 6 always run. Before presenting, the transcript shows the `/eli--word-slop`, `/eli--fact-check-writing` and `/eli--tense-audit` Skill calls, plus each conditional audit that applied, and `msg-audit.md` has a row for every heading. If any is missing, the audit did not run.
