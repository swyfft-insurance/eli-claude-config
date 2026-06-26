<#
.SYNOPSIS
    Read a SolarWinds JSONL log file (produced by Search-SolarWinds.ps1) without dumping
    every full record into view.

.DESCRIPTION
    Search-SolarWinds.ps1 writes one complete log object per line (JSONL). Those lines are
    long (the message field carries large XML payloads), so reading the file raw is unusable.
    This helper gives two ways to look at it:

      -Keys            List every field that appears in the file, with how many records
                       contain it and a sample value. Use this first when you don't know
                       which field holds what you need (e.g. the environment).

      (default)        Print one short line per record showing only the fields you pick
                       (-Fields), with each value trimmed to -MessageMax characters so the
                       big message field can't blow up the line. Optionally keep only records
                       matching -Match.

.PARAMETER Path
    The JSONL file written by Search-SolarWinds.ps1.

.PARAMETER Keys
    Discovery mode: list field paths present (dot notation for nested), record counts, samples.

.PARAMETER Fields
    Comma-separated field paths to show per record (dot notation supported, e.g.
    "attributes.environment"). Default: time,severity,hostname,message.

.PARAMETER MessageMax
    Max characters shown per field value before truncation. Default 200.

.PARAMETER Match
    Regex; only records whose raw JSON line matches are shown (case-insensitive).

.PARAMETER First
    Show at most this many records (0 = all). Default 0.

.EXAMPLE
    .\Parse-SolarWindsLog.ps1 .\solarwinds-b7a17d53-...txt -Keys

.EXAMPLE
    .\Parse-SolarWindsLog.ps1 .\solarwinds-b7a17d53-...txt -Fields time,environment,severity,message -MessageMax 120
#>
param(
    [Parameter(Mandatory)]
    [string]$Path,

    [switch]$Keys,
    [string[]]$Fields = @('time', 'severity', 'hostname', 'message'),
    [int]$MessageMax = 200,
    [string]$Match,
    [int]$First = 0
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $Path)) {
    Write-Error "File not found: $Path"
    exit 1
}

# Render any value to a single trimmed line (objects/arrays become compact JSON).
function Format-Value {
    param($Value, [int]$Max)
    if ($null -eq $Value) { return '' }
    if ($Value -is [string]) { $s = $Value }
    else { $s = ($Value | ConvertTo-Json -Depth 50 -Compress) }
    $s = ($s -replace '\s+', ' ').Trim()
    if ($Max -gt 0 -and $s.Length -gt $Max) { $s = $s.Substring(0, $Max) + '…' }
    return $s
}

# Walk a record's properties, emitting "path => value" for every leaf (recursing into objects).
function Get-LeafPaths {
    param($Obj, [string]$Prefix)
    foreach ($prop in $Obj.PSObject.Properties) {
        $name = if ($Prefix) { "$Prefix.$($prop.Name)" } else { $prop.Name }
        $val = $prop.Value
        if ($val -is [System.Management.Automation.PSCustomObject]) {
            Get-LeafPaths -Obj $val -Prefix $name
        }
        else {
            [pscustomobject]@{ Path = $name; Value = $val }
        }
    }
}

# Follow a dot path (e.g. attributes.environment) into a record.
function Get-FieldValue {
    param($Obj, [string]$DotPath)
    $cur = $Obj
    foreach ($seg in $DotPath.Split('.')) {
        if ($null -eq $cur) { return $null }
        $prop = $cur.PSObject.Properties[$seg]
        if (-not $prop) { return $null }
        $cur = $prop.Value
    }
    return $cur
}

$lines = [System.IO.File]::ReadLines($Path)
$parsed = 0
$skipped = 0

if ($Keys) {
    # Discovery: which fields exist, in how many records, with a sample value.
    $counts = [ordered]@{}
    $samples = @{}
    $total = 0
    foreach ($line in $lines) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        try { $obj = $line | ConvertFrom-Json } catch { $skipped++; continue }
        $total++
        foreach ($leaf in (Get-LeafPaths -Obj $obj -Prefix '')) {
            if (-not $counts.Contains($leaf.Path)) {
                $counts[$leaf.Path] = 0
                $samples[$leaf.Path] = Format-Value -Value $leaf.Value -Max 80
            }
            $counts[$leaf.Path]++
            if (-not $samples[$leaf.Path] -and $null -ne $leaf.Value) {
                $samples[$leaf.Path] = Format-Value -Value $leaf.Value -Max 80
            }
        }
    }
    if ($total -eq 0) {
        Write-Host "No records found in $Path" -ForegroundColor Yellow
        if ($skipped -gt 0) { Write-Host "$skipped non-JSON line(s) skipped." -ForegroundColor DarkGray }
        exit 0
    }
    $pad = ($counts.Keys | Measure-Object -Property Length -Maximum).Maximum
    Write-Host "Fields across $total record(s):" -ForegroundColor Cyan
    foreach ($k in ($counts.Keys | Sort-Object)) {
        $name = $k.PadRight($pad)
        $cov = "($($counts[$k])/$total)".PadRight(10)
        Write-Host "$name  $cov  $($samples[$k])"
    }
    if ($skipped -gt 0) { Write-Host "`n$skipped non-JSON line(s) skipped." -ForegroundColor DarkGray }
    exit 0
}

# Projected view: one short line per record, only the chosen fields.
# Accept both -Fields a,b,c (bound as an array) and -Fields "a,b,c" (one string) by
# splitting every element on commas and flattening.
$fieldList = $Fields | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ }
$shown = 0
foreach ($line in $lines) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    if ($Match -and ($line -notmatch $Match)) { continue }
    try { $obj = $line | ConvertFrom-Json } catch { $skipped++; continue }
    $parsed++
    $cells = foreach ($f in $fieldList) {
        Format-Value -Value (Get-FieldValue -Obj $obj -DotPath $f) -Max $MessageMax
    }
    $cells -join ' | '
    $shown++
    if ($First -gt 0 -and $shown -ge $First) { break }
}

Write-Host "`n$shown record(s) shown." -ForegroundColor Cyan
if ($skipped -gt 0) { Write-Host "$skipped non-JSON line(s) skipped." -ForegroundColor DarkGray }
