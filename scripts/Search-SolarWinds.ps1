<#
.SYNOPSIS
    Search SolarWinds Observability logs via the REST API.

.DESCRIPTION
    Splits date ranges into single-day chunks (wide ranges return empty from the API) and
    paginates through all results per day. Each search gets its own subfolder under the output
    root, containing two files:
      - logs.jsonl    Raw API log records, one per line (JSONL), written verbatim from the
                      response via System.Text.Json GetRawText() — never re-serialized, so no
                      field is altered or dropped. This is the parse target (Parse-SolarWindsLog.ps1).
      - metadata.txt  JSON run summary: filter, date range, run time, per-day counts, total.
                      Kept separate so logs.jsonl stays pure JSONL.

.PARAMETER Filter
    Full-text search query (e.g., "29bd85f2-f907-4ac2-bbcb-d11277329bf1 ThrowIfExcelError").

.PARAMETER StartDate
    Start date. Accepts yyyy-MM-dd (full day from 00:00) or yyyy-MM-ddTHH:mm:ssZ (sub-day boundary). Defaults to yesterday.

.PARAMETER EndDate
    End date. Accepts yyyy-MM-dd (full day to 23:59:59) or yyyy-MM-ddTHH:mm:ssZ (sub-day boundary). Defaults to today.

.PARAMETER PageSize
    Number of logs per API page. Default 100.

.PARAMETER TicketFolder
    REQUIRED. The ticket work-folder name under ~/.claude/tickets/ (e.g. SW-52867-<title>).
    Log dumps are written into that folder's gitignored artifacts/solarwinds/ area.

.PARAMETER OutputRoot
    Override for the folder under which the per-search subfolder is created.
    Defaults to the ticket's artifacts/solarwinds/ area.

.EXAMPLE
    .\Search-SolarWinds.ps1 -Filter "29bd85f2 ThrowIfExcelError" -StartDate 2026-03-28 -EndDate 2026-03-29
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$TicketFolder,

    [Parameter(Mandatory)]
    [string]$Filter,

    [string]$StartDate,
    [string]$EndDate,
    [int]$PageSize = 100,
    [string]$OutputRoot
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

$start = [DateTime]::Parse($StartDate)
$end = [DateTime]::Parse($EndDate)
if ($start -eq $end) {
    Write-Error "StartDate and EndDate resolve to the same timestamp ($start). Use -EndDate with the next day or a T23:59:59Z suffix."
    exit 1
}

# Each search gets its own subfolder (overwritten when the same filter+range is re-run), holding
# the raw JSONL data and the JSON metadata. Splitting data from run-summary keeps logs.jsonl pure.
if (-not $OutputRoot) { $OutputRoot = Join-Path $HOME ".claude/tickets/$TicketFolder/artifacts/solarwinds" }
$safeName = ($Filter -replace '[^a-zA-Z0-9\-]', '_').Substring(0, [Math]::Min(50, $Filter.Length))
$safeStartDate = $StartDate -replace '[:\s]', '_'
$safeEndDate = $EndDate -replace '[:\s]', '_'
$searchDir = Join-Path $OutputRoot "solarwinds-$safeName-$safeStartDate-to-$safeEndDate"
if (Test-Path $searchDir) { Remove-Item $searchDir -Recurse -Force }
New-Item -ItemType Directory -Path $searchDir -Force | Out-Null
$logFile = Join-Path $searchDir 'logs.jsonl'
$metaFile = Join-Path $searchDir 'metadata.txt'

$baseUrl = 'https://api.na-01.cloud.solarwinds.com/v1/logs'

