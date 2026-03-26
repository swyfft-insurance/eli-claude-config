---
name: Always read YouTrack tickets first
description: Before any investigation or planning for YouTrack bugs, read the actual ticket content — error messages contain the root cause
type: feedback
---

Always read the YouTrack ticket (via get_issue) BEFORE exploring code or launching agents.
Bug tickets filed by automation include full error messages, stack traces, and element values that identify the exact root cause.

**Why:** Wasted 20+ minutes exploring code and writing a speculative plan for SW-48747/SW-48748 when the ticket descriptions contained the exact error messages showing: (1) ScreenedEnclosuresCoverage mismatch due to Dorchester→BenchmarkSpecialty carrier rename, and (2) MinimumPremium V3→V4 version mismatch. Could have identified both fixes in 2 minutes.

**How to apply:** For ANY YouTrack bug ticket, the FIRST action is `get_issue` to read the full description. Extract the error details. Only then investigate the specific code paths indicated by the error.
