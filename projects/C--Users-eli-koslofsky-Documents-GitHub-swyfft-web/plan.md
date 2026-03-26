# Plan: E&S 0% Coverage, AOP Deductible, 1% NSD, 25% ARC

## Ground Rules

**ASK before acting** on anything uncertain. Specifically:
- **Constraint code strategy**: Before creating any new constraint codes, present the approach and get approval.
- **Element definitions**: Before adding elements to the ElementLoader, confirm the exact element type, display name, choices, and constraint code assignment.
- **Generator changes**: Before modifying a generator, verify which constraint codes it should add/remove and confirm with the user.
- **Visibility predicates / premium calc**: Before editing QuoteElementFactory, ByPerilElementService, or HomeownerQuoteHelper, confirm the approach.
- **Build/test failures**: If any build or test fails, report the failure and ask — do NOT silently refactor tests or change approach.
- **Unclear patterns**: If the codebase has multiple patterns that could apply, ask which to follow rather than guessing.
- **Rater unstashing**: When unstashing rater files for a state, only replace raters for carriers listed in that ticket. The stash contains raters copied to ALL carrier folders for a state, but some carriers (e.g., ClearBlue Admitted) are NOT part of this work. In AL we accidentally included ClearBlue raters that shouldn't have been there. Cross-check the ticket's carrier list before accepting unstashed files.
The goal is to discuss pros/cons of different approaches together. No going rogue.

---

## Context

