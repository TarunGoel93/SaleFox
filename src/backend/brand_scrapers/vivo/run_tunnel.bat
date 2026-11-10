@echo off
title Vivo Scraper 24/7 Tunnel
cd /d "%~dp0vivo_intelligence" 2>nul || cd /d "%~dp0"
echo ========================================================
echo   Vivo Intelligence Pro 24/7 Cloudflare HTTP/2 Tunnel
echo ========================================================
:loop
cloudflared.exe tunnel --url http://127.0.0.1:5050 --protocol http2
echo Tunnel disconnected! Reconnecting in 2 seconds...
timeout /t 2 /nobreak >nul
goto loop
