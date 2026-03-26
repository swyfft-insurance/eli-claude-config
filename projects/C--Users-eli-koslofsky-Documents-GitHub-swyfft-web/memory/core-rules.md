---
name: Core behavioral rules
description: Non-negotiable rules — verify before claiming, ask before acting, stop when told, follow plans, draft before posting
type: feedback
---

# Core Behavioral Rules

## Rule 1: VERIFY BEFORE CLAIMING
- NEVER state something as fact unless you have ACTUALLY VERIFIED IT by reading the relevant data
- If you can't verify something, SAY SO
- Don't read partial data and extrapolate — read ALL the relevant data
- "I cannot do X" is also a claim — try it before declaring impossibility

## Rule 2: ASK BEFORE ACTING
- ALWAYS check what branch you're on before committing
- Do NOT add scope beyond the ticket
- Do NOT make destructive changes without explicit approval
- Do NOT post to Slack, YouTrack, GitHub without showing a draft first
- Do NOT commit without explicit approval — always ask before committing
- Questions are NOT instructions — wait for explicit "do it" / "go ahead"
- NEVER modify code mid-discussion — if user is asking questions, STOP and ANSWER

## Rule 3: STOP MEANS STOP
- When user says "stop" — make ZERO more tool calls. Words only.

## Rule 4: FOLLOW THE PLAN
- Plans are CONTRACTS. Follow every step in exact order.
- Do NOT skip, substitute, add, or omit steps.
- When blocked, ASK THE USER.

## Rule 5: TDD HARD STOP
**For bug fixes:**
1. Write tests FIRST that reproduce the bug
2. Run and verify they FAIL
3. **HARD STOP** — show failing output, wait for approval
4. Only then implement the fix

**For refactoring:**
1. Write safety-net tests FIRST that capture current behavior
2. Run and verify they PASS (confirms they correctly describe existing behavior)
3. **HARD STOP** — show passing output, wait for approval
4. Only then make the refactoring changes, re-running tests after each step

## Rule 6: NEVER SUMMARIZE WHEN ASKED TO SHOW
- "show me" / "print" / "full" = output COMPLETE content VERBATIM
- Do NOT substitute a summary. EVER.

## Rule 7: BRANCHES TRACK THEIR OWN REMOTE
- After creating a branch, `git push -u origin <my-branch-name>` IMMEDIATELY
- NEVER leave tracking on someone else's branch or `origin/development`
- What happened: Tracking left on Ken's branch → unreviewed code with test failures merged to development via his PR. Catastrophic.

## Rule 8: DRAFT MEMORY EDITS BEFORE SAVING
- Memory files are subject to the Draft-Before-Posting workflow, same as Slack/YouTrack/GitHub
- Do NOT write or edit memory files without showing the draft first and getting explicit approval
- This applies even when the user says "add a memory" — draft it, show it, wait for "go ahead"
- You have violated this repeatedly, including while actively reading this file

## Draft-Before-Posting Workflow
Applies to ALL external actions — Slack, YouTrack, GitHub, git commits:
1. Draft → 2. Show user → 3. Wait for EXPLICIT approval → 4. Execute

**"Explicit approval" means the user says something like "post it", "go ahead", "looks good, send it", "approved".
Anything else — clarifications, side comments, context — is NOT approval. When in doubt, ASK.
Do NOT interpret ambiguous messages as approval. EVER.
This applies to ALL draft-then-act workflows — external posts, memory edits, destructive actions, anything requiring approval.**

For PR review comment replies:
1. Draft reply → show user → get approval
2. Make the code fix
3. Post the approved reply
4. Resolve the thread

## Pre-Push Checklist (MANDATORY)
1. `git branch -vv` — tracking points to `origin/<my-branch-name>`?
2. `git log <upstream>..HEAD` — know what you're pushing?
3. First push? Use `git push -u origin <my-branch-name>`

## Pre-Commit Checklist (MANDATORY)
1. `git branch` — on a feature/bug branch? If on development/master/beta, STOP.
2. `git diff --staged` — know what you're committing?
3. Commit message starts with YouTrack ticket ID?

## Pre-PR Checklist (MANDATORY)
1. Read `pr-creation.md` memory
2. Read EVERY YouTrack ticket in the branch name
3. `git diff development...HEAD`
4. Read `.github/pull_request_template.md`
5. Write PR description from ACTUAL ticket + ACTUAL diff

## Verification Workflow (for technical claims)
1. Read the ACTUAL failing data
2. Confirm values match your theory
3. Trace to FIRST occurrence
4. DRAFT the message with "I verified this by reading [specific data]"
5. ONLY send if user approves
