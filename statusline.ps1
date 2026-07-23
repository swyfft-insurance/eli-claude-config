$j = [Console]::In.ReadToEnd() | ConvertFrom-Json

$m = $j.model.display_name
$mid = $j.model.id
$u = [int]($j.context_window.used_percentage)

if ($u -ge 75) { $c = "`e[31m"; $r = "`e[0m" }
elseif ($u -ge 50) { $c = "`e[33m"; $r = "`e[0m" }
else { $c = "`e[32m"; $r = "`e[0m" }

$parts = "$m ($mid) | ${c}Context: ${u}%${r}"

function Format-Timestamp($t, $withDate) {
    if ($withDate) {
        $day = @{Monday='Mon';Tuesday='Tue';Wednesday='Wed';Thursday='Th';
                 Friday='Fri';Saturday='Sat';Sunday='Sun'}[$t.DayOfWeek.ToString()]
        "$day $($t.ToString('M/d h:mm tt'))"
    } else {
        $t.ToString('h:mm tt')
    }
}

function Format-RateLimit($usedPct, $epoch, $windowHours, $withDate, $showExhaustion) {
    if ($null -eq $epoch) { return "" }
    $resetTime = [DateTimeOffset]::FromUnixTimeSeconds([long]$epoch).ToLocalTime()
    $text = "$([char]0x003B) reset $(Format-Timestamp $resetTime $withDate)"

    if ($showExhaustion) {
        $windowStart = $resetTime.AddHours(-$windowHours)
        $elapsedMinutes = ([DateTimeOffset]::Now - $windowStart).TotalMinutes
        if ($usedPct -gt 0 -and $elapsedMinutes -gt 0) {
            $projectedMinutes = $elapsedMinutes * (100.0 / $usedPct)
            $exhaustion = $windowStart.AddMinutes($projectedMinutes)
            $text += "$([char]0x003B) exh $(Format-Timestamp $exhaustion $withDate)"
        }
    }

    $text
}

$r5h = $j.rate_limits.five_hour.used_percentage
$r7d = $j.rate_limits.seven_day.used_percentage
if ($null -ne $r5h) {
    $parts += " | 5h: $([int]$r5h)%$(Format-RateLimit $r5h $j.rate_limits.five_hour.resets_at 5 $false $true)"
}
if ($null -ne $r7d) {
    $parts += " | 7d: $([int]$r7d)%$(Format-RateLimit $r7d $j.rate_limits.seven_day.resets_at 168 $true $true)"
}

$cwd = $j.cwd
$proj = $j.workspace.project_dir
if ($cwd -and $proj) {
    $short = $cwd.Replace($proj, '.')
    $parts += " | $short"
}

Write-Host $parts
