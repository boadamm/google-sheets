@echo off
echo =====================================
echo   SheetsBot - Google Sheets Automation
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo.
    echo Please install Python 3.11 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Run the main application
python SheetsBot.py %*

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo ❌ Application exited with an error
    pause
) 