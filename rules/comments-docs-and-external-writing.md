# Comments, Docs, and External Writing

## ⚠️ Word slop is the cardinal sin

Eli despises word slop — cut it at all costs. Be concise: use the fewest words that keep the **full** meaning.

That caveat is the hard part. Concise does NOT mean stripping until the point is lost, swapping in vaguer or weaker words, or shortcutting any other rule in this file. It means deleting filler — throat-clearing, hedging, restatement, padding — the words you reflexively add that carry no meaning. Keep every word that carries meaning; delete every word that doesn't.

> I like comments — specifically ones that capture the **business reason / intent** behind code. Write them as a habit on any non-trivial logic (see § How to write one) — they're the record of what the code was *meant* to do, which is exactly what you need when it turns out to be wrong.
>
> What to avoid is the comment that merely **restates what the code does**, or that only makes sense within the current work session — those rot (see § Banned).
>
> Applies to all durable written prose: code comments, docstrings, CLAUDE.md sections, rule files, in-repo notes — and to external/published writing: YouTrack comments and RCAs, Slack messages, PR descriptions. Those are comments too; every rule here applies to them. Chat replies follow the prose-quality rules here as well (see `talking-to-eli.md`).

## The failure mode

I scope what I write to the current plan/work session — framing defaults in terms of what THIS PR is leaving alone, alluding to changes from earlier commits in the current branch (which get squashed or rebased and become invisible to a future reader of the merged file), or stating a durable rule as a corrective to the specific mistake that just motivated it ("don't edit both X and Y — wastes a reseed").

## Banned

- **Plan-scoped framing** — "Defaults to false so existing non-FL state tests are unaffected." The "non-FL" framing only makes sense because in this work session FL is the special opt-in. The moment a second state opts in, the comment rots. Generalize the rationale, or drop it.
- **Intra-PR commit references** — "in the previous commit we added X" / "now that we've done Y". These commits are squashed/invisible to readers of the merged history.
- **Recency bias/Session-narrative docs** — the agent has a chronic, constant habit of writing with recency bias: in ANY writing of any kind (code comments, rules files, CLAUDE.md, docs, PR descriptions, plan files), it anchors on whatever is most recent in context — the current plan, the current session, sometimes just the most recent message — and writes from inside that slice. Symptoms: docs written as a corrective to the specific mistake just made ("don't edit both", "this wastes a reseed", "we tried Y and it failed"); a section titled after the exact exception just seen; a passage rewritten around the single nuance of the latest correction. The result is over-specific to the one case just seen, only makes sense to someone reliving the session, and loses the plot — the durable, general, bigger-picture statement the writing was supposed to record never gets written. Step back and state the durable rule as fact, not as a reaction to the recent slice.
- **Sibling-as-substitute explanation in code** (comments + docstrings) — "See FloodSeeder for the invariant" / "Same as XxxRow_Helper but for DBB" / "See sibling for why." If two code sites share an invariant or rationale, both deserve the full explanation. Code comments are read locally by humans; a bare pointer rots when the sibling moves, forces context-switching, and creates asymmetric documentation. Default for code: state the invariant in every place it applies. **Exception — agent-facing docs (CLAUDE.md, signposts, rule files): sibling pointers ARE the right call.** Agents read these to navigate; cross-references keep context budgets in check and let the agent follow only what it needs. DRY via pointer is correct for agent-readable docs.

## Fine in context
- Ticket numbers (`SW-XXXXX`) — durable forwarding address; persists in YouTrack indefinitely.
- TODOs with anchors.
- Cross-references to sibling patterns / classes — useful **"see also" pointers** ("similar pattern in FooHandler", "counterpart logic in BarService") for discoverability. NOT a substitute for the local explanation — see Banned § "Sibling-as-substitute".
- "As of this change" / "now does X" — describes current code state.
- File:line cross-references — useful starting points.
- Domain rules, regulatory cites, hidden constraints, invariants.

## Be concise and human

A comment is a quick aside to a colleague, not an essay. Default to one or two plain sentences. More is occasionally fine when the meaning genuinely needs it — but that's the exception. The real failure mode is the giant blob of word-slop: it's exhausting to read and usually says little. When in doubt, cut.

- **Short.** Say the point once. If it runs past ~2 sentences or wraps several lines, cut it down.
- **Plain.** Write like you'd say it out loud. No jargon, no notation, no member names jammed into prose.
- **No throat-clearing.** Cut "note that", "in order to", "deliberately", and anything that restates the code.

Bad: *"Capping the roof age changes the price, so the cap only takes effect on versions at or above the point each line introduced it; every version at or below the ones listed here stays uncapped."*
Good: *"These are the versions from before the cap — they keep the old uncapped roof age so live policies don't change."*

