---
name: PR description quality
description: Rules for writing PR descriptions — verify claims, don't include stale plan info, skip review guides for iterative commits
type: feedback
---

Never include unverified claims in PR descriptions. Specifically:
- Do NOT copy "known issues" or bug status from plan files without verifying they still apply
- Do NOT include a commit-by-commit Review Guide when commits are iterative development (fix-on-fix), not clean logical units
- The `/create-pr` skill template suggests a Review Guide for 3+ commits — ignore this when commits aren't independently reviewable

**Why:** User was embarrassed by a PR description that claimed a test was failing when it had actually been fixed, and by a review guide that made iterative fix commits look like intentional logical units.

**How to apply:** Before writing any PR description, verify every factual claim against actual test results and git state. Only include a Review Guide if commits were intentionally structured (e.g., via `/logical-commits`).
