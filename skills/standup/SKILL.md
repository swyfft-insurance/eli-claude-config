---
name: standup
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
python ~/.claude/skills/standup/standup.py
```

Timeout: 60000ms. The script gathers GitHub PRs, YouTrack issues, and YouTrack activities, then outputs structured JSON with work items already attributed to the correct days.

If the script errors, show the error and stop.

## Step 2: Format the output

The JSON contains:

| Field | Content |
|-------|---------|
| `dates` | `today`, `todayName`, `lastWorkingDay`, `lastWorkingDayName` |
| `ticketDetails` | Map of ticket ID → {summary, url, stage} |
| `workItems[]` | Each item has `date`, `type`, and type-specific fields |

### Work item types

| Type | Meaning | Key fields |
|------|---------|------------|
| `pr_opened` | Eli opened a PR on this date | `tickets`, `pr`, `prTitle`, `prUrl`, `prState`, `mergedOn`, `reviews` |
| `pr_feedback_addressed` | Eli pushed commits addressing review feedback | `tickets`, `pr`, `prTitle`, `prUrl` |
| `stage_change` | Eli changed a ticket's field | `ticket`, `ticketSummary`, `ticketUrl`, `field`, `from`, `to` |
| `active_ticket` | Ticket currently in Develop/Review | `ticket`, `ticketSummary`, `ticketUrl`, `stage` |
| `pr_in_review` | PR opened before the window, still open | `tickets`, `pr`, `prTitle`, `prUrl`, `reviews` |

### Building the standup

Group work items by date into EXACTLY two sections:

1. **Last working day** (`lastWorkingDayName`) — items where `date == lastWorkingDay`
2. **Today** (`todayName`) — items where `date == today`

For each item, create a bullet combining the ticket + PR + what happened. Use `ticketDetails` to look up ticket summaries for tickets referenced by PRs.

**Rules:**
- Merges are NOT separate bullets. If a PR was opened on the last working day and merged, just mention it was merged in the same bullet.
- `pr_feedback_addressed` = "addressed PR feedback on #XXXX" — don't over-explain.
- `stage_change` where `to` is "Develop" = "picked up" or "started developing". Where `to` is "Review" = "moved to review".
- `active_ticket` = what you're working on today.
- `pr_in_review` = mention it's still in review, note approvals from `reviews`.
- If a ticket appears in both a PR item and a stage_change, combine into one bullet.
- If no work items exist for a day, say so briefly.

## Step 3: Write the draft

Write to `~/Desktop/standups/standup-YYYY-MM-DD.txt` (today's date). Create the directory if needed.

### Slack format

- `*LastWorkingDayName*` and `*Today*` as section headers (Slack bold)
- Each bullet: ticket as Markdown link `[SW-XXXXX](youtrack_url)`, ticket summary in quotes, action, PR as link `[PR #XXXX](pr_url)`
- Concise — one line per bullet

### Spoken format

- Plain text, no links or formatting
- Each bullet: ticket number + one short phrase about what happened and status
- Don't explain what the ticket IS, just what you DID

## Step 4: Post (Slack only)

After the user explicitly approves, post to Slack channel `C06ALP0GTHV` using `mcp__slack__slack_send_message`. Do NOT post without approval.
