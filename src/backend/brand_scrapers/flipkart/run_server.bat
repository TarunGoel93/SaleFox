@echo off
title Flipkart Scraper Service (Port 5051)
cd /d "%~dp0"
set PORT=5051
echo Starting Flipkart Scraper Web Server on Port 5051...
python web_server.py
pause

