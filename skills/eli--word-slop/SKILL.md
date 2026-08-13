---
name: eli--word-slop
description: Re-present my most recent message with all word slop stripped — filler, hedging, throat-clearing, restatement, narration. Cuts only; no new content, no fact-checking, no full rules audit (/eli--audit-msg-and-present-again is the heavyweight variant). Use when my message was bloated.
---

# Strip Slop — same message, fewest words

When invoked, do this and nothing else. The subject is the last message you sent before this
skill was invoked.

## 1. Read the brevity rules — actual Read calls, this turn

- `~/.claude/rules/talking-to-eli.md` — § "Be concise — this is the top rule"
- `~/.claude/rules/comments-docs-and-external-writing.md` — § "Word slop is the cardinal sin"

Nothing else. This skill is a cutting pass, not an audit.

## 2. Cut

Rewrite the message in the fewest words that keep the FULL meaning. Delete:
- Throat-clearing, preamble, and narration of your own process ("I checked...", "to be clear...")
- Hedging and qualifiers that change nothing
- Restatement — anything said twice, anything Eli already knows, anything the previous
  messages already established
- Explanations nobody asked for, background, adjacent answers to questions not asked

Keep every word that carries meaning: exact names, numbers, file:line references, the question
being asked. Cutting meaning is failure, same as keeping filler.

## 3. Present

Output the stripped message. Nothing else — no before/after word counts, no list of what was
cut, no commentary. The stripped message IS the entire reply.
