# SheetsBot Installation Guide

Choose the installation method that works best for your operating system:

## 🖥️ Windows Installation

### Option 1: Windows Installer (Recommended)
1. Download `SheetsBot-Setup-vX.X.X.exe` from the [latest release](https://github.com/baranozck/demoproject/releases/latest)
2. Double-click the installer
3. Follow the installation wizard
4. Launch SheetsBot from Start Menu or Desktop shortcut

**Features:**
- ✅ Automatic installation to Program Files
- ✅ Start Menu shortcuts
- ✅ Desktop shortcut (optional)
- ✅ Uninstaller in Add/Remove Programs
- ✅ No Python installation required

### Option 2: Portable Version
1. Download `SheetsBot-vX.X.X-Windows-Portable.zip`
2. Extract to any folder
3. Run `SheetsBot.exe` from the extracted folder

**Features:**
- ✅ No installation required
- ✅ Run from USB drive
- ✅ No admin rights needed

---

## 🐧 Linux Installation

### Option 1: AppImage (Recommended)
1. Download `SheetsBot-vX.X.X-x86_64.AppImage`
2. Make it executable: `chmod +x SheetsBot-vX.X.X-x86_64.AppImage`
3. Double-click or run: `./SheetsBot-vX.X.X-x86_64.AppImage`

**Features:**
- ✅ Runs on most Linux distributions
- ✅ No installation required
- ✅ Self-contained

### Option 2: Debian Package (Ubuntu/Debian)
```bash
# Download the .deb file
wget https://github.com/baranozck/demoproject/releases/latest/download/sheetsbot-vX.X.X_amd64.deb

# Install
sudo dpkg -i sheetsbot-vX.X.X_amd64.deb

# If dependencies are missing, fix them
sudo apt-get install -f

# Launch
sheetsbot
```

**Features:**
- ✅ System integration
- ✅ Desktop shortcut
- ✅ Command line access
- ✅ Proper uninstallation

### Option 3: Portable Archive
```bash
# Download and extract
wget https://github.com/baranozck/demoproject/releases/latest/download/SheetsBot-vX.X.X-Linux-Portable.tar.gz
tar -xzf SheetsBot-vX.X.X-Linux-Portable.tar.gz

# Run
cd SheetsBot
./SheetsBot
```

---

## 🔧 Build from Source

If you want to build from source or contribute to development:

### Prerequisites
- Python 3.11+
- Git

### Build Steps
```bash
# Clone the repository
git clone https://github.com/baranozck/demoproject.git
cd demoproject

# Set up environment
conda env create -f environment.yml
conda activate demoproject

# Build desktop application
make build-gui

# Build all installers (optional)
make build-installers
```

---

## 🎯 Quick Start After Installation

1. **First Launch**: SheetsBot will open with a welcome screen
2. **Google Sheets Setup**: Configure your Google Sheets API credentials
3. **Test Connection**: Use the "Test" button to verify everything works
4. **Start Automating**: Upload CSV/Excel files or use the file watcher

---

## 🆘 Troubleshooting

### Windows Issues

**"Windows protected your PC" message:**
- Click "More info" → "Run anyway"
- This happens because the installer isn't code-signed yet

**App won't start:**
- Right-click → "Run as administrator"
- Check Windows Defender/antivirus isn't blocking it

### Linux Issues

**AppImage won't run:**
```bash
# Install FUSE if missing
sudo apt install fuse libfuse2

# Or run with --appimage-extract-and-run
./SheetsBot-vX.X.X-x86_64.AppImage --appimage-extract-and-run
```

**Permission denied:**
```bash
# Make sure the file is executable
chmod +x SheetsBot-vX.X.X-x86_64.AppImage
```

### General Issues

**Missing dependencies:**
- Download the "Portable" version which includes all dependencies
- Or install Python 3.11+ and run from source

**Google Sheets API errors:**
- Follow the [API Setup Guide](API_SETUP_GUIDE.md)
- Make sure credentials.json is in the config folder

---

## 🔄 Updates

### Automatic Updates (Coming Soon)
- SheetsBot will check for updates automatically
- You'll be notified when new versions are available

### Manual Updates
1. Download the latest version from [releases](https://github.com/baranozck/demoproject/releases/latest)
2. Uninstall old version (Windows) or replace files (Linux/Portable)
3. Install new version

---

## 📞 Support

Need help? Here are your options:

1. **Documentation**: Check the [docs folder](docs/) for detailed guides
2. **Issues**: Report bugs on [GitHub Issues](https://github.com/baranozck/demoproject/issues)
3. **Discussions**: Ask questions in [GitHub Discussions](https://github.com/baranozck/demoproject/discussions)

---

## 📋 System Requirements

**Minimum:**
- Windows 10+ or Linux (any modern distribution)
- 4GB RAM
- 500MB disk space
- Internet connection for Google Sheets API

**Recommended:**
- Windows 11 or Ubuntu 20.04+
- 8GB RAM
- 1GB disk space
- Stable internet connection

---

*Last updated: January 2024* 