@echo off
title Scalefox Multi-Scraper Launcher
echo ===================================================
echo   Scalefox Live Multi-Scraper Launch Suite
echo   Launching: Amazon (5050), Flipkart (5051), Apple (5055), Croma (5054), Samsung (5053), Vivo (5052), Reliance (5056), JioMart (5062), Oppo (5057)
echo ===================================================

cd /d "%~dp0"

echo [1/9] Starting Amazon Scraper (Port 5050)...
start "Amazon Scraper (Port 5050)" cmd /k "cd /d %~dp0\brand_scrapers\amazon && set PORT=5050 && python web_server.py"

timeout /t 2 /nobreak >nul

echo [2/9] Starting Flipkart Scraper (Port 5051)...
start "Flipkart Scraper (Port 5051)" cmd /k "cd /d %~dp0\brand_scrapers\flipkart && set PORT=5051 && python web_server.py"

timeout /t 2 /nobreak >nul

echo [3/9] Starting Apple Scraper (Port 5055)...
start "Apple Scraper (Port 5055)" cmd /k "cd /d %~dp0\brand_scrapers\apple && set PORT=5055 && python web_server.py"

timeout /t 2 /nobreak >nul

echo [4/9] Starting Croma Scraper (Port 5054)...
start "Croma Scraper (Port 5054)" cmd /k "cd /d %~dp0\brand_scrapers\croma && set PORT=5054 && python web_server.py"

timeout /t 2 /nobreak >nul

echo [5/9] Starting Samsung Scraper (Port 5053)...
start "Samsung Scraper (Port 5053)" cmd /k "cd /d %~dp0\brand_scrapers\samsung && set PORT=5053 && python web_server.py"

timeout /t 2 /nobreak >nul

echo [6/9] Starting Vivo Scraper (Port 5052)...
start "Vivo Scraper (Port 5052)" cmd /k "cd /d %~dp0\brand_scrapers\vivo && set PORT=5052 && python web_server.py"

timeout /t 2 /nobreak >nul

echo [7/9] Starting Reliance Digital Scraper (Port 5056)...
start "Reliance Digital Scraper (Port 5056)" cmd /k "cd /d %~dp0\brand_scrapers\reliance && set PORT=5056 && python web_server.py"

timeout /t 2 /nobreak >nul

echo [8/9] Starting JioMart Scraper (Port 5062)...
start "JioMart Scraper (Port 5062)" cmd /k "cd /d %~dp0\brand_scrapers\jiomart && set PORT=5062 && python web_server.py"

timeout /t 2 /nobreak >nul

echo [9/9] Starting Oppo Scraper (Port 5057)...
start "Oppo Scraper (Port 5057)" cmd /k "cd /d %~dp0\brand_scrapers\oppo && set PORT=5057 && python web_server.py"

echo ===================================================
echo All scrapers launched in separate windows!
echo - Amazon:   http://localhost:5050
echo - Flipkart: http://localhost:5051
echo - Apple:    http://localhost:5055
echo - Croma:    http://localhost:5054
echo - Samsung:  http://localhost:5053
echo - Vivo:     http://localhost:5052
echo - Reliance: http://localhost:5056
echo - JioMart:  http://localhost:5062
echo - Oppo:     http://localhost:5057
echo ===================================================
pause
