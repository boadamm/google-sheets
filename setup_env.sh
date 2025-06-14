#!/bin/bash

# Sheets Bot Environment Setup Script
# This script helps you create your .env file and verify your setup

echo "🔑 Sheets Bot Environment Setup"
echo "================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

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

# Check if .env already exists
if [[ -f ".env" ]]; then
    print_warning ".env file already exists"
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [[ $overwrite != "y" ]]; then
        echo "Setup cancelled. Use 'nano .env' to edit manually."
        exit 0
    fi
fi

# Copy template to .env
if [[ -f "env.template" ]]; then
    cp env.template .env
    print_status ".env file created from template"
else
    print_error "env.template not found. Please make sure you're in the project directory."
    exit 1
fi

echo
print_info "Your .env file has been created. Now you need to fill in your API keys."
echo

echo "📋 What you need to do next:"
echo
echo "1. 🔗 Google Sheets API Setup:"
echo "   - Go to: https://console.cloud.google.com/"
echo "   - Enable Google Sheets API"
echo "   - Create a Service Account"
echo "   - Download the JSON credentials"
echo "   - Save as: config/creds.json"
echo
echo "2. 📝 Edit your .env file:"
echo "   - Open: nano .env"
echo "   - Fill in your Google API credentials"
echo "   - Add your Google Spreadsheet ID"
echo
echo "3. 💬 Optional - Slack Setup:"
echo "   - Go to: https://api.slack.com/messaging/webhooks"
echo "   - Create an incoming webhook"
echo "   - Add the webhook URL to .env"
echo

# Check if config directory exists
if [[ ! -d "config" ]]; then
    mkdir -p config
    print_status "Created config directory"
fi

# Check if example credentials exist
if [[ -f "config/creds.example.json" ]] && [[ ! -f "config/creds.json" ]]; then
    print_warning "Found creds.example.json but no creds.json"
    read -p "Copy example file to creds.json? (y/n): " copy_creds
    if [[ $copy_creds == "y" ]]; then
        cp config/creds.example.json config/creds.json
        print_status "Copied creds.example.json to creds.json"
        print_warning "Remember to replace the example values with your actual credentials!"
    fi
fi

echo
print_info "For detailed instructions, see: API_SETUP_GUIDE.md"
echo

# Offer to open the .env file for editing
read -p "Open .env file for editing now? (y/n): " edit_now
if [[ $edit_now == "y" ]]; then
    if command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    elif command -v code &> /dev/null; then
        code .env
    else
        print_info "Please edit .env file manually with your preferred editor"
    fi
fi

echo
echo "🧪 Test your setup with:"
echo "   python cli.py --file samples/data.csv --push"
echo
print_status "Setup complete! Check API_SETUP_GUIDE.md for detailed instructions." 