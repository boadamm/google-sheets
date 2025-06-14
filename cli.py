#!/usr/bin/env python3
"""
Wrapper script for backwards compatibility.
This allows existing tests and scripts to still call cli.py from the root directory.
"""
import sys
from pathlib import Path


def main():
    """Main entry point that sets up path and calls the actual CLI."""
    # Add src directory to Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))

    # Import and run the actual CLI after path setup
    import cli_main

    cli_main.main()


if __name__ == "__main__":
    main()
