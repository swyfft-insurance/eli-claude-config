---
name: eli--audit-standup-draft
description: Audit a written standup draft against every rule that governs it, then fact-check every line against the standup script's JSON output. Fixes violations in place and hands back the corrected draft. Mandatory before the draft is ever presented to Eli.
---

# Standup Draft Audit

Run this on every standup draft before showing it to Eli. It is the standup counterpart to
`/eli--audit-pr-desc` and `/eli--plan-audit`: mandatory, never requested, and the draft is not
presented until it passes.

**The draft is guilty until proven clean.** A rule with no recorded verdict has not been audited. If
the audit finds nothing, be suspicious of the audit.

**The corrected draft is the only output.** The audit's own findings are never shown to Eli: no
verdict table, no list of what was violated or fixed, no count of what was checked, no mention that
an audit ran. He already knows the first pass broke the rules, which is why this skill exists.
Surfacing the wreckage costs him time and tells him nothing he wants.

This skill holds the procedure only. It restates no rule, because the passes below reach every rule
in the files they walk, and a local copy would both duplicate and go stale.

## Why it exists

Two failure shapes are structural to writing a standup, and neither is something a hook can catch.

The draft is assembled from a large JSON document, so every date, stage, PR number and name in it is
a field lookup. A value taken from the wrong field reads exactly like a verified one, and Eli has no
way to tell from the draft which field it came from.

The format's rules are mostly exclusions: items the draft must leave out. An excluded item still
looks like work, so it survives by feeling like something worth reporting. Having the rules in
context does not prevent that, because the failure is never checking the draft against them.

The gate is on **presenting**, not on drafting. Showing Eli a draft this skill has not passed is the
violation.

## Invocation

```
/eli--audit-standup-draft <path-to-draft-file>
```

The draft file is required, and it is the real file on disk under `~/Desktop/standups/`. With no
arg, stop and ask. Never audit a draft that exists only in a message: the thing audited must be the
thing presented, line for line.

## 0. Resolve the format and the data source, before anything else

The format chosen in the standup skill's Step 0 decides which ruleset applies in 2b, and the two
rulesets contradict each other on purpose: the Slack format reports a merge, the Spoken format
excludes it. A wrong or assumed format collapses that part of the audit. So resolve the format and
the data before auditing anything.

1. **The format**, as Eli chose it, Slack or Spoken. Never inferred from what the draft looks like.
2. **The data**, the JSON `standup.py` wrote in this turn, as a file, by path. A recollection of what
   the JSON said is not the data.

**HARD STOP, no verdict pass, when any of these holds:**

- the draft file does not exist on disk
- the format was not stated by Eli
- the JSON is not in hand as a file

A hard stop is the one thing that does reach Eli, because it asks him for something. Say what is
missing, and nothing else.

## 1. Read the rules, with actual Read calls, in this turn

Not from memory, not from the SessionStart injection, and **not skipped because the harness says a
file is already in context.** A dedupe notice means the content is available, not that the check
happened. If a `Read` is deflected, use the content that is there and audit against it anyway.

- `~/.claude/skills/eli--standup/SKILL.md`, in full. Its Step 2, and the chosen format's section in
  its Step 3, are rules rather than guidance.
- `~/.claude/rules/standup.md`, in full.
- `~/.claude/rules/comments-docs-and-external-writing.md`, in full. A standup draft is written prose
  and the file governs it completely.
- `~/.claude/rules/slack.md`, for the Slack format.
- `~/.claude/rules/swyfft-domain.md` § "Generator and Lookup vs Config Versions", when any version
  number appears in the draft.

Then read the draft file, start to finish.

## 2. Verdict pass

Every rule gets its own verdict, recorded as you go. A rule with no verdict has not been audited, and
no pass may be waved through as "the rest are fine".

| Verdict | Means |
|---|---|
| **Satisfied** | The line of the draft that satisfies it is identified. |
| **N/A** | The reason is known. |
| **Violated** | Fix the draft, then re-check as Satisfied. |

### 2a. `standup.md` — every rule, every time

Walk it top to bottom. Every rule gets a verdict whether or not the draft touches it: the
two-sections cap, attribution to the day the work actually happened, work meaning commits and PRs
and Eli's own stage moves rather than assignments made by someone else, and the rest.

### 2b. The standup skill — Step 2, plus the chosen format's section

Every bullet in "Building the standup" and every bullet in the chosen format's section gets its own
verdict. This is where the draft fails, and the exclusions fail hardest:

- **an item the format's rules drop**, whatever it represents. A merge, a PR waiting on reviews, a
  stage transition the rules call housekeeping. "It was real work" is the argument the rule already
  answered.
- **a story appearing twice, or under the wrong day.** The day is the one the rules assign, not the
  one the most visible activity landed on.
- **the comment-traffic bullet.** Eli's own comments, Copilot review bodies and empty approvals are
  excluded by name. A bullet built from any of them is a violation, and so is a placeholder standing
  in for traffic that does not exist.
- **the bullet cap, and the ticket-ID placement.**

Two traps. A rule that excludes something is satisfied only by the thing being absent, never by the
draft mentioning it more briefly. And "the rules don't cover this item" is never an N/A on its own:
an item no rule admits does not appear.

### 2c. `comments-docs-and-external-writing.md`, plus `slack.md` for the Slack format

Walk each rule by rule. Word slop, no em-dashes, causal connectors as claims, one sentence per
subject and moment, exact terms repeated rather than varied, consistent bullet granularity, no
ambiguous references, and the tense map all apply.

The Spoken format's fragments are not an exemption from any of it.

## 3. Claim audit — every line traced to a JSON field

A separate pass over different objects. Step 2 asks whether the draft satisfies a rule; this asks
whether a line in it is true.

Every claim is **verified against a named field in the JSON**, or **deleted**. There is no third
disposition. Verified means the field's path can be written beside the claim:
`ticketDetails["SW-XXXXX"].stage`, `workItems[n].date`, `reviews[n].reviewer`. A value recalled from
reading the JSON earlier in the session is not verified.

The claims that go wrong most often:

- **A ticket's current stage.** It is `ticketDetails[ticket].stage`. A `stage_change` item's `to` is
  one transition inside the window, and the ticket has usually moved past it since.
- **When a story started and finished.** Started is `ticketDetails[ticket].developedOn`, finished is
  the `pr_opened` item's `date`. Neither is inferable from the other.
- **Whether a PR opened inside the window.** Only a `pr_opened` item proves it. `reviewOn`,
  `mergedOn` and the ticket's stage each say something else.
- **Every name, and what that person did.** Reviewers come from `reviews[].reviewer` with
  `reviews[].state`, comment authors from `comments[].author`. A finding is attributed to whoever the
  field names, and never to Eli.
- **Every characterization of what a reviewer or stakeholder raised.** It comes from the body text of
  that review or comment, or it is cut.

A claim that fails is **deleted**, never rephrased, per `comments-docs-and-external-writing.md`
§ "Fixing a failed claim means deleting it". Deleting a story's only bullet deletes the story.

Fix every violation in the draft file, then hand back the corrected draft and nothing else.
