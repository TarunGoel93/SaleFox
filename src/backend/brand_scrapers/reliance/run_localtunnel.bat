@echo off
title Reliance Scraper LocalTunnel
cd /d "%~dp0"
echo Starting LocalTunnel on port 5050...
npx -y localtunnel --port 5050 --subdomain reliance-pro-dash
pause
