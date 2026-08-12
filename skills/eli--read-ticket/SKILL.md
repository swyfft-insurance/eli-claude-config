---
name: eli--read-ticket
description: Read a YouTrack ticket with full description, comments, all attachments (images, logs, etc.), and custom fields. Use when you need to deeply understand a ticket before starting work.
---

# Read YouTrack Ticket

Fetches a YouTrack ticket's full context: description, all comments, custom fields, linked issues, and **downloads all attachments** (images, log files, text files, etc.) so you can view them.

**Read `~/.claude/rules/youtrack.md` § "A ticket is its description, comments, and attachments,
together" before presenting anything.** It governs how the output below is read: the AC is often in
a comment or an attachment, a later comment overrides the description, and comment order matters.

## Usage

The user provides a ticket ID (e.g., `SW-49236`). If not provided, ask for one.

## Steps

### 1. Run the Python script

```bash
python ~/.claude/skills/eli--read-ticket/read-ticket.py <ISSUE-ID> [TICKET-FOLDER]
```

Set timeout to 30000ms. The script:
- Fetches the issue via YouTrack REST API (description, custom fields, links)
- Fetches all comments (paginated)
- Fetches field-change history (Stage transitions, reassignments, priority changes)
- Downloads all attachments into a timestamped dump under the ticket's folder: `~/.claude/tickets/<TICKET-FOLDER>/artifacts/ticket-dumps/<timestamp>/` (images in `images/`, other files in `attachments/`). `<TICKET-FOLDER>` is optional — it defaults to the issue ID, so a first read lands in `tickets/<ISSUE-ID>/…`; pass an existing plan folder's name to co-locate the dump with that ticket's work.
- Outputs structured JSON to stdout

### 2. Parse the JSON output

The output contains:

| Field | Content |
|-------|---------|
| `id`, `summary`, `url` | Ticket identity |
| `customFields` | Stage, Priority, IssueType, ProductLine, Carrier, RatingType, USState, Assignee, etc. |
| `description` | Full markdown description with `[IMAGE: <local_path>]` markers where screenshots appear |
| `comments[]` | Each comment with `author`, `created`, `text` (also with resolved image markers) |
| `fieldHistory[]` | Field-change history — each with `on`, `author`, `field`, `from`, `to` (Stage transitions, reassignments, priority changes) |
| `tags[]` | Tag names on the ticket |
| `links[]` | Linked issues with type, direction, id, summary |
| `images` | Map of `filename → local path` for all downloaded images |
| `imagesDir` | Directory containing all downloaded images |
| `attachments` | Map of `filename → local path` for all non-image attachments (logs, text files, PDFs, etc.) |
| `attachmentsDir` | Directory containing all non-image attachments |

### 3. View images in context

The script replaces `![](filename)` references with `[IMAGE: C:\...\path]` markers **inline in the text**. This tells you exactly where each image appears in the description or comment.

Walk through the description and comments in order. When you hit an `[IMAGE: path]` marker, use the **Read** tool to view that image. This way you see each screenshot in the same context the reporter intended.

### 4. View non-image attachments

Check the `attachments` map in the JSON output. Every attachment gets read. An attachment left
unopened is context the reporter deliberately attached and you ignored.

- **Text/log files** (`.txt`, `.log`, `.csv`): the **Read** tool.
- **PDF files**: **Read** with no `pages` argument. That path hands the PDF over natively —
  rendered pages plus text, tables intact — and needs no external binary. This is the default for
  any PDF of 10 pages or fewer, which is most attachments.
    - **Over 10 pages**, `pages` is required (max 20 per call). Don't read 100 pages blind:
      `pdftotext -layout "<file>" - | grep -n "<term>"` to find the page, then Read that range.
      Extracted text is a *locator*, never the read itself — it interleaves multi-column tables
      into wrong label/value pairs and drops every embedded image and screenshot.
    - **`pdftoppm is not installed`** means poppler is missing, or Claude Code's PATH predates its
      install. Install: `winget install --id oschwartz10612.Poppler`. Already installed → restart
      Claude Code so the process inherits the new PATH. Never report the error as a result; a
      no-`pages` Read still works meanwhile.
- **Excel/binary** (`.xlsm`, `.xlsx`, `.zip`): give the user the path. A rater workbook goes through
  the sanctioned dump path only (`~/.claude/rules/excel-rater-plans-common.md`).

These attachments often contain critical context (SolarWinds logs, error dumps, repro data) that isn't in the ticket description.

### 5. Present the ticket

Summarize the ticket with:
- **Header**: ID, summary, URL
- **Fields**: The custom fields as a compact list
- **Description**: The full description text, describing what each inline image shows
- **Attachments**: List non-image attachments and summarize their contents
- **Comments**: Each comment with author, date, and content (including what their images show)
- **Field history**: Notable field changes (e.g. Stage transitions, reassignments), when relevant
- **Links**: Related/duplicate/parent tickets

## Error Handling

- If the script fails with `YOUTRACK_API_TOKEN not found`, the user needs to set the environment variable
- If attachment downloads fail, the JSON will show `DOWNLOAD_FAILED: <reason>` — report this but continue with the text content
- If the script times out, try again with a longer timeout (60000ms)
- A tool failure is not a result to report. The reader wants the attachment's contents; why a binary
  was missing is worth nothing to them. Fix the tool or change methods until you have the content.
  Only report something as unread after exhausting the alternatives, naming what you ran.
