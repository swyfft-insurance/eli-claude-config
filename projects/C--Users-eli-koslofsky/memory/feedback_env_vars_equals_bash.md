---
name: Bash truncates env vars containing equals signs
description: Bash/printenv/python os.environ silently truncate values with = characters — always read via PowerShell
type: feedback
---

Any environment variable whose value contains `=` characters (common in base64 tokens) will be silently truncated by bash, `printenv`, `env`, and even `python3 os.environ`. The returned value looks plausible but is incomplete.

**Why:** This has caused repeated runarounds where Claude insists the truncated value is correct and doubles down when the user corrects it. The partial value often looks valid (e.g. valid base64 prefix) so Claude doesn't realize it's incomplete.

**How to apply:** When an env var value might contain `=` (API tokens, base64-encoded values, connection strings), ALWAYS read via `powershell -NoProfile -Command "[System.Environment]::GetEnvironmentVariable('VAR_NAME', 'User')"`. Never trust bash for these. **Never argue with the user about it.**
