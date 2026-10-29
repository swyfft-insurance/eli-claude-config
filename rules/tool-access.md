# Tool Access

## Never claim you lack access

Never tell Eli you lack access. YouTrack is reachable through MCP and GitHub through `gh`. If a call fails, load the tool with ToolSearch. If it still fails, ask.

## A gap in Eli's tooling is a gap to fix, not a limit to report

When a skill, script or hook under `~/.claude/` can't answer a question and the direct call is blocked, never report the data as unreachable. Say what's missing, propose extending the tool, and ask before changing it.

## Never make Eli hunt for a link

Find any URL, folder, channel or file Eli needs yourself, and open it with `Start-Process "<url>"` through the PowerShell tool. Never ask him for a locator or name a location for him to navigate to. Slack holds most links: search with `slack_search_public` and an `in:<#CHANNEL>` filter, then grep the saved output for the host. When a locator is written down nowhere, record it in the rules file that governs the work.

## An auto-mode block on routine work is a settings gap, not a handoff

When the auto-mode classifier blocks a step of the work, never hand Eli the command to run. In the same message, offer both: switching out of auto mode so the step retries under the normal permission prompt, and an `autoMode.allow` entry for `~/.claude/settings.json`, drafted in full. Editing `settings.json` also needs auto mode off.

## A skill that did not do its job is broken, and the skill gets fixed where it lives

When a skill, script or hook under `~/.claude/` gives a wrong result, misses what it exists to catch, lets a step be skipped unnoticed, or has to be worked around, say so, naming the skill and what it got wrong. Find the cause in that skill, and draft the fix to it alongside the corrected output. Never fix only the output, or patch the defect inside a skill that calls it.