Parent epic **SW-46837** ("By Peril HO All States - Feb 28, 2026 Versioned Changes") bundles two sets of changes into the same new quote def versions:
1. **SW-46712** — Wind mitigation revert (already in PR #18781 on the wind-mit-revert branch)
2. **SW-46853** — 0% Cov B/C/D + AOP Deductible + 1% NSD + 25% ARC (this work)

Both target **Feb 28, 2026** go-live. The wind-mit branch already created the new quote def versions/StateConfigs/factory mappings for released products. This branch adds the element changes on top of those same versions.

**Tickets**: SW-46853 (epic), SW-46855 (AL), SW-46856 (FL), SW-46857 (LA), SW-46858 (MA), SW-46859 (MS), SW-46860 (NC), SW-46861 (NJ), SW-46862 (NY), SW-46863 (SC), SW-46864 (TX)

**Branch**: `feature/ek/20260212_SW-46855_SW-46856_SW-46857_SW-46858_SW-46859_SW-46860_SW-46861_SW-46862_SW-46863_SW-46864_eans-0pct-aop-nsd-arc`

**Unreleased products** (modify in-place, no new quote defs): FL ARK V1, TX ARK V1, LA ARK V1, NY QBE V1, MS DOR V1

**Stacked version**: NJ BSIC V7 (stacked after V4/V5/V6 which have 2030 placeholder dates due to sub-fees/IMS blockers). Already created by wind-mit branch.

**Go-live dates** (from SW-46837):
| State | NewQuotesOn | RenewalOn |
|-------|-------------|-----------|
| AL (Admitted+E&S) | `2026-02-28 06:00:00.000` | `2026-04-04` |
| FL E&S | `2026-02-28 05:00:00.000` | `2026-04-19` |
| LA E&S | `2026-02-28 06:00:00.000` | `2026-04-04` |
| MA (Admitted+E&S) | `2026-02-28 05:00:00.000` | `2026-04-19` |
| NC E&S | `2026-02-28 05:00:00.000` | `2026-04-04` |
| SC E&S | `2026-02-28 05:00:00.000` | `2026-05-04` |
| TX (Admitted+E&S) | `2026-02-28 06:00:00.000` | `2026-04-04` |

---

## Step 0: Download and replace Excel raters — DONE

All 10 rater files downloaded from SharePoint and copied to 27 carrier-specific files. Changes are **stashed** (`git stash` — "All 10 state rater files"). Each story unstashes its own state's raters.

---

## CRITICAL: ByPerilVersionLookup — Check Before Modifying

**Before adding version settings to ANY lookup version, grep `HomeownerStateConfig.cs` for all state configs that reference it.**

- If the lookup version is used by ONLY the new state config (e.g., wind-mit branch already created a dedicated one), it's safe to add settings to it.
- If it's shared by older state configs too, you MUST create a NEW lookup version and point only the new state config at it.

Example (AL — the mistake we made and fixed):
- V7, V8, and V9 all pointed to `ByPerilVersionLookup.Homeowner.AL.EAndS.BenchmarkSpecialty.V5`
- Adding LimitedWaterDamage V2 to V5 broke V7/V8 quote creation
- Fix: Created V6 = V5.Clone() + new settings, pointed only V9 at V6

**This is case-by-case per state.** The wind-mit branch may or may not have created a dedicated lookup version for each state's new config. Always verify.

---

## CRITICAL: ByPerilName vs QuoteElementName

**ByPerilVersionLookup uses `ByPerilName` (seeded factor table names), NOT `QuoteElementName` (element names).**

The correct names for version lookups are:
- `ByPerilName.CoverageB` (NOT `CoverageBLimit`)
- `ByPerilName.CoverageC` (NOT `CoverageCLimit`)
- `ByPerilName.CoverageD` (NOT `CoverageDLimit`)
- `ByPerilName.AopDeductible`
- `ByPerilName.LimitedWaterDamage`

---

## What AL Created (Shared Plumbing — Already Done)

The AL commit created shared infrastructure that subsequent states reuse. **Do NOT recreate these.**

### Shared across all states (already committed):
| Component | File | What was added |
|-----------|------|----------------|
| Constraint codes | `ConstraintCode.cs` | `ByPerilDeclineOtherStructures`, `ByPerilDeclineContents`, `ByPerilDeclineLivingExpenses` |
| Element names | `QuoteElementName.cs` | `DeclineOtherStructuresCoverage`, `CoverageBOtherStructuresDeclined` |
| Element definitions | `ElementLoader_Homeowner_ByPeril.cs` | 3 decline toggle + 3 declined companion elements |
| Visibility predicates | `QuoteElementFactory.cs` | 6 predicates on shared codes (`ByPerilNewCoverageB/C/D` + `ByPerilDecline*`) |
| Premium calc | `ByPerilElementService.cs` | CoverageBLimit decline check |
| TIV calc | `HomeownerQuoteHelper.cs` | CoverageBLimit decline check in GetTotalInsuredValue |
| Rater comparison | `ByPerilPremiumCalculator.cs` | SurplusLinesServiceFee excluded from Excel rater comparison |
| Version cell names | `ByPerilCellNames.cs` | `CoverageBVersion`, `CoverageBLimitVersion`, `CoverageCLimitVersion`, `CoverageDLimitVersion` |
| Seeder refactor | `ByPerilSeederHomeowner.cs` | Extracted `SeedCoverageBFactors()` and `SeedCoverageCFactors()` to virtual methods |

### AL-specific (pattern for other states):
| Component | File | What was added |
|-----------|------|----------------|
| AOP constraint code | `ConstraintCode.cs` | `ByPerilEAndSAopAL` (state-specific — other states with AOP need their own) |
| AOP element | `ElementLoader_Homeowner_ByPeril.cs` | AL-specific AOP with $25K/$50K options |
| Version lookup | `ByPerilVersionLookup.cs` | V6 for AL BSIC E&S (CoverageB/C/D V2, AopDeductible V3, LimitedWaterDamage V2) |
| Generator | `DefaultElementGeneratorByPerilEAndSBenchmarkSpecialtyV5AL.cs` | Added decline + AOP + LWD constraint codes |
| Seeder override | `ByPerilSeederHomeownerEAndSBenchmarkSpecialtyAL.cs` | Versioned CoverageB/C/D seeding + LWD V2 |
| LWD premium calc | `HomeownerEAndSByPerilPremiumGeneratorBenchmarkSpecialtyAL.cs` | LWD V2 logarithmic formula override |

---

## Per-State Checklist (What Each Remaining State Needs)

For each state, work through this checklist:

### 0. Review `Swyfft.Seeding/ExcelLoaders/ByPeril/CLAUDE.md`
- Before making any changes, re-read the ByPeril seeding CLAUDE.md to ensure all three paths (C# premium generator, Excel audit service, validation tests) are covered.
- Key sections to verify against:
  - **"Before finalizing any version bump" checklist** — Versions tab, Input tab, trace new inputs, element generator defaults, quote migrations
  - **Excel rater service `TableNameToExcelCellVersionName`** — ensure new versioned factors are mapped so the audit service writes the correct version to the Versions tab
  - **Seeder: static vs formula data** — determine if `SetLength` is needed or if default read-all behavior is correct
  - **Premium generator** — check if any formula replication is needed (Coverage B/C/D are static lookups, no formula replication needed)
  - **Three paths must agree** — C# uses DB version lookup, Excel rater gets version via `TableNameToExcelCellVersionName`, validation tests compare them

### 1. Rater files
- Unstash from git stash

### 2. ByPerilVersionLookup (CRITICAL — check sharing first!)
- Grep `HomeownerStateConfig.cs` for all configs referencing the lookup version
- If shared: create new lookup version; if dedicated: add to existing
- Use `ByPerilName.CoverageB` / `CoverageC` / `CoverageD` (NOT `CoverageBLimit` etc.)

### 3. Seeder override (if rater has versioned Coverage B/C/D layout)
- Check if the state's rater has version columns in Coverage B/C/D sheets
- If yes: create `ByPerilSeederHomeownerEAndS{Carrier}{State}.cs` overriding `SeedCoverageBFactors`/`SeedCoverageCFactors`/`SeedCoverageDFactors` with versioned format (like AL)
- If no: the base class seeding is fine

### 4. Generator update
- Add `ByPerilDeclineOtherStructures` (for Cov B 0%)
- Add `ByPerilDeclineContents` (for Cov C 0%, if applicable)
- Add `ByPerilDeclineLivingExpenses` (for Cov D 0%, if applicable)
- If AOP changes: swap old AOP code for new state-specific AOP code
- If LWD changes: add `ByPerilLimitedWaterDamageAllOptions` (swap from `ByPerilLimitedWaterDamage`)

### 5. LWD premium generator override (if LWD V2)
- If the state gets LWD V2: the state's premium generator needs `GetLimitedWaterDamageRiskFactors` override (same pattern as AL)

### 6. State-specific new elements (if AOP/NSD/ARC changes)
- AOP: new constraint code + ElementLoader entry per state (different states may have different option sets)
- NSD: add 1% choice to existing state-specific NSD constraint code
- ARC: create ARC elements/codes (first needed in NC commit)

### 7. New StateConfigs / QuoteDefinitions (if not already created by wind-mit)
- FL is the main case — wind-mit didn't include FL, so FL needs new StateConfigs, QuoteDefinitions, generators, and factory registration
- Other unreleased products (ARK, DOR, NY QBE) are modified in-place

### 8. Excel validation tests
- Write or update test class for new version
- Run new + previous version tests

### 9. Seed + verify (see Per-Story Verification below)

---

## Commit 1: SW-46855 — AL E&S HO — DONE

### Ticket Description (from YouTrack)

> ## Summary
>
> **0% Coverage Limits:** Adds 0% options for Coverage B (Other Structures), Coverage C (Contents), and Coverage D (Loss of Use).
>
> **AOP Deductible:** Adds $25,000 and $50,000 options to the AOP Deductible dropdown.
>
> ## Versioning
>
> AL BSIC E&S is released. These changes share the same version bump as the wind mitigation revert (SW-46712) — no additional quote def needed.
>
> See parent epic **SW-46837** for go-live dates.
>
> ## Technical Details
>
> ### ByPerilVersionLookup
>
> Add to the **same** ByPerilVersionLookup version being created for wind mit (`ByPerilVersionLookup.Homeowner.AL.EAndS.BenchmarkSpecialty`):
>
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageCLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageDLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.AopDeductible, SwyfftVersion.V3)`
>
> ### Element Work
>
> - **Decline Other Structures Coverage** (`DeclineOtherStructuresCoverage`): NEW — must be created.
> - **Decline Contents Coverage** (`DeclineContentsCoverage`): NEW — must be created.
> - **Decline Living Expenses** (`DeclineLivingExpenses`): NEW — must be created.
> - **AOP Deductible:** Add $25,000 and $50,000 options to existing dropdown.
>
> ### Rater
>
> HO_ES_TOPA_AL_Rater_2026_02_03.xlsm

All AL changes committed in `ea796cbf620`.

---

## Commit 2: SW-46856 — FL E&S HO - 0% Coverage B

### Ticket Description (from YouTrack)

> ## Summary
>
> Adds a **0% option for Coverage B** (Other Structures) only. No changes to Coverage C, D, or AOP Deductible for FL.
>
> Note: QBE FL already has "Decline Contents Coverage" (Coverage C 0%) — that's unrelated to this ticket.
>
> ## Versioning
>
> FL was **not** included in the wind mitigation revert (SW-46712). This ticket requires **new quote def versions** for released carriers. See parent epic **SW-46837** for go-live dates.
>
> | Carrier | Current Version | New Version | Status |
> |---------|----------------|-------------|--------|
> | BSIC | V2 (released) | V3 | New quote def needed |
> | QBE | V4 (released) | V5 | New quote def needed |
> | ARK | V1 (unreleased, 2030) | V1 | Modify in-place |
>
> ## Technical Details
>
> ### ByPerilVersionLookup
>
> **BSIC** — Create new version in `ByPerilVersionLookup.Homeowner.FL.EAndS.BenchmarkSpecialty`:
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
>
> **QBE** — Create new version in `ByPerilVersionLookup.Homeowner.FL.EAndS.Qbe`:
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
>
> **ARK** — Add to existing V1 in `ByPerilVersionLookup.Homeowner.FL.EAndS.Ark`:
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
>
> ### StateConfig and QuoteDefinitions
>
> Create new HomeownerStateConfig entries and add to `Data/QuoteDefinitions.txt`:
> - `FL.BSIC.ByPeril.EAndS.V3`
> - `FL.QBE.ByPeril.EAndS.V5`
>
> Add override entries to `Seeder.cs` → `CustomizeCoreLocalAndDevAndBeta()`.
>
> ### Element Work
>
> - **Decline Other Structures Coverage** (`DeclineOtherStructuresCoverage`): NEW — must be created for all 3 carriers.
>
> ### Rater
>
> HO_ES_TOPA_FL_Rater_2026_01_26.xlsm

### Steps

1. Unstash FL rater files from stash
2. Reuse Cov B decline elements/codes created in AL commit
3. **Create new StateConfig entries** + QuoteDefinitions for FL BSIC V3, QBE V5
4. **Create new generators** + factory registration
5. Add ByPerilVersionLookup entries (check sharing!)
6. Check if FL rater has versioned CoverageB sheet — if so, create seeder override
7. Update ARK generator in-place
8. Add override entries to Seeder.cs
9. Write/update Excel validation test classes
10. Verify (see Per-Story Verification below)
11. Commit

### ByPerilVersionLookup

**BSIC** — Create new version: `.SetVersion(ByPerilName.CoverageB, SwyfftVersion.V2)`
**QBE** — Create new version: `.SetVersion(ByPerilName.CoverageB, SwyfftVersion.V2)`
**ARK** — Add to existing V1: `.SetVersion(ByPerilName.CoverageB, SwyfftVersion.V2)` (check sharing first!)

### New generators + factory registration

- `DefaultElementGeneratorByPerilEAndSBenchmarkSpecialtyV3FL` — inherit from V2, add Cov B decline code
- `DefaultElementGeneratorEAndSQbeV5FL` — inherit from V4, add Cov B decline code
- Update ARK generator in-place
- Register in `HomeownerDefaultElementGeneratorFactory.cs`

### Rater

`HO_ES_TOPA_FL_Rater_2026_01_26.xlsm` → copied to ARK, BSIC, CBS, QBE, TOPA (in stash)

---

## Commit 3: SW-46857 — LA E&S HO - 0% Cov B/C/D

### Ticket Description (from YouTrack)

> ## Summary
>
> **0% Coverage Limits:** Adds 0% options for Coverage B (Other Structures), Coverage C (Contents), and Coverage D (Loss of Use).
>
> ## Versioning
>
> LA BSIC E&S is released. These changes share the same version bump as the wind mitigation revert (SW-46712). LA ARK E&S is unreleased (2030 placeholder) — modify in-place.
>
> See parent epic **SW-46837** for go-live dates.
>
> | Carrier | Status |
> |---------|--------|
> | BSIC | Released — shares version bump with wind mit |
> | ARK | Unreleased — modify V1 in-place |
>
> ## Technical Details
>
> ### ByPerilVersionLookup
>
> **BSIC** — Add to the **same** version being created for wind mit (`ByPerilVersionLookup.Homeowner.LA.EAndS.BenchmarkSpecialty`):
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageCLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageDLimit, SwyfftVersion.V2)`
>
> **ARK** — Add to existing V1 in `ByPerilVersionLookup.Homeowner.LA.EAndS.Ark`:
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageCLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageDLimit, SwyfftVersion.V2)`
>
> ### Element Work
>
> - **Decline Other Structures Coverage** (`DeclineOtherStructuresCoverage`): NEW — must be created.
> - **Decline Contents Coverage** (`DeclineContentsCoverage`): NEW — must be created.
> - **Decline Living Expenses** (`DeclineLivingExpenses`): NEW — must be created.
>
> ### Rater
>
> HO_ES_TOPA_LA_Rater_2026_01_26.xlsm

### Steps

1. Unstash LA rater files
2. Reuse Cov B/C/D decline elements/codes from AL commit
3. Add ByPerilVersionLookup entries (check sharing!)
4. Check if LA rater has versioned CoverageB/C/D sheets — if so, create seeder override
5. Update BSIC + ARK generators
6. Write/update Excel validation test classes
7. Verify (see Per-Story Verification below)
8. Commit

### ByPerilVersionLookup

**BSIC** — Add to wind mit version: `.SetVersion(ByPerilName.CoverageB, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.CoverageC, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.CoverageD, SwyfftVersion.V2)`
**ARK** — Add to existing V1: same three settings (check sharing first!)

### Rater

`HO_ES_TOPA_LA_Rater_2026_01_26.xlsm` → copied to ARK, BSIC, TOPA (in stash)

---

## Commit 4: SW-46858 — MA E&S HO - 0% Cov B/C/D + AOP Deductible

### Ticket Description (from YouTrack)

> ## Summary
>
> **0% Coverage Limits:** Adds 0% options for Coverage B (Other Structures), Coverage C (Contents), and Coverage D (Loss of Use). All three are genuinely new for MA — no prior 0% options existed.
>
> **AOP Deductible:** Adds $25,000 and $50,000 options to the AOP Deductible dropdown.
>
> ## Versioning
>
> MA BSIC E&S is released. These changes share the same version bump as the wind mitigation revert (SW-46712) — no additional quote def needed.
>
> See parent epic **SW-46837** for go-live dates.
>
> ## Technical Details
>
> ### ByPerilVersionLookup
>
> Add to the **same** version being created for wind mit (`ByPerilVersionLookup.Homeowner.MA.EAndS.BenchmarkSpecialty`):
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageCLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageDLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.AopDeductible, SwyfftVersion.V4)`
>
> ### Element Work
>
> - **Decline Other Structures Coverage** (`DeclineOtherStructuresCoverage`): NEW — must be created.
> - **Decline Contents Coverage** (`DeclineContentsCoverage`): NEW — must be created.
> - **Decline Living Expenses** (`DeclineLivingExpenses`): NEW — must be created.
> - **AOP Deductible:** Add $25,000 and $50,000 options to existing dropdown.
>
> ### Rater
>
> HO_ES_TOPA_MA_Rater_2026_02_03.xlsm

