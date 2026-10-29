# Windows / Tooling

## Bash on Windows

- Bash truncates env var values containing `=`. Read them with `powershell -NoProfile -Command "[System.Environment]::GetEnvironmentVariable('YOUTRACK_API_TOKEN', 'User')"`, not `printenv`.
- Bash `tee` crashes on Windows. Use pwsh `Tee-Object` with a Windows path in the ticket's artifacts.
- Never pipe a background command through `tail`. It buffers everything and hides progress.
- `mv` fails silently on Windows. Use `cp source dest && ls dest && rm source`.

## pwsh paths

- pwsh doesn't translate Unix paths. Give it Windows paths, and put work product in the ticket's artifacts, not Temp.
