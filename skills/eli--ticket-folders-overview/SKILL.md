---
name: eli--ticket-folders-overview
description: Report what is sitting in ~/.claude/tickets/, sorted oldest first, with sizes and ages. Read-only. Use when Eli wants to see what ticket work is on disk, or to decide what to clear out.
---

# Ticket Folders Overview

Reports what is on disk under `~/.claude/tickets/`. Read-only. **This skill never deletes,
moves, or modifies anything.** Eli decides what goes; removal happens afterward, only for the
rows he names.

## Run

```bash
pwsh -NoProfile -File "$HOME/.claude/skills/eli--ticket-folders-overview/Get-TicketFolders.ps1"
```

Add `-Json` for machine-readable output when the report needs further filtering.

## Present the result

**Paste the script's output into the reply, verbatim, in a code block.** Tool output is not shown
to Eli. Reporting on a table he cannot see is worthless, and describing rows instead of showing
them has already caused one long argument over what the numbers meant.

Show every row. Do not summarize, sample, or pre-judge which folders look prunable: the point is
for Eli to see everything and choose.

| Column | Meaning |
|---|---|
| Folder | Directory name under `tickets/` |
| Age | Days since the oldest file in the folder was created |
| Created | Creation date of that oldest file |
| Size | Total on disk |
| Plan | Whether `plan.md` exists |
| Title | Ticket summary, read from the newest `ticket.json` dump |

The Title column is not optional. A bare `SW-54207` tells Eli nothing about whether a folder
matters (`talking-to-eli.md` § "Ticket numbers").

Rows are split into two sections. `pr-review-` prefixed folders are dumps from reviewing other
people's PRs and are pure byproduct, so they are listed separately from Eli's own ticket work.

## After the report

Stop. Wait for Eli to name what he wants gone. Never infer a deletion from the report alone.

**"Delete the folder" means the whole directory, everything inside it, gone.** Do not offer to
preserve `plan.md`, the git-tracked artifacts, or anything else, and do not ask which parts to
keep. A plan lives in git history, so deleting its working copy loses nothing. Offering a partial
delete invents a decision Eli did not ask for and wastes a turn.

Before deleting, confirm every named folder exists and state the count and total size. Then delete
and report what remains.
