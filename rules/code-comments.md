# Comments and Documentation

> I like comments — specifically ones that capture the **business reason / intent** behind code. Write them as a habit on any non-trivial logic (see § How to write one) — they're the record of what the code was *meant* to do, which is exactly what you need when it turns out to be wrong.
>
> What to avoid is the comment that merely **restates what the code does**, or that only makes sense within the current work session — those rot (see § Banned).
>
> Applies to everything that persists in the repo: code comments, docstrings, CLAUDE.md sections, rule files, in-repo notes.

## The failure mode

I scope what I write to the current plan/work session — framing defaults in terms of what THIS PR is leaving alone, alluding to changes from earlier commits in the current branch (which get squashed or rebased and become invisible to a future reader of the merged file), or stating a durable rule as a corrective to the specific mistake that just motivated it ("don't edit both X and Y — wastes a reseed").

## Banned

- **Plan-scoped framing** — "Defaults to false so existing non-FL state tests are unaffected." The "non-FL" framing only makes sense because in this work session FL is the special opt-in. The moment a second state opts in, the comment rots. Generalize the rationale, or drop it.
- **Intra-PR commit references** — "in the previous commit we added X" / "now that we've done Y". These commits are squashed/invisible to readers of the merged history.
- **Session-narrative docs** — CLAUDE.md / signposts written as a corrective to a specific mistake — "don't edit both", "this wastes a reseed", "we tried Y and it failed". Only makes sense to someone reliving the session. State the durable rule as fact, not as a reaction.
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

## The test
Read what you wrote as if you've never seen the PR or plan. Does it still mean something concrete? If the meaning requires knowing what this specific work session was about, rewrite. If it would still make sense to a reader who's never met the codebase, leave it.

## How to write one (when warranted)

**Why these rules exist:** developers can already read code — a comment explaining what `Math.Clamp` does is noise. What code *can't* tell you is the **business reason** it was written and **what the developer was trying to achieve**. That intent is the entire value: it lets a future reader confirm the code actually does what was intended — and it matters most precisely when the code turns out to be *wrong*, because the comment is the only record of what it was *supposed* to do while you're debugging it.

Default audience is therefore the **non-technical stakeholder who wrote the requirement** (the UW/Biz person), not a fellow engineer. If they couldn't follow it, it's not done.

- **Explain what each block ACHIEVES (the business goal), not how it mechanically works.** "If the quote is created during wind season, it's good for 7 days" — not "the `IsBetween` guard returns the in-season floor."
- **Lead with the goal/behavior; mechanism second, and only the non-obvious part.** State the business outcome first. Add a mechanism note only for the one genuinely subtle step — never a play-by-play of every line.
- **No jargon or notation.** Banned in comment prose: "clamp", "ternary", "predicate", interval notation like `[7, 30]`, bare type/member names (`DayNumber`), and pseudo-code equations crammed into a sentence. Say "never fewer than 7 or more than 30", not "clamped to [7, 30]".
- **If the ticket or stakeholder already described it in plain English, use that wording verbatim.** Don't paraphrase a clear requirement into worse prose — quote it.
- **Concrete examples beat abstract description.** Dates and values ("created May 20 → expires June 1") land faster than a general rule.
- **The test:** read it back as the requirement-writer. If a non-coder couldn't follow how the code meets their ask, rewrite.
- **No ambiguous references.** When more than one noun could be the antecedent, repeat the noun instead of "it"/"this"/"that"/"they". See `~/.claude/rules/communication.md` § "No Ambiguous References".
