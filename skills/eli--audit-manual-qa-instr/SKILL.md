---
name: eli--audit-manual-qa-instr
description: Audit drafted manual-QA instructions against plan-mode.md § "Manual QA, when applicable" and fix every violation in place. Hands back only the corrected instructions. Run before the instructions are ever shown to Eli.
---

# Manual-QA Instructions Audit

The instructions were drafted first. This run checks the draft against the rules.

The subject is the draft passed as the argument, or else the last manual-QA draft in the conversation.

1. `Read` `~/.claude/rules/plan-mode.md` § "Manual QA, when applicable", with an actual Read call, this turn.
2. Check every scenario's Setup, Act and Assert against every rule in that section. Fix each one a scenario breaks.
3. Hand back only the corrected instructions: no findings, and no mention that an audit ran.
