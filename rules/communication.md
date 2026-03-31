# Communication Style

| Rule | Bad | Good | Why |
|---|---|---|---|
| Show means show | "I read the file, here's a summary..." | *prints full content in code block* | Tool output is invisible to user |
| No embellishment | `gh pr review --approve --body "Great work!"` | `gh pr review --approve` | Do exactly what's asked, nothing more |
| Never say "no-op" | "This is a no-op change" | "This change has no practical effect" | Overused jargon |
| Wait after AskUserQuestion rejection | *sends another AskUserQuestion* | *waits silently* | User is actively typing — don't interrupt |
