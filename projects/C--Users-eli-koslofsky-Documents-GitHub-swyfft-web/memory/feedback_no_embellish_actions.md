---
name: Don't embellish user-requested actions
description: When user says to do X, do exactly X — don't add comments, messages, or flourishes they didn't ask for
type: feedback
---

When the user tells you to perform an action (e.g., "approve the PR"), do EXACTLY that and nothing more. Do not add a body, comment, message, or any embellishment unless explicitly asked.

**Why:** User said "approve the pr" and Claude added an unsolicited review comment body. This is a violation of Rule 2 (ASK before acting) — adding scope the user didn't request.

**How to apply:** For any external action (GitHub, Slack, YouTrack), if the user doesn't specify a message/body/comment, don't add one. If you think one would be helpful, ASK first.
