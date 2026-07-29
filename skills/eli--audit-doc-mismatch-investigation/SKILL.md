---
name: eli--audit-doc-mismatch-investigation
description: Investigate ByPeril Homeowner and Commercial Excel audit-doc failures (ByPerilHomeownerExcelQuoteAuditService/CommercialExcelQuoteAuditService GenerateAuditDoc — LogMonitor "audit service generation failure" / "premium/fee mismatch" tickets). Reproduce with the three-way diagnostic test, then compare against known prior root causes (examples below — NOT an exhaustive taxonomy; a new failure may not fit any of them). Use for any ByPeril audit crash or premium/fee mismatch.
---

# Audit Doc Mismatch Investigation

The audit job re-rates each purchased quote with the **current** Excel rater and compares to the
**stored** DB premium+fees (tolerance 0.05%, min $1). It fails one of two ways:

- **CRASH** — can't read a cell (`#VALUE!`/`#REF!`/`#N/A` cascading to `Subtotal` on `Rating_Algorithm`),
  or a required quote line is missing.
- **MISMATCH** — it generates, but the premium/fee total ≠ stored ("Premium/fee mismatch:" log).

Either way the current Excel-rater path can't reproduce what the quote was charged. **The audit is a
tripwire — it usually surfaces an *upstream* bug (or a since-bind data change), not an audit bug.**

**Ticket-level workflow** (catch-all tickets, current-failing-set first, RCA per failure, spin-offs): `~/.claude/rules/plan-mode.md` § "Audit-Doc LogMonitor (catch-all)".

## Step 1 — Reproduce with the diagnostic test. Do this FIRST.
`/eli--byperil-audit-diagnostic <quote GUIDs>` runs `HomeownerExcelQuoteAuditDiagnosticTests` (origin: SW-49341) —
a three-way compare of **DB(bind) / Excel(now) / Recompute(now)** that names the diverging factor or
line. No DumpRater archaeology needed to localize. That skill handles the beta/prod-copy DB setup.
For Commercial quotes the same skill runs `CommercialExcelQuoteAuditDiagnosticTests` — pass `-Commercial`
(both share `ExcelQuoteAuditDiagnosticTestBase`, which asserts via the audit service's own
`ComparePremium`; added in SW-53865).

## Step 2 — Compare against the known prior root causes (EXAMPLES, not an exhaustive taxonomy)
**These categories are past failures we have already diagnosed and acted on — a reference for
pattern-matching, NOT a closed set.** A new audit failure may match one, partially match, or be
something entirely new. Let the diagnostic test's evidence drive the conclusion — **never force-fit a
new failure into a category just to close it.** If it doesn't match, investigate it on its own merits,
and once it's resolved add it here as a new example.

Which two of the three columns agree narrows where it sits; the diverging factor/line points at the cause.

### A. Rater lookup missing a row for a VALID input → CRASH
C# rates leniently (interpolation/formula with fallback); the Excel rater uses a strict `VLOOKUP`
needing an exact row. A valid input the rater has no row for → `#VALUE!`/`#N/A`/`#REF!` → cascades to
`Subtotal`. Find the FIRST erroring cell, trace its VLOOKUP to the lookup table, confirm the input has
no row. **Fix is a rater change (actuarial adds the row), not a C# premium bug.**
- 0% Coverage B/C/D on V1 tables: SW-48603, SW-49035, SW-49434, SW-49436, SW-49437, SW-49439
- inverse — admin override = 100% (tables top out at 40/75/20%, `#REF!`): SW-50221
- $25K/$50K AOP not in the rater table (fix SW-48682): SW-48594
- RMPS="No" missing from `Rating_Algorithm_Prior` T:AH lookup: SW-47164, SW-47135

### B. Invalid/unfiled input the rater rightly can't rate → NO code fix
Same crash signature as A, but the input should never have been allowed — e.g. 0% coverage on an
**Admitted** policy where 0% was never filed with the DOIs. **There is no rater fix.** The gap that
let the policy be set that way is closed going forward (separate prevention work), and the existing
in-force policies must be **corrected by UW**, not by code. (Example tickets are Blocked/open, so not
listed here — but recognize the pattern: Admitted + 0% coverage + "no planned rater change.")

### C. Missing required quote line in stored `QuoteLinesJson` → CRASH
`GetRequiredValue("X") not found`. The stored quote (often a renewal from an older version, or a quote
from a past code-bug window) lacks a line the current rater service expects. **Fix: legacy fallback in
the rater service, or produce the line.**
- `Cap_RawSarHurricanePremium` — AL BIC Admitted V10 renewals from V5 (RCA on SW-47136): SW-49034, SW-47057
- `"Inspection Fee"` vs `"InspectionFee"` baked into old quotes' JSON → legacy fallback: SW-47467

### D. Genuine C#-vs-rater divergence (code / rater / fee bug) → MISMATCH
Audit generates but premium/fee ≠ stored, and the inputs DO match — C# and the rater genuinely
compute differently. **Fix: bring the two into agreement (version the change per immutability).**
- double-applied Rate Modeling on SAR hurricane → `RawSarHurricanePremium` line: SW-47136
- AL E&S rater formula drift (Topa V16 / BSIC V9): SW-47147
- MA admitted mismatch (then handed to LA fee-name/composition drift): SW-50832

### E. Input/data changed since bind → re-rate diverges → MISMATCH (immutability)
Audit generates but premium ≠ stored **because a rating input or underlying datum changed after bind**
— the rater/C# code is CORRECT. Tell-tale: the diverging factor's rater data is byte-identical across
history (DumpRater old vs current), yet DB(bind) ≠ Recompute/Excel. **Usually NO premium-code action:
the policy was charged correctly for its inputs at bind; any fix is forward-only and in-force quotes
keep their values by design.**
- property zip edited post-bind (36535→36532) → territory NonHurricaneWind/Hail re-rates higher: **SW-51664** (current; AL half)
- CSR "ghost reprice" — second reprice against the parent left a stale `AnnualPremium`: SW-49774 (won't-fix; Dashboard Reprice eliminates it)
- ghost reprice, Commercial variant — re-initiating a reprice preserves the first accept's `AcceptedOn` (`CopyQuoteToActor` excludes it from the copy), so `ShouldRecalculate()` skips all re-rating and the scalar premium totals go stale against the quote lines: SW-53826 (won't-fix per SW-49774's precedent)
- CompetitiveFactor rounding — full precision in memory, `decimal(18,4)` truncates on save; audit re-reads the rounded value → $1 diff; forward-only fix, in-force keeps the mismatch: SW-49524, SW-50197, SW-49527, SW-50214

## Step 3 — Interpretation gotchas (READ — don't rediscover)
- **Recompute's Hurricane = 0 is a CLONE ARTIFACT**, not a bug — the in-RAM reprice doesn't re-run the
  SAR hurricane cat model, so Recompute's total comes out ~$1k low. The *audit* (Excel vs DB) reproduces
  hurricane fine. Ignore Recompute's hurricane. ("Hurricane base rate X vs Excel 0" on the Base Rates
  sheet is also a downstream non-issue for SAR-hurricane states.)
- **Commercial Recompute's hurricane is an artifact too** — the in-RAM recalc's SAR call fails
  (`ApplySarResultActor … SAR data version: N but response has: 1`), collapsing Recompute's
  hurricane premium and everything premium-banded downstream (policy fee tier, premium tax, SLSF).
  Diagnose from DB vs Excel; use Recompute only for non-hurricane components.
- Diagnose by **Excel(now) vs DB(bind)** — that's the audit. Recompute is supplementary.
- The $ delta must **reconcile to the penny** via the changed factor. If it doesn't, you named the wrong one.
- **No audit backoff:** a single failing quote re-fires every run → 100s of occurrences/day. Occurrence
  count ≠ number of affected quotes.
- **Signature churn:** diagnostics PRs changed the error text, so LogMonitor auto-filed "new" tickets for
  the *same* bug (e.g. SW-48603→SW-49035). Check for duplicates before chasing.
- **RCA can be wrong early** — SW-47164 had THREE wrong root causes before the right one. Don't commit
  until the diagnostic test reproduces it.

## Step 4 — Fix per immutability
A shipped/in-force version keeps its values. Restore the bind-era value for the shipped version; new
values go only in a NEW version for new business. For category E, the fix is usually forward-only (or
no code at all — UW/data correction). Never bring C# "up to" a changed value on an in-force config.

## Key files
- `Swyfft.Services.Excel/ExcelQuoteAuditServiceBase.cs` — GenerateAuditDoc flow.
- `Swyfft.Services.Excel/Homeowner/ByPeril/Audit/ByPerilHomeownerExcelQuoteAuditService.cs` — HO ComparePremium (tolerance).
- `Swyfft.Services.Excel/Commercial/CommercialExcelQuoteAuditService.cs` — Commercial ComparePremium (tolerance).
- `Swyfft.Services.Excel.IntegrationTests/ExcelQuoteAuditDiagnosticTestBase.cs` — the shared three-way diagnostic base (asserts via the audit service's own ComparePremium).
- `Swyfft.Services.Excel.IntegrationTests/Homeowner/HomeownerExcelQuoteAuditDiagnosticTests.cs` — HO diagnostic subclass.
- `Swyfft.Services.Excel.IntegrationTests/Commercial/CommercialExcelQuoteAuditDiagnosticTests.cs` — Commercial diagnostic subclass.
- `Swyfft.Seeding/ExcelLoaders/ByPeril/reading-rater-files.md` — DumpRater (recovering a bind-era rater: `git show <sha>:<path> | git lfs smudge > old.xlsm`).
