---
name: GATE — PR creation safety checks
description: Behavioral gate before gh pr create — verify tickets read, diff checked, draft approved
type: feedback
---

## STOP: Before Every gh pr create

This is a behavioral gate, not a guideline. You MUST answer these before creating ANY pull request.

1. Did I read EVERY YouTrack ticket referenced in the branch name using `get_issue`?
2. Did I check the actual diff with `git diff development...HEAD`?
3. Did I read `.github/pull_request_template.md`?
4. Did I show the user a draft and get explicit approval?

If any answer is NO → DO NOT CREATE THE PR.

**If YouTrack is unavailable:** STOP and say "YouTrack is failing — are you connected to the VPN?" Do NOT guess ticket descriptions. Do NOT proceed without them. Do NOT try workarounds like gh api or WebFetch.

## PR Description Must Be Based On TWO Sources

1. **YouTrack tickets** — read EVERY ticket referenced in the branch name to get the actual summaries and descriptions
2. **Code diff** — `git diff development...HEAD` to see the actual changes being submitted

NEVER write a PR description based on memory, plan files, or assumptions alone.

## Treat the PR as ONE Diff
When drafting a PR description, look at `git diff development...HEAD` — the single combined diff. Do NOT read individual commits. Individual commits on this branch are iterative work-in-progress (fix-on-fix, trial-and-error) and do NOT represent logical units. Describing them leads to irrelevant implementation details that waste the reviewer's time. The reviewer sees ONE diff — describe what that diff does and why.

## Do NOT Blindly Follow the /create-pr Skill Template

- **Review Guide**: Do NOT include a commit-by-commit review guide unless commits were intentionally structured as logical units (e.g., via `/logical-commits`). Iterative fix-on-fix commits are NOT reviewable individually.
- **Known issues**: NEVER claim a test is failing or passing without running or checking it. Plan files go stale across sessions.
- **Claims about code**: Every bullet point must come from the actual diff, not from what you think you remember doing.

## What Happened (2026-03-13)

- Created a PR with a "known issue" claiming a migration test was failing — but that test had been fixed. Claim was copied from a stale plan file without verification.
- Included a commit-by-commit "Review Guide" for iterative fix-on-fix commits, pretending they were logical review units.
- Wrote wrong descriptions of what code changed — didn't check the diff.
- Did NOT draft for user review before posting.

## What Happened (2026-03-03)

- Created a PR with GUESSED ticket descriptions because YouTrack was temporarily unavailable (VPN disconnect).
- Should have STOPPED and asked about VPN instead of creating a garbage PR.
- User had to correct this multiple times.
