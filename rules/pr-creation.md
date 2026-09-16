# PR Creation

> Gate 2 applies here — see `core-behavior.md`.

- **Read the ticket first**: Before creating a PR, invoke `/eli--read-ticket` to read the YouTrack ticket(s) in the branch name.
- PR description from TWO sources: the ticket (already read above) + actual diff (`git diff development...HEAD`). Never from memory or plan files.
- **"Actual diff" means the full content diff, read at draft time.** A `--stat`/`-StatOnly` file list is NOT the diff — it names files without showing a single change. Earlier-in-session content reads are not the diff either: investigation reads are scoped to what that investigation needed, and every file not re-read ends up described from memory or the plan — exactly what this rule exists to prevent. Pull `/eli--diff branch` fresh and read every hand-written file's hunks before drafting.
- **Skip generated files by default.** Captured-assert expected-result files, EF migration designer
  snapshots (`*Designer.cs`), `*_Generated.cs`, and LFS-pointer binaries hold most of a large diff's
  line count and none of its intent, so reading them spends context for nothing. Split them out and
  read only the hand-written files. Read a generated file individually only when its content is
  itself the subject at hand, and then read only that one.
- Treat as ONE combined diff, not commit-by-commit. Iterative commits are not logical units.
- No Review Guide unless commits were structured via `/logical-commits`.
- Never claim test status without running or checking — plan files go stale.
- If YouTrack unavailable: STOP and ask about VPN. Don't guess ticket descriptions.
- **Multiline PR bodies**: The `block-prod-db.ps1` hook splits on newlines, so multiline `gh pr create --body "..."` or `gh pr edit --body "..."` triggers false positives. Use `--body-file` instead: write the body to the ticket's artifacts (`~/.claude/tickets/<TicketFolder>/artifacts/pr/`), then pass that file as a single-line command. Never a scratchpad/temp file — the PR body is ticket work product and stays with the ticket.
- **Request the `dev` team on every PR**: pass `--reviewer swyfft-insurance/dev` to `gh pr create`.
  Individual reviewers need no flag. `.github/auto_request_review.yml` requests them when the PR
  opens, from the `per_author` entry for `eli-swyfft` (`prebind-backend` plus `ken-swyfft`) and from
  any `files` glob the diff matches, and `.github/CODEOWNERS` adds its own path owners on top.
  Neither requests a *team*: `auto_request_review.yml` sets `enable_group_assignment: false`, so its
  groups expand to individuals, and `CODEOWNERS` lists no team handles. The team is the one part the
  flag is for. Requests are additive.
  The `auto_request_review.yml` workflow skips drafts and runs only on `feature/`, `bug/`, `test/`
  and `tests/` branches targeting `development`. Outside that shape its reviewers do not arrive,
  while `CODEOWNERS` is unaffected by those conditions.
- **Always hyperlink ticket refs; always cite the PR for prior code; prefer PRs over commits.** In every PR description: (a) every YouTrack ticket ID mentioned in the body must be a markdown link to the YouTrack issue (e.g., `[SW-49577](https://swyfft.myjetbrains.com/youtrack/issue/SW-49577)`); (b) every reference to *prior code* — an earlier fix, a previous commit's behavior, the code being reverted, etc. — must cite the GitHub PR number that introduced it via bare auto-link (e.g., `#19959`); (c) **prefer PR references over commit SHAs**. Only reference a specific commit when the PR alone isn't enough (e.g., one commit out of a multi-commit PR), and in that case cite BOTH — the commit SHA as a bare auto-link (`235a80eda15`, which GitHub auto-links) AND the PR number it came from (`#19959`).
- **Version ambiguity**: PR descriptions referencing "V1"/"V2" must qualify the numbering scheme (state config vs lookup vs generator). See `swyfft-domain.md` § "Generator and Lookup vs Config Versions".

## Length: the description covers what the diff cannot, and nothing else

A PR description exists to give the reviewer what the diff can't. That is a short list, so the
narrative prose is short. Budget the **narrative** — intent, surprises, blast radius:

- **Intent and blast radius: ~100 words total.** These don't scale with the size of the change.
- **Each surprise: up to 75 words, any quote included in the count.** Most PRs have zero or one
  surprise. Three is a lot.

So a no-surprise PR's narrative lands near 100 words and a three-surprise PR's near 325. Over budget
means cut content, not reflow it, and a long narrative has to be able to name which surprises it
spent on.

**Verification is exempt from the budget, not from brevity.** What ran and what it proves is
evidence, not prose, so per-suite names and counts belong there and the budget doesn't apply. The
form is one line per suite or check: what ran, the result, and at most a clause on what it proves.
Nothing wraps it — no lead-in paragraph, no summary after. A verification line that starts
explaining the code is narrative and gets cut or moved.

Three things earn a place in the narrative:

