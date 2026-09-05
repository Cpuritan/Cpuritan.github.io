$ErrorActionPreference = "Stop"

$apiUrl = "https://cpuritan-schedule.bqf-cpuritan.workers.dev/api/quotas/kimi"
$pushToken = [Environment]::GetEnvironmentVariable("CPURITAN_QUOTA_PUSH_TOKEN", "User")
if (-not $pushToken) { throw "Missing CPURITAN_QUOTA_PUSH_TOKEN" }

$credentialPath = Join-Path $env:USERPROFILE ".kimi-code\credentials\kimi-code.json"
$databasePath = Join-Path $env:USERPROFILE ".cc-switch\cc-switch.db"
$sqlite = (Get-Command sqlite3 -ErrorAction Stop).Source

$credential = Get-Content -Raw -LiteralPath $credentialPath | ConvertFrom-Json
$parts = $credential.access_token -split "\."
if ($parts.Count -lt 2) { throw "Current Kimi login is unavailable" }
$jwtPayload = $parts[1].Replace("-", "+").Replace("_", "/")
switch ($jwtPayload.Length % 4) {
  2 { $jwtPayload += "==" }
  3 { $jwtPayload += "=" }
}
$claims = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($jwtPayload)) | ConvertFrom-Json
$currentUserId = [string]$claims.user_id

$query = "SELECT json_group_array(json(settings_config)) FROM providers WHERE lower(name) LIKE '%kimi%' OR lower(settings_config) LIKE '%kimi.com/coding%';"
$configs = (& $sqlite -readonly $databasePath $query) | ConvertFrom-Json
$candidates = foreach ($config in $configs) {
  if ($config.auth.OPENAI_API_KEY) { [string]$config.auth.OPENAI_API_KEY }
  $match = [regex]::Match([string]$config.config, 'experimental_bearer_token\s*=\s*"([^"]+)"')
  if ($match.Success) { $match.Groups[1].Value }
}

$accounts = @{}
foreach ($candidate in @($candidates | Sort-Object -Unique)) {
  try {
    $usage = Invoke-RestMethod -Uri "https://api.kimi.com/coding/v1/usages" -Headers @{ Authorization = "Bearer $candidate" } -Method Get -TimeoutSec 30
  } catch {
    continue
  }

  $name = if ([string]$usage.user.userId -eq $currentUserId) { "Kimi-Bob" } else { "Kimi-Mary" }
  if ($accounts.ContainsKey($name)) { continue }
  $fiveHour = @($usage.limits | Where-Object { $_.window.duration -eq 300 -and $_.window.timeUnit -eq "TIME_UNIT_MINUTE" })[0]
  if (-not $fiveHour -or -not $usage.usage) { continue }

  $accounts[$name] = [ordered]@{
    name = $name
    fiveHour = [ordered]@{
      remainingPercent = [decimal]$fiveHour.detail.remaining
      resetsAt = [string]$fiveHour.detail.resetTime
    }
    weekly = [ordered]@{
      remainingPercent = [decimal]$usage.usage.remaining
      resetsAt = [string]$usage.usage.resetTime
    }
  }
}

if (-not $accounts.ContainsKey("Kimi-Bob") -or -not $accounts.ContainsKey("Kimi-Mary")) {
  throw "Both Kimi account quotas are required"
}

$payload = [ordered]@{
  capturedAt = (Get-Date).ToUniversalTime().ToString("o")
  accounts = @($accounts["Kimi-Bob"], $accounts["Kimi-Mary"])
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri $apiUrl -Method Post -Headers @{ Authorization = "Bearer $pushToken" } -ContentType "application/json" -Body $payload -TimeoutSec 30 | Out-Null
Write-Output "Kimi quota snapshot pushed."