### Steps

1. Unstash MA rater files
2. Reuse Cov B/C/D decline elements/codes
3. Create MA-specific AOP constraint code (or reuse AL's if same choices) + ElementLoader entry
4. Add ByPerilVersionLookup entries (check sharing!)
5. Check if MA rater has versioned CoverageB/C/D sheets — if so, create seeder override
6. Update generator (add decline codes + swap AOP code)
7. Write/update Excel validation test classes
8. Verify (see Per-Story Verification below)
9. Commit

### ByPerilVersionLookup

Add to wind mit version: `.SetVersion(ByPerilName.CoverageB, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.CoverageC, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.CoverageD, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.AopDeductible, SwyfftVersion.V4)`

### Rater

`HO_ES_TOPA_MA_Rater_2026_02_03.xlsm` → copied to BSIC, CBS, TOPA (in stash)

---

## Commit 5: SW-46859 — MS E&S HO - 0% Cov B/C/D

### Ticket Description (from YouTrack)

> ## Summary
>
> **0% Coverage Limits:** Adds 0% options for Coverage B (Other Structures), Coverage C (Contents), and Coverage D (Loss of Use).
>
> ## Versioning
>
> MS DOR E&S is **unreleased** (2030 placeholder dates). Modify existing V1 in-place — no new quote def needed.
>
> ## Technical Details
>
> ### ByPerilVersionLookup
>
> Add to existing V1 in `ByPerilVersionLookup.Homeowner.MS.EAndS.Dorchester`:
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageCLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageDLimit, SwyfftVersion.V2)`
>
> ### Element Work
>
> - **Decline Other Structures Coverage** (`DeclineOtherStructuresCoverage`): NEW — must be created.
> - **Decline Contents Coverage** (`DeclineContentsCoverage`): NEW — must be created.
> - **Decline Living Expenses** (`DeclineLivingExpenses`): NEW — must be created.
>
> ### Rater
>
> HO_ES_DOR_MS_Rater_2026_01_26.xlsm

### Steps

1. Unstash MS rater files
2. Reuse Cov B/C/D decline elements/codes
3. Add ByPerilVersionLookup entries (check sharing!)
4. Check if MS rater has versioned CoverageB/C/D sheets — if so, create seeder override
5. Update DOR generator in-place
6. Write/update Excel validation test classes
7. Verify (see Per-Story Verification below)
8. Commit

### ByPerilVersionLookup

Add to existing V1: `.SetVersion(ByPerilName.CoverageB, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.CoverageC, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.CoverageD, SwyfftVersion.V2)` (check sharing first!)

### Rater

`HO_ES_DOR_MS_Rater_2026_01_26.xlsm` → copied to DOR (in stash)

---

## Commit 6: SW-46860 — NC E&S HO - 0% Cov B/D + 1% NSD + 25% ARC

### Ticket Description (from YouTrack)

> ## Summary
>
> Adds 0% options for **Coverage B** (Other Structures) and **Coverage D** (Loss of Use). Also adds **1% Named Storm Deductible** option for BSIC and **25% Additional Replacement Cost** option for both carriers.
>
> Note: QBE NC already has "Decline Living Expenses" (Coverage D 0%), so the Cov D element work is BSIC-only. QBE NC already has 1% NSD (added in SW-46363), so the NSD element change is BSIC-only.
>
> ## Versioning
>
> Both NC carriers are released. These changes share the same version bump as the wind mitigation revert (SW-46712) — no additional quote defs needed.
>
> See parent epic **SW-46837** for go-live dates.
>
> | Carrier | Status |
> |---------|--------|
> | BSIC | Released — shares version bump with wind mit |
> | QBE | Released — shares version bump with wind mit |
>
> ## Technical Details
>
> ### ByPerilVersionLookup
>
> **BSIC** — Add to the **same** version being created for wind mit (`ByPerilVersionLookup.Homeowner.NC.EAndS.BenchmarkSpecialty`):
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageDLimit, SwyfftVersion.V2)`
>
> **QBE** — Add to the **same** version being created for wind mit (`ByPerilVersionLookup.Homeowner.NC.EAndS.Qbe`):
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageDLimit, SwyfftVersion.V2)`
>
> ### Element Work — 0% Cov B/D
>
> - **Decline Other Structures Coverage** (`QuoteElementName.DeclineOtherStructuresCoverage`): NEW for both BSIC and QBE — must be created.
> - **Decline Living Expenses** (`QuoteElementName.DeclineLivingExpenses`): NEW for BSIC only. QBE already has this element.
>
> ### Element Work — 1% Named Storm Deductible
>
> - **Named Storm Deductible** (`QuoteElementName.NamedStormDeductible`): Add `Percent_1` choice to existing BSIC element (`ConstraintCode.ByPerilNamedStormNC`). QBE already has 1% via `ConstraintCode.ByPerilQbeNamedStormNC` (SW-46363).
>
> ### Element Work — 25% Additional Replacement Cost
>
> - **Additional Replacement Cost** (`QuoteElementName.AdditionalReplacementCost`): NEW for both BSIC and QBE. Follow FL pattern — create ARC Choice element (options: None, 25%) alongside existing GRC boolean. Needs new constraint code(s).
>
> ### Rater
>
> HO_ES_BSIC_NC_Rater_2026_02_09.xlsm

### Steps

1. Unstash NC rater files
2. Reuse Cov B decline elements/codes
3. Add Cov D decline for BSIC (reuse code from AL or create BSIC-specific)
4. Add 1% choice to BSIC NSD element (`ByPerilNamedStormNC`)
5. Create ARC elements/codes for NC (follow FL pattern)
6. Add ByPerilVersionLookup entries (check sharing!)
7. Check if NC rater has versioned CoverageB/D sheets — if so, create seeder override
8. Update BSIC + QBE generators
9. Write/update Excel validation test classes
10. Verify
11. Commit

### ByPerilVersionLookup

**BSIC** — Add to wind mit version: `.SetVersion(ByPerilName.CoverageB, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.CoverageD, SwyfftVersion.V2)`
**QBE** — Add to wind mit version: `.SetVersion(ByPerilName.CoverageB, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.CoverageD, SwyfftVersion.V2)`

### Rater

`HO_ES_BSIC_NC_Rater_2026_02_09.xlsm` → **same file** copied to both BSIC and QBE carrier folders (in stash). All carriers share a single rater.

---

## Commit 7: SW-46861 — NJ E&S HO - 0% Cov B/D + 1% NSD + 25% ARC

### Ticket Description (from YouTrack)

> ## Summary
>
> Adds 0% options for **Coverage B** (Other Structures) and **Coverage D** (Loss of Use). Also includes a Cov D slider fix (max up to 30% x Cov A). Also adds **1% Named Storm Deductible** option for BSIC and **25% Additional Replacement Cost** option for both carriers.
>
> Note: QBE NJ already has "Decline Living Expenses" (Coverage D 0%), so the Cov D element work is BSIC-only. QBE NJ already has 1% NSD (added in SW-46363), so the NSD element change is BSIC-only.
>
> ## Versioning
>
> NJ BSIC E&S is released but has stacked unreleased versions (V4/V5/V6 blocked by sub-fees/IMS). These changes go into **V7**, stacked after V6 — same version as the wind mitigation revert (SW-46712).
>
> NJ QBE E&S is **unreleased** (V1 with 2030 placeholder) — modify in-place.
>
> See parent epic **SW-46837** for details on the stacking situation.
>
> | Carrier | Status |
> |---------|--------|
> | BSIC | Stacked V7 — shares with wind mit |
> | QBE | Unreleased — modify V1 in-place |
>
> ## Technical Details
>
> ### ByPerilVersionLookup
>
> **BSIC** — Add to the **same** stacked version being created for wind mit (`ByPerilVersionLookup.Homeowner.NJ.EAndS.BenchmarkSpecialty`):
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageDLimit, SwyfftVersion.V2)`
>
> **QBE** — Add to existing V1 in `ByPerilVersionLookup.Homeowner.NJ.EAndS.Qbe`:
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageDLimit, SwyfftVersion.V2)`
>
> ### Element Work — 0% Cov B/D
>
> - **Decline Other Structures Coverage** (`QuoteElementName.DeclineOtherStructuresCoverage`): NEW for both BSIC and QBE — must be created.
> - **Decline Living Expenses** (`QuoteElementName.DeclineLivingExpenses`): NEW for BSIC only. QBE already has this element.
> - **Cov D slider:** Fix max to 30% x Cov A (rater change).
>
> ### Element Work — 1% Named Storm Deductible
>
> - **Named Storm Deductible** (`QuoteElementName.NamedStormDeductible`): Add `Percent_1` choice to existing BSIC element (`ConstraintCode.ByPerilNamedStormNJ`). QBE already has 1% via `ConstraintCode.ByPerilQbeNamedStormNJ` (SW-46363).
>
> ### Element Work — 25% Additional Replacement Cost
>
> - **Additional Replacement Cost** (`QuoteElementName.AdditionalReplacementCost`): NEW for both BSIC and QBE. Follow FL pattern — create ARC Choice element (options: None, 25%) alongside existing GRC boolean. Needs new constraint code(s).
>
> ### Rater
>
> HO_ES_BSIC_NJ_Rater_2026_02_09.xlsm

### Steps

1. Unstash NJ rater files
2. Reuse Cov B decline elements/codes
3. Add Cov D decline for BSIC (reuse code)
4. Add 1% choice to BSIC NSD element (`ByPerilNamedStormNJ`)
5. Reuse ARC elements/codes from NC
6. Add ByPerilVersionLookup entries (check sharing!)
7. Check if NJ rater has versioned CoverageB/D sheets — if so, create seeder override
8. Update BSIC + QBE generators
9. Write/update Excel validation test classes
10. Verify
11. Commit

### ByPerilVersionLookup

**BSIC** — Add to stacked V7: `.SetVersion(ByPerilName.CoverageB, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.CoverageD, SwyfftVersion.V2)`
**QBE** — Add to existing V1: `.SetVersion(ByPerilName.CoverageB, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.CoverageD, SwyfftVersion.V2)` (check sharing first!)

### Rater

`HO_ES_BSIC_NJ_Rater_2026_02_09.xlsm` → **same file** copied to both BSIC and QBE carrier folders (in stash). All carriers share a single rater.

---

## Commit 8: SW-46862 — NY E&S HO - 0% Cov B/D

### Ticket Description (from YouTrack)

> ## Summary
>
> Adds a **0% option for Coverage B** (Other Structures). Coverage D rater table is bumped to V2, but QBE NY already has "Decline Living Expenses" — no new Cov D element work needed. Also includes a Cov D slider fix (max up to 30% x Cov A).
>
> ## Versioning
>
> NY QBE E&S is **unreleased** (V1 with 2030 placeholder) — modify in-place. No new quote def needed.
>
> ## Technical Details
>
> ### ByPerilVersionLookup
>
> Add to existing V1 in `ByPerilVersionLookup.Homeowner.NY.EAndS.Qbe`:
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageDLimit, SwyfftVersion.V2)`
>
> ### Element Work
>
> - **Decline Other Structures Coverage** (`DeclineOtherStructuresCoverage`): NEW — must be created.
> - **Decline Living Expenses** (`DeclineLivingExpenses`): QBE already has this element — no work needed.
> - **Cov D slider:** Fix max to 30% x Cov A (rater change).
>
> ### Rater
>
> ~~HO_ES_NY_Rater_2026_01_26.xlsm~~ — **REPLACED**: The stashed NY rater is outdated. Alex posted an updated rater that includes the 25% ARC option: `HO_ES_NY_Rater_2026_02_09.xlsm` (see [Slack thread](https://swyfft.slack.com/archives/C06V258BWHJ/p1771443359429389)). The updated rater has been downloaded to `C:\Users\eli.koslofsky\Downloads\HO_ES_TOPA_MA_Rater_2026_02_03 (2).xlsm`. **Do NOT use the stashed rater — replace it with this downloaded file.**

### Steps

1. Copy corrected NY rater from Downloads to the QBE carrier path (do NOT use stash — stash has an outdated rater):
   - `Data\NY\Homeowner\ByPeril\EAndS\HO_ES_QBE_NY_Rater.xlsm`
2. Reuse Cov B decline elements/codes
3. Add ByPerilVersionLookup entries (check sharing!)
4. Check if NY rater has versioned CoverageB/D sheets — if so, create seeder override
5. Update QBE generator in-place
6. Write/update Excel validation test classes
7. Verify (see Per-Story Verification below)
8. Commit

### ByPerilVersionLookup

Add to existing V1: `.SetVersion(ByPerilName.CoverageB, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.CoverageD, SwyfftVersion.V2)` (check sharing first!)

### Rater

`HO_ES_NY_Rater_2026_01_26.xlsm` → copied to QBE carrier folder (in stash). NY only has one E&S carrier.

---

## Commit 9: SW-46863 — SC E&S HO - 0% Cov B/D + 1% NSD + 25% ARC

### Ticket Description (from YouTrack)

> ## Summary
>
> Adds 0% options for **Coverage B** (Other Structures) and **Coverage D** (Loss of Use). Also includes a Cov D slider fix (max up to 30% x Cov A). Also adds **1% Named Storm Deductible** option for BSIC and **25% Additional Replacement Cost** option for both carriers.
>
> Note: QBE SC already has "Decline Living Expenses" (Coverage D 0%), so the Cov D element work is BSIC-only. QBE SC already has 1% NSD (added in SW-46363), so the NSD element change is BSIC-only.
>
> ## Versioning
>
> Both SC carriers are released. These changes share the same version bump as the wind mitigation revert (SW-46712) — no additional quote defs needed.
>
> See parent epic **SW-46837** for go-live dates.
>
> | Carrier | Status |
> |---------|--------|
> | BSIC | Released — shares version bump with wind mit |
> | QBE | Released — shares version bump with wind mit |
>
> ## Technical Details
>
> ### ByPerilVersionLookup
>
> **BSIC** — Add to the **same** version being created for wind mit (`ByPerilVersionLookup.Homeowner.SC.EAndS.BenchmarkSpecialty`):
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageDLimit, SwyfftVersion.V2)`
>
> **QBE** — Add to the **same** version being created for wind mit (`ByPerilVersionLookup.Homeowner.SC.EAndS.Qbe`):
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageDLimit, SwyfftVersion.V2)`
>
> ### Element Work — 0% Cov B/D
>
> - **Decline Other Structures Coverage** (`QuoteElementName.DeclineOtherStructuresCoverage`): NEW for both BSIC and QBE — must be created.
> - **Decline Living Expenses** (`QuoteElementName.DeclineLivingExpenses`): NEW for BSIC only. QBE already has this element.
> - **Cov D slider:** Fix max to 30% x Cov A (rater change).
>
> ### Element Work — 1% Named Storm Deductible
>
> - **Named Storm Deductible** (`QuoteElementName.NamedStormDeductible`): Add `Percent_1` choice to existing BSIC element (`ConstraintCode.ByPerilNamedStormSC`). QBE already has 1% via `ConstraintCode.ByPerilQbeNamedStormSC` (SW-46363).
>
> ### Element Work — 25% Additional Replacement Cost
>
> - **Additional Replacement Cost** (`QuoteElementName.AdditionalReplacementCost`): NEW for both BSIC and QBE. Follow FL pattern — create ARC Choice element (options: None, 25%) alongside existing GRC boolean. Needs new constraint code(s).
>
> ### Rater
>
> HO_ES_BSIC_SC_Rater_2026_02_09.xlsm

### Steps

1. Copy corrected SC rater from `C:\Users\eli.koslofsky\Downloads\HO_ES_BSIC_SC_Rater_2026_02_09.xlsm` to BOTH carrier paths (do NOT use stash — stash has the old rater with the ARC VLOOKUP bug that Quentin fixed):
   - `Data\SC\Homeowner\ByPeril\EAndS\HO_ES_BSIC_SC_Rater.xlsm`
   - `Data\SC\Homeowner\ByPeril\EAndS\HO_ES_QBE_SC_Rater.xlsm`
2. Reuse Cov B decline elements/codes
3. Add Cov D decline for BSIC (reuse code)
4. Add 1% choice to BSIC NSD element (`ByPerilNamedStormSC`)
5. Reuse ARC elements/codes from NC
6. Add ByPerilVersionLookup entries (check sharing!)
7. Check if SC rater has versioned CoverageB/D sheets — if so, create seeder override
8. Update BSIC + QBE generators
9. Write/update Excel validation test classes
10. Verify
11. Commit

### ByPerilVersionLookup

**BSIC** — Add to wind mit version: `.SetVersion(ByPerilName.CoverageB, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.CoverageD, SwyfftVersion.V2)`
**QBE** — Add to wind mit version: `.SetVersion(ByPerilName.CoverageB, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.CoverageD, SwyfftVersion.V2)`

### Rater

`HO_ES_BSIC_SC_Rater_2026_02_09.xlsm` → **same file** copied to both BSIC and QBE carrier folders (in stash). All carriers share a single rater.

---

## Commit 10: SW-46864 — TX E&S HO - 0% Cov B/D + AOP Deductible

### Ticket Description (from YouTrack)

> ## Summary
>
> **0% Coverage Limits:** Adds 0% options for Coverage B (Other Structures) and Coverage D (Loss of Use).
>
> **AOP Deductible:** Adds $25,000 and $50,000 options plus a new **0.2% floor** option to the AOP Deductible dropdown.
>
> Note: QBE TX already has "Decline Living Expenses" (Coverage D 0%), so the Cov D element work is BSIC/ARK only.
>
> ## Versioning
>
> TX BSIC E&S and QBE E&S are released. These changes share the same version bump as the wind mitigation revert (SW-46712). TX ARK E&S is unreleased (2030 placeholder) — modify in-place.
>
> See parent epic **SW-46837** for go-live dates.
>
> | Carrier | Status |
> |---------|--------|
> | BSIC | Released — shares version bump with wind mit |
> | QBE | Released — shares version bump with wind mit |
> | ARK | Unreleased — modify V1 in-place |
>
> ## Technical Details
>
> ### ByPerilVersionLookup
>
> **BSIC** — Add to the **same** version being created for wind mit (`ByPerilVersionLookup.Homeowner.TX.EAndS.BenchmarkSpecialty`):
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageDLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.AopDeductible, SwyfftVersion.V3)`
>
> **QBE** — Add to the **same** version being created for wind mit (`ByPerilVersionLookup.Homeowner.TX.EAndS.Qbe`):
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageDLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.AopDeductible, SwyfftVersion.V3)`
>
> **ARK** — Add to existing V1 in `ByPerilVersionLookup.Homeowner.TX.EAndS.Ark`:
> - `.SetVersion(ByPerilName.CoverageBLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.CoverageDLimit, SwyfftVersion.V2)`
> - `.SetVersion(ByPerilName.AopDeductible, SwyfftVersion.V3)`
>
> ### Element Work
>
> - **Decline Other Structures Coverage** (`DeclineOtherStructuresCoverage`): NEW for all carriers — must be created.
> - **Decline Living Expenses** (`DeclineLivingExpenses`): NEW for BSIC and ARK. QBE already has this element.
> - **AOP Deductible:** Add $25,000, $50,000, and 0.2% floor options to existing dropdown.
>
> ### Rater
>
> HO_ES_TOPA_TX_Rater_2026_02_03.xlsm

