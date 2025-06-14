# 🤖 SheetsBot - Google Sheets Automation Tool

**The easiest way to automate Google Sheets with file monitoring, Slack notifications, and a beautiful GUI setup wizard.**

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/boadamm/google-sheets/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#-platform-support)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🚀 What SheetsBot Does

SheetsBot automatically processes your CSV and Excel files and uploads them to Google Sheets with optional Slack notifications. **No technical knowledge required** - everything is configured through a beautiful, user-friendly interface!

### ✨ **Key Features:**
- 🖥️ **Beautiful GUI Setup Wizard** - Configure everything without editing files
- 📊 **Smart File Processing** - Automatically clean and upload CSV/Excel files
- 👀 **Real-time File Monitoring** - Watch folders and process files automatically
- 💬 **Slack Notifications** - Get notified when files are processed
- ⚡ **One-Click Installation** - No technical setup required
- 🔧 **Test Your Setup** - Built-in testing for Google Sheets and Slack
- 🖱️ **Two Modes** - GUI for easy use, CLI for automation

---

## ⚡ Quick Start (3 Steps)

### 🖱️ **Step 1: Download & Launch**
1. **Download** the latest release from [GitHub Releases](https://github.com/boadamm/google-sheets/releases)
2. **Extract** the ZIP file to any folder
3. **Double-click** your platform's launcher:
   - **Windows**: `SheetsBot.bat`
   - **macOS**: `SheetsBot.command`
   - **Linux**: `SheetsBot.py`

### ⚙️ **Step 2: Configure APIs (Easy!)**
When the app opens, go to the **⚙️ Configuration** tab and follow the setup wizard:

**Google Sheets Setup (Required):**
1. The app provides step-by-step instructions with clickable links
2. Get your Google Sheets API credentials (free)
3. Paste them into the configuration form
4. Test your connection with one click

**Slack Notifications Setup (Optional):**
1. Get a Slack webhook URL (if you want notifications)
2. Paste it into the Slack section
3. Customize your bot settings
4. Test your Slack integration

### 📁 **Step 3: Start Using!**
- **Manual Sync**: Upload files instantly with the Manual Sync tab
- **Auto Monitoring**: Set up folder watching with the Watcher tab
- **See Real-time Logs**: Monitor everything in the built-in log panel

**That's it! No config files to edit, no command line required.**

---

## 🖥️ **Platform Support**

| Platform | Launcher | Requirements |
|----------|----------|-------------|
| **Windows 10/11** | `SheetsBot.bat` | Python 3.11+ (auto-installed) |
| **macOS 10.15+** | `SheetsBot.command` | Python 3 (pre-installed) |
| **Linux (Ubuntu/Debian)** | `SheetsBot.py` | Python 3.11+ |

### **Platform Notes:**
- **Windows**: Automatically installs Python and dependencies if needed
- **macOS**: Uses built-in Python 3, right-click → "Open" on first run
- **Linux**: Requires `python3` and `pip3` (usually pre-installed)

---

## 📊 **How It Works**

### **File Processing Magic**
SheetsBot automatically:
1. **Detects** CSV and Excel files (.csv, .xlsx, .xls)
2. **Cleans** your data (removes empty rows/columns, standardizes formatting)
3. **Uploads** to your Google Sheet with proper formatting
4. **Tracks changes** and shows you what was added/updated/deleted
5. **Notifies** you via Slack (if configured)

### **Two Powerful Modes**

#### 🖱️ **GUI Mode (Recommended for Most Users)**
- **⚙️ Configuration Tab**: Easy setup wizard for APIs
- **📄 Manual Sync Tab**: Drag & drop or browse to upload files
- **👀 Watcher Tab**: Set up automatic folder monitoring
- **📋 Live Logs**: See everything happening in real-time

#### 💻 **CLI Mode (For Automation & Scripts)**
```bash
# Process a single file
python SheetsBot.py --file data.csv --push

# Watch a folder for new files
python SheetsBot.py --watch --folder ./incoming

# See all options
python SheetsBot.py --help
```

---

## 🛠️ **Complete Setup Guide**

### **Google Sheets API Setup (Required)**

**Don't worry - the GUI walks you through this with clickable links!**

1. **Go to Google Cloud Console**: [console.cloud.google.com](https://console.cloud.google.com/)
2. **Create/Select Project**: Choose or create a project
3. **Enable API**: Enable "Google Sheets API"
4. **Create Service Account**: 
   - Go to "Credentials" → "Create Credentials" → "Service Account"
   - Download the JSON key file
5. **Share Your Sheet**: Share your Google Sheet with the service account email
6. **Configure in App**: Paste the credentials into SheetsBot's Configuration tab

### **Slack Notifications Setup (Optional)**

**Want to get notified when files are processed? Set up Slack!**

1. **Get Webhook URL**: 
   - Go to your Slack workspace settings
   - Create an [Incoming Webhook](https://api.slack.com/messaging/webhooks)
   - Choose your notification channel
   - Copy the webhook URL
2. **Configure in App**: Paste the webhook URL into SheetsBot's Slack section
3. **Test**: Use the "Test Slack Notification" button to verify it works

---

## 🎯 **Usage Examples**

### **Scenario 1: Process Sales Data Weekly**
1. **Setup**: Configure Google Sheets API once
2. **Use Manual Sync**: Every week, use the Manual Sync tab to upload your sales CSV
3. **Result**: Clean, formatted data in your Google Sheet + Slack notification to your team

### **Scenario 2: Real-time Data Monitoring**
1. **Setup**: Configure both Google Sheets and Slack
2. **Use Watcher**: Set the Watcher tab to monitor your data export folder
3. **Result**: Any new CSV/Excel file is automatically processed and your team gets notified

### **Scenario 3: Batch Processing**
1. **Setup**: Use CLI mode for scripting
2. **Script**: Automate with `python SheetsBot.py --watch --folder ./data`
3. **Result**: Hands-off processing of multiple files

---

## 📁 **What You Get**

```
📦 SheetsBot/
├── 🚀 SheetsBot.bat          # Windows launcher
├── 🚀 SheetsBot.command      # macOS launcher  
├── 🚀 SheetsBot.py           # Linux launcher
├── 📂 src/                   # Application code
├── ⚙️ config/                # Configuration files
│   ├── creds.example.json    # Example credentials
│   └── settings.example.toml # Example settings
├── 📊 samples/               # Example CSV/Excel files
├── 👀 watch/                 # Default monitoring folder
├── 📖 README.md              # This guide
├── 📄 LICENSE                # MIT License
└── 📋 requirements.txt       # Python dependencies
```

---

## ⚡ **Features Overview**

### **🔧 Configuration Made Easy**
- ✅ **Visual Setup Wizard** - No config files to edit
- ✅ **Step-by-step Instructions** - With clickable links
- ✅ **Live Testing** - Test Google Sheets and Slack connections
- ✅ **Smart Validation** - Prevents common setup mistakes
- ✅ **Auto-save Settings** - Remembers your configuration

### **📊 Smart File Processing**
- ✅ **Multiple Formats** - CSV, XLSX, XLS support
- ✅ **Data Cleaning** - Removes empty rows/columns automatically
- ✅ **Format Standardization** - Consistent data formatting
- ✅ **Change Tracking** - Shows what was added/updated/deleted
- ✅ **Error Handling** - Clear error messages if something goes wrong

### **👀 File Monitoring**
- ✅ **Real-time Watching** - Processes files as soon as they appear
- ✅ **Multiple File Types** - Watches for CSV and Excel files
- ✅ **Custom Folders** - Watch any folder you choose
- ✅ **Debounced Processing** - Avoids duplicate processing
- ✅ **Background Operation** - Runs quietly in the background

### **💬 Slack Integration**
- ✅ **Rich Notifications** - Beautiful messages with file stats
- ✅ **Custom Channels** - Send notifications to any channel
- ✅ **Bot Customization** - Choose your bot name and icon
- ✅ **Optional Setup** - Works perfectly without Slack too
- ✅ **Live Testing** - Test notifications before saving

### **🖥️ Beautiful Interface**
- ✅ **Professional Design** - Clean, modern interface
- ✅ **Real-time Logs** - See everything happening live
- ✅ **Progress Indicators** - Visual feedback for all operations
- ✅ **Error Messages** - Clear explanations if something goes wrong
- ✅ **Success Confirmations** - Know when operations complete

---

## 🆘 **Troubleshooting**

### **Installation Issues**

**"Python not found" (Windows)**
- Download Python from [python.org](https://www.python.org/downloads/)
- ✅ **Important**: Check "Add Python to PATH" during installation
- Restart your computer after installation

**"Permission denied" (macOS)**
- Right-click `SheetsBot.command` → "Open" (first time only)
- macOS will ask for permission - click "Open"

**"Permission denied" (Linux)**
- Run: `chmod +x SheetsBot.py`
- Or run: `python3 SheetsBot.py`

### **Configuration Issues**

**"Failed to connect to Google Sheets"**
- ✅ Make sure you've shared your Google Sheet with the service account email
- ✅ Check that your spreadsheet ID is correct (from the URL)
- ✅ Verify your worksheet name (usually "Sheet1")
- ✅ Use the built-in "Test Google Sheets Connection" button

**"Slack notifications not working"**
- ✅ Make sure your webhook URL is correct
- ✅ Check that the channel exists in your Slack workspace
- ✅ Use the built-in "Test Slack Notification" button
- ✅ Slack is optional - app works fine without it

**"No files being processed"**
- ✅ Make sure files are in CSV or Excel format (.csv, .xlsx, .xls)
- ✅ Check that the watch folder path is correct
- ✅ Verify the file isn't empty or corrupted

### **Getting Help**

**🔍 Built-in Diagnostics**
- Use the Configuration tab's test buttons
- Check the real-time log panel for error messages
- Try processing a file from the `samples/` folder first

**📧 Need More Help?**
- Check the [Issues](https://github.com/boadamm/google-sheets/issues) page
- Create a new issue with your error message
- Include your platform (Windows/macOS/Linux) and Python version

---

## 🎉 **Success Stories**

**"I used to spend 2 hours every week copying CSV data to Google Sheets. Now it takes 30 seconds!"** - Small Business Owner

**"Our team gets Slack notifications whenever new sales data is uploaded. Game changer!"** - Marketing Team Lead

**"The setup wizard made it so easy. I'm not technical but had it working in 10 minutes."** - Operations Manager

---

## 📄 **License & Contributing**

**MIT License** - Feel free to use, modify, and share!

**Want to contribute?** 
- Fork the repository
- Make your improvements
- Submit a pull request

---

## 🎯 **Ready to Automate Your Workflow?**

**🚀 Download now and have your Google Sheets automation running in under 10 minutes!**

[**📥 Download Latest Release**](https://github.com/boadamm/google-sheets/releases) | [**📖 View Documentation**](https://github.com/boadamm/google-sheets/wiki) | [**🐛 Report Issues**](https://github.com/boadamm/google-sheets/issues)

---

**✨ Made with ❤️ for anyone who wants to automate their spreadsheet workflow without the hassle.**
