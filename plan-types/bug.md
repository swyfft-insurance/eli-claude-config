# Plan type: Bug

## 1. What makes it a Bug

- **The code doesn't do what it was written to do.** If it does what it was written to do and someone wants something else, it's Missed AC or Change request. A missed requirement or a disliked behavior isn't a defect, and `IssueType: Bug`, a Current/Expected Result template, Found-in-Stage Beta or a QA reporter don't show a malfunction. Rater bug and LogMonitor bug supersede Bug.

## 2. Requirement

- **The behavior the ticket expects.** Scope is the reported mechanism plus whatever is part of the same defect, and an incomplete report doesn't narrow it.

## 3. Discovery

- **Discovery finds the code that produced the reported failure and proves it with a test.**

### Steps

1. **Start from the ticket's evidence:** record IDs, attachments, log queries, repro steps. Someone else's diagnosis, the ticket's included, is a starting point: verify each of its claims.
2. **Read the code to find where to look.** Read the full inheritance chain, base to leaf, before saying what a class does or doesn't override.
3. **Pin down what happened to the failing records:** prod-copy queries (Eli runs them), and log searches through `/search-logs` with the ticket's query run verbatim.
4. **Write a test that recreates the failing record** from that data and reproduces the failure on current code.

### What each kind of evidence proves

- **Query results and log lines** prove what happened to the failing records: the values, the events and their order.
- **A stack trace** proves which code ran.
- **Only a test** proves which code produces the failure. Until a test reproduces it, a cause is a hypothesis and is labeled as one.

### The reproducing test

- **It runs on current code.**
- **It recreates the failing record as the data holds it,** even when today's code couldn't create it that way, and never from made-up values.
- **It asserts its setup before it acts:** the subject exists and matches the failing record in every value the scenario depends on (`testing.md` § "Setup asserts: verify the arrange before testing behavior"). A result from a test without them is not evidence.
- **It becomes the regression guard** (§ 5).

### When discovery ends

- **A part is a malfunction the ticket reports:** something the code did that it wasn't written to do. A remedy the ticket asks for, such as correcting a record or adding an override, is a requirement for the fix. Discovery doesn't test it or give it a disposition.

Every part of the reported defect gets one disposition:

- **Fix**: a test reproduces it on current code.
- **Already fixed**: the data shows where it failed, and a test shows current code doesn't fail there.
- **Not a defect**: the data shows the code doing what it was written to do.
- **Spin off**: the reported defect is fixed or isn't a defect, and the evidence gathered for it already proves a different one. A defect is different only when it has its own cause and the reported scenario is fully fixed without touching it. Otherwise it's part of this bug. Never investigate to build a spin off: anything that evidence doesn't already prove is a "noticed" line. The different defect gets its own ticket, filed only after Eli approves it.

- **"Already fixed" and "not a defect" end the work on that part.** When a test can't be built, say what blocks it and stop.

### The report

In one message:

- **each part of the defect:** its disposition, the file:line where behavior diverges from intent, and the test or data behind it
- **noticed, not investigated:** one line each

## 4. Banned at every stage: discovery, design, the plan, execution

- **Treating code reading as proof.** The step after a hypothesis is a query, a log search or a test, not more reading.
- **Suspecting established infrastructure:** ClosedSets, `SwyfftVersion`, `GetTableVersion`, equality operators, DI, EF. Unless the ticket is changing it, treat it like framework code. When it seems wrong, the bug is in your code or your understanding.
- **Searching git history across the whole repo.** A history search names a file or a method.
- **Investigating a finding outside the defect to decide whether it belongs.** It gets one line under "noticed", and never rides along on another finding as a caveat.
- **Pairing a finding with a claim that the next step will prove it.** Say what the evidence would rule out.
- **Writing a plan for the investigation, or asking Eli how to investigate.**

## 5. Steps and stops

- **The test that reproduced the defect in discovery is kept as the regression guard.** The plan's first step brings it up to the repo's test standards and stops for Eli's approval. Then the fix, then the closing stops.

## 6. Verification

- **The failing test is the regression guard.** A bug inside a real service gets an integration test, because a mocked unit test can't reach the real code path.
