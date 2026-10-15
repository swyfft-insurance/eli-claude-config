---
name: eli--word-slop
description: Rewrite my most recent message from scratch around what Eli asked. Decide what the answer is, keep only what serves it, and say it in the fewest words that still read on their own. No fact-checking, no full rules audit (/eli--audit-msg-and-present-again is the heavyweight variant). Use when my message was bloated.
---

# Strip Slop: rethink the point, then say it in the fewest words

When invoked, do this and nothing else. The subject is the last message you sent before this
skill was invoked.

## 1. Read the rules: actual Read calls, this turn

- `~/.claude/rules/talking-to-eli.md` § "Be concise — this is the top rule"
- `~/.claude/rules/comments-docs-and-external-writing.md` § "Word slop is the cardinal sin"
- `~/.claude/rules/core-behavior.md` § "Gate 2: Draft before posting": "When a correction shows
  the draft's premise was wrong, rewrite it from scratch instead of patching."

Nothing else. This skill is a rethink, not an audit.

## 2. Rethink the point

Start from the message of Eli's that your message was answering, not from your message.

1. Quote what Eli asked for.
2. State the answer in one or two sentences.
3. Keep a part of your message only if it answers the ask or changes what Eli decides or does
   next.

A message that answers the wrong question stays wrong however short it gets.

## 3. Write the new message from step 2

Build the message from the answer in step 2, not from the old message's text or structure.

- Lead with the plain-language meaning. Give exact names, numbers and file:line references with it.
- Every sentence makes sense to a reader who doesn't hold your context. Shorthand only you can
  decode fails the same as filler.
- New sentences use only facts already verified this session.
- No throat-clearing, preamble, or narration of your own process ("I checked...", "to be clear...").
- No hedging or qualifiers that change nothing.
- No restatement: nothing said twice, nothing Eli already knows, nothing earlier messages
  established.
- No background, and no answers to questions Eli didn't ask.

## 4. Present

Output the new message. Nothing else: no before/after word counts, no list of what was cut, no
commentary. The new message IS the entire reply.
