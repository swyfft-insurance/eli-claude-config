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
    A .csproj project path (passed to dotnet test --project). Mutually exclusive with -Solution.

.PARAMETER Solution
    A .slnx solution file (passed to dotnet test --solution). Mutually exclusive with -Project.

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
    Run-DotnetTest.ps1 -Solution "SwyfftCI.slnx" -NoBuild

.EXAMPLE
    Run-DotnetTest.ps1 -Project "Swyfft.Services.UnitTests" -FilterTrait "TestGroup=PreBindResidentialValidationTests" -NoBuild

.EXAMPLE
    Run-DotnetTest.ps1 -Project "Swyfft.Services.Excel.IntegrationTests" -FilterClass "*ByPerilQuoteAuditDiagnosticTests" -Suffix "3-quotes"
#>
[CmdletBinding()]
param(
    [string]$Project,
    [string]$Solution,

    [string]$FilterTrait,
    [string]$FilterClass,
    [string]$FilterMethod,
    [string]$FilterNamespace,

    [switch]$NoBuild,

    [string]$Suffix,

    [switch]$ListTests,

    [ValidateSet('full', 'classes', 'methods', 'tests', 'traits')]
    [string]$ListLevel = 'full'
)

$ErrorActionPreference = 'Stop'

# --- Validate params ---
if ($Project -and $Solution) {
    throw "-Project and -Solution are mutually exclusive. Pass one or the other."
}
if (-not $Project -and -not $Solution) {
    throw "You must pass either -Project or -Solution."
}
if ($Project -and $Project -match '\.slnx?$') {
    throw "-Project received a solution file ('$Project'). Use -Solution instead."
}
if ($Solution -and $Solution -notmatch '\.slnx?$') {
    throw "-Solution received a non-solution file ('$Solution'). Use -Project instead."
}

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

# Resolve target
$target = if ($Solution) { $Solution } else { $Project }

# Project/solution name (strip path and extension, keep dots)
$projectName = ($target -replace '[\\/]', '/' -split '/')[-1] -replace '\.(csproj|slnx?)$', ''

# --- List-tests mode (read-only): enumerate tests instead of running them ---
# Listing goes through `dotnet run` (the xUnit v3 NATIVE runner CLI) — `dotnet test` is the MTP
# integration and has no list capability. `dotnet run` locates the built assembly itself, so no
# exe-path / output-dir guessing. The native runner uses `-list <level>` and single-dash filters
# `-trait`/`-class`/`-method`/`-namespace` — NOT the MTP `--filter-*` flags used when running.
if ($ListTests) {
    if ($Solution) { throw "-ListTests requires -Project, not -Solution." }

    $runArgs = @('run', '--project', $Project)
    if ($NoBuild) { $runArgs += '--no-build' }
    $runArgs += '--'
    $runArgs += @('-list', $ListLevel)
    if ($FilterTrait)     { $runArgs += '-trait';     $runArgs += $FilterTrait }
    if ($FilterClass)     { $runArgs += '-class';     $runArgs += $FilterClass }
    if ($FilterMethod)    { $runArgs += '-method';    $runArgs += $FilterMethod }
    if ($FilterNamespace) { $runArgs += '-namespace'; $runArgs += $FilterNamespace }

    Write-Host "Listing tests: $projectName  (level: $ListLevel)" -ForegroundColor Cyan
    Write-Host "Command: dotnet $($runArgs -join ' ')" -ForegroundColor Cyan
    Write-Host ""
    & dotnet @runArgs
    exit $LASTEXITCODE
}

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
if ($Solution) {
    $testArgs = @('test', '--solution', $Solution)
} else {
    $testArgs = @('test', '--project', $Project)
}
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

# A run that matched no tests must never look like success. MTP returns exit code 8 for "Zero tests
# ran" — almost always a stale or renamed filter (trait/class/method/namespace) that matches nothing
# on this branch. Fail loudly with a non-zero code so no caller can mistake a no-op for a green suite.
if ($exitCode -eq 8 -or (Select-String -Path $outputFile -Pattern 'Zero tests ran' -Quiet)) {
    Write-Host ""
    Write-Host "FAILED: Zero tests ran - filter matched no tests ($filterStr)." -ForegroundColor Red
    if ($exitCode -eq 0) { $exitCode = 8 }
}

exit $exitCode
