@echo off
title Croma Intelligence Pro - 24/7 Supervisor
cd /d "%~dp0"
echo ========================================================
echo   Croma Intelligence Pro 24/7 Engine
echo ========================================================
python persistent_runner.py
pause
