@echo off
title EmergencyPass - Localhost Server
color 0B
echo ======================================================================
echo   EmergencyPass - Smart Emergency Private Vehicle Assistance System
echo   Starting Localhost Web Server...
echo ======================================================================
echo.

cd /d "%~dp0"

echo Launching application on http://localhost:5000 ...
echo Opening default web browser...
echo.

start "" cmd /c "timeout /t 2 >nul & start http://localhost:5000"
py app.py

pause
