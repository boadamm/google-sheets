"""
Test suite for README badges and download links functionality.

This module tests Sprint 6 – T17 requirements:
- Latest Release badge presence in README.md
- Direct download links for Windows and Linux artifacts
- Status documentation update

Tests follow TDD/BDD principles with descriptive assertions.
"""

import pytest
from pathlib import Path


class TestReadmeBadges:
    """Test README.md contains required release badges and download links."""

    @pytest.fixture
    def readme_content(self):
        """Load README.md content for testing."""
        readme_path = Path(__file__).parent.parent / "README.md"
        if not readme_path.exists():
            pytest.fail(f"README.md not found at {readme_path}")
        return readme_path.read_text(encoding="utf-8")

    @pytest.fixture
    def status_content(self):
        """Load docs/status.md content for testing."""
        status_path = Path(__file__).parent.parent / "docs" / "status.md"
        if not status_path.exists():
            pytest.fail(f"docs/status.md not found at {status_path}")
        return status_path.read_text(encoding="utf-8")

    def test_readme_contains_latest_release_badge(self, readme_content):
        """Assert README.md contains a Shields.io badge with alt text 'Latest Release'."""
        # Check for the exact badge format we expect
        expected_badge_pattern = "[![Latest Release]"
        assert expected_badge_pattern in readme_content, (
            f"README.md must contain a badge starting with '{expected_badge_pattern}'. "
            "Expected format: [![Latest Release](https://img.shields.io/github/v/release/...)](...)"
        )

        # Additional check for the shields.io URL pattern
        shields_pattern = "https://img.shields.io/github/v/release/"
        assert (
            shields_pattern in readme_content
        ), f"README.md must contain shields.io release badge URL pattern '{shields_pattern}'"

    def test_readme_contains_windows_download_link(self, readme_content):
        """Assert README.md contains direct link ending with 'SheetsBot-Windows-signed.zip'."""
        windows_link_pattern = "SheetsBot-Windows-signed.zip"
        assert windows_link_pattern in readme_content, (
            f"README.md must contain a download link ending with '{windows_link_pattern}'. "
            "This should be a direct link to the Windows signed release artifact."
        )

    def test_readme_contains_linux_download_link(self, readme_content):
        """Assert README.md contains direct link ending with 'SheetsBot-Linux.zip'."""
        linux_link_pattern = "SheetsBot-Linux.zip"
        assert linux_link_pattern in readme_content, (
            f"README.md must contain a download link ending with '{linux_link_pattern}'. "
            "This should be a direct link to the Linux release artifact."
        )

    def test_readme_downloads_section_exists(self, readme_content):
        """Assert README.md contains a Downloads section with proper structure."""
        downloads_section = "## Downloads"
        assert (
            downloads_section in readme_content or "Downloads" in readme_content
        ), "README.md must contain a Downloads section for release artifacts"

    def test_status_md_contains_sprint6_t17_entry(self, status_content):
        """Assert docs/status.md includes the Sprint 6 – T17 completion entry."""
        expected_status_line = "Sprint 6 – T17 badges & download links added"
        assert expected_status_line in status_content, (
            f"docs/status.md must include the line '{expected_status_line}' "
            "to track completion of this sprint task."
        )

    def test_badge_links_to_latest_release(self, readme_content):
        """Assert the Latest Release badge links to GitHub releases/latest page."""
        # Look for the complete badge with both image and link
        releases_latest_pattern = "/releases/latest"
        assert (
            releases_latest_pattern in readme_content
        ), "The Latest Release badge must link to '/releases/latest' page for direct access"

    def test_download_links_are_direct_github_urls(self, readme_content):
        """Assert download links are direct GitHub release URLs, not relative paths."""
        # Check that we have proper GitHub release URLs
        github_releases_pattern = "github.com"

        # This test ensures we have proper direct links, not just filenames
        if "SheetsBot-Windows-signed.zip" in readme_content:
            # If we have the Windows link, it should be a proper GitHub URL
            lines_with_windows = [
                line
                for line in readme_content.split("\n")
                if "SheetsBot-Windows-signed.zip" in line
            ]
            assert any(
                github_releases_pattern in line for line in lines_with_windows
            ), "Windows download link must be a direct GitHub releases URL, not a relative path"

        if "SheetsBot-Linux.zip" in readme_content:
            # If we have the Linux link, it should be a proper GitHub URL
            lines_with_linux = [
                line
                for line in readme_content.split("\n")
                if "SheetsBot-Linux.zip" in line
            ]
            assert any(
                github_releases_pattern in line for line in lines_with_linux
            ), "Linux download link must be a direct GitHub releases URL, not a relative path"
