# 24/7 Persistent Cloudflare Tunnel Monitor with Auto-Restart
$logFile = Join-Path $PSScriptRoot "tunnel.log"
$urlFile = Join-Path $PSScriptRoot "public_url.txt"
$cfExe = Join-Path $PSScriptRoot "cloudflared.exe"

while ($true) {
    Write-Host "[$(Get-Date)] Starting Cloudflare Tunnel on http://127.0.0.1:5050..."
    
    # Clear previous log
    if (Test-Path $logFile) { Remove-Item $logFile -Force }
    
    # Start cloudflared process
    $proc = Start-Process -FilePath $cfExe -ArgumentList "tunnel --url http://127.0.0.1:5050 --protocol http2 --logfile `"$logFile`"" -PassThru -WindowStyle Hidden
    
    # Wait for the tunnel URL to appear in the log file
    $foundUrl = $false
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        if (Test-Path $logFile) {
            $match = Get-Content $logFile -ErrorAction SilentlyContinue | Select-String -Pattern 'https://[a-zA-Z0-9-]+\.trycloudflare\.com'
            if ($match) {
                $url = $match.Matches[0].Value
                $url | Out-File -FilePath $urlFile -Encoding utf8 -Force
                Write-Host "[$(Get-Date)] Tunnel Live: $url"
                $foundUrl = $true
                break
            }
        }
    }
    
    # Wait for the process to exit (e.g. edge disconnect or network switch)
    if ($proc -and -not $proc.HasExited) {
        $proc.WaitForExit()
    }
    
    Write-Host "[$(Get-Date)] Tunnel exited. Reconnecting in 3 seconds..."
    Start-Sleep -Seconds 3
}
