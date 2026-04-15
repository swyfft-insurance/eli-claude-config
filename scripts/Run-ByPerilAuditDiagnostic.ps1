<#
.SYNOPSIS
    Run the ByPeril Homeowner Excel audit diagnostic test against one or more quote IDs.

.DESCRIPTION
    Loads each quote from the DB (per current Swyfft.Common/appsettings.json), runs the
    Excel rater, and compares AnnualPremium + AnnualFeesTotal against FinalTotalPremium —
    same comparison as the production ByPerilHomeownerExcelQuoteAuditService.

    Prerequisites (the byperil-audit-diagnostic skill checks these):
    - Swyfft.Common/appsettings.json pointed at beta, dev, or prod-copy (not localhost, not prod)
    - [Trait(TestGroup, ByPerilTests)] attribute present on ByPerilQuoteAuditDiagnosticTests
      (temporary until PR #19915 merges)

.PARAMETER QuoteIds
    Comma-, semicolon-, or whitespace-separated list of quote GUIDs.

.PARAMETER OutputName
    Optional. Base name for the tee'd output file and TRX report.
    Defaults to "ByPerilQuoteAuditDiagnosticTests-<count>-quotes".

.EXAMPLE
    Run-ByPerilAuditDiagnostic.ps1 -QuoteIds "f820d3a8-7290-495e-bbf1-ab22d5a8d2a8,2fbb65e4-22e2-443a-815d-56cdb7c39577"

.EXAMPLE
    Run-ByPerilAuditDiagnostic.ps1 -QuoteIds (Get-Content quotes.txt -Raw) -OutputName "investigation-run-1"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$QuoteIds,

    [Parameter(Mandatory = $false)]
    [string]$OutputName
)

$ErrorActionPreference = 'Stop'

# Normalize: split on comma/semicolon/whitespace, trim, dedupe
$ids = $QuoteIds -split '[,;\s]+' |
    Where-Object { $_ } |
    ForEach-Object { $_.Trim() } |
    Select-Object -Unique

if ($ids.Count -eq 0) {
    throw "No quote IDs provided."
}

$guidPattern = '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
$badIds = $ids | Where-Object { $_ -notmatch $guidPattern }
if ($badIds) {
    throw "Invalid quote ID format: $($badIds -join ', ')"
}

if (-not $OutputName) {
    $OutputName = "ByPerilQuoteAuditDiagnosticTests-$($ids.Count)-quotes"
}

$outputDir = Join-Path $env:TEMP 'swyfft-tests'
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

$outputFile = Join-Path $outputDir "$OutputName.txt"
$trxName = "$OutputName.trx"

Write-Host "Running $($ids.Count) quote(s) through ByPerilQuoteAuditDiagnosticTests"
Write-Host "Output:  $outputFile"
Write-Host "TRX:     build/Debug/net10.0/TestResults/$trxName"
Write-Host ""

$env:EXCEL_AUDIT_DIAGNOSTIC_TEST_QUOTE_IDS = ($ids -join ',')
$env:GITHUB_ACTIONS = 'true'

$testArgs = @(
    '--project', 'Swyfft.Services.Excel.IntegrationTests'
    '--'
    '--filter-class', '*ByPerilQuoteAuditDiagnosticTests'
    '--filter-trait', 'TestGroup=ByPerilTests'
    '--report-trx'
    '--report-trx-filename', $trxName
    '--output', 'Detailed'
)

dotnet test @testArgs 2>&1 | Tee-Object -FilePath $outputFile

Write-Host ""
Write-Host "Done. Output: $outputFile"
