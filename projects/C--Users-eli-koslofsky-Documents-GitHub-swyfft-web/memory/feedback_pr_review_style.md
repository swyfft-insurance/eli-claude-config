---
name: PR review style preferences
description: User only comments on fundamental bugs and red flags — no nits, no style comments, no minor suggestions
type: feedback
---

When reviewing PRs, only draft comments for things that are truly fundamental bugs or red flags. Specifically:

- **Comment on**: Behavioral changes that could be unintentional regressions, logic bugs, missing test coverage for critical paths, design divergences from the ticket that need discussion
- **Don't comment on**: Style nits (#region, blank lines, naming), minor code suggestions, "nice to have" improvements, things that are technically correct but could be slightly better

**Why:** User doesn't want to be a "nit" reviewer. Nit comments waste the author's time and create noise. The goal is to catch real problems, not polish.

**How to apply:** When drafting PR review comments, filter aggressively. If a finding wouldn't block the PR or cause a production issue, don't comment on it.
