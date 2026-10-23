---
name: eli--create-plan-from-ticket
description: Plan a YouTrack ticket. Reads every rules file, then follows plan-mode.md Part A, which confirms the ticket's plan type with Eli before anything else.
---

# Create Plan From Ticket

    /eli--create-plan-from-ticket SW-XXXXX

No ticket ID: ask for it.

1. `Read` every file in `~/.claude/rules/*.md`, `plan-mode.md` included.
2. Follow `plan-mode.md` Part A. Its step 2 confirms the type with Eli as a y/n before anything else.
