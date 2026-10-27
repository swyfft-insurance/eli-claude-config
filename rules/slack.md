# Slack

- Look up every user ID with `slack_search_users` before composing. Never guess.
- Tag people with `<@USER_ID>`, never by plain-text name.
- In a draft shown for approval, write each tag as the person's name (`@Alex Good`) and list the `<@USER_ID>` each name posts as below the draft.
- Messages can't be deleted. If one is wrong, ask Eli what to do. Never send a duplicate.
- `slack_send_message` takes standard markdown, per its tool description. A line starting `1.` opens an ordered list (Slack's markdown block docs, "Lists (ordered)"). `<url|text>` links and `<@ID>` mentions also render.- Link every ticket as `<https://swyfft.myjetbrains.com/youtrack/issue/SW-XXXXX|SW-XXXXX>`. Plain `SW-XXXXX` doesn't link.
- Cite every earlier Slack message the text relies on (a request, a decision, your own earlier post) with its permalink: `<https://swyfft.slack.com/archives/<channel>/p<ts with the dot removed>?thread_ts=<parent ts>&cid=<channel>|link text>`. `slack_read_thread` gives each message's ts.
- A message in `#dev-analytics-rater-handoff` (`C06V258BWHJ`) also follows `~/.claude/plan-types/excel-rater-plans-common.md` § "Rater edits — when warranted, and the SharePoint flow" (who to tag, the product line in the first sentence) and § "What a message to the channel is for".
- Before replying, read the channel's or DM's recent history, not just the linked message, and reply where the discussion is live: top level when it runs at top level, in the thread when it's in a thread. In a DM that is almost always top level.
- Every draft states its destination: top level, or the thread under a named message. Eli approves the destination with the text.
- The Slack MCP has no file upload, so a message with an image goes out as a Slack draft Eli finishes. Present the text with `*[screenshot]*` marking the image. On approval, create it with `slack_send_message_draft` (with `thread_ts` for a thread reply) and leave the placeholder out. Open the returned `channel_link` with `Start-Process` through the PowerShell tool. Eli drags the image in and sends it.
- Slack allows one draft per channel. On `draft_already_exists`, tell Eli and wait. The existing draft is his.
