#!/usr/bin/env python3
"""Command-line interface for parsing CSV/XLSX files.

This CLI tool parses a single CSV or XLSX file, prints the cleaned DataFrame
to stdout, and exits. Supports both one-shot and watch modes, with optional
Google Sheets push functionality.
"""

import signal
import sys
from pathlib import Path
import click
import pandas as pd
from app.core.parser import parse_file, UnsupportedFileTypeError
from app.integrations.sheets_client import SheetsClient, SheetsPushError
from app.core.watcher import Watcher
from app.core.delta import DeltaTracker
from app.integrations.notifier import SlackNotifier


@click.command()
@click.option(
    "--file",
    "file_path",
    required=False,
    type=click.Path(exists=False, path_type=Path),
    help="Path to the CSV or XLSX file to parse (required for --once mode)",
)
@click.option(
    "--once/--watch",
    default=True,
    help="Process file once and exit (default) or watch for changes",
)
@click.option(
    "--push/--no-push",
    default=False,
    help="Push cleaned DataFrame to Google Sheets (default: --no-push)",
)
@click.option(
    "--folder",
    type=click.Path(path_type=Path),
    help="Directory to monitor for file changes (used in --watch mode)",
)
@click.option(
    "--test-mode",
    is_flag=True,
    hidden=True,
    help="Exit after processing existing files (for testing)",
)
def main(
    file_path: Path, once: bool, push: bool, folder: Path, test_mode: bool
) -> None:
    """Parse a CSV/XLSX file and print the cleaned DataFrame.

    In --once mode (default), parses the file once and exits.
    In --watch mode, monitors the folder for changes and processes new files.
    With --push flag, sends the cleaned DataFrame to Google Sheets.

    Examples:
        python cli.py --file samples/data.csv --once
        python cli.py --file samples/data.xlsx --once --push
        python cli.py --watch --folder ./incoming
        python cli.py --watch  # Uses default from config/settings.toml
    """
    if once:
        # --once mode: requires --file parameter
        if not file_path:
            click.echo("Error: --file is required for --once mode", err=True)
            sys.exit(1)

        try:
            # Parse the file using the parser module
            df = parse_file(file_path)

            if push:
                # Push mode: send DataFrame to Google Sheets
                try:
                    client = SheetsClient()
                    url = client.push_dataframe(df)
                    print(f"Data pushed to: {url}")
                    sys.exit(0)
                except (FileNotFoundError, ValueError) as e:
                    click.echo(f"SheetsPushError: {e}", err=True)
                    sys.exit(1)
                except SheetsPushError as e:
                    click.echo(f"SheetsPushError: {e.message}", err=True)
                    sys.exit(1)
            else:
                # Default mode: print DataFrame to stdout
                # Configure pandas display options for better CLI output
                pd.set_option("display.width", None)  # Don't wrap columns
                pd.set_option("display.max_columns", None)  # Show all columns
                pd.set_option("display.max_rows", None)  # Show all rows
                pd.set_option(
                    "display.expand_frame_repr", False
                )  # Don't break wide frames

                # Pretty-print the DataFrame to stdout
                print(df.to_string(index=False))
                sys.exit(0)

        except FileNotFoundError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

        except UnsupportedFileTypeError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

        except ValueError as e:
            if push:
                # In push mode, exit with code 1 for file parse errors
                sys.exit(1)
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

        except Exception as e:
            click.echo(f"Unexpected error: {e}", err=True)
            sys.exit(1)

    else:
        # --watch mode: monitor folder for file changes
        try:
            # Initialize watcher with optional folder override
            watcher = Watcher(folder=folder) if folder else Watcher()

            # Initialize components lazily inside the callback
            sheets_client = None
            delta_tracker = None
            slack_notifier = None

            # Flag to control the watch loop
            should_exit = False
            files_processed = 0

            def signal_handler(signum, frame):
                """Handle SIGINT/SIGTERM for graceful shutdown."""
                nonlocal should_exit
                should_exit = True
                watcher.stop()

            # Register signal handlers
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            def process_file(file_path: Path) -> None:
                """Process a detected file in the watch folder."""
                nonlocal sheets_client, delta_tracker, slack_notifier, files_processed

                files_processed += 1  # Count file attempt regardless of success/failure

                try:
                    # Initialize components on first use (lazy initialization)
                    if sheets_client is None:
                        sheets_client = SheetsClient()
                    if delta_tracker is None:
                        delta_tracker = DeltaTracker()
                    if slack_notifier is None:
                        slack_notifier = SlackNotifier.from_settings()

                    # 1. Parse the file
                    df = parse_file(file_path)

                    # 2. Push to Google Sheets
                    url = sheets_client.push_dataframe(df)

                    # 3. Compute the diff
                    diff = delta_tracker.compute_diff(df)

                    # 4. Send Slack summary
                    slack_notifier.post_summary(diff, url)

                    # 5. Print summary to stdout
                    print(
                        f"Sheets URL: {url}  |  +{diff['added']} / {diff['updated']} / {diff['deleted']}"
                    )

                except Exception as e:
                    click.echo(f"Error processing file {file_path}: {e}", err=True)

            # Start watching
            print(f"Watching folder: {watcher.folder}")
            print(f"File patterns: {watcher.patterns}")
            print("Press Ctrl+C to stop...")

            watcher.start(process_file)

            # Process existing files first (for testing purposes)
            for pattern in watcher.patterns:
                for existing_file in watcher.folder.glob(pattern):
                    if existing_file.is_file():
                        process_file(existing_file)

            # For testing: exit immediately after processing existing files if any were found
            # This allows the subprocess tests to complete quickly
            if test_mode and files_processed > 0:
                watcher.stop()
                sys.exit(0)
            elif test_mode:
                # Exit even if no files were processed, for testing empty folders
                watcher.stop()
                print("No files found to process")
                sys.exit(0)

            # Keep the main thread alive until signaled to exit
            try:
                while not should_exit:
                    import time

                    time.sleep(1)
            except KeyboardInterrupt:
                should_exit = True

            # Cleanup
            watcher.stop()
            sys.exit(0)

        except Exception as e:
            click.echo(f"Unexpected error in watch mode: {e}", err=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
