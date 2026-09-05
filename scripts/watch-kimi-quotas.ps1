$mutex = [Threading.Mutex]::new($false, "Local\CpuritanKimiQuotaWatcher")
if (-not $mutex.WaitOne(0)) { exit 0 }

$pushScript = Join-Path $PSScriptRoot "push-kimi-quotas.ps1"
$logPath = Join-Path $PSScriptRoot "state\kimi-quota.log"

try {
  while ($true) {
    try {
      & $pushScript | Out-Null
    } catch {
      $message = "{0} {1}" -f (Get-Date).ToUniversalTime().ToString("o"), $_.Exception.Message
      Add-Content -LiteralPath $logPath -Value $message -Encoding utf8
    }
    Start-Sleep -Seconds 60
  }
} finally {
  $mutex.ReleaseMutex()
  $mutex.Dispose()
}
