# Pre-PR Adversarial Review

The project's `/review-pr` skill is open-ended by default. Its prompt template ends with "be thorough, skeptical, and assume bugs exist — look hard for them" with no time, file, or output caps. That's what licenses unbounded archaeology. Subagents are fine; the prompt has to be reasonably scoped.

## Every Agent prompt MUST include hard caps

- **Time budget**: "Spend no more than 5 minutes. If approaching the limit, stop and report what you have."
- **File-read cap**: "Read at most 15 files."
- **Trace depth cap**: "Don't trace callers/callees more than 1 level deep unless the diff explicitly shows a cross-file integration."
- **Output cap**: "Report under 600 words."
- **Stop-early instruction**: "If you find a Critical issue early, stop and report it. Don't keep tracing."

**Banned phrases** that license unbounded work. Never use these in an Agent prompt:
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

A runaway subagent doesn't just delay the user. It burns tokens against their session budget while producing nothing. That's a real cost. Treat it like a destructive action and give the user explicit options to abandon as soon as time slips.

## A review finding is a claim, not a result

The reviewer read the diff cold, which is what makes it useful and also what makes it wrong. It
does not know what was asked for. Findings arrive fluent, cited, severity-labelled and confident,
and none of that is evidence.

Form your own view on every finding before Eli sees it. Two questions, in this order:

- **Is it a finding at all?** The commonest shape is a finding that restates the requirement as a
  defect: the change does what the ticket asked, and the reviewer, not having the ticket, reports
  the intended behavior as an unintended consequence. Check it against what was asked before
  checking it against the code.
- **Is the mechanism real?** Verify the code path it names yourself. A citation proves the reviewer
  read something, never that the something means what the finding says.

Question 1 is answered by opening a source, never by reasoning: the AC, the plan section that chose
the shape, or the precedent the code copied. The verdict names the source. A finding that objects
to the codebase's own precedent is a convention change, and goes to Eli labelled as one.

The reviewer's suggested fix is a second claim. Audit it against `coding-standards.md` before
applying it. A fix that duplicates a source of truth, or that adds a test for something a captured
assert already proves, is rejected even when the finding is real.

- **What happened:** a theory computed its expectation from the predicate under test. The reviewer
  called it tautological and proposed an explicit config list. The mechanism was real, the QBE
  precedent the plan named was never opened, and the list duplicated `HiscoxConstants`.

Present what survives, with your own verdict attached. A finding relayed without one hands Eli the
reviewer's confidence and none of your judgement, which is the work the review was meant to save
him. Say plainly which findings you rejected and why, in one line each.

Run `/eli--fact-check-writing` on the write-up before presenting it. Every finding you keep is a
claim you are now making in your own voice, and so is every reason you give for rejecting one.
Inheriting the reviewer's wording inherits its errors under your name.
