---
name: eli--revise-draft
description: Iterate a draft (rule text, PR description, Slack/YouTrack post, doc section, skill text) with Eli through feedback rounds until explicit approval. Use whenever presenting draft text for review or applying Eli's feedback to a prior draft.
---

# Revise Draft (feedback rounds)

The collaborative loop: present a draft, take feedback, revise, re-present — until explicit
approval. Gate 2 governs the whole flow: nothing is posted, written to rules/memory, committed,
or sent anywhere until Eli explicitly approves the text.

> **RE-READ THIS SKILL FILE BETWEEN EVERY ROUND.** Multi-step and repetition-based skills decay in
> working memory as feedback rounds pile up — mid-loop drift away from the skill's mandates is a
> known, repeated failure. Re-read this file before acting on each round of feedback, every time,
> no exceptions.

## MANDATORY reads — before the FIRST draft and before EVERY revision round

`Read` (don't recall — "I just read it" is not reading it):
- `~/.claude/rules/comments-docs-and-external-writing.md` — all prose rules, including
  § "Fixing a failed claim means deleting it — rewrites create new unverified claims"
- `~/.claude/rules/talking-to-eli.md` — concision, exact names, question format

## The loop

1. **Present the draft** in chat, verbatim — the exact text that would ship, not a summary of it.
2. **Take feedback.** Every point Eli raises gets addressed — fixed, or answered with why not
   (then his call). Questions in his feedback are questions (Gate 1): answer them, don't
   silently redraft around them.
3. **Revise exactly what was flagged.** No drive-by rewrites of unflagged text. Any new sentence
   a fix requires follows the delete-don't-rewrite rule: verified material only, or leave it out.
4. **Re-present the delta** — what changed since the last round, stated plainly. Re-show the full
   draft only when the changes are scattered enough that the delta alone is unreadable.
5. **Repeat** until Eli explicitly approves ("post it", "write it", "go ahead"). Clarifications,
   side comments, and partial edits are NOT approval (Gate 2). When in doubt, ask.
6. **Only then** perform the external action — and perform it with the approved text verbatim.

## Rules

- Approval applies to the text approved — a later edit, however small, resets to unapproved.
- If the draft contains factual claims, they carry the same verification bar as any doc: a claim
  that can't be verified is deleted before the draft is ever presented (run `/eli--fact-check-writing`
  on drafts with factual content).
