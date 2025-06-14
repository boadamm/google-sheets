@echo off
echo ========================================
echo    Sheets Bot Desktop App Builder
echo ========================================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or later from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
python --version

:: Create conda environment if it doesn't exist
echo.
echo 📦 Setting up conda environment...
call conda env list | findstr "sheets-bot" >nul
if errorlevel 1 (
    echo Creating new conda environment...
    call conda env create -f environment.yml
) else (
    echo Environment already exists, updating...
    call conda env update -f environment.yml
)

:: Activate environment
echo.
echo 🔄 Activating conda environment...
call conda activate sheets-bot

:: Install build dependencies
echo.
echo 📋 Installing build dependencies...
pip install pyinstaller

:: Clean previous builds
echo.
echo 🧹 Cleaning previous builds...
rmdir /s /q dist 2>nul
rmdir /s /q build\__pycache__ 2>nul

:: Build the desktop application
echo.
echo 🔨 Building desktop application...
pyinstaller -y build/pyinstaller.spec

:: Check if build was successful
if exist "dist\SheetsBot\SheetsBot.exe" (
    echo.
    echo ✅ BUILD SUCCESSFUL!
    echo 📁 Desktop app created at: dist\SheetsBot\SheetsBot.exe
    echo 📂 Full folder: %CD%\dist\SheetsBot\
    echo.
    echo 🚀 You can now:
    echo    1. Run SheetsBot.exe directly
    echo    2. Create a desktop shortcut
    echo    3. Copy the entire SheetsBot folder anywhere
    echo.
    
    :: Ask if user wants to create desktop shortcut
    set /p create_shortcut="Create desktop shortcut? (y/n): "
    if /i "%create_shortcut%"=="y" (
        call :create_desktop_shortcut
    )
    
    :: Ask if user wants to run the app
    set /p run_app="Run the app now? (y/n): "
    if /i "%run_app%"=="y" (
        start "" "dist\SheetsBot\SheetsBot.exe"
    )
) else (
    echo.
    echo ❌ BUILD FAILED!
    echo Check the output above for errors.
)

echo.
pause
exit /b 0

:create_desktop_shortcut
echo.
echo 🔗 Creating desktop shortcut...

:: Get desktop path
for /f "tokens=3*" %%a in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop 2^>nul') do set desktop_path=%%a %%b

:: Create VBS script to make shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > temp_shortcut.vbs
echo sLinkFile = "%desktop_path%\Sheets Bot.lnk" >> temp_shortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> temp_shortcut.vbs
echo oLink.TargetPath = "%CD%\dist\SheetsBot\SheetsBot.exe" >> temp_shortcut.vbs
echo oLink.WorkingDirectory = "%CD%\dist\SheetsBot" >> temp_shortcut.vbs
echo oLink.Description = "Sheets Bot Desktop Application" >> temp_shortcut.vbs
echo oLink.Save >> temp_shortcut.vbs

:: Execute VBS script
cscript temp_shortcut.vbs >nul 2>&1

:: Clean up
del temp_shortcut.vbs >nul 2>&1

if exist "%desktop_path%\Sheets Bot.lnk" (
    echo ✅ Desktop shortcut created: %desktop_path%\Sheets Bot.lnk
) else (
    echo ❌ Failed to create desktop shortcut
)

goto :eof 