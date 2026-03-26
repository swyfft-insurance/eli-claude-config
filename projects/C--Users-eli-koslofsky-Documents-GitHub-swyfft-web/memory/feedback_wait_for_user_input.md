---
name: Wait when user rejects AskUserQuestion to clarify
description: When user selects "clarify" with no answer on AskUserQuestion, they are actively typing - WAIT instead of sending another question
type: feedback
---

When AskUserQuestion is rejected with "The user wants to clarify these questions" and "No answer provided", this means the user is actively trying to type their response. Do NOT immediately send another AskUserQuestion or any other tool call. Just wait silently for them to finish typing.

**Why:** Repeatedly sending AskUserQuestion while the user is typing is extremely annoying and interrupts their flow. It happened 3 times in a row and caused real frustration.

**How to apply:** After any AskUserQuestion rejection with "wants to clarify" + no answer, respond with brief text only (no tools) and wait for the user's next message.
