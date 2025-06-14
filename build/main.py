#!/usr/bin/env python3
"""Entry point script for sheets-bot desktop application.

This script serves as the main entry point for the PyInstaller-built
desktop application, importing and calling the GUI runner function.
"""

import sys
from pathlib import Path

# Add the project root to Python path for imports
if getattr(sys, 'frozen', False):
    # We're running in a PyInstaller bundle
    bundle_dir = Path(sys._MEIPASS)
else:
    # We're running in a normal Python environment
    bundle_dir = Path(__file__).parent.parent

sys.path.insert(0, str(bundle_dir))

# Import and run the GUI
try:
    from app.gui.main_window import run_gui
    
    if __name__ == "__main__":
        run_gui()
        
except Exception as e:
    # Fallback error handling for debugging
    import traceback
    print(f"Error starting Sheets Bot GUI: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1) 