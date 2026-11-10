@echo off
title JioMart Scraper Server (Port 5062)
cd /d "%~dp0"
set PORT=5062
echo Starting JioMart Scraper Server on port 5062...
python web_server.py
pause

