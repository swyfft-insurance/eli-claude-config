---
name: eli--prep-for-compact
description: Get ready for /compact. Brings the plan (or resume.md when no plan exists) up to date with everything done so far, then hands Eli the /compact command from compaction.md.
---

# Prep for Compact

The rules and the plan are in context now and won't be after the compaction. The plan is what brings
them back, so it has to be current.

1. **Bring the plan up to date.**
   - Its Progress section records every step done so far and what is outstanding, with entries made
     through `eli--generate-progress-entry`.
   - Every decision made in chat since the plan was written is in it, in Eli's words.

   **With no plan yet,** write or update `resume.md` in the ticket folder. It holds:
   - the mandatory reads: every rules file, skill and repo doc the work depends on
   - every decision, in Eli's words
   - the open questions
   - what is done and what is outstanding
2. **Hand Eli the command** from `compaction.md`, with the path filled in, in one code block.
