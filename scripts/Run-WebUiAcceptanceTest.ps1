<#
.SYNOPSIS
    Deterministically run UI acceptance tests from swyfft_web on the local machine.

.DESCRIPTION
    Single-script orchestration of the website lifecycle for UI acceptance tests:
      1. Kill site (Swyfft.Web, bun)
      2. Build solution (Build-Solution.ps1)
      3. Start site (RunSwyfftWeb.ps1, background job)
      4. Wait for health (poll HealthUrl, HealthTimeoutSec)
      5. Run tests (Run-DotnetTest.ps1 with -NoBuild + filter args)
      6. List failure screenshots if tests failed
      7. Kill site - ALWAYS, in finally block

    Returns the test exit code (0 = pass, non-zero = fail or infrastructure error).

    REFUSES to run without at least one filter arg - the full UI suite is hours.

    Run from the swyfft_web repo root.

.PARAMETER FilterMethod
    Method-name wildcard filter (e.g., "*RoofGeometry*").

.PARAMETER FilterClass
    Class-name wildcard filter (e.g., "*ValidateUiFlowTestsChrome").

.PARAMETER FilterTrait
    Trait filter (e.g., "TestGroup=Critical").

.PARAMETER FilterNamespace
    Namespace filter (e.g., "Swyfft.Web.Ui.AcceptanceTests.Homeowner").

.PARAMETER HealthTimeoutSec
    How long to wait for the website to become healthy. Default 120.

.PARAMETER HealthUrl
    URL polled for health. Default https://localhost:5001.

.EXAMPLE
    pwsh -NoProfile -File ~/.claude/scripts/Run-WebUiAcceptanceTest.ps1 -FilterMethod "*RoofGeometry*"
#>
param(
    [string]$FilterMethod,
    [string]$FilterClass,
    [string]$FilterTrait,
    [string]$FilterNamespace,
    [int]$HealthTimeoutSec = 60,
    [string]$HealthUrl = "https://localhost:5001"
)

$ErrorActionPreference = "Stop"

# --- Validate filter ---
$hasFilter = $FilterMethod -or $FilterClass -or $FilterTrait -or $FilterNamespace
if (-not $hasFilter) {
    Write-Host "ERROR: At least one filter arg is required (-FilterMethod, -FilterClass, -FilterTrait, -FilterNamespace)." -ForegroundColor Red
    Write-Host "The full UI suite is hours. Aborting." -ForegroundColor Red
    exit 2
}

# --- Locate repo files ---
$repoRoot = (Get-Location).Path
$runWebPath = Join-Path $repoRoot "RunSwyfftWeb.ps1"
$testProj = Join-Path $repoRoot "Swyfft.Web.Ui.AcceptanceTests/Swyfft.Web.Ui.AcceptanceTests.csproj"

if (-not (Test-Path $runWebPath)) {
    Write-Host "ERROR: RunSwyfftWeb.ps1 not found at $runWebPath" -ForegroundColor Red
    Write-Host "Run this script from the swyfft_web repo root." -ForegroundColor Red
    exit 2
}
if (-not (Test-Path $testProj)) {
    Write-Host "ERROR: Test project not found at $testProj" -ForegroundColor Red
    exit 2
}

$buildScript = Join-Path $HOME ".claude/scripts/Build-Solution.ps1"
$runDotnetTest = Join-Path $HOME ".claude/scripts/Run-DotnetTest.ps1"

if (-not (Test-Path $buildScript)) {
    Write-Host "ERROR: Build-Solution.ps1 not found at $buildScript" -ForegroundColor Red
    exit 2
}
if (-not (Test-Path $runDotnetTest)) {
    Write-Host "ERROR: Run-DotnetTest.ps1 not found at $runDotnetTest" -ForegroundColor Red
    exit 2
}

# --- Helper: kill site ---
function Stop-Site {
    Write-Host "Stopping Swyfft.Web and bun processes..." -ForegroundColor Yellow
    Stop-Process -Name Swyfft.Web -ErrorAction SilentlyContinue
    Stop-Process -Name bun -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
}

$webJob = $null
$testExitCode = 1

