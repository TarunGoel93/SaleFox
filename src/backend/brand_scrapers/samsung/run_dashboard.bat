@echo off
title Samsung Intelligence Pro - Web Dashboard Server
cd /d "%~dp0"
echo ========================================================
echo   Samsung Galaxy Pro Intelligence Server (Port 5053)
echo ========================================================
set PORT=5053
python web_server.py
pause
