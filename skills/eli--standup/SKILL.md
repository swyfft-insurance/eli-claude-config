---
name: eli--standup
description: Generate a standup update based on my YouTrack and GitHub activity from yesterday and today.
---

# Standup

## Step 0: Ask standup type

Use AskUserQuestion:

> Which type of standup?
> 1. **Slack** — written update for #standup
> 2. **Spoken** — speech notes for on-camera standup

Do NOT proceed until the user answers.

## Step 1: Run the data script

```bash
python ~/.claude/skills/eli--standup/standup.py
```

Timeout: 60000ms. The script gathers GitHub PRs, YouTrack issues, and YouTrack activities, then outputs structured JSON with work items already attributed to the correct days.

If the script errors, show the error and stop.

## Step 2: Format the output

The JSON contains:

| Field | Content |
|-------|---------|
| `dates` | `today`, `todayName`, `lastWorkingDay`, `lastWorkingDayName` |
| `ticketDetails` | Map of ticket ID → {summary, url, stage, comments} — `comments` is the full comment history (any author), each `{date, author, text}`, oldest first |
| `workItems[]` | Each item has `date`, `type`, and type-specific fields |

### Work item types

| Type | Meaning | Key fields |
|------|---------|------------|
| `pr_opened` | Eli opened a PR on this date | `tickets`, `pr`, `prTitle`, `prUrl`, `prState`, `mergedOn`, `reviews` (each carries `reviewer`, `state`, `date`, `body`) |
| `pr_merged` | A PR opened before the window merged on this date | `tickets`, `pr`, `prTitle`, `prUrl`, `reviews` |
| `pr_feedback_addressed` | Eli pushed commits addressing review feedback | `tickets`, `pr`, `prTitle`, `prUrl` |
| `stage_change` | Eli changed a ticket's field | `ticket`, `ticketSummary`, `ticketUrl`, `field`, `from`, `to` |
| `active_ticket` | Ticket currently in Develop/Review | `ticket`, `ticketSummary`, `ticketUrl`, `stage` |
| `pr_in_review` | PR opened before the window, still open | `tickets`, `pr`, `prTitle`, `prUrl`, `reviews` |

### Building the standup

The rules below describe how to interpret the work items and combine them into bullets. The daily two-section layout is the **Slack format's** layout; the **Spoken format** regroups the same material story-by-story (see its section in Step 3).

Group work items by date into EXACTLY two sections:

1. **Last working day** — items where `date == lastWorkingDay`
2. **Today** — items where `date == today`

**Section header labels:** If `lastWorkingDay` is the calendar day before `today`, use "Yesterday" and "Today". Otherwise (e.g., after a weekend or holiday), use the day names from `lastWorkingDayName` and `todayName`.

For each item, create a bullet combining the ticket + PR + what happened. Use `ticketDetails` to look up ticket summaries for tickets referenced by PRs.

