<#
.SYNOPSIS
    Search SolarWinds Observability logs via the REST API.

.DESCRIPTION
    Splits date ranges into single-day chunks (wide ranges return empty from the API) and
    fetches the days in parallel, paginating through all results within each day. Each search
    gets its own subfolder under the output root, containing:
      - logs.jsonl    Raw API log records, one per line (JSONL), written verbatim from the
                      response via System.Text.Json GetRawText() — never re-serialized, so no
                      field is altered or dropped. This is the parse target (Parse-SolarWindsLog.ps1).
                      Assembled in day order once every day has been fetched.
      - days/         One <yyyy-MM-dd>.jsonl per day, flushed after every page. Readable while
                      the run is still going; removed once logs.jsonl is assembled. A run that
                      dies partway leaves them in place.
      - progress.txt  One line per finished day (day, count, time), in completion order. Shows
                      how far a run has got while it is still going.
      - metadata.txt  JSON run summary: filter, date range, run time, per-day counts, total, and
                      status ("complete", or "incomplete" when any day failed). Kept separate so
                      logs.jsonl stays pure JSONL.

.PARAMETER Filter
    Full-text search query (e.g., "29bd85f2-f907-4ac2-bbcb-d11277329bf1 ThrowIfExcelError").

.PARAMETER StartDate
    Start date. Accepts yyyy-MM-dd (full day from 00:00) or yyyy-MM-ddTHH:mm:ssZ (sub-day boundary). Defaults to yesterday.

.PARAMETER EndDate
    End date. Accepts yyyy-MM-dd (full day to 23:59:59) or yyyy-MM-ddTHH:mm:ssZ (sub-day boundary). Defaults to today.

.PARAMETER PageSize
    Number of logs per API page. Default 100.

.PARAMETER ThrottleLimit
    How many days are fetched at once. Default 8. Pages within one day are always sequential,
    because each page's skipToken comes from the page before it.

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
    [ValidateRange(1, 16)]
    [int]$ThrottleLimit = 8,
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
# Name the folder from the search terms, not the program/severity scope: every ticket query starts
# with the same "program:(...) severity:error" prefix, which alone filled the old 50-char name and
# made different searches over the same dates share (and delete) one folder. The hash of the full
# filter keeps two distinct filters apart even when their readable part truncates the same.
$distinctTerms = ($Filter -replace 'program:\([^)]*\)', '' -replace 'severity:\S+', '').Trim()
if (-not $distinctTerms) { $distinctTerms = $Filter }
$safeTerms = $distinctTerms -replace '[^a-zA-Z0-9\-]', '_'
$safeName = $safeTerms.Substring(0, [Math]::Min(50, $safeTerms.Length))
$filterHash = [System.BitConverter]::ToString(
    [System.Security.Cryptography.SHA256]::HashData([System.Text.Encoding]::UTF8.GetBytes($Filter))
).Replace('-', '').Substring(0, 8).ToLowerInvariant()
$safeStartDate = $StartDate -replace '[:\s]', '_'
$safeEndDate = $EndDate -replace '[:\s]', '_'
$searchDir = Join-Path $OutputRoot "solarwinds-$safeName-$filterHash-$safeStartDate-to-$safeEndDate"
if (Test-Path $searchDir) { Remove-Item $searchDir -Recurse -Force }
New-Item -ItemType Directory -Path $searchDir -Force | Out-Null
$daysDir = Join-Path $searchDir 'days'
New-Item -ItemType Directory -Path $daysDir -Force | Out-Null
$logFile = Join-Path $searchDir 'logs.jsonl'
$metaFile = Join-Path $searchDir 'metadata.txt'
$progressFile = Join-Path $searchDir 'progress.txt'

$baseUrl = 'https://api.na-01.cloud.solarwinds.com/v1/logs'

