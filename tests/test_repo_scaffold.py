"""
Test suite for repository scaffolding structure.

Following TDD principles, these tests define the expected repository structure
and configuration that needs to be implemented.
"""

import tomli
from pathlib import Path


class TestRepositoryStructure:
    """Test that required directories and files exist."""

    def test_app_directory_exists(self):
        """Test that app/ directory exists."""
        assert Path("app").exists(), "app/ directory should exist"
        assert Path("app").is_dir(), "app/ should be a directory"

    def test_config_directory_exists(self):
        """Test that config/ directory exists."""
        assert Path("config").exists(), "config/ directory should exist"
        assert Path("config").is_dir(), "config/ should be a directory"

    def test_docs_directory_exists(self):
        """Test that docs/ directory exists."""
        assert Path("docs").exists(), "docs/ directory should exist"
        assert Path("docs").is_dir(), "docs/ should be a directory"

    def test_samples_directory_exists(self):
        """Test that samples/ directory exists."""
        assert Path("samples").exists(), "samples/ directory should exist"
        assert Path("samples").is_dir(), "samples/ should be a directory"

    def test_app_init_exists(self):
        """Test that app/__init__.py exists."""
        init_file = Path("app/__init__.py")
        assert init_file.exists(), "app/__init__.py should exist"
        assert init_file.is_file(), "app/__init__.py should be a file"

    def test_tests_init_exists(self):
        """Test that tests/__init__.py exists."""
        init_file = Path("tests/__init__.py")
        assert init_file.exists(), "tests/__init__.py should exist"
        assert init_file.is_file(), "tests/__init__.py should be a file"


class TestConfigurationFile:
    """Test that configuration file exists and has required structure."""

    def test_settings_toml_exists(self):
        """Test that config/settings.toml exists."""
        settings_file = Path("config/settings.toml")
        assert settings_file.exists(), "config/settings.toml should exist"
        assert settings_file.is_file(), "config/settings.toml should be a file"

    def test_settings_toml_loads(self):
        """Test that config/settings.toml can be loaded as TOML."""
        settings_file = Path("config/settings.toml")
        with open(settings_file, "rb") as f:
            config = tomli.load(f)
        assert isinstance(config, dict), "Settings should load as dictionary"

    def test_settings_has_sheets_section(self):
        """Test that settings has sheets configuration section."""
        settings_file = Path("config/settings.toml")
        with open(settings_file, "rb") as f:
            config = tomli.load(f)

        assert "sheets" in config, "Settings should have [sheets] section"
        assert (
            "spreadsheet_id" in config["sheets"]
        ), "sheets section should have spreadsheet_id"
        assert (
            "worksheet_name" in config["sheets"]
        ), "sheets section should have worksheet_name"

    def test_settings_has_slack_section(self):
        """Test that settings has slack configuration section."""
        settings_file = Path("config/settings.toml")
        with open(settings_file, "rb") as f:
            config = tomli.load(f)

        assert "slack" in config, "Settings should have [slack] section"
        assert "webhook_url" in config["slack"], "slack section should have webhook_url"

    def test_settings_has_watcher_section(self):
        """Test that settings has watcher configuration section."""
        settings_file = Path("config/settings.toml")
        with open(settings_file, "rb") as f:
            config = tomli.load(f)

        assert "watcher" in config, "Settings should have [watcher] section"
        assert "folder" in config["watcher"], "watcher section should have folder"


class TestRequirementsFile:
    """Test that requirements.txt exists and has correct dependencies."""

    def test_requirements_txt_exists(self):
        """Test that requirements.txt exists."""
        requirements_file = Path("requirements.txt")
        assert requirements_file.exists(), "requirements.txt should exist"
        assert requirements_file.is_file(), "requirements.txt should be a file"

    def test_requirements_has_watchdog(self):
        """Test that requirements.txt contains watchdog with version."""
        requirements_file = Path("requirements.txt")
        content = requirements_file.read_text()
        assert (
            "watchdog==" in content
        ), "requirements.txt should contain watchdog with pinned version"

    def test_requirements_has_pandas(self):
        """Test that requirements.txt contains pandas with version."""
        requirements_file = Path("requirements.txt")
        content = requirements_file.read_text()
        assert (
            "pandas==" in content
        ), "requirements.txt should contain pandas with pinned version"

    def test_requirements_has_numpy(self):
        """Test that requirements.txt contains numpy with version."""
        requirements_file = Path("requirements.txt")
        content = requirements_file.read_text()
        assert (
            "numpy==" in content
        ), "requirements.txt should contain numpy with pinned version"
