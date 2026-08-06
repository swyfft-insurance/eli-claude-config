---
name: eli--fact-check-writing
description: Audit a piece of durable writing (CLAUDE.md, docs, RCA, PR description, plan) in successive single-predicate waves until a wave finds zero factual defects. Use when asked to fact-check, harden, or "do another pass" on written prose.
---

# Fact-Check Writing (waves)

Audits a draft by running **waves** over it. One wave = one named predicate applied to EVERY
sentence, run to completion — never a general once-over. Waves are ordered strictest-first so
errors are caught in wave 1, not discovered by escalating standards across passes.

> **RE-READ THIS SKILL FILE BETWEEN EVERY WAVE.** Multi-step and repetition-based skills decay in
> working memory as tool results pile up — mid-audit drift away from the skill's mandates is a
> known, repeated failure. Re-read this file before each wave, every time, no exceptions.

## Before wave 1 — MANDATORY reads

`Read` (don't recall — "I just read it" is not reading it):
- `~/.claude/rules/comments-docs-and-external-writing.md` — all prose rules, including
  § "Fixing a failed claim means deleting it — rewrites create new unverified claims"
- `~/.claude/rules/talking-to-eli.md` — concision, exact names

Re-read both again before the final (prose) wave.

## Fix discipline (every wave)

Per § "Fixing a failed claim means deleting it — rewrites create new unverified claims":
a failed claim is **deleted**, or replaced only with already-verified material — the verbatim
quote, the literal name, the exact thing read or run. A fix must never add a claim that itself
needs fact-checking. When in doubt, cut: not writing the sentence is always an option.

## The waves

Run in order. Within a wave, walk every sentence — no sampling.

1. **Source** — does each claim trace to something read, run, or quoted? Claims of absence carry
   their verification inline (`core-behavior.md` Gate 3). No source → verify it NOW (run the
   grep, read the file) or delete the claim.
2. **Strength** — does the source carry the claim *as phrased*? A doc comment or ticket supports
   only an attributed claim ("per its doc: …"). A sample supports no universal. A folder-scoped
   search supports no repo-wide conclusion — widen the search or narrow the claim.
3. **Quantifiers** — every "each / every / all / only / never / the two" is a separate
   verification obligation. Verify it exhaustively or delete the quantifier.
4. **Paraphrase** — interpretations of names, comments, and docs are replaced with the literal
   name or the verbatim quote.
5. **Prose** — full audit against `comments-docs-and-external-writing.md`: word slop, ambiguous
   references, exact-name repetition, tense precision, plan-scoped framing, bullet granularity.

## Termination

Stop when a wave finds **zero factual defects** (prose-only fixes don't reset the count).
Then say so and stop self-passing: the same auditor re-reading the same evidence has hit its
ceiling — remaining defects are for a different reader (PR review) to find.

## Report

After each wave: the wave name, each finding, and its disposition (deleted / replaced-with-quote /
verified-and-kept). No findings → say "wave N: clean".

**Then PRESENT THE FULL REVISED TEXT, verbatim, in the reply.** The findings list is not the
deliverable — the text is. Eli cannot approve, or even judge, prose he has not been shown; an audit
log with no text attached forces him to go read a file to see what he is being asked about. Show the
complete final text every time, even when the wave was clean, and even when the text is long. If the
text was written to a file, it still gets shown in the reply.
