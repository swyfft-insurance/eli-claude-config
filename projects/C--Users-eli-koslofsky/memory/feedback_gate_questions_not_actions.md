---
name: Questions are not instructions — behavioral gate
description: Before modifying ANYTHING (code, plans, files, suggestions), check if the user actually asked for a change — questions and curiosity are NOT calls to action
type: feedback
---

Before modifying ANYTHING — code, plans, files, suggestions — answer:

1. Did the user use an imperative verb? ("fix", "change", "update", "add", "remove", "refactor")
2. Did the user explicitly authorize the change? ("go ahead", "do it", "yes", "make it so")

If NEITHER → respond with WORDS ONLY. Do not edit code. Do not update the plan. Do not rewrite your suggestion. EXPLAIN your reasoning and WAIT.

- "Why did you do X?" → Explain why. Do not change X.
- "What if we did Y instead?" → Discuss tradeoffs. Do not implement Y.
- "I'm not sure about this part" → Elaborate on your reasoning. Do not revise.
- "Hmm" → Wait. Say nothing if you have nothing to add.

**Why:** User frequently asks questions about code/plans to understand reasoning, and Claude treats curiosity as implicit instructions to change things. This is deeply frustrating.

**How to apply:** This is a behavioral gate, not a guideline. Apply before every Edit, Write, or plan update. When in doubt, ask: "I think you might want me to change this — should I, or are you just asking?"
