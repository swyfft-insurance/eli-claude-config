---
name: eli--pr-feedback
description: Address reviewer feedback on my PRs. Use when you need to reply to or resolve PR review comments. Raw gh api reply/resolve calls are blocked, so this skill is the only path.
---

# Address PR Feedback

Every review comment, from a person or a bot (Copilot, Claude), is a claim about the PR. This skill decides which claims hold up, brings Eli only those, makes the fixes he picks, and replies to and resolves every thread.

## Arguments

PR number (`/eli--pr-feedback 19821`). With none, use the current branch's PR without asking:

```bash
gh pr view --json number --jq .number
```

Ask only when that errors or returns more than one PR.

## Steps

### 1. Fetch

```bash
python ~/.claude/scripts/pr-feedback.py fetch <PR#>
```

Timeout 30000ms. The JSON has `unresolvedThreads` (inline threads, attached to lines) and `reviews` (top-level review bodies). A Copilot review's body is out of scope (`~/.claude/rules/pr-mine-address-feedback.md` § "Copilot reviews: inline comments only").

### 2. Research

Finish this for every comment before forming any verdict or recommendation. A recommendation is a claim about the code and needs the same evidence. There is no time pressure: never shortcut a step to get a thread off the list.

Once per PR:
- **The ticket, from the source.** Read every YouTrack ticket in the PR with `/eli--read-ticket`: the description, all comments, and any ticket it was scoped from. The ticket is the authority on what the change is for and what it guarantees. A plan, a summary or memory never stands in for it.
- **The plan**, when the ticket folder has one: its scope, its decisions in Eli's words, and the paths its tests cover. A comment the plan already decided is answered with the plan's reason.
- **The diff, fresh.** `/eli--diff branch`, every hand-written file's hunks. Skip generated files (`~/.claude/rules/pr-creation.md` § "Skip generated files by default") unless a comment targets one. A `--stat` list or an earlier read is not the diff.

Per comment:
- **The code.** The method the comment points at, its callers and its callees, read now. Every assertion about the code rests on lines just read.
- **The governing docs.** The `CLAUDE.md`/`AGENTS.md` and `.claude/rules/*.md` for the touched subsystem, found through the root `CLAUDE.md` tables. Reading a diff doesn't load path-scoped rules, so open them.
- **Every factual claim**, the reviewer's and your own, checked against code or a doc (§ "Claims").
- **Suggested alternatives**, evaluated against the real code.

### 3. Verdict

Sort each comment first:
- **Asks for nothing** (`pr-mine-address-feedback.md` § "A review comment is not automatically a request"): it gets a reply and is resolved.
- **A question**: answered in its reply from the research. A question that proposes a change ("should this also handle Y?") is a requested change and gets a verdict.
- **A claim about wording, docs, naming, tests or style**: actionable when it is true, the diff adds or changes what it's about, and something goes wrong (question 4 below).
- **A claim that the code does the wrong thing**: the four questions below.

For a wrong-behavior claim, step 2 must have verified the mechanism first. A verified mechanism is necessary, not sufficient. The comment is actionable only when all four hold, each answered with its evidence:

1. **Reachable.** The scenario can happen in production once this PR ships, on a path a user, job or caller actually takes. Name the path.
2. **Not contrived.** It doesn't need an implausible combination of conditions. Name the conditions it needs.
3. **This PR's.** The diff causes it, or the ticket's AC is unmet without the fix. Behavior the diff doesn't touch is not this PR's.
4. **Something goes wrong.** Name what a person or downstream system gets wrong: an amount charged, a document, a transaction, a screen. If nothing does, the comment fails.

A comment that fails is not actionable. Its reply says what failed and why, and the thread is resolved.

### 4. Present

Re-read this file before each message in this step. The entry shape decays within a few messages otherwise.

**The first message is the thread list:** every thread and top-level review, in fetch order, each with its verdict. The list asks for no decision. Eli can overrule any verdict in it.

