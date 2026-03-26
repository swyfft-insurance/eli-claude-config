# CRITICAL: Tool Access
- YouTrack MCP tools and Slack MCP tools are DEFERRED tools — they MUST be loaded via ToolSearch before use
- NEVER tell the user you don't have access to YouTrack or GitHub. You DO have access — YouTrack via MCP, GitHub via `gh` CLI.
- If a tool call fails or you can't find a tool, use ToolSearch to load it. If still failing, ASK the user — do NOT just give up and claim the tool doesn't exist.

# Standup Notes
- YouTrack custom field is called "Stage" (not "State") — values include Develop, Review, Ready for Test, Done, Tested
- Attribute work to the day it ACTUALLY happened based on commit timestamps (ET timezone), don't shift things between days
- Standup has EXACTLY TWO sections: last working day and Today. Never add a third section (e.g. "Monday") — work from before the last working day is not included
- Don't reference internal epic labels/dates (e.g. "Feb 21 versioned changes") in standups — just describe the work
- GitHub username: eli-swyfft, YouTrack login: eli.koslofsky
- Slack #standup channel ID: C06ALP0GTHV
- CRITICAL: YouTrack search_issues returns INTERNAL IDs (2-XXXXX), not SW- numbers. After searching, call get_issue on any active/in-progress tickets (Stage: Develop, Review) to get their idReadable (SW-XXXXX) and include them in the standup. Do NOT skip this step.
- [feedback_standup_reread.md](feedback_standup_reread.md) — After gathering data, re-read the skill instructions before writing the standup output
- [feedback_standup_real_work.md](feedback_standup_real_work.md) — Only report actual work (commits, PRs, code) in standups, not ticket assignments or stage moves

# Behavioral Gates
- [feedback_gate_questions_not_actions.md](feedback_gate_questions_not_actions.md) — STOP: Questions are NOT instructions. Do not modify anything unless user uses imperative verb or explicit authorization.

# PR Reviews
- [feedback_pr_comments_draft.md](feedback_pr_comments_draft.md) — ALL public-facing content (PR comments, Slack, YouTrack comments) must be drafted and approved before posting

# Environment / Tooling
- [feedback_env_vars_equals_bash.md](feedback_env_vars_equals_bash.md) — Bash truncates env vars with = in values — ALWAYS read via PowerShell
- [feedback_youtrack_token_bash.md](feedback_youtrack_token_bash.md) — YOUTRACK_API_TOKEN specifically — always PowerShell, never bash