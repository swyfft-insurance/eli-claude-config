# Plan type: Bug

## 1. What makes it a Bug

The code doesn't do what it was written to do. If it does what it was written to do and someone wants something else, it's Missed AC or Change request. A missed requirement or a disliked behavior isn't a defect, and `IssueType: Bug`, a Current/Expected Result template, Found-in-Stage Beta or a QA reporter don't show a malfunction. Rater bug and LogMonitor bug supersede Bug.

## 2. Requirement

The behavior the ticket expects. Scope is the reported mechanism plus whatever is part of the same defect, and an incomplete report doesn't narrow it.

## 3. Discovery

How:

1. Start from the ticket's evidence: record IDs, attachments, log queries, repro steps. Someone else's diagnosis, the ticket's included, is a starting point: verify each of its claims against the code.
2. Read the code to find where to look. Read the full inheritance chain, base to leaf, before saying what a class does or doesn't override.
3. Settle which mechanism fired: a prod-copy query on the reported records (Eli runs it), a log search through `/search-logs` with the ticket's query run verbatim, a diagnostic harness, a throwaway test, or a test that becomes the regression guard.

Counts as evidence:

- query results on the failing records
- log lines
- a test that reproduces the failure
- code tracing along an explicit stack trace's frames, or for a trivial cause

A root cause is a hypothesis, labeled as one, until a test reproduces it.

Banned:

- **Treating code reading as proof.** Code tracing proves a cause only along an explicit stack trace's frames, or when the cause is trivial. Otherwise the step after a hypothesis is a query, a log search or a test, not more reading.
- **Suspecting established infrastructure:** ClosedSets, `SwyfftVersion`, `GetTableVersion`, equality operators, DI, EF. Unless the ticket is changing it, treat it like framework code. When it seems wrong, the bug is in your code or your understanding.
- **Searching git history across the whole repo.** A history search names a file or a method.
- **Building a test from made-up values.** A test is built from the failing environment's real data. It recreates the record as it exists in that data, even when today's code couldn't create it that way.
- **Investigating a finding outside the defect to decide whether it belongs.** It gets one line under "noticed", and never rides along on another finding as a caveat.
- **Pairing a finding with a claim that the next step will prove it.** Say what the evidence would rule out.
- **Writing a plan for the investigation, or asking Eli how to investigate.**

Ends the work: a disposition of "not a defect" or "already fixed". The other two are "fix" and "spin off".

What it reports, in the one message:

- the defect: the file:line where behavior diverges from intent, or, short of that, that it isn't pinned down and what would settle it
- the evidence for each claim, with proven and hypothesis labeled separately
- the proving test, if one was written: kept as the guard, or discarded
- noticed, not diagnosed: one line each
- the disposition

When the ticket already names the cause and the data confirms it, the report is the line of code and the evidence.

## 5. Steps and stops

Write the failing test, run it, see it fail, and stop for Eli's approval. Then the fix, then the closing stops.

## 6. Verification

The failing test is the regression guard. A bug inside a real service gets an integration test, because a mocked unit test can't reach the real code path.
