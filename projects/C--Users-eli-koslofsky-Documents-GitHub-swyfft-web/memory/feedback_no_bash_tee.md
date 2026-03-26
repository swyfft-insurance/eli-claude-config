---
name: Use pwsh for tee output, not bash
description: bash tee crashes on Windows — always use pwsh Tee-Object with Windows paths for capturing test output
type: feedback
---

NEVER use bash `tee` to capture dotnet test output. Git bash's `tee` frequently crashes with "fatal error - add_item" on Windows.

**Why:** bash tee crashes randomly on this machine. Has happened repeatedly. The user has to ask "what does git bash have to do with running tests?" every time.

**How to apply:**
- Use `pwsh -NoProfile -Command "dotnet test ... 2>&1 | Tee-Object -FilePath 'C:\Users\eli.koslofsky\AppData\Local\Temp\swyfft-tests\filename.txt'"`
- Use WINDOWS paths (not `/tmp/...`) — pwsh doesn't translate Unix paths
- Create the directory first: `pwsh -NoProfile -Command "New-Item -ItemType Directory -Force -Path 'C:\Users\eli.koslofsky\AppData\Local\Temp\swyfft-tests'"`
