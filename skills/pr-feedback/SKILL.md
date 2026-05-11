---
name: pr-feedback
description: Address reviewer feedback on my PRs. Use when you need to reply to or resolve PR review comments. Raw gh api reply/resolve calls are blocked — you must use this skill.
---

# Address PR Feedback

Guides the workflow for responding to reviewer comments on my pull requests. Bot comments (Copilot, Claude) get the **same seriousness** as human comments — never dismiss them.

## Arguments

Provide the PR number (e.g., `/pr-feedback 19821`). If not provided, ask for it.

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

- **Decisions belong to the user, not you.** You may recommend an option, but never decide for them. Don't proceed on the "obvious" choice without explicit approval — wait for the user's pick, every entry.
- **One identifier per decision.** Every actionable item gets exactly ONE identifier in ONE numbering scheme. Sub-numbering is fine (e.g., `1.1, 1.2` when a parent group has sub-decisions), but pick a scheme and use it consistently. Don't run parallel schemes (e.g., "Bucket C" + "Question 3" + "C2" all pointing to the same thread).
- **Numbered list, not table.** Tables fall apart once you need code blocks in cells (line breaks become `<br>` hacks, fenced code can't render). Always use a numbered list.
- **Every entry has the same shape.** Same sub-fields, in the same order, every time:
  1. **Header:** `<file>:<line>` — @reviewer (+ "×N identical" if batched, or "(reviewer replied)" if thread context exists)
  2. **Code block:** the commented line(s), in a fenced code block
  3. **Comment quote:** the reviewer's exact text in a blockquote
  4. **Thread context (when present):** other replies on the same thread, e.g. "Justin replied: X"
  5. **Recommendation:** your pick + one-sentence reason
  6. **Options:** lettered list (a, b, c...)
- **Original comment + code go inline.** The user should never have to scroll to find what they're answering. Always quote the reviewer's exact text AND include the commented code lines.
- **Preserve content when restructuring.** If asked to fix formatting or numbering, keep the substantive content — reviewer quotes, code blocks, thread context, option descriptions. Don't bare-label options ("a) decline all") to fit a tighter layout. Restructuring is renumbering, not stripping.

The user answers per entry with a single token (e.g. `1a 2a 3d 4c ...`).

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

**Recommendation:** a — none of the surrounding V_prev configs have summaries; would be a new pattern, not parity.

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

**Recommendation:** d — Justin's reply stands; allow-list-in-drift-test is the only valid suggestion and is low-value.

**Options:**
- a) allow-list `name` in drift test
- b) fall back to `sourceConfig.Name`
- c) endorse Justin, no code change
- d) skip
````

### 4. Process inline threads

For EACH unresolved inline thread with actionable feedback, follow this sequence **in order**. Do not skip steps.

#### a. Research

Before drafting ANY reply, **read the relevant code** that the comment refers to. Use Read, Grep, or other tools to understand the context. Do not reply based on memory or assumptions.

- If the comment claims something about the code, **verify the claim** by reading the code
- If the comment suggests an alternative approach, **evaluate it** against the existing code
- If the comment is from a bot (Copilot, Claude), give it the **same consideration** as a human comment

#### b. Draft the reply

Write the reply using **quote-then-reply format**:

```markdown
> <exact quote from reviewer>

<your response>
```

For comments with multiple points, quote and reply to each point individually. Never use `#1`, `#2` etc. as labels — GitHub renders those as issue/PR links.

**Show the draft to the user in your response.** Do not proceed until the user approves.

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

**Tag the reviewer** at the top of the reply so it's clear which review you're responding to (e.g., `Responding to @ehrenw's review:`).

To post a reply to a top-level review:

```bash
python ~/.claude/scripts/pr-feedback.py review-reply <PR#> "<approved reply body>"
```

This posts an issue comment on the PR conversation tab.

### 6. Repeat

Move to the next actionable item. Repeat until all are addressed.

## Important

- **Never skip the research step.** The whole point of this skill is to prevent lazy replies.
- **Never post without approval.** Gate 2 applies to every reply and every resolve action.
- If a comment identifies a legitimate issue, **fix the code** before replying. Then mention the fix in your reply.
- If you disagree with a comment, explain why with evidence from the code — don't just dismiss it.
- **Only address actionable points.** Positive observations, summaries, and acknowledgements don't need replies.
