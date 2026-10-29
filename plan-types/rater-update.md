# Plan type: Rater update

## Required reading

- **Reading the matching playbook in full is MANDATORY:** `~/.claude/plan-types/ho-excel-rater-plans.md` (Homeowner) or `~/.claude/plan-types/co-excel-rater-plans.md` (Commercial), plus `~/.claude/plan-types/excel-rater-plans-common.md`.

## 1. What makes it a Rater update

- **Actuarial delivers a new rater `.xlsm`, on any sheet, and the C# is brought into agreement with it.** Usually a YouTrack Feature. Supersedes Feature.

## 2. Requirement

- **The requirement is the diff between the delivered rater and the captured baselines,** which doesn't exist until the raters are placed and the validation tests regenerate the baselines. The ticket, the `version_history` sheet and the on-disk rater don't substitute for it.

## 3. Discovery

- **Branch, place the raters, regenerate the baselines, scoping checkpoint, versioning check.** No code, seeder included.

Before the diff:

- **No reading ahead into the C#** to check the ticket's technical notes.
- **No provisional C# change list.** Don't transcribe the technical notes as steps.

## 5. Steps and stops

- **The plan is written from the diff:** every sheet's verdict, the C# change list, configs, version lookups, quote defs, tests, Verification. Implementation starts here, seeder first (`excel-rater-plans-common.md` § "Implement the seeder first"). It follows the Feature sequence.

- **Every Excel Rater (ByPeril) plan carries a "Rater defect found during execution" section. MANDATORY**, whether or not a defect is suspected; `/eli--plan-audit` fails a plan without it. When a defect small enough to fix ourselves surfaces, HARD STOP and prepare the edit to the standard in `excel-rater-plans-common.md` § "Rater edits — when warranted, and the SharePoint flow" before anything downstream runs. The section also carries the channel message, per `excel-rater-plans-common.md` § "What a message to the channel is for".
