$j = [Console]::In.ReadToEnd() | ConvertFrom-Json

$m = $j.model.display_name
$mid = $j.model.id
$u = [int]($j.context_window.used_percentage)

if ($u -ge 75) { $c = "`e[31m"; $r = "`e[0m" }
elseif ($u -ge 50) { $c = "`e[33m"; $r = "`e[0m" }
else { $c = "`e[32m"; $r = "`e[0m" }

$parts = "$m ($mid) | ${c}Context: ${u}%${r}"

$r5h = $j.rate_limits.five_hour.used_percentage
$r7d = $j.rate_limits.seven_day.used_percentage
if ($null -ne $r5h) { $parts += " | 5h: $([int]$r5h)%" }
if ($null -ne $r7d) { $parts += " | 7d: $([int]$r7d)%" }

$cwd = $j.cwd
$proj = $j.workspace.project_dir
if ($cwd -and $proj) {
    $short = $cwd.Replace($proj, '.')
    $parts += " | $short"
}

Write-Host $parts
