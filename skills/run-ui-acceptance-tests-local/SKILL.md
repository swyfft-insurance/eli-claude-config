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

## Optional flags

- `-NoBuild` — skip Step 2 (build). Use when you're confident the build is already current. Saves 5–10 minutes on a cold cache, seconds on incremental.

## Invocation

```bash
pwsh -NoProfile -File "$HOME/.claude/scripts/Run-WebUiAcceptanceTest.ps1" <FILTER_ARGS> [-NoBuild]
```

Set the Bash tool timeout to ~30 minutes when building (build 5–10 min + health up to 1 min + test up to 15 min). With `-NoBuild`, ~20 minutes is plenty.

## What the script does

| Step | Action | Failure mode |
|------|--------|--------------|
| 1 | Stop `Swyfft.Web` and `bun` processes | (none — best effort) |
| 2 | `Build-Solution.ps1 -Solution Swyfft.slnx` (skipped if `-NoBuild`) | exit non-zero, skip rest, run Step 7 |
| 3 | `RunSwyfftWeb.ps1` in a background `Start-Job` | (none — failure surfaces in Step 4) |
| 4 | Poll `https://localhost:5001` until 200 OK or 60s timeout (`-HealthTimeoutSec` to override) | exit 3, run Step 7 |
| 5 | `Run-DotnetTest.ps1 -Project ... -NoBuild` + filter args | test exit code propagates |
| 6 | List failure screenshots from `Path.GetTempPath() + test-failure-screenshots/` | only if Step 5 failed |
| 7 | **finally:** save web stdout to a file, stop/remove the web job, stop site processes | always runs |

The script's exit code is the test's exit code (0 = pass), or 2 / 3 for infrastructure errors (no filter / health timeout).

## Output locations

Both files land in `%TEMP%\swyfft-tests\` and survive after the script exits.

| What | Path | Notes |
|------|------|-------|
| Test output (text + TRX) | `%TEMP%\swyfft-tests\{branch}_{project}_{filters}_{timestamp}.txt` and `.trx` | **Same location and naming as any other test run via `Run-DotnetTest.ps1`.** This script delegates Step 5 to Run-DotnetTest.ps1, so the location is consistent across all tests. |
| Website stdout | `%TEMP%\swyfft-tests\Run-WebUiAcceptanceTest_{timestamp}_website.txt` | What `Swyfft.Web` printed during the test — written **every run** (pass or fail). Always read this when diagnosing a failure: backend exceptions (e.g., the SW-50063 KeyNotFoundException) only surface here. The script also tails the last 50 lines to stdout. |

Failure screenshots, when produced (only on Playwright element timeouts — not on assertion failures inside `ClickOptionButtonAndVerify`), still go to `%TEMP%\test-failure-screenshots\{TestMethodName}.png` per `PlaywrightTestBase.cs:107-113`.

## After the run

Read the script's stdout — it echoes each step header and the test's full output. Surface to the user:
- Pass/fail (the final `Test exit code: N` line)
- The website stdout file path (always saved; quote relevant exceptions on failure)
- Any screenshot paths from Step 6
- The Step 7 confirmation that the site was killed
