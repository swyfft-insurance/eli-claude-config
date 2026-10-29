# Investigation

## What to suspect, and what to read first

- **Never suspect established infrastructure.** Treat core Swyfft components (ClosedSets, DI, EF, equality operators) like Microsoft framework code: assume they work unless one is itself the subject of the feature or bug being worked on. A defect in one would fail hundreds of tests, not a handful.
- **Read the full inheritance chain**, base to leaf, before saying what a class does or doesn't override.

## Git history investigation

To find when or why something changed, always scope to a file or method. Never sweep whole-repo history; a hook blocks unscoped `git log -S` and bare `git log`. Prefer `/eli--file-history`. Commands:

- One method: `git log -L :MethodName:path/to/File.cs`
- Who changed lines: `git blame -L <start>,<end> -- path/to/File.cs`
- A string entering or leaving: `git log -S "<string>" -- path/to/File.cs`
- A file's history: `git log --follow -- path/to/File.cs`
- A branch's commits: `git log development..HEAD`

Every commit message starts with its `SW-XXXXX` ticket. If one doesn't, find its PR (`gh pr list --search "<sha>"`) and read the ticket there.
