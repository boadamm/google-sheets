# sheets-bot

[![CI Pipeline](https://github.com/boadamm/demoproject/actions/workflows/ci.yml/badge.svg)](https://github.com/boadamm/demoproject/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](https://github.com/boadamm/demoproject/actions)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Latest Release](https://img.shields.io/github/v/release/boadamm/demoproject)](https://github.com/boadamm/demoproject/releases/latest)

A production-quality Python application for Google Sheets automation using Miniconda on Ubuntu WSL.

📖 **[→ Complete Documentation & Quick Start Guide](docs/README.md)** ←


## Downloads

Get the latest desktop applications for your platform:

### Latest Release

- **Windows**: [Download SheetsBot-Windows-signed.zip](https://github.com/boadamm/demoproject/releases/latest/download/SheetsBot-Windows-signed.zip)
- **Linux**: [Download SheetsBot-Linux.zip](https://github.com/boadamm/demoproject/releases/latest/download/SheetsBot-Linux.zip)

> 💡 **Want to build now?** Run `make build-gui` to create your own desktop app.


## Quick Start (Conda on WSL)

### Prerequisites
WSL users may need to install build dependencies:
```bash
sudo apt-get update
sudo apt-get install build-essential libffi-dev
```

### Setup Development Environment

```bash
# 1 – Create env
conda env create -f environment.yml
conda activate sheets-bot

# 2 – Run tests
pytest -q

# 3 – Install pre-commit hooks (optional)
pip install pre-commit && pre-commit install
```

### Development Workflow

1. **Write tests first** (TDD approach)
2. **Implement functionality** to make tests pass
3. **Run quality checks**:
   ```bash
   ruff check .             # Linting
   black --check .          # Formatting check
   pytest --cov=. --cov-report=term-missing  # Tests with coverage
   ```

### Usage Examples

#### CLI File Parser
```bash
# Parse a CSV file and display cleaned DataFrame
python cli.py --file samples/data.csv --once

# Parse an Excel file and display cleaned DataFrame  
python cli.py --file samples/data.xlsx --once

# Parse and push to Google Sheets
python cli.py --file samples/data.csv --push
python cli.py --file samples/data.xlsx --push
```

**Sample Output:**
```
       Name  Age        City
   John Doe   30    New York
 Jane Smith   25 Los Angeles
Bob Johnson   35     Chicago
```

**Sample Output with --push:**
```
Data pushed to: https://docs.google.com/spreadsheets/d/your-sheet-id/edit#gid=0
```

#### Live Watch Demo
```bash
# Live watch demo - monitors incoming files and processes them automatically
python cli.py --watch
```

Monitor a specific folder for incoming CSV/XLSX files. When files are detected, the CLI will:
1. Parse the file automatically
2. Push data to Google Sheets
3. Compute row differences (added/updated/deleted)
4. Send Slack notification with summary
5. Display progress in terminal

**Sample Output:**
```
Watching folder: ./watch
File patterns: ['*.csv', '*.xlsx']
Press Ctrl+C to stop...
Sheets URL: https://docs.google.com/spreadsheets/d/your-sheet-id/edit#gid=0  |  +3 / 0 / 0
```

#### File Watcher Demo
```bash
# Run the interactive file watcher demo
python -m app.watcher_demo

# Monitor files programmatically
python -c "
from app.watcher import Watcher
from pathlib import Path

def callback(path): print(f'File detected: {path}')
w = Watcher(); w.start(callback)
# Watcher runs in background...
"
```

#### Slack Notifications
```bash
# Send diff summary to Slack channel
python -c "
from app.notifier import SlackNotifier

# Configure via settings.toml or directly
notifier = SlackNotifier.from_settings()
diff = {'added': 3, 'updated': 1, 'deleted': 0}
sheet_url = 'https://docs.google.com/spreadsheets/d/your-sheet-id/edit'
success = notifier.post_summary(diff, sheet_url)
"
```

**Slack Setup**: Configure your webhook URL in `config/settings.toml` under `[slack]` section. See [Slack Incoming Webhooks documentation](https://api.slack.com/messaging/webhooks) for webhook URL setup.

### Project Structure

```
sheets-bot/
├── environment.yml       # Conda environment specification
├── .cursorrules         # Development guidelines
├── app/                 # Application source code
│   ├── watcher.py       # File monitoring system
│   ├── sheets_client.py # Google Sheets integration
│   └── watcher_demo.py  # Demo script
├── config/
│   └── settings.toml    # Configuration file
├── tests/               # Test suite
└── docs/                # Documentation
```

## Features

- **Conda Environment**: Reproducible development setup with pinned dependencies
- **Quality Gates**: Black, Ruff, pytest with 90%+ coverage requirement
- **TDD/BDD**: Test-first development approach
- **Google Sheets Integration**: Push DataFrames directly to Google Sheets
- **WSL Optimized**: Tested on Ubuntu WSL with Miniconda

## Requirements

- Python 3.11+
- Miniconda or Anaconda
- Ubuntu WSL (for WSL users)

## Contributing

1. Follow TDD principles - write failing tests first
2. Ensure all quality gates pass before committing
3. Use conventional commit messages
4. Maintain test coverage above 90%

## License

TBD 