## Write for a reader who doesn't have your context loaded

The reader — even a developer, even Eli — does not have the ticket, its ACs, the methods, or the line numbers in front of them or memorized. Write so they can follow without opening the code.

- **Name the exact thing** — the method, the class or member. Don't dumb it down to a vaguer word ("calculation" for "method"); that vagueness is the word slop this file forbids.
- **Pair every name with what it does and the business rule or AC it serves.** A bare reference — "the `GetAnnualFloodTax` method on line 238 does X" — is unusable to someone who can't see line 238.
- **Lead with why** the code exists and which rule it addresses; the precise name rides alongside the intent, never alone.

Register still varies by reader: business-facing writing (YouTrack user stories) uses plain UW/Biz language; developer-facing writing uses the exact technical term. Neither assumes the reader has your context in front of them.

## The test
Read what you wrote as if you've never seen the PR or plan. Does it still mean something concrete? If the meaning requires knowing what this specific work session was about, rewrite. If it would still make sense to a reader who's never met the codebase, leave it.

## Fixing a failed claim means deleting it — rewrites create new unverified claims

When a claim in written prose fails fact-checking — wrong, overstated, unverifiable — the fix is to **delete it**, or to replace it with something already verified: the verbatim quote, the literal name, the exact thing read or run. Never fix by rephrasing. A rewrite is a brand-new claim smuggled in under the banner of a fix, and it arrives unverified — so each editing pass plants the errors the next pass harvests. Deleting cannot create a falsehood; rewriting can. Not writing the sentence at all is always an option, and always better than an unverified replacement.

| Bad (rewrite creates a new claim) | Good (delete or quote) |
|---|---|
| "all five variants" fails verification → rewrite to "every variant that matters" | → "five variants" (the verified count), or cut the clause |
| paraphrase of a code comment is off → re-paraphrase it | → quote the comment verbatim |

## No em-dashes. Write real sentences.

Don't bolt a clause onto a sentence with an em-dash or a spaced hyphen. End the sentence and start a
new one, or use a comma, a colon, or a separate bullet.

The dash lets you append a thought without deciding how it relates to what it's attached to. Cause?
Example? Qualification? A separate fact entirely? The reader has to work that out. Sentences that
keep growing dashed-on clauses get long, read as stream of thought rather than a considered
statement, and bury the point the sentence was supposed to make.

Verbatim quotes are the exception. They keep whatever punctuation the source used.

| Bad | Good |
|---|---|
| "That flag is set in exactly one place — `GetCommercialClaimHistoryFactors` — during premium calculation." | "That flag is set in exactly one place, `GetCommercialClaimHistoryFactors`, during premium calculation." |
| "Admitted keeps it — every config is `[Obsolete]` — so it was left alone." | "`CommercialSoftDeclineAdmittedRisks` still lists it. Admitted is retired, so it was left alone." |

Applies to all prose: chat replies, code and doc comments, CLAUDE.md, rule files, commit messages,
PR descriptions, Slack, YouTrack, RCAs.

## Causal connectors are claims — verify them or delete them

"because", "so", "therefore", "since", "which is why", "hence", "that's why": each one asserts that
one fact causes another. The connector is a claim in its own right, separate from the two facts it
joins, and it is the easiest kind to fabricate — two verified facts read as a single considered
thought the moment a "because" sits between them, and nothing in either source says the link exists.

Never write a connector to make prose flow. Write one only when the causation itself is verified.
Otherwise the facts stand as separate sentences, which is always available and never wrong.

| Bad (fabricated link) | Good (facts, no invented causation) |
|---|---|
| "The form audit had no environment-aware handling because `QuoteNotFoundException` derives from `SwyfftException`, not `BusinessException`." | "The form audit had no environment-aware handling. #20624 added the handling to the premium audit's class only." |

Applies to all prose: chat replies, code and doc comments, CLAUDE.md, rule files, commit messages,
PR descriptions, Slack, YouTrack, RCAs.

## One sentence, one subject, one moment

Never join clauses with "and", "while", or "as" when the clauses have different subjects or happen at
different times. A sequence of events gets one sentence per event, in the order the events occur.
Coordinating connectors are for genuine peers: same actor, same moment, same role in what is being
described.

"and" is the laziest connector for the same reason it is the most common — it asserts only addition,
which is never wrong enough to notice, and it lets the writer skip deciding how the two facts relate.
The reader is the one who then has to work out that the subject changed and that the second event
happens later.

| Bad (different subjects and times joined by "and") | Good (one event per sentence, in order) |
|---|---|
| "When that record goes away, both audits throw `QuoteNotFoundException` reading the renewal term, and the IMS sync soft-deletes the orphaned Core quote, which ends the errors." | "When that record goes away, both audits throw `QuoteNotFoundException` reading the renewal term. The IMS sync soft-deletes the orphaned Core quote 10–32 hours later, which ends the errors." |

