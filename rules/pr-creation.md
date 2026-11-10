---
audited-by: []
---

# PR Creation

## Filing the PR

- No Review Guide unless the commits were structured with `/logical-commits`.
- **The body goes in a file**: write it to `~/.claude/tickets/<TicketFolder>/artifacts/pr/` and pass `--body-file`. Never a multiline `--body`, and never a scratchpad file.
- **Request the `dev` team on every PR**: pass `--reviewer swyfft-insurance/dev` to `gh pr create`. Individual reviewers need no flag: `.github/auto_request_review.yml` (the `per_author` entry for `eli-swyfft`, plus `files` globs) and `.github/CODEOWNERS` add them, but neither requests a team. Requests are additive. That workflow skips drafts and runs only on `feature/`, `bug/`, `test/` and `tests/` branches targeting `development`. `CODEOWNERS` always applies.
- **Link tickets, cite PRs for prior code.** Every ticket ID in the body is a link (`[SW-49577](https://swyfft.myjetbrains.com/youtrack/issue/SW-49577)`). Every reference to prior code cites the PR that introduced it as a bare auto-link (`#19959`). Cite a commit SHA (`235a80eda15`) only when the PR alone isn't enough, and then cite its PR too.

## Writing the PR description

Read the plan in its entirety, Progress included. The plan is based on a read of the ticket and outlines exactly what we did and why, with the hurdles, key decisions and bumps along the road recorded. It is the story of the pull request.

The PR is the final unit. The description gives the final state of what we produced, never the intermediary steps:
- **What we did**, explained briefly.
- **Why**, including each key decision a reviewer needs and why it was made.
- **Also in this PR** (optional): smaller changes that aren't key decisions but would make a reviewer ask why, each with its why. A PR with no such changes has no Also in this PR section.
- **Verification**: one line per suite or check, saying what ran and the result.

Keep it short, about 150 words before Verification, but never at the cost of meaning. Every item makes sense on its own to a reviewer who hasn't read the plan, and states its why in full.

Every claim is fact-checked against the code before the description is shown. `/eli--audit-pr-desc` runs that check.

## Audit-doc fixes: the audit re-run leads Verification

A PR fixing an audit-doc failure is verified by re-running the audit on the record that failed, with the fix in place: `HomeownerExcelQuoteAuditDiagnosticTests` for Homeowner, `CommercialExcelQuoteAuditDiagnosticTests` for Commercial. That bullet comes first in Verification:

```markdown
- Re-ran the production audit on <policy number>, the policy whose audit failed, against a prod copy with <the fix>: passes. `<HomeownerExcelQuoteAuditDiagnosticTests | CommercialExcelQuoteAuditDiagnosticTests>` runs the audit's own rater fill and `ComparePremium` on that record, and <what the fix now reproduces>.
```

## Never editorialize against the change

Never call any part of the change "unrelated", "drive-by", "while I was in there", "unfortunately", "admittedly", "hacky" or "for now". Name what a rider is and what produced it. If something doesn't belong in the PR, take it out.

## Verification reports the end state

Verification reports the PR's state when it is opened. Fixes after that follow `pr-mine-address-feedback.md` § "The PR description is a snapshot of the PR as opened".

When a fix can't reach the tests that already passed, report one passing result with the fixed tests counted. Never list the failing run, and never mark untouched tests as not rerun.

## Attaching screenshots to a PR

**A PR gets a screenshot only when Eli asks for one.** Never plan, capture or attach one otherwise, whatever the change shows. The rest of this section applies once he has asked.

### A screenshot shows the change with a reasonable amount of the screen around it, outlined in red

- One screenshot per surface the change touches, showing enough of the screen to see where the change sits, usually its section of the page. Never crop to the element alone.
- Playwright MCP writes files only under the repo. Capture into `demos/` (gitignored), then copy to the ticket's `artifacts/pr/`.

#### Web page (Playwright MCP)

1. Sign in, so agent-only elements render:
   - `browser_navigate`: `https://localhost:5001/sign-in?redirect=<url-encoded page path>`
   - `browser_fill_form`: `#email-address` = `testbucket@swyfft.com`, `#password` = `swyfftrocks2`
   - `browser_click`: `#submit`
