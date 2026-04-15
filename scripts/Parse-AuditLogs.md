# Parse-AuditLogs.ps1

Parses `ByPerilHomeownerExcelQuoteAuditService` audit-mismatch logs from SolarWinds into a structured table.

## When to use

When investigating production audit mismatches — any ticket with the signature `ByPerilHomeownerExcelQuoteAuditService | GenerateAuditDocs - GenerateAuditDoc` — this script turns a raw SolarWinds log dump into a deduplicated list of affected quotes.

Pairs with `Search-SolarWinds.ps1`:
1. `Search-SolarWinds.ps1` → dumps raw logs to `$env:TEMP\swyfft-logs\`
2. `Parse-AuditLogs.ps1` → extracts the unique quote GUIDs + metadata for the ByPerilQuoteAuditDiagnosticTests env var

## Parameters

| Param | Required | Default | Description |
|---|---|---|---|
| `-LogFile` | yes | — | Path to the SolarWinds log dump |
| `-SortBy` | no | `Purchased` | Sort column: `Id`, `Policy`, `QuoteDef`, `Purchased`, `DbPrem`, `Excel` |
| `-AsObject` | no | off | Emit `PSCustomObject[]` for piping, instead of a formatted table |

## Usage

### Display a table

```powershell
pwsh -NoProfile -File "$HOME\.claude\scripts\Parse-AuditLogs.ps1" -LogFile "$env:TEMP\swyfft-logs\solarwinds-search.txt"
```

Output columns: `Purchased | QuoteDefId | QuoteDef | Policy | Id | DbPrem | DbFees | Excel`.

### Get the comma-separated GUID list

Feed straight into `EXCEL_AUDIT_DIAGNOSTIC_TEST_QUOTE_IDS`:

```powershell
$guids = (& "$HOME\.claude\scripts\Parse-AuditLogs.ps1" `
    -LogFile "path\to\log.txt" -AsObject |
    Select-Object -ExpandProperty Id) -join ','
$env:EXCEL_AUDIT_DIAGNOSTIC_TEST_QUOTE_IDS = $guids
```

### Export to CSV

```powershell
& "$HOME\.claude\scripts\Parse-AuditLogs.ps1" -LogFile "path\to\log.txt" -AsObject |
    Export-Csv audit.csv -NoTypeInformation
```

### Sort by Excel delta

```powershell
& "$HOME\.claude\scripts\Parse-AuditLogs.ps1" -LogFile "path\to\log.txt" -SortBy Excel
```

## Pattern

The script matches this exact log line shape (one per failing quote, per audit run):

```
Quote <guid> (IMS policy <policy>, QuoteDef: <type> (<id> / <name>),
PriorQuoteDef: <prior>, <address>, purchased on <date>):
The DB quote premium $<X> and fees $<Y> did not match the Excel premium and fees $<Z>
```

Captured fields:

| Column | Source |
|---|---|
| `Id` | Quote GUID |
| `Policy` | IMS policy number |
| `QuoteDefId` | Numeric QuoteDefinitionId |
| `QuoteDef` | HomeownerStateConfig code (e.g., `TX.QBE.ByPeril.EAndS.V5`) |
| `Prior` | Prior QuoteDef (usually `none` for new business) |
| `Address` | Risk address |
| `Purchased` | Purchase date |
| `DbPrem` | `EFHomeownerQuote.AnnualPremium` (what we charged) |
| `DbFees` | `EFHomeownerQuote.AnnualFeesTotal` |
| `Excel` | What the Excel rater re-computed on audit |

## Limitations

- Hard-coded to the ByPeril Homeowner audit mismatch log format. Other audit services (commercial, flood) have different signatures and will need their own parser.
- Dedup key is `Id`: if the same quote appears in multiple log entries (nightly re-audits), only the first instance is kept.
- Dollar amounts are captured as formatted strings (e.g. `"5,558"`) — cast to int/decimal yourself if you need numeric math.

## Related

- `~/.claude/scripts/Search-SolarWinds.ps1` — produces the input log
- `~/.claude/rules/solarwinds.md` — SolarWinds search rules and the `/search-logs` skill
- `Swyfft.Services.Excel.IntegrationTests/Homeowner/ByPerilQuoteAuditDiagnosticTests.cs` — the diagnostic test that consumes `EXCEL_AUDIT_DIAGNOSTIC_TEST_QUOTE_IDS`
