# Addressing Feedback on My PRs

- **Quote only what needs quoting.** An inline reply quotes only the sub-part of a multi-point comment it answers, if any. A top-level reply quotes each point and replies under it. Never label points `#1`, `#2`: GitHub renders those as links.
- **Drafts shown to Eli carry the reviewer's verbatim text** in a blockquote above each reply, never a placeholder like `(quote Justin)`. This governs the draft, not the posted body.
- Reply to every thread, then resolve it. The merge queue requires resolution.
- Never use `minimizeComment`. It hides a comment instead of resolving it.

## Copilot reviews: inline comments only

A Copilot review's inline comments are its whole scope. Ignore everything in its body, including the "Suppressed comments" section: don't address it and don't present it for triage. A human reviewer's top-level comment is still real feedback.

## A review comment is not automatically a request

Decide from each comment's own words whether it asks for anything. Length and a file:line anchor don't make it a request. This matters most on Ehren's AI-authored reviews, signed "Reviewed as Claudulina (AI)", which are mostly confirmation.

A comment goes to Eli for a ruling only when it requests a change and passes the verdict in `/eli--pr-feedback` step 3. A question is answered in its reply, and one that proposes a change counts as a requested change. A wrong claim no other reply has corrected is corrected in the reply. A soft suggestion inside a confirmatory comment ("worth a line in the PR body") is weighed in the reply, not promoted to a ruling. When the reviewer asks for nothing, never frame the reply as a decline: correct a wrong claim, acknowledge a right one, stop.

Not actionable is not the same as not answered: still reply to the thread, still resolve it.

## A feedback fix is the minimum change that resolves the comment

An approved PR changes only where a verified comment requires it. The fix is the smallest diff that makes the comment's failing test pass.
- No refactor, rename, extracted constant or shared set the fix doesn't need, even when a coding standard would ask for one.
- Never edit a line the reviewers approved unless the comment is about that line.
- When a standard would push the fix past this, name it to Eli and leave it out.

## Order of operations: push before replying

Never post a reply before the code it describes is on the remote. Order: make the change, build and run affected tests, commit, push, confirm the push succeeded, then `pr-feedback reply` each thread, then resolve each one. If the push is rejected (merge queue, branch protection), stop and post nothing.

## Never tag copilot; post only what was approved, byte for byte

An `@copilot` mention anywhere in a posted body, quoted text included, spawns a coding-agent session under Eli's account. Never tag copilot, and never work around the guards in pr-feedback.py, pr-review.py and the pretooluse hook. The posted body is the approved draft byte for byte: never regenerate it from a parse, template or script, and read the exact body back against the approved text before posting.

## The PR description is a snapshot of the PR as opened

The description and its Verification section describe the PR as opened. A fix made after that changes the description only when it changes the intent, adds a surprise (`pr-creation.md` § "Length"), changes the blast radius, or makes a sentence in the description false. A fix that only adds tests or changes a count leaves the description alone: its commit and thread reply carry it.

A fix that does change the description gets a bullet in a `### After review` section, below Verification: the commit, what it changed, and the tests it ran. A sentence the fix makes false is struck through in place (`~~...~~`), never deleted, and its replacement follows it, so a reader still sees what the PR said before.

Writing either touches only those lines. Their claims are fact-checked, nothing else in the description is re-audited, and no suite is rerun for them.
