---
paths:
  - "**/Homeowner/ByPeril/**/*.xlsm"
  - "**/ByPerilSeederHomeowner*.cs"
  - "**/ByPerilHomeowner*ExcelRaterService*.cs"
  - "**/HomeownerStateConfig/**"
  - "**/Commercial/EAndS/**/*.xlsm"
  - "**/ByPerilSeederCommercialEAndS*.cs"
  - "**/CommercialEAndS*.cs"
  - "**/CommercialStateConfig.cs"
---
# Excel Rater (ByPeril) — Shared Conventions

Applies to both rater playbooks: HO (`ho-excel-rater-plans.md`) and Commercial (`co-excel-rater-plans.md`). Each inherits everything here and holds only its own product's differences.

Both products run one Excel test infrastructure: a shared validation base, the same config sampling, the same captured-assert baselines, the same element sweep, and the same sentinel checks. Anything about that infrastructure belongs here, never in a product playbook.

## Rater edits — when warranted, and the SharePoint flow (MANDATORY)

<!-- Rewritten 2026-09-11 during SW-54689 — the old "only for actual rater bugs" test forbade a
     reconciliation Eli has actually chosen, and never asked whether the config was live. The
     decision itself now lives in the repo doc; only the agent-behavior guard stays here -->
**When a rater edit is warranted, and how a C#-vs-rater discrepancy is reconciled, live in
`Swyfft.Services/Premium/AGENTS.md` § "The rater is the acceptance criteria". Read it before proposing
either.**

**This is never the agent's call to make, and never a shortcut.** Leaning on a rater edit as the
easy way out of a C#-vs-rater discrepancy is a known agent failure mode. Present the discrepancy,
the config's live status, and both options. Eli decides.

**The repo `Data\` copy is NOT the source of truth — the actuaries' SharePoint copy is.** The actuaries don't work out of the Swyfft solution's `Data` folder; an edit made only in the repo gets blown away the next time they deliver a rater. `#dev-analytics-rater-handoff` exists to coordinate rater changes from both ends.

<!-- Added 2026-09-09 during SW-55584 — Eli had to supply the SharePoint address himself -->
**Where the raters live.** Site `swyfft-developmentsite`, library `Shared Documents`:

| Product line | Folder |
|---|---|
| Homeowner | `https://swyfft2.sharepoint.com/sites/swyfft-developmentsite/Shared%20Documents/By-Peril/<STATE>` |
| Commercial EandS | `https://swyfft2.sharepoint.com/sites/swyfft-developmentsite/Shared%20Documents/E%26S/<STATE>` |

The actuaries post every delivery as a link in `#dev-analytics-rater-handoff` (`C06V258BWHJ`), which
is where to find a file whose folder these two rows don't cover.

**Who to tag.** The channel is `#dev-analytics-rater-handoff` (`C06V258BWHJ`). Two on the actuarial
side:

- **Blake Smith** (`U019J5G7UTF`), the actuaries' leader, on every rater change.
- **The actuary who delivered the rater in hand.** It varies per rater and per delivery. Find them
  by reading the channel for the delivery post carrying that rater's SharePoint link. Alex
  Terragnoli (`U03JA79NY8L`) posts many of them. The rater's own `version_history` tab has an
  `Analyst` column naming who made each change, which cross-checks the channel.
- **Ehren** (`U1F5C7Q3W`), the pre-bind manager, on every message, tagged or cc'd.

**Name the product line in the first sentence, every time.** The channel carries both Homeowner and
Commercial raters, and the same state and carrier exist in both: NY QBE has
`HO_ES_QBE_NY_Rater.xlsm` and `CO_ES_QBE_NY_Rater.xlsm`. "The QBE NY rater" therefore names nothing,
and the actuaries have to guess which product they are being asked about. Say Homeowner or
Commercial up front, name the rater file, and repeat the product line wherever the message names a
state, a carrier or a config. This applies to every message and every reply in that channel.

The flow when a rater edit is warranted:

