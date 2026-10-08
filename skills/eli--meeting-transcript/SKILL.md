---
name: eli--meeting-transcript
description: Pull a Teams meeting transcript through the Microsoft 365 connector and save it to disk as the raw .vtt plus a compact speaker-turn .md. Use when Eli names a meeting ("yesterday's standup", "the SOV meeting on 10/6") and wants its transcript, or wants work done from what was said or decided in a meeting.
---

# Meeting Transcript

Finds a Teams meeting on Eli's calendar, reads its transcript through the Microsoft 365 connector,
and saves it. Works for meetings someone else organized, as long as the meeting is on Eli's
calendar.

## Inputs

- **Meeting**: a subject, or part of one, and optionally a date. No date means the most recent past
  occurrence.
- **Ticket folder** (optional): a folder name under `~/.claude/tickets/`. Pass it when the meeting
  belongs to a ticket being worked.

## Steps

### 1. Load the connector tools

They are deferred. Load them with ToolSearch:
`select:mcp__claude_ai_Microsoft_365__outlook_calendar_search,mcp__claude_ai_Microsoft_365__read_resource`

If ToolSearch finds only `mcp__claude_ai_Microsoft_365__authenticate`, the connector is signed out.
Ask Eli to run `/mcp` and select **claude.ai Microsoft 365**, then wait.

### 2. Find the event

`outlook_calendar_search` with:

- `query`: the subject
- With a date: `afterDateTime` that date, `beforeDateTime` the next day
- Without a date: `afterDateTime` "30 days ago", `beforeDateTime` "now", `order` "newest"
- `limit`: 5

One clear match: use it. Several candidates: list them numbered, with subject, start time and
organizer, and ask which.

### 3. Get the transcript URL

`read_resource` on the event's `uri`, then take `meetingTranscriptUrl` from the result.

Never edit `meetingTranscriptUrl`. For a recurring meeting it carries `start` and `end` parameters
that scope it to this occurrence. Without them the connector returns the series' most recent
transcripts.

No `meetingTranscriptUrl` means the event is not a Teams meeting. Stop and say so.

### 4. Read the transcript

`read_resource` on `meetingTranscriptUrl`. The result is JSON: `meeting`, plus `transcripts[]` whose
`content` holds the WebVTT.

- **Ignore `meeting.startDateTime`.** For a recurring meeting it can be years old. The script dates
  the transcript from the occurrence.
- **403 `GraphAccessToTranscriptsDisabled`**: Graph access to transcripts is turned off for the
  tenant. Bob turned it on 2026-10-07 with
  `Set-CsTeamsMeetingConfiguration -EnableGraphTranscriptAccess $true -EnableAttributedTranscripts $true`.
  If the error comes back, tell Eli. Retrying won't help.
- **No transcript content**: the meeting wasn't transcribed. Stop and say so.

### 5. Save it

Pass `--uri` the string given to `read_resource`, character for character:

```bash
python ~/.claude/skills/eli--meeting-transcript/save-transcript.py --uri "<meetingTranscriptUrl>" [--ticket-folder <TicketFolder>]
```

The connector returns the transcript inline, so there is no file to copy. The script finds that
`read_resource` call in the session log under `~/.claude/projects/` and writes its result to disk
exactly as Microsoft returned it. Never write the transcript out by hand. Retyping it costs tokens
and can change the text.

Output folder:

- With `--ticket-folder`: `~/.claude/tickets/<TicketFolder>/artifacts/meetings/<date>-<subject>/`
- Without: `~/.claude/meetings/<date>-<subject>/`

| File | Content |
|------|---------|
| `transcript.vtt` | The WebVTT exactly as returned |
| `transcript.md` | One paragraph per speaker turn: `[offset] **Speaker:** text` |
| `source.json` | Subject, transcript URL, and the session log the script read |

When the result holds more than one transcript, the files are numbered: `transcript-1.vtt`,
`transcript-2.vtt` and so on.

On failure the script exits non-zero and prints `{"error": ...}`. Report the error verbatim.

### 6. Report

Give Eli:

- The meeting's subject, date and organizer
- The output folder path
- The speakers from the script's `speakerTurns`, flagging any `@N` label

Then stop. Don't summarize the meeting or pull out decisions unless Eli asks.

## Speaker labels can be wrong

The labels are Teams' attribution. In the 2026-10-07 Unified Dev Standup:

- Phil's update was labeled `@1`, meaning Teams didn't attribute it to anyone.
- Ken called on Laurel, and the cues that followed were labeled `Joe Nichols`.

When a quote or decision depends on who said it, check the label against the conversation (who was
called on, who is answering) and say when the speaker is inferred.
