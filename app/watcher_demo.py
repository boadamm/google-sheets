"""Demo script for the file watcher functionality.

This script demonstrates how to use the Watcher class to monitor
file changes in a directory.
"""

import time
from pathlib import Path
from app.watcher import Watcher


def file_callback(file_path: Path) -> None:
    """Callback function that handles detected file changes.

    Args:
        file_path: Path to the file that was created or modified
    """
    print(f"📁 File detected: {file_path}")
    print(f"   Size: {file_path.stat().st_size} bytes")
    print(f"   Extension: {file_path.suffix}")
    print("-" * 50)


def main() -> None:
    """Main demo function."""
    print("🔍 Starting File Watcher Demo")
    print("=" * 50)

    # Create watcher using config defaults
    watcher = Watcher()

    print(f"📂 Monitoring folder: {watcher.folder}")
    print(f"🎯 File patterns: {watcher.patterns}")
    print(f"⏱️  Poll interval: {watcher.poll_interval}s")
    print("\n💡 Create or modify CSV/XLSX files in the watch folder to see events!")
    print("   Press Ctrl+C to stop watching...\n")

    # Start the watcher
    watcher.start(file_callback)

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping watcher...")
        watcher.stop()
        print("✅ Watcher stopped successfully!")


if __name__ == "__main__":
    main()
