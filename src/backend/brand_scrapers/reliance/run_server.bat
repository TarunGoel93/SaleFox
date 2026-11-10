@echo off
title Reliance Digital Web Server
cd /d "%~dp0"
set OPENBLAS_NUM_THREADS=1
set MKL_NUM_THREADS=1
set OMP_NUM_THREADS=1
set NUMEXPR_NUM_THREADS=1
set PORT=5056
echo Starting Reliance Digital Web Server on port 5056...
:loop
python web_server.py
echo [WARNING] Server stopped. Restarting in 2 seconds...
ping 127.0.0.1 -n 3 >nul
goto loop
