---
name: eli--fact-check-writing
description: Fact-check a piece of writing (CLAUDE.md, docs, RCA, PR description, PR review comment, Slack or YouTrack draft, plan). Confirm every claim is correct and every proposal is sound, and change ONLY what is actually incorrect. The ideal result is the text unchanged. Use when asked to fact-check or "do another pass" on written prose.
---

> **⚠️ EXTREMELY IMPORTANT: DO NOT change anything that is actually correct. Eli runs this skill out of an abundance of caution.**

# Fact-Check Writing

## The goal: confirm the text is right

A fact-check confirms that the writing is correct. **The ideal outcome is no change at all.**
Change a sentence ONLY when it is actually incorrect: what it says is false, or a proposal in it
would not work. Nothing else is a reason to touch it.

None of these is a defect:
- The sentence is incomplete, or leaves out a caveat.
- It could be shorter, tighter, more precise, or easier to defend.
- It characterizes instead of enumerating.
- You would have framed, ordered or emphasized it differently.
- It fails under a stricter or more literal reading than the plain one.

A clean fact-check returns the input verbatim. That is success, not a missed opportunity.

> **RE-READ THIS SKILL FILE BETWEEN EVERY WAVE.** Drifting away from these mandates mid-audit is a
> known, repeated failure.

## Before wave 1: mandatory read

`Read` (don't recall):
- `~/.claude/rules/comments-docs-and-external-writing.md` § "Fixing a failed claim means deleting
  it — rewrites create new unverified claims"

## What a sentence says

Check what the sentence means in plain English, in its context, to the reader it was written for.
Never construct a reading the words don't carry and then fact-check that. A sentence describing
how something works ("each request gets its own connection") describes the pattern. It is not a
count of every request that exists.

## The waves

One wave applies one check to every sentence, with no sampling. Run them in order.

1. **Source.** Each factual claim traces to something read, run or quoted. When it doesn't, verify
   it now: read the file, run the grep, run the query. A verified claim stays as written.
2. **Strength.** The evidence supports the claim as the plain reading states it. A sample doesn't
   support a universal. A folder-scoped search doesn't support a repo-wide conclusion. A doc
   comment or ticket supports only an attributed claim. **Causal connectors are claims.**
   "Because", "so", "therefore" and "since" assert a causation on top of the facts they join.
   Verify the causation itself.
3. **Quantifiers.** "Each", "every", "all", "only", "never" and "the two" cover the set the
   sentence is about, read in context. The quantifier is wrong only when a member of that set
   breaks it.
4. **Paraphrase.** A paraphrase of a name, comment, doc or quote is wrong only when it misstates
   its source. A correct paraphrase stays.
5. **Advice.** A sentence telling the reader to do something ("should", "worth", "consider", "the
   fix is", "needs to", "recommend", "just") is a proposal, and waves 1-4 don't test it. Check it
   on its own terms:
   - **Whose advice is it?** In a draft posted as Eli, a proposal Eli didn't make is deleted.
   - **Does the action achieve the stated goal?** Read the thing being changed and the thing being
     cited, then follow the change through to the outcome.
   - **Is the goal already met without it?** A proposal that duplicates existing code, an existing
     rule or the surrounding text is redundant.
   - **Is every part load-bearing?** A proposal joining two changes with "and" is two proposals.
     Check each.

## Fixing an incorrect sentence

Fix only the part that is incorrect, per § "Fixing a failed claim means deleting it — rewrites
create new unverified claims":
- **A false claim**: delete it, or replace it with already-verified material in hand (the verbatim
  quote, the literal name, the exact number). Never rephrase it. A rephrasing is a new, unverified
  claim.
- **A false causal connector**: delete the connector. The facts it joined stay as separate
  sentences.
- **A false quantifier**: delete the quantifier.
- **A wrong paraphrase**: replace it with the literal name or the verbatim quote.
- **An unsound proposal**: delete it. Don't soften it or turn it into a question.

A claim you can't verify either way is not a fix target. Leave it as written and name it below the
text (§ "Output").

A fix never adds a claim that itself needs checking, and never adds words to defend a claim.

## Before replying: justify every change, in writing

Compare your output with the input, sentence by sentence. Write one row per change to `fact-check.md` in the ticket's `artifacts/`, or in the session scratchpad when there is no ticket. The file is never shown to Eli.

| Input text | Plain reading, in context | Evidence the plain reading is false |

- The evidence column cites a file:line, a command's output or a quote that contradicts the plain reading. Evidence against a stricter reading, or against a neighboring sentence, is not evidence against this one.
- Each sentence gets its own row. Finding one claim false changes nothing around it.
- Before replying, revert every change whose row has no evidence, and every rewording no row justifies.

## Termination

Stop when a full set of waves finds nothing incorrect. Don't run another pass over the same
evidence after that.

## Output

The reply is the text, complete and verbatim. It is unchanged when nothing was incorrect, and
otherwise carries only the fixes. Nothing else goes in the reply, except one line per claim you
couldn't verify, naming the claim and what verifying it would take.

No findings list, no per-wave report, no word counts, no preamble, no commentary on the audit, no
explanation of fixes. Never quote a failed claim back at Eli, and never write a Retractions block.
Show the complete text even when it is long or was written to a file.
