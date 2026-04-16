---
name: read-ticket
description: Read a YouTrack ticket with full description, comments, all attachments (images, logs, etc.), and custom fields. Use when you need to deeply understand a ticket before starting work.
---

# Read YouTrack Ticket

Fetches a YouTrack ticket's full context: description, all comments, custom fields, linked issues, and **downloads all attachments** (images, log files, text files, etc.) so you can view them.

## Usage

The user provides a ticket ID (e.g., `SW-49236`). If not provided, ask for one.

## Steps

### 1. Run the Python script

```bash
python ~/.claude/skills/read-ticket/read-ticket.py <ISSUE-ID>
```

Set timeout to 30000ms. The script:
- Fetches the issue via YouTrack REST API (description, custom fields, links)
- Fetches all comments (paginated)
- Downloads all attachments: images to `$TEMP/swyfft-tickets/<ISSUE-ID>/images/`, other files to `$TEMP/swyfft-tickets/<ISSUE-ID>/attachments/`
- Outputs structured JSON to stdout

### 2. Parse the JSON output

The output contains:

| Field | Content |
|-------|---------|
| `id`, `summary`, `url` | Ticket identity |
| `customFields` | Stage, Priority, IssueType, ProductLine, Carrier, RatingType, USState, Assignee, etc. |
| `description` | Full markdown description with `[IMAGE: <local_path>]` markers where screenshots appear |
| `comments[]` | Each comment with `author`, `created`, `text` (also with resolved image markers) |
| `links[]` | Linked issues with type, direction, id, summary |
| `images` | Map of `filename → local path` for all downloaded images |
| `imagesDir` | Directory containing all downloaded images |
| `attachments` | Map of `filename → local path` for all non-image attachments (logs, text files, PDFs, etc.) |
| `attachmentsDir` | Directory containing all non-image attachments |

### 3. View images in context

The script replaces `![](filename)` references with `[IMAGE: C:\...\path]` markers **inline in the text**. This tells you exactly where each image appears in the description or comment.

Walk through the description and comments in order. When you hit an `[IMAGE: path]` marker, use the **Read** tool to view that image. This way you see each screenshot in the same context the reporter intended.

### 4. View non-image attachments

Check the `attachments` map in the JSON output. For each non-image attachment:
- **Text/log files** (`.txt`, `.log`, `.csv`): Use the **Read** tool to view the file contents
- **PDF files**: Use the **Read** tool with a page range
- **Binary files** (`.xlsx`, `.zip`, etc.): Mention the file path to the user so they can open it manually

These attachments often contain critical context (SolarWinds logs, error dumps, repro data) that isn't in the ticket description.

### 5. Present the ticket

Summarize the ticket with:
- **Header**: ID, summary, URL
- **Fields**: The custom fields as a compact list
- **Description**: The full description text, describing what each inline image shows
- **Attachments**: List non-image attachments and summarize their contents
- **Comments**: Each comment with author, date, and content (including what their images show)
- **Links**: Related/duplicate/parent tickets

## Error Handling

- If the script fails with `YOUTRACK_API_TOKEN not found`, the user needs to set the environment variable
- If attachment downloads fail, the JSON will show `DOWNLOAD_FAILED: <reason>` — report this but continue with the text content
- If the script times out, try again with a longer timeout (60000ms)
