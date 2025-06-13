#!/usr/bin/env python3
"""Command-line interface for parsing CSV/XLSX files.

This CLI tool parses a single CSV or XLSX file, prints the cleaned DataFrame
to stdout, and exits. Supports both one-shot and watch modes, with optional
Google Sheets push functionality.
"""

import sys
from pathlib import Path
import click
import pandas as pd
from app.parser import parse_file, UnsupportedFileTypeError
from app.sheets_client import SheetsClient, SheetsPushError


@click.command()
@click.option(
    "--file",
    "file_path",
    required=True,
    type=click.Path(exists=False, path_type=Path),
    help="Path to the CSV or XLSX file to parse",
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
def main(file_path: Path, once: bool, push: bool) -> None:
    """Parse a CSV/XLSX file and print the cleaned DataFrame.

    In --once mode (default), parses the file once and exits.
    In --watch mode, monitors the file for changes (reserved for future use).
    With --push flag, sends the cleaned DataFrame to Google Sheets.

    Examples:
        python cli.py --file samples/data.csv --once
        python cli.py --file samples/data.xlsx --once --push
        python cli.py --file samples/data.csv --push
    """
    if not once:
        click.echo("--watch mode is not yet implemented", err=True)
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
            pd.set_option("display.expand_frame_repr", False)  # Don't break wide frames

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


if __name__ == "__main__":
    main()
