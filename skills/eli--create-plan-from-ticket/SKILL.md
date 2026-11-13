---
name: eli--create-plan-from-ticket
description: Plan a YouTrack ticket. Reads every rules file, then follows plan-mode.md Part A, which reads the ticket and confirms its plan type with Eli before any other work.
---

# Create Plan From Ticket

    /eli--create-plan-from-ticket SW-XXXXX

No ticket ID: ask for it.

1. `Read` every file in `~/.claude/rules/*.md`, `plan-mode.md` included.
2. Follow `plan-mode.md` Part A. As soon as `/eli--read-ticket` returns, rename the chat: `python ~/.claude/scripts/rename-chat.py "SW-XXXXX <YouTrack title>"`.
3. Before the outline message, Eli gets only two messages: the Develop-move y/n when the ticket isn't in Develop yet, and the plan-type message. Never present a discovery finding before the outline message. A question from Eli gets its answer at any point.

## Plan-type message

Send it as written, in exactly this shape:

    **SW-XXXXX "<YouTrack title>"**

    Summary:
    - <two or three bullets from the description>

    Comments:
    - <two or three bullets from the comments, or "None.">

    Open PRs:
    - <each of Eli's open PRs whose ticket duplicates or partly duplicates this one, with its ticket's title; or "None.">

    1. Plan it as a <type>?
       1a. <type> (Recommended)
       1b. Another type: you name it

## Outline message

Write it to `~/.claude/tickets/<ticket-folder>/artifacts/plan-messages/outline.md`, run `/eli--audit-msg-and-present-again` on that file, and send only the text it presents. Write every item in full sentences, as you would say them out loud. Leave out file paths, line numbers, code history and reasons. Exactly this shape:

    **Asks:** <what the ticket wants, in one or two sentences>
    **Found:** <one sentence per discovery finding; only for types with a discovery step>
    **Change:**
    - <one sentence per thing the plan adds to Asks: how the code meets it, or work beyond it; never a restatement of Asks>
    **Tests:**
    - <one sentence per test: new, changed or run only, the behavior it proves, its level, and `<TestClass>`>

    <only a question `plan-mode.md` Part A step 4 allows, as its own numbered question with lettered options>
    <N>. Is the outline above approved?
       <N>a. Approved: I write the plan (Recommended)
       <N>b. Not approved: you say what changes
