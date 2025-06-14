#!/bin/bash

echo "========================================"
echo "   Sheets Bot Desktop App Builder"
echo "========================================"

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

# Check if Python is installed
if ! command -v python &> /dev/null; then
    print_error "Python is not installed or not in PATH"
    echo "Please install Python 3.11 or later"
    exit 1
fi

print_status "Python found: $(python --version)"

# Check if conda is available
if command -v conda &> /dev/null; then
    print_info "Setting up conda environment..."
    
    # Check if environment exists
    if conda env list | grep -q "sheets-bot"; then
        print_info "Environment exists, updating..."
        conda env update -f environment.yml
    else
        print_info "Creating new conda environment..."
        conda env create -f environment.yml
    fi
    
    # Activate environment
    print_info "Activating conda environment..."
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate sheets-bot
else
    print_warning "Conda not found, using system Python with pip"
    
    # Install requirements with pip
    print_info "Installing requirements..."
    pip install -r requirements.txt
fi

# Install build dependencies
print_info "Installing build dependencies..."
pip install pyinstaller

# Clean previous builds
print_info "Cleaning previous builds..."
rm -rf dist/
rm -rf build/__pycache__/

# Build the desktop application
print_info "Building desktop application..."
if python -c "import PyQt5" 2>/dev/null || python -c "import PySide6" 2>/dev/null; then
    # Check if spec file exists
    if [[ -f "build/pyinstaller.spec" ]]; then
        pyinstaller -y build/pyinstaller.spec
    else
        print_warning "PyInstaller spec file not found, using make command..."
        make build-gui
    fi
else
    print_error "Qt libraries not found. GUI build may fail."
    print_info "Attempting build anyway..."
    if [[ -f "build/pyinstaller.spec" ]]; then
        pyinstaller -y build/pyinstaller.spec
    else
        make build-gui
    fi
fi

# Check if build was successful
if [[ -f "dist/SheetsBot/SheetsBot" ]]; then
    echo
    print_status "BUILD SUCCESSFUL!"
    echo "📁 Desktop app created at: dist/SheetsBot/SheetsBot"
    echo "📂 Full folder: $(pwd)/dist/SheetsBot/"
    echo
    echo "🚀 You can now:"
    echo "   1. Run ./dist/SheetsBot/SheetsBot directly"
    echo "   2. Create a desktop shortcut"
    echo "   3. Copy the entire SheetsBot folder anywhere"
    echo
    
    # Make sure the executable has proper permissions
    chmod +x dist/SheetsBot/SheetsBot
    
    # Ask if user wants to create desktop shortcut
    read -p "Create desktop shortcut? (y/n): " create_shortcut
    if [[ $create_shortcut =~ ^[Yy]$ ]]; then
        create_desktop_shortcut
    fi
    
    # Ask if user wants to run the app
    read -p "Run the app now? (y/n): " run_app
    if [[ $run_app =~ ^[Yy]$ ]]; then
        print_info "Launching Sheets Bot..."
        # For WSL2, we might need to set DISPLAY
        if [[ -n "$WSL_DISTRO_NAME" ]]; then
            export DISPLAY=:0
        fi
        ./dist/SheetsBot/SheetsBot &
    fi
else
    echo
    print_error "BUILD FAILED!"
    echo "Check the output above for errors."
    
    # Provide troubleshooting info
    echo
    print_info "Troubleshooting tips:"
    echo "1. Make sure all dependencies are installed: pip install -r requirements.txt"
    echo "2. Check if Qt libraries are available: python -c 'import PySide6'"
    echo "3. For WSL2, you might need X11 forwarding or Windows X server"
    exit 1
fi

# Function to create desktop shortcut
create_desktop_shortcut() {
    echo
    print_info "Creating desktop shortcut..."
    
    # Get desktop directory
    if [[ -n "$WSL_DISTRO_NAME" ]]; then
        # WSL2 - try to get Windows desktop
        DESKTOP_DIR="/mnt/c/Users/$USER/Desktop"
        if [[ ! -d "$DESKTOP_DIR" ]]; then
            # Fallback to Linux desktop
            DESKTOP_DIR="$HOME/Desktop"
        fi
    else
        # Native Linux
        DESKTOP_DIR="$HOME/Desktop"
    fi
    
    # Create desktop directory if it doesn't exist
    mkdir -p "$DESKTOP_DIR"
    
    # Create .desktop file
    DESKTOP_FILE="$DESKTOP_DIR/SheetsBot.desktop"
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Sheets Bot
Comment=Desktop application for Google Sheets automation
Exec=$(pwd)/dist/SheetsBot/SheetsBot
Icon=$(pwd)/dist/SheetsBot/icon.png
Terminal=false
StartupNotify=true
Categories=Office;Productivity;
EOF
    
    # Make desktop file executable
    chmod +x "$DESKTOP_FILE"
    
    if [[ -f "$DESKTOP_FILE" ]]; then
        print_status "Desktop shortcut created: $DESKTOP_FILE"
        
        # For WSL2, also create Windows shortcut
        if [[ -n "$WSL_DISTRO_NAME" ]]; then
            create_windows_shortcut
        fi
    else
        print_error "Failed to create desktop shortcut"
    fi
}

# Function to create Windows shortcut (for WSL2)
create_windows_shortcut() {
    print_info "Creating Windows shortcut for WSL2..."
    
    # Get Windows username
    WIN_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r\n')
    WIN_DESKTOP="/mnt/c/Users/$WIN_USER/Desktop"
    
    if [[ -d "$WIN_DESKTOP" ]]; then
        # Create PowerShell script to make Windows shortcut
        PS_SCRIPT=$(mktemp --suffix=.ps1)
        
        cat > "$PS_SCRIPT" << 'EOF'
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Sheets Bot.lnk")
$Shortcut.TargetPath = "wsl.exe"
$Shortcut.Arguments = "-d Ubuntu -e bash -c 'cd /home/$env:USER/demoproject && ./dist/SheetsBot/SheetsBot'"
$Shortcut.WorkingDirectory = "$env:USERPROFILE"
$Shortcut.Description = "Sheets Bot Desktop Application (WSL2)"
$Shortcut.Save()
EOF
        
        # Execute PowerShell script
        powershell.exe -ExecutionPolicy Bypass -File "$(wslpath -w "$PS_SCRIPT")" 2>/dev/null
        
        # Clean up
        rm "$PS_SCRIPT"
        
        if [[ -f "$WIN_DESKTOP/Sheets Bot.lnk" ]]; then
            print_status "Windows shortcut created on Desktop"
        fi
    fi
}

echo
print_status "Desktop app builder completed!" 