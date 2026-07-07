# Excel Rater (ByPeril) Implementation Tickets

This is the full playbook for the **Excel Rater (ByPeril)** plan type (defined in `plan-mode.md` § "Plan Types"). It inherits every general rule in `plan-mode.md` — the Gates, Parts A/B/C, the Seeder-Override and HomeownerStateConfig feature-doc requirements, and the full Verification structure. The one carve-out is the provisional-scope rule below.

**These plans are a deliberate exception to "resolve every open question before execution."** You can't place the new rater or regenerate baselines while authoring — the new rater arrives only at execution time (you download/place it), so its true scope (the diff) doesn't exist yet. A rater plan is therefore a **ticket-shaped outline, hardened by the diff immediately after the files are placed.**

## MANDATORY plan header — the rater-parsing hard rule (physically insert into EVERY rater plan)

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
`DumpRaterTask.cs` (dump sheets → JSON; `-sheet` for one; skips large reference sheets like
`Market_Factor` / `Roof_Type_Age` unless `-sheet` is passed — see its `SkipSheets`),
`ReadExcelTask.cs`, and `ReadNamedRangesTask.cs`. Build the console once
(`pwsh ~/.claude/scripts/Build-Solution.ps1` — the wrapper lives in `~/.claude/scripts/`, NOT the repo
root) and run `Swyfft.Console/bin/<Debug|Release>/net10.0/Swyfft.Console.exe`.

## Mandatory pre-reads — before authoring an Excel rater plan

A rater plan must not be authored — and the plan file must list as required pre-reads — without reading:

- **Implementation / component docs:** `Swyfft.Services/Common/CLAUDE.md` (ByPerilVersionLookup); `Swyfft.Services/Common/Homeowner/CLAUDE.md` (HomeownerStateConfig, QuoteDefinitions, seeder overrides, fold-vs-stack); `Swyfft.Services/Elements/CLAUDE.md` + `Elements/Homeowner/CLAUDE.md` (elements, constraint codes, generators, factory version fallback); `Swyfft.Services/Premium/CLAUDE.md` (element-model wiring); `Swyfft.Services/QuoteFees/CLAUDE.md` (fees); `Swyfft.Seeding/ExcelLoaders/ByPeril/CLAUDE.md` + its children `reading-rater-files.md`, `Homeowner/CLAUDE.md`, `Homeowner/rater-sheets-reference.md` (seeding + the sheet→component mapping); `Swyfft.Services.Excel/Homeowner/ByPeril/Rater/CLAUDE.md` + `audit-and-debugging.md` (rater-service overrides).
- **Excel test docs:** `Swyfft.Services.Excel.IntegrationTests/CLAUDE.md` + `Homeowner/CLAUDE.md` (ByPeril validation tests, debugging `#VALUE!`); `~/.claude/rules/captured-asserts.md` and the `/prebind-validation` skill (the baseline regen flow).

Always read the seeding/sheet-mapping, rater-service, and validation-test docs — not just the ones the ticket seems to touch — because the step-3 diff can implicate any component.

## Authoring rules

- Write the C# change list from the **ticket's stated scope, and label it provisional.** Do **not** assert as fact what the rater changed — you haven't seen it. Mark every ticket-derived scope claim explicitly unverified (e.g., *"per ticket; unverified until the step-3 diff"*). This is the one place a plan is allowed to carry unverified items — *because* they're labeled and a checkpoint resolves them.
- You may read the **old, on-disk** rater (`ReadExcel`) to sharpen the provisional scope, but that's the baseline, not the change — still provisional.

## Plan shape (every rater ticket)

1. Branch.
2. **(You) place the rater(s).** Overwrite the canonical `Data/{State}/…/{Rater}.xlsm`. For a UnifiedRater (E&S HO ships one rater per state), propagate it byte-identical to each in-scope carrier file and hash-verify.
3. **Scoping checkpoint — HARD STOP.** Run the ByPeril Excel validation tests for the affected leaves; the `RaterFileContents` baselines auto-update locally on the run (captured-assert update behavior: see `~/.claude/rules/captured-asserts.md`). Read the `ExpectedResults/` diff and reconcile against the provisional plan: diff ⊆ provisional → proceed; diff shows more (another factor, new input, fee, layout) → surface the delta and expand the plan before any C#. **This is where provisional becomes verified.**
4. **Implement** the C# the diff dictates (map below).
5. **Verify.** Run the ByPeril Excel validation tests again (baselines auto-update on the run; review the diff) — now it also reflects the version wiring — plus `/prebind-validation`; confirm the final diff matches the scope with nothing unexpected, and the C# premium == Excel across all indices.

