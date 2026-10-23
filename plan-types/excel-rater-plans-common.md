# Excel Rater (ByPeril) — Shared Conventions

Shared by the Homeowner (`ho-excel-rater-plans.md`) and Commercial (`co-excel-rater-plans.md`) playbooks. Both products run one Excel test infrastructure, so anything about it belongs here.

## Rater edits — when warranted, and the SharePoint flow (MANDATORY)

When a rater edit is warranted, and how a C#-vs-rater discrepancy is reconciled, live in `Swyfft.Services/Premium/AGENTS.md` § "The rater is the acceptance criteria". Read it before proposing either. The call is never the agent's: present the discrepancy, the config's live status and both options, and Eli decides. Never reach for a rater edit as the easy way out.

The actuaries' SharePoint copy is the source of truth, not the repo `Data\` copy. An edit made only in the repo is lost at their next delivery.

**Where the raters live.** Site `swyfft-developmentsite`, library `Shared Documents`:

| Product line | Folder |
|---|---|
| Homeowner | `https://swyfft2.sharepoint.com/sites/swyfft-developmentsite/Shared%20Documents/By-Peril/<STATE>` |
| Commercial EandS | `https://swyfft2.sharepoint.com/sites/swyfft-developmentsite/Shared%20Documents/E%26S/<STATE>` |

Every delivery is posted as a link in `#dev-analytics-rater-handoff` (`C06V258BWHJ`). Look there for a file these folders don't cover.

**Find the file yourself.** The Microsoft 365 connector reaches the library, drive id `b!tBNV3k6K8kCdPLPGZkBK1vEWJmsPHglMlxi9NMlA4v4eCrl5UDM3TZFSpD58-3xY`. `read_resource` lists a folder by its path from the library root, without `Shared Documents`:

- Homeowner: `file:///<driveId>/By-Peril/<STATE>`
- Commercial EandS: `file:///<driveId>/E&S/<STATE>`

The listing gives each file's name, size and `file:///` URI. `sharepoint_search` gives a `webUrl` but not who modified the file; the delivering actuary comes from the channel post. Never ask Eli where a rater is.

**Eli moves files; the agent opens the pages.** No agent route reaches a rater's bytes: the connector won't open `.xlsm`, Graph file access needs tenant admin approval, and Playwright can't reach SharePoint (`Scripts/AgentHooks/validate-browser-url.ps1`).

**Who to tag** in the channel:

- Blake Smith (`U019J5G7UTF`), the actuaries' leader, on every rater change.
- The actuary who delivered the rater in hand, found from the delivery post carrying its SharePoint link. Alex Terragnoli (`U03JA79NY8L`) posts many. The rater's `version_history` `Analyst` column cross-checks.
- Ehren (`U1F5C7Q3W`), the pre-bind manager, tagged or cc'd on every message.

**Name the product line in the first sentence of every message and reply in that channel.** The same state and carrier exist in both products (`HO_ES_QBE_NY_Rater.xlsm`, `CO_ES_QBE_NY_Rater.xlsm`). Say Homeowner or Commercial, name the rater file, and repeat the product line wherever a state, carrier or config is named.

