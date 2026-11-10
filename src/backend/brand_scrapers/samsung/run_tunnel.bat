@echo off
title Samsung Scraper 24/7 Tunnel
cd /d "%~dp0"
echo ========================================================
echo   Samsung Intelligence Pro 24/7 Public Tunnel
echo ========================================================
echo Attempting Cloudflare Tunnel...
cloudflared.exe tunnel --url http://127.0.0.1:5051 --protocol http2
echo.
echo Cloudflare rate-limited or disconnected. Switching to Localtunnel fallback...
npx -y localtunnel --port 5051
pause
