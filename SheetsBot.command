#!/bin/bash
# SheetsBot Launcher for macOS
# Double-click this file to run SheetsBot

echo "====================================="
echo "  SheetsBot - Google Sheets Automation"
echo "====================================="
echo ""

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo ""
    echo "Please install Python 3.11 or higher from:"
    echo "https://www.python.org/downloads/macos/"
    echo ""
    echo "Or install using Homebrew:"
    echo "brew install python"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Python 3 found"
echo ""

# Run the main application
python3 SheetsBot.py "$@"

# Keep terminal open if there was an error
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Application exited with an error"
    read -p "Press Enter to exit..."
fi 