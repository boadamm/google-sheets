"""Slack notification module for posting diff summaries.

This module provides functionality to send formatted diff summaries to Slack
channels using Incoming Webhooks with rich message formatting.
"""

import logging
from pathlib import Path
from typing import Dict, Any
import requests
import tomli


class SlackNotifier:
    """Posts diff summaries to Slack channels using Incoming Webhooks.

    This class formats and sends concise diff summaries to Slack with
    rich formatting including added/updated/deleted counts and sheet URLs.
    """

    def __init__(
        self,
        webhook_url: str,
        channel: str,
        username: str = "Sheets-Bot",
        icon_emoji: str = ":robot_face:",
    ):
        """Initialize SlackNotifier with webhook configuration.

        Args:
            webhook_url: Slack Incoming Webhook URL
            channel: Target Slack channel (e.g., "#general")
            username: Bot username for messages (default: "Sheets-Bot")
            icon_emoji: Bot icon emoji (default: ":robot_face:")
        """
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username
        self.icon_emoji = icon_emoji

    def post_summary(self, diff: Dict[str, int], sheet_url: str) -> bool:
        """Post diff summary to Slack channel.

        Args:
            diff: Dictionary with added/updated/deleted counts
            sheet_url: URL to the Google Sheets document

        Returns:
            bool: True if message sent successfully (HTTP 200), False otherwise
        """
        try:
            # Build message payload
            payload = self._build_payload(diff, sheet_url)

            # Send POST request to webhook URL
            response = requests.post(self.webhook_url, json=payload)

            if response.status_code == 200:
                return True
            else:
                logging.warning(
                    f"Slack notification failed with status {response.status_code}: {response.text}"
                )
                return False

        except Exception as e:
            logging.warning(f"Slack notification failed with exception: {str(e)}")
            return False

    def _build_payload(self, diff: Dict[str, int], sheet_url: str) -> Dict[str, Any]:
        """Build Slack message payload with formatted diff summary.

        Args:
            diff: Dictionary with added/updated/deleted counts
            sheet_url: URL to the Google Sheets document

        Returns:
            dict: Formatted Slack webhook payload
        """
        # Format diff counts as "+added / updated / deleted"
        diff_text = f"+{diff['added']} / {diff['updated']} / {diff['deleted']}"

        # Build rich attachment with diff details and sheet link
        attachment_text = (
            f"📊 *Changes*: {diff_text}\n"
            f"🔗 *Sheet*: <{sheet_url}|View Updated Sheet>"
        )

        payload = {
            "text": "✅ Sheets Bot Sync Completed",
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "attachments": [
                {
                    "color": "good",
                    "text": attachment_text,
                    "mrkdwn_in": ["text"],
                }
            ],
        }

        return payload

    @classmethod
    def from_settings(
        cls, settings_path: Path = Path("config/settings.toml")
    ) -> "SlackNotifier":
        """Create SlackNotifier from TOML settings file.

        Args:
            settings_path: Path to settings.toml file

        Returns:
            SlackNotifier: Configured instance

        Raises:
            FileNotFoundError: If settings file doesn't exist
            KeyError: If required Slack configuration is missing
        """
        if not settings_path.exists():
            raise FileNotFoundError(f"Settings file not found: {settings_path}")

        with open(settings_path, "rb") as f:
            config = tomli.load(f)

        slack_config = config["slack"]

        return cls(
            webhook_url=slack_config["webhook_url"],
            channel=slack_config.get("channel", "#general"),
            username=slack_config.get("username", "Sheets-Bot"),
            icon_emoji=slack_config.get("icon_emoji", ":robot_face:"),
        )
