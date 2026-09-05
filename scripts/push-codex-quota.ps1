param(
  [Parameter(Mandatory = $true)][decimal]$FiveHourRemaining,
  [Parameter(Mandatory = $true)][string]$FiveHourResetsAt,
  [Parameter(Mandatory = $true)][decimal]$WeeklyRemaining,
  [Parameter(Mandatory = $true)][string]$WeeklyResetsAt
)

$ErrorActionPreference = "Stop"
$apiUrl = "https://cpuritan-schedule.bqf-cpuritan.workers.dev/api/quotas/codex"
$pushToken = [Environment]::GetEnvironmentVariable("CPURITAN_QUOTA_PUSH_TOKEN", "User")
if (-not $pushToken) { throw "Missing CPURITAN_QUOTA_PUSH_TOKEN" }

$payload = [ordered]@{
  capturedAt = (Get-Date).ToUniversalTime().ToString("o")
  fiveHour = [ordered]@{
    remainingPercent = $FiveHourRemaining
    resetsAt = ([DateTimeOffset]$FiveHourResetsAt).ToUniversalTime().ToString("o")
  }
  weekly = [ordered]@{
    remainingPercent = $WeeklyRemaining
    resetsAt = ([DateTimeOffset]$WeeklyResetsAt).ToUniversalTime().ToString("o")
  }
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri $apiUrl -Method Post -Headers @{ Authorization = "Bearer $pushToken" } -ContentType "application/json" -Body $payload -TimeoutSec 30 | Out-Null
Write-Output "Codex quota snapshot pushed."
