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

## Audit-doc fixes: the audit re-run leads Verification

A PR fixing an audit-doc failure is verified by re-running the audit on the record that failed,
with the fix in place. For Homeowner that is `HomeownerExcelQuoteAuditDiagnosticTests`, and for
Commercial it is `CommercialExcelQuoteAuditDiagnosticTests`. Each runs the audit's own rater fill
and `ComparePremium` on the record, so it is the audit itself, not a stand-in for it. That bullet
comes first in Verification and reads like this:

```markdown
- Re-ran the production audit on <policy number>, the policy whose audit failed, against a prod copy with <the fix>: passes. `<HomeownerExcelQuoteAuditDiagnosticTests | CommercialExcelQuoteAuditDiagnosticTests>` runs the audit's own rater fill and `ComparePremium` on that record, and <what the fix now reproduces>.
```

## Never editorialize against the change

The description states what the change does and why. It does not argue against itself. "Unrelated",
"drive-by", "while I was in there", "unfortunately", "admittedly", "hacky", "for now": each hands
the reviewer an objection they did not arrive with, and each is usually inaccurate too. A doc or
test change that came out of doing the work is a byproduct of the work, not a stranger to it.

Name what a rider is and what produced it. If something genuinely does not belong in the PR, take
it out instead of shipping it with an apology attached.

<!-- Added 2026-10-05 after #23242 -->
## Verification reports the end state

When a fix can't reach the tests that passed, the suite passed. Report one result with the fixed tests
counted as passed. Never list the failing run, and never mark untouched tests as not rerun.

- **What happened:** #23242 listed a fixed NY failure and said the other Commercial classes weren't rerun.

## Attaching screenshots to a PR

### A screenshot shows the change with a reasonable amount of the screen around it, outlined in red

- Never crop down to the changed element alone. Include enough of the surrounding screen that a
  reviewer sees where it sits and what is beside it, usually its section of the page.
- Outline the change in red. One screenshot per surface the change touches.
- Playwright MCP writes files only under the repo. Capture into `demos/` (gitignored), then copy to
  the ticket's `artifacts/pr/`.

#### Web page (Playwright MCP)

1. Sign in, so agent-only elements render:
   - `browser_navigate`: `https://localhost:5001/sign-in?redirect=<url-encoded page path>`
   - `browser_fill_form`: `#email-address` = `testbucket@swyfft.com`, `#password` = `swyfftrocks2`
   - `browser_click`: `#submit`
