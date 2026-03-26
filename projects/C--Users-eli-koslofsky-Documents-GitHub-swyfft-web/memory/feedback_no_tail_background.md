---
name: No tail/head on background commands
description: Never pipe background bash commands through tail or head — it buffers all output until completion, making progress invisible
type: feedback
---

Never pipe background commands through `tail`, `head`, or other buffering filters. `tail` waits for all input before producing output, so the output file stays empty until the entire pipeline finishes — you can't monitor progress.

**Why:** A `dotnet test ... 2>&1 | tail -40` run as a background task produced zero output for 10+ minutes, making it impossible to tell if tests were running, stuck, or failed. The user had to wait with no feedback.

**How to apply:** For background tasks (`run_in_background: true`), run the command directly without piping. For foreground commands where you only need the summary, `tail` is fine since you'll see output when it completes.
