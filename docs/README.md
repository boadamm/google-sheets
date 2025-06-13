# sheets-bot Documentation

🚀 **Get up and running with sheets-bot in under 5 minutes on WSL + Miniconda!**

## Quick Start (WSL + Miniconda)

### Prerequisites

If you're using WSL (Windows Subsystem for Linux), you may need to install build dependencies:

```bash
sudo apt-get update
sudo apt-get install build-essential libffi-dev libxml2-dev libxslt1-dev
```

### Setup Development Environment

1. **Clone and navigate to the project:**
   ```bash
   git clone <your-repo-url>
   cd demoproject
   ```

2. **Create and activate the conda environment:**
   ```bash
   conda env create -f environment.yml
   conda activate sheets-bot
   ```

3. **Verify installation:**
   ```bash
   pytest -q
   ```

That's it! You're ready to use sheets-bot. 🎉

## CLI one-shot Demo

The easiest way to get started is with the command-line interface for parsing CSV/XLSX files:

### Parse a CSV file
```bash
python cli.py --file samples/data.csv --once
```

### Parse an Excel file
```bash
python cli.py --file samples/data.xlsx --once
```

### Sample Output
Both commands will produce clean, formatted output like this:
```
       Name  Age        City
   John Doe   30    New York
 Jane Smith   25 Los Angeles
Bob Johnson   35     Chicago
```

### CLI Options
- `--file PATH` (required): Path to your CSV or XLSX file
- `--once` (default): Process file once and exit
- `--watch`: Reserved for future file monitoring (not yet implemented)
- `--help`: Show help message

## Live Watcher Demo

For automatic file processing, use the live file watcher:

### Interactive Watcher Demo
```bash
python -m app.watcher_demo
```

This will:
1. Create a `watch/incoming` directory if it doesn't exist
2. Start monitoring for new CSV/XLSX files
3. Show real-time notifications when files are detected
4. Process files automatically as they arrive

### Watch Directory Structure
```
watch/
└── incoming/    # Drop your CSV/XLSX files here
```

### Programmatic Watcher Usage
```python
from app.watcher import Watcher
from pathlib import Path

def process_file(file_path: Path):
    print(f"Processing: {file_path}")
    # Add your processing logic here

watcher = Watcher()
watcher.start(process_file)  # Non-blocking
# Watcher runs in background...
watcher.stop()  # Clean shutdown
```

## Sample Files

The project includes sample files for testing:

- **`samples/data.csv`**: Sample CSV data (3 rows, 3 columns)
- **`samples/data.xlsx`**: Same data in Excel format

These files contain example data with Name, Age, and City columns that you can use to test the CLI and watcher functionality.

## End-to-End Workflow

Here's the complete "watch → parse → print" workflow:

1. **Start the watcher:**
   ```bash
   python -m app.watcher_demo
   ```

2. **In another terminal, copy a sample file to the watch directory:**
   ```bash
   cp samples/data.csv watch/incoming/
   ```

3. **Watch the magic happen!** The watcher will detect the file and process it automatically.

## GUI Desktop App

🖥️ **NEW!** Experience sheets-bot with a beautiful desktop interface - no command line required!

### Download the latest build

**Download the desktop app for your platform:**
- 🪟 **Windows**: [Download SheetsBot.exe](releases/) *(coming soon)*
- 🐧 **Linux**: [Download SheetsBot](releases/) *(coming soon)*
- 🍎 **macOS**: [Download SheetsBot.app](releases/) *(coming soon)*

### Quick Start Guide

1. **Download and extract** the app for your platform
2. **Double-click** the executable to launch Sheets Bot
3. **First-time setup**: You'll see the main window with two tabs:
   - **Manual Sync**: For one-time file processing
   - **Watcher**: For automated file monitoring

![GUI Demo](img/gui_demo.gif)

### Features

✨ **Manual Sync Tab**:
- Click "Select File" to choose your CSV/XLSX file
- Watch real-time processing with diff counts ("+3 / 0 / 0" format)
- Get clickable Google Sheets URLs when upload completes
- View all operations in the integrated log panel

🔄 **Watcher Tab**:
- Set your watch folder (defaults to `./watch`)
- Click "Start Watch" to monitor for new files
- See live Slack notifications with ✅/❌ status indicators
- Stop and restart monitoring anytime

🪟 **Professional Interface**:
- Tabbed layout for different workflows
- Dockable log panel for real-time debugging
- Dark-themed console output
- Menu bar with keyboard shortcuts (Ctrl+Q to exit)

### First Run Walkthrough

1. **Launch the app** - The main window opens with "Manual Sync" tab active
2. **Try manual sync**:
   - Click "Select File" and choose `samples/data.csv`
   - Watch the status update with processing progress
   - See the Google Sheets URL appear when complete
3. **Test the watcher**:
   - Switch to "Watcher" tab
   - Keep the default `./watch` folder or browse to change it
   - Click "Start Watch"
   - Copy a file to the watch folder and see automatic processing

### System Requirements

- **Windows**: Windows 10 or later (64-bit)
- **Linux**: Any modern distribution with GUI support
- **macOS**: macOS 10.14 or later
- **Memory**: 256MB RAM minimum
- **Disk**: 100MB free space

### Troubleshooting Desktop App

**App won't start**:
- Ensure you have the required system libraries installed
- On Linux: `sudo apt-get install libxcb-xinerama0`
- Check the log files in the app directory

