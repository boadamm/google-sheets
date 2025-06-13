"""Tests for service account documentation requirements.

These tests verify that the documentation contains the required sections
and content for Google Service Account setup, following TDD principles.
"""

from pathlib import Path


class TestServiceAccountDocs:
    """Test suite for service account documentation requirements."""

    def test_docs_readme_contains_required_headings(self):
        """Assert that docs/README.md contains required service account headings."""
        docs_readme = Path("docs/README.md")
        assert docs_readme.exists(), "docs/README.md file should exist"

        content = docs_readme.read_text()

        # Test for required headings
        assert (
            "Create Service Account" in content
        ), "docs/README.md should contain 'Create Service Account' heading"
        assert (
            "Share the Sheet" in content
        ), "docs/README.md should contain 'Share the Sheet' heading"
        assert (
            "Save creds.json" in content
        ), "docs/README.md should contain 'Save creds.json' heading"

    def test_docs_readme_contains_google_sheets_setup_section(self):
        """Assert that docs/README.md contains Google Sheets Setup section."""
        docs_readme = Path("docs/README.md")
        assert docs_readme.exists(), "docs/README.md file should exist"

        content = docs_readme.read_text()

        # Test for main section heading
        assert (
            "Google Sheets Setup (Free Tier)" in content
        ), "docs/README.md should contain 'Google Sheets Setup (Free Tier)' section"

    def test_docs_readme_contains_troubleshooting_section(self):
        """Assert that docs/README.md contains Troubleshooting subsection."""
        docs_readme = Path("docs/README.md")
        assert docs_readme.exists(), "docs/README.md file should exist"

        content = docs_readme.read_text()

        # Test for troubleshooting section
        assert (
            "Troubleshooting" in content
        ), "docs/README.md should contain 'Troubleshooting' subsection"
        assert (
            "APIError: 403" in content
        ), "docs/README.md should contain 'APIError: 403' troubleshooting info"

    def test_docs_readme_contains_verification_command(self):
        """Assert that docs/README.md contains the verification command."""
        docs_readme = Path("docs/README.md")
        assert docs_readme.exists(), "docs/README.md file should exist"

        content = docs_readme.read_text()

        # Test for verification command
        assert (
            "python cli.py --file samples/data.csv --push" in content
        ), "docs/README.md should contain verification command with --push flag"

    def test_status_md_contains_sprint3_t8_entry(self):
        """Assert that docs/status.md includes Sprint 3 T8 service-account docs entry."""
        status_md = Path("docs/status.md")
        assert status_md.exists(), "docs/status.md file should exist"

        content = status_md.read_text()

        # Test for specific sprint entry
        assert (
            "Sprint 3 – T8 service-account docs finished" in content
        ), "docs/status.md should contain 'Sprint 3 – T8 service-account docs finished' line"

    def test_docs_readme_contains_api_enable_instructions(self):
        """Assert that docs/README.md contains Google Sheets API enabling instructions."""
        docs_readme = Path("docs/README.md")
        assert docs_readme.exists(), "docs/README.md file should exist"

        content = docs_readme.read_text()

        # Test for API enabling instructions
        assert (
            "Enabling the Google Sheets API" in content
        ), "docs/README.md should contain instructions for enabling Google Sheets API"

    def test_docs_readme_contains_json_key_download_instructions(self):
        """Assert that docs/README.md contains JSON key download instructions."""
        docs_readme = Path("docs/README.md")
        assert docs_readme.exists(), "docs/README.md file should exist"

        content = docs_readme.read_text()

        # Test for JSON key download instructions
        assert (
            "downloading the JSON key" in content
        ), "docs/README.md should contain instructions for downloading JSON key"

    def test_docs_readme_contains_config_path_info(self):
        """Assert that docs/README.md contains config/creds.json path information."""
        docs_readme = Path("docs/README.md")
        assert docs_readme.exists(), "docs/README.md file should exist"

        content = docs_readme.read_text()

        # Test for config path information
        assert (
            "config/creds.json" in content
        ), "docs/README.md should mention config/creds.json file path"
