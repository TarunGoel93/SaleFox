@echo off
title Reliance Digital Pro Intelligence 24/7 Launcher
cd /d "%~dp0"

set OPENBLAS_NUM_THREADS=1
set MKL_NUM_THREADS=1
set OMP_NUM_THREADS=1
set NUMEXPR_NUM_THREADS=1

echo ============================================================
echo   STARTING RELIANCE DIGITAL PRO INTELLIGENCE (24/7 MODE)
echo ============================================================
echo [1/2] Starting Flask Backend Server (Port 5050)...
start "Reliance Web Server (Port 5050)" /min cmd /c "run_server.bat"

echo [2/2] Starting Cloudflare Public Tunnel...
start "Reliance Cloudflare Tunnel" /min cmd /c "run_tunnel.bat"

echo.
echo ==================================================x`==========
echo   Both processes are running in the background!
echo   Open 'public_url.txt' to view your active public link.
echo ============================================================
ping 127.0.0.1 -n 5 >nul
