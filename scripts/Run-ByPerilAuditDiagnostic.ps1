<#
.SYNOPSIS
    Run the ByPeril Homeowner Excel audit diagnostic test against one or more quote IDs.

.DESCRIPTION
    Loads each quote from the DB (per current Swyfft.Common/appsettings.json), runs the
    Excel rater, and compares AnnualPremium + AnnualFeesTotal against FinalTotalPremium —
    same comparison as the production ByPerilHomeownerExcelQuoteAuditService.

    Prerequisites (the byperil-audit-diagnostic skill checks these):
    - Swyfft.Common/appsettings.json pointed at beta, dev, or prod-copy (not localhost, not prod)

.PARAMETER QuoteIds
    Comma-, semicolon-, or whitespace-separated list of quote GUIDs.

.EXAMPLE
    Run-ByPerilAuditDiagnostic.ps1 -QuoteIds "f820d3a8-7290-495e-bbf1-ab22d5a8d2a8,2fbb65e4-22e2-443a-815d-56cdb7c39577"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$QuoteIds
)

$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $HOME ".claude" "scripts" "Run-DotnetTest.ps1"

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

Write-Host "Running $($ids.Count) quote(s) through ByPerilQuoteAuditDiagnosticTests"
Write-Host ""

$env:EXCEL_AUDIT_DIAGNOSTIC_TEST_QUOTE_IDS = ($ids -join ',')
$env:GITHUB_ACTIONS = 'true'

& $scriptPath `
    -Project 'Swyfft.Services.Excel.IntegrationTests' `
    -FilterClass '*ByPerilQuoteAuditDiagnosticTests' `
    -Suffix "$($ids.Count)-quotes"