Write-Host "SolarWinds Log Search" -ForegroundColor Cyan
Write-Host "Filter: $Filter"
Write-Host "Range: $StartDate to $EndDate"
Write-Host "Run at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# Return a named child JsonElement, or $null if absent. Avoids TryGetProperty's out-parameter,
# which PowerShell can't bind on the JsonElement struct.
function Get-JsonProp {
    param($Element, [string]$Name)
    if ($Element.ValueKind -ne [System.Text.Json.JsonValueKind]::Object) { return $null }
    foreach ($prop in $Element.EnumerateObject()) {
        if ($prop.Name -eq $Name) { return $prop.Value }
    }
    return $null
}

$rawLines = [System.Collections.Generic.List[string]]::new()
$dayCounts = [ordered]@{}
$totalLogs = 0

$currentDay = $start.Date
while ($currentDay -le $end.Date) {
    # Clamp the first day's start to the parsed StartDate (allows sub-day ranges like "T21:07:44Z")
    # and the last day's end to the parsed EndDate.
    $dayStart = if ($currentDay -eq $start.Date) { $start.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ") } else { $currentDay.ToString('yyyy-MM-ddT00:00:00Z') }
    $dayEnd   = if ($currentDay -eq $end.Date)   { $end.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")   } else { $currentDay.ToString('yyyy-MM-ddT23:59:59Z') }
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
        $rawText = ($raw -join "`n")

        $skipToken = $null
        # Parse the raw response. If the API returns something unparseable, fail loudly —
        # the JsonException halts the whole run. Never silently skip a page or a day.
        $doc = [System.Text.Json.JsonDocument]::Parse($rawText)
        try {
            $root = $doc.RootElement
            # Write each log record's raw JSON verbatim — no re-serialization, nothing dropped.
            $logsEl = Get-JsonProp $root 'logs'
            if ($null -ne $logsEl -and $logsEl.ValueKind -eq [System.Text.Json.JsonValueKind]::Array) {
                foreach ($el in $logsEl.EnumerateArray()) {
                    $rawLines.Add($el.GetRawText())
                    $dayLogs++
                    $totalLogs++
                }
            }
            # Follow pagination via pageInfo.nextPage.
            $pageInfoEl = Get-JsonProp $root 'pageInfo'
            if ($null -ne $pageInfoEl) {
                $nextPageEl = Get-JsonProp $pageInfoEl 'nextPage'
                if ($null -ne $nextPageEl -and
                    $nextPageEl.ValueKind -eq [System.Text.Json.JsonValueKind]::String) {
                    $nextPage = $nextPageEl.GetString()
                    if ($nextPage -and $nextPage -match 'skipToken=([^&]+)') {
                        $skipToken = [Uri]::UnescapeDataString($Matches[1])
                    }
                }
            }
        }
        finally {
            $doc.Dispose()
        }

        # Safety: stop after 50 pages per day
        if ($page -ge 50) {
            Write-Warning "Hit 50-page limit for $dayLabel, stopping pagination for this day."
            break
        }
    } while ($skipToken)

    $dayCounts[$dayLabel] = $dayLogs
    if ($dayLogs -gt 0) {
        Write-Host "$dayLabel : $dayLogs logs" -ForegroundColor Green
    }
    else {
        Write-Host "$dayLabel : 0 logs" -ForegroundColor DarkGray
    }

    $currentDay = $currentDay.AddDays(1)
}

# logs.jsonl: raw records only, one per line (WriteAllLines puts a newline after each).
[System.IO.File]::WriteAllLines($logFile, $rawLines)

# metadata.txt: JSON run summary, kept out of logs.jsonl so the data file stays pure JSONL.
$meta = [ordered]@{
    filter    = $Filter
    startDate = $StartDate
    endDate   = $EndDate
    runAt     = (Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz')
    pageSize  = $PageSize
    totalLogs = $totalLogs
    perDay    = $dayCounts
    logFile   = 'logs.jsonl'
}
$meta | ConvertTo-Json -Depth 5 | Out-File -FilePath $metaFile -Encoding utf8

Write-Host ""
Write-Host "Total: $totalLogs logs" -ForegroundColor Cyan
Write-Host "Output: $searchDir" -ForegroundColor Cyan
