---
name: eli--file-history
description: Investigate git history for a SPECIFIC file, method, line range, or branch/PR — never the whole repo. Use when asked "when/why was X introduced", "find the ticket/PR for this code", "who changed this", or to review the commits on a branch/PR. Runs scoped git commands and traces each commit to its SW- ticket.
---

# File History

Answers history questions WITHOUT sweeping whole-repo history. A hook blocks unscoped `git log`
(no path/range/limit) — this skill runs the correctly-scoped command instead. Every command this
skill runs MUST end with the bypass token `# via-file-history-skill` (the hook lets it through).

> NEVER run `git log -S "..."` without a `-- <path>`, and never run a bare `git log` with no
> range/limit/path. That walks every commit in an enterprise solution — minutes wasted. There is
> no question that requires it; you always know the file, method, or range you care about.

## Pick the command by what's being asked

| The ask | Command (append `# via-file-history-skill`) |
|---|---|
| History of ONE method | `git log -L :MethodName:path/to/File.cs --format="%h\|%ai\|%s"` |
| Who/when changed specific LINES | `git blame -L <start>,<end> -- path/to/File.cs` |
| When a STRING entered/left a file | `git log -S "<string>" --format="%h\|%ai\|%s" -- path/to/File.cs` |
| When a string was ADDED/REMOVED by regex | `git log -G "<regex>" --format="%h\|%ai\|%s" -- path/to/File.cs` |
| A FILE's full commit history | `git log --follow --format="%h\|%ai\|%s" -- path/to/File.cs` |
| The commits on a BRANCH / PR | `git log development..HEAD --format="%h\|%ai\|%s"` |
| Inspect ONE commit's diff | `git show <sha>` |
| Read a file at a REF (PR review of others) | `git show <ref>:path/to/File.cs` |

`git blame` and `git show` are file/object-scoped and not blocked, but still append the token when
this skill runs them, for consistency.

Run via the PowerShell tool (Bash is flaky on this machine):
`git log -S "GroupAndSetEarliest" --format="%h|%ai|%s" -- path/File.cs # via-file-history-skill`

To find the ORIGINAL introduction, add `--reverse` and take the first row.

## Then: get the ticket — EVERY commit gets one, and you MUST read it

Every relevant commit MUST be reported with a ticket. Two steps, both mandatory.

### Step 1 — find the ticket number

1. **Commit message starts with `SW-XXXXX`** — that's the candidate ticket.
2. **No `SW-` prefix** (refactor commits, merges, "Fix typo", etc.) — the ticket is NOT gone, it's
   on the PR. Run this BEFORE you write a single word of your report:
   ```
   gh pr list --search "<sha>" --state all --json number,title,url,mergedAt
   ```
   The PR title almost always carries the `[SW-XXXXX]`. Use PR number + ticket.

> **BANNED OUTPUT — never write any of these:** "no ticket to link", "carries no SW- prefix so
> there's no ticket", "couldn't find a ticket", "no associated ticket". A missing `SW-` prefix in
> the commit message is NOT a missing ticket — it means you have not yet run `gh pr list --search`.
> Run it. If the PR genuinely has no `SW-`, report the PR number itself as the forwarding address.

### Step 2 — READ the ticket before citing it (non-negotiable)

A commit's ticket tag tells you which ticket *touched* the file — it does NOT tell you the ticket is
*about* that code. Commits routinely change many files for one reason; the file you care about may be
incidental to the ticket's real subject. Before you cite a ticket as the reason/origin/provenance of
any code, READ IT:

```
PYTHONIOENCODING=utf-8 python ~/.claude/skills/eli--read-ticket/read-ticket.py <SW-XXXXX>
```
(or `/eli--read-ticket`). Confirm the ticket's actual subject matches the claim you're about to make.

> **BANNED OUTPUT — never describe, summarize, or attribute a purpose to a ticket you have not read
> this session.** Writing "since ~Oct 2020 (SW-13077, the FL E&S calculator)" without reading
> SW-13077 is the exact failure this rule exists to stop — SW-13077 turned out to be an archived TX
> *Diligent Effort form* ticket that merely touched the fee file in passing. If you have not read it,
> write "commit `<sha>` touched this file; I have not yet read its ticket" — never invent the
> ticket's subject from the filename or the commit's diff.

**Archived-ticket trap:** old tickets get renumbered into the archive project (`SW-XXXX` →
`SWA-XXXX`) and the YouTrack link redirects to the archived issue, whose title may describe a
*different* sub-feature than the code you traced. Reading the ticket is the only way to catch this.

Do NOT fall back to reading broad history.

## GitHub links — build them right, verify before emitting

Any GitHub link in the report MUST resolve and MUST highlight the relevant lines. A link you have
not verified is a link that does not work. The repo is **private**, so you cannot HTTP-test it —
git IS the test. Verify every component with git BEFORE you paste the link.

Link shape:
```
https://github.com/swyfft-insurance/swyfft_web/blob/<FULL-40-char-sha>/<path-AT-that-commit>#L<start>-L<end>
```

Three things break these links — check all three, every time:

1. **FULL 40-char SHA**, never the abbreviated form (abbreviated SHAs 404 in `blob` URLs):
   ```
   git rev-parse <shortsha>          # -> full sha
   ```
2. **The path AS IT EXISTED AT THAT COMMIT**, not today's path. Files get renamed / moved / copied /
   deleted, so the current path often does not exist at an old commit. Find the historical path with
   `git log --follow --name-status ...`, then CONFIRM it resolves in that commit's tree:
   ```
   git cat-file -e "<fullsha>:<path-at-that-commit>"   # exit 0 = exists; error = link will 404
   ```
3. **Line range** `#L<start>-L<end>`: use the real line numbers of the code AT THAT COMMIT (from
   `git blame -L` or by viewing the file at the ref). Do NOT reuse line numbers from today's version
   — the file may have a different length/layout at the old commit.

Only paste a link after `git rev-parse` (full sha) AND `git cat-file -e` (path) both succeed. Append
`# via-file-history-skill` to these verification commands like every other command this skill runs.

## Report

For each relevant commit, report:
- **GitHub permalink** — full-SHA blob URL with the line range highlighted, verified per "GitHub
  links" above (rev-parse + cat-file both passed).
- Date and one-line commit summary.
- **The ticket — read, not just referenced.** Link it, and only state its purpose if you read it
  this session (per "get the ticket"). If you couldn't read it, say so explicitly.

When the ask is "when was X introduced", lead with the single introducing commit + its read-and-
confirmed ticket.
