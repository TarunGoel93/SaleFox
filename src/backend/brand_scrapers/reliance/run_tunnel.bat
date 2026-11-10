@echo off
title Reliance Scraper 24/7 Tunnel
cd /d "%~dp0"
:loop
echo [%date% %time%] Starting Cloudflare Tunnel...
cloudflared.exe tunnel --url http://127.0.0.1:5050 --protocol http2 --logfile tunnel.log
echo [%date% %time%] Tunnel disconnected! Reconnecting in 30 seconds...
ping 127.0.0.1 -n 31 >nul
goto loop
