---
name: eli-pr-feedback
description: Address reviewer feedback on my PRs. Use when you need to reply to or resolve PR review comments. Raw gh api reply/resolve calls are blocked — you must use this skill.
---

# Address PR Feedback

Guides the workflow for responding to reviewer comments on my pull requests. Bot comments (Copilot, Claude) get the **same seriousness** as human comments — never dismiss them.

## Arguments

PR number (e.g., `/eli-pr-feedback 19821`). If not provided, default to the PR for the current branch — do NOT ask, just resolve it:

```bash
gh pr view --json number --jq .number
```

If that errors (no PR for current branch) or returns multiple, then ask. Otherwise use what it returns silently and move on. Asking "which PR?" when there's exactly one PR for the current branch is noise.

## Steps

### 1. Fetch feedback

```bash
python ~/.claude/scripts/pr-feedback.py fetch <PR#>
```

Set timeout to 30000ms. The script outputs JSON with:
- `unresolvedThreads`: Inline review threads (attached to specific lines)
- `reviews`: Top-level review comments (review body text, not attached to lines)

### 2. Display the feedback

**Inline threads:**

```
Thread 1: <file>:<line> (@<author>)
> <quoted comment body>
```

**Top-level reviews:**

```
Review: @<author> (<state>)
> <quoted review body>
```

### 3. Triage

Only address **actionable** points — things that require a code change, an explanation, or a decision. Skip positive observations, summaries, and "looks good" comments. Present the actionable items to the user.

**Presentation rules:**

- **IMPORTANT: Present items ONE AT A TIME — never dump all items in a single message.** Show exactly one actionable item (in the entry shape below), then STOP and wait for the user's pick for that item. Only after they answer do you present the next one. Dumping all items at once is a hard violation — the user has repeatedly and emphatically rejected it. The total count may be stated up front (e.g. "7 actionable items — here's #1 of 7"), but the body of each message contains a single item.
- **IMPORTANT: Decisions belong to the user, not you.** You may recommend an option, but never decide for them. Don't proceed on the "obvious" choice without explicit approval — wait for the user's pick, every entry. This is a hard requirement, not a suggestion — never skip it.
- **One identifier per decision.** Every actionable item gets exactly ONE identifier in ONE numbering scheme. Sub-numbering is fine (e.g., `1.1, 1.2` when a parent group has sub-decisions), but pick a scheme and use it consistently. Don't run parallel schemes (e.g., "Bucket C" + "Question 3" + "C2" all pointing to the same thread).
- **Numbered list, not table.** Tables fall apart once you need code blocks in cells (line breaks become `<br>` hacks, fenced code can't render). Always use a numbered list.
- **Every entry has the same shape.** Same sub-fields, in the same order, every time:
  1. **Header:** `<file>:<line>` — @reviewer (+ "×N identical" if batched, or "(reviewer replied)" if thread context exists)
  2. **Code block:** the commented line(s), in a fenced code block
  3. **Comment quote:** the reviewer's exact text in a blockquote
  4. **Thread context (when present):** other replies on the same thread, e.g. "Justin replied: X"
  5. **Strongest case for the comment:** one sentence stating the strongest, most convincing version of the reviewer's concern, written as if you agreed with it. Do this BEFORE the recommendation — it forces genuine engagement and blocks reflexive dismissal. You cannot recommend declining a concern you haven't first stated at full strength.
  6. **Recommendation:** your pick + one-sentence reason. If the pick is **decline** or **skip**, the reason must state whether it rests on a *structural guarantee* (and cite the enforcing mechanism) or merely on *current state*. If it's only current state, declining a future-proofing comment is not permitted (see Important §).
  7. **Options:** lettered list (a, b, c...)
- **Original comment + code go inline.** The user should never have to scroll to find what they're answering. Always quote the reviewer's exact text AND include the commented code lines.
- **Preserve content when restructuring.** If asked to fix formatting or numbering, keep the substantive content — reviewer quotes, code blocks, thread context, option descriptions. Don't bare-label options ("a) decline all") to fit a tighter layout. Restructuring is renumbering, not stripping.

The user answers one entry at a time with a single token (e.g. `1a`). Present the next item only after they've answered the current one — do NOT batch.

**Example** (from PR #20495, SW-50765 CompetitiveFactor rounding):

````markdown
### 1. `HomeownerStateConfigByPerilEAndSBenchmarkSpecialtyAL.cs:282-285` — @copilot-pull-request-reviewer (×17 identical)

```csharp
public static HomeownerStateConfig ALByPerilEAndSBenchmarkSpecialtyV15 { get; } =
    new(sourceConfig: ALByPerilEAndSBenchmarkSpecialtyV14,
        stateConfigName: "AL.BSIC.ByPeril.EAndS",
        version: SwyfftVersion.V15);
```

> This newly introduced public config property doesn't have the usual summary/ticket context that the surrounding versioned configs have. Consider adding a brief `/// <summary>` (e.g., referencing SW-50765).

**Strongest case for the comment:** a developer landing on this config cold has no inline pointer to the ticket or rationale.

**Recommendation:** a — none of the surrounding V_prev configs carry summaries either; a summary here would be a new pattern, not parity (current-state basis; not a future-proofing comment, so declining is permitted).

**Options:**
- a) decline all
- b) add summaries
- c) address one as rep, decline rest

