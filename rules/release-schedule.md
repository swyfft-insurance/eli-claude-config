---
audited-by: [code-complete]
---

# Release Schedule

## The weekly schedule

Beta is cut from `development` on Tuesday by end of day Pacific, with rare exceptions. Beta goes to prod on Friday night. Code merged to `development` from Wednesday through Tuesday reaches beta that Tuesday and prod that Friday. The schedule almost never slips. The exceptions are hotfixes and a rare skipped release week, such as Thanksgiving. #tech-announcements (`C022SJ0M65P`) posts every beta and prod deploy with its time.

On Sunday the weekly refresh replaces the dev and beta databases with copies of prod, which deletes every record created there since the previous refresh. `Swyfft.LogMonitor/Services/SuppressionRules/NonProdRefreshWindowDatabaseReadOnlyRule.cs` holds the refresh's observed hours, and it notes that the job does not run every week.

## Code already shipped

To date when code reached prod:
1. **Check whether it was hotfixed.** Look at the base branch of every merged PR for its ticket (`gh pr list --state merged --search <ticket>`). A hotfix PR into `master` reached prod when #tech-announcements posted its deploy. A cherry-pick into `beta` after the cut reached prod that Friday.
2. **Otherwise, follow § "The weekly schedule"** from its merge into `development`. For a change merged on a Tuesday, #tech-announcements shows whether it beat that day's beta merge.
