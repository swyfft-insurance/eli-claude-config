param(
    [string]$Solution = "Swyfft.slnx",
    [switch]$NoBuild,
    [switch]$ErrorsOnly
)

$ErrorActionPreference = "Continue"

$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) {
    Write-Error "Not in a git repository"
    exit 1
}

Push-Location $repoRoot
try {
    $solutionPath = Join-Path $repoRoot $Solution
    if (-not (Test-Path $solutionPath)) {
        Write-Error "Solution not found: $solutionPath"
        exit 1
    }

    Write-Host "Building $Solution..." -ForegroundColor Cyan

    $output = dotnet build $solutionPath 2>&1 | Out-String
    $buildExitCode = $LASTEXITCODE

    # Match ALL error types: CS, IDE, SWYF, or any other ": error " pattern
    $errorLines = $output -split "`n" | Where-Object { $_ -match ": error " }

    if ($buildExitCode -ne 0 -or $errorLines.Count -gt 0) {
        if ($errorLines.Count -gt 0) {
            Write-Host "`nBuild FAILED with $($errorLines.Count) error(s):`n" -ForegroundColor Red
            $errorLines | ForEach-Object { Write-Host $_.Trim() -ForegroundColor Red }
        }
        else {
            Write-Host "`nBuild FAILED with exit code $buildExitCode (no error lines captured)." -ForegroundColor Red
        }
        exit 1
    }
    else {
        if (-not $ErrorsOnly) {
            Write-Host "`nBuild succeeded — 0 errors." -ForegroundColor Green
        }
        exit 0
    }
}
finally {
    Pop-Location
}