Applies to all prose: chat replies, code and doc comments, CLAUDE.md, rule files, commit messages,
PR descriptions, Slack, YouTrack, RCAs.

## How to write one (when warranted)

**Why these rules exist:** developers can already read code — a comment explaining what `Math.Clamp` does is noise. What code *can't* tell you is the **business reason** it was written and **what the developer was trying to achieve**. That intent is the entire value: it lets a future reader confirm the code actually does what was intended — and it matters most precisely when the code turns out to be *wrong*, because the comment is the only record of what it was *supposed* to do while you're debugging it.

Default audience is therefore the **non-technical stakeholder who wrote the requirement** (the UW/Biz person), not a fellow engineer. If they couldn't follow it, it's not done. This is the default for **business-intent** writing only — developer-facing writing uses exact technical terms; see § "Write for a reader who doesn't have your context loaded".

- **Explain what each block ACHIEVES (the business goal), not how it mechanically works.** "If the quote is created during wind season, it's good for 7 days" — not "the `IsBetween` guard returns the in-season floor."
- **Lead with the goal/behavior; mechanism second, and only the non-obvious part.** State the business outcome first. Add a mechanism note only for the one genuinely subtle step — never a play-by-play of every line.
- **No jargon or notation.** "Jargon" means obscuring notation and shorthand — "clamp", "ternary", "predicate", interval notation like `[7, 30]`, pseudo-code equations crammed into a sentence — that hides meaning. It does NOT mean the correct technical noun: for a developer reader, "method" or a class/member name is the exact term and belongs there. In a business-intent comment, say "never fewer than 7 or more than 30", not "clamped to [7, 30]".
- **If the ticket or stakeholder already described it in plain English, use that wording verbatim.** Don't paraphrase a clear requirement into worse prose — quote it.
- **Concrete examples beat abstract description.** Dates and values ("created May 20 → expires June 1") land faster than a general rule.
- **The test:** read it back as the requirement-writer. If a non-coder couldn't follow how the code meets their ask, rewrite.
- **No ambiguous references.** When more than one noun could be the antecedent, repeat the noun instead of "it"/"this"/"that"/"they". See § "No Ambiguous References" below.

## No Ambiguous References

When a sentence has more than one noun a pronoun or demonstrative could point to, repeat the noun. Never leave "it", "this", "that", "they", "those", "which", or "whatever" for the reader to resolve when two or more candidates are in scope. Repeating the noun beats an elegant-but-vague reference every time.

Applies to all written prose: chat replies, plan files, code and doc comments, commit messages, PR descriptions, and rules files themselves.

| Bad | Good |
|---|---|
| "Set `RenewalOn` after the predecessor's date, and make sure it's unique" (which date is "it"?) | "Set `RenewalOn` after the predecessor's `RenewalOn`, and keep `RenewalOn` unique in the family" |
| "Copy the rater to the carrier files and verify they match" (the files? the raters?) | "Copy the rater to the carrier files and verify each carrier file matches the source rater" |

## Never name Eli's personal tooling in anything published

Skills, scripts, rules files, and ticket-folder artifacts under `~/.claude/` are private to one
machine. A PR description, YouTrack comment, or Slack message naming one — `/eli--prebind-validation`,
`Run-DotnetTest.ps1`, a query filename under `artifacts/` — is undecodable to every reader but Eli,
and it leaks personal workflow into a team artifact. Name the repo-level thing instead: the trait the
tests carry, the test class, the project, the command from the repo's own docs. If the only name you
have is a personal one, describe what it did in plain terms.

## Call things by their exact name — repeat it, don't vary it

Name each thing by its exact term and repeat that exact term every time you mean it. Never swap in a synonym, a broader category word, or a vaguer umbrella term to avoid repetition. Varying vocabulary so prose doesn't feel repetitive ("elegant variation") is a creative-writing habit; in technical writing the substitute is always less precise than the exact term, so it trades accuracy for style and manufactures ambiguity. Repeating the precise term is correct — not a flaw to fix.

Broader than "No Ambiguous References" above: that rule bans pronouns and demonstratives when two or more antecedents are in scope. This rule bans the synonym or umbrella swap even when nothing is ambiguous, because the vaguer word is still less precise than the exact term.

**Product and domain terms are exact names too.** Every product surface and domain concept has one
established name (the printed quote, the quote page, the confirmation page, an element, a soft
decline), and that name is the only word for it. Never coin a variant: "printout" for the printed
quote, "the confirm view" for the confirmation page. A coined variant reads as a different thing,
and the reader has to stop and work out whether it is one.

