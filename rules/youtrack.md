# YouTrack

- Use `create_issue`, never `create_draft_issue`. Drafts cause duplicates.
- Read ALL custom fields (Carrier, USState, ProductLine, RatingType) — they scope the work.
- Read tickets FIRST before exploring code. Bug tickets contain error messages with the root cause.
  - **What happened:** Wasted 20+ min exploring code when ticket description had the exact error.
- `IssueType` field (not `Type`). Valid values: Feature, Bug, Support, Epic, Inquiry. No "Task".
- API returns `.youtrack.cloud:443` URLs — always convert to `swyfft.myjetbrains.com/youtrack/` for user-facing links.
- Use `youtrack-write-ticket` skill before writing ticket content.
- search_issues returns INTERNAL IDs (2-XXXXX). Call get_issue to get idReadable (SW-XXXXX).
- Closing as not applicable / won't fix: set Stage to "Done", then set Release Stage to "NA". Moving to Done auto-sets Release Stage to "Production", so you must explicitly override it to "NA" afterward.
  - **What happened:** Set Stage to Done without overriding Release Stage on SW-48843, making it look like we released code to prod.
