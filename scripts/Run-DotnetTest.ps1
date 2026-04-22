<#
.SYNOPSIS
    Standard wrapper for dotnet test with deterministic output file naming.

.DESCRIPTION
    Runs dotnet test with standardized flags (Tee-Object, --output Detailed, --report-trx)
    and deterministic output filenames based on branch, project, filters, and timestamp.

    Output format: {branch}_{project}_{filters}_{timestamp}.txt
    Example: feature-ek-20260421_SW-49862_consolidate_Swyfft.Services.Excel.IntegrationTests_filter-trait-TestGroup=ByPerilTests_20260421-1430.txt

    The pretooluse hook blocks raw dotnet test commands. All test execution
    must go through this script.

.PARAMETER Project
    The dotnet test project path or name (passed to --project).

.PARAMETER FilterTrait
    Trait filter (e.g., "TestGroup=ByPerilTests"). Passed as --filter-trait.

.PARAMETER FilterClass
    Class filter (e.g., "*TopaFL*"). Passed as --filter-class.

.PARAMETER FilterMethod
    Method filter. Passed as --filter-method.

.PARAMETER FilterNamespace
    Namespace filter. Passed as --filter-namespace.

.PARAMETER NoBuild
    Skip building before testing (--no-build).

.PARAMETER Suffix
    Optional suffix appended before the timestamp (e.g., "3-quotes").

.EXAMPLE
    Run-DotnetTest.ps1 -Project "Swyfft.Services.Excel.IntegrationTests" -FilterTrait "TestGroup=ByPerilTests"

.EXAMPLE
    Run-DotnetTest.ps1 -Project "Swyfft.Services.UnitTests" -FilterTrait "TestGroup=PreBindResidentialCapturedAssertTests" -NoBuild

.EXAMPLE
    Run-DotnetTest.ps1 -Project "Swyfft.Services.Excel.IntegrationTests" -FilterClass "*ByPerilQuoteAuditDiagnosticTests" -Suffix "3-quotes"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Project,

    [string]$FilterTrait,
    [string]$FilterClass,
    [string]$FilterMethod,
    [string]$FilterNamespace,

    [switch]$NoBuild,

    [string]$Suffix
)

$ErrorActionPreference = 'Stop'

# --- Output directory ---
$outputDir = Join-Path $env:TEMP 'swyfft-tests'
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# --- Deterministic filename ---

# Branch (replace / with -)
$branch = git branch --show-current 2>$null
if (-not $branch) { $branch = 'detached' }
$branch = $branch -replace '/', '-'

# Project name (strip path and .csproj extension, keep dots)
$projectName = ($Project -replace '[\\/]', '/' -split '/')[-1] -replace '\.csproj$', ''

# Filters (strip wildcards — invalid in filenames)
$filterParts = @()
if ($FilterTrait)     { $filterParts += "filter-trait-$FilterTrait" }
if ($FilterClass)     { $filterParts += "filter-class-$($FilterClass -replace '\*', '')" }
if ($FilterMethod)    { $filterParts += "filter-method-$($FilterMethod -replace '\*', '')" }
if ($FilterNamespace) { $filterParts += "filter-namespace-$($FilterNamespace -replace '\*', '')" }
$filterStr = if ($filterParts.Count -gt 0) { $filterParts -join '_' } else { 'no-filter' }

# Suffix (optional)
$suffixStr = if ($Suffix) { "_$Suffix" } else { '' }

# Timestamp
$timestamp = Get-Date -Format 'yyyyMMdd-HHmm'

$baseName = "${branch}_${projectName}_${filterStr}${suffixStr}_${timestamp}"
$outputFile = Join-Path $outputDir "$baseName.txt"
$trxName = "$baseName.trx"

# --- Build dotnet test args ---
$testArgs = @('test', '--project', $Project)
if ($NoBuild) { $testArgs += '--no-build' }
$testArgs += '--'

if ($FilterTrait)     { $testArgs += '--filter-trait';     $testArgs += $FilterTrait }
if ($FilterClass)     { $testArgs += '--filter-class';     $testArgs += $FilterClass }
if ($FilterMethod)    { $testArgs += '--filter-method';    $testArgs += $FilterMethod }
if ($FilterNamespace) { $testArgs += '--filter-namespace'; $testArgs += $FilterNamespace }

$testArgs += '--output';              $testArgs += 'Detailed'
$testArgs += '--report-trx'
$testArgs += '--report-trx-filename'; $testArgs += $trxName

# --- Run ---
Write-Host "Branch:  $branch" -ForegroundColor Cyan
Write-Host "Project: $projectName" -ForegroundColor Cyan
Write-Host "Filters: $filterStr" -ForegroundColor Cyan
Write-Host "Output:  $outputFile" -ForegroundColor Cyan
Write-Host "TRX:     $trxName" -ForegroundColor Cyan
Write-Host ""

& dotnet @testArgs 2>&1 | Tee-Object -FilePath $outputFile

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "Output: $outputFile" -ForegroundColor Green
Write-Host "TRX:    $trxName" -ForegroundColor Green

exit $exitCode
