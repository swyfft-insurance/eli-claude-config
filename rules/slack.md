# Slack

> Gate 2 applies here. See `core-behavior.md`.

- Look up ALL user IDs via `slack_search_users` BEFORE composing. Never guess.
- **Tag, don't name.** Never mention someone by plain text name in a Slack message. Always use `<@USER_ID>` to tag them.
- Messages CANNOT be deleted. If wrong, ASK the user what to do. Don't send a duplicate.
  - **What happened:** Duplicate message in group DM with CTO. Embarrassing.
- Slack uses `mrkdwn`: code blocks need blank line after ```, no markdown tables, test in DM first.
- **Hyperlink all YouTrack ticket references** using Slack mrkdwn `<https://swyfft.myjetbrains.com/youtrack/issue/SW-XXXXX|SW-XXXXX>`. Plain `SW-XXXXX` text doesn't auto-link in Slack.
- **Version ambiguity**: when a "V1"/"V2" reference could mean either a state config or a lookup, qualify with the class-prefixed shorthand. See `swyfft-domain.md` § "Generator and Lookup vs Config Versions".

## Reply where the conversation is happening

Before replying, read the recent history of the channel or DM, not just the linked message. The
reply goes where the discussion is live:

- Discussion running at top level → reply top level, even when the linked message could take a
  thread.
- Discussion already happening in a thread with replies → reply in that thread.

A linked message tells you what is being discussed. It doesn't tell you where to reply. In a DM,
the answer is almost always top level.

Every Slack draft states where it will go: top level, or in the thread under a named message. Eli
approves the destination along with the text.

- **What happened:** Patti posted a retest result top level in a DM, and the conversation was
  running top level. The reply went into a new thread under her message, and Eli had to repost it
  top level after it was sent.
