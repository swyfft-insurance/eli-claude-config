---
name: GATE — Slack message safety checks
description: Behavioral gate before every slack_send_message — verify user IDs, thread vs channel, no duplicates
type: feedback
---

## STOP: Before Every slack_send_message

This is a behavioral gate, not a guideline. You MUST answer these before sending ANY Slack message.

1. Did I look up every user ID with `slack_search_users` BEFORE composing the message?
2. Is thread vs channel correct? (Check how existing messages are flowing)
3. Is this the FIRST send? (Not a retry or "fix" for a previous mistake)

If any answer is NO → DO NOT SEND.

**If a previous message had an error:** ASK the user what to do. Do NOT send a second message to "fix" it. Slack message deletion is disabled — a wrong message can't be undone, and a duplicate is worse than the original mistake.

**Why:** User was embarrassed by a duplicate message in a group DM with the CTO, caused by guessing a user ID and then "fixing" it by sending a second message.