1. **The edit is made on SharePoint, by a human.** Eli usually makes it himself directly on SharePoint; routing the change to the actuaries instead is always a valid option (some devs prefer it).
2. **The agent prepares the edit; it NEVER applies one.** Programmatic edits of rater `.xlsm` files by the agent are banned.
   <!-- Rewritten 2026-09-09, SW-55584 -->
   Eli copies each value in one action. Markdown tables are banned: the terminal draws them with
   borders and the text inside cannot be selected.

   **Shape.** The workbook filename on its own line, then one block per sheet, headed `Sheet: <name>`.
   A named range heads its own block by name instead of a sheet.
   - One numbered item per cell, holding the cell address. Its value goes in a code block directly
     under it, with no blank line between them.
   - Never split selecting and pasting into two steps.
   - No before/after pair. Where a mismatch would mean the wrong workbook, state the current content
     once, outside the numbered steps.
   - A `version_history` row is a single step: `Add a row with:` then the cell values separated
     by ` | `.
   - The numbered steps are workbook edits only. Telling the actuaries is not one of them; the agent
     sends that message itself, drafted for approval.

   **Up to three or four cells on a sheet** use the shape above. **More than that** (a full row of
   real edits, a contiguous block, many scattered edits) uses a paste file:
   - Holds the full rectangle spanning every edited cell. Tab-separated, one line per row.
   - Edited cells hold the new content. Every other cell in the rectangle holds its current content,
     from the pre-dumped baselines, formulas as formulas (`=...`) and values as values.
   - The step names the cell to select before pasting: the rectangle's top-left corner.
   - Lives in the ticket's `artifacts/rater-edits/`, named for the sheet and rows it fills.
   - Opened for Eli with `Start-Process`, in the same message that gives the step, and its contents
     are NOT reprinted in that message. Open it or print it, never both. Giving the path instead of
     opening it leaves him to go find it, which `tool-access.md` § "Never make Eli hunt for a link"
     already bans. Never a relative path.

   **Adding a row to a lookup table: insert inside the range, then paste the rows the insert got
   wrong.** Excel expands a formula's range reference only when the inserted row lands strictly
   inside that range. With a table at `$6:$9`, inserting at 7, 8 or 9 rewrites every referencing
   formula to `$6:$10`. Inserting at either edge does not: at row 6 the range slides to `$7:$10`,
   and at row 10 it stays `$6:$9`. Either way the new row sits outside the lookup, the sheet looks
   correct, and the new key silently never matches.

   When the new row's own position is interior, insert there. The blank lands where it belongs, so
   paste that one row.

   Insert **cells, shifted down, scoped to the table's own columns**, not a whole row. Rater sheets
   routinely park a second table a few columns to the right of the first, sharing its rows, and a
   whole-row insert drags that table down with it. Check the columns beside the table in the
   baseline before choosing the insert, and name the exact range in the step (`A7:L7`, Insert Cells,
   Shift cells down).

   When the new row belongs first or last, insert one row in from that edge and paste two rows: the
   new value, and the value it displaced. Every other row keeps its content untouched.

   The baseline diff is the proof. Referencing formulas still carrying the old range mean the insert
   was at an edge and the paste hid it.

   **Edits that are not a cell's contents** (adding or repointing a named range, adding a sheet,
   renaming a tab) get the menu path and every field, each exact value in a code block.

   In ALL cases, exact steps. Generic instructions ("fix the formula on the sheet") are banned.
3. **Tell the actuaries and document the change in the rater's `version_history` tab.**
4. **After the SharePoint edit, Eli downloads the file from SharePoint** and the agent places that download into the repo `Data` folder (the standard rater-placement step).

   **The delivered filename never matches the repo path, and its carrier token does not scope the
   delivery.** SharePoint carries the actuaries' delivery name: product, rating type, sometimes a
   carrier, the state, and a date whose format varies (`HO_ES_NY_Rater_2026_08_20.xlsm`,
   `HO_AD_BIC_AL_Rater_20260810.xlsm`, `CO_ES_TOPA_FL_Rater_20260914.xlsm`). Every Homeowner ByPeril
   path in `Data/` instead carries a carrier and no date
   (`Data/NY/Homeowner/ByPeril/EAndS/HO_ES_QBE_NY_Rater.xlsm`). A carrier in the delivered name
   settles nothing about which repo files it covers: TX's rater was delivered as
   `HO_ES_TOPA_TX_Rater_2026_08_03.xlsm`, and `HO_ES_TOPA_TX_Rater.xlsm`, `HO_ES_BSIC_TX_Rater.xlsm`,
   `HO_ES_HSIC_TX_Rater.xlsm` and `HO_ES_QBE_TX_Rater.xlsm` are one byte-identical file.

   **The hashes under `Data/` are the authority on which carrier files are one rater**, and so on
   which files a delivery is in scope for:

   ```powershell
   Get-ChildItem Data -Recurse -Filter *.xlsm |
     ForEach-Object { [pscustomobject]@{ Hash=(Get-FileHash $_.FullName -Algorithm SHA256).Hash; Path=$_.FullName } } |
     Group-Object Hash | Where-Object Count -gt 1
   ```

   Never remark on the mismatch between the delivered name and the repo path.

