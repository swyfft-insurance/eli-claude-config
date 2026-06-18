---
name: ask-properly
description: Re-present my most recent message in full — keep all the context and info as-is — but rewrite every question at the end into a clearly numbered list of explicit choices I can answer with a single number. Use when my questions were buried in prose or otherwise hard to answer.
---

# Ask Properly — replay my message with numbered choices

When invoked, do this and nothing else.

## 1. Re-read your most recent message
Re-read the last message you sent before this skill was invoked.

## 2. Re-present it
Output that message again with its information intact — don't drop context, don't summarize
it away. The only change: every question or decision you put to Eli (including ones buried in
prose, multi-part asks, and implicit "which way?" forks) becomes a clearly **numbered** list
at the end, each entry an explicit choice Eli can answer with a single number.

Follow `~/.claude/rules/communication.md` (§ "Question format", § "Don't Offer Anti-Pattern
Options", § "No Ambiguous References"):
- Each choice must be **genuine** — no filler, strawman, or anti-pattern decoys.
- When you have a recommendation, make it choice 1 and label it "(Recommended)".
- Every question answerable with a single number. No "X, or Y?" prose forks.
- Repeat the noun instead of "it"/"this"/"that" when more than one antecedent is in scope.

## 3. Constraints
- **Only reformat what you already asked.** Don't invent new questions, expand scope, or add
  decisions Eli never faced.
- **Don't answer the questions yourself**, and don't start or continue any work until Eli answers.
- If your last message contained **no** real question, say so plainly — don't fabricate one.
  State what (if anything) you're waiting on.
