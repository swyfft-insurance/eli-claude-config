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

Applies to both rater playbooks: HO (`ho-excel-rater-plans.md`) and Commercial (`co-excel-rater-plans.md`). Each inherits everything here.

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
> 1. **HO:** the pre-dumped baselines under `Swyfft.Services.Excel.IntegrationTests/ExpectedResults/`.
> 2. **Any rater without a baseline (Commercial, or a brand-new file):** the `DumpRater` / `ReadExcel`
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
execution, when you place it and diff it (against the HO baselines, or via `DumpRater` for
Commercial). So a rater plan is a **ticket-shaped outline, hardened by the diff right after the files
are placed:**

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

