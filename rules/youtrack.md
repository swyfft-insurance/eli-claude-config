# YouTrack

> Gate 2 applies here — see `core-behavior.md`.

- Match implementation detail to ticket type:
  - **User stories / behavioral features**: WHAT and WHY only — requirement, business reason / constraint, acceptance criteria. No code samples, file paths, class names, internal mechanisms, or named refactors. Implementation details belong in the plan file or PR description; they rot the moment the code changes. Tickets are read by Biz, UW, QA, and devs across teams — none need the implementation surface.
  - **Bugs**: code pointers help the dev start the investigation — file paths, methods, line numbers, SolarWinds log queries.
  - **Technical refactors / specific implementation tickets**: code references are warranted — the ticket itself is about the technical change.
  - **What happened:** Behavioral-feature draft included code samples and implementation mechanics. Flagged as overstepping Agile discipline.
- Use `create_issue`, never `create_draft_issue`. Drafts cause duplicates.
- Read ALL custom fields (Carrier, USState, ProductLine, RatingType) — they scope the work.
- Read tickets FIRST before exploring code, always via the /eli--read-ticket skill — it returns the full ticket (description, all comments, custom fields, attachments). get_issue/get_issue_comments are blocked by the pretooluse hook; /eli--read-ticket is the only ticket-read path. Bug tickets contain error messages with the root cause.
  - **What happened:** Wasted 20+ min exploring code when ticket description had the exact error.
- `IssueType` field (not `Type`). Valid values: Feature, Bug, Support, Epic, Inquiry. No "Task".
- API returns `.youtrack.cloud:443` URLs — always convert to `swyfft.myjetbrains.com/youtrack/` for user-facing links.
- **Version ambiguity**: when a "V1"/"V2" reference could mean either a state config or a lookup, qualify with the class-prefixed shorthand. See `swyfft-domain.md` § "Generator and Lookup vs Config Versions".
- search_issues returns INTERNAL IDs (2-XXXXX). To read one, pass that ID straight to /eli--read-ticket — it resolves the internal ID and returns idReadable along with the full ticket. (get_issue is blocked; /eli--read-ticket is the only ticket-read path.)
- When a ticket contains a SolarWinds log search URL, extract and use those exact search terms. Don't paraphrase or invent your own query.
  - **What happened:** Paraphrased "did not match" as "mismatch", got zero results, and confidently claimed the bug was fixed when it wasn't.
- Closing as not applicable / won't fix: set Stage to "Done", then set Release Stage to "NA". Moving to Done auto-sets Release Stage to "Production", so you must explicitly override it to "NA" afterward.
- **Release Stage "NA"**: The MCP tool's schema doesn't include "NA" as a valid Release Stage value, so `update_issue` will reject it. Use the YouTrack command API instead:
  ```
  YOUTRACK_TOKEN=$(powershell -NoProfile -Command "[System.Environment]::GetEnvironmentVariable('YOUTRACK_API_TOKEN', 'User')")
  curl -s -X POST -H "Authorization: Bearer $YOUTRACK_TOKEN" -H "Content-Type: application/json" \
    -d '{"query":"Release Stage NA","issues":[{"idReadable":"SW-XXXXX"}]}' \
    "https://swyfft.myjetbrains.com/youtrack/api/commands"
  ```
  HTTP 200 with empty `{}` body = success.
- **Activity history (field changes)**: Included in the /eli--read-ticket output as `fieldHistory` (Stage transitions, reassignments, priority changes — each with `on`, `author`, `field`, `from`, `to`). No separate call; the raw `/api/issues/{id}/activities` REST read is blocked like every other ticket read, and /eli--read-ticket is the source.
  - **What happened:** Set Stage to Done without overriding Release Stage on SW-48843, making it look like we released code to prod.
