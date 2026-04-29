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

.PARAMETER NoBuild
    Skip Step 2 (Build-Solution.ps1). Use when you're confident the build is already current.

.EXAMPLE
    pwsh -NoProfile -File ~/.claude/scripts/Run-WebUiAcceptanceTest.ps1 -FilterMethod "*RoofGeometry*"

.EXAMPLE
    pwsh -NoProfile -File ~/.claude/scripts/Run-WebUiAcceptanceTest.ps1 -FilterMethod "*RoofGeometry*" -NoBuild
#>
param(
    [string]$FilterMethod,
    [string]$FilterClass,
    [string]$FilterTrait,
    [string]$FilterNamespace,
    [int]$HealthTimeoutSec = 60,
    [string]$HealthUrl = "https://localhost:5001",
    [switch]$NoBuild
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

# --- Output paths ---
# Test output is written by Run-DotnetTest.ps1 to %TEMP%\swyfft-tests\ (standard location).
# Website stdout always goes to the same dir so future agents have one place to look.
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$webOutputDir = Join-Path $env:TEMP "swyfft-tests"
if (-not (Test-Path $webOutputDir)) {
    New-Item -ItemType Directory -Path $webOutputDir -Force | Out-Null
}
$webOutputFile = Join-Path $webOutputDir "Run-WebUiAcceptanceTest_${timestamp}_website.txt"
Write-Host "Website stdout will be saved to: $webOutputFile" -ForegroundColor DarkCyan

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
    if ($NoBuild) {
        Write-Host "`n=== Step 2: Build (SKIPPED via -NoBuild) ===" -ForegroundColor Cyan
    } else {
        Write-Host "`n=== Step 2: Build Swyfft.slnx ===" -ForegroundColor Cyan
        & pwsh -NoProfile -File $buildScript -Solution "Swyfft.slnx"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Build failed with exit code $LASTEXITCODE. Aborting." -ForegroundColor Red
            exit $LASTEXITCODE
        }
    }

    # --- Step 3: Start site (background) ---
    # Tee the web job's stdout/stderr to the output file in real time so the log is
    # accessible while the test runs (and survives if the parent script is killed
    # before Step 7 — Receive-Job in finally is too late for live debugging).
    Write-Host "`n=== Step 3: Start website (background) ===" -ForegroundColor Cyan
    $webJob = Start-Job -ScriptBlock {
        param($repo, $script, $logFile)
        Set-Location $repo
        & pwsh -NoProfile -File $script *>&1 | Tee-Object -FilePath $logFile -Append
    } -ArgumentList $repoRoot, $runWebPath, $webOutputFile
    Write-Host "Started web job: Id=$($webJob.Id)" -ForegroundColor Green
    Write-Host "Live web log: $webOutputFile" -ForegroundColor DarkCyan

    # --- Step 4: Wait for health ---
    # ASP.NET returns 200 on root the moment Kestrel binds the port, but the React
    # app is served by Vite (http://localhost:5173) which compiles bundles on first
    # request. The test browser hits /sign-in, then waits for #email-address — that
    # selector wait races Vite's first compile and intermittently times out at 30s.
    # Two-stage check: (4a) ASP.NET listening, then (4b) force Vite to compile the
    # SPA entry by fetching it directly, with a long timeout for the cold compile.
    Write-Host "`n=== Step 4: Wait for health (up to ${HealthTimeoutSec}s, $HealthUrl) ===" -ForegroundColor Cyan

    # 4a: ASP.NET listening
    $healthy = $false
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    while ($stopwatch.Elapsed.TotalSeconds -lt $HealthTimeoutSec) {
        try {
            $resp = Invoke-WebRequest -Uri $HealthUrl -SkipCertificateCheck -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            if ($resp.StatusCode -eq 200) {
                $healthy = $true
                Write-Host "ASP.NET healthy at $HealthUrl ($([int]$stopwatch.Elapsed.TotalSeconds)s)" -ForegroundColor Green
                break
            }
        } catch {
            # Not ready yet
        }
        Start-Sleep -Seconds 5
    }

    if (-not $healthy) {
        Write-Host "ERROR: ASP.NET did not become healthy within ${HealthTimeoutSec}s." -ForegroundColor Red
        Write-Host "Web stdout will be saved on cleanup. See: $webOutputFile" -ForegroundColor Yellow
        exit 3
    }

    # 4b: Warm up Vite by fetching the SPA entry (Views/SinglePageApplication/Index.cshtml
    # references "/app/Page.tsx"). First request triggers a cold compile in Vite — give
    # it up to 120s before declaring the warmup failed.
    Write-Host "Warming up Vite (compiling /app/Page.tsx)..." -ForegroundColor Cyan
    $viteEntry = "http://localhost:5173/app/Page.tsx"
    $viteWarm = $false
    $viteStopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $viteTimeout = 120
    while ($viteStopwatch.Elapsed.TotalSeconds -lt $viteTimeout) {
        try {
            $resp = Invoke-WebRequest -Uri $viteEntry -TimeoutSec 90 -UseBasicParsing -ErrorAction Stop
            if ($resp.StatusCode -eq 200 -and $resp.Content.Length -gt 0) {
                $viteWarm = $true
                Write-Host "Vite warmed at $viteEntry ($([int]$viteStopwatch.Elapsed.TotalSeconds)s, $($resp.Content.Length) bytes)" -ForegroundColor Green
                break
            }
        } catch {
            # Vite still starting / compiling
        }
        Start-Sleep -Seconds 3
    }

    if (-not $viteWarm) {
        Write-Host "ERROR: Vite did not warm up within ${viteTimeout}s." -ForegroundColor Red
        Write-Host "Web stdout will be saved on cleanup. See: $webOutputFile" -ForegroundColor Yellow
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
    # --- Step 7: Tail live log + kill site ---
    # The web log is already being written live by Tee-Object inside the job
    # (see Step 3), so cleanup just tails the file and kills the job + site.
    Write-Host "`n=== Step 7: Tail web log + kill website (cleanup) ===" -ForegroundColor Cyan
    if (Test-Path $webOutputFile) {
        Write-Host "Web log: $webOutputFile" -ForegroundColor Green
        Write-Host "--- Last 50 lines ---" -ForegroundColor DarkCyan
        Get-Content -Path $webOutputFile -Tail 50 -ErrorAction SilentlyContinue | Out-Host
    } else {
        Write-Host "No web log at $webOutputFile" -ForegroundColor Yellow
    }
    if ($webJob) {
        Stop-Job -Job $webJob -ErrorAction SilentlyContinue
        Remove-Job -Job $webJob -Force -ErrorAction SilentlyContinue
    }
    Stop-Site
}

exit $testExitCode
