param(
    [Parameter(Mandatory = $true)]
    [string]$TicketFolder,
    [switch]$NoBuild,
    [switch]$ListTests,
    [ValidateSet('full', 'classes', 'methods', 'tests', 'traits')]
    [string]$ListLevel = 'methods'
)

$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $HOME ".claude" "scripts" "Run-DotnetTest.ps1"

$trait = "TestGroup=PreBindResidentialValidationTests"
$projects = @(
    "Swyfft.Services.UnitTests",
    "Swyfft.Services.IntegrationTests",
    "Swyfft.Seeding.IntegrationTests"
)

# --- List-tests mode (read-only): show exactly which tests this skill covers, no regeneration ---
# Use before listing tests in a plan's verification section so you don't double-list a test the
# skill already runs. Delegates to Run-DotnetTest.ps1 -ListTests (xUnit v3 native `-list`).
# Output is grouped and prefixed by project so it's clear which project each test comes from.
if ($ListTests) {
    $grandTotal = 0
    foreach ($proj in $projects) {
        Write-Host "==================== $proj ($trait) ====================" -ForegroundColor Cyan
        $raw = & $scriptPath -TicketFolder $TicketFolder -Project $proj -ListTests -ListLevel $ListLevel -FilterTrait $trait 2>&1
        # Keep only discovered test FQNs (they start with "Swyfft."); drop the runner/wrapper banner.
        $tests = @($raw | Where-Object { $_ -is [string] -and $_ -match '^Swyfft\.' })
        foreach ($t in $tests) { Write-Host "[$proj] $t" }
        Write-Host ("  -> {0} test(s) in {1}" -f $tests.Count, $proj) -ForegroundColor Green
        $grandTotal += $tests.Count
        Write-Host ""
    }
    Write-Host ("TOTAL: {0} PreBind test(s) across {1} project(s)" -f $grandTotal, $projects.Count) `
        -ForegroundColor Green
    return
}

$env:UPDATE_TEST_EXPECTED_RESULTS = "true"
Write-Host "UPDATE_TEST_EXPECTED_RESULTS=true" -ForegroundColor Yellow

if ($NoBuild) {
    Write-Host "Skipping build (-NoBuild)" -ForegroundColor Yellow
} else {
    $buildScript = Join-Path $HOME ".claude" "scripts" "Build-Solution.ps1"
    & $buildScript
    if ($LASTEXITCODE -ne 0) { throw "Build failed" }
}

Write-Host "Running PreBind Validation Tests concurrently..." -ForegroundColor Cyan

$jobs = foreach ($proj in $projects) {
    Start-Job -Name $proj -ScriptBlock {
        param($script, $proj, $trait, $ticketFolder)
        $env:UPDATE_TEST_EXPECTED_RESULTS = "true"
        & $script -TicketFolder $ticketFolder -Project $proj -FilterTrait $trait -NoBuild
        # Run-DotnetTest returns the runner exit code without throwing; treat any non-zero as failure.
        # Exit 8 = "Zero tests ran" (the trait filter matched nothing — e.g. a renamed trait whose
        # retag isn't on this branch), which must fail loudly instead of reporting a false green over
        # a suite that never executed.
        if ($LASTEXITCODE -ne 0) {
            $reason = if ($LASTEXITCODE -eq 8) { "zero tests matched trait '$trait'" } else { "test failures" }
            throw "$proj : Run-DotnetTest exited $LASTEXITCODE ($reason)."
        }
    } -ArgumentList $scriptPath, $proj, $trait, $TicketFolder
}

$failed = @()
foreach ($job in $jobs) {
    Receive-Job -Job $job -Wait -ErrorAction SilentlyContinue
    if ($job.State -eq 'Failed') {
        $failed += $job.Name
    }
}

$jobs | Remove-Job -Force

$outputDir = Join-Path $HOME ".claude/tickets/$TicketFolder/artifacts/tests"
Write-Host ""
Write-Host "Output files in: $outputDir" -ForegroundColor Cyan

if ($failed.Count -gt 0) {
    throw "PreBind Validation Tests failed for: $($failed -join ', ')"
}

Write-Host ""
Write-Host "All PreBind Validation Tests passed." -ForegroundColor Green
