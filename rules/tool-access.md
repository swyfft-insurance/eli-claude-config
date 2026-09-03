# Tool Access

- YouTrack and Slack MCP tools are DEFERRED. Use ToolSearch to load them before calling.
- NEVER tell the user you don't have access. You DO. YouTrack via MCP, GitHub via `gh` CLI.
- If a tool call fails, use ToolSearch to load it. If still failing, ASK. Don't give up.
- A gated publish that fails on a schema or validation error is retried whole, never trimmed to get
  past the gate. See `~/.claude/rules/core-behavior.md` § "A failed publish is retried whole, never
  trimmed".
