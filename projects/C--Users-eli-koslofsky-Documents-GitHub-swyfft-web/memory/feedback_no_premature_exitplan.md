---
name: no_premature_exitplan
description: Do not call ExitPlanMode while actively discussing the plan with the user
type: feedback
---

Do not call ExitPlanMode after every response during an active plan discussion. Wait until the user explicitly signals they're done reviewing.

**Why:** User was actively asking questions and providing feedback on the plan, and I kept trying to call ExitPlanMode after each response, which was disruptive.

**How to apply:** During plan review, focus on answering questions and updating the plan. Only call ExitPlanMode when the conversation has naturally concluded and the user hasn't asked any new questions or raised concerns.
