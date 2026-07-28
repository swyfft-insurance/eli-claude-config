# Windows / Tooling

| Rule | Bad | Good | Why |
|---|---|---|---|
| Env vars with `=` | `printenv YOUTRACK_API_TOKEN` | `powershell -NoProfile -Command "[System.Environment]::GetEnvironmentVariable('YOUTRACK_API_TOKEN', 'User')"` | Bash silently truncates values containing `=` (common in base64 tokens) |
| No bash tee | `dotnet test \| tee output.txt` | `pwsh -NoProfile -Command "dotnet test 2>&1 \| Tee-Object -FilePath 'C:\Users\eli.koslofsky\.claude\tickets\<TicketFolder>\artifacts\tests\output.txt'"` | bash tee crashes on Windows; output belongs in the ticket's artifacts |
| No tail on background | `dotnet test 2>&1 \| tail -40` with `run_in_background` | `dotnet test` with `run_in_background: true`, no pipe | tail buffers everything, hides progress |
| Safe file moves | `mv source dest` | `cp source dest && ls dest && rm source` | mv silently fails on Windows — lost untracked analysis file |
| Windows paths in pwsh | `pwsh -Command "... '/tmp/file.txt'"` | `pwsh -Command "... 'C:\Users\eli.koslofsky\.claude\tickets\<TicketFolder>\artifacts\file.txt'"` | pwsh doesn't translate Unix paths; work product belongs in the ticket's artifacts, not Temp |