---

### 2. `HomeownerStateConfig.cs:182-186` — @copilot-pull-request-reviewer

```csharp
/// <summary>
/// Clones <paramref name="sourceConfig"/> with overrides. ...
/// <paramref name="name"/> is intentionally omitted so the main ctor re-derives it.
/// </summary>
```

> The XML doc says 'name is intentionally omitted' but the ctor actually has a `name` parameter (and forwards it). Consider rewording.

**Strongest case for the comment:** the doc comment directly contradicts the signature it documents, so a reader will trust a false statement about how the ctor behaves.

**Recommendation:** a — Copilot's right, wording's confusing.

**Options:**
- a) reword
- b) decline

---

### 3. `HomeownerStateConfig.cs:245` — @ken-swyfft (Justin replied)

```csharp
name: name,
```

> `name` is the only param that doesn't fall back to `sourceConfig`... Either fall back to `sourceConfig.Name`, or have `HomeownerStateConfigCloneCtorTests` allow-list `name` explicitly so the intent is enforced rather than assumed.

Justin replied: *"That would be wrong as it would default to the previous config's name. By passing null to the other constructor it will default it to the correct name."*

**Strongest case for the comment:** `name` behaving differently from every other param is an unstated invariant; encoding it in the drift test would make the intent enforced rather than assumed.

**Recommendation:** d — Justin's reply stands; the only remaining suggestion (allow-list `name` in the drift test) is low-value relative to its upkeep cost.

**Options:**
- a) allow-list `name` in drift test
- b) fall back to `sourceConfig.Name`
- c) endorse Justin, no code change
- d) skip
````

### 4. Process inline threads

For EACH unresolved inline thread with actionable feedback, follow this sequence **in order**. Do not skip steps.

#### a. Research — the heart of this skill; do it BEFORE you form a recommendation, not just before the reply

**Take every comment seriously. Treat it as correct until you have read the code and proven otherwise.** This is not a queue to clear — it is a set of claims to verify. You are a computer; there is no time pressure and nothing else competing for your attention. "This is taking too long" / "I just want to resolve this thread" is NEVER a reason to short-cut. Rushing a reply out to get the comment off your plate is the single worst, most unacceptable failure mode of this skill. Slow down and do the work.

This research must be complete before you write the **Triage recommendation** in step 3, not merely before the reply in 4b — a recommendation is itself a claim about the code.

Mandatory, every comment, no exceptions:

- **Read the actual ticket(s) — FROM THE SOURCE, NEVER A PARAPHRASE.** Before you form a single
  recommendation, read every YouTrack ticket in the PR/branch via the `/eli-read-ticket` skill — the
  only sanctioned way — including its description, ALL comments, and any ticket it was scoped from.
  The ticket is the authoritative statement of what the change is FOR and what it **explicitly
  guarantees**; reviewer concerns are routinely *already answered there*. **A plan file, a
  conversation/compaction summary, a prior-session recollection, or memory is NOT a substitute for
  reading the live ticket — these paraphrases silently drop or distort the exact guarantees a
  reviewer is questioning.** If you find yourself writing a "strongest case" or a recommendation
  resting on what the plan/summary *said* the ticket says, STOP and run `/eli-read-ticket`. This is
  non-negotiable: skipping it once shipped a review whose "strongest case" asserted a danger the
  ticket explicitly ruled out — destroying the credibility of the entire triage and wasting the
  user's time. NEVER let this happen again.
