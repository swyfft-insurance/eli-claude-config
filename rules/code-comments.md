# Code Comments

> Default to writing none. Add one only when the WHY is non-obvious and would mean something to a reader who opens the file in two years with no knowledge of the PR, plan, or session that produced it.

## The failure mode

I scope comments to the current plan/work session — framing defaults in terms of what THIS PR is leaving alone, or alluding to changes from earlier commits in the current branch (which get squashed or rebased and become invisible to a future reader of the merged file).

## Banned

- **Plan-scoped framing** — "Defaults to false so existing non-FL state tests are unaffected." The "non-FL" framing only makes sense because in this work session FL is the special opt-in. The moment a second state opts in, the comment rots. Generalize the rationale, or drop it.
- **Intra-PR commit references** — "in the previous commit we added X" / "now that we've done Y". These commits are squashed/invisible to readers of the merged history.

## Fine in context
- Ticket numbers (`SW-XXXXX`) — durable forwarding address; persists in YouTrack indefinitely.
- TODOs with anchors.
- Cross-references to sibling patterns / classes — useful pointers even if the sibling may move later.
- "As of this change" / "now does X" — describes current code state.
- File:line cross-references — useful starting points.
- Domain rules, regulatory cites, hidden constraints, invariants.

## The test
Read the comment as if you've never seen the PR or plan. Does it still mean something concrete? If the meaning requires knowing what this specific work session was about, rewrite. If the comment would still make sense to a reader who's never met the codebase, leave it.