- **Intent** — what the change accomplishes, two or three sentences.
- **Surprises** — anything that makes a reviewer stop and ask "why did they do that?" A deviation
  from the ticket, an unrelated change riding along, a decision with a non-obvious alternative. This
  is the payload; if the description has one job, it is this.
- **Blast radius** — what else the change touches that its title doesn't suggest.

Two things belong only when they are load-bearing for judging the diff:

- **A quote from the ticket or Slack, when it is the authority for something in the diff.**
  Reviewers rarely open the ticket, and an acceptance criterion or a ruling is often the only thing
  that explains code that looks arbitrary or wrong. Quote it verbatim and keep it to the sentence
  that does the work. A quote restating intent the description already states in its own words earns
  nothing. When the surprise is a conflict between two sources, quote both, verbatim.
- **An explanation of existing machinery, when the change's correctness rests on it.** Say the one
  thing that matters. A tour of machinery no reviewer would question earns nothing.

Never include:

- **Mechanism the diff shows.** If the reviewer reads it in the code, don't narrate it.
- **A section per file or per component.** Structure by what's surprising, not by what's touched.

The test on every sentence: would the reviewer reach this on their own from the diff? Then cut it.

## Never editorialize against the change

The description states what the change does and why. It does not argue against itself. "Unrelated",
"drive-by", "while I was in there", "unfortunately", "admittedly", "hacky", "for now": each hands
the reviewer an objection they did not arrive with, and each is usually inaccurate too. A doc or
test change that came out of doing the work is a byproduct of the work, not a stranger to it.

Name what a rider is and what produced it. If something genuinely does not belong in the PR, take
it out instead of shipping it with an apology attached.

## Attaching screenshots to a PR

### The screenshot is the whole screen, with the change outlined in red

A PR screenshot shows the full web app viewport as the user sees it, never a crop of the changed
element. A crop strips the context a reviewer uses to judge the change: where it sits, what
surrounds it, whether it matches its neighbors. Draw a red outline around the element or region the
change touches so the reviewer finds it without hunting. One screenshot per surface the change
touches.

**Every PR screenshot is opened for Eli's approval before the PR is drafted.** Open it with
`Start-Process` through the PowerShell tool the moment it is saved, and treat it as a draft under
Gate 2: it goes into the PR only after he approves it. He judges the image, so describing it in chat
is never a substitute for showing it.

### Referencing and attaching

**Run the command below verbatim, from the repo root. The only thing that changes is the image
filename, the title and the ticket folder. No other flag form, path form or order.** Every variant
that was reasoned about instead of run has failed on a real PR (#22830). This form is proven on
#22710 and #22831.

The body references the image by bare filename; the flag gets `./<file>#<alt>`. gh rewrites the body
reference to the uploaded asset in place and keeps the alt text written in the body.

```markdown
## User Interface

![Confirmation page with the new element outlined in red](systems-update-attestation.png)
```

```sh
cp "$HOME/.claude/tickets/<ticket-folder>/artifacts/pr/systems-update-attestation.png" ./systems-update-attestation.png
gh pr create --base development --title "<title>" --body-file "$HOME/.claude/tickets/<ticket-folder>/artifacts/pr/body.md" --reviewer swyfft-insurance/dev --attach "./systems-update-attestation.png#<alt>"
rm ./systems-update-attestation.png
```

An absolute path in `--attach` is not rewritten: the image is appended after the last section and
the body reference stays broken (#22830).

## Every ticket the PR covers goes in the title

`youtrack-update-on-merge.yml` moves ticket stages off the `SW-XXXXX` IDs in the PR **title** — it
never reads the description. A covered ticket missing from the title silently never moves.

Every ticket in the body's `## Ticket Link` section gets its own `[SW-XXXXX]` in the title — the two
sets match exactly. A long title is not a reason to drop one. An epic never stands in for its
children; list every child the PR delivers.

Add the epic itself only when the PR delivers all of its children. Otherwise tag its Ticket Link
line `(partially delivered)`, which keeps it out of the title so its stage stays put.

A PR delivering part of a ticket that spans several PRs uses `Part N` in the title — the workflow
skips the YouTrack update entirely for those (`youtrack-update-on-merge.yml:44`).

- **What happened:** #22073 covered nine tickets; the title carried three. The epic SW-54113 stood
  in for its six per-state children, so AL, FL, LA, MA, NJ, and TX never left Develop.

Enforced by `~/.claude/hooks/pretooluse.py` on `gh pr create`. No bypass.

## Name the product line in the title

The product line goes in parens after the ticket brackets: `(HO)`, `(CO)`, `(Flood)`, `(DBB)`.
More than one — `(HO, CO)`. Then the ticket's `IssueType` in its own parens: `(Feature)`, `(Bug)`.
Brackets stay reserved for ticket IDs.

`[SW-54114] [SW-54115] (HO) (Feature) Aug 8, 2026 base rate updates for AL and FL`

Enforced by the same hook. Bypass with `# no-product-line` when the PR has no product line (build,
CI, tooling).
