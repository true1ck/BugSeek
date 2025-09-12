# BugSeek - Database Clear Script (PowerShell)
# This script clears all data from the BugSeek database with safety checks

Write-Host ""
Write-Host "================================================================" -ForegroundColor Blue
Write-Host "BugSeek - Database Clear Utility" -ForegroundColor Blue
Write-Host "================================================================" -ForegroundColor Blue
Write-Host "This will clear ALL data from your BugSeek database!" -ForegroundColor Yellow
Write-Host "A backup will be created automatically before clearing." -ForegroundColor Green
Write-Host ""
Write-Host "WARNING: This action cannot be undone (except from backup)!" -ForegroundColor Red
Write-Host ""

# Check if we're in the correct directory
if (-not (Test-Path "run.py")) {
    Write-Host "❌ Error: This script must be run from the BugSeek project root directory" -ForegroundColor Red
    Write-Host "Current directory: $PWD" -ForegroundColor Yellow
    Write-Host "Expected files: run.py, backend/, frontend/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python is not available or not in PATH" -ForegroundColor Red
    Write-Host "Please ensure Python is installed and accessible" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Confirm action
$confirm = Read-Host "Are you sure you want to clear the database? (type YES to confirm)"

if ($confirm -ne "YES") {
    Write-Host "Operation cancelled." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host ""
Write-Host "Running database clear script..." -ForegroundColor Blue
Write-Host ""

# Run the Python clear script
try {
    python clear_database.py
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host "DATABASE CLEARED SUCCESSFULLY!" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Blue
        Write-Host "  1. To load sample data: python 2_load_sample_data.py" -ForegroundColor White
        Write-Host "  2. To start fresh: python 1_initialize_database.py" -ForegroundColor White
        Write-Host "  3. To start BugSeek: python run.py" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host "DATABASE CLEAR FAILED!" -ForegroundColor Red
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please check the error messages above." -ForegroundColor Yellow
        Write-Host "You may need to:" -ForegroundColor Yellow
        Write-Host "  - Stop BugSeek if it's currently running" -ForegroundColor White
        Write-Host "  - Check file permissions" -ForegroundColor White
        Write-Host "  - Ensure you're in the correct directory" -ForegroundColor White
        Write-Host ""
    }
} catch {
    Write-Host ""
    Write-Host "❌ Failed to run clear script: $_" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to exit"
