# Plan type: Rater bug

It inherits the rater playbooks in full: reading `~/.claude/plan-types/excel-rater-plans-common.md` plus `ho-excel-rater-plans.md` or `co-excel-rater-plans.md` is MANDATORY (HARD RULE header, pre-reads, seeder-first, versioning, verification surface, rater-edit flow).

## 1. What makes it a Rater bug

A defect in a rater already on disk, or in C#-vs-rater parity, with no new rater delivered. Supersedes Bug.

## 3. Discovery

Follows `bug.md`.

## 5. Steps and stops

It follows the Bug sequence (`bug.md`). With no delivery there is no baseline diff, so there is no scoping checkpoint. When the fix is the rater, `excel-rater-plans-common.md` § "Rater edits — when warranted, and the SharePoint flow" governs the fix step, and the plan carries the prepared edit before it counts as written. `Read` that section when writing the step and again when executing it.

## 6. Verification

**The product's parity suite is the guard. Never write a unit test for a rater-parity defect.**
