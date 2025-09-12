@echo off
REM BugSeek - One-Click Setup for New PC (Windows)
REM This batch file automates the complete setup process

echo.
echo ================================================================
echo BugSeek - One-Click Setup for New PC (Windows)
echo ================================================================
echo This will automatically set up BugSeek with all dependencies
echo and sample data. The process may take a few minutes.
echo.
echo Prerequisites:
echo - Python 3.8 or higher (will be verified)
echo - Internet connection for downloading packages
echo.

set /p continue="Press Enter to continue or Ctrl+C to cancel..."

echo.
echo Running automated setup script...
echo.

REM Run the Python setup script
python setup_new_pc.py

if %errorlevel% equ 0 (
    echo.
    echo ================================================================
    echo SETUP COMPLETED SUCCESSFULLY!
    echo ================================================================
    echo.
    echo To start BugSeek:
    echo   1. Double-click 'start_bugseek.bat' 
    echo   2. Or run: python run.py
    echo.
    echo Access points:
    echo   - Frontend UI: http://localhost:8080
    echo   - Backend API: http://localhost:5000
    echo.
    set /p start="Would you like to start BugSeek now? (y/n): "
    if /i "%start%"=="y" (
        echo Starting BugSeek...
        python run.py
    ) else (
        echo Setup complete. Run 'python run.py' when ready to start.
    )
) else (
    echo.
    echo ================================================================
    echo SETUP FAILED!
    echo ================================================================
    echo.
    echo Please check the error messages above and try the manual setup:
    echo   1. See NEW_PC_SETUP_GUIDE.md for detailed instructions
    echo   2. Check Python installation and version
    echo   3. Ensure you're in the correct directory
    echo.
)

pause
