# 🔑 API Keys & Credentials Setup Guide

This guide will walk you through setting up all the required API keys and credentials for your Sheets Bot application.

## 📋 Quick Overview

Your Sheets Bot needs these integrations:
- ✅ **Google Sheets API** (Required) - For reading/writing spreadsheet data
- ✅ **Slack Webhooks** (Optional) - For notifications and status updates

## 🚀 Step-by-Step Setup

### 1️⃣ Create Your Environment File

First, copy the template to create your environment file:

```bash
# Copy the template
cp env.template .env

# Make sure it's properly ignored by Git (should already be in .gitignore)
echo ".env" >> .gitignore
```

### 2️⃣ Google Sheets API Setup (REQUIRED)

#### A. Enable Google Sheets API

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Create a new project or select an existing one

2. **Enable the Google Sheets API**
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google Sheets API"
   - Click on it and press "Enable"

#### B. Create Service Account

1. **Create Service Account**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Fill in:
     - **Service account name**: `sheets-bot-service`
     - **Service account ID**: (auto-generated)
     - **Description**: `Service account for sheets-bot automation`
   - Click "Create and Continue"

2. **Skip Role Assignment** (not needed for basic sheets access)
   - Click "Continue" → "Done"

#### C. Generate JSON Key

1. **Create Key**
   - Find your service account in the list
   - Click on the service account email
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Select "JSON" format
   - Click "Create"

2. **Download & Save**
   - The JSON file downloads automatically
   - **Save it as**: `config/creds.json` in your project
   - **Keep it secure!** This contains your private key

#### D. Extract Values for .env

Open the downloaded JSON file and extract these values for your `.env` file:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",              ← GOOGLE_PROJECT_ID
  "private_key_id": "abc123...",                ← GOOGLE_PRIVATE_KEY_ID
  "private_key": "-----BEGIN PRIVATE KEY-----\n...", ← GOOGLE_PRIVATE_KEY
  "client_email": "sheets-bot@project.iam.gserviceaccount.com", ← GOOGLE_SERVICE_ACCOUNT_EMAIL
  "client_id": "123456789",                     ← GOOGLE_CLIENT_ID
  ...
}
```

**Fill in your `.env` file:**
```bash
GOOGLE_PROJECT_ID=your-actual-project-id
GOOGLE_SERVICE_ACCOUNT_EMAIL=sheets-bot@your-project-id.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY_ID=your-actual-private-key-id
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_ACTUAL_PRIVATE_KEY_CONTENT\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_ID=your-actual-client-id
```

#### E. Set Up Your Google Sheet

1. **Create or Open Your Google Sheet**
   - Go to https://sheets.google.com
   - Create a new sheet or open an existing one

2. **Get the Sheet ID**
   - Copy the URL: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit`
   - Extract the `YOUR_SHEET_ID` part

3. **Share with Service Account**
   - Click "Share" button (top-right)
   - Add your service account email: `sheets-bot@your-project-id.iam.gserviceaccount.com`
   - Set permission to "Editor"
   - **Uncheck "Notify people"** (avoid sending email)
   - Click "Share"

4. **Update .env File**
   ```bash
   GOOGLE_SPREADSHEET_ID=your-actual-sheet-id
   GOOGLE_WORKSHEET_NAME=Sheet1
   ```

### 3️⃣ Slack Integration Setup (OPTIONAL)

#### A. Create Slack Webhook

1. **Go to Slack API**
   - Visit: https://api.slack.com/messaging/webhooks
   - Click "Create your Slack app"

2. **Create App**
   - Choose "From scratch"
   - App Name: `Sheets Bot`
   - Choose your workspace
   - Click "Create App"

3. **Enable Incoming Webhooks**
   - Click "Incoming Webhooks" in the left sidebar
   - Toggle "Activate Incoming Webhooks" to ON
   - Click "Add New Webhook to Workspace"
   - Choose a channel (e.g., #general)
   - Click "Allow"

4. **Copy Webhook URL**
   - Copy the webhook URL (starts with `https://hooks.slack.com/services/...`)

#### B. Update .env File

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/ACTUAL/WEBHOOK
SLACK_CHANNEL=#general
SLACK_USERNAME=Sheets-Bot
SLACK_ICON_EMOJI=:robot_face:
```

### 4️⃣ Application Settings

Configure basic app settings in your `.env`:

```bash
# File watching settings
WATCH_FOLDER=./watch
WATCH_PATTERNS=*.csv,*.xlsx
WATCH_POLL_INTERVAL=5

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

### 5️⃣ Verify Your Setup

Test your configuration:

```bash
# Test with a sample file
python cli.py --file samples/data.csv --push

# Expected output:
# ✅ Data pushed to: https://docs.google.com/spreadsheets/d/your-sheet-id/edit
```

## 🔧 Alternative: Using Config Files

Instead of environment variables, you can use config files:

### Option 1: Google Credentials JSON
- Save your downloaded JSON as `config/creds.json`
- The app will automatically use it

### Option 2: Settings TOML
- Edit `config/settings.toml`:
```toml
[sheets]
spreadsheet_id = "your-sheet-id"
worksheet_name = "Sheet1"

[slack]
webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
channel = "#general"
username = "Sheets-Bot"
icon_emoji = ":robot_face:"
```

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### ❌ `FileNotFoundError: config/creds.json`
**Solution**: Make sure you saved the downloaded JSON file as `config/creds.json`

#### ❌ `APIError: 403 — share sheet with SA email`
**Solution**: Share your Google Sheet with the service account email with Editor permissions

#### ❌ `ValueError: Invalid JSON in credentials file`
**Solution**: Re-download the service account key from Google Cloud Console

#### ❌ `APIError: 400 — Invalid spreadsheet ID`
**Solution**: Check that your `GOOGLE_SPREADSHEET_ID` matches the ID in your Google Sheets URL

#### ❌ Slack notifications not working
**Solution**: Verify your `SLACK_WEBHOOK_URL` is correct and the webhook is active

### Test Commands

```bash
# Test Google Sheets connection
python -c "from app.sheets_client import SheetsClient; client = SheetsClient(); print('✅ Google Sheets connection successful')"

# Test Slack notifications
python -c "from app.notifier import SlackNotifier; notifier = SlackNotifier.from_settings(); print('✅ Slack connection successful')"

# Test file parsing
python cli.py --file samples/data.csv --once

# Test full pipeline
python cli.py --file samples/data.csv --push
```

## 🔒 Security Best Practices

### DO:
- ✅ Keep your `.env` file out of version control
- ✅ Use environment variables for sensitive data
- ✅ Rotate service account keys regularly
- ✅ Limit Google Sheets permissions to specific sheets

### DON'T:
- ❌ Commit API keys to Git
- ❌ Share your service account JSON file
- ❌ Use overly broad permissions
- ❌ Hard-code secrets in your source code

## 📚 Additional Resources

- **Google Sheets API Documentation**: https://developers.google.com/sheets/api
- **Slack Webhook Documentation**: https://api.slack.com/messaging/webhooks
- **Google Cloud Console**: https://console.cloud.google.com/
- **Slack API Dashboard**: https://api.slack.com/apps

---

🎉 **You're all set!** Your Sheets Bot is now configured and ready to automate your spreadsheet workflows. 