<!-- Added 2026-09-23 -->
## What a message to the channel is for

The actuaries' SharePoint copy is what their next delivery is built from. A rater change they don't
know about gets undone by that delivery. A change they would object to on actuarial grounds never
reaches them to object to. Every message here keeps their picture of their own rater accurate, and
gives Blake and Ehren what they need to judge rate impact and versioning.

Two kinds come out of rater work: an edit made on SharePoint, and an edit or defect handed to the
actuaries to make. Either way the message carries:

- The product line and the rater file, linked to its SharePoint copy.
- What the rater did, and why that was wrong or had to change, in the actuaries' terms: the sheet,
  the cell, what a quote got. When the rater moved to match live C# rather than being wrong on its
  own terms, say so. It is not a defect in their formula, and knowing that is what keeps them from
  reverting it.
- What changed, or what is being asked, precisely enough to find.
- The premium impact, stated either way, and whether the config is live.
- The `version_history` entry and the ticket link.

None of that is a template. The message is as long as the reasoning needs.


## MANDATORY plan header — the rater-parsing HARD RULE (physically insert into EVERY rater plan)

Every Excel rater plan MUST reproduce the block below **verbatim, at the very top of the plan file**
(immediately after the title/type line, above the preamble) — not a link, not a paraphrase, the
actual text. A rater plan without this block physically inserted is incomplete, exactly like a
missing HARD STOP. Copy it in as the first thing you write, and re-insert it if a revision drops it.

> ### HARD RULE — never parse a rater `.xlsm` yourself
> To read anything out of a rater workbook — Versions-sheet values, named ranges, input options,
> factor tables, fees — there are exactly TWO sanctioned sources:
> 1. **The pre-dumped baselines** under `Swyfft.Services.Excel.IntegrationTests/ExpectedResults/`,
>    which cover Homeowner and Commercial leaves alike.
> 2. **A rater with no baseline yet** (a brand-new file): the `DumpRater` / `ReadExcel`
>    console task (`WorkbookJsonDump.cs`).
>
> **NEVER open the `.xlsm` yourself** — not with a Python/zip/XML parser, not by unzipping the OOXML
> and reading `sheetN.xml` / `sharedStrings.xml`, not with any ad-hoc script. Hand-rolled Excel
> parsing is banned: it silently mishandles shared strings, cached-vs-formula values, and
> defined-name scoping, and it reinvents tooling the repo already owns. When the sanctioned tool is
> heavyweight (DumpRater needs a console build/run), that cost is the price of correctness — pay it.
> "It was faster to parse it myself" is never a justification.

## Running the Excel dump tasks — pointer

The three Excel tasks live in `Swyfft.Console/Tasks/Excel/` and use NPOI (no Excel/COM); each carries
its exact `-t:...` invocation in a `/// Usage:` header — read the file, don't re-derive it:
`DumpRaterTask.cs` (dump sheets → JSON; dumps every sheet by default, `-sheet` narrows to one;
formula cells emit only formula text unless `-IncludeFormulaValues:true` is passed),
`ReadExcelTask.cs`, and `ReadNamedRangesTask.cs`. Build the console once
(`pwsh ~/.claude/scripts/Build-Solution.ps1` — the wrapper lives in `~/.claude/scripts/`, NOT the repo
root) and run `Swyfft.Console/bin/<Debug|Release>/net10.0/Swyfft.Console.exe`.

## The diff is the requirement

`plan-mode.md` § Plan Types § "Excel Rater (ByPeril)" governs, and is read before authoring: the
entire plan is provisional until the diff has been run, so the plan is written in two parts around
the scoping checkpoint and nothing about the C# is decided before it.

Three things are routinely mistaken for the diff, and none of them is:

- **The old, on-disk rater.** It is the baseline. Reading it says what the rater did before the
  delivery, never what the delivery changed.
