<#
.SYNOPSIS
    Parse ByPeril Homeowner audit mismatch logs from SolarWinds into a structured table.

.DESCRIPTION
    Reads a SolarWinds log dump (typically produced by Search-SolarWinds.ps1) containing
    ByPerilHomeownerExcelQuoteAuditService audit mismatch errors, extracts the unique
    quote GUIDs, and emits a deduplicated table with policy number, quote definition,
    purchase date, and DB vs Excel totals.

    Pattern matched (one per log line):
        Quote <guid> (IMS policy <policy>, QuoteDef: <type> (<id> / <name>),
        PriorQuoteDef: <prior>, <address>, purchased on <date>):
        The DB quote premium $<X> and fees $<Y> did not match the Excel premium and fees $<Z>

.PARAMETER LogFile
    Path to the SolarWinds log dump to parse. Mandatory.

.PARAMETER SortBy
    Column to sort output by. Valid: Id, Policy, QuoteDef, Purchased, DbPrem, Excel.
    Default: Purchased.

.PARAMETER AsObject
    Emit PSCustomObject records instead of a formatted table. Useful for piping to
    ConvertTo-Csv, Export-Csv, ForEach-Object, etc.

.EXAMPLE
    .\Parse-AuditLogs.ps1 -LogFile "$env:TEMP\swyfft-logs\solarwinds-search.txt"

.EXAMPLE
    # Pipe to CSV
    .\Parse-AuditLogs.ps1 -LogFile "path\to\log.txt" -AsObject |
        Export-Csv audit.csv -NoTypeInformation

.EXAMPLE
    # Pull just the GUIDs, comma-separated (handy for EXCEL_AUDIT_DIAGNOSTIC_TEST_QUOTE_IDS)
    (.\Parse-AuditLogs.ps1 -LogFile "path\to\log.txt" -AsObject | Select-Object -ExpandProperty Id) -join ','
#>
param(
    [Parameter(Mandatory)]
    [string]$LogFile,

    [ValidateSet('Id', 'Policy', 'QuoteDef', 'Purchased', 'DbPrem', 'Excel')]
    [string]$SortBy = 'Purchased',

    [switch]$AsObject
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $LogFile)) {
    Write-Error "Log file not found: $LogFile"
    exit 1
}

$pattern = 'Quote ([a-f0-9-]{36}) \(IMS policy ([\w-]+), QuoteDef: \w+ \((\d+) / ([\w.]+)\), PriorQuoteDef: ([\w.]+), (.+?), purchased on ([\d/]+)\): The DB quote premium \$([\d,]+) and fees \$([\d,]+) did not match the Excel premium and fees \$([\d,]+)'

$seen = @{}
Get-Content $LogFile | ForEach-Object {
    $m = [regex]::Match($_, $pattern)
    if ($m.Success) {
        $id = $m.Groups[1].Value
        if (-not $seen.ContainsKey($id)) {
            $seen[$id] = [PSCustomObject]@{
                Id         = $id
                Policy     = $m.Groups[2].Value
                QuoteDefId = $m.Groups[3].Value
                QuoteDef   = $m.Groups[4].Value
                Prior      = $m.Groups[5].Value
                Address    = $m.Groups[6].Value
                Purchased  = $m.Groups[7].Value
                DbPrem     = $m.Groups[8].Value
                DbFees     = $m.Groups[9].Value
                Excel      = $m.Groups[10].Value
            }
        }
    }
}

$results = @($seen.Values | Sort-Object $SortBy)

if ($AsObject) {
    $results
} else {
    Write-Host ("Parsed: {0} unique quotes" -f $seen.Count) -ForegroundColor Cyan
    Write-Host ""
    $results | Format-Table -AutoSize Purchased, QuoteDefId, QuoteDef, Policy, Id, DbPrem, DbFees, Excel
}
