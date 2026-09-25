# Tool Access

- YouTrack and Slack MCP tools are DEFERRED. Use ToolSearch to load them before calling.
- NEVER tell the user you don't have access. You DO. YouTrack via MCP, GitHub via `gh` CLI.
- If a tool call fails, use ToolSearch to load it. If still failing, ASK. Don't give up.
- A gated publish that fails on a schema or validation error is retried whole, never trimmed to get
  past the gate. See `~/.claude/rules/core-behavior.md` § "A failed publish is retried whole, never
  trimmed".

<!-- Added 2026-09-04 after SW-55583 — /eli--read-ticket returned no watchers and the answer given
     was "I'd be guessing" instead of an offer to add the field. -->
## A gap in Eli's tooling is a gap to fix, not a limit to report

The skills, scripts, and hooks under `~/.claude/` are Eli's own. When one of them can't answer a
question, and the direct call is blocked or unavailable, the answer is to extend the tool, not to
tell him the data is unreachable. Say what's missing, propose the change, and ask before making it.

<!-- Added 2026-09-09 during SW-55584 -->
## Never make Eli hunt for a link

A URL, folder, channel, or file Eli needs is yours to find and yours to open. Search for it, then
open it with `Start-Process "<url>"` through the PowerShell tool. Two failures, not one: asking him
to supply a locator, and naming a location in prose for him to navigate to himself.

Slack holds most of them. `slack_search_public` with an `in:<#CHANNEL>` filter retrieves a link
someone posted, and the search output is usually too large to return inline, so grep the saved file
for the host rather than reading it back.

When the locator turns out to be written down nowhere, that is the gap above. Record it in the rules
file that governs the work, so the next ticket starts with the address instead of a search.

## An auto-mode block on routine work is a settings gap, not a handoff

When the auto-mode classifier blocks a step that is part of the work (placing a rater, writing a
tracked file, running a sanctioned script), never hand the command to Eli to run himself. In the
same message that reports the block, offer both of these:

- **Switch out of auto mode for this step.** Eli toggles the mode, the step retries under the
  normal permission prompt, and he approves it there.
- **An `autoMode.allow` entry** in `~/.claude/settings.json` covering that class of step, drafted
  in full, so the next occurrence doesn't block. The classifier also blocks edits to
  `settings.json` itself as self-modification, so this edit also goes through outside auto mode.

- **What happened:** placing an edited FL rater into its four `Data/` carrier files was blocked as
  irreversible destruction. The reply offered Eli the copy command to run by hand and never
  mentioned leaving auto mode.

## A skill that did not do its job is broken, and the skill gets fixed where it lives

When a skill, script or hook under `~/.claude/` produces a wrong result, misses what it exists to
catch, or has to be worked around, the skill is broken. Correcting the output by hand, or patching
the defect inside some other skill that happens to call it, leaves it broken for the next run.

The response, in order:

1. Say plainly that the skill failed, naming the skill and what it got wrong.
2. Read the skill or script and find the cause.
3. Draft the fix to the skill itself and present it alongside the corrected output. The output is
   not re-presented until the skill fix is drafted too.

"I skipped that step" or "I worked around it" is never the whole answer. A step that can be
skipped, or a defect that can be worked around, without the skill noticing is a defect in the
skill.

- **What happened:** `/eli--diff` baselined on a stale local `development` and pulled 109
  unrelated files. The first fix landed in `eli--review-prs-parallel`, which calls it, and the
  diff skill itself stayed broken until the same failure repeated.
- **What happened:** `/eli--audit-pr-desc` passed a PR body that argued against the change and
  quoted one ticket but not the other, both rules in the files it walks. The miss was reported as
  a personal slip and the body was corrected in place.