2. `browser_wait_for` the changed element's label text.
3. Close any open dialog by clicking its OKAY button.
4. Resize the viewport to the document height, or the page background renders white below the original viewport (`.claude/rules/frontend-styling.md` § "Tile Backgrounds and Full-Page PR Screenshots"):
   - `browser_evaluate`: `() => ({ scrollH: document.documentElement.scrollHeight, innerH: window.innerHeight, dpr: window.devicePixelRatio })`
   - `browser_resize`: width `1920`, height `Math.ceil(scrollH * dpr)`
   - Measure again. Repeat until `innerH` ≥ `scrollH`, or the gap between them stops shrinking.
5. Outline and capture with `browser_run_code_unsafe`. For a quote-page element, the box covers its row and its label:
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
2. Render each page and dump the word positions:
   ```sh
   pdftoppm -png -r 150 "demos/<pdf>" demos/printed-quote
   pdftotext -bbox-layout "demos/<pdf>" demos/printed-quote-bbox.html
   ```
3. In `printed-quote-bbox.html`, find each item's `<word xMin yMin xMax yMax>` entries, in points on a 612 × 792 page. Pick a y-range and an x-range that enclose only that item's words.
4. Outline the items with the PowerShell tool, one `Get-WordsBox` call per item, with a 0-based page index:
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

**Every PR screenshot is opened for Eli's approval before the PR is drafted.** In one PowerShell call, check the file's size is non-zero and its first eight bytes are the PNG signature (`89-50-4E-47-0D-0A-1A-0A`), then open it with `Start-Process "ms-photos:viewer?fileName=<full path>"`. A bare `Start-Process <path>` opens the Snipping Tool. The screenshot is a draft under Gate 2: it goes into the PR only after he approves the image itself, never a description of it.

### Referencing and attaching

Run the commands below verbatim from the repo root, changing only the image filename, the title and the ticket folder. The body references the image by bare filename and the flag gets `./<file>#<alt>`. An absolute path in `--attach` is not rewritten, and the body reference breaks.

```markdown
## User Interface

![Confirmation page with the new element outlined in red](systems-update-attestation.png)
```

```sh
cp "$HOME/.claude/tickets/<ticket-folder>/artifacts/pr/systems-update-attestation.png" ./systems-update-attestation.png
gh pr create --base development --title "<title>" --body-file "$HOME/.claude/tickets/<ticket-folder>/artifacts/pr/body.md" --reviewer swyfft-insurance/dev --attach "./systems-update-attestation.png#<alt>"
rm ./systems-update-attestation.png
```

## Every ticket the PR covers goes in the title

`youtrack-update-on-merge.yml` moves ticket stages using only the `SW-XXXXX` IDs in the PR title. The title and the body's `## Ticket Link` section carry the same tickets, each in its own `[SW-XXXXX]`, however long the title gets. An epic never stands in for its children: list every child the PR delivers, and add the epic only when the PR delivers all of them. Otherwise tag the epic's Ticket Link line `(partially delivered)` and leave it out of the title. A PR delivering part of a multi-PR ticket uses `Part N` in the title, which skips the YouTrack update (`youtrack-update-on-merge.yml`). Enforced by `~/.claude/hooks/pretooluse.py` on `gh pr create`. No bypass.

## Name the product line in the title

After the ticket brackets: the product line in parens (`(HO)`, `(CO)`, `(Flood)`, `(DBB)`, or `(HO, CO)`), then the ticket's `IssueType` in parens (`(Feature)`, `(Bug)`). Brackets are only for ticket IDs.

`[SW-54114] [SW-54115] (HO) (Feature) Aug 8, 2026 base rate updates for AL and FL`

Enforced by the same hook. Bypass with `# no-product-line` when the PR has no product line (build, CI, tooling).

## "Stacked PRs" means GitHub's stacked pull requests feature

Driven by the `gh stack` CLI extension (`github/gh-stack`), never a hand-built chain of PRs based on feature branches. Read before any `gh stack` command: https://docs.github.com/en/pull-requests/get-started/about-stacked-prs, https://docs.github.com/en/pull-requests/get-started/stacked-prs-quickstart, https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands, https://docs.github.com/en/pull-requests/tutorials/roll-out-stacked-prs. A stack is one linear chain: the PR that merges first targets `development`, each later PR targets the branch of the PR that merges just before it, and they merge in that order through `development`'s merge queue. Branching stacks are not supported.

- **Describe a stack by merge order: "merges first", "merges second" and so on.** Never "bottom", "top", "above" or "below", even though GitHub's docs and `gh stack` output use them. Name each PR as `talking-to-eli.md` § "Ticket numbers: never bare" requires.
- **In most cases, the older PR merges first.** Merging a newer PR first makes the older one wait on the newer one's review and fixes.