- **The `version_history` sheet.** Intent, not a change list. See § "The `version_history` sheet".
- **The ticket's technical notes.** A statement of what the filer expects the change to require.

The diff itself is the `ExpectedResults/` baseline diff, regenerated as soon as the raters are
placed. It needs no seeder change and no reseed, which is why it comes before both. See § "Plan
shape" for the run and § "Why the baseline diff, not `DumpRater`" for why this dump and no other.

## The `version_history` sheet — intent, not the change list

`version_history` is the actuary's changelog inside the rater workbook. Read it: it tells you what
the actuaries **intended**, which is useful context. But it is not the list of what actually
changed — the diff is. Actuaries write it to convey intent, not to enumerate every moved cell, and
rows sometimes backfill notes about already-live factors. Use it to understand intent; rely on the
diff for the actual changes. Never treat a missing row as "nothing changed," or a row as proof a
change is functional.

## Implement the seeder first

This orders the implementation, which starts at the scoping checkpoint. It never puts the seeder
before the diff: the diff is what says whether the seeder changes at all, and the delivered sheets
are often exactly what it has to be changed to read.

Within the implementation, the seeder goes first. It is the first layer that reads the actual rater
sheets and their layout, so sheet-name mismatches, shifted columns, and non-opt-in-carrier breakage
surface there concretely rather than as a guess. Every downstream layer (premium, rater service,
elements, validation) depends on seeded factor data and can't run until a full reseed is green.
Order: seeder → green full reseed → premium / rater service / elements / validation. Implement the
seeder late and layout or opt-in breakage only shows up when the work looks finished.

## Rating changes have an outsized blast radius

Premium is extremely sensitive: a change that leaks onto a state or carrier you didn't intend silently mis-prices quotes and policies — a leak here is a mispriced policy, not just a failed test. So before touching any shared base in the rating stack, read the actual inheritance chain of the class you're editing, and contain the change by construction (see `refactoring.md` § "Contain a shared-base change by construction").

## Plan shape — the same four steps for both products

Steps 1 to 3 are the plan written up front. Step 4 is written at the checkpoint, from the diff.

1. Branch.
2. **(You) place the rater(s).** Overwrite the canonical rater under `Data/`. A state's E&S rater is
   one file shared by its carriers, so propagate it byte-identical to every in-scope carrier file and
   hash-verify.
3. **Scoping checkpoint — HARD STOP.** Regenerate the `RaterFileContents` baselines for the affected
   leaves, which rewrite themselves locally on that run (`~/.claude/rules/captured-asserts.md`).
   Filter to `RaterFileContents_ShouldMatchCaptured` by method: it dumps the placed workbooks, and
   the premium comparisons in the same classes rate against seeded factor rows that are still the old
   ones. Read the `ExpectedResults/` diff, give every touched sheet a verdict, and write the
   implementation plan from it. **This is where provisional becomes verified.**
4. **Implement** what the diff dictates, seeder first (§ "Implement the seeder first"), then a green
   full reseed, then the rest of the C#. **Verify**: run the full validation suite, review the
   regenerated diff, and confirm C# premium equals Excel premium across every index of every affected
   leaf. Each playbook lists the extra suites its product requires.

## Why the baseline diff, not `DumpRater`

`RaterFileContents_ShouldMatchCaptured` writes canonical, code-controlled inputs through
`SetExcelValues` before dumping, so the baseline reflects the rater's factors, formulas and structure
and nothing else. A raw `DumpRater` of the on-disk file also captures whatever stray inputs someone
left in the workbook from clicking around, which makes it ad-hoc debugging rather than a scoping
tool. The baseline diff is the same drift-free mechanism at the scoping checkpoint and again at
verification.

The fact lives on `ExcelRaterValidationTestBase`, so both products inherit it and neither can override
it away.

## Researching rater structure — read the pre-dumped baselines

Every rater's structure is already on disk under
`Swyfft.Services.Excel.IntegrationTests/ExpectedResults/{TestClass}/`: `_NamedRanges.txt` holds every
named cell and its target, and the per-sheet dumps hold the rest. To answer a question about a rater's
current shape, whether a named range exists, what a fee cell's formula is, which fees are wired,
**read these dumps rather than opening the `.xlsm`**. They need no Excel and no COM, and they carry no
input drift. One grep across the `_NamedRanges.txt` files answers "which raters have this cell" for
every leaf that has a baseline.

