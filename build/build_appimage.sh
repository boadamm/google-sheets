#!/bin/bash

echo "========================================"
echo "   SheetsBot AppImage Builder"
echo "========================================"

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

# Check if we have the PyInstaller build
if [[ ! -d "dist/SheetsBot" ]]; then
    print_error "PyInstaller build not found. Please run build_desktop_app.sh first"
    exit 1
fi

# Create AppDir structure
print_info "Creating AppDir structure..."
APPDIR="SheetsBot.AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR"

# Copy the application
print_info "Copying application files..."
cp -r dist/SheetsBot/* "$APPDIR/"

# Create desktop file
print_info "Creating desktop file..."
cat > "$APPDIR/SheetsBot.desktop" << EOF
[Desktop Entry]
Type=Application
Name=SheetsBot
Comment=Desktop application for Google Sheets automation
Exec=SheetsBot
Icon=sheetsbot
StartupNotify=true
Categories=Office;Productivity;
EOF

# Create a simple icon if none exists
if [[ ! -f "$APPDIR/sheetsbot.png" ]]; then
    print_info "Creating default icon..."
    # Create a simple 64x64 PNG icon using ImageMagick (if available)
    if command -v convert &> /dev/null; then
        convert -size 64x64 xc:lightblue -font Arial -pointsize 10 -fill black -gravity center -annotate +0+0 "SB" "$APPDIR/sheetsbot.png"
    else
        # Create a basic icon placeholder
        echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" | base64 -d > "$APPDIR/sheetsbot.png"
    fi
fi

# Make the main executable file... executable
chmod +x "$APPDIR/SheetsBot"

# Download and set up AppImageTool
APPIMAGE_TOOL="appimagetool-x86_64.AppImage"
if [[ ! -f "$APPIMAGE_TOOL" ]]; then
    print_info "Downloading AppImageTool..."
    wget -O "$APPIMAGE_TOOL" "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "$APPIMAGE_TOOL"
fi

# Build the AppImage
print_info "Building AppImage..."
ARCH=x86_64 ./"$APPIMAGE_TOOL" "$APPDIR" SheetsBot-x86_64.AppImage

if [[ -f "SheetsBot-x86_64.AppImage" ]]; then
    print_status "AppImage created successfully!"
    echo "📁 AppImage: $(pwd)/SheetsBot-x86_64.AppImage"
    echo "📂 Size: $(du -h SheetsBot-x86_64.AppImage | cut -f1)"
    echo
    echo "🚀 Users can now run: ./SheetsBot-x86_64.AppImage"
    echo "   Or make it executable and double-click in file manager"
    
    # Make it executable
    chmod +x SheetsBot-x86_64.AppImage
    
    # Clean up
    rm -rf "$APPDIR"
    
    print_info "AppImage is ready for distribution!"
else
    print_error "AppImage build failed!"
    exit 1
fi 