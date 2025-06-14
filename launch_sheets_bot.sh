#!/bin/bash

# Simple launcher for Sheets Bot Desktop App
# This script can be used as a desktop shortcut

echo "🚀 Launching Sheets Bot..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_PATH="$SCRIPT_DIR/dist/SheetsBot/SheetsBot"

# Check if the app exists
if [[ ! -f "$APP_PATH" ]]; then
    echo "❌ Sheets Bot not found at: $APP_PATH"
    echo "🔨 Building the app first..."
    
    # Change to script directory and build
    cd "$SCRIPT_DIR"
    ./build_desktop_app.sh
    
    # Recheck if app exists after build
    if [[ ! -f "$APP_PATH" ]]; then
        echo "❌ Build failed. Cannot launch Sheets Bot."
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# For WSL2, set up display
if [[ -n "$WSL_DISTRO_NAME" ]]; then
    export DISPLAY=:0
    echo "🔧 WSL2 detected, setting DISPLAY=:0"
fi

# Launch the application
echo "✅ Starting Sheets Bot Desktop App..."
"$APP_PATH" &

# Optional: Show process info
echo "📱 Sheets Bot is running (PID: $!)"
echo "ℹ️  Close this terminal or press Ctrl+C to continue"

# Keep the launcher running for a moment to show any startup messages
sleep 2 