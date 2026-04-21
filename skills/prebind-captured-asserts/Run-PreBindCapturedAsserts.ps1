$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $HOME ".claude" "scripts" "Run-DotnetTest.ps1"

$env:UPDATE_TEST_EXPECTED_RESULTS = "true"
Write-Host "UPDATE_TEST_EXPECTED_RESULTS=true" -ForegroundColor Yellow

Write-Host "Building Swyfft.slnx..." -ForegroundColor Cyan
dotnet build Swyfft.slnx
if ($LASTEXITCODE -ne 0) { throw "Build failed with exit code $LASTEXITCODE" }

$projects = @(
    "Swyfft.Services.UnitTests",
    "Swyfft.Services.IntegrationTests",
    "Swyfft.Seeding.IntegrationTests"
)

Write-Host "Running PreBind Captured Assert Tests concurrently..." -ForegroundColor Cyan

$jobs = foreach ($proj in $projects) {
    Start-Job -ScriptBlock {
        param($script, $proj)
        $env:UPDATE_TEST_EXPECTED_RESULTS = "true"
        & $script -Project $proj -FilterTrait "TestGroup=PreBindResidentialCapturedAssertTests" -NoBuild
    } -ArgumentList $scriptPath, $proj
}

$failed = @()
foreach ($job in $jobs) {
    Receive-Job -Job $job -Wait
    if ($job.State -eq 'Failed') {
        $failed += $job.Name
    }
}

$jobs | Remove-Job -Force

$outputDir = Join-Path $env:TEMP 'swyfft-tests'
Write-Host ""
Write-Host "Output files in: $outputDir" -ForegroundColor Cyan

if ($failed.Count -gt 0) {
    throw "PreBind Captured Assert Tests failed for: $($failed -join ', ')"
}

Write-Host ""
Write-Host "All PreBind Captured Assert Tests passed." -ForegroundColor Green
