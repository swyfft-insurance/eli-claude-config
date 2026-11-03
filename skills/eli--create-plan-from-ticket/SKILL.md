---
name: eli--create-plan-from-ticket
description: Plan a YouTrack ticket. Reads every rules file, then follows plan-mode.md Part A, which reads the ticket and confirms its plan type with Eli before any other work.
---

# Create Plan From Ticket

    /eli--create-plan-from-ticket SW-XXXXX

No ticket ID: ask for it.

1. `Read` every file in `~/.claude/rules/*.md`, `plan-mode.md` included.
2. Follow `plan-mode.md` Part A. As soon as `/eli--read-ticket` returns in its step 1, rename the chat: `python ~/.claude/scripts/rename-chat.py "SW-XXXXX <verbatim YouTrack title>"`.
3. Before Part A step 5, the skill sends Eli only two messages: the Develop-move y/n when a hook blocks the move, and the plan-type message in step 4. Never present a discovery finding before step 5. A question from Eli gets its answer at any point.
4. The plan-type message takes exactly this shape:

       **SW-XXXXX "<verbatim YouTrack title>"**

       Summary:
       - <two or three bullets from the description>

       Comments:
       - <two or three bullets from the comments, or "None.">

       Open PRs:
       - <each of Eli's open PRs whose ticket duplicates or partly duplicates this one, with its ticket's verbatim title; or "None.">

       1. Plan it as a <type>?
          1a. <type> (Recommended)
          1b. Another type: you name it

5. Part A step 5's message takes exactly this shape. Write every item in full sentences, as you would say them out loud. Leave out file paths, line numbers, code history and reasons.

       **Asks:** <what the ticket wants, in one or two sentences>
       **Found:** <one sentence per discovery finding; only for types with a discovery step>
       **Change:**
       - <one sentence per thing the plan adds to Asks: how the code meets it, or work beyond it; never a restatement of Asks>
       **Tests:**
       - <one sentence per test: the behavior it proves, its level, and `<TestClass>`>

       <only a question Part A step 4 allows, as its own numbered question with lettered options>
       <N>. Is the outline above approved?
          <N>a. Approved: I write the plan (Recommended)
          <N>b. Not approved: you say what changes

6. Write the step 4 message to `~/.claude/tickets/<ticket-folder>/artifacts/plan-messages/step-4-plan-type.md` and the step 5 message to `.../step-5-outline.md`. Run `/eli--audit-msg-and-present-again <that file>` on each, and send only the text it presents.
