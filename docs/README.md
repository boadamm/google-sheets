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

## Next Steps

- **Google Sheets Integration**: Configure `config/settings.toml` for spreadsheet uploads
- **Slack Notifications**: Set up webhook URLs for automated alerts  
- **Custom Processing**: Extend `app/parser.py` for domain-specific data cleaning
- **Scheduling**: Use cron or systemd for automated processing

---

**Need help?** Check the main [README.md](../README.md) or review the [project status](status.md) for the latest updates. 