---
name: eli--audit-msg-and-present-again
description: Audit my most recent message against the rules and re-present it corrected — or retract it. Use when my last message needs to be checked against the rules (word slop, rule violations, suspect claims) instead of Eli having to type "read the rules" himself. Covers general communication; /eli--ask-properly is the variant for question formatting, /eli--revise-draft for iterating draft text.
---

# Audit Message — read the rules, audit what I just said, say it right or retract it

When invoked, do this and nothing else. The subject is the last message you sent before this
skill was invoked.

## 1. Read the rules — actual Read calls, this turn

Issue actual `Read` tool calls on ALL of:
- `~/.claude/rules/core-behavior.md` — the Gates, Gate 3, "say nothing", "every explanation teaches"
- `~/.claude/rules/talking-to-eli.md` — concision, exact names, options, caveats, invented weight
- `~/.claude/rules/comments-docs-and-external-writing.md` — all prose rules

Plus, when the message's content matches, the topical file(s): drafts of Slack/YouTrack/PR text →
`slack.md` / `youtrack.md` / `pr-creation.md`; version references → `swyfft-domain.md`;
investigation findings → `investigation.md`.

"They're already in my context" / "I just read them" do NOT count. This skill is invoked at the
exact moment your memory of the rules has demonstrably failed — no Reads in this turn's
transcript = skill failure.

## 2. Fact audit — invoke /eli--fact-check-writing on the message

Invoke `/eli--fact-check-writing` (Skill tool) and run its waves against the message — every
factual claim traced to something read, run, or quoted; quantifiers verified or deleted;
paraphrases replaced with the literal quote. Its fix discipline applies unchanged: a claim that
fails verification is deleted. Checkable-but-unchecked claims get checked NOW, with real tool
calls in this turn.

## 3. Rules audit — sentence by sentence

Treat the message as guilty until proven clean. The rows are the `##` headings of the files read in
step 1, derived when the skill runs, never from a list written here:

```bash
grep -n '^## ' ~/.claude/rules/core-behavior.md ~/.claude/rules/talking-to-eli.md ~/.claude/rules/comments-docs-and-external-writing.md
```

plus the headings of any topical file step 1 added. Every heading gets a verdict, **Satisfied** with
the sentence that earns it, **N/A** with the reason, or **Violated** with the fix applied. The table
is written to `msg-audit.md` in the session scratchpad directory. A heading with no row has not been
audited. The file is never shown to Eli.

## 4. Present the verdict — one of two outcomes

**NEVER write a Retractions block, and never quote a failed claim back at Eli.** He read it once
already; reprinting it makes him read it twice and buries the corrected text under a list of things
that are not true. Deleted claims leave no trace in the output.

- **The message survives**: present the full corrected message and nothing else. Every fix, factual
  or stylistic, is made silently. No findings list, no narration of the audit.
- **The message does not survive** — its core point fails verification, or it shouldn't have been
  sent: do NOT re-present it. Say in one or two sentences that the message was wrong, state what is
  actually true with its evidence, and re-ask any question that still stands. It is always
  acceptable for the audit's outcome to be "my last message was wrong; disregard it."

## 5. Constraints

- Audit only the last message. Don't expand scope, don't continue the underlying work, don't
  answer your own questions.
- The audit is the work. Running the Reads and then re-pasting the message unchanged is theater —
  if you found nothing to fix, be suspicious of the audit, not proud of the message.
- Steps 2 and 3 are not optional. Before presenting, `msg-audit.md` must exist in the scratchpad
  with a verdict row for every heading from the grep, and the transcript must show the
  `/eli--fact-check-writing` Skill call. If either is missing, the audit did not run.
