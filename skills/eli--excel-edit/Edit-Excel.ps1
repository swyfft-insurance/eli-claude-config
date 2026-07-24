#Requires -Version 7
<#
.SYNOPSIS
    Apply a small set of declared edits to an Excel workbook (.xlsm/.xlsx) natively via Excel COM,
    preserving every other byte of the file, then read the edits back to prove they landed.

.DESCRIPTION
    Uses the real Excel engine (COM) rather than NPOI/ClosedXML so the file the actuaries reopen is
    their original workbook plus exactly the declared changes — no full re-serialization, no
    formatting/print-setting drift. Excel recalculates natively on save, so cached values are correct.

    Three operations, supplied as a JSON spec:
      - namedRanges: add or update a workbook-scoped defined name -> RefersTo target.
      - cells (formula): set a cell's formula.
      - cells (value):   set a cell's literal value.

    Named ranges are applied BEFORE formulas, so a formula may reference a name added in the same run.

.PARAMETER Path
    Full path to the .xlsm/.xlsx file to edit (edited in place).

.PARAMETER SpecPath
    Path to a JSON file describing the edits. Mutually exclusive with -Spec.

.PARAMETER Spec
    Inline JSON string describing the edits. Mutually exclusive with -SpecPath.

.PARAMETER Backup
    If set, copies the original to "<Path>.bak-<timestamp>" before editing.

.EXAMPLE
    Edit-Excel.ps1 -Path "C:\...\HO_ES_BSIC_NC_Rater.xlsm" -SpecPath "C:\...\nc-edit.json"

    Spec JSON shape:
    {
      "namedRanges": [ { "name": "InspectionFeeRequired", "refersTo": "Input!$F$60" } ],
      "cells":       [ { "sheet": "Fees", "cell": "C4", "formula": "=IF(InspectionFeeRequired,100,35)" },
                       { "sheet": "Input", "cell": "F60", "value": 1 } ]
    }
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Path,
    [string] $SpecPath,
    [string] $Spec,
    [switch] $Backup
)

$ErrorActionPreference = 'Stop'

# Excel SaveAs format codes / open args we rely on.
$xlOpenXMLWorkbookMacroEnabled = 52   # .xlsm
$xlOpenXMLWorkbook             = 51   # .xlsx
$xlCalculationManual           = -4135
$xlCalculationAutomatic        = -4105
$doNotUpdateLinks              = 0

function Resolve-Spec {
    if ($SpecPath -and $Spec) { throw 'Provide either -SpecPath or -Spec, not both.' }
    if (-not $SpecPath -and -not $Spec) { throw 'Provide -SpecPath or -Spec.' }
    $json = if ($SpecPath) {
        if (-not (Test-Path -LiteralPath $SpecPath)) { throw "Spec file not found: $SpecPath" }
        Get-Content -LiteralPath $SpecPath -Raw
    } else { $Spec }
    return $json | ConvertFrom-Json
}

function Get-NormalizedFormula([string] $formula) {
    if ([string]::IsNullOrWhiteSpace($formula)) { throw 'Empty formula.' }
    if ($formula.StartsWith('=')) { return $formula }
    return "=$formula"
}

if (-not (Test-Path -LiteralPath $Path)) { throw "Workbook not found: $Path" }
$Path = (Resolve-Path -LiteralPath $Path).Path

# NOTE: do not name this $spec — PowerShell variables are case-insensitive and the [string] $Spec
# parameter would coerce the parsed object back to a string, silently nulling .namedRanges/.cells.
$editSpec = Resolve-Spec
$namedRanges = @($editSpec.namedRanges | Where-Object { $_ })
$cells = @($editSpec.cells | Where-Object { $_ })
if ($namedRanges.Count + $cells.Count -eq 0) {
    throw 'Spec contained no operations (no namedRanges and no cells). Nothing to do.'
}

# Mark-of-the-web can make Excel open read-only / prompt; clear it.
try { Unblock-File -LiteralPath $Path -ErrorAction SilentlyContinue } catch { }

$originalHash = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
Write-Output "Editing: $Path"
Write-Output "Original SHA256: $originalHash"
Write-Output "Operations: $($namedRanges.Count) named range(s), $($cells.Count) cell(s)"

if ($Backup) {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $bak = "$Path.bak-$stamp"
    Copy-Item -LiteralPath $Path -Destination $bak
    Write-Output "Backup written: $bak"
}

$ext = [System.IO.Path]::GetExtension($Path).ToLowerInvariant()
$saveFormat = if ($ext -eq '.xlsm') { $xlOpenXMLWorkbookMacroEnabled } else { $xlOpenXMLWorkbook }

