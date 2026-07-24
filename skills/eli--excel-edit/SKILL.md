---
name: eli--excel-edit
description: Edit an Excel workbook (.xlsm/.xlsx) programmatically and natively via Excel COM — set a cell formula, set a cell value, or add/update a workbook-scoped named range. Excel re-saves through its own writer, so all workbook parts and features are preserved (no formatting/print-setting drift). Use for edits to ByPeril rater files and any other workbook deliverable. Requires Excel installed (COM).
---

# Excel Edit (native, via COM)

Applies a small declared set of edits to a workbook through the real Excel engine, then reopens the
saved file and reads every edit back to prove it landed. Excel re-saves the whole workbook with its
own writer, so every part and feature it wrote is preserved (verified on a real rater: 107 parts in,
107 parts out, none dropped). Formulas are recalculated natively so cached values are correct.

**Use this for rater `.xlsm` edits.** A surgical, Excel-native edit keeps the workbook's formatting,
print settings, and structure intact — so the only thing that changes is the cell/name you asked for,
which the captured-assert and ByPeril validation suite then confirm functionally.

## Prerequisite

Excel must be installed (COM). Confirm once with the PowerShell tool:

```powershell
try { $x = New-Object -ComObject Excel.Application; $v=$x.Version; $x.Quit(); "Excel COM: $v" }
catch { "Excel COM NOT available: $($_.Exception.Message)" }
```

## Supported operations

| Operation | Spec entry |
|---|---|
| Set a cell **formula** | `{ "sheet": "Fees", "cell": "C4", "formula": "=IF(InspectionFeeRequired,100,35)" }` |
| Set a cell **value** | `{ "sheet": "Input", "cell": "F60", "value": 0 }` |
| Add/update a **named range** | `{ "name": "InspectionFeeRequired", "refersTo": "Input!$F$60" }` |

Named ranges are applied **before** formulas, so a formula may reference a name added in the same run.
A `=` prefix on `formula`/`refersTo` is optional (added if missing).

## Spec format

```json
{
  "namedRanges": [
    { "name": "InspectionFeeRequired", "refersTo": "Input!$F$60" }
  ],
  "cells": [
    { "sheet": "Fees",  "cell": "C4",  "formula": "=IF(InspectionFeeRequired,100,35)" },
    { "sheet": "Input", "cell": "F60", "value": 0 }
  ]
}
```

Write the spec to a JSON file (the scratchpad dir is fine), then run the driver.

## Run

Use the PowerShell tool (not Bash — pwsh is blocked through Bash):

```powershell
& "$HOME/.claude/skills/eli--excel-edit/Edit-Excel.ps1" -Path "C:\...\HO_ES_BSIC_NC_Rater.xlsm" -SpecPath "C:\...\scratch\nc-edit.json"
```

Inline spec instead of a file:

```powershell
& "$HOME/.claude/skills/eli--excel-edit/Edit-Excel.ps1" -Path "<file>" -Spec '{"cells":[{"sheet":"Fees","cell":"C4","formula":"=IF(InspectionFeeRequired,100,35)"}]}'
```

Add `-Backup` to copy the original to `<file>.bak-<timestamp>` first.

## What it prints

- Original + new SHA256 (errors if the hash didn't change — i.e., nothing persisted).
- Each edit as applied.
- A **Verification** block from a fresh reopen of the saved file: each named range's `RefersTo` and
  each edited cell's `Formula`/`Value2`. Throws if a named range is missing after save.

## After editing a rater

The skill proves the *edit* landed; it does not prove premium correctness. For rater changes, still:
1. Regenerate `RaterFileContents` baselines and read the diff (only the intended cell/name should change).
2. Run the ByPeril Excel validation suite for the affected leaf (C# == Excel).

## Notes / gotchas (handled by the driver)

- `DisplayAlerts`/`AskToUpdateLinks` are off so no modal dialog hangs the run; links are not updated on open.
- The file is `Unblock-File`'d first (mark-of-the-web can force read-only).
- `.xlsm` is saved back as macro-enabled (`.xlsm`); `.xlsx` as `.xlsx`.
- COM objects are released and `EXCEL.EXE` is quit in a `finally`, so no zombie process lingers.
- One workbook at a time. Don't run two instances against the same file concurrently.
