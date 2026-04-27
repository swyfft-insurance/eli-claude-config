---
name: background-tasks
description: List running and completed background tasks/agents in the current and past Claude Code sessions. Use when you lose track of agents after context compaction or need to check what's still running.
---

# Background Tasks

Lists background task output files from Claude Code sessions. Useful after context compaction when you've lost track of running agents.

## Usage

No arguments required. Just invoke the skill.

## Steps

### 1. Run the script (default — most recent session per CWD)

```bash
pwsh -NoProfile -File "$HOME/.claude/scripts/List-BackgroundTasks.ps1"
```

### 2. If the user asks for all sessions or a specific session

```bash
# All sessions across all CWDs:
pwsh -NoProfile -File "$HOME/.claude/scripts/List-BackgroundTasks.ps1" -All

# Specific CWD only:
pwsh -NoProfile -File "$HOME/.claude/scripts/List-BackgroundTasks.ps1" -Cwd "C:\Users\eli.koslofsky\Documents\GitHub\swyfft-web"

# Specific session UUID:
pwsh -NoProfile -File "$HOME/.claude/scripts/List-BackgroundTasks.ps1" -SessionId "6bc142ab-b2f1-45c2-84a5-0bbb97340f28"
```

### 3. Interpret the output

| Status | Meaning |
|--------|---------|
| `done` | Output file has content — agent completed and wrote results |
| `RUNNING?` | 0-byte file in the most recent session — likely still active |
| `no output` | 0-byte file in an older session — agent completed but didn't persist output to disk (normal for Agent-type tasks that return results directly to the conversation) |

### 4. Check a specific task

If you need to check a `RUNNING?` task, use `TaskOutput` with `block=false`:

```
TaskOutput(task_id="<id>", block=false, timeout=5000)
```

Note: `TaskOutput` only works for tasks in the **current** conversation instance. Tasks from other sessions or pre-compaction tasks will return "No task found".