2. `browser_wait_for` the changed element's label text.
3. Close any open dialog by clicking its OKAY button.
4. Resize the viewport to the document height (`.claude/rules/frontend-styling.md` § "Tile
   Backgrounds and Full-Page PR Screenshots"). Otherwise Chromium paints the fixed page background
   only within the original viewport, and the capture comes out white below it.
   - `browser_evaluate`: `() => ({ scrollH: document.documentElement.scrollHeight, innerH: window.innerHeight, dpr: window.devicePixelRatio })`
   - `browser_resize`: width `1920`, height `Math.ceil(scrollH * dpr)`
   - Measure again. Repeat until `innerH` ≥ `scrollH`, or the gap between them stops shrinking.
5. Outline and capture with `browser_run_code_unsafe`. The outline is an overlay on `body`, so no
   parent element clips it. The clip is multiplied by `devicePixelRatio`; unscaled, it lands on the
   wrong rows. For a quote-page element, the box covers its row and its label:
   ```js
   async (page) => {
     const elementDisplayName = '<element display name>';
     const marginAboveAndBelow = 450;
     const outlinePadding = 6;
     const box = await page.evaluate(({ elementDisplayName, outlinePadding }) => {
       const row = document.querySelector(`[role=radiogroup][aria-label="${elementDisplayName}"]`).closest('.comparison-row');
       const label = [...document.querySelectorAll('div,span,label,p')]
         .find(e => e.childElementCount === 0 && e.textContent.trim() === elementDisplayName);
       const rects = [row.getBoundingClientRect(), label.getBoundingClientRect()];
       const left = Math.min(...rects.map(r => r.left)), top = Math.min(...rects.map(r => r.top));
       const right = Math.max(...rects.map(r => r.right)), bottom = Math.max(...rects.map(r => r.bottom));
       const overlay = document.createElement('div');
       Object.assign(overlay.style, {
         position: 'absolute', pointerEvents: 'none', zIndex: '2147483647', boxSizing: 'border-box', border: '3px solid red',
         left: `${left + scrollX - outlinePadding}px`, top: `${top + scrollY - outlinePadding}px`,
         width: `${right - left + 2 * outlinePadding}px`, height: `${bottom - top + 2 * outlinePadding}px`,
       });
       document.body.appendChild(overlay);
       return { top, height: bottom - top, width: innerWidth, dpr: devicePixelRatio };
     }, { elementDisplayName, outlinePadding });
     const clip = {
       x: 0,
       y: Math.max(0, box.top - marginAboveAndBelow) * box.dpr,
       width: box.width * box.dpr,
       height: (box.height + 2 * marginAboveAndBelow) * box.dpr,
     };
     await page.screenshot({ path: 'demos/<name>.png', clip, scale: 'css' });
   }
   ```
6. `Read` the PNG and confirm the outline and its surroundings are in it.

#### Printed quote (PDF)

1. On the Quote page, `browser_click` the `Print` button. The PDF downloads to `demos/`.
2. Render each page, and dump the word positions:
   ```sh
   pdftoppm -png -r 150 "demos/<pdf>" demos/printed-quote
   pdftotext -bbox-layout "demos/<pdf>" demos/printed-quote-bbox.html
   ```
3. In `printed-quote-bbox.html`, find each item's `<word xMin yMin xMax yMax>` entries, in points on a
   612 × 792 page. Pick a y-range and an x-range that enclose only that item's words.
4. Outline the items with the PowerShell tool. One `Get-WordsBox` call per item, with a 0-based page
   index:
   ```powershell
   Add-Type -AssemblyName System.Drawing
   $demos = "C:\Users\eli.koslofsky\Documents\GitHub\swyfft_web\demos"
   [xml]$bbox = (Get-Content "$demos\printed-quote-bbox.html" -Raw) -replace '<!DOCTYPE[^>]*>', ''
   $ns = New-Object System.Xml.XmlNamespaceManager($bbox.NameTable); $ns.AddNamespace('h', 'http://www.w3.org/1999/xhtml')
   $pages = $bbox.SelectNodes('//h:page', $ns)
   function Get-WordsBox($page, [double]$yFrom, [double]$yTo, [double]$xFrom, [double]$xTo) {
     $words = $page.SelectNodes('.//h:word', $ns) | Where-Object { [double]$_.yMin -ge $yFrom -and [double]$_.yMax -le $yTo -and [double]$_.xMin -ge $xFrom -and [double]$_.xMax -le $xTo }
     [pscustomobject]@{
       xMin = ($words | ForEach-Object { [double]$_.xMin } | Measure-Object -Minimum).Minimum
       yMin = ($words | ForEach-Object { [double]$_.yMin } | Measure-Object -Minimum).Minimum
       xMax = ($words | ForEach-Object { [double]$_.xMax } | Measure-Object -Maximum).Maximum
       yMax = ($words | ForEach-Object { [double]$_.yMax } | Measure-Object -Maximum).Maximum
     }
   }
   $pointsToPixels = 150 / 72; $paddingPoints = 4
   function Draw-Outlines($pngIn, $pngOut, $boxes) {
     $img = [System.Drawing.Image]::FromFile($pngIn); $g = [System.Drawing.Graphics]::FromImage($img)
     $pen = New-Object System.Drawing.Pen ([System.Drawing.Color]::Red), 4
     foreach ($b in $boxes) {
       $g.DrawRectangle($pen, [float](($b.xMin - $paddingPoints) * $pointsToPixels), [float](($b.yMin - $paddingPoints) * $pointsToPixels), [float](($b.xMax - $b.xMin + 2 * $paddingPoints) * $pointsToPixels), [float](($b.yMax - $b.yMin + 2 * $paddingPoints) * $pointsToPixels))
     }
     $g.Dispose(); $img.Save($pngOut, [System.Drawing.Imaging.ImageFormat]::Png); $img.Dispose()
   }
   Draw-Outlines "$demos\printed-quote-1.png" "$demos\<name>-page-1.png" @(Get-WordsBox $pages[0] <yFrom> <yTo> <xFrom> <xTo>)
   ```
5. `Read` each PNG and confirm the outlines sit on the items.

**Every PR screenshot is opened for Eli's approval before the PR is drafted.** Open it in Photos
through the PowerShell tool, `Start-Process "ms-photos:viewer?fileName=<full path>"`, only after
confirming the file is complete: in the same call, read its bytes and check the size is non-zero and
the first eight bytes are the PNG signature (`89-50-4E-47-0D-0A-1A-0A`), then open it. A bare
`Start-Process <path>` opens the machine's default `.png` app, which is the Snipping Tool. Treat the
screenshot as a draft under Gate 2: it goes into the PR only after he approves it. He judges the
image, so describing it in chat is never a substitute for showing it.

- **What happened:** SW-55350's screenshot was opened right after it was copied into the ticket
  folder, and the viewer would not load it. Eli had to ask for it to be opened again. Same failure
  as earlier tickets.
- **What happened:** SW-56006's screenshot passed the size and signature check and was opened three
  times with a bare `Start-Process`, which launched the Snipping Tool. Eli never saw it load
  properly. Opened in Photos, it loaded.

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

## "Stacked PRs" means GitHub's stacked pull requests feature

When Eli asks for stacked PRs, he means GitHub's native stacked pull requests, driven by the
`gh stack` CLI extension (`github/gh-stack`). Never a hand-built chain of PRs whose base is another
feature branch.

- Docs: https://docs.github.com/en/pull-requests/how-tos/stacked-pull-requests. That page is an
  index. The content is in its four linked pages: about, quickstart, CLI commands, and roll-out.
- A stack is one linear chain. The bottom PR targets `development`, each PR above targets the
  branch below it, and PRs merge bottom-up. Branching stacks are not supported.
- `development` has a merge queue, so merging a stack adds it to the queue.
