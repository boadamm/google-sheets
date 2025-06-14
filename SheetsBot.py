#!/usr/bin/env python3
"""
SheetsBot - Google Sheets Automation Tool
Main launcher for end users - simply double-click to run!

This file automatically:
1. Checks for required dependencies
2. Installs missing packages
3. Launches the GUI application
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def check_and_install_requirements():
    """Check if required packages are installed, install if missing."""
    
    # Required packages for basic functionality
    required_packages = [
        'click',
        'pandas', 
        'watchdog',
        'gspread',
        'gspread-dataframe',
        'pyyaml',
        'tomli',
        'openpyxl',
        'PySide6'
    ]
    
    missing_packages = []
    
    print("🔍 Checking dependencies...")
    
    for package in required_packages:
        try:
            importlib.import_module(package.lower().replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--user'
            ] + missing_packages)
            print("✅ All dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print("\nPlease install manually using:")
            print(f"pip install {' '.join(missing_packages)}")
            input("Press Enter to continue anyway...")
    else:
        print("✅ All dependencies are already installed!")

def setup_config():
    """Ensure configuration is set up."""
    config_dir = Path("config")
    if not config_dir.exists():
        print("❌ Configuration directory not found!")
        return False
    
    creds_file = config_dir / "creds.json"
    if not creds_file.exists():
        example_file = config_dir / "creds.example.json"
        if example_file.exists():
            print("\n⚠️  Google Sheets credentials not found!")
            print("📝 Don't worry! The app includes an easy setup wizard.")
            print("   When the GUI opens, go to the '⚙️ Configuration' tab")
            print("   to set up your Google Sheets API credentials easily.")
            print("\n📖 For manual setup, see README.md for detailed instructions.")
            
            choice = input("\nWould you like to continue to the GUI? (Y/n): ")
            if choice.lower() == 'n':
                return False
        else:
            print("\n⚠️  Google Sheets credentials not found!")
            print("📝 Use the Configuration tab in the GUI to set up your credentials.")
    
    return True

def launch_gui():
    """Launch the GUI application."""
    try:
        # Add src to path
        src_path = Path(__file__).parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        print("\n🚀 Launching SheetsBot GUI...")
        
        # Import and run the GUI
        from app.gui.main_window import run_gui
        run_gui()
        
    except ImportError as e:
        print(f"❌ Failed to import GUI: {e}")
        print("Falling back to CLI mode...")
        launch_cli()
    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        print("Falling back to CLI mode...")
        launch_cli()

def launch_cli():
    """Launch the CLI application."""
    try:
        # Add src to path
        src_path = Path(__file__).parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        print("\n💻 Starting SheetsBot CLI...")
        print("Use --help for available commands")
        
        from cli_main import main
        
        # If no arguments provided, show help
        if len(sys.argv) == 1:
            sys.argv.append('--help')
        
        main()
        
    except Exception as e:
        print(f"❌ Failed to launch CLI: {e}")
        input("Press Enter to exit...")

def main():
    """Main entry point for SheetsBot."""
    print("=" * 50)
    print("🤖 SheetsBot - Google Sheets Automation Tool")
    print("=" * 50)
    
    # Step 1: Check and install dependencies
    check_and_install_requirements()
    
    # Step 2: Check configuration
    if not setup_config():
        input("\nPress Enter to exit...")
        return
    
    # Step 3: Determine launch mode
    if len(sys.argv) > 1:
        # CLI mode if arguments provided
        launch_cli()
    else:
        # GUI mode by default
        choice = input("\n🖥️  Launch GUI (G) or CLI (C)? [G]: ").strip().lower()
        if choice == 'c':
            launch_cli() 
        else:
            launch_gui()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...") 