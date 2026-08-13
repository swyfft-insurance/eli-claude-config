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
paraphrases replaced with the literal quote. One modification to its fix discipline: a claim
that FAILS verification is not just deleted — it is quoted in the Retractions block (section 4),
because Eli has already read and absorbed the original claim. Checkable-but-unchecked claims get
checked NOW, with real tool calls in this turn.

## 3. Rules audit — sentence by sentence

Treat the message as guilty until proven clean. Every sentence: "which rule does this break?",
not "does this seem fine?". Hunt hardest for: word slop and throat-clearing; invented weight on
options; fake caveats (off-topic, non-differentiating, always-true, ass-covering); bare ticket/PR
numbers; ambiguous references; missing business-reason-plus-exact-name pairing; tense drift;
buried or ambiguous questions.

## 4. Present the verdict — one of three outcomes

- **Clean or style-only fixes**: re-present the full corrected message. Style violations are
  fixed silently — no narration of the audit.
- **Contained false claims**: open with a **Retractions** block — each false or unverifiable
  claim quoted verbatim, followed by what is actually true (with its evidence) or "unverified,
  deleted." Then the corrected message. Never silently fix a factual claim: Eli has already
  absorbed the original into his understanding, and a silent fix leaves it there.
- **The message was fundamentally wrong** — its core point fails verification, or the whole thing
  shouldn't have been sent: do NOT re-present it. Output only the retraction: what was wrong,
  what is actually true (verified), and — if the message posed a question that survives — the
  question re-asked honestly. It is always acceptable for the audit's outcome to be "my last
  message was wrong; disregard it."

## 5. Constraints

- Audit only the last message. Don't expand scope, don't continue the underlying work, don't
  answer your own questions.
- The audit is the work. Running the Reads and then re-pasting the message unchanged is theater —
  if you found nothing to fix, be suspicious of the audit, not proud of the message.
