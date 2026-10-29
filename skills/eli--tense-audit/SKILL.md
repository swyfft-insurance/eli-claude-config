---
name: eli--tense-audit
description: Audit a draft's tense clause by clause. Name the world each clause describes (environment and code state), check its tense against the tense map, and fix it. Use on any YouTrack, Slack or PR draft, and on any message that describes code in more than one environment or state. Hands back only the corrected text.
---

# Tense Audit

## 1. Read the tense map, with a Read call, this turn

`Read` `~/.claude/rules/comments-docs-and-external-writing.md` § "Tense precision — don't state the future or a hypothesis as present fact", including "The tense map". A dedupe notice is not a read: use the content it points to.

## 2. One row per clause

Write the table to the ticket's `artifacts/`, or the session scratchpad when there is no ticket. It is never shown to Eli.

| Clause | Environment | Code state | Tense-map row | Required tense | Actual tense | Fix |

- **Environment**: local, dev, beta, production, or none (a fact about the code or the requirement itself).
- **Code state**: before the change, the PR as written, after it merges, after it reaches beta, after the release, or a design considered or abandoned.
- A sentence whose clauses are in different worlds becomes one sentence per world.
- A clause about an event that hasn't happened yet (a merge, a cherry-pick, a deploy, a release) takes "will", with that event named in the sentence.

## 3. Hand back the corrected text

Only the corrected text, per `talking-to-eli.md` § "An audit's only output is the fixed artifact". Fix tense and world splits only. Change no other words.
