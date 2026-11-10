@echo off
title Amazon Intelligence Scraper Server (Port 5050)
cd /d "%~dp0"
set PORT=5050
echo Starting Amazon Scraper Server on port 5050...
python web_server.py
pause

