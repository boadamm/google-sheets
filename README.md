# 🤖 SheetsBot - Google Sheets Automation Tool

**Simple, powerful automation for Google Sheets with file monitoring and Slack notifications.**

## ⚡ Quick Start

### 🖱️ **One-Click Launch** (Recommended)
1. **Download** the latest release
2. **Double-click** `SheetsBot.py` 
3. **Done!** The app will automatically install dependencies and launch

### 📋 Manual Installation
```bash
# 1. Install Python 3.11 or higher
# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python SheetsBot.py
```

## 🛠️ Setup (First Time Only)

### 1. **Google Sheets API Setup**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sheets API
4. Create service account credentials
5. Download the JSON key file
6. Copy it as `config/creds.json`

### 2. **Configuration**
- Copy `config/creds.example.json` to `config/creds.json`
- Add your Google Sheets credentials
- Edit `config/settings.toml` for your preferences

## 🚀 Features

### 📊 **File Processing**
- **Auto-detect** CSV and Excel files
- **Clean and standardize** data automatically
- **Push to Google Sheets** with one click

### 👀 **File Monitoring** 
- **Watch folders** for new files
- **Process automatically** when files are added
- **Real-time notifications** via Slack

### 🖥️ **Two Interfaces**
- **GUI**: Easy point-and-click interface
- **CLI**: Command-line for automation and scripting

## 📖 Usage Examples

### GUI Mode (Default)
```bash
python SheetsBot.py
```
Click through the intuitive interface to:
- Process single files
- Set up folder monitoring
- Configure settings

### CLI Mode
```bash
# Process a single file
python SheetsBot.py --file data.csv --push

# Watch a folder for changes
python SheetsBot.py --watch --folder ./incoming

# Get help
python SheetsBot.py --help
```

### File Processing
Place your CSV or Excel files in the `samples/` folder or any folder you're monitoring. SheetsBot will:
1. **Parse** the file automatically
2. **Clean** the data (remove duplicates, standardize formats)
3. **Upload** to your Google Sheet
4. **Notify** you via Slack (if configured)

## 📁 Project Structure

```
SheetsBot/
├── SheetsBot.py          # 👆 Main launcher - double-click to run!
├── src/                  # Application code
├── config/               # Configuration files
├── samples/              # Example data files
├── watch/                # Default folder for monitoring
├── README.md             # This file
├── LICENSE               # Open source license
└── requirements.txt      # Dependencies
```

## ⚙️ Configuration Files

- **`config/creds.json`** - Google Sheets API credentials (you create this)
- **`config/settings.toml`** - Application settings (Slack, folders, etc.)
- **`samples/`** - Place your test files here

## 🆘 Troubleshooting

### Common Issues

**"Module not found" errors**
- Run: `pip install -r requirements.txt`
- Or just run `SheetsBot.py` - it auto-installs dependencies

**"Credentials not found"**
- Make sure `config/creds.json` exists with your Google API credentials
- See INSTALLATION.md for detailed setup

**"Permission denied"**
- Make sure your Google service account has access to your spreadsheet
- Share the spreadsheet with the service account email

### Need Help?
- Check `INSTALLATION.md` for detailed setup instructions
- Look at `samples/` for example files
- All features work without configuration in demo mode

## 📄 License

MIT License - Feel free to use, modify, and distribute!

---

**🎯 Ready to automate your Google Sheets workflow?**  
**Just double-click `SheetsBot.py` and get started!** 
