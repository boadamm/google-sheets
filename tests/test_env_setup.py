"""
Tests for environment setup validation.
Ensures all required meta-files exist and contain expected content.
"""

import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


class TestEnvironmentSetup:
    """Test suite for validating development environment setup."""

    def test_environment_yml_exists(self):
        """Test that environment.yml exists at repo root."""
        env_file = PROJECT_ROOT / "environment.yml"
        assert env_file.exists(), "environment.yml must exist at repo root"

    def test_environment_yml_contains_python_311(self):
        """Test that environment.yml declares python=3.11 under dependencies."""
        env_file = PROJECT_ROOT / "environment.yml"
        assert env_file.exists(), "environment.yml must exist"

        with open(env_file, "r") as f:
            env_config = yaml.safe_load(f)

        assert (
            "dependencies" in env_config
        ), "environment.yml must have dependencies section"
        dependencies = env_config["dependencies"]

        # Check for python=3.11 in dependencies
        python_deps = [
            dep
            for dep in dependencies
            if isinstance(dep, str) and dep.startswith("python=")
        ]
        assert len(python_deps) > 0, "python dependency must be specified"
        assert any(
            "python=3.11" in dep for dep in python_deps
        ), "python=3.11 must be specified in dependencies"

    def test_gitignore_exists_and_contains_patterns(self):
        """Test that .gitignore exists and contains required patterns."""
        gitignore_file = PROJECT_ROOT / ".gitignore"
        assert gitignore_file.exists(), ".gitignore must exist at repo root"

        with open(gitignore_file, "r") as f:
            gitignore_content = f.read()

        required_patterns = [
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            "*.egg-info",
            "venv/",
            ".env",
            ".idea/",
        ]

        for pattern in required_patterns:
            assert (
                pattern in gitignore_content
            ), f"Pattern '{pattern}' must be in .gitignore"

    def test_cursorrules_exists_and_contains_python_style(self):
        """Test that .cursorrules exists and includes PYTHON_STYLE: key string."""
        cursorrules_file = PROJECT_ROOT / ".cursorrules"
        assert cursorrules_file.exists(), ".cursorrules must exist at repo root"

        with open(cursorrules_file, "r") as f:
            cursorrules_content = f.read()

        assert (
            "PYTHON_STYLE:" in cursorrules_content
        ), ".cursorrules must include 'PYTHON_STYLE:' key string"

    def test_readme_has_quick_start_section(self):
        """Test that README.md has a section titled 'Quick Start (Conda on WSL)'."""
        readme_file = PROJECT_ROOT / "README.md"
        assert readme_file.exists(), "README.md must exist at repo root"

        with open(readme_file, "r") as f:
            readme_content = f.read()

        assert (
            "Quick Start (Conda on WSL)" in readme_content
        ), "README.md must have 'Quick Start (Conda on WSL)' section"
