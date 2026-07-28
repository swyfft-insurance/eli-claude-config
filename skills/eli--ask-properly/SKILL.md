---
name: eli--ask-properly
description: Re-present my most recent message in full — keep all the context and info as-is — but rewrite every question at the end into a clearly labeled list of explicit choices — each question numbered, each option within it lettered — that I can answer with a number+letter (e.g. 1a). Use when my questions were buried in prose or otherwise hard to answer.
---

# Ask Properly — replay my message with numbered choices

When invoked, do this and nothing else.

## 1. Re-read your most recent message
Re-read the last message you sent before this skill was invoked.

## 2. Re-present it
Output that message again with its information intact — don't drop context, don't summarize
it away. The only change: every question or decision you put to Eli (including ones buried in
prose, multi-part asks, and implicit "which way?" forks) becomes a clearly labeled list at the
end.

Use a two-level label scheme so the question and the chosen option are never confused:
- **Number each distinct question** — `1.`, `2.`, `3.` …
- **Letter each option within a question** — `a`, `b`, `c` …
- So Eli answers with a number+letter per question, e.g. `1a` (or `1a, 2c, 3b` across several).

NEVER use bare numbers for both the questions and their options — answering `1, 1, 2` is
ambiguous about which number is the question and which is the chosen option. Always
question-number + option-letter.

Follow `~/.claude/rules/talking-to-eli.md` (§ "Question format", § "Don't Offer Anti-Pattern
Options", § "No Ambiguous References"):
- Each option must be **genuine** — no filler, strawman, or anti-pattern decoys.
- When you have a recommendation, make it option **a** and label it "(Recommended)".
- Every question answerable with a single number+letter. No "X, or Y?" prose forks.
- Repeat the noun instead of "it"/"this"/"that" when more than one antecedent is in scope.

## 3. THE AUDIT — actually perform it, sentence by sentence

**This skill exists because your last message likely violates the rules. The audit is the work;
everything else is setup. The catastrophic failure mode is running the Reads, then pasting your
message through untouched with a clean conscience — that is not an audit, it is theater.**

First, issue actual `Read` tool calls, in this same turn, on BOTH files — they are the checklist
the audit runs against:
- `~/.claude/rules/comments-docs-and-external-writing.md`
- `~/.claude/rules/talking-to-eli.md`

"They're already in my context" / "I read them earlier" / "I remember the rules" do NOT count —
this skill gets invoked when Eli suspects a violation, and trusting your memory at that exact
moment is absurd. No Reads in this turn's transcript = skill failure.

Then audit. **Treat your message as guilty until proven clean.** Go sentence by sentence — every
sentence, not just the questions — and for each one actively ask "which rule does this break?",
not "does this seem fine?". You are hunting for violations you already missed once; if the audit
finds nothing to fix, be suspicious of the audit, not proud of the message. Recurring offenders to
hunt hardest:

- Bare ticket or PR numbers — every `SW-XXXXX` and `#NNNNN` glued to a plain-English shorthand
  ("#21881, the SW-52867 Commercial rater PR"). Eli cannot decode an opaque number, ever.
- Word slop, throat-clearing, creative-writing flourishes.
- Ambiguous references — repeat the noun.
- Business reason first; exact names ride alongside, never alone.
- Tense precision — never state a future or hypothetical outcome as present fact.
- Every option genuine; no filler, no strawman, no invented closing caveats.

Rewrite every violation before presenting. Present the conforming version — fix silently, don't
narrate the audit.

## 4. Constraints
- **Only reformat what you already asked.** Don't invent new questions, expand scope, or add
  decisions Eli never faced.
- **Don't answer the questions yourself**, and don't start or continue any work until Eli answers.
- If your last message contained **no** real question, say so plainly — don't fabricate one.
  State what (if anything) you're waiting on.
