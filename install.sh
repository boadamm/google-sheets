#!/bin/bash

# SheetsBot One-Click Installation Script
# This script will install SheetsBot and all its dependencies

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="$HOME/.local/share/sheetsbot"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
REPO_URL="https://github.com/boadamm/demoproject"

# Logging function
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if running on supported OS
check_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        error "Unsupported operating system: $OSTYPE"
    fi
    log "Detected OS: $OS"
}

# Check and install dependencies
install_dependencies() {
    log "Checking dependencies..."
    
    # Check for Python 3.11+
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if (( $(echo "$PYTHON_VERSION >= 3.11" | bc -l) )); then
            log "Python $PYTHON_VERSION found"
        else
            error "Python 3.11+ required, found $PYTHON_VERSION"
        fi
    else
        error "Python 3 not found. Please install Python 3.11+"
    fi
    
    # Check for pip
    if ! command -v pip3 &> /dev/null; then
        error "pip3 not found. Please install pip3"
    fi
    
    # Check for git
    if ! command -v git &> /dev/null; then
        error "git not found. Please install git"
    fi
    
    # Install build dependencies on Linux
    if [[ "$OS" == "linux" ]]; then
        if command -v apt-get &> /dev/null; then
            log "Installing build dependencies (requires sudo)..."
            sudo apt-get update
            sudo apt-get install -y build-essential libffi-dev python3-dev python3-pip
        elif command -v yum &> /dev/null; then
            log "Installing build dependencies (requires sudo)..."
            sudo yum install -y gcc gcc-c++ libffi-devel python3-devel python3-pip
        else
            warn "Could not detect package manager. You may need to install build-essential and libffi-dev manually"
        fi
    fi
}

# Create installation directories
create_directories() {
    log "Creating installation directories..."
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    mkdir -p "$DESKTOP_DIR"
}

# Download and install SheetsBot
install_sheetsbot() {
    log "Downloading SheetsBot..."
    
    cd "$INSTALL_DIR"
    
    # Clone the repository
    if [ -d "demoproject" ]; then
        log "Updating existing installation..."
        cd demoproject
        git pull
    else
        git clone "$REPO_URL" demoproject
        cd demoproject
    fi
    
    log "Installing Python dependencies..."
    pip3 install --user -r requirements.txt
    
    # Make CLI executable
    chmod +x cli.py
}

# Create launcher scripts
create_launchers() {
    log "Creating launcher scripts..."
    
    # Create CLI launcher
    cat > "$BIN_DIR/sheetsbot" << EOF
#!/bin/bash
cd "$INSTALL_DIR/demoproject"
python3 cli.py "\$@"
EOF
    chmod +x "$BIN_DIR/sheetsbot"
    
    # Create GUI launcher
    cat > "$BIN_DIR/sheetsbot-gui" << EOF
#!/bin/bash
cd "$INSTALL_DIR/demoproject"
python3 -m app.gui.main_window
EOF
    chmod +x "$BIN_DIR/sheetsbot-gui"
    
    # Create desktop entry
    cat > "$DESKTOP_DIR/sheetsbot.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SheetsBot
Comment=Google Sheets automation tool
Exec=$BIN_DIR/sheetsbot-gui
Icon=$INSTALL_DIR/demoproject/assets/icon.png
Terminal=false
Categories=Office;Productivity;
EOF
}

# Set up configuration
setup_config() {
    log "Setting up configuration..."
    
    CONFIG_DIR="$HOME/.config/sheetsbot"
    mkdir -p "$CONFIG_DIR"
    
    # Copy default config if it doesn't exist
    if [ ! -f "$CONFIG_DIR/settings.toml" ]; then
        cp "$INSTALL_DIR/demoproject/config/settings.toml" "$CONFIG_DIR/settings.toml"
        log "Default configuration copied to $CONFIG_DIR/settings.toml"
        log "Please edit this file to configure your Google Sheets and Slack settings"
    fi
}

# Add to PATH
update_path() {
    log "Updating PATH..."
    
    # Add to .bashrc if it exists
    if [ -f "$HOME/.bashrc" ]; then
        if ! grep -q "$BIN_DIR" "$HOME/.bashrc"; then
            echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$HOME/.bashrc"
            log "Added $BIN_DIR to PATH in .bashrc"
        fi
    fi
    
    # Add to .zshrc if it exists
    if [ -f "$HOME/.zshrc" ]; then
        if ! grep -q "$BIN_DIR" "$HOME/.zshrc"; then
            echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$HOME/.zshrc"
            log "Added $BIN_DIR to PATH in .zshrc"
        fi
    fi
    
    # Add to current session
    export PATH="$BIN_DIR:$PATH"
}

# Main installation function
main() {
    echo -e "${BLUE}SheetsBot One-Click Installer${NC}"
    echo "==============================="
    
    check_os
    install_dependencies
    create_directories
    install_sheetsbot
    create_launchers
    setup_config
    update_path
    
    echo ""
    echo -e "${GREEN}✓ Installation completed successfully!${NC}"
    echo ""
    echo "Usage:"
    echo "  CLI: sheetsbot --help"
    echo "  GUI: sheetsbot-gui"
    echo ""
    echo "Configuration: $HOME/.config/sheetsbot/settings.toml"
    echo ""
    echo "To start using SheetsBot:"
    echo "1. Configure your Google Sheets API credentials"
    echo "2. Run: source ~/.bashrc (or restart your terminal)"
    echo "3. Run: sheetsbot --help"
    echo ""
    echo -e "${YELLOW}Note: You may need to restart your terminal for PATH changes to take effect${NC}"
}

# Run main function
main "$@" 