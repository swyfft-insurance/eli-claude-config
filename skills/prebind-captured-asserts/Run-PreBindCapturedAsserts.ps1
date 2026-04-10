$ErrorActionPreference = 'Stop'

$outputDir = Join-Path $env:TEMP "swyfft-tests"
if (-not (Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir -Force | Out-Null }

$env:UPDATE_TEST_EXPECTED_RESULTS = "true"
Write-Host "UPDATE_TEST_EXPECTED_RESULTS=true" -ForegroundColor Yellow

Write-Host "Building Swyfft.slnx..." -ForegroundColor Cyan
dotnet build Swyfft.slnx
if ($LASTEXITCODE -ne 0) { throw "Build failed with exit code $LASTEXITCODE" }

$projects = @(
    @{ Name = "Swyfft.Services.UnitTests"; Short = "services-unit-prebind" },
    @{ Name = "Swyfft.Services.IntegrationTests"; Short = "services-integration-prebind" },
    @{ Name = "Swyfft.Seeding.IntegrationTests"; Short = "seeding-integration-prebind" }
)

Write-Host "Running PreBind Captured Assert Tests concurrently..." -ForegroundColor Cyan

$jobs = foreach ($project in $projects) {
    $proj = $project.Name
    $short = $project.Short
    $outFile = Join-Path $outputDir "$short.txt"
    $trxName = "$short.trx"
    Start-Job -ScriptBlock {
        param($proj, $outFile, $trxName)
        $env:UPDATE_TEST_EXPECTED_RESULTS = "true"
        dotnet test --no-build --project $proj -- --filter-trait "TestGroup=PreBindResidentialCapturedAssertTests" --output Detailed --report-trx --report-trx-filename $trxName 2>&1 |
            Tee-Object -FilePath $outFile
        return $LASTEXITCODE
    } -ArgumentList $proj, $outFile, $trxName
}

$failed = @()
foreach ($job in $jobs) {
    $result = Receive-Job -Job $job -Wait
    if ($job.State -eq 'Failed') {
        $failed += $job.Name
    }
}

$jobs | Remove-Job -Force

Write-Host ""
Write-Host "Output files:" -ForegroundColor Cyan
foreach ($project in $projects) {
    $outFile = Join-Path $outputDir "$($project.Short).txt"
    Write-Host "  $outFile"
}

if ($failed.Count -gt 0) {
    throw "PreBind Captured Assert Tests failed for: $($failed -join ', ')"
}

Write-Host ""
Write-Host "All PreBind Captured Assert Tests passed." -ForegroundColor Green
