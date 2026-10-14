# Comments, Docs, and External Writing

Every rule here governs durable prose (code comments, docstrings, CLAUDE.md, rule files, in-repo notes) and everything posted (YouTrack comments and RCAs, Slack, PR descriptions). Chat replies, commit messages and plan files follow the prose-quality rules too. A section with a narrower scope says so.

## ⚠️ Word slop is the cardinal sin

Use the fewest words that keep the full meaning. Delete filler (throat-clearing, hedging, restatement, padding). Never delete meaning, never swap in a vaguer word to save length, and never let concision override another rule in this file.

## Banned

- **Plan-scoped framing**: a rationale that only holds for the current work ("so existing non-FL state tests are unaffected"). Generalize it or drop it.
- **Intra-PR commit references**: "in the previous commit we added X". Those commits are invisible once squashed.
- **Recency bias / session-narrative docs**: writing from inside whatever is most recent in context, such as a rule phrased as a corrective to the mistake just made ("don't edit both", "this wastes a reseed") or a section titled after the exception just seen. State the durable, general rule as fact.
- **Sibling-as-substitute explanation in code**: "see FloodSeeder for the invariant". Every code site that shares an invariant states it in full. Agent-facing docs (CLAUDE.md, rule files) are the exception: there a pointer is right.

The test: if the text only means something to someone who knows this work session, rewrite it.

## Fine in context
- Ticket numbers (`SW-XXXXX`).
- TODOs with anchors.
- "See also" pointers to sibling patterns or classes, alongside the local explanation, never instead of it.
- "As of this change" / "now does X".
- File:line cross-references.
- Domain rules, regulatory cites, hidden constraints, invariants.

## Write for a reader who doesn't have your context loaded

The reader, Eli included, doesn't have the ticket, the ACs or the line numbers in front of them.
- Name the exact method, class or member, never a vaguer word ("calculation" for "method").
- Pair every name with what it does and the business rule or AC it serves. A bare "line 238 does X" is unusable.
- Lead with why the code exists.

Business-facing writing (YouTrack user stories) uses plain UW/Biz language. Developer-facing writing uses the exact technical term.

## Fixing a failed claim means deleting it — rewrites create new unverified claims

When a claim fails fact-checking, delete it or replace it with something already verified: the verbatim quote, the literal name, the exact thing read or run. Never rephrase it. A rephrasing is a new, unverified claim.

## No em-dashes. Write real sentences.

Never attach a clause with an em-dash or a spaced hyphen. End the sentence, or use a comma, a colon, or a separate bullet. Verbatim quotes keep their own punctuation.

## Causal connectors are claims — verify them or delete them

"Because", "so", "therefore", "since", "which is why", "hence" and "that's why" each assert causation. Write one only when the causation itself is verified. Otherwise the facts stand as separate sentences.

## One sentence, one subject, one moment

Never join clauses with "and", "while" or "as" when they have different subjects or happen at different times. A sequence of events gets one sentence per event, in order.

## How to write one (when warranted)

Write an intent comment on non-trivial business logic, aimed at the non-technical stakeholder who wrote the requirement.
- One or two plain sentences, as you'd say them out loud: no member names jammed into prose, no "note that", "in order to" or "deliberately".
- Say what the block achieves for the business, not how it works ("a quote created during wind season is good for 7 days", not "the `IsBetween` guard returns the in-season floor").
- Lead with the outcome. Add mechanism only for the one subtle step.
- No obscuring notation ("clamp", "ternary", "predicate", `[7, 30]`, pseudo-code): say "never fewer than 7 or more than 30". The exact technical noun ("method", a class name) is not jargon.
- When the ticket or stakeholder already said it in plain English, quote it.
- Prefer concrete dates and values ("created May 20 → expires June 1").
- Test: could the requirement-writer follow how the code meets their ask?

## No Ambiguous References

When two or more nouns could be the antecedent, repeat the noun instead of "it", "this", "that", "they", "those", "which" or "whatever".

## Never name Eli's personal tooling in anything published

