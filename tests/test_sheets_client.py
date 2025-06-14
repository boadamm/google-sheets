"""Tests for the SheetsClient module.

This module contains comprehensive tests for the Google Sheets client
functionality, following TDD principles with extensive mocking.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd
import json

from app.integrations.sheets_client import SheetsClient, SheetsPushError


class TestSheetsClient:
    """Test cases for the SheetsClient class."""

    def test_sheets_client_init_with_default_paths(self):
        """Test SheetsClient initialization with default config paths."""
        with patch("app.integrations.sheets_client.Path.exists", return_value=True), patch(
            "builtins.open", mock_open_for_configs()
        ):
            client = SheetsClient()
            assert client.creds_path == Path("config/creds.json")
            assert client.settings_path == Path("config/settings.toml")

    def test_sheets_client_init_with_custom_paths(self):
        """Test SheetsClient initialization with custom paths."""
        custom_creds = Path("custom/creds.json")
        custom_settings = Path("custom/settings.toml")

        with patch("app.integrations.sheets_client.Path.exists", return_value=True), patch(
            "builtins.open", mock_open_for_configs()
        ):
            client = SheetsClient(
                creds_path=custom_creds, settings_path=custom_settings
            )
            assert client.creds_path == custom_creds
            assert client.settings_path == custom_settings

    def test_sheets_client_missing_creds_file(self):
        """Test SheetsClient raises error when creds file is missing."""
        with patch("app.integrations.sheets_client.Path.exists", return_value=False):
            with pytest.raises(FileNotFoundError, match="Credentials file not found"):
                SheetsClient()

    def test_sheets_client_missing_settings_file(self):
        """Test SheetsClient raises error when settings file is missing."""

        def mock_exists(path_obj):
            return "creds.json" in str(path_obj)

        with patch("app.integrations.sheets_client.Path.exists", mock_exists):
            with pytest.raises(FileNotFoundError, match="Settings file not found"):
                SheetsClient()

    @patch("app.integrations.sheets_client.gspread.service_account")
    @patch("app.integrations.sheets_client.gspread_dataframe.set_with_dataframe")
    def test_push_dataframe_success(
        self, mock_set_with_dataframe, mock_service_account
    ):
        """Test successful DataFrame push to Google Sheets."""
        # Arrange
        mock_gc = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_worksheet.url = "https://docs.google.com/spreadsheets/d/abc123/edit#gid=0"

        mock_service_account.return_value = mock_gc
        mock_gc.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet

        with patch("app.integrations.sheets_client.Path.exists", return_value=True), patch(
            "builtins.open", mock_open_for_configs()
        ):
            client = SheetsClient()

        df = pd.DataFrame({"Name": ["John", "Jane"], "Age": [30, 25]})

        # Act
        result_url = client.push_dataframe(df)

        # Assert
        mock_service_account.assert_called_once_with(filename=Path("config/creds.json"))
        mock_gc.open_by_key.assert_called_once_with(
            "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        )
        mock_spreadsheet.worksheet.assert_called_once_with("Sheet1")
        mock_worksheet.clear.assert_called_once()
        mock_set_with_dataframe.assert_called_once_with(mock_worksheet, df)
        assert result_url == "https://docs.google.com/spreadsheets/d/abc123/edit#gid=0"

    @patch("app.integrations.sheets_client.gspread.service_account")
    def test_push_dataframe_api_error(self, mock_service_account):
        """Test SheetsPushError is raised when gspread raises APIError."""
        from gspread.exceptions import APIError

        # Arrange
        mock_gc = Mock()
        mock_service_account.return_value = mock_gc

        # Create a proper mock response for APIError
        mock_response = Mock()
        mock_response.json.return_value = {
            "error": {"message": "API quota exceeded", "code": 429}
        }
        mock_gc.open_by_key.side_effect = APIError(mock_response)

        with patch("app.integrations.sheets_client.Path.exists", return_value=True), patch(
            "builtins.open", mock_open_for_configs()
        ):
            client = SheetsClient()

        df = pd.DataFrame({"Name": ["John"], "Age": [30]})

        # Act & Assert
        with pytest.raises(
            SheetsPushError, match="Failed to push DataFrame to Google Sheets"
        ):
            client.push_dataframe(df)

    @patch("app.integrations.sheets_client.gspread.service_account")
    @patch("app.integrations.sheets_client.gspread_dataframe.set_with_dataframe")
    def test_push_dataframe_worksheet_clear_called_before_set(
        self, mock_set_with_dataframe, mock_service_account
    ):
        """Test that worksheet.clear() is called before set_with_dataframe()."""
        # Arrange
        mock_gc = Mock()
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_worksheet.url = "https://example.com/sheet"

        mock_service_account.return_value = mock_gc
        mock_gc.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet

        # Create a call order tracker
        call_order = []
        mock_worksheet.clear.side_effect = lambda: call_order.append("clear")
        mock_set_with_dataframe.side_effect = lambda ws, df: call_order.append(
            "set_with_dataframe"
        )

        with patch("app.integrations.sheets_client.Path.exists", return_value=True), patch(
            "builtins.open", mock_open_for_configs()
        ):
            client = SheetsClient()

        df = pd.DataFrame({"A": [1, 2]})

        # Act
        client.push_dataframe(df)

        # Assert
        assert call_order == ["clear", "set_with_dataframe"]

    def test_sheets_push_error_custom_exception(self):
        """Test that SheetsPushError is a custom exception with proper message."""
        error_msg = "Test error message"
        error = SheetsPushError(error_msg)
        assert str(error) == error_msg
        assert isinstance(error, Exception)


def mock_open_for_configs():
    """Mock file opening for config files (creds.json and settings.toml)."""
    from unittest.mock import mock_open

    def mock_open_side_effect(filepath, mode="r", **kwargs):
        filepath_str = str(filepath)

        if "creds.json" in filepath_str:
            content = json.dumps(
                {
                    "type": "service_account",
                    "project_id": "test-project",
                    "private_key_id": "abc123",
                    "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
                    "client_email": "test@test-project.iam.gserviceaccount.com",
                    "client_id": "123456789",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            )
            return mock_open(read_data=content).return_value
        elif "settings.toml" in filepath_str:
            content = b"""[sheets]
spreadsheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
worksheet_name = "Sheet1"
"""
            return mock_open(read_data=content).return_value

        return mock_open().return_value

    return mock_open_side_effect
