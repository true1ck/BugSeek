@echo off
REM BugSeek - Quick Start Script
REM Double-click this file to start BugSeek after setup

echo.
echo ================================================================
echo Starting BugSeek Error Log Management System
echo ================================================================
echo.
echo Backend will start on: http://localhost:5000
echo Frontend will start on: http://localhost:8080
echo.
echo Press Ctrl+C to stop the application
echo ================================================================
echo.

REM Start BugSeek
python run.py

echo.
echo BugSeek has been stopped.
pause
