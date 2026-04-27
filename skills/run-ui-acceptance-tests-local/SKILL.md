---
name: run-ui-acceptance-tests-local
description: Run UI acceptance tests from swyfft_web on Eli's local machine via a single deterministic script. The script handles kill site → build solution → start site → wait for health → run tests → kill site (always, in finally). Pass filter args the same way Run-DotnetTest.ps1 takes them (-FilterMethod, -FilterClass, -FilterTrait, -FilterNamespace). Use this in interactive Claude Code when the test-runner MCP server is NOT running.
---

# Run UI Acceptance Tests (Local)

One command. The script `~/.claude/scripts/Run-WebUiAcceptanceTest.ps1` runs the full lifecycle as a single atomic operation. The website is killed in a `finally` block so it shuts down even if the build, health check, or test errors mid-flow.

## Filter args (required)

User invokes `/run-ui-acceptance-tests-local` with one or more of:
- `-FilterMethod "*MyTestName*"`
- `-FilterClass "*MyClass*"`
- `-FilterTrait "TestGroup=Critical"`
- `-FilterNamespace "Swyfft.Web.Ui.AcceptanceTests.Homeowner"`

If no filter is provided, STOP and ask the user before invoking — the script also refuses, but ask first to save startup time.

## Invocation

```bash
pwsh -NoProfile -File "$HOME/.claude/scripts/Run-WebUiAcceptanceTest.ps1" <FILTER_ARGS>
```

Set the Bash tool timeout to ~30 minutes (build can be 5–10 min on a cold cache, health up to 4 min, test up to 15 min).

## What the script does

| Step | Action | Failure mode |
|------|--------|--------------|
| 1 | Stop `Swyfft.Web` and `bun` processes | (none — best effort) |
| 2 | `Build-Solution.ps1 -Solution Swyfft.slnx` | exit non-zero, skip rest, run Step 7 |
| 3 | `RunSwyfftWeb.ps1` in a background `Start-Job` | (none — failure surfaces in Step 4) |
| 4 | Poll `https://localhost:5001` until 200 OK or 60s timeout (`-HealthTimeoutSec` to override) | exit 3, run Step 7 |
| 5 | `Run-DotnetTest.ps1 -Project ... -NoBuild` + filter args | test exit code propagates |
| 6 | List failure screenshots from `Path.GetTempPath() + test-failure-screenshots/` | only if Step 5 failed |
| 7 | **finally:** stop site processes, stop/remove the web job | always runs |

The script's exit code is the test's exit code (0 = pass), or 2 / 3 for infrastructure errors (no filter / health timeout).

## After the run

Read the script's stdout — it echoes each step header and the test's full output. Surface to the user:
- Pass/fail (the final `Test exit code: N` line)
- Any screenshot paths from Step 6
- The Step 7 confirmation that the site was killed
