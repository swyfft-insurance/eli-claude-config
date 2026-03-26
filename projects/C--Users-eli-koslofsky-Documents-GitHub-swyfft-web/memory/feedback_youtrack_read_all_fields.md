---
name: Always read all YouTrack custom fields
description: When reading YouTrack tickets, examine ALL custom fields (Carrier, USState, ProductLine, RatingType, etc.) — they scope the work
type: feedback
---

When reading a YouTrack ticket, always examine and call out ALL custom fields, not just summary and description. The custom fields contain critical scoping information:

- **USState**: Which state(s) the work applies to
- **Carrier**: Which carrier (QBE, BSIC, Hiscox, etc.)
- **ProductLine**: HO, Commercial, Flood
- **RatingType**: E&S, Admitted
- **Platform**: Internal, External
- **Assignee**, **QA Assignee**, **Business Owner**, etc.

**Why:** These fields define the scope of the work. The description may say "change the threshold" without qualifying it, but the Carrier/State/ProductLine fields tell you exactly which configs are affected. Ignoring them leads to wrong assumptions (e.g., assuming a change is global when it's state-specific).

**How to apply:** When referencing ticket details in plans or discussions, list out the relevant custom fields explicitly. Use them to determine scope before making implementation decisions.
