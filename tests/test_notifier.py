"""Test module for Slack notification functionality.

This module contains tests for the SlackNotifier class that posts diff summaries
to Slack channels using Incoming Webhooks.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from app.notifier import SlackNotifier


class TestSlackNotifier:
    """Test cases for the SlackNotifier class."""

    def test_slack_notifier_initialization(self):
        """Test that SlackNotifier initializes correctly with required parameters."""
        webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
        channel = "#general"

        notifier = SlackNotifier(webhook_url=webhook_url, channel=channel)

        assert notifier.webhook_url == webhook_url
        assert notifier.channel == channel
        assert notifier.username == "Sheets-Bot"  # default
        assert notifier.icon_emoji == ":robot_face:"  # default

    def test_slack_notifier_initialization_with_custom_params(self):
        """Test that SlackNotifier initializes with custom username and icon."""
        webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
        channel = "#notifications"
        username = "Custom-Bot"
        icon_emoji = ":gear:"

        notifier = SlackNotifier(
            webhook_url=webhook_url,
            channel=channel,
            username=username,
            icon_emoji=icon_emoji,
        )

        assert notifier.webhook_url == webhook_url
        assert notifier.channel == channel
        assert notifier.username == username
        assert notifier.icon_emoji == icon_emoji

    @patch("requests.post")
    def test_post_summary_success_returns_true(self, mock_post):
        """Test post_summary returns True on HTTP 200 response."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Setup notifier
        webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
        notifier = SlackNotifier(webhook_url=webhook_url, channel="#general")

        # Test data
        diff = {"added": 3, "updated": 1, "deleted": 0}
        sheet_url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0"

        # Execute
        result = notifier.post_summary(diff, sheet_url)

        # Assertions
        assert result is True
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_post_summary_payload_structure(self, mock_post):
        """Test that post_summary sends correct payload structure to Slack."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Setup notifier
        webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
        notifier = SlackNotifier(webhook_url=webhook_url, channel="#general")

        # Test data
        diff = {"added": 3, "updated": 1, "deleted": 0}
        sheet_url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0"

        # Execute
        notifier.post_summary(diff, sheet_url)

        # Get the call arguments
        call_args = mock_post.call_args
        assert call_args[0][0] == webhook_url  # URL argument

        # Check JSON payload
        payload = call_args[1]["json"]

        # Check main message text
        assert payload["text"] == "✅ Sheets Bot Sync Completed"
        assert payload["channel"] == "#general"
        assert payload["username"] == "Sheets-Bot"
        assert payload["icon_emoji"] == ":robot_face:"

        # Check attachments
        assert len(payload["attachments"]) == 1
        attachment = payload["attachments"][0]
        assert "+3 / 1 / 0" in attachment["text"]
        assert sheet_url in attachment["text"]

    @patch("requests.post")
    def test_post_summary_formats_diff_correctly(self, mock_post):
        """Test that diff counts are formatted correctly in different scenarios."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Setup notifier
        webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
        notifier = SlackNotifier(webhook_url=webhook_url, channel="#general")

        # Test different diff scenarios
        test_cases = [
            ({"added": 0, "updated": 0, "deleted": 0}, "+0 / 0 / 0"),
            ({"added": 5, "updated": 0, "deleted": 2}, "+5 / 0 / 2"),
            ({"added": 10, "updated": 15, "deleted": 3}, "+10 / 15 / 3"),
        ]

        sheet_url = "https://docs.google.com/spreadsheets/d/test/edit"

        for diff, expected_format in test_cases:
            # Reset mock
            mock_post.reset_mock()

            # Execute
            notifier.post_summary(diff, sheet_url)

            # Check payload
            payload = mock_post.call_args[1]["json"]
            attachment_text = payload["attachments"][0]["text"]
            assert expected_format in attachment_text

    @patch("requests.post")
    @patch("logging.warning")
    def test_post_summary_non_200_returns_false_and_logs_warning(
        self, mock_log, mock_post
    ):
        """Test post_summary returns False on non-200 response and logs warning."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_post.return_value = mock_response

        # Setup notifier
        webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
        notifier = SlackNotifier(webhook_url=webhook_url, channel="#general")

        # Test data
        diff = {"added": 1, "updated": 0, "deleted": 0}
        sheet_url = "https://docs.google.com/spreadsheets/d/test/edit"

        # Execute
        result = notifier.post_summary(diff, sheet_url)

        # Assertions
        assert result is False
        mock_log.assert_called_once()
        # Check that warning message contains status code
        warning_call = mock_log.call_args[0][0]
        assert "404" in warning_call

    @patch("requests.post")
    @patch("logging.warning")
    def test_post_summary_request_exception_returns_false_and_logs(
        self, mock_log, mock_post
    ):
        """Test post_summary handles request exceptions gracefully."""
        # Setup mock to raise exception
        mock_post.side_effect = Exception("Connection error")

        # Setup notifier
        webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
        notifier = SlackNotifier(webhook_url=webhook_url, channel="#general")

        # Test data
        diff = {"added": 1, "updated": 0, "deleted": 0}
        sheet_url = "https://docs.google.com/spreadsheets/d/test/edit"

        # Execute
        result = notifier.post_summary(diff, sheet_url)

        # Assertions
        assert result is False
        mock_log.assert_called_once()

    def test_from_settings_class_method_exists(self):
        """Test that from_settings class method exists and can be called."""
        # Test that the method exists and is callable
        assert hasattr(SlackNotifier, "from_settings")
        assert callable(getattr(SlackNotifier, "from_settings"))

    @patch("pathlib.Path.exists")
    @patch("builtins.open")
    @patch("tomli.load")
    def test_from_settings_loads_from_toml_file(
        self, mock_tomli, mock_open, mock_exists
    ):
        """Test from_settings loads configuration from TOML file."""
        # Setup mocks
        mock_exists.return_value = True
        mock_config = {
            "slack": {
                "webhook_url": "https://hooks.slack.com/services/TEST/WEBHOOK/URL",
                "channel": "#test-channel",
                "username": "Test-Bot",
                "icon_emoji": ":test:",
            }
        }
        mock_tomli.return_value = mock_config

        # Execute
        notifier = SlackNotifier.from_settings(Path("config/settings.toml"))

        # Assertions
        assert (
            notifier.webhook_url == "https://hooks.slack.com/services/TEST/WEBHOOK/URL"
        )
        assert notifier.channel == "#test-channel"
        assert notifier.username == "Test-Bot"
        assert notifier.icon_emoji == ":test:"

    @patch("pathlib.Path.exists")
    def test_from_settings_missing_file_raises_error(self, mock_exists):
        """Test from_settings raises error when settings file doesn't exist."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            SlackNotifier.from_settings(Path("nonexistent/settings.toml"))
