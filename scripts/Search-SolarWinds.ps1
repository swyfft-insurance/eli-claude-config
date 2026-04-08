<#
.SYNOPSIS
    Search SolarWinds Observability logs via the REST API.

.DESCRIPTION
    Splits date ranges into single-day chunks (wide ranges return empty from the API),
    paginates through all results per day, and writes logs to an output file.

.PARAMETER Filter
    Full-text search query (e.g., "29bd85f2-f907-4ac2-bbcb-d11277329bf1 ThrowIfExcelError").

.PARAMETER StartDate
    Start date (yyyy-MM-dd). Defaults to yesterday.

.PARAMETER EndDate
    End date (yyyy-MM-dd). Defaults to today.

.PARAMETER PageSize
    Number of logs per API page. Default 100.

.PARAMETER OutputFile
    Path to write results. Default: $env:TEMP\swyfft-logs\solarwinds-search.txt

.EXAMPLE
    .\Search-SolarWinds.ps1 -Filter "29bd85f2 ThrowIfExcelError" -StartDate 2026-03-28 -EndDate 2026-03-28
#>
param(
    [Parameter(Mandatory)]
    [string]$Filter,

    [string]$StartDate,
    [string]$EndDate,
    [int]$PageSize = 100,
    [string]$OutputFile
)

$ErrorActionPreference = 'Stop'

# Resolve API token
$token = [System.Environment]::GetEnvironmentVariable('SWO_API_TOKEN', 'User')
if (-not $token) {
    Write-Error "SWO_API_TOKEN not set. Set it via: [System.Environment]::SetEnvironmentVariable('SWO_API_TOKEN', 'YOUR_TOKEN', 'User')"
    exit 1
}

# Default dates
if (-not $StartDate) { $StartDate = (Get-Date).AddDays(-1).ToString('yyyy-MM-dd') }
if (-not $EndDate) { $EndDate = (Get-Date).ToString('yyyy-MM-dd') }

# Default output file
if (-not $OutputFile) {
    $outDir = Join-Path $env:TEMP 'swyfft-logs'
    if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir -Force | Out-Null }
    $safeName = ($Filter -replace '[^a-zA-Z0-9\-]', '_').Substring(0, [Math]::Min(50, $Filter.Length))
    $OutputFile = Join-Path $outDir "solarwinds-$safeName-$StartDate-to-$EndDate.txt"
}
$outFileDir = Split-Path $OutputFile -Parent
if (-not (Test-Path $outFileDir)) { New-Item -ItemType Directory -Path $outFileDir -Force | Out-Null }

$baseUrl = 'https://api.na-01.cloud.solarwinds.com/v1/logs'
$headers = @{ 'Authorization' = "Bearer $token" }

$start = [DateTime]::Parse($StartDate)
$end = [DateTime]::Parse($EndDate)
$totalLogs = 0

# Clear output file
"SolarWinds Log Search" | Out-File -FilePath $OutputFile -Encoding utf8
"Filter: $Filter" | Out-File -FilePath $OutputFile -Append -Encoding utf8
"Range: $StartDate to $EndDate" | Out-File -FilePath $OutputFile -Append -Encoding utf8
"Run at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -FilePath $OutputFile -Append -Encoding utf8
"" | Out-File -FilePath $OutputFile -Append -Encoding utf8

$currentDay = $start
while ($currentDay -le $end) {
    $dayStart = $currentDay.ToString('yyyy-MM-ddT00:00:00Z')
    $dayEnd = $currentDay.ToString('yyyy-MM-ddT23:59:59Z')
    $dayLabel = $currentDay.ToString('yyyy-MM-dd')

    $dayLogs = 0
    $skipToken = $null
    $page = 0

    do {
        $page++
        $query = "filter=$([Uri]::EscapeDataString($Filter))" +
                 "&startTime=$([Uri]::EscapeDataString($dayStart))" +
                 "&endTime=$([Uri]::EscapeDataString($dayEnd))" +
                 "&pageSize=$PageSize" +
                 "&direction=backward"
        if ($skipToken) { $query += "&skipToken=$([Uri]::EscapeDataString($skipToken))" }

        $url = "${baseUrl}?${query}"
        $raw = & curl -s -H "Authorization: Bearer $token" $url
        $response = $raw | ConvertFrom-Json

        $logs = $response.logs
        if ($logs -and $logs.Count -gt 0) {
            foreach ($log in $logs) {
                $dayLogs++
                $totalLogs++
                $time = $log.time
                $severity = $log.severity
                $hostname = $log.hostname
                $msg = $log.message
                "[$time] $severity | $hostname | $msg" | Out-File -FilePath $OutputFile -Append -Encoding utf8
                "" | Out-File -FilePath $OutputFile -Append -Encoding utf8
            }
        }

        # Extract skipToken from nextPage URL
        $skipToken = $null
        $nextPage = $response.pageInfo.nextPage
        if ($nextPage -and $nextPage -match 'skipToken=([^&]+)') {
            $skipToken = [Uri]::UnescapeDataString($Matches[1])
        }

        # Safety: stop after 50 pages per day
        if ($page -ge 50) {
            Write-Warning "Hit 50-page limit for $dayLabel, stopping pagination for this day."
            break
        }
    } while ($skipToken -and $logs -and $logs.Count -gt 0)

    if ($dayLogs -gt 0) {
        Write-Host "$dayLabel : $dayLogs logs" -ForegroundColor Green
    } else {
        Write-Host "$dayLabel : 0 logs" -ForegroundColor DarkGray
    }

    $currentDay = $currentDay.AddDays(1)
}

Write-Host ""
Write-Host "Total: $totalLogs logs" -ForegroundColor Cyan
Write-Host "Output: $OutputFile" -ForegroundColor Cyan
"" | Out-File -FilePath $OutputFile -Append -Encoding utf8
"Total: $totalLogs logs" | Out-File -FilePath $OutputFile -Append -Encoding utf8
