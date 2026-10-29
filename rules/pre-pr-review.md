# Pre-PR Adversarial Review

## Every Agent prompt MUST include hard caps

The project's `/review-pr` prompt template has no time, file or output caps. Subagents are fine; their prompts carry the caps below.

- **Time budget**: "Spend no more than 5 minutes. If approaching the limit, stop and report what you have."
- **File-read cap**: "Read at most 15 files."
- **Trace depth cap**: "Don't trace callers/callees more than 1 level deep unless the diff explicitly shows a cross-file integration."
- **Output cap**: "Report under 600 words."
- **Stop-early instruction**: "If you find a Critical issue early, stop and report it. Don't keep tracing."

Never use these phrases in an Agent prompt: "Be thorough", "Trace 2-3 levels up and down", "Look hard for them", "Read enough surrounding context", or "Question your assumptions" without a scope limit.

## If a delegated review runs over

Past 1.5x your estimated upper bound, abandon it with TaskStop immediately, without asking. Never stretch the estimate after the fact: if you said "3–8 minutes" and it's at 12, the estimate was wrong; say so and act on the real elapsed time. A runaway subagent burns tokens against Eli's session budget while producing nothing. Offer to abandon as soon as time slips.

## A review finding is a claim, not a result

The reviewer read the diff cold and doesn't know what was asked for. Before Eli sees a finding, answer two questions, in order:

- **Is it a finding at all?** Open the AC, the plan section that chose the shape, or the precedent the code copied, and name that source in the verdict. The commonest false finding reports the requested behavior as a defect. A finding against the codebase's own precedent goes to Eli labelled as a convention change.
- **Is the mechanism real?** Verify the code path yourself.

The suggested fix is a second claim. Audit it against `coding-standards.md`, and reject a fix that duplicates a source of truth or tests what a captured assert already proves, even when the finding is real.

Present the surviving findings with your own verdict, and each rejected one with a line on why. Run `/eli--fact-check-writing` on the write-up first.