**Rules:**
- **MANDATORY — check comments before describing any active ticket or stage change.** Before writing a bullet for an `active_ticket` or `stage_change`, read that ticket's `comments` in `ticketDetails`. A ticket's real status (tabled, reprioritized, waiting on someone, blocked-because) frequently lives in a recent comment, not in the Stage field — a ticket sitting in Develop may actually be paused. Use the comment `date` to judge which comments are recent and relevant. If a comment changes the true status, the bullet must reflect that (e.g. "tabled X until Y is done"), not just the raw stage.
- **Comments tell you a ticket's STATUS, never what Eli did.** Check each comment's `author`. Most are written by someone else: an investigation writeup, a QA test plan, a triage note. Mine a comment for status and nothing else: tabled, blocked, superseded, waiting on someone. Never turn another author's findings into a description of Eli's work, and never restate a comment's technical detail as the day's progress. The work items are the record of what Eli did; the comments are not.
- Merges are NOT separate bullets. If a PR was opened on the last working day and merged, just mention it was merged in the same bullet.
- `pr_merged` = a PR that predates the window but merged inside it. Say it was merged (and approved, from `reviews`). If the SAME PR also has a `pr_feedback_addressed` item on that day, collapse both into ONE bullet — "addressed feedback and merged" — never two.
- `pr_feedback_addressed` = "addressed PR feedback on #XXXX" — don't over-explain.
- `stage_change`: these `to` values represent real work:
  - `to` = "Develop" → "picked up" or "started developing"
  - `to` = "Review" → "finished coding"
  - `to` = "Blocked" → "blocked" (read the ticket's `comments` in `ticketDetails` to explain why)
  - `to` = "Done" → resolved (read the ticket's `comments` in `ticketDetails` to explain why — won't fix, duplicate, not applicable, etc.)
  - All other values (Backlog, Ready for Dev, Ready for Test, Test, Tested, Failed Test) → skip. Ticket housekeeping, not coding.
  - Same-day collapse: if a ticket has BOTH a Develop and Review transition on the same day, that means the whole ticket was completed in one day. Emit ONE bullet — don't narrate both transitions as separate bullets.
  - Example: SW-49790 moves to Develop and Review on Wednesday → "SW-49790 — picked up and finished the Hadron LA EachElementOption test failure, opened PR 19974"
  - Counter-example (wrong): two separate bullets, one for "picked up" and one for "finished coding"
- `active_ticket` = ongoing work on a ticket in Develop/Review. Appears for today AND for the last working day if the ticket was already in that stage before the window (i.e., no stage transition into it during the window). Use "continued working on" for last working day, "continuing" for today.
- `pr_in_review` = mention it's still in review, note approvals from `reviews`.
- If a ticket appears in both a PR item and a stage_change, combine into one bullet.
- If no work items exist for a day, say so briefly.

## Step 3: Write the draft

Write to `~/Desktop/standups/standup-YYYY-MM-DD.txt` (today's date). The directory already exists — don't pre-check or `mkdir`, just Write.

The draft contains only the format chosen in Step 0 — never both.

**Then print the full draft verbatim in your response.** Writing the file does not show it to Eli, and neither does `cat`-ing the file back: tool output is invisible to him. The file is the artifact; the response is where he reads it.

### Slack format

- Section headers in bold (`**...**`), using the label chosen above ("Yesterday"/"Today" or the day names). The `slack_send_message` tool takes standard markdown, not Slack mrkdwn — use `**bold**` and `[text](url)` links, which the tool converts to Slack formatting on send.
- Each bullet: ticket as Markdown link `[SW-XXXXX](youtrack_url)`, ticket summary in quotes, action, PR as link `[PR #XXXX](pr_url)`
- Concise — one line per bullet

### Spoken format

**Speech notes, NOT a script.** Eli glances at these while talking, he does not read them out. Write fragments, not paragraphs.

**Two sections, same as the Slack format: last working day, then Today.** Use the day labels chosen in Step 2 ("Yesterday"/"Today", or the day names after a weekend). Those two are the only headers the file ever contains. Never add a group, bucket, or category heading of any kind.

- Under each day, one entry per story (a ticket / piece of work): a short plain-English story name on its own line, then bullet(s) for what moved that day.
- **A story appears exactly once, under the day it was picked up.** Never repeat a story under both days. Its bullets cover everything that happened across the whole window and end with where it stands now (in review, merged, continuing).
- A story picked up before the window goes under the earlier day, with the bullet saying when it actually started ("started last Tuesday").
- **Say when the story started, in the bullet.** "picked up Friday", "started today", "been going since last week". That framing is what the reader needs, and it belongs in the words, not in a heading.
- **Every story bullet says when it started and when it finished.** "Started" is the day the ticket moved to Develop, read from `ticketDetails[ticket].developedOn`, never the day the PR opened. "Finished" is the day the PR went up, read from the `pr_opened` item's `date`. A story with no PR yet has no finish; say what it is doing instead ("still going", "continuing"). `developedOn` comes from the ticket's full Stage history, so it is populated even for a story that started long before the window, and can be `null` when the transition has not happened.
- **A merge is not work, and neither is waiting for reviews.** When a story's PR went up before the window (no `pr_opened` item inside it, and `reviewOn` earlier than the window), the work finished before the window, so the merge landing inside it earns no entry at all. Overrides the `pr_merged` rule in Step 2, which is the Slack format's. Give such a story a line only when Eli pushed commits for it in the window (`pr_feedback_addressed`), and then only a one-liner about clearing review feedback.
- **The second bullet is the comment traffic since Eli picked the story up.** Two sources, summarized together in one line: ticket comments in `ticketDetails[ticket].comments` dated on or after `developedOn` and written by someone other than Eli, and the review bodies on the story's PR (`reviews[].body`). Say what the reviewer or stakeholder actually raised, in a few words. Drop this bullet entirely when there is nothing, and never write "nothing since" or any other placeholder. Eli's own comments are his own writing and are never reported back to him. A Copilot review body is a restatement of the diff, an overview paragraph plus a per-file table, so it is never comment traffic no matter how long it is. Copilot's actual findings are inline comments, which this data does not carry. An approval with an empty body is not traffic either.
- Within a day, sort by `developedOn`, earliest first. The data carries dates but not times, so same-day stories keep the order the data provides.
- Sentence fragments / shorthand only, no full prose, no narrative paragraphs
- **Two bullets per story, three at the absolute most.** These are notes Eli glances at while speaking the detail from his own memory of the work, not a briefing he reads. Say what moved and where it stands, then stop. A story that seems to need five bullets is carrying ticket content rather than work done; cut the extras.
- Plain text, no links or formatting
- **Prefix the story-name line with the ticket ID(s)**, e.g. `SW-55072 / SW-55074 - Removing the MEP acknowledgement and direct repair elements`. It is there only so Eli can answer if someone in standup asks which ticket a story is; he does not read it out. Everything after the prefix, and every bullet, stays plain English with no ticket numbers in it.
- Don't explain what the ticket IS, just what you DID

## Step 4: Post (Slack only)

After the user explicitly approves, post to Slack channel `C06ALP0GTHV` using `mcp__slack__slack_send_message`. Do NOT post without approval.