> Running the ByPeril Excel validation tests (the `ByPerilEAndSValidationTests*` classes in `Swyfft.Services.Excel.IntegrationTests`) through `Run-DotnetTest.ps1` **must** include `-FilterTrait "TestGroup=ByPerilTests"` — omit it and the run also pulls the Commercial validation tests (900+, ~45 min) and the pre-tool hook blocks it. Scope to one state by AND-ing `-FilterNamespace "*{ST}.EAndS"`.

## Ignore the `version_history` sheet

`version_history` is the actuary's free-text changelog — not consumed by any premium
calculation. A new rater routinely adds log rows, sometimes backfilling notes about factors
that were already live. Read it for context if you want, but never scrutinize its diff or
treat a log row as evidence of a functional change.

## Why the baseline diff, not `DumpRater`

`RaterFileContents_ShouldMatchCaptured` (SW-50657) writes canonical, code-controlled inputs via `SetExcelValues` before dumping, so it reflects only the rater's factors/formulas/structure — never the stray inputs someone left in the file from clicking around. A raw `DumpRater` of the on-disk file carries that drift; it's ad-hoc debugging only. The diff is the same drift-free mechanism at both step-3 scoping and step-5 verification.

## Researching rater structure — read the pre-dumped baselines

Every ByPeril HO rater's full structure is already captured on disk by
`RaterFileContents_ShouldMatchCaptured`, under
`Swyfft.Services.Excel.IntegrationTests/ExpectedResults/{TestClass}/` — `_NamedRanges.txt` (every
named cell and its target), `Fees.txt`, `Rating_Algorithm.txt`, and the per-sheet dumps. To
research a rater's current shape (does a named range exist? what's the inspection-fee cell and its
formula? which fees are wired?), **read these dumps — never open the `.xlsm`**. It's drift-free
(canonical inputs written before the dump), needs no Excel/COM, and covers every state/carrier
leaf. Use it both to scope a change and to find which raters already have or lack a given named
range (e.g. grep the `_NamedRanges.txt` files for a cell name across all leaves at once).

## Component → Excel-signal map

The diff signal on the left tells you which component on the right must change:

| Rater signal in the diff | C# component to change | Key file(s) |
|---|---|---|
| A factor's version bumped on the `Versions` sheet | Bump that factor in the carrier `ByPerilVersionLookup` class (clone latest → `.SetVersion`) | `Swyfft.Services/Common/ByPerilVersionLookup/Homeowner/{ST}/{Calc}/…{Carrier}{ST}.cs` |
| Any new factor version now in use | New `HomeownerStateConfig` version (`sourceConfig:` + new `lookupVersions:`) + `QuoteDefinitions.txt` row + seeder override | `…/Common/Homeowner/HomeownerStateConfig/ByPeril/…`; `Data/QuoteDefinitions.txt`; `Swyfft.Seeding/Seeder.cs` |
| Factor sheet: new static rows / shifted header rows | Seeder reader params (`startRow`/`startCol`/`versionOffset`; `.SetLength(N)` if static rows now mix with formula rows) | `Swyfft.Seeding/ExcelLoaders/ByPeril/Homeowner/ByPerilSeederHomeowner…` |
| Factor sheet: a new version is **formula-only** | Replicate the formula in the premium generator, version-branched | `Swyfft.Services/Premium/Homeowner/HomeownerByPerilPremiumGenerator.cs` (+ carrier subclass) |
| `Input` sheet: new input/option | Element loader + constraint code → generator → `ByPerilQuoteElementModel`/`ByPerilElementService` → `ByPerilName`; then write it via the rater service `WorkbookSetters` | `ElementLoader_Homeowner_ByPeril.cs`, `ConstraintCode.cs`, generator + `HomeownerDefaultElementGeneratorFactory.cs`, `ByPerilQuoteElementModel.cs`, `ByPerilElementService`, `ByPerilName.cs` |
| A **newly versioned** factor appears on `Versions` | Add `(ByPerilName, cellName)` to the rater service `TableNameToExcelCellVersionName` (+ `ByPerilCellNames`) | `…/Rater/{ST}/ByPerilHomeowner{RT}ExcelRaterService{ST}.cs`, `ByPerilCellNames.cs` |
| `Rating_Algorithm`: new fee/tax row | `FeeNames` on the rater service + the QuoteFees service/values | rater service; `…/QuoteFees/Homeowner/…`, `StateQuoteFeeFactoryHelper.cs` |
| `Rating_Algorithm`: new factor / optional-coverage row | `GetFactorAndRateNames` / `CoverageNames` / `FactorsToSetNames` on the rater service | rater service |
| New config version needs different premium logic | Generator + `HomeownerByPerilPremiumGeneratorFactory` mapping (falls back to lower version if unmapped) | `…/Premium/Homeowner/HomeownerByPerilPremiumGeneratorFactory.cs` |

Which rows apply is dictated entirely by the step-3 diff — a ticket touches only a subset of these rows, often just one or two. The diff, not the ticket, tells you which.
