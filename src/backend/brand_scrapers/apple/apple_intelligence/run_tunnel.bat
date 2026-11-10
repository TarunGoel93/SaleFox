@echo off
title Apple Scraper 24/7 Tunnel
cd /d "%~dp0"
echo ========================================================
echo   Apple Intelligence Pro 24/7 Cloudflare HTTP/2 Tunnel
echo ========================================================
:loop
cloudflared.exe tunnel --url http://127.0.0.1:5050 --protocol http2
echo Tunnel disconnected! Reconnecting in 2 seconds...
timeout /t 2 /nobreak >nul
goto loop
