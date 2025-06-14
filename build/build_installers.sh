#!/bin/bash

echo "========================================"
echo "   SheetsBot Multi-Platform Installer Builder"
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

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

# Get version from git tag or set default
VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v1.0.0")
VERSION_NO_V=${VERSION#v}

print_info "Building installers for version: $VERSION"

# Create build output directory
BUILD_OUTPUT="build_output"
mkdir -p "$BUILD_OUTPUT"

# Function to build Windows installer
build_windows_installer() {
    print_info "Building Windows installer..."
    
    # Check if NSIS is available
    if ! command -v makensis &> /dev/null; then
        print_warning "NSIS not found. Skipping Windows installer."
        print_info "To build Windows installer, install NSIS: https://nsis.sourceforge.io/"
        return 1
    fi
    
    # Create license file if it doesn't exist
    if [[ ! -f "LICENSE.txt" ]]; then
        echo "MIT License - Copyright (c) 2024 SheetsBot" > LICENSE.txt
    fi
    
    # Build with NSIS
    makensis build/installer.nsi
    
    if [[ -f "SheetsBot-Setup.exe" ]]; then
        mv "SheetsBot-Setup.exe" "$BUILD_OUTPUT/SheetsBot-Setup-${VERSION_NO_V}.exe"
        print_status "Windows installer created: $BUILD_OUTPUT/SheetsBot-Setup-${VERSION_NO_V}.exe"
        return 0
    else
        print_error "Windows installer build failed"
        return 1
    fi
}

# Function to build Linux AppImage
build_linux_appimage() {
    print_info "Building Linux AppImage..."
    
    if [[ ! -f "build/build_appimage.sh" ]]; then
        print_error "AppImage build script not found"
        return 1
    fi
    
    # Run the AppImage builder
    bash build/build_appimage.sh
    
    if [[ -f "SheetsBot-x86_64.AppImage" ]]; then
        mv "SheetsBot-x86_64.AppImage" "$BUILD_OUTPUT/SheetsBot-${VERSION_NO_V}-x86_64.AppImage"
        print_status "Linux AppImage created: $BUILD_OUTPUT/SheetsBot-${VERSION_NO_V}-x86_64.AppImage"
        return 0
    else
        print_error "Linux AppImage build failed"
        return 1
    fi
}

# Function to create Debian package
build_debian_package() {
    print_info "Building Debian package..."
    
    # Create debian package structure
    DEB_DIR="sheetsbot-${VERSION_NO_V}"
    mkdir -p "$DEB_DIR/DEBIAN"
    mkdir -p "$DEB_DIR/usr/bin"
    mkdir -p "$DEB_DIR/usr/share/applications"
    mkdir -p "$DEB_DIR/usr/share/icons/hicolor/64x64/apps"
    
    # Copy application files
    if [[ -d "dist/SheetsBot" ]]; then
        cp -r dist/SheetsBot "$DEB_DIR/usr/share/sheetsbot"
        
        # Create wrapper script
        cat > "$DEB_DIR/usr/bin/sheetsbot" << 'EOF'
#!/bin/bash
cd /usr/share/sheetsbot
exec ./SheetsBot "$@"
EOF
        chmod +x "$DEB_DIR/usr/bin/sheetsbot"
        
        # Create desktop file
        cat > "$DEB_DIR/usr/share/applications/sheetsbot.desktop" << EOF
[Desktop Entry]
Type=Application
Name=SheetsBot
Comment=Desktop application for Google Sheets automation
Exec=sheetsbot
Icon=sheetsbot
StartupNotify=true
Categories=Office;Productivity;
EOF
        
        # Create control file
        cat > "$DEB_DIR/DEBIAN/control" << EOF
Package: sheetsbot
Version: ${VERSION_NO_V}
Section: office
Priority: optional
Architecture: amd64
Maintainer: SheetsBot <support@sheetsbot.com>
Description: Desktop application for Google Sheets automation
 SheetsBot is a powerful desktop application that allows you to
 automate Google Sheets operations with an intuitive GUI interface.
EOF
        
        # Build the package
        dpkg-deb --build "$DEB_DIR" "$BUILD_OUTPUT/sheetsbot-${VERSION_NO_V}_amd64.deb"
        
        # Clean up
        rm -rf "$DEB_DIR"
        
        if [[ -f "$BUILD_OUTPUT/sheetsbot-${VERSION_NO_V}_amd64.deb" ]]; then
            print_status "Debian package created: $BUILD_OUTPUT/sheetsbot-${VERSION_NO_V}_amd64.deb"
            return 0
        fi
    fi
    
    print_error "Debian package build failed"
    return 1
}

# Function to create portable ZIP archives
create_portable_archives() {
    print_info "Creating portable archives..."
    
    if [[ -d "dist/SheetsBot" ]]; then
        # Windows portable
        cd dist
        zip -r "../$BUILD_OUTPUT/SheetsBot-${VERSION_NO_V}-Windows-Portable.zip" SheetsBot/
        cd ..
        print_status "Windows portable archive created: $BUILD_OUTPUT/SheetsBot-${VERSION_NO_V}-Windows-Portable.zip"
        
        # Linux portable (same content, different name)
        cd dist
        tar -czf "../$BUILD_OUTPUT/SheetsBot-${VERSION_NO_V}-Linux-Portable.tar.gz" SheetsBot/
        cd ..
        print_status "Linux portable archive created: $BUILD_OUTPUT/SheetsBot-${VERSION_NO_V}-Linux-Portable.tar.gz"
        
        return 0
    else
        print_error "No build found in dist/SheetsBot"
        return 1
    fi
}

# Main build process
print_info "Starting multi-platform build process..."

# Check if we have a PyInstaller build
if [[ ! -d "dist/SheetsBot" ]]; then
    print_error "PyInstaller build not found. Please run build_desktop_app.sh first"
    exit 1
fi

# Build all installers
WINDOWS_SUCCESS=0
LINUX_SUCCESS=0
DEBIAN_SUCCESS=0
PORTABLE_SUCCESS=0

# Build Windows installer
if build_windows_installer; then
    WINDOWS_SUCCESS=1
fi

# Build Linux AppImage
if build_linux_appimage; then
    LINUX_SUCCESS=1
fi

# Build Debian package (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if build_debian_package; then
        DEBIAN_SUCCESS=1
    fi
fi

# Create portable archives
if create_portable_archives; then
    PORTABLE_SUCCESS=1
fi

# Summary
echo
echo "========================================"
echo "   BUILD SUMMARY"
echo "========================================"

echo "Windows Installer: $([ $WINDOWS_SUCCESS -eq 1 ] && echo -e "${GREEN}✅ Success${NC}" || echo -e "${RED}❌ Failed${NC}")"
echo "Linux AppImage: $([ $LINUX_SUCCESS -eq 1 ] && echo -e "${GREEN}✅ Success${NC}" || echo -e "${RED}❌ Failed${NC}")"
echo "Debian Package: $([ $DEBIAN_SUCCESS -eq 1 ] && echo -e "${GREEN}✅ Success${NC}" || echo -e "${RED}❌ Failed${NC}")"
echo "Portable Archives: $([ $PORTABLE_SUCCESS -eq 1 ] && echo -e "${GREEN}✅ Success${NC}" || echo -e "${RED}❌ Failed${NC}")"

echo
print_info "All installer files are in: $BUILD_OUTPUT/"
ls -la "$BUILD_OUTPUT/"

echo
print_info "Upload these files to your GitHub release!"
echo "Users can now download and install SheetsBot easily on any platform." 