### Steps

1. Unstash TX rater files
2. Reuse Cov B decline elements/codes
3. Add Cov D decline for BSIC/ARK (reuse code)
4. Create TX-specific AOP constraint code (adds $25K/$50K + 0.2% to non-QBE) + ElementLoader entry
5. Add ByPerilVersionLookup entries (check sharing!)
6. Check if TX rater has versioned CoverageB/D sheets — if so, create seeder override
7. Update BSIC + QBE + ARK generators
8. Write/update Excel validation test classes
9. Verify (see Per-Story Verification below)
10. Commit

### ByPerilVersionLookup

**BSIC** — Add to wind mit version: `.SetVersion(ByPerilName.CoverageB, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.CoverageD, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.AopDeductible, SwyfftVersion.V3)`
**QBE** — Add to wind mit version: `.SetVersion(ByPerilName.CoverageB, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.CoverageD, SwyfftVersion.V2)`, `.SetVersion(ByPerilName.AopDeductible, SwyfftVersion.V3)`
**ARK** — Add to existing V1: same three settings (check sharing first!)

### Rater

`HO_ES_TOPA_TX_Rater_2026_02_03.xlsm` → **same file** copied to ARK, BSIC, CBS, QBE, TOPA carrier folders (in stash). All carriers share a single rater.