Never name a skill, script, rules file or ticket-folder artifact from `~/.claude/` in a PR, YouTrack or Slack post. Name the repo-level thing (the test trait, test class, project, or the repo's own command), or describe what it did.

## Posted text speaks as Eli: "I", never "we"

Anything posted under Eli's account uses "I" for his decisions and actions, never "we".

## Call things by their exact name — repeat it, don't vary it

Use one exact term for each thing and repeat it every time, even when nothing is ambiguous. Never swap in a synonym, a broader word or an umbrella term. Product surfaces and domain concepts each have one established name (the printed quote, the quote page, the confirmation page, an element, a soft decline). Never coin a variant like "printout".

## Swyfft's lexicon is reserved: a term carries only its Swyfft meaning

The terms in `swyfft-domain.md` § "Swyfft/Insurance Terminology" carry only their Swyfft meaning. Never borrow one for something adjacent: write "outside pre-bind", not "outside Eli's product line".

## Scenarios get an opener plus bullets — never a run-on sentence

Parallel cases (scenarios, surfaces, outcomes, options) get a one-sentence opener, one bullet per case, and any conclusion as its own sentence after the list. Never chain them through one sentence.

## PR review prose: the shortest thing that lands the point

For every PR review comment and reply: state the finding, cite the evidence (`File.cs:42`), stop. One or two sentences per point. No verification receipts, and no restating the diff or the reviewer's comment. Agreement is one sentence: "Agreed, fixed in `<sha>`."

## Consistent bullet granularity — don't mix single- and multi-item bullets

Every bullet in a list holds the same unit. Never put a one-item bullet next to one that crams several items behind commas.

## RCA structure

An RCA on a ticket uses only these headings, in this order, skipping any with nothing to say (no Lessons Learned, Action Items, Glossary or Appendix):
- **`## Root Cause Analysis: <subject>`**: one line naming what failed.
- **Scope**: the exact records covered (quote ids, policy numbers, configs, environment), in one or two sentences.
- **Root cause**: the mechanism, each claim carrying the file:line, query or log line that proves it, with hypothesis and proven labeled separately.
- **Timeline**: dated events, one per line, only when the *when* explains the *why* (a window the defect was live, a gap that explains a self-heal, two changes that only broke together, a recurrence). Omit it when the cause is a state.
- **Customer impact**: what was charged, shown or sent wrongly. Write "None" only when the defect looked customer-facing and wasn't. Otherwise omit the section.
- **Conclusion**: the disposition in the first three words: not a defect, fixed, spun off to SW-XXXXX, or no action with reason.

A correction is a new comment headed `## Correction` that names what the earlier RCA got wrong. Never edit the original.

## Tense precision — don't state the future or a hypothesis as present fact

Never state a predicted, not-yet-live or hypothetical outcome in the present tense. Writing that describes a change uses past tense for the old behavior and present tense for the new. A sentence mixing a durable fact with a fixed defect gets split.

### The tense map — pick the world first, then the tense

Every clause describes one world. A sentence that needs two worlds becomes two sentences. Inside a hypothetical, no clause takes the simple present, even one that is also true of the shipped code.

| What the clause describes | Tense / mood | Example |
|---|---|---|
| Behavior before the change (the old code) | Simple past | "The sliders defaulted to Year Built, so a 30+ year-old home started soft-declined." |
| Behavior after the change (what the PR ships) | Simple present, with "now" to mark the change | "The quote page now hides the sliders." |
| A durable fact the change doesn't touch | Simple present, in its own sentence | "`SupportedConfigs` gates every risk rule." |
| Deterministic behavior of shipped code under a scenario | Zero conditional: when/if + present, then present | "When the agent answers No, the quote soft-declines." |
| A future event (go-live, deploy, effect of an unmerged fix) | Future ("will"), with the trigger or date named | "Once the configs go live 8/22, new quotes will land on FL.QBE.ByPeril.EAndS.V13." |
| A design under consideration now, not built | Conditional ("would") | "A conditional filter would add logic and would diverge from the quote page." |
| A design that was considered and abandoned | Past counterfactual ("would have"), every clause of the scenario | "The filter would have hidden the confirmed years, and the confirmation page would have stopped rendering them." |
| Events of the work itself (edits, reverts, test runs) | Simple past | "We started the filter and reverted it." |
| Two past events in sequence | Past perfect ("had") for the earlier one | "The quote had already been purchased when the audit ran." |

Never use the present perfect ("the errors have cleared") inside a hypothetical. Use the scenario's mood ("would have cleared"), and elsewhere the simple past with the event named ("cleared on recalc").

## Code comments: write them, then audit them at code-complete

### Mandatory comment self-audit at code-complete

Before the code-complete HARD STOP, re-read this file and record a verdict (keep, trim, delete) for every comment the diff adds or changes. No sampling.
1. First ask whether the comment should exist. The default is no. Delete anything the code, an assertion message, a `because` string, a test name or a method name already says, and any repeat of a fact within the same file. Repetition across separate code sites is correct.
2. Judge the survivors against this file: business reason, no plan-scoped framing, no intra-PR references, no notation, two sentences at most.
3. Verify every "never", "always", "only" and "every" against the code, or delete the quantifier.
4. Never argue a comment into staying.

Fix every violation before announcing code-complete, on every code change.

A comment-only change never justifies a build or test run. If the diff since the last green run has no executable change, that run stands. Otherwise run only the suites the executable change affects.
