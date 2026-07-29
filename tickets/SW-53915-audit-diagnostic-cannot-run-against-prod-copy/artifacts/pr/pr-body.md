## Ticket Link

[SW-53915](https://swyfft.myjetbrains.com/youtrack/issue/SW-53915) Homeowner and Commercial Excel audit diagnostic tests cannot run against prod-copy

## Reviewer Notes

These diagnostics get pointed at the prod-copy database to investigate audit-doc failures. #21419
added a third comparison — an in-RAM recompute — whose auth came from a test agent that only exists
where our test data has been loaded. Against prod-copy the diagnostic now gets through the Excel
re-rate and then dies at that recompute, so none of its three comparisons run.

The recompute now uses any agent already present in whatever database it's pointed at — the agent's
identity has no effect on the premium being compared.

This fix was originally written on `master`, where the code predates the shared base, and was used
there against prod-copy to diagnose [SW-52290](https://swyfft.myjetbrains.com/youtrack/issue/SW-52290) —
so it has already done the job it exists for. This PR ports it to the shape on `development`.

Also renames the three types to mirror the services they exercise:

| Before | After |
|---|---|
| `QuoteAuditDiagnosticTestBase` | `ExcelQuoteAuditDiagnosticTestBase` |
| `ByPerilQuoteAuditDiagnosticTests` | `HomeownerExcelQuoteAuditDiagnosticTests` |
| `CommercialQuoteAuditDiagnosticTests` | `CommercialExcelQuoteAuditDiagnosticTests` |

Verified against a purchased FL BSIC quote on a local database: the recompute completes and all three
totals agree. These are manual diagnostics — they skip without
`EXCEL_AUDIT_DIAGNOSTIC_TEST_QUOTE_IDS` and skip on TeamCity — so no CI impact.
