@echo off
REM BugSeek - Database Clear Script (Windows)
REM This batch file clears all data from the BugSeek database

echo.
echo ================================================================
echo BugSeek - Database Clear Utility
echo ================================================================
echo This will clear ALL data from your BugSeek database!
echo A backup will be created automatically before clearing.
echo.
echo WARNING: This action cannot be undone (except from backup)!
echo.

set /p confirm="Are you sure you want to clear the database? (type YES to confirm): "

if /i not "%confirm%"=="YES" (
    echo Operation cancelled.
    pause
    exit /b 0
)

echo.
echo Running database clear script...
echo.

REM Run the Python clear script
python clear_database.py

if %errorlevel% equ 0 (
    echo.
    echo ================================================================
    echo DATABASE CLEARED SUCCESSFULLY!
    echo ================================================================
    echo.
    echo Next steps:
    echo   1. To load sample data: python 2_load_sample_data.py
    echo   2. To start fresh: python 1_initialize_database.py
    echo   3. To start BugSeek: python run.py
    echo.
) else (
    echo.
    echo ================================================================
    echo DATABASE CLEAR FAILED!
    echo ================================================================
    echo.
    echo Please check the error messages above.
    echo You may need to:
    echo   - Stop BugSeek if it's currently running
    echo   - Check file permissions
    echo   - Ensure you're in the correct directory
    echo.
)

pause
