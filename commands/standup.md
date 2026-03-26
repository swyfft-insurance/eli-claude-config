Generate a standup update based on my YouTrack and GitHub activity from yesterday and today.

## BLOCKING: Required Tool Access

**You MUST have access to both YouTrack and GitHub before proceeding. Do NOT skip this.**

- **YouTrack**: Available via MCP deferred tools. You MUST use `ToolSearch` to load `mcp__YouTrackNative__search_issues` (and any other YouTrack tools) BEFORE calling them.
- **GitHub**: Available via the `gh` CLI.

If a tool appears missing or a call fails, use `ToolSearch` to load it. Do NOT tell the user you lack access — you DO have access. If something is genuinely broken, ASK the user before giving up.

## Step 0: Ask Which Type of Standup

**BEFORE doing anything else**, use AskUserQuestion to ask:

Question: "Which type of standup is it today?"
- **Slack standup** — "Written update posted to #standup channel"
- **Spoken standup** — "Speech notes / TLDR for on-camera standup"

Do NOT proceed to data gathering until the user answers.

## IMPORTANT: Keep It Simple

This is a quick daily task. Do NOT:
- Use the Task tool or subagents — call MCP tools and gh commands directly
- Write elaborate scripts or PowerShell to process results
- Spend more than a couple minutes gathering data
- Over-engineer the data collection

If a tool result is too large, use `--limit` or filter the query — don't write scripts to parse giant JSON files.

## Data Gathering

### Step 1: GitHub PRs + YouTrack issues (run ALL in parallel)

**GitHub — two commands:**
```
gh search prs --author=eli-swyfft --updated=">=YYYY-MM-DD" --repo=swyfft-insurance/swyfft_web --json number,title,state,createdAt,updatedAt,url --limit 30
```
```
gh pr list --author=eli-swyfft --repo=swyfft-insurance/swyfft_web --state all --json number,title,state,createdAt,updatedAt,mergedAt,url,headRefName --limit 20
```
(The first gives search results; the second gives mergedAt timestamps. Use both.)

Replace `YYYY-MM-DD` with the last working day's date (not today — to catch things updated since yesterday).

**YouTrack — TWO queries, run both:**

Query 1 — recently updated tickets:
```
assignee: me updated: {Last working day} .. {Today}
```

Query 2 — currently active tickets (catches ongoing work that may not have been updated in the window):
```
assignee: me Stage: Develop, Review
```

Use `fields: "idReadable,summary,customFields(name,value(name))"` on both to get Stage and other fields.

### Step 2: YouTrack activity timestamps (run after Step 1)

For EVERY ticket returned in Step 1, call `get_issue_activities` with `categories: "CustomFieldCategory"` and `reverse: true`, `limit: 10`.

This gives you the precise timestamps of when each ticket changed stage (e.g., moved to Develop, moved to Ready for Test). You NEED these timestamps to correctly attribute work to yesterday vs today. Convert all timestamps from ms-since-epoch UTC to US Eastern time.

### Step 3: PR details (run after Step 1, parallel with Step 2)

For each relevant PR (updated in the standup window), get body, reviews, comments, and commits:
```
gh pr view <NUMBER> --repo swyfft-insurance/swyfft_web --json body,reviews,comments,commits --jq '{body: .body[0:1000], reviews: [.reviews[] | {author: .author.login, state: .state, submittedAt: .submittedAt}], comments: [.comments[] | {author: .author.login, body: .body[0:300], createdAt: .createdAt}], commits: [.commits[] | {messageHeadline: .messageHeadline, committedDate: .committedDate}]}'
```

For PRs with inline review comments (code review feedback), also fetch:
```
gh api --method GET repos/swyfft-insurance/swyfft_web/pulls/<NUMBER>/comments --jq '[.[] | {author: .user.login, body: .body[0:300], path: .path, createdAt: .created_at}]'
```

## Step 4: STOP — Re-read rules before writing

**BEFORE writing ANY output**, re-read the "Day Attribution Rules" and the relevant "Output" section below. Large tool results push these rules out of working memory. Do NOT skip this step.

## Day Attribution Rules

- Attribute work to the day the PR was OPENED (i.e. when the code was written), NOT the day it was merged. Merging is just clicking a button and is not meaningful work to report.
- Do NOT create separate bullets for merges. If a PR was opened yesterday and merged today, it only appears under Yesterday.
- Exception: if PR review feedback was addressed the following day by pushing new commits (actual code changes, not just replying to comments), note that as work for that day (e.g. "addressed PR feedback on #18688").
- Use commit timestamps to determine which day code was actually written — all times should be interpreted as US Eastern.
- Use YouTrack activity timestamps to determine when tickets changed stage. If a ticket was moved to Develop on Tuesday but no commits exist for it on Wednesday, don't claim Wednesday work on it unless there's other evidence (comments, stage changes that day, etc.).
- NEVER move activity from one day to another to fill gaps. If there are no PRs or commits on a given day, that day's work may have been YouTrack-only (moving tickets to Develop, reading specs, planning). Report what actually happened, not what sounds better.
- Do NOT reference internal epic labels or go-live dates (e.g. "Feb 21 versioned changes"). Just describe the actual work.
- For "Today" section: report tickets currently in Develop/Review as what you're working on today. If a ticket has been in Develop since before today with no commits yet, it's still valid to list as today's plan.

## Output: Slack Standup

Write the draft to `~/Desktop/standups/standup-YYYY-MM-DD.txt` (using today's date) and show it to the user for review.

Format rules:
- Break down by Yesterday and Today. "Yesterday" means the last working day — this could be Friday (after a weekend), or even earlier if there was a holiday (e.g. Monday was Presidents' Day → "yesterday" is Friday). Use the appropriate day name as the header (e.g. *Friday* not *Yesterday*).
- Each bullet: ticket number as Markdown hyperlink (e.g. `[SW-12345](https://swyfft.myjetbrains.com/youtrack/issue/SW-12345)`), ticket title in quotes, actions taken (wrote, opened PR, still in review, currently developing, addressed PR feedback, etc.), any relevant bonus info from PR description/comments
- PR references should also be Markdown hyperlinks (e.g. `[PR #18697](https://github.com/swyfft-insurance/swyfft_web/pull/18697)`)
- Keep it concise - no over-explaining
- Use Slack formatting: `*bold*` for headers, `- ` for bullets (Slack renders these as formatted lists)

**After the user approves the draft**, post it to Slack channel `C06ALP0GTHV` using the Slack MCP `slack_send_message` tool. Do NOT post until the user explicitly approves.

## Output: Spoken Standup

Write speech notes to `~/Desktop/standups/standup-YYYY-MM-DD.txt` (using today's date).

Format rules:
- No Markdown links or formatting — just plain text
- Break down by last working day and "Today". Use the actual day name (e.g. "Friday") if it wasn't literally yesterday.
- Each bullet: ticket number + one short phrase describing the work and status
- Don't explain what the ticket IS — just what you DID and where it stands
- Don't describe the content of PR feedback — just mention that there was feedback and you're addressing it

Example:
```
Yesterday
- SW-46898: Fixed QBE NJ fee structure, merged
- SW-46838-46849: Wind mit revert across 9 states, opened PR

Today
- Wind mit PR approved by Ron, Warren, Ehren; addressing Justin's feedback
- SW-46868: Opened a defaults fix, closed it — Justin already had a PR
```
