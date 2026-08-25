---
name: eli--generate-progress-entry
description: Append a timestamped row to a plan's Progress table, reading the time from the clock or from the artifact the row describes. Use for every Progress entry — never hand-write a row, and never type a timestamp.
---

# Generate Progress Entry

Appends one row to the Progress table in `~/.claude/tickets/<TicketFolder>/plan.md`.

**You do not supply the time.** You supply what happened; the script sources the time. There is no
time parameter, which is the whole point of the skill: a timestamp you type is a timestamp you
invented. Your context carries the date but never the clock.

## Run

```
pwsh -NoProfile -File "$HOME/.claude/scripts/Add-ProgressEntry.ps1" -TicketFolder "<folder>" -Entry "<what happened>"
```

When the entry describes work that produced an artifact, name it. The artifact's own timestamp is
when the work actually happened, which the clock at write-time is not — a test suite that ran twenty
minutes ago gets its own time, not this moment's:

```
-ArtifactPath "<path to a file the work wrote — a test log, a seed log, a ticket dump>"
-CommitSha "<sha>"
```

`-ArtifactPath` and `-CommitSha` are mutually exclusive. With neither, the script uses the current
local time, which is right for an entry about a decision rather than a run.

`-CommitSha` reads `git log`, so run it from inside the repo.

## What the row says

The `Entry` text is prose about outcomes, per `~/.claude/rules/plan-mode.md` § "Keep a Progress record
in the plan": what completed, what the result was, and any deviation from the plan. Not a restatement
of the step's title.

## Never

- Hand-write a Progress row with Edit or Write. The table is this script's output.
- Pass a time. There is no parameter for one.
- Infer a time by continuing the sequence from the row above. That is the specific failure this skill
  exists to stop: once one row is real, the next one feels like arithmetic rather than a fact.

## The plan only needs the heading

The script owns the whole table. Given `## Progress` with nothing under it, the first run writes the
header and separator itself. A missing heading is the one thing it throws on, because guessing where
Progress belongs in a plan is worse than failing.
