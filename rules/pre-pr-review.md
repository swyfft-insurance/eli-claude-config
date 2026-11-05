---
audited-by: []
---

# Pre-PR Adversarial Review

## Every Agent prompt MUST include hard caps

The project's `/review-pr` prompt template has no time, file or output caps. Subagents are fine; their prompts carry the caps below.

- **Time budget**: "Spend no more than 5 minutes. If approaching the limit, stop and report what you have."
- **File-read cap**: "Read at most 15 files."
- **Trace depth cap**: "Don't trace callers/callees more than 1 level deep unless the diff explicitly shows a cross-file integration."
- **Output cap**: "Report under 600 words."
- **Stop-early instruction**: "If you find a Critical issue early, stop and report it. Don't keep tracing."

This overrides `/review-pr`'s "Fill in the values and change nothing else": its reviewer and claim-verifier prompts get these caps appended.

Never use these phrases in an Agent prompt: "Be thorough", "Trace 2-3 levels up and down", "Look hard for them", "Read enough surrounding context", or "Question your assumptions" without a scope limit.

## If a delegated review runs over

Past 1.5x your estimated upper bound, abandon it with TaskStop immediately, without asking. Never stretch the estimate after the fact: if you said "3–8 minutes" and it's at 12, the estimate was wrong; say so and act on the real elapsed time. A runaway subagent burns tokens against Eli's session budget while producing nothing. Offer to abandon as soon as time slips.

## A review finding is a claim, not a result

The reviewer read the diff cold and doesn't know what was asked for. Before Eli sees a finding, answer two questions, in order:
A verifier's CONFIRMED proves the mechanism, not the defect.

- **Is it a finding at all?** Open the AC, Eli's ruling on the shape (the plan's Decisions, in his words), or the precedent the code copied, and name that source in the verdict. The commonest false finding reports the requested behavior as a defect. A finding against the codebase's own precedent goes to Eli labelled as a convention change.
- **Is the mechanism real?** Verify the code path yourself.

Every finding in the write-up quotes the ticket sentence or Eli ruling it breaks, or the one that allows it, and says whether its scenario happens in production or is an edge case the ticket never asks for. An edge case the ticket never asks for is not a finding (`plan-mode.md` § "Banned"). A write-up missing either answer for any finding is never presented.

A finding must be a defect the diff introduces. Behavior the diff didn't cause, however real, is not a finding for this PR.

The suggested fix is a second claim. Audit it against `coding-standards.md`, and reject a fix that duplicates a source of truth or tests what a captured assert already proves, even when the finding is real.

Present the surviving findings with your own verdict, and each rejected one with a line on why. Run `/eli--fact-check-writing` on the write-up first.
