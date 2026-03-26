---
name: standup-only-real-work
description: Don't include ticket assignments or stage moves as "work" in standups — only report actual code/effort
type: feedback
---

Tickets being assigned to you by someone else is NOT work to report in standups. But actions YOU took — like moving tickets to Develop, moving to Ready for Test, etc. — ARE real work worth reporting.

**Why:** Getting assigned a ticket is just someone else clicking a button. But deliberately picking up tickets and moving them to Develop represents starting work / planning.

**How to apply:** Check the `author` field on YouTrack activity items. If Eli made the stage change, it's reportable work. If someone else just assigned the ticket or changed a field, that's not Eli's work. Don't include tickets where the only recent activity was someone else assigning it.
