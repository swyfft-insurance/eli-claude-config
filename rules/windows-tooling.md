# Windows / Tooling

| Rule | Bad | Good | Why |
|---|---|---|---|
| Env vars with `=` | `printenv YOUTRACK_API_TOKEN` | `powershell -NoProfile -Command "[System.Environment]::GetEnvironmentVariable('YOUTRACK_API_TOKEN', 'User')"` | Bash silently truncates values containing `=` (common in base64 tokens) |
| Existing files | Use Write tool on existing `.cs` file | Use Edit tool | Write destroys CRLF line endings |
| New files | Write tool, walk away | Write tool, then fix CRLF: `python3 -c "..."` | Write creates LF-only, repo uses CRLF |
| No sed -i | `sed -i 's/foo/bar/' file.cs` | Use the Edit tool | Destroys CRLF on Windows |
| No bash tee | `dotnet test \| tee output.txt` | `pwsh -NoProfile -Command "dotnet test 2>&1 \| Tee-Object -FilePath 'C:\...\output.txt'"` | bash tee crashes on Windows |
| No tail on background | `dotnet test 2>&1 \| tail -40` with `run_in_background` | `dotnet test` with `run_in_background: true`, no pipe | tail buffers everything, hides progress |
| Safe file moves | `mv source dest` | `cp source dest && ls dest && rm source` | mv silently fails on Windows — lost untracked analysis file |
| Windows paths in pwsh | `pwsh -Command "... '/tmp/file.txt'"` | `pwsh -Command "... 'C:\Users\eli.koslofsky\AppData\Local\Temp\file.txt'"` | pwsh doesn't translate Unix paths |
