<#
.SYNOPSIS
    Audit the quote-def overrides: list the ones whose configs have already gone live in prod.

.DESCRIPTION
    Runs QuoteDefinitionsUnitTests.ReportOverridesForLiveConfigs
    (Swyfft.Services.UnitTests). It compares every Homeowner / Flood / DBB quote-def override
    against QuoteDefinitions.txt and reports three buckets: STALE (config already live → removal
    candidate), KEEP (not yet live), and KEEP (no prod row → override is the only activation).

    Pure unit test over static files — no DB, no appsettings changes, no prod-db concern.
    Report-only: it never edits Seeder.cs / EnvironmentFilters.

.PARAMETER NoBuild
    Skip the incremental build (pass when the solution is already built).

.EXAMPLE
    Run-QuoteDefOverrideAudit.ps1
#>
[CmdletBinding()]
param(
    [switch]$NoBuild
)

$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $HOME ".claude" "scripts" "Run-DotnetTest.ps1"

# Gate the otherwise-skipped diagnostic test on. Absent this var, normal/CI runs skip it.
$env:QUOTE_DEF_OVERRIDE_AUDIT = 'true'

$testArgs = @{
    Project      = 'Swyfft.Services.UnitTests'
    FilterMethod = '*ReportOverridesForLiveConfigs'
}
if ($NoBuild) { $testArgs.NoBuild = $true }

& $scriptPath @testArgs
