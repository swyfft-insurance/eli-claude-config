---
name: Draft all public-facing content before posting — behavioral gate
description: Before posting ANY public-facing content, verify user has seen a draft and explicitly approved it
type: feedback
---

Before calling any tool that posts public-facing content (gh api for PR comments, slack_send_message, YouTrack comments, etc.), answer:

1. Have I shown the user a draft of the exact text?
2. Has the user explicitly approved it? ("post it", "go ahead", "yes", "send it")

If NEITHER → DO NOT POST. Show the draft first and wait for approval.

This includes:
- PR comments
- Slack messages
- YouTrack comments
- Anything else visible to others

**Why:** User wants control over what gets posted under their name. Jumping ahead and posting without approval is frustrating and can result in incorrect or unwanted content.

**How to apply:** This is a behavioral gate, not a guideline. Apply before every public-facing post. Never skip it, even if you're confident the content is correct.
