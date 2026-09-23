---
name: eli--fact-check-writing
description: Audit a piece of writing (CLAUDE.md, docs, RCA, PR description, PR review comment, plan) in successive single-predicate waves until a wave finds zero factual defects and zero unsound proposals. Audits both what the text asserts and what it tells the reader to do. Use when asked to fact-check, harden, or "do another pass" on written prose.
---

# Fact-Check Writing (waves)

Audits a draft by running **waves** over it. One wave = one named predicate applied to EVERY
sentence, run to completion — never a general once-over. Waves are ordered strictest-first so
errors are caught in wave 1, not discovered by escalating standards across passes.

> **RE-READ THIS SKILL FILE BETWEEN EVERY WAVE.** Multi-step and repetition-based skills decay in
> working memory as tool results pile up — mid-audit drift away from the skill's mandates is a
> known, repeated failure. Re-read this file before each wave, every time, no exceptions.

## Before wave 1 — MANDATORY read

`Read` (don't recall — "I just read it" is not reading it):
- `~/.claude/rules/comments-docs-and-external-writing.md` § "Fixing a failed claim means deleting
  it — rewrites create new unverified claims"

## Fix discipline (every wave)

**The default outcome of every wave is the input, unchanged.** Retain the original text. A sentence
is edited only when what it asserts is false, and then by deletion or by substituting the verified
value (the quote, the literal name, the number). Nothing else is a reason to touch a sentence: not
that it could be tighter, not that it characterizes rather than enumerates, not that a narrower
phrasing would be easier to defend, not that the auditor would have written it differently. A
framing or emphasis the author chose is the author's, and "incomplete" is not "wrong".

Every change in the output must trace to one named false claim. A change that cannot be traced that
way is a rewrite, and a rewrite is the failure this skill exists to prevent.

- **What happened:** three architectural characterizations ("answers what the house is",
  "initialization from property data", "a carrier branch inside `ElementService`") were cut as
  overclaims. None was false. The text lost its point.

Per § "Fixing a failed claim means deleting it — rewrites create new unverified claims":
**DELETE IT. Deletion is the default fix and needs no justification.** Replacement is the
exception, allowed only when the replacement is already-verified material already in hand: the
verbatim quote, the literal name, the exact thing read or run. A fix must never add a claim that
itself needs fact-checking. Not writing the sentence is always an option and is never the wrong
call.

**Length is never a target.** The text comes out shorter only when a claim was actually wrong and
dropping it beat researching a rephrasing. That is the only source of shrinkage. When the waves find
nothing wrong, the correct output is the input, unchanged, and a word count that did not move is a
clean audit rather than a failed one.

**A sentence that survives the waves is not yours to rewrite.** Leave every clean sentence verbatim,
including ones you would have written differently. Cutting good content to make the count fall
destroys the sentences carrying the point, because those are the only ones left to cut.

The seductive failure is the receipt: Gate 3 requires an absence or universal claim to carry its
verification inline, so you reach for another clause to support the claim instead of deleting the
claim. **Deleting the claim satisfies Gate 3 too, costs zero words, and is the preferred fix.**
Never trade a word of length for a claim the reader did not ask for.

## The waves

Run in order. Within a wave, walk every sentence — no sampling.

1. **Source** — does each claim trace to something read, run, or quoted? Claims of absence carry
   their verification inline (`core-behavior.md` Gate 3). No source → verify it NOW (run the
   grep, read the file) or delete the claim.
2. **Strength** — does the source carry the claim *as phrased*? A doc comment or ticket supports
   only an attributed claim ("per its doc: …"). A sample supports no universal. A folder-scoped
   search supports no repo-wide conclusion — widen the search or narrow the claim.
   **Causal connectors are claims.** "A because B", "A so B", "A therefore B", "A since B" assert
   causation on top of A and B, so each connector is a third thing to verify. Verifying A and B and
   moving on is how a fabricated link survives an audit. Unverified causation → delete the
   connector and leave the facts as separate sentences.
3. **Quantifiers** — every "each / every / all / only / never / the two" is a separate
   verification obligation. Verify it exhaustively or delete the quantifier.
4. **Paraphrase** — interpretations of names, comments, and docs are replaced with the literal
   name or the verbatim quote.
5. **Advice** — every sentence telling the reader to do something is a proposal, not a claim, and
   waves 1-4 cannot touch it. They all work by going and reading a source; a proposal has no
   source, so it passes clean the moment the nouns inside it point at real things. Find them by
   their verbs: "should", "worth", "consider", "the fix is", "needs to", "recommend", "just".
   Check each proposal on its own terms:
   - **Does the proposed action achieve the stated goal?** Read the thing being changed and the
     thing being cited, then follow the change through to the outcome.
   - **Is the goal already achieved without it?** A proposal that duplicates what existing code, an
     existing rule, or the surrounding text already does is redundant however real its nouns are.
   - **Is every part of it load-bearing?** A proposal joining two changes with "and" is two
     proposals. Check each separately; one can be sound and the other not.

   A proposal that fails any of these is **deleted**, not softened. Rephrasing it as a question
   does not rescue it: a question premised on a false proposal costs the reader exactly as much
   time. State the problem and leave the fix to whoever owns the code. That is always available
   and never wrong.

   - **What happened:** a PR review inline ended "Worth one line mirroring the 'genuine API
     surface' scoping and the OpenAPI exception at line 273." Both nouns were real and both were
     read, so two full audits passed it. The OpenAPI exception requires those docs to be present;
     the rule being edited already flags them when missing, so mirroring it in would have changed
     nothing.

## Termination

Stop when a wave finds **zero factual defects and zero unsound proposals**.
Then stop self-passing: the same auditor re-reading the same evidence has hit its ceiling.

**Never narrate the stop.** This section is instruction to you, not copy for the reply. Sentences
like "remaining defects are for a different reader" are skill boilerplate, and pasting them into the
reply is filler that describes the process instead of delivering the text.

## Output

**The reply is the revised text, verbatim, and nothing else.**

No findings list, no per-wave dispositions, no word-count delta, no preamble, no reflection on how
the audit went, no explanation of why a fix was chosen, no self-criticism, no promises about future
passes. **Never quote a failed claim back at Eli, and never write a Retractions block.** He read the
original once already; reprinting the parts that were wrong makes him read them twice and buries the
text he actually needs. A deleted claim leaves no trace in the output.

Show the complete final text every time, even when every wave was clean, and even when the text is
long. If the text was written to a file, it still gets shown in the reply.
