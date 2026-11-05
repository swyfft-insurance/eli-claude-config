---
name: eli--code-complete-audit
description: Audit a code diff against every personal rules file, the repo's root AGENTS.md, and the repo's .NET .claude/rules files, one pass per rule file with a verdict per section that names every object it governs, fixing violations in place. Hands back the corrected code.
---

# Code-Complete Audit

Audits the diff whole. **The diff is guilty until proven clean.** A rule section with no recorded
verdict has not been audited. If a pass finds nothing, be suspicious of the pass.

This skill holds the procedure only. It restates no rule, because the passes reach every section of
the files they walk, and a local copy would both duplicate and go stale.

## Invocation

```
/eli--code-complete-audit <ticket-folder>
```

The ticket folder is required. With no arg, stop and ask.

## 0. Pull the diff

Run `/eli--diff all`: everything the branch carries against `origin/development`, committed,
uncommitted and untracked alike. The passes walk every added or changed line, comment, identifier
and test in it.

On a PR-feedback fix, audit `/eli--diff local` only. The committed branch was already audited and
approved. A violation on a line outside that diff goes to Eli and is never edited.

## 1. Derive the passes at run time

The governing files, in pass order:

- every `~/.claude/rules/*.md` whose frontmatter `audited-by` names `code-complete`
- the repo's root `AGENTS.md`
- every `.claude/rules/*.md` in the repo except `frontend-*.md`, `powershell.md`, `teamcity.md`
  and `openapi-spec.md`

`audit-files.sh`, beside this file, prints that list. It reads `~/.claude/rules/` and the repo's
`.claude/rules/` when it runs, so a rule file added to either is audited without editing this skill.

One pass per file. A file's sections are its `##` headings, derived when the skill runs, never from
a list written here:

```bash
bash ~/.claude/skills/eli--code-complete-audit/audit-files.sh | xargs -d '\n' grep -Hn '^## '
```

**A repo rule file the diff can't touch gets no pass.** When none of the `paths` globs in a repo
`.claude/rules/*.md` file's frontmatter matches a file in the diff, record one row,
`<file name> :: no file in the diff matches its paths`, naming the globs, and skip the file. A file
with no `paths` frontmatter always gets a pass.

**Every personal rules file declares `audited-by`.** Its YAML frontmatter lists the audits that walk it
(`audited-by: [code-complete]`, or `audited-by: []`). A `NO AUDITED-BY` line from `section-guard.sh`
fails the audit.

A conflict between a repo file and a personal rule is a hard stop (§ 2, step 4). `frontend-*.md` is left
out because Eli does not work frontend tickets. `powershell.md`, `teamcity.md` and
`openapi-spec.md` are left out too. Nothing else under the repo is read by this skill, subsystem
`AGENTS.md` files included. Where a rule points at one of those, the pointer stays for the human
reader and this skill does not follow it.

## 2. Run the passes

Each run starts a new `## Run <date and time>` section in
`~/.claude/tickets/<ticket-folder>/artifacts/code-complete-audit.md`, and writes its rows there.
The file is never shown to Eli.

For each pass, in order:

1. `Read` the whole file, with an actual Read call, immediately before the pass. Not from memory,
   not from the rules loaded at session start, not from having read it for an earlier pass.
2. Take its sections in order. A section that describes a workflow rather than the code (a HARD
   STOP sequence, a TDD ordering) gets the verdict **N/A** with the reason. Walk every other
   section against every object in the diff it governs.
3. Write one row per section, labeled `<file name> :: <heading>` (`csharp-patterns.md ::
   ClosedSets`). Several files share headings, so the file name is what tells their rows apart. The
   row names each object the section governs and that object's verdict: **Satisfied**, or
   **Violated** with the fix applied. A row that names no object ("nothing in the diff violates
   it") is not a verdict, and neither is "the rest are fine". No sampling.
4. Fix every violation in this pass before starting the next, so later passes see the corrected
   code. A fix that would change an approved design, or that the rule leaves to Eli, is a hard
   stop, not a silent edit. So is a conflict between a repo rule and a personal rule: quote both,
   recommend the personal one, and wait for Eli's ruling on which side changes
   (`~/.claude/rules/meta.md` § "Loading Priority Order").
5. Re-read this skill file before the next pass.

Within `comments-docs-and-external-writing.md`, the section holding the comment self-audit runs first
(its question 1, "should this comment exist at all?", deletes before anything else judges wording);
the remaining sections then run over the surviving comments.

**Prove every section got a row in this run, mechanically.** After the last pass, run from the repo root:

```bash
bash ~/.claude/skills/eli--code-complete-audit/section-guard.sh <ticket-folder>
```

Any `MISSING` line fails the audit: walk that section and rerun until nothing prints. A
`NO SECTIONS` line means a governing file has no `##` heading, so none of its rules got a verdict.
That is a hard stop: tell Eli which file.

## 3. Terminate

After the last pass, run the line-length gate (`~/.claude/scripts/Test-LineLength.ps1 -Mode branch`,
then `-Mode local` for anything uncommitted) and re-walk every section whose fixes touched code. Stop
when a full pass records zero violations.

## 4. Output

The corrected code is the output. Findings are never shown to Eli: no verdict table, no counts, no
list of what was violated or fixed, no mention that the audit ran.

Two things still reach him:

- **A hard stop**, when a fix would change an approved design, the rule leaves the call to him, or
  a repo rule conflicts with a personal rule. Say what is blocked, nothing else. For a conflict,
  that means both rules quoted and the recommendation.
- **The build or test consequence**, in one line: whether the fixes contain an executable change,
  since a comment-only or rename-only pass never justifies a re-run.
