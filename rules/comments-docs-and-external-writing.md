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

## Call things by their exact name — repeat it, don't vary it

Name each thing by its exact term and repeat that exact term every time you mean it. Never swap in a synonym, a broader category word, or a vaguer umbrella term to avoid repetition. Varying vocabulary so prose doesn't feel repetitive ("elegant variation") is a creative-writing habit; in technical writing the substitute is always less precise than the exact term, so it trades accuracy for style and manufactures ambiguity. Repeating the precise term is correct — not a flaw to fix.

Broader than "No Ambiguous References" above: that rule bans pronouns and demonstratives when two or more antecedents are in scope. This rule bans the synonym or umbrella swap even when nothing is ambiguous, because the vaguer word is still less precise than the exact term.

Applies to all prose: chat replies, code and doc comments, CLAUDE.md, rule files, commit messages, PR descriptions, Slack, YouTrack, RCAs.

| Bad (term varied) | Good (exact term repeated) |
|---|---|
| "a change could re-rate existing business; that business keeps its premium" | "a change could re-rate existing quotes and policies; those quotes and policies keep their premium" |

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

Applies to all prose: chat, comments, RCAs, YouTrack/Slack, PR descriptions.
