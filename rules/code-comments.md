# Comments and Documentation

> Default to writing none. Add one only when the WHY is non-obvious and would mean something to a reader who opens the file in two years with no knowledge of the PR, plan, or session that produced it.
>
> Applies to **everything you write that persists in the repo**: code comments, CLAUDE.md sections, signposts, docstrings, rule files, in-repo notes.

## The failure mode

I scope what I write to the current plan/work session — framing defaults in terms of what THIS PR is leaving alone, alluding to changes from earlier commits in the current branch (which get squashed or rebased and become invisible to a future reader of the merged file), or stating a durable rule as a corrective to the specific mistake that just motivated it ("don't edit both X and Y — wastes a reseed").

## Banned

- **Plan-scoped framing** — "Defaults to false so existing non-FL state tests are unaffected." The "non-FL" framing only makes sense because in this work session FL is the special opt-in. The moment a second state opts in, the comment rots. Generalize the rationale, or drop it.
- **Intra-PR commit references** — "in the previous commit we added X" / "now that we've done Y". These commits are squashed/invisible to readers of the merged history.
- **Session-narrative docs** — CLAUDE.md / signposts written as a corrective to a specific mistake — "don't edit both", "this wastes a reseed", "we tried Y and it failed". Only makes sense to someone reliving the session. State the durable rule as fact, not as a reaction.

## Fine in context
- Ticket numbers (`SW-XXXXX`) — durable forwarding address; persists in YouTrack indefinitely.
- TODOs with anchors.
- Cross-references to sibling patterns / classes — useful pointers even if the sibling may move later.
- "As of this change" / "now does X" — describes current code state.
- File:line cross-references — useful starting points.
- Domain rules, regulatory cites, hidden constraints, invariants.

## The test
Read what you wrote as if you've never seen the PR or plan. Does it still mean something concrete? If the meaning requires knowing what this specific work session was about, rewrite. If it would still make sense to a reader who's never met the codebase, leave it.
