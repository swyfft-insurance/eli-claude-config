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

**A rater edit is warranted for actual rater bugs — and only for actual rater bugs.** The actuaries absolutely make mistakes, and a genuine defect in the rater gets fixed in the rater — a lookup that can't resolve a valid input, a formula whose range doesn't cover the sheet's own data, a structural error. What a rater edit is NOT for: making the rater agree with C#. The C# is ours to change (a state-specific override, a conditional argument — see `coding-standards.md` § "We own this code"), and leaning on rater edits as the easy way out of a C#-vs-rater discrepancy is a known agent failure mode. The test: is the rater wrong on its own terms, or merely different from the code?

**The repo `Data\` copy is NOT the source of truth — the actuaries' SharePoint copy is.** The actuaries don't work out of the Swyfft solution's `Data` folder; an edit made only in the repo gets blown away the next time they deliver a rater. `#dev-analytics-rater-handoff` exists to coordinate rater changes from both ends.

The flow when a rater edit is warranted:

1. **The edit is made on SharePoint, by a human.** Eli usually makes it himself directly on SharePoint; routing the change to the actuaries instead is always a valid option (some devs prefer it).
2. **The agent prepares the edit; it NEVER applies one.** Programmatic edits of rater `.xlsm` files by the agent are banned.
   - Big edits (a row, several rows, a whole sheet): write the paste-ready content to a txt file, and state the EXACT cell to select for the paste.
   - Individual cell or named-range edits: PRECISE instructions — the exact cell address and the exact formula/value, or the exact named-range name and its target reference.
   - In ALL cases, exact per-cell steps. Generic instructions ("fix the formula on the sheet") are banned.
3. **Tell the actuaries and document the change in the rater's `version_history` tab.**
4. **After the SharePoint edit, Eli downloads the file from SharePoint** and the agent places that download into the repo `Data` folder (the standard rater-placement step).

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

## Scope stays provisional until the rater diff exists

Rater plans are a deliberate exception to plan-mode's "resolve every open question before execution."
You can't see what the rater changed while authoring — the new rater `.xlsm` arrives only at
execution, when you place it and diff it against the captured baselines. So a rater plan is a
**ticket-shaped outline, hardened by the diff right after the files are placed:**

- Write the C# change list from the **ticket's stated scope, and label it provisional.** Don't assert
  as fact what the rater changed — mark every ticket-derived scope claim unverified (e.g. *"per
  ticket; unverified until the diff"*). This is the one place a plan may carry unverified items,
  because they're flagged and a checkpoint resolves them.
- You may read the **old, on-disk** rater (`ReadExcel`) to sharpen the provisional scope, but that's
  the baseline, not the change — still provisional.

## The `version_history` sheet — intent, not the change list

`version_history` is the actuary's changelog inside the rater workbook. Read it: it tells you what
the actuaries **intended**, which is useful context. But it is not the list of what actually
changed — the diff is. Actuaries write it to convey intent, not to enumerate every moved cell, and
rows sometimes backfill notes about already-live factors. Use it to understand intent; rely on the
diff for the actual changes. Never treat a missing row as "nothing changed," or a row as proof a
change is functional.

## Implement the seeder first

The seeder is the first layer that reads the actual rater sheets and their layout, so sheet-name mismatches, shifted columns, and non-opt-in-carrier breakage surface there — concretely, not as a guess. Every downstream layer (premium, rater service, elements, validation) depends on seeded factor data and can't run until a full reseed is green. Order: seeder → green full reseed → premium / rater service / elements / validation. Implement the seeder late and layout or opt-in breakage only shows up when the work looks finished.

## Rating changes have an outsized blast radius

Premium is extremely sensitive: a change that leaks onto a state or carrier you didn't intend silently mis-prices quotes and policies — a leak here is a mispriced policy, not just a failed test. So before touching any shared base in the rating stack, read the actual inheritance chain of the class you're editing, and contain the change by construction (see `refactoring.md` § "Contain a shared-base change by construction").

## Plan shape — the same five steps for both products

1. Branch.
2. **(You) place the rater(s).** Overwrite the canonical rater under `Data/`. A state's E&S rater is
   one file shared by its carriers, so propagate it byte-identical to every in-scope carrier file and
   hash-verify.
3. **Implement the seeder and reseed** (see § "Implement the seeder first"). Nothing downstream runs
   until a full reseed is green.
4. **Scoping checkpoint — HARD STOP.** Run the validation tests for the affected leaves. The
   `RaterFileContents` baselines rewrite themselves locally on that run (see
   `~/.claude/rules/captured-asserts.md`). Read the `ExpectedResults/` diff and reconcile it against
   the provisional plan. Diff within the provisional scope means proceed. Diff showing more means
   surface the delta and expand the plan before writing any C#. **This is where provisional becomes
   verified.**
5. **Implement** the C# the diff dictates, then **verify**: re-run the validation tests, review the
   regenerated diff, and confirm C# premium equals Excel premium across every index of every affected
   leaf. Each playbook lists the extra suites its product requires.

## Why the baseline diff, not `DumpRater`

`RaterFileContents_ShouldMatchCaptured` writes canonical, code-controlled inputs through
`SetExcelValues` before dumping, so the baseline reflects the rater's factors, formulas and structure
and nothing else. A raw `DumpRater` of the on-disk file also captures whatever stray inputs someone
left in the workbook from clicking around, which makes it ad-hoc debugging rather than a scoping
tool. The baseline diff is the same drift-free mechanism at both the step-4 scoping checkpoint and
the step-5 verification.

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
original values (`Swyfft.Services/Premium/AGENTS.md` § "Changes must not alter what existing quotes or
policies are charged"). This holds even where a carrier has no active book, because the ABQ re-rates
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

