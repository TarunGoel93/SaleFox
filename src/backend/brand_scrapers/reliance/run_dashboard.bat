@echo off
title Reliance Digital Pro Intelligence Server
cd /d "%~dp0"
echo =====================================================================
echo  Reliance Digital Pro Intelligence Scraper - Web Dashboard
echo =====================================================================
echo Starting server on http://127.0.0.1:5050 ...
start "" http://127.0.0.1:5050
python web_server.py
pause
