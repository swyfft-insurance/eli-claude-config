---
name: eli--audit-msg-and-present-again
description: Audit my most recent message by running every audit that applies to it (facts, tense, question format, the artifact's own audit, a heading-by-heading rules pass, then word slop), then re-present it corrected or retract it. Use when my last message needs checking against the rules instead of Eli having to type "read the rules" himself.
---

# Audit Message: run every audit that applies, then say it right or retract it

When invoked, do this and nothing else. The subject is the file passed as the argument, an unsent draft, when there is one, and otherwise the last message you sent before this skill was invoked. Every skill invoked here audits that subject wherever its own instructions say "the last message you sent". Each step runs on the text the step before it produced. A skill invoked here skips its own "present" step, and its output feeds the next step.

## 1. Facts

Invoke `/eli--fact-check-writing` on the text. A claim that fails is deleted. A claim that can be checked gets checked now, with real tool calls in this turn.

## 2. Tense

Invoke `/eli--tense-audit` on the text.

## 3. Questions

When the text asks Eli anything, or leaves a decision he has to make unasked, invoke `/eli--ask-properly` on it.

## 4. The artifact's own audit

When the message carries a draft that has its own row in `~/.claude/rules/auditing.md` § "The audit skills", invoke that row's audit. Skip the audits steps 1 to 3 already ran.

## 5. Rules pass, heading by heading

`Read`, with actual Read calls this turn, `~/.claude/rules/core-behavior.md`, `~/.claude/rules/talking-to-eli.md` and `~/.claude/rules/comments-docs-and-external-writing.md`. Add the topical files the content matches: `slack.md`, `writing-tickets.md` or `pr-creation.md` for a draft of posted text, `swyfft-domain.md` for version references, `investigation.md` for findings, and `plan-mode.md` plus the plan type's file in `~/.claude/plan-types/` for any message sent while working a ticket. Every question in such a message is checked against `plan-mode.md` § "Banned" and the type file's ban list. A dedupe notice is not a read: use the content it points to.

The rows are the `##` headings of those files, derived when the skill runs:

    grep -n '^## ' ~/.claude/rules/core-behavior.md ~/.claude/rules/talking-to-eli.md ~/.claude/rules/comments-docs-and-external-writing.md

plus the headings of any topical file added. Every heading gets a verdict: **Satisfied** with the sentence that earns it, **N/A** with the reason, or **Violated** with the fix applied. The table goes in `msg-audit.md` in the session scratchpad and is never shown to Eli.

## 6. Word slop

Invoke `/eli--word-slop` on the text steps 1 to 5 produced. It runs last (`~/.claude/rules/auditing.md` § "Slop first, audit later").

## 7. Present: one of two outcomes

Never write a Retractions block, and never quote a failed claim back at Eli. Deleted claims leave no trace in the output.

- **The message survives**: present the full corrected message and nothing else. Every fix is made silently.
- **The message does not survive** (its core point fails verification, or it shouldn't have been sent): don't re-present it. Say in one or two sentences that it was wrong, state what is true with its evidence, and re-ask any question that still stands.
- **The subject is a file**: write the corrected text back to the file before presenting it.

## 8. Constraints

- Audit only the subject. Don't expand scope, continue the underlying work, or answer your own questions.
- An audit that finds nothing is suspect, not the message's credit.
- Steps 1, 2, 5 and 6 always run. Before presenting, the transcript shows the `/eli--fact-check-writing`, `/eli--tense-audit` and `/eli--word-slop` Skill calls, plus each conditional audit that applied. `msg-audit.md` has a row for every heading, and `word-slop.md` has a row for every sentence word-slop received. If any is missing, the audit did not run.