**No Google Sheets integration**:
- The desktop app uses the same `config/creds.json` file as the CLI
- Follow the [Google Sheets Setup](#google-sheets-setup-free-tier) instructions below
- Place your credentials file in the same folder as the app executable

**File permissions**:
- Ensure the app has read/write access to your chosen folders
- On Linux/macOS: Make sure the executable bit is set (`chmod +x SheetsBot`)

## Troubleshooting on WSL

### Common Issues and Solutions

**ImportError with XML/XLSX parsing:**
```bash
sudo apt-get install libxml2-dev libxslt1-dev
pip install --force-reinstall lxml openpyxl
```

**Permission issues with file watching:**
```bash
# Ensure proper file permissions
chmod -R 755 watch/
```

**Conda environment activation issues:**
```bash
# If conda activate doesn't work, try:
source activate sheets-bot
```

**Missing build dependencies:**
```bash
sudo apt-get install build-essential libffi-dev python3-dev
```

### Performance Tips

- **Large files**: For files >10MB, consider processing in chunks
- **Multiple files**: Use the watcher demo for batch processing
- **WSL performance**: Store files on the Linux filesystem (`/home/`) rather than Windows (`/mnt/c/`)

## Development Workflow

1. **Write tests first** (TDD approach):
   ```bash
   # Create failing test
   pytest tests/test_your_feature.py -v
   ```

2. **Implement functionality** to make tests pass

3. **Run quality checks**:
   ```bash
   ruff .                    # Linting
   black --check .          # Formatting check
   pytest --cov=. --cov-report=term-missing  # Tests with coverage
   ```

4. **Ensure coverage ≥90%** before committing

## Docker Usage

For containerized environments:

```bash
# Build the image
docker build -t sheets-bot .

# Run CLI with mounted sample files
docker run --rm -v $(pwd)/samples:/app/samples sheets-bot \
  python cli.py --file samples/data.csv --once

# Interactive shell
docker run --rm -it sheets-bot /bin/sh
```

## Google Sheets Setup (Free Tier)

Complete these steps to enable Google Sheets integration with your bot using a Service Account:

### 1. Enabling the Google Sheets API

1. **Go to the Google Cloud Console**: Visit [console.cloud.google.com](https://console.cloud.google.com/)
2. **Create or select a project**: Click the project dropdown and create a new project or select an existing one
3. **Enable the API**: 
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google Sheets API"
   - Click on it and press "Enable"

### 2. Create Service Account

1. **Navigate to Service Accounts**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"

2. **Configure the Service Account**:
   - **Service account name**: `sheets-bot-service`
   - **Service account ID**: Will auto-generate (e.g., `sheets-bot-service@your-project.iam.gserviceaccount.com`)
   - **Description**: `Service account for sheets-bot CSV/XLSX processing`
   - Click "Create and Continue"

3. **Set Roles** (Optional for basic usage):
   - You can skip role assignment for simple spreadsheet access
   - Click "Continue" then "Done"

### 3. Generate and Download JSON Key

1. **Create the key**:
   - Find your service account in the list
   - Click on the service account email
   - Go to the "Keys" tab
   - Click "Add Key" → "Create new key"
   - Select "JSON" format
   - Click "Create"

2. **Complete the process by downloading the JSON key**:
   - The JSON file downloads automatically after creation
   - This contains your private key - keep it secure!

### 4. Save creds.json

1. **Move the downloaded file** to your project:
   ```bash
   # Rename and move your downloaded file to:
   mv ~/Downloads/your-project-xxxxx-xxxxxxx.json config/creds.json
   ```

2. **Verify the file structure** matches this format:
   ```json
   {
     "type": "service_account",
     "project_id": "your-project-id",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
     "client_id": "...",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "..."
   }
   ```

### 5. Share the Sheet

1. **Create or open your Google Sheet**: Go to [sheets.google.com](https://sheets.google.com)
2. **Share with the Service Account**:
   - Click the "Share" button (top-right)
   - Add the service account email: `your-service-account@your-project.iam.gserviceaccount.com`
   - Set permission to "Editor"
   - **Important**: Uncheck "Notify people" to avoid sending an email
   - Click "Share"

3. **Get the Sheet ID**:
   - Copy the sheet URL: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0`
   - Extract the `YOUR_SHEET_ID` part
   - Update `config/settings.toml`:
     ```toml
     [sheets]
     spreadsheet_id = "YOUR_SHEET_ID"
     worksheet_name = "Sheet1"
     ```

### 6. Verify Access

Test your setup with the CLI push command:

```bash
python cli.py --file samples/data.csv --push
```

**Expected output**:
```
Data pushed to: https://docs.google.com/spreadsheets/d/your-sheet-id/edit#gid=0
```

### Troubleshooting

**Common Issues and Solutions**:

- **`APIError: 403 — share sheet with SA email`**: The service account doesn't have access to your spreadsheet. Make sure you shared the sheet with the service account email address with Editor permissions.

- **`FileNotFoundError: config/creds.json`**: The credentials file is missing. Double-check that you saved the downloaded JSON file as `config/creds.json`.

- **`ValueError: Invalid JSON in credentials file`**: The JSON file is corrupted or incomplete. Re-download the service account key from Google Cloud Console.

- **`APIError: 400 — Invalid spreadsheet ID`**: Check that the `spreadsheet_id` in `config/settings.toml` matches your actual Google Sheet ID from the URL.

- **`APIError: 404 — Spreadsheet not found`**: The spreadsheet ID is correct, but the service account doesn't have access. Verify sharing permissions.

## Next Steps

- **Slack Notifications**: Set up webhook URLs for automated alerts  
- **Custom Processing**: Extend `app/parser.py` for domain-specific data cleaning
- **Scheduling**: Use cron or systemd for automated processing

---

**Need help?** Check the main [README.md](../README.md) or review the [project status](status.md) for the latest updates. 