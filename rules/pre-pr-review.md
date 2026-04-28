# Pre-PR Adversarial Review

The project's `/review-pr` skill is open-ended by default — its prompt template ends with "be thorough, skeptical, and assume bugs exist — look hard for them" with no time, file, or output caps. That's what licenses unbounded archaeology. Subagents are fine; the prompt has to be reasonably scoped.

## Every Agent prompt MUST include hard caps

- **Time budget**: "Spend no more than 5 minutes. If approaching the limit, stop and report what you have."
- **File-read cap**: "Read at most 15 files."
- **Trace depth cap**: "Don't trace callers/callees more than 1 level deep unless the diff explicitly shows a cross-file integration."
- **Output cap**: "Report under 600 words."
- **Stop-early instruction**: "If you find a Critical issue early, stop and report it — don't keep tracing."

**Banned phrases** that license unbounded work — never use these in an Agent prompt:
- "Be thorough"
- "Trace 2-3 levels up and down"
- "Look hard for them"
- "Read enough surrounding context"
- "Question your assumptions" without a scope limit

## If a delegated review runs over

If the agent runs more than **1.5x** my estimated upper bound, **abandon via TaskStop immediately**. Don't ask the user. Don't rationalize the delay. Don't say "still plausible" or "probably doing X". The agent's authorization expires when it exceeds the budget.

## Never move time-estimate goalposts

If I said "3–8 minutes" and it took 12, that's past my estimate, full stop. Don't say "10 is at the upper end" or "with this prompt, longer is plausible". Admit the estimate was wrong, then act on the real elapsed time (abandon if past 1.5x).

## Acknowledge the cost

A runaway subagent doesn't just delay the user — it burns tokens against their session budget while producing nothing. That's a real cost. Treat it like a destructive action and give the user explicit options to abandon as soon as time slips.