$excel = $null
$wb = $null
try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    $excel.AskToUpdateLinks = $false
    $excel.ScreenUpdating = $false

    # Open(Filename, UpdateLinks=0, ReadOnly=$false)
    $wb = $excel.Workbooks.Open($Path, $doNotUpdateLinks, $false)
    if ($wb.ReadOnly) { throw "Workbook opened read-only; cannot edit: $Path" }

    # Calculation is an Application property that can only be set once a workbook is open.
    # Hold recalculation until all edits are applied, then do one full rebuild before saving.
    $excel.Calculation = $xlCalculationManual

    # --- Named ranges first (so formulas may reference them) ---
    foreach ($nr in $namedRanges) {
        $name = [string]$nr.name
        $refersTo = [string]$nr.refersTo
        if (-not $refersTo.StartsWith('=')) { $refersTo = "=$refersTo" }

        $existing = $null
        foreach ($n in $wb.Names) { if ($n.Name -eq $name) { $existing = $n; break } }
        if ($existing) {
            $existing.RefersTo = $refersTo
            Write-Output "  name (updated): $name -> $refersTo"
        } else {
            $wb.Names.Add($name, $refersTo) | Out-Null
            Write-Output "  name (added):   $name -> $refersTo"
        }
    }

    # --- Cell edits ---
    foreach ($c in $cells) {
        $ws = $wb.Worksheets.Item([string]$c.sheet)
        $range = $ws.Range([string]$c.cell)
        $hasFormula = $null -ne $c.PSObject.Properties['formula'] -and $null -ne $c.formula
        $hasValue   = $null -ne $c.PSObject.Properties['value']   -and $null -ne $c.value
        if ($hasFormula -and $hasValue) { throw "Cell $($c.sheet)!$($c.cell): specify formula OR value, not both." }
        if ($hasFormula) {
            $range.Formula = Get-NormalizedFormula ([string]$c.formula)
            Write-Output "  cell formula:   $($c.sheet)!$($c.cell) = $($range.Formula)"
        } elseif ($hasValue) {
            $range.Value2 = $c.value
            Write-Output "  cell value:     $($c.sheet)!$($c.cell) = $($c.value)"
        } else {
            throw "Cell $($c.sheet)!$($c.cell): neither formula nor value provided."
        }
    }

    # Recalculate natively so saved cached values are correct, then save in place.
    $excel.Calculation = $xlCalculationAutomatic
    $wb.ForceFullCalculation = $true
    $excel.CalculateFullRebuild()
    $wb.Save()
    $wb.Close($true)
    $wb = $null
    $excel.Quit()
    $excel = $null
}
finally {
    if ($wb)    { try { $wb.Close($false) | Out-Null } catch { }; [void][Runtime.InteropServices.Marshal]::ReleaseComObject($wb) }
    if ($excel) { try { $excel.Quit() } catch { }; [void][Runtime.InteropServices.Marshal]::ReleaseComObject($excel) }
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}

$newHash = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
Write-Output "New SHA256:      $newHash"
if ($newHash -eq $originalHash) { throw 'File hash did not change — no edit was persisted.' }

# --- Verify: reopen the SAVED file fresh and assert every edit actually landed ---
Write-Output '--- Verification (reopened from disk) ---'
$vExcel = $null
$vwb = $null
$failures = @()
try {
    $vExcel = New-Object -ComObject Excel.Application
    $vExcel.Visible = $false
    $vExcel.DisplayAlerts = $false
    $vExcel.AskToUpdateLinks = $false
    $vwb = $vExcel.Workbooks.Open($Path, $doNotUpdateLinks, $true)  # read-only

    foreach ($nr in $namedRanges) {
        $name = [string]$nr.name
        $found = $null
        foreach ($n in $vwb.Names) { if ($n.Name -eq $name) { $found = $n; break } }
        if ($found) {
            Write-Output "  name OK:   $name -> $($found.RefersTo)"
        } else {
            $failures += "named range '$name' missing after save"
        }
    }
    foreach ($c in $cells) {
        $ws = $vwb.Worksheets.Item([string]$c.sheet)
        $range = $ws.Range([string]$c.cell)
        $hasFormula = $null -ne $c.PSObject.Properties['formula'] -and $null -ne $c.formula
        if ($hasFormula) {
            if ($range.HasFormula) {
                Write-Output "  cell OK:   $($c.sheet)!$($c.cell) formula=[$($range.Formula)] value=[$($range.Value2)]"
            } else {
                $failures += "$($c.sheet)!$($c.cell) expected a formula but cell has none (value=[$($range.Value2)])"
            }
        } else {
            $expected = $c.value
            if ("$($range.Value2)" -eq "$expected") {
                Write-Output "  cell OK:   $($c.sheet)!$($c.cell) value=[$($range.Value2)]"
            } else {
                $failures += "$($c.sheet)!$($c.cell) expected value [$expected] but found [$($range.Value2)]"
            }
        }
    }
}
finally {
    if ($vwb)    { try { $vwb.Close($false) | Out-Null } catch { }; [void][Runtime.InteropServices.Marshal]::ReleaseComObject($vwb) }
    if ($vExcel) { try { $vExcel.Quit() } catch { }; [void][Runtime.InteropServices.Marshal]::ReleaseComObject($vExcel) }
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}

if ($failures.Count -gt 0) {
    throw ("Verification failed:`n" + ($failures -join "`n"))
}
Write-Output 'Verification passed.'
