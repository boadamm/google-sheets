"""Google Sheets client module.

This module provides functionality to push pandas DataFrames to Google Sheets
using a service account for authentication.
"""

from pathlib import Path
from typing import Union
import pandas as pd
import gspread
import gspread_dataframe
import tomli
from gspread.exceptions import APIError


class SheetsPushError(Exception):
    """Custom exception for Google Sheets push operations."""

    def __init__(self, message: str) -> None:
        """Initialize SheetsPushError with a message.

        Args:
            message: Error message describing the failure
        """
        super().__init__(message)
        self.message = message


class SheetsClient:
    """Client for pushing DataFrames to Google Sheets.

    This class handles authentication with Google Sheets API using a service account
    and provides functionality to push pandas DataFrames to specified worksheets.
    """

    def __init__(
        self,
        creds_path: Union[Path, str, None] = None,
        settings_path: Union[Path, str, None] = None,
    ) -> None:
        """Initialize SheetsClient with configuration paths.

        Args:
            creds_path: Path to Google service account credentials JSON file.
                       If None, defaults to 'config/creds.json'
            settings_path: Path to settings TOML file containing spreadsheet config.
                          If None, defaults to 'config/settings.toml'

        Raises:
            FileNotFoundError: If credentials or settings files don't exist
        """
        # Set default paths if not provided
        self.creds_path = Path(creds_path) if creds_path else Path("config/creds.json")
        self.settings_path = (
            Path(settings_path) if settings_path else Path("config/settings.toml")
        )

        # Validate that configuration files exist
        if not self.creds_path.exists():
            raise FileNotFoundError(f"Credentials file not found: {self.creds_path}")

        if not self.settings_path.exists():
            raise FileNotFoundError(f"Settings file not found: {self.settings_path}")

        # Load settings
        self._load_settings()

    def _load_settings(self) -> None:
        """Load settings from the TOML configuration file."""
        with open(self.settings_path, "rb") as f:
            settings = tomli.load(f)

        sheets_config = settings.get("sheets", {})
        self.spreadsheet_id = sheets_config.get("spreadsheet_id")
        self.worksheet_name = sheets_config.get("worksheet_name")

        if not self.spreadsheet_id:
            raise ValueError("Missing 'spreadsheet_id' in settings configuration")
        if not self.worksheet_name:
            raise ValueError("Missing 'worksheet_name' in settings configuration")

    def push_dataframe(self, df: pd.DataFrame) -> str:
        """Push a pandas DataFrame to the configured Google Sheets worksheet.

        This method:
        1. Authenticates using the service account credentials
        2. Opens the spreadsheet and selects the worksheet
        3. Clears the existing worksheet content
        4. Writes the DataFrame to the worksheet
        5. Returns the URL of the updated worksheet

        Args:
            df: pandas DataFrame to push to Google Sheets

        Returns:
            str: URL of the updated worksheet

        Raises:
            SheetsPushError: If any error occurs during the push operation
        """
        try:
            # Authenticate with Google Sheets API
            gc = gspread.service_account(filename=self.creds_path)

            # Open spreadsheet and select worksheet
            spreadsheet = gc.open_by_key(self.spreadsheet_id)
            worksheet = spreadsheet.worksheet(self.worksheet_name)

            # Clear existing content
            worksheet.clear()

            # Write DataFrame to worksheet
            gspread_dataframe.set_with_dataframe(worksheet, df)

            # Return worksheet URL
            return worksheet.url

        except APIError as e:
            raise SheetsPushError(
                f"Failed to push DataFrame to Google Sheets: {str(e)}"
            )
        except Exception as e:
            raise SheetsPushError(f"Unexpected error during sheets operation: {str(e)}")
