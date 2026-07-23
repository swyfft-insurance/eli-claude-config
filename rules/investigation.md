# Investigation

> Gate 3 applies here — see `core-behavior.md`.

- **Never suspect established infrastructure.** Treat core Swyfft components (ClosedSets, SwyfftVersion, GetTableVersion, equality operators, DI, EF) the same as Microsoft framework code — assume they work unless there's a ticket explicitly changing them. If `==` or `GetTableVersion` were broken, hundreds of tests would fail, not 4. When something "seems wrong" with infrastructure, the bug is in YOUR code or YOUR understanding.
- **Check the full inheritance chain.** When investigating what a class does, read the ENTIRE chain from base to leaf — not just the leaf class. Claiming "this class doesn't override X" after only reading one file is wrong if you didn't read its parents.

## Git history investigation

When asked "when/why was X introduced", "find the ticket/PR for this code", or to trace a change:
**always scope to a file or method. NEVER sweep whole-repo history.** `git log -S "..."` with no
`-- <path>`, or a bare `git log` with no range/limit/path, walks every commit in the solution —
minutes wasted on an enterprise repo, for a question a scoped query answers instantly. You always
know which file you're asking about, so there is no excuse for an unscoped sweep. (A hook blocks the
unscoped shapes; scoped/bounded reads — `git blame`, `git show <sha>`, `git show <ref>:<file>`,
`git log <range>`, `git log --oneline -N`, `git log -- <path>` — stay free.)

Prefer the `/eli-file-history` skill — it runs the right scoped command and traces the ticket for you.
Canonical commands:
- One method's history:        `git log -L :MethodName:path/to/File.cs`
- Who/when changed lines:       `git blame -L <start>,<end> -- path/to/File.cs`
- When a string entered/left:   `git log -S "<string>" -- path/to/File.cs`
- A file's full history:        `git log --follow -- path/to/File.cs`
- A PR's / branch's commits:    `git log development..HEAD`

Every commit message starts with an `SW-XXXXX` prefix — that's the ticket. If one lacks it, find
its PR (`gh pr list --search "<sha>"` or the GitHub commit page) and read the ticket there.
