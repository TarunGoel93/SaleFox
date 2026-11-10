@echo off
title Croma Intelligence Pro - Web Dashboard Server
cd /d "%~dp0"
echo ========================================================
echo   Croma Intelligence Pro Server (Port 5054)
echo ========================================================
set PORT=5054
python web_server.py
pause
