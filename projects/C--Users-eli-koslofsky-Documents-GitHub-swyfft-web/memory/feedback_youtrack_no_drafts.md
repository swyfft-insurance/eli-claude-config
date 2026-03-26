---
name: YouTrack - use create_issue not create_draft_issue
description: Always use create_issue to publish tickets directly — never create_draft_issue which creates invisible drafts requiring manual publishing
type: feedback
---

Always use `mcp__YouTrackNative__create_issue`, never `mcp__YouTrackNative__create_draft_issue`.

**Why:** User asked to create a ticket, I used create_draft_issue, then when questioned I created a second ticket with create_issue — resulting in a duplicate. The draft tool exists but should never be used when the intent is to create a real ticket.

**How to apply:** When asked to create a YouTrack ticket, go straight to `create_issue`. The draft tool has no practical use in our workflow.
