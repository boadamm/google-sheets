"""Test suite for desktop packaging functionality.

Following TDD principles, these tests define the expected behavior
of the desktop build system before implementation.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path
import pytest


class TestDesktopPackaging:
    """Test cases for desktop application packaging."""

    def test_build_executable_exists_after_build_command(self):
        """Test that build command creates the expected executable file."""
        # Determine expected executable name based on platform
        if platform.system() == "Windows":
            expected_executable = "dist/SheetsBot/SheetsBot.exe"
        else:
            expected_executable = "dist/SheetsBot/SheetsBot"

        # Clean any existing build artifacts
        if Path("dist").exists():
            import shutil

            shutil.rmtree("dist")

        # Skip actual build in CI environment to avoid GUI dependencies
        if os.environ.get("CI"):
            pytest.skip("Skipping GUI build test in CI environment")

        # Run the build command
        result = subprocess.run(
            ["make", "build-gui"],
            capture_output=True,
            text=True,
        )

        # Assert build command succeeded
        assert result.returncode == 0, f"Build failed with stderr: {result.stderr}"

        # Assert the expected executable exists
        executable_path = Path(expected_executable)
        assert (
            executable_path.exists()
        ), f"Expected executable not found at: {expected_executable}"

        # Assert it's actually executable (on Unix systems)
        if platform.system() != "Windows":
            assert os.access(
                executable_path, os.X_OK
            ), f"File is not executable: {expected_executable}"

    def test_docs_readme_contains_gui_section(self):
        """Test that docs/README.md contains required GUI desktop app section."""
        readme_path = Path("docs/README.md")

        # Assert the file exists
        assert readme_path.exists(), "docs/README.md does not exist"

        # Read the file content
        content = readme_path.read_text(encoding="utf-8")

        # Assert required heading exists
        assert (
            "GUI Desktop App" in content
        ), "Missing 'GUI Desktop App' heading in docs/README.md"

        # Assert download instruction exists
        assert (
            "Download the latest build" in content
        ), "Missing 'Download the latest build' phrase in docs/README.md"

    def test_pyinstaller_spec_file_exists(self):
        """Test that build/pyinstaller.spec exists with correct configuration."""
        spec_path = Path("build/pyinstaller.spec")

        # Assert the file exists
        assert spec_path.exists(), "build/pyinstaller.spec does not exist"

        # Read the file content
        content = spec_path.read_text(encoding="utf-8")

        # Assert it contains the correct entry point (now using build/main.py)
        assert (
            '"build" / "main.py"' in content
        ), "Missing entry point in pyinstaller.spec"

        # Assert it's configured for single-folder mode (onedir=True)
        assert (
            "onedir=True" in content or "onefile=False" in content
        ), "Should be configured for single-folder mode"

        # Assert noconsole flag is set for clean UX
        assert (
            "--noconsole" in content or "console=False" in content
        ), "Missing noconsole configuration"

    def test_makefile_exists_with_build_tasks(self):
        """Test that Makefile exists with required build and clean tasks."""
        makefile_path = Path("Makefile")

        # Assert the file exists
        assert makefile_path.exists(), "Makefile does not exist"

        # Read the file content
        content = makefile_path.read_text(encoding="utf-8")

        # Assert build-gui target exists
        assert "build-gui:" in content, "Missing build-gui target in Makefile"

        # Assert clean-gui target exists
        assert "clean-gui:" in content, "Missing clean-gui target in Makefile"

        # Assert pyinstaller command is present
        assert "pyinstaller" in content, "Missing pyinstaller command in Makefile"

        # Assert CI guard is present (POSIX shell syntax)
        assert (
            'if [ "$$CI" = "" ]' in content or "ifndef CI" in content
        ), "Missing CI guard in Makefile"

    def test_gui_demo_gif_exists(self):
        """Test that GUI demo GIF exists in docs/img/ directory."""
        gif_path = Path("docs/img/gui_demo.gif")

        # Assert the file exists
        assert gif_path.exists(), "docs/img/gui_demo.gif does not exist"

        # Assert it's not too large (≤ 5MB as specified)
        file_size = gif_path.stat().st_size
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        assert (
            file_size <= max_size
        ), f"GIF file too large: {file_size} bytes (max: {max_size})"

    def test_build_directory_structure(self):
        """Test that build directory has the expected structure."""
        build_dir = Path("build")

        # Assert build directory exists
        assert build_dir.exists(), "build/ directory does not exist"

        # Assert it contains pyinstaller.spec
        spec_file = build_dir / "pyinstaller.spec"
        assert spec_file.exists(), "build/pyinstaller.spec does not exist"

    def test_requirements_includes_pyinstaller(self):
        """Test that pyinstaller is available for building."""
        # Try to import pyinstaller or run pyinstaller --version
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import PyInstaller; print(PyInstaller.__version__)",
                ],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, "PyInstaller not available for import"
        except Exception:
            # Alternative: check if pyinstaller command exists
            result = subprocess.run(
                ["pyinstaller", "--version"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, "PyInstaller command not available"
