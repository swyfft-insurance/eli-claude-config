---
name: GATE — Always read memory before acting
description: Before ANY external action or multi-step task, read MEMORY.md and relevant memory files first
type: feedback
---

Before doing ANYTHING non-trivial, the **first step** is: read MEMORY.md and relevant memory files.

This applies to:
- Plan Mode plans
- Creating PRs, YouTrack tickets, Slack messages
- Committing code
- Writing memories (draft in response text first, show user, get approval)
- Any multi-step workflow

**Why:** Claude repeatedly makes mistakes already documented in memory. The system only works if loaded before acting.

**How to apply:** Read memory → then act. No exceptions.
