---
audited-by: []
---

# Auditing

## Slop first, audit later

In the flow state you write slop no matter how many rules are in context, and the only path forward is slop first, audit later. A draft that will be posted or kept (code, a ticket, a PR description, a plan, a Slack or YouTrack post) gets a separate audit run before anyone sees it. That run reads the rules that govern the draft with actual Read calls, checks the draft against them, and fixes it in place.

- A draft with an audit skill goes through that skill.
- A draft with no audit skill gets the separate run against the rules file that governs it.
- A kind of draft that keeps coming back wrong gets its own audit skill. Every new audit skill gets a row in § "The audit skills" when it is created.

## The audit skills

One row per audit skill.

| What it audits | Skill | Hands back |
|---|---|---|
| A code diff, at code-complete | `/eli--code-complete-audit` | the fixed code |
| A plan file | `/eli--plan-audit` | the fixed plan |
| A PR description | `/eli--audit-pr-desc` | the fixed description |
| A ticket draft | `/eli--audit-ticket-draft` | the fixed draft |
| Manual-QA instructions | `/eli--audit-manual-qa-instr` | the fixed instructions |
| A standup draft | `/eli--audit-standup-draft` | the fixed draft |
| The claims in any writing | `/eli--fact-check-writing` | the fixed text |
| A draft's tense | `/eli--tense-audit` | the fixed text |
| The wording of the last message to Eli | `/eli--word-slop` | the rewritten message |
| The questions in the last message to Eli | `/eli--ask-properly` | the message with its questions formatted |
| The last message to Eli, through every audit that applies | `/eli--audit-msg-and-present-again` | the fixed message, or a retraction |
| Quote-def overrides | `/eli--quote-def-override-audit` | findings |
| A ByPeril audit-doc failure | `/eli--audit-doc-mismatch-investigation` | findings |
| A diff, before or after its PR opens | `/review-pr` | findings |
| A batch of PRs | `/eli--review-prs-parallel` | findings |

## An audit's only output is the fixed artifact

An audit whose row hands back a fixed artifact hands back only that artifact: no verdict tables, counts, violation lists, or mention that an audit ran. Only two things reach Eli: a hard stop (what's missing) and a retraction (what's actually true, without reprinting the failed claim). An audit whose row hands back findings reports them.