## The scoping diff demands a verdict on EVERY sheet — none is presumed noise

Enumerate every sheet the diff touches and record an explicit verdict for each: versioned-safe, inert,
or break. Never let a sheet pass by omission. Working from the ticket's factor list and skimming the
rest is how a break ships, because the parity tests cannot catch an unversioned change that the seeder
faithfully mirrors into C#. The diff verdict is the only guard.

A **seeded factor sheet** gets a stricter bar. There is no innocent layout change to seeded data. If a
seeded sheet's values differ at all, either properly versioned rows were added, with V1 holding the
prior values and the new behavior on V2, or the change is wrong. An unversioned value change on an
existing tab is a backwards-compatibility break exactly like an unversioned new factor.
Reference-shift noise exists only on formula sheets, where `Rating_Algorithm` references auto-shift
around inserted rows, never on data tabs.

- **What happened:** SW-52867, the LA/TX `Ordinance_Law` values changed unversioned (1.15 on
  Fire and Hurricane only, to 1.25/1.4/1.65 on all perils). The audit enumerated only the new factor
  sheets, so the change sat unflagged in the diff artifacts until TX validation failures exposed it.
  The in-force LA and TX books would have silently re-rated.

## Validation runs sample configs — they never sweep every version

`ExcelRaterValidationTestBase.GetConfigsForGroup` runs at most five configs per state, carrier and
rating-type group: the oldest, a midpoint, and the three newest, plus anything a leaf names in
`AlwaysIncludedConfigs`. A version in the middle of a long chain is not exercised, so a change aimed
at one of those needs the config named explicitly rather than assumed covered.

## The element sweep is sourced from the generators

`EachElementOption_ShouldBeExpected` builds its values from the config's own default element
generators, taking each choice-bearing element's `DefaultChoices`. It is a blacklist: everything the
generator offers is swept unless the leaf excludes it. The knobs on the shared base:

- **the exclusion list** — elements the generators offer that no rater rates
- **`ElementTestValues`** — replaces an element's dynamic values with a fixed set
- **`ElementCombinationTestValues`** — elements whose values only make sense together, walked as a
  mixed-radix group
- **`ElementTestValuesSkipVersions`** — values a given factor version cannot rate

**`DefaultChoices` is the element's option list, not the rater's ratable set.** An element offering an
option the rater has no factor row for is a production defect, and catching it is what the sweep is
for. So the first response is never to narrow the sweep, which hides the finding. Fix the element, or
get the rows into the rater. If neither fits the ticket, exclude it with a TODO naming the story that
will. Treat an existing narrowing the same way: it may be suppressing exactly this.

## The sentinel checks prove every cell is written

Two facts on the shared base guard the write side, which the premium comparison cannot see:
`InputSheet_AllInputCellsShouldBeWrittenByCSharp` fails on any labeled Input cell C# never writes, and
`VersionsSheet_AllVersionCellsShouldBeWrittenByCSharp` fails on an unwritten non-V1 version cell and
on an Excel default that disagrees with the config's lookup. An unwritten input silently rates against
whatever sample value the actuary left in the cell.

Neither proves a cell is ever **varied**. An input can hold its create-time value through every
iteration and still pass both.

## Versioning is mandatory, even with no live policies

A rater change that moves premium or fees must be gated so existing quotes and policies keep their
original values (`Swyfft.Services/Premium/AGENTS.md` § "No re-rating live business"). This holds even where a carrier has no active book, because the ABQ re-rates
historical policies. A delivered rater that adds an unversioned premium-affecting factor, or puts real
values on V1, is a backwards-compatibility break to fix at the rater before any C# is wired.

## Reading each playbook's surfaces list and signal map

Both are thorough, and a rater rarely needs a surface absent from them, but neither is a closed set.
A ticket touches only a subset of the rows, often one or two. The scoping diff decides which, not the
ticket, and an off-list surface is not ruled out by its absence.

## A rater service's mappings describe its own rater

When one carrier stays on a different rater from its siblings, give that carrier its own rater service
carrying its own mappings. Do not guard a shared service so the odd carrier silently skips: a mapping
that names a cell its rater does not have is the data model lying, and a silent skip hides it forever.
`CommercialEAndSExcelRaterServiceFLCbs` is the shipped example, holding ClearBlue Specialty's own
version-cell mappings after FL's other carriers moved to a new rater.