**Who makes the edit.** When what the rater should say is known (a clear mistake with obvious intent, or rounding moved to match the live C#, § "Rounding changes"), we make it through the flow below. When it needs an actuarial decision, hand it to the actuaries in the channel (§ "What a message to the channel is for").

The flow:

1. **Open the rater for Eli.** Find it (§ "Find the file yourself") and open its `webUrl` in Chrome with `Start-Process`. He downloads it.
2. **Take it from `~/Downloads`.** A repeat download is saved as `name (1).xlsm`. Save the edited file under the exact SharePoint filename.
3. **Edit in desktop Excel through COM** (`New-Object -ComObject Excel.Application`). No other library writes a rater.
   - Eli approves the edit list before Excel opens: every cell and its new content, every structural change (named range, sheet, tab name), and the `version_history` row word for word (date, analyst, text). Write only what was approved.
   - Fill every changed cell orange (`#FFC000`) and turn every touched sheet's tab orange. Add the `version_history` row, highlighted the same way.
   - **Adding a row to a lookup table.** Excel expands a referencing formula's range only when the insert lands strictly inside it: with `$6:$9`, inserting at 7, 8 or 9 gives `$6:$10`, while inserting at 6 or 10 leaves the new row outside the lookup, where it silently never matches. Insert cells shifted down, scoped to the table's own columns (name the range, e.g. `A7:L7`), never a whole row: rater sheets park second tables beside the first, so check the baseline for one. For an interior position, insert there and paste the one row. For a first or last position, insert one row in from that edge and paste two rows, the new value and the one it displaced. In the baseline diff, a referencing formula still carrying the old range means the insert was at an edge.
4. **Verify before anything else runs.** Place the edited file in the repo `Data` folder. The delivered filename never matches the repo path (`Data/` paths carry a carrier and no date), and a carrier in the delivered name doesn't scope the delivery. The hashes under `Data/` decide which carrier files are one rater, and so which files the delivery covers:

   ```powershell
   Get-ChildItem Data -Recurse -Filter *.xlsm |
     ForEach-Object { [pscustomobject]@{ Hash=(Get-FileHash $_.FullName -Algorithm SHA256).Hash; Path=$_.FullName } } |
     Group-Object Hash | Where-Object Count -gt 1
   ```

   Never remark on the name mismatch. Run `RaterFileContents_ShouldMatchCaptured` alone, by method, on one leaf per distinct rater file. The baseline diff must be the planned edits and the `version_history` row, nothing else. The diff doesn't see formatting, so read the highlights back through Excel. Any mismatch: HARD STOP.
5. **Upload after the PR is up.** Once the PR carrying the edited rater exists, open the SharePoint folder page. Eli drags the file in, and SharePoint saves it as a new version.
6. **Tell the actuaries, last.** The channel message goes out only after that PR exists, links it, and covers every rater edit in one message. Nothing follows it.

## What a message to the channel is for

The actuaries build their next delivery from their SharePoint copy. A message keeps their picture of their rater accurate and gives Blake and Ehren what they need to judge rate impact and versioning.

- The actuaries own the rating algorithm. Tell them what changed in how it behaves, and why, in rating terms. Sheet and cell addresses are locators, not the substance.
- Write "the rater" or "our raters", never "your rater" or "your formulas".
- Lead with what required the change: the ticket's requirement, quoted, or the defect or live C# the rater had to match. Present the edit as following from it ("To meet the SW-XXXXX requirement, the rater now …"), never as Eli's own action ("I changed …").

Every message, for an edit made on SharePoint or one handed to them, carries:

- the product line and the rater file, linked to its SharePoint copy
- what the rater did and why that was wrong or had to change, in rating terms, with the sheet and cell. When the rater moved to match live C#, say so: it is not a defect in their formula.
- what changed, or what is being asked, precisely enough to find
- the premium impact either way, with the reason. An edit that only moves the rater to match live C# moves no premium: the C# charges, and it did not change. The config's live status matters only when what the C# charges changes.
- the `version_history` entry and the ticket link

It is not a template. The message is as long as the reasoning needs.

### Rounding changes

Rounding consistency is between a rater and its own live C#, never between raters, which have always rounded differently. The fix only ever moves the rater. Moving the C# would re-rate in-force quotes and policies, which needs versioning. Every rounding message states, on its own:

- where the rater rounds this value and where the C# rounds it, with the step and precision on each side
- that the rater now rounds it the way its own C# does, which is the whole reason for the edit
- that other raters rounding it differently is expected and stays

Never call the old rounding an error in their formula, and never suggest uniform rounding across raters.

## MANDATORY plan header — the rater-parsing HARD RULE (physically insert into EVERY rater plan)

Every Excel rater plan reproduces the block below verbatim at the very top of the plan file, right after the title/type line and above the preamble. A plan without it is incomplete. Re-insert it if a revision drops it.

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
>
> Desktop Excel through COM is how an approved edit is applied (§ "Rater edits"), and how its
> highlights are read back. It is never a way to read rater values.

## Running the Excel dump tasks — pointer

The tasks live in `Swyfft.Console/Tasks/Excel/` and use NPOI: `DumpRaterTask.cs` (sheets to JSON, every sheet by default, `-sheet` narrows to one, formula cells emit only formula text unless `-IncludeFormulaValues:true`), `ReadExcelTask.cs` and `ReadNamedRangesTask.cs`. Each file's `/// Usage:` header carries its exact `-t:...` invocation; read it. Build once with `pwsh ~/.claude/scripts/Build-Solution.ps1` (in `~/.claude/scripts/`, not the repo root) and run `Swyfft.Console/bin/<Debug|Release>/net10.0/Swyfft.Console.exe`.

## A rater plan's AC

The rater is the acceptance criteria (`Swyfft.Services/Premium/AGENTS.md` § "The rater is the acceptance criteria"). Every rater plan's AC includes these, whatever the ticket says, followed by the ticket's own AC (extracted per `youtrack.md`, go-live dates included):

- The C# rates every new or changed config exactly as the rater does.
- Every existing config rates exactly as before (`Swyfft.Services/Premium/AGENTS.md` § "No re-rating live business").
- The rater seeds correctly.
- Every Excel rater validation test passes on every affected leaf.

## The diff is the requirement

`rater-update.md` governs. The diff is the `ExpectedResults/` baseline diff, regenerated as soon as the raters are placed, with no seeder change or reseed. The `version_history` sheet is the actuaries' intent: a missing row doesn't mean nothing changed, and a row doesn't prove a change is functional.

## Implement the seeder first

Implementation starts after discovery, never before the diff. Within it the order is seeder, then a green full reseed, then premium, rater service, elements and validation. The seeder is the first layer that reads the actual sheets, so layout and opt-in breakage surface there.

## New code goes where the codebase already keeps that kind of code (MANDATORY)

- Code only premium generation uses goes in the premium generator hierarchy (the shared base, or the state and carrier generators), never an adjacent class.
- A small method or constant more than one subsystem uses goes in an existing static helper class.

A new static class is never the default. When a plan adds one, the plan says why no existing home fits.

## Deprecated and run-off carriers are out of scope (MANDATORY step)

A carrier that no longer writes new business is out of scope unless the ticket names it. In Homeowner that is ClearBlue and ClearBlue Specialty (CBS). Their tests (same scenarios, same assertions), premium (same factors, same result) and seeders (same rows read and written) stay exactly as before, and their configs are never a test subject. Structure around them may change: a shared class can be refactored, or gain members only in-scope classes call. When an in-scope change would alter what a deprecated carrier runs, refactor so it doesn't reach them, such as a new subclass for the in-scope carriers. That refactor is part of the ticket.

Every rater plan:

- names the deprecated and run-off carriers in its states before the plan's C# change list
- at the code-complete HARD STOP, names each class in the diff a deprecated carrier runs and shows its tests, premium and seeding are unchanged
- at the tests-complete HARD STOP, confirms their validation tests pass with zero baseline diff

## Plan shape — the same five steps for both products

Steps 1 to 4 are discovery, done before any plan exists. Step 5 is the plan, written from the diff.

1. Branch.
2. **Place the rater(s).** Find each on SharePoint (§ "Find the file yourself") and open its `webUrl` for Eli to download. Take it from `~/Downloads`, overwrite the canonical rater under `Data/`, propagate it byte-identical to every in-scope carrier file, and hash-verify.
3. **Scoping checkpoint.** Build once with `pwsh ~/.claude/scripts/Build-Solution.ps1`. Then run the three tests below in parallel, one background `Run-DotnetTest.ps1` call each through the PowerShell tool (it takes one `-FilterMethod`). None of them rates a premium.

   - **`RaterFileContents_ShouldMatchCaptured`** regenerates the baselines. The `ExpectedResults/` diff is what the delivery changed.
     ```
     $env:UPDATE_TEST_EXPECTED_RESULTS='true'; pwsh -NoProfile -File "$HOME/.claude/scripts/Run-DotnetTest.ps1" -TicketFolder <folder> -Project Swyfft.Services.Excel.IntegrationTests -FilterTrait "<trait>" -FilterMethod "*RaterFileContents_ShouldMatchCaptured" -NoBuild
     ```
   - **`VersionsSheet_AllVersionCellsShouldBeWrittenByCSharp`** reports each rater `Versions` default the newest config doesn't have yet (`EXCEL: V3 | LOOKUP: V2`). The baselines can't show these.
     ```
     pwsh -NoProfile -File "$HOME/.claude/scripts/Run-DotnetTest.ps1" -TicketFolder <folder> -Project Swyfft.Services.Excel.IntegrationTests -FilterTrait "<trait>" -FilterMethod "*VersionsSheet_AllVersionCellsShouldBeWrittenByCSharp" -NoBuild
     ```
   - **`InputSheet_AllInputCellsShouldBeWrittenByCSharp`** reports each `Input` cell C# doesn't write.
     ```
     pwsh -NoProfile -File "$HOME/.claude/scripts/Run-DotnetTest.ps1" -TicketFolder <folder> -Project Swyfft.Services.Excel.IntegrationTests -FilterTrait "<trait>" -FilterMethod "*InputSheet_AllInputCellsShouldBeWrittenByCSharp" -NoBuild
     ```

   `<trait>` is `TestGroup=ByPerilTests` for Homeowner and `TestGroup=Commercial` for Commercial. Every touched sheet in the diff, and every failure from the two sentinel checks, gets a verdict.
4. **Versioning check.** Run § "The versioning check" on the scoping diff and record every sheet's verdict for the message that ends discovery. The plan waits until every sheet is versioned or inert.
5. **Implement** what the diff dictates (§ "Implement the seeder first"). **Verify**: run the full validation suite, review the regenerated diff, and confirm C# premium equals Excel premium across every index of every affected leaf, plus the extra suites each playbook lists.

## Researching rater structure — read the pre-dumped baselines

Answer questions about a rater's current shape from `Swyfft.Services.Excel.IntegrationTests/ExpectedResults/{TestClass}/`, never from the `.xlsm`. `_NamedRanges.txt` holds every named cell and its target, and the per-sheet dumps hold the rest. One grep across the `_NamedRanges.txt` files answers which raters have a given cell.

## The versioning check (MANDATORY on every delivered rater)

With every `Versions` cell holding the version an existing config's `ByPerilVersionLookup` writes, the delivered rater must compute exactly what the old rater computed, for every input an existing quote can hold. The parity suite can't prove this: an unversioned change that C# mirrors still passes parity.

Record a verdict for every sheet the diff touches: versioned, inert, or break.

- **A table's values.** Existing versions' rows keep their prior values, and new values sit only on a new version's rows, whether C# seeds the table, replicates its formula, or never reads it.
- **A table versioned for the first time.** The prior table survives unchanged as V1, and every formula reading the table selects on the new version key.
- **A formula.** A changed calculation branches on a version cell. A reference shifted around an inserted row is inert, and that shift happens only on formula sheets, never on data tabs.
- **The `Versions` sheet and `_NamedRanges.txt`.** Every newly versioned table has its own row and named range. Existing version cells keep their names, since C# writes each one by name through `TableNameToExcelCellVersionName`.
- **A new input option** is inert only if no existing quote can hold it.

A break goes to the plan's "Rater defect found during execution" section.

## Validation runs sample configs — they never sweep every version

`ExcelRaterValidationTestBase.GetConfigsForGroup` runs at most five configs per state, carrier and rating-type group (the oldest, a midpoint and the three newest), plus anything a leaf names in `AlwaysIncludedConfigs`. A change aimed at a mid-chain version names that config explicitly.

## The element sweep is sourced from the generators

`EachElementOption_ShouldBeExpected` sweeps each choice-bearing element's `DefaultChoices` from the config's own generators, unless the leaf excludes the element. The knobs on the shared base:

- **the exclusion list**: elements the generators offer that no rater rates
- **`ElementTestValues`**: a fixed set replacing an element's dynamic values
- **`ElementCombinationTestValues`**: elements whose values only make sense together, walked as a mixed-radix group
- **`ElementTestValuesSkipVersions`**: values a given factor version cannot rate

An option the rater has no factor row for is a production defect, and catching it is the sweep's job. Fix the element or get the rows into the rater; never narrow the sweep first. If neither fits the ticket, exclude it with a TODO naming the story that will. An existing narrowing may be suppressing exactly this.

## Rater logic that singles out counties must be swept

When the diff shows the rater treating a small set of counties, or groups of counties, differently from the rest of the state, the sweep rates at least one county from each group. The plan adds any county the sweep doesn't already rate. Data with a row for every county or zip singles none out and is out of scope.

## The sentinel checks prove every cell is written

`InputSheet_AllInputCellsShouldBeWrittenByCSharp` fails on any labeled Input cell C# never writes. `VersionsSheet_AllVersionCellsShouldBeWrittenByCSharp` fails on an unwritten non-V1 version cell and on an Excel default that disagrees with the config's lookup. Neither proves a cell is ever varied.

## Versioning is mandatory, even with no live policies

A rater change that moves premium or fees is gated so existing quotes and policies keep their values (`Swyfft.Services/Premium/AGENTS.md` § "No re-rating live business"), even where a carrier has no active book, since the ABQ re-rates historical policies. A delivered rater with an unversioned premium-affecting factor, or real values on V1, is fixed at the rater before any C# is wired.

## A rater service's mappings describe its own rater

A carrier that stays on a different rater from its siblings gets its own rater service with its own mappings, as `CommercialEAndSExcelRaterServiceFLCbs` does for ClearBlue Specialty. Never guard a shared service so the odd carrier silently skips a mapping its rater doesn't have.
