---
name: pr-feedback
description: Address reviewer feedback on my PRs. Use when you need to reply to or resolve PR review comments. Raw gh api reply/resolve calls are blocked — you must use this skill.
---

# Address PR Feedback

Guides the workflow for responding to reviewer comments on my pull requests. Bot comments (Copilot, Claude) get the **same seriousness** as human comments — never dismiss them.

## Arguments

Provide the PR number (e.g., `/pr-feedback 19821`). If not provided, ask for it.

## Steps

### 1. Fetch unresolved threads

```bash
python ~/.claude/scripts/pr-feedback.py fetch <PR#>
```

Set timeout to 30000ms. The script outputs JSON with all unresolved review threads, including thread IDs, comment IDs, authors, file paths, line numbers, and comment bodies.

### 2. Display the comments

Print each unresolved thread clearly:

```
Thread 1: <file>:<line> (@<author>)
> <quoted comment body>

Thread 2: <file>:<line> (@<author>)
> <quoted comment body>
```

### 3. Process each thread

For EACH unresolved thread, follow this sequence **in order**. Do not skip steps.

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

### 4. Repeat

Move to the next unresolved thread. Repeat steps 3a-3e for each one.

## Important

- **Never skip the research step.** The whole point of this skill is to prevent lazy replies.
- **Never post without approval.** Gate 2 applies to every reply and every resolve action.
- If a comment identifies a legitimate issue, **fix the code** before replying. Then mention the fix in your reply.
- If you disagree with a comment, explain why with evidence from the code — don't just dismiss it.
