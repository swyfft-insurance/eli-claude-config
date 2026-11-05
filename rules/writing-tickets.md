# Writing Tickets

## Writing tickets

- Everything in a ticket above its `## Technical Details` section says what and why only: the requirement or what went wrong, the business reason, and the AC or Expected Result. Biz, UW, QA and developers across teams read tickets, and most of them never need the implementation. Implementation detail also goes stale the moment the code changes.
- Most tickets have no `## Technical Details` section. A ticket gets one only when a code pointer is essential to acting on it, or when it is a tech debt ticket whose whole subject is the code. Code pointers (file paths, methods, line numbers, SolarWinds queries) go only in that final section.
- Everything above `## Technical Details` comes from the ticket's source material: the reporter's words, the requester's message, the meeting, the email, or Eli's ruling.
- Custom fields (Carrier, USState, ProductLine, RatingType) cover what the ticket asks for.
- Use `create_issue`, never `create_draft_issue`.
- Attach every dump, log, output and screenshot a ticket relies on when filing it. Never point at a file on a dev machine. If something can't be attached yet, the ticket isn't ready to file. Capture an artifact the moment it turns up, before drafting: Windows deletes crash dumps, and older log entries get overwritten.
- Name a person in a YouTrack comment or description by tagging them (`@login`), never by plain-text name.
- Never put an `@mention` in a heading. Put it on its own line below.
- A ticket never carries an open question. Resolve every question before drafting, from the source material, the code, a skill built for it (`/go-live-dates` turns an effective date into go-live dates), or Eli. A question only the business owner can answer goes to Eli first, and the draft waits for the answer.

## Tag Eli's tech debt tickets `technical debt`

A ticket Eli files for his own refactor, test-infrastructure or tooling work gets the `technical debt` tag at creation, listed in the create draft with the custom fields. His work views split on it (`tag: {technical debt}` and `tag: -{technical debt}`). A ticket filed for the business, such as one with a Business Owner, never gets it.

## Eli's own tickets start assigned to him, at Ready for Dev

A ticket Eli files for himself is created with Assignee `eli.koslofsky` and Stage Ready for Dev, both shown in the create draft. `youtrack_batch.py` sets that Stage on every create assigned to him.
