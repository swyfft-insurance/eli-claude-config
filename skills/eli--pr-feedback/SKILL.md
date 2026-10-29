---
name: eli--pr-feedback
description: Address reviewer feedback on my PRs. Use when you need to reply to or resolve PR review comments. Raw gh api reply/resolve calls are blocked, so this skill is the only path.
---

# Address PR Feedback

Every review comment, from a person or a bot (Copilot, Claude), is a claim about the PR. This skill decides which claims hold up, brings Eli one thread at a time with its verdict and reply, makes the fixes he picks, and replies to and resolves every thread.

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
- **Asks for nothing** (`pr-mine-address-feedback.md` § "A review comment is not automatically a request"): an inline thread gets a reply and is resolved. A top-level review gets no reply (step 4).
- **A question**: answered in its reply from the research. A question that proposes a change ("should this also handle Y?") is a requested change and gets a verdict.
- **A claim about wording, docs, naming, tests or style**: actionable when it is true, the diff adds or changes what it's about, and something goes wrong (question 4 below).
- **A claim that the code does the wrong thing**: the four questions below.

For a wrong-behavior claim, step 2 must have verified the mechanism first. A verified mechanism is necessary, not sufficient. The comment is actionable only when all four hold, each answered with its evidence:

1. **Reachable.** The scenario can happen in production once this PR ships, on a path a user, job or caller actually takes. Name the path.
2. **Not contrived.** It doesn't need an implausible combination of conditions. Name the conditions it needs.
3. **This PR's.** The diff causes it, or the ticket's AC is unmet without the fix. Behavior the diff doesn't touch is not this PR's.
4. **Something goes wrong.** Name what a person or downstream system gets wrong: an amount charged, a document, a transaction, a screen. If nothing does, the comment fails.

A comment that fails is not actionable. On an inline thread, its reply says what failed and why, and the thread is resolved.

### 4. Present one thread at a time

Re-read this file before each message in this step. The shape decays within a few messages otherwise.

One inline thread per message: the actionable threads first, then the rest, each group in fetch order. Never list the threads, never put two threads in one message, and never preview the next thread or say how many remain. After the closing question, stop. Waiting means emitting nothing.

A top-level review is presented only for its actionable points and its questions, after the inline threads, in its own message, the same way. A review that asks for nothing is never presented and gets no reply. A Copilot review's body is out of scope (step 1).

Each message contains, and contains only:
1. **Header:** `<file>:<line>` (@reviewer) for an inline thread or `Review` (@reviewer) for a top-level review, plus "(reviewer replied)" when the thread has replies.
2. **The commented lines** (inline threads only), verbatim, in a code block.
3. **The comment:** the reviewer's exact text in a blockquote, plus any other replies on the thread.
4. **Strongest case for the comment** (actionable only): one sentence stating the concern at full strength, as if you agreed with it.
5. **Verdict:** the step 3 answer in one or two sentences, with evidence.
6. **Options** (actionable only): a lettered list of genuinely plausible choices, each saying what it changes.
7. **Recommendation** (actionable only): your pick and a one-sentence reason.
8. **The reply:** the exact text to post, for the recommended option, or otherwise the only reply (step 5).
9. **One closing question.** Actionable: which option. Otherwise: "Post this reply and resolve the thread? (y/n)", or "Post this reply? (y/n)" for a top-level review.

The decision is Eli's: recommend, never decide. He answers with one token (`a`, or `y`).

### 5. Writing a reply

- An agreement with a fix made is one word: "Done."
- A decline, disagreement, correction or answer is a sentence or two per point, citing evidence (`comments-docs-and-external-writing.md` § "PR review prose: the shortest thing that lands the point").
- A not-actionable reply says what failed.
- A top-level reply opens by tagging the reviewer (`Responding to @ehrenw's review:`) and quotes each point it answers. An inline reply quotes only the sub-part it answers, if any.
- Never tag copilot (`pr-mine-address-feedback.md` § "Never tag copilot; post only what was approved, byte for byte").

### 6. After each answer

- **A reply with no code change:** post it byte for byte and resolve its thread, if it has one, then present the next thread.
- **A reply that describes a fix:** hold it, and present the next thread. It posts in step 7, after the push (`pr-mine-address-feedback.md` § "Order of operations: push before replying").
- **An edit or a different pick:** re-present that thread whole and wait again.

```bash
python ~/.claude/scripts/pr-feedback.py reply <PR#> <comment-database-id> "<approved reply body>"
python ~/.claude/scripts/pr-feedback.py resolve <thread-graphql-id>
python ~/.claude/scripts/pr-feedback.py review-reply <PR#> "<approved reply body>"
```

`review-reply` posts a top-level review's reply on the conversation tab.

### 7. Fix, push, then post the held replies

After the last thread, when any pick needs a fix:
1. Make every chosen fix. Each is the minimum change that resolves its comment (`pr-mine-address-feedback.md` § "A feedback fix is the minimum change that resolves the comment").
2. Build, and run the tests the fixes affect.
3. Ask once to commit and push (`~/.claude/rules/git-safety.md`). Commit, push and confirm the push. A rejected push stops the skill, and nothing more is posted.
4. Post each held reply byte for byte, and resolve its thread.

### 8. The PR description

Apply `pr-mine-address-feedback.md` § "The PR description is a snapshot of the PR as opened" to the fixes. Draft an `### After review` bullet only for a fix that meets that bar.

## Claims

- **A verified mechanism is not a verdict.** The comment is actionable only when step 3 passes.
- **Disagreement rests on verified facts.** A structural absolute ("can't happen", "impossible", "only ever", "by construction", "guaranteed") needs the mechanism that enforces it: a compile error, a type constraint, an exhaustive switch, a guard clause, a DB constraint. A not-reachable verdict names what makes it so: the code, config or data as it will stand once this PR ships.

## Reviewer shorthand

- **"IB"** is Konstantin's (`kkkmail`) shorthand for "Iron Blockhead", the AI coding agent. A comment headed "For IB:" is a reviewer's request like any other, triaged the same way, and the decision is Eli's.
