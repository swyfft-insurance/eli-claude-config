# YouTrack

- Use `create_issue`, never `create_draft_issue`. Drafts cause duplicates.
- Read ALL custom fields (Carrier, USState, ProductLine, RatingType) — they scope the work.
- Read tickets FIRST before exploring code. Bug tickets contain error messages with the root cause.
  - **What happened:** Wasted 20+ min exploring code when ticket description had the exact error.
- `IssueType` field (not `Type`). Valid values: Feature, Bug, Support, Epic, Inquiry. No "Task".
- API returns `.youtrack.cloud:443` URLs — always convert to `swyfft.myjetbrains.com/youtrack/` for user-facing links.
- Use `youtrack-write-ticket` skill before writing ticket content.
- search_issues returns INTERNAL IDs (2-XXXXX). Call get_issue to get idReadable (SW-XXXXX).
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
- **Activity history (field changes)**: The YouTrack MCP has no `get_issue_activities` tool. Use the REST API directly:
  ```
  YOUTRACK_TOKEN=$(powershell -NoProfile -Command "[System.Environment]::GetEnvironmentVariable('YOUTRACK_API_TOKEN', 'User')")
  curl -s -H "Authorization: Bearer $YOUTRACK_TOKEN" \
    "https://swyfft.myjetbrains.com/youtrack/api/issues/ISSUE-ID/activities?fields=id,timestamp,author(login,name),added(name),removed(name),field(name)&categories=CustomFieldCategory&\$top=20"
  ```
  Timestamps are ms-since-epoch UTC.
  - **What happened:** Set Stage to Done without overriding Release Stage on SW-48843, making it look like we released code to prod.
