@echo off
title Vivo Intelligence Scraper (Port 5052)
cd /d "%~dp0"
set PORT=5052
echo Starting Vivo Intelligence Scraper Server on Port 5052...
python web_server.py
pause