- **Read the actual code.** Open the method the comment points at, its callers, and its callees — using Read/Grep. Not from memory. Not from the diff alone. If you assert anything about the code, you must have *just read the lines that prove it*.
- **Read the governing docs.** Find and read the relevant `CLAUDE.md` and `.claude/rules/*.md` for the touched subsystem (use the "Namespace-Specific Documentation" and "Conditional Rules" tables in the root `CLAUDE.md` as the index). A comment is frequently right or wrong on the basis of a documented convention you have not loaded. Reading the diff does NOT auto-load path-scoped rule files — you must open them yourself.
- **Verify every factual claim — the reviewer's AND your own.** Before you write "this can't happen" / "this is fine" / "this is wrong", point to the specific code or doc that establishes it. See the Important § ban on overstated absolutes.
- **Evaluate suggested alternatives** against the real code, not a mental model of it.
- **A bot comment (Copilot, Claude) gets the same seriousness as a human's.** "It's just Copilot" is not a triage shortcut.

If you feel the urge to decline or skip a comment quickly, that urge is the signal to read MORE, not less.

#### b. Draft the reply

Write the reply using **quote-then-reply format**:

```markdown
> <exact quote from reviewer>

<your response>
```

For comments with multiple points, quote and reply to each point individually. Never use `#1`, `#2` etc. as labels — GitHub renders those as issue/PR links.

**IMPORTANT: Show the draft to the user in your response.** Do not proceed until the user approves. This is a hard requirement, not a suggestion — never skip it.

#### c. Wait for approval

**STOP and wait.** The user must explicitly approve ("post it", "go ahead", "send it", "yes") before you post anything. Clarifications and side comments are NOT approval.

#### d. Post the reply

After approval:

```bash
python ~/.claude/scripts/pr-feedback.py reply <PR#> <comment-database-id> "<approved reply body>"
```

#### e. Resolve the thread

After the reply is posted:

```bash
python ~/.claude/scripts/pr-feedback.py resolve <thread-graphql-id>
```

### 5. Process top-level reviews

For top-level reviews with actionable points, follow the same research → draft → approve → post flow. Only address the actionable points — quote each one individually and reply.

**IMPORTANT: Tag the reviewer** at the top of the reply so it's clear which review you're responding to (e.g., `Responding to @ehrenw's review:`). This is a hard requirement, not a suggestion — never skip it.

To post a reply to a top-level review:

```bash
python ~/.claude/scripts/pr-feedback.py review-reply <PR#> "<approved reply body>"
```

This posts an issue comment on the PR conversation tab.

### 6. Repeat

Move to the next actionable item. Repeat until all are addressed.

## Important

- **The live ticket is mandatory reading — a paraphrase is not the ticket.** Plan files,
  conversation/compaction summaries, prior-session memory: none are acceptable stand-ins for the
  PR's YouTrack ticket(s) and comments. The ticket states the change's purpose and its explicit
  guarantees, and reviewer concerns are often settled there already. Forming ANY recommendation
  from a paraphrase instead of the read-it-yourself ticket is a hard skill violation.
- **Never skip the research step.** The whole point of this skill is to prevent lazy replies.
- **Never post without approval.** Gate 2 applies to every reply and every resolve action.
- If a comment identifies a legitimate issue, **fix the code** before replying. Then mention the fix in your reply.
- **Disagreement must rest on verified facts, not overstated ones.** Citing code is not a free pass — you can cite real evidence and still draw a conclusion it doesn't support. Do not lean on a structural absolute ("can't happen", "impossible", "only ever", "by construction", "by design", "guaranteed") unless you cite the mechanism that *enforces* it: a compile error, a type constraint, an exhaustive switch, a guard clause, a DB/schema constraint. **"The only values that exist today are X" is a current-state fact, NOT a structural guarantee** — a future addition breaks it. If a current-state fact is all you have, you may not claim the case can't occur.
- **Future-proofing comments are valid by default.** A comment of the form "if X is added later, this silently breaks" can be declined only by (a) citing a mechanism that structurally prevents X, or (b) showing the guard's cost outweighs the risk — **never** by asserting X doesn't exist today. "A defensive guard for a case that can't currently arise" is a reason to *add* the guard, not to dismiss the comment.
- **Only address actionable points.** Positive observations, summaries, and acknowledgements don't need replies.