Write-Host "SolarWinds Log Search" -ForegroundColor Cyan
Write-Host "Filter: $Filter"
Write-Host "Range: $StartDate to $EndDate"
Write-Host "Parallel days: $ThrottleLimit"
Write-Host "Run at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# One work item per day. The first day's start is clamped to the parsed StartDate (allows
# sub-day ranges like "T21:07:44Z") and the last day's end to the parsed EndDate.
$days = [System.Collections.Generic.List[object]]::new()
$currentDay = $start.Date
while ($currentDay -le $end.Date) {
    $days.Add([pscustomobject]@{
        Label = $currentDay.ToString('yyyy-MM-dd')
        Start = if ($currentDay -eq $start.Date) { $start.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ") } else { $currentDay.ToString('yyyy-MM-ddT00:00:00Z') }
        End   = if ($currentDay -eq $end.Date)   { $end.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")   } else { $currentDay.ToString('yyyy-MM-ddT23:59:59Z') }
    })
    $currentDay = $currentDay.AddDays(1)
}

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
# Every day's worker writes its progress line here, so the writer is synchronized.
$progressWriter = [System.IO.TextWriter]::Synchronized(
    [System.IO.StreamWriter]::new($progressFile, $false, $utf8NoBom))

$results = @()
try {
    $results = $days | ForEach-Object -ThrottleLimit $ThrottleLimit -Parallel {
        $day = $_
        $ErrorActionPreference = 'Stop'
        $maxPagesPerDay = 50
        $maxAttempts = 5
        $retryableStatuses = @(429, 500, 502, 503, 504)

        # Return a named child JsonElement, or $null if absent. Avoids TryGetProperty's
        # out-parameter, which PowerShell can't bind on the JsonElement struct.
        function Get-JsonProp {
            param($Element, [string]$Name)
            if ($Element.ValueKind -ne [System.Text.Json.JsonValueKind]::Object) { return $null }
            foreach ($prop in $Element.EnumerateObject()) {
                if ($prop.Name -eq $Name) { return $prop.Value }
            }
            return $null
        }

        $dayFile = Join-Path $using:daysDir "$($day.Label).jsonl"
        $writer = [System.IO.StreamWriter]::new($dayFile, $false, $using:utf8NoBom)
        $dayLogs = 0
        $hitPageLimit = $false
        try {
            $skipToken = $null
            $page = 0
            do {
                $page++
                $query = "filter=$([Uri]::EscapeDataString($using:Filter))" +
                         "&startTime=$([Uri]::EscapeDataString($day.Start))" +
                         "&endTime=$([Uri]::EscapeDataString($day.End))" +
                         "&pageSize=$($using:PageSize)" +
                         "&direction=backward"
                if ($skipToken) { $query += "&skipToken=$([Uri]::EscapeDataString($skipToken))" }
                $url = "$($using:baseUrl)?$query"

                # Parallel days can trip the API's rate limit, so throttled and transient
                # responses are retried with backoff. Anything else fails the day loudly.
                $attempt = 0
                while ($true) {
                    $attempt++
                    $raw = & curl -s -w "`n%{http_code}" -H "Authorization: Bearer $($using:token)" $url
                    $lines = @($raw)
                    $status = [int]$lines[-1]
                    $rawText = ($lines[0..($lines.Count - 2)] -join "`n")
                    if ($status -eq 200) { break }
                    if ($status -notin $retryableStatuses -or $attempt -ge $maxAttempts) {
                        throw "HTTP $status on $($day.Label) page $page after $attempt attempt(s): $rawText"
                    }
                    Start-Sleep -Seconds ([Math]::Pow(2, $attempt))
                }

                $skipToken = $null
                # If the API returns something unparseable, fail the day loudly. Never silently
                # skip a page or a day.
                $doc = [System.Text.Json.JsonDocument]::Parse($rawText)
                try {
                    $root = $doc.RootElement
                    # Write each log record's raw JSON verbatim — no re-serialization, nothing dropped.
                    $logsEl = Get-JsonProp $root 'logs'
                    if ($null -ne $logsEl -and $logsEl.ValueKind -eq [System.Text.Json.JsonValueKind]::Array) {
                        foreach ($el in $logsEl.EnumerateArray()) {
                            $writer.WriteLine($el.GetRawText())
                            $dayLogs++
                        }
                        $writer.Flush()
                    }
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

                if ($skipToken -and $page -ge $maxPagesPerDay) {
                    $hitPageLimit = $true
                    break
                }
            } while ($skipToken)

            ($using:progressWriter).WriteLine("$($day.Label)`t$dayLogs`t$(Get-Date -Format 'HH:mm:ss')")
            ($using:progressWriter).Flush()
            [pscustomobject]@{ Label = $day.Label; Count = $dayLogs; HitPageLimit = $hitPageLimit; Error = $null }
        }
        catch {
            ($using:progressWriter).WriteLine("$($day.Label)`tFAILED`t$(Get-Date -Format 'HH:mm:ss')`t$($_.Exception.Message)")
            ($using:progressWriter).Flush()
            [pscustomobject]@{ Label = $day.Label; Count = $dayLogs; HitPageLimit = $hitPageLimit; Error = $_.Exception.Message }
        }
        finally {
            $writer.Dispose()
        }
    }
}
finally {
    $progressWriter.Dispose()
}

# Assemble logs.jsonl in day order and summarize. A run is complete only when every day came back
# without an error; otherwise the per-day files stay behind next to the partial logs.jsonl.
$byDay = @{}
foreach ($r in $results) { $byDay[$r.Label] = $r }
$dayCounts = [ordered]@{}
$failedDays = [ordered]@{}
$pageLimitDays = [System.Collections.Generic.List[string]]::new()
$totalLogs = 0
$logWriter = [System.IO.StreamWriter]::new($logFile, $false, $utf8NoBom)
try {
    foreach ($day in $days) {
        $r = $byDay[$day.Label]
        if ($null -eq $r) {
            $failedDays[$day.Label] = 'no result returned'
            continue
        }
        if ($r.Error) { $failedDays[$day.Label] = $r.Error }
        if ($r.HitPageLimit) { $pageLimitDays.Add($day.Label) }
        $dayCounts[$day.Label] = $r.Count
        $totalLogs += $r.Count
        $dayFile = Join-Path $daysDir "$($day.Label).jsonl"
        if (Test-Path $dayFile) {
            foreach ($line in [System.IO.File]::ReadLines($dayFile)) { $logWriter.WriteLine($line) }
        }
    }
}
finally {
    $logWriter.Dispose()
}

$runStatus = if ($failedDays.Count -eq 0) { 'complete' } else { 'incomplete' }
if ($runStatus -eq 'complete') { Remove-Item $daysDir -Recurse -Force }

# metadata.txt: JSON run summary, kept out of logs.jsonl so the data file stays pure JSONL.
$meta = [ordered]@{
    filter         = $Filter
    startDate      = $StartDate
    endDate        = $EndDate
    runAt          = (Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz')
    status         = $runStatus
    pageSize       = $PageSize
    throttleLimit  = $ThrottleLimit
    totalLogs      = $totalLogs
    perDay         = $dayCounts
    failedDays     = $failedDays
    pageLimitDays  = $pageLimitDays
    logFile        = 'logs.jsonl'
}
$meta | ConvertTo-Json -Depth 5 | Out-File -FilePath $metaFile -Encoding utf8

foreach ($label in $dayCounts.Keys) {
    $count = $dayCounts[$label]
    Write-Host "$label : $count logs" -ForegroundColor ($(if ($count -gt 0) { 'Green' } else { 'DarkGray' }))
}
foreach ($label in $pageLimitDays) {
    Write-Warning "Hit the 50-page limit for $label; that day's results are truncated."
}
foreach ($label in $failedDays.Keys) {
    Write-Warning "$label FAILED: $($failedDays[$label])"
}
Write-Host ""
Write-Host "Status: $runStatus" -ForegroundColor ($(if ($runStatus -eq 'complete') { 'Cyan' } else { 'Red' }))
Write-Host "Total: $totalLogs logs" -ForegroundColor Cyan
Write-Host "Output: $searchDir" -ForegroundColor Cyan
if ($runStatus -ne 'complete') { exit 1 }