---

## Per-Story Verification (after each commit)

After each story commit, run this verification sequence:

### 0. Review CLAUDE.md documentation
Before running verification, re-read these docs and confirm:

**`Swyfft.Seeding/ExcelLoaders/ByPeril/CLAUDE.md`**:
- All version bumps are in `ByPerilVersionLookup`
- All versioned factors have `TableNameToExcelCellVersionName` mappings in the Excel rater service
- Any new inputs are traced through the full chain (Input tab → QuoteElementName → ByPerilElementService → ByPerilQuoteElementModel → premium generator)
- Static vs formula data is handled correctly in the seeder (SetLength vs read-all)
- No premium generator formula replication is missing

**`Swyfft.Services/Elements/CLAUDE.md`**:
- When adding a constraint code that introduces an element already present under a shared constraint code (e.g., `ByPerilNewGRC` adds GRC boolean, but `ByPeril_NC` already has one), extract the element from the shared code first — see "Replacing a Single Element from a Shared Constraint Code"
- Verify no duplicate elements across constraint codes in the generator's list

### 1. Seed database
```powershell
.\Seed-Database-Local.ps1
```
Full seed is required — not just elements — because new raters are involved.

### 2. Write + run Excel validation tests
Write Excel validation test class(es) for the new config in `Swyfft.Services.Excel.IntegrationTests/`. Follow existing patterns:
- Tag with `[Trait(TestGroup, ByPerilTests)]`, `[Trait("Carrier", "...")]`, `[Trait("State", "...")]`
- Use `HomeownerStateConfig.{NewConfig}`
- Override `ElementTestValues` / `ElementCombinationTestValues` as needed for new element options

