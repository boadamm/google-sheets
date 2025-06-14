@echo off
REM SheetsBot One-Click Installation Script for Windows
REM This script will install SheetsBot and all its dependencies

setlocal enabledelayedexpansion

REM Configuration
set "INSTALL_DIR=%USERPROFILE%\AppData\Local\SheetsBot"
set "BIN_DIR=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps"
set "REPO_URL=https://github.com/boadamm/demoproject"

echo.
echo SheetsBot One-Click Installer for Windows
echo ========================================
echo.

REM Check for Python
echo [INFO] Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.11+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%v"
echo [INFO] Found Python %PYTHON_VERSION%

REM Check for pip
echo [INFO] Checking for pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip not found. Please reinstall Python with pip
    pause
    exit /b 1
)

REM Check for git
echo [INFO] Checking for git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] git not found. Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

REM Create installation directory
echo [INFO] Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Download and install SheetsBot
echo [INFO] Downloading SheetsBot...
cd /d "%INSTALL_DIR%"

if exist "demoproject" (
    echo [INFO] Updating existing installation...
    cd demoproject
    git pull
) else (
    git clone %REPO_URL% demoproject
    cd demoproject
)

REM Install Python dependencies
echo [INFO] Installing Python dependencies...
pip install --user -r requirements.txt

REM Create launcher scripts
echo [INFO] Creating launcher scripts...

REM Create CLI launcher
echo @echo off > "%BIN_DIR%\sheetsbot.bat"
echo cd /d "%INSTALL_DIR%\demoproject" >> "%BIN_DIR%\sheetsbot.bat"
echo python cli.py %%* >> "%BIN_DIR%\sheetsbot.bat"

REM Create GUI launcher
echo @echo off > "%BIN_DIR%\sheetsbot-gui.bat"
echo cd /d "%INSTALL_DIR%\demoproject" >> "%BIN_DIR%\sheetsbot-gui.bat"
echo python -m app.gui.main_window >> "%BIN_DIR%\sheetsbot-gui.bat"

REM Create desktop shortcut
echo [INFO] Creating desktop shortcut...
set "DESKTOP=%USERPROFILE%\Desktop"
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\SheetsBot.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%BIN_DIR%\sheetsbot-gui.bat" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%INSTALL_DIR%\demoproject" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "SheetsBot - Google Sheets Automation Tool" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"
cscript "%TEMP%\CreateShortcut.vbs" >nul
del "%TEMP%\CreateShortcut.vbs"

REM Set up configuration
echo [INFO] Setting up configuration...
set "CONFIG_DIR=%USERPROFILE%\.config\sheetsbot"
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

if not exist "%CONFIG_DIR%\settings.toml" (
    copy "%INSTALL_DIR%\demoproject\config\settings.toml" "%CONFIG_DIR%\settings.toml" >nul
    echo [INFO] Default configuration copied to %CONFIG_DIR%\settings.toml
    echo [INFO] Please edit this file to configure your Google Sheets and Slack settings
)

echo.
echo [SUCCESS] Installation completed successfully!
echo.
echo Usage:
echo   CLI: sheetsbot --help
echo   GUI: sheetsbot-gui
echo   Desktop: Double-click SheetsBot shortcut on desktop
echo.
echo Configuration: %CONFIG_DIR%\settings.toml
echo.
echo To start using SheetsBot:
echo 1. Configure your Google Sheets API credentials
echo 2. Open a new Command Prompt or PowerShell window
echo 3. Run: sheetsbot --help
echo.
echo Press any key to exit...
pause >nul 