try {
    # --- Step 1: Kill site ---
    Write-Host "`n=== Step 1: Kill website ===" -ForegroundColor Cyan
    Stop-Site

    # --- Step 2: Build ---
    Write-Host "`n=== Step 2: Build Swyfft.slnx ===" -ForegroundColor Cyan
    & pwsh -NoProfile -File $buildScript -Solution "Swyfft.slnx"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Build failed with exit code $LASTEXITCODE. Aborting." -ForegroundColor Red
        exit $LASTEXITCODE
    }

    # --- Step 3: Start site (background) ---
    Write-Host "`n=== Step 3: Start website (background) ===" -ForegroundColor Cyan
    $webJob = Start-Job -ScriptBlock {
        param($repo, $script)
        Set-Location $repo
        & pwsh -NoProfile -File $script
    } -ArgumentList $repoRoot, $runWebPath
    Write-Host "Started web job: Id=$($webJob.Id)" -ForegroundColor Green

    # --- Step 4: Wait for health ---
    Write-Host "`n=== Step 4: Wait for health (up to ${HealthTimeoutSec}s, $HealthUrl) ===" -ForegroundColor Cyan
    $healthy = $false
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    while ($stopwatch.Elapsed.TotalSeconds -lt $HealthTimeoutSec) {
        try {
            $resp = Invoke-WebRequest -Uri $HealthUrl -SkipCertificateCheck -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            if ($resp.StatusCode -eq 200) {
                $healthy = $true
                Write-Host "Website healthy at $HealthUrl ($([int]$stopwatch.Elapsed.TotalSeconds)s)" -ForegroundColor Green
                break
            }
        } catch {
            # Not ready yet
        }
        Start-Sleep -Seconds 5
    }

    if (-not $healthy) {
        Write-Host "ERROR: Website did not become healthy within ${HealthTimeoutSec}s." -ForegroundColor Red
        Write-Host "--- Web job output ---" -ForegroundColor Yellow
        Receive-Job -Job $webJob -Keep | Out-Host
        exit 3
    }

    # --- Step 5: Run test ---
    Write-Host "`n=== Step 5: Run test ===" -ForegroundColor Cyan
    $testArgs = @("-Project", $testProj, "-NoBuild")
    if ($FilterMethod)    { $testArgs += @("-FilterMethod", $FilterMethod) }
    if ($FilterClass)     { $testArgs += @("-FilterClass", $FilterClass) }
    if ($FilterTrait)     { $testArgs += @("-FilterTrait", $FilterTrait) }
    if ($FilterNamespace) { $testArgs += @("-FilterNamespace", $FilterNamespace) }

    & pwsh -NoProfile -File $runDotnetTest @testArgs
    $testExitCode = $LASTEXITCODE
    $color = if ($testExitCode -eq 0) { "Green" } else { "Red" }
    Write-Host "Test exit code: $testExitCode" -ForegroundColor $color

    # --- Step 6: Screenshots if failed ---
    if ($testExitCode -ne 0) {
        Write-Host "`n=== Step 6: Failure screenshots ===" -ForegroundColor Cyan
        $shotDir = Join-Path ([System.IO.Path]::GetTempPath()) "test-failure-screenshots"
        if (Test-Path $shotDir) {
            $shots = Get-ChildItem -Path $shotDir -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending |
                Select-Object -First 20
            if ($shots) {
                $shots | Format-Table -AutoSize -Property Name, LastWriteTime, Length | Out-Host
                Write-Host "Screenshot dir: $shotDir" -ForegroundColor Yellow
            } else {
                Write-Host "No screenshots in $shotDir" -ForegroundColor Yellow
            }
        } else {
            Write-Host "No screenshot dir at $shotDir" -ForegroundColor Yellow
        }
    }
}
finally {
    # --- Step 7: Always kill site ---
    Write-Host "`n=== Step 7: Kill website (cleanup) ===" -ForegroundColor Cyan
    Stop-Site
    if ($webJob) {
        Stop-Job -Job $webJob -ErrorAction SilentlyContinue
        Remove-Job -Job $webJob -Force -ErrorAction SilentlyContinue
    }
}

exit $testExitCode