Run for the specific test class(es) in the commit — both the **new version AND previous versions** to ensure nothing is broken:
```powershell
# New version
dotnet test --project "Swyfft.Services.Excel.IntegrationTests" -- --filter-class "*ByPerilValidationTests{State}{Carrier}V{NewVersion}"
# Previous versions (pass multiple --filter-class for OR)
dotnet test --project "Swyfft.Services.Excel.IntegrationTests" -- --filter-class "*ByPerilValidationTests{State}{Carrier}V{PrevVersion1}" --filter-class "*ByPerilValidationTests{State}{Carrier}V{PrevVersion2}"
```
Verify all pass. If failures, debug using the CLAUDE.md workflow (check saved Excel file in `%TEMP%\Swyfft\ByPerilValidationTests\`).

**CRITICAL: Always `tee` test output to a file** (`2>&1 | tee /tmp/test-output.txt`). If tests fail, you already have the output — do NOT re-run just to see what went wrong.

### 3. Run PreBindResidentialCapturedAssertTests
```powershell
$env:UPDATE_TEST_EXPECTED_RESULTS="true"
dotnet test --project "Swyfft.Services.IntegrationTests" -- --filter-trait "TestGroup=PreBindResidentialCapturedAssertTests" 2>&1 | tee /tmp/captured-assert-integration.txt
dotnet test --project "Swyfft.Services.UnitTests" -- --filter-trait "TestGroup=PreBindResidentialCapturedAssertTests" 2>&1 | tee /tmp/captured-assert-unit.txt
```

### 4. Individually review captured assert changes
For each updated expected result file in `Swyfft.Services.IntegrationTests/ExpectedResults/`:
- **Do NOT spot-check.** Review every change individually.
- Verify new elements appear in the correct position, with correct constraint codes, choices, and defaults.
- Verify comparison quote ordering is correct.
- Report findings to user before proceeding to next commit.

## Final Verification (after all commits)

1. Full build: `dotnet build Swyfft.slnx`
2. Unit tests: `dotnet test --solution SwyfftCI.slnx`
3. Migration coverage: `dotnet test --project "Swyfft.Services.IntegrationTests" -- --filter-class "*MigrationCoverage*"`