```
Thread 1: <file>:<line> (@<author>)
> <comment body>
Verdict: actionable | not actionable: <what failed and why> | asks for nothing | question
```

```
Review: @<author> (<state>)
> <review body>
Verdict: ...
```

End the list with the actionable count. When it's zero, say so in one line and go to step 6.

**Then the actionable items, one per message.** Present one, stop, and wait for Eli's pick before the next. Never put two items in one message. The decision is Eli's: recommend, never decide.

Every entry has the same fields in the same order:
1. **Header:** `<file>:<line>` (@reviewer), plus "×N identical" when batched or "(reviewer replied)" when the thread has replies.
2. **Code block:** the commented lines, verbatim.
3. **Comment quote:** the reviewer's exact text, in a blockquote.
4. **Thread context**, when present: the other replies on the thread.
5. **Strongest case for the comment:** one sentence stating the concern at full strength, as if you agreed with it.
6. **Verdict:** the step 3 answers, one line each, with evidence.
7. **Recommendation:** your pick and a one-sentence reason.
8. **Options:** a lettered list. Every option is a genuinely plausible choice.

Formatting:
- One identifier per decision, in one numbering scheme. Sub-numbers (`1.1`) are fine; parallel schemes are not.
- A numbered list, never a table.
- Restructuring on request renumbers. It never strips quotes, code, thread context or option descriptions.

Eli answers one entry with one token (`1a`).

### 5. Fix

After the last pick:
1. Make every chosen fix. Each is the minimum change that resolves its comment (`pr-mine-address-feedback.md` § "A feedback fix is the minimum change that resolves the comment").
2. Build, and run the tests the fixes affect.
3. Ask once to commit and push (`~/.claude/rules/git-safety.md`). Commit, push and confirm the push. A rejected push stops the skill, and nothing is posted.

### 6. Replies

Draft a reply for every thread and top-level review, actionable or not, and show them together for approval. Each draft sits under the reviewer's verbatim text in a blockquote.
- An agreement with a fix made is one word: "Done."
- A decline, disagreement, correction or answer is a sentence or two per point, citing evidence (`comments-docs-and-external-writing.md` § "PR review prose: the shortest thing that lands the point").
- A not-actionable reply says what failed.
- A top-level reply opens by tagging the reviewer (`Responding to @ehrenw's review:`) and quotes each point it answers. An inline reply quotes only the sub-part it answers, if any.
- Never tag copilot (`pr-mine-address-feedback.md` § "Never tag copilot; post only what was approved, byte for byte").

Wait for an explicit approval. Clarifications and side comments are not approval.

### 7. Post and resolve

Post each approved body byte for byte, then resolve its thread:

```bash
python ~/.claude/scripts/pr-feedback.py reply <PR#> <comment-database-id> "<approved reply body>"
python ~/.claude/scripts/pr-feedback.py resolve <thread-graphql-id>
python ~/.claude/scripts/pr-feedback.py review-reply <PR#> "<approved reply body>"
```

`review-reply` posts a top-level review's reply on the conversation tab.

### 8. The PR description

Apply `pr-mine-address-feedback.md` § "The PR description is a snapshot of the PR as opened" to the fixes. Draft an `### After review` bullet only for a fix that meets that bar.

## Claims

- **A verified mechanism is not a verdict.** The comment is actionable only when step 3 passes.
- **Disagreement rests on verified facts.** A structural absolute ("can't happen", "impossible", "only ever", "by construction", "guaranteed") needs the mechanism that enforces it: a compile error, a type constraint, an exhaustive switch, a guard clause, a DB constraint. A not-reachable verdict names what makes it so: the code, config or data as it will stand once this PR ships.

## Reviewer shorthand

- **"IB"** is Konstantin's (`kkkmail`) shorthand for "Iron Blockhead", the AI coding agent. A comment headed "For IB:" is a reviewer's request like any other, triaged the same way, and the decision is Eli's.
