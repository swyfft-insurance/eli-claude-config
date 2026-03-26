---
name: YouTrack token truncated by bash
description: YOUTRACK_API_TOKEN contains base64 with == — always read via PowerShell, never bash
type: feedback
---

`YOUTRACK_API_TOKEN` contains `==` in its base64 segments. Bash silently truncates it, returning a partial token that fails auth. This is the most common instance of the general env-var-equals-truncation issue.

**Why:** This specific case has happened many times and wastes minutes every time.

**How to apply:** ALWAYS use `powershell -NoProfile -Command "[System.Environment]::GetEnvironmentVariable('YOUTRACK_API_TOKEN', 'User')"` to read the token. See also `feedback_env_vars_equals_bash.md` for the general rule.