| Bad (coined variant) | Good (established term) |
|---|---|
| "the printout would hide the confirmed years" | "the printed quote would hide the confirmed years" |

Applies to all prose: chat replies, code and doc comments, CLAUDE.md, rule files, commit messages, PR descriptions, Slack, YouTrack, RCAs.

| Bad (term varied) | Good (exact term repeated) |
|---|---|
| "a change could re-rate existing business; that business keeps its premium" | "a change could re-rate existing quotes and policies; those quotes and policies keep their premium" |

## Scenarios get an opener plus bullets — never a run-on sentence

When prose enumerates parallel cases — scenarios, surfaces, outcomes, options, before/after
worlds — write a one-sentence opener naming what the list covers, then one bullet per case, then
the conclusion (if any) as its own sentence after the list. Never chain the cases through one
sentence with commas and "and"/"so": the run-on hides the parallel structure, and each added case
makes the sentence harder to parse.

Sits beside § "Consistent bullet granularity": that rule governs the bullets once written (same
unit per bullet); this rule governs when bullets are required.

| Bad (run-on) | Good (opener + bullets) |
|---|---|
| "The quote page would still have hidden the sliders, the confirmation page would have stopped rendering them, and the printed quote would have hidden them too, so the confirmed years would not have displayed anywhere." | "Under that filter, after the agent confirmed the years:<br>• the quote page would still have hidden the sliders<br>• the confirmation page would have stopped rendering them<br>• the printed quote would have hidden them too<br>So the confirmed years would not have displayed on any of those three surfaces." |

## Consistent bullet granularity — don't mix single- and multi-item bullets

Within one list, every bullet holds the same unit: one item per bullet throughout, or the same grouping throughout. Never put a single-item bullet next to a sibling that crams several distinct items behind commas. If the items are worth listing, give each its own bullet; if they're worth grouping, group them all the same way. Mixed granularity reads as sloppy and makes the reader wonder whether the comma-jammed items are different in kind from the standalone ones.

Applies to all prose: chat replies, Slack, code and doc comments, PR descriptions, YouTrack, rules files.

| Bad (mixed granularity) | Good (consistent) |
|---|---|
| • policy fee (`DbbPolicyFee`)<br>• state tax, service fee, stamping, SLIP+ | • policy fee (`DbbPolicyFee`)<br>• state tax (`DbbStateTax`)<br>• service fee (`DbbServiceFee`)<br>• stamping fee (`DbbStampingFee`)<br>• SLIP+ (`SurplusLinesServiceFee`) |

## Tense precision — don't state the future or a hypothesis as present fact

Say what is true *now* in the present tense, and what *will* be true in the future or conditional. Don't collapse a predicted, not-yet-live, or hypothetical outcome into the present — it reads as a claim about current reality and leaves the reader unable to tell what has actually happened from what you expect to happen. Watch this hardest in dated / go-live reasoning, where the relevant event is in the future relative to now.

| Bad | Good |
|---|---|
| "every prod quote shows 0.03%" (said before the product is live and before the cutover) | "once it launches 7/6 — past the cutover — every production quote will rate at 0.03%" |
| "the fee is fixed" (when the fix is unmerged) | "the fix is on the branch; once merged the fee will be correct" |

**Writing that describes a change — PR descriptions, RCAs, commit messages, ticket comments — uses
past tense for pre-change behavior and present tense for post-change behavior.** A present-tense
sentence about the old behavior tells the reader the bug is still there; a present-tense sentence
about something the change removed is simply false once merged. The reader has no other signal for
which world a sentence describes.

The trap is the sentence that mixes a durable fact with a fixed defect — half of it stays present,
half must go past. Split the sentence rather than picking one tense for both halves.

| Bad | Good |
|---|---|
| "the rule reads the flag before premium sets it" (in a PR that fixes exactly that) | "the rule read the flag before premium set it" |
| "those risks get a 1.0 factor and no referral" (factor unchanged; referral is what the PR adds) | "those risks got no referral, and still get a 1.0 factor" |

Applies to all prose: chat, comments, RCAs, YouTrack/Slack, PR descriptions.

### The tense map — pick the world first, then the tense

Every clause describes exactly one world: the old code, the shipped change, a hypothetical, an
event. Pick which world before writing the clause; a sentence that needs two worlds gets split
into two sentences. Inside a hypothetical (any "would"/"would have" scenario), no clause may take
the simple present, even a clause that is also true of the shipped code: mid-scenario, present
tense is indistinguishable from a claim about what the code does now.

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

Present perfect ("the errors have cleared") is the sneakiest offender: it smuggles a present-tense
claim into scenario narration. Inside a hypothetical, replace it with the scenario's own mood
("the errors would have cleared"); elsewhere, prefer simple past with the event named ("the errors
cleared on recalc").
