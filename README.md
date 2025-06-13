# sheets-bot

[![CI Pipeline](https://github.com/baranozck/demoproject/actions/workflows/ci.yml/badge.svg)](https://github.com/baranozck/demoproject/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen)](https://github.com/baranozck/demoproject/actions)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A production-quality Python application for Google Sheets automation using Miniconda on Ubuntu WSL.

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
   ruff .                    # Linting
   black --check .          # Formatting check
   pytest --cov=. --cov-report=term-missing  # Tests with coverage
   ```

### Usage Examples

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

### Project Structure

```
sheets-bot/
├── environment.yml       # Conda environment specification
├── .cursorrules         # Development guidelines
├── app/                 # Application source code
│   ├── watcher.py       # File monitoring system
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