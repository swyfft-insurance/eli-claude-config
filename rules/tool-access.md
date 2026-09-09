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
