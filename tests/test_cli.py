"""Test suite for CLI functionality.

Following TDD principles, these tests define the expected behavior
of the command-line interface before implementation.
"""

import subprocess
import sys
from pathlib import Path
import pytest
import tempfile


class TestCLI:
    """Test cases for the CLI entry point."""

    def test_cli_module_importable(self):
        """Test that the CLI module can be imported."""
        # This test will fail until cli.py is created
        import cli  # noqa: F401

    @pytest.mark.parametrize(
        "sample_file",
        [
            "samples/data.csv",
            "samples/data.xlsx",
        ],
    )
    def test_cli_success_with_valid_files(self, sample_file):
        """Test CLI exits with code 0 and prints DataFrame for valid files."""
        # Run the CLI with a valid sample file
        result = subprocess.run(
            [sys.executable, "cli.py", "--file", sample_file, "--once"],
            capture_output=True,
            text=True,
        )

        # Should exit successfully
        assert result.returncode == 0, f"CLI failed with stderr: {result.stderr}"

        # Should contain column headers in stdout
        # We expect at least 3 columns based on requirements
        output_lines = result.stdout.strip().split("\n")
        assert len(output_lines) > 0, "No output from CLI"

        # Should contain data from the cleaned DataFrame
        assert any(
            "Name" in line or "Age" in line or "City" in line for line in output_lines
        ), f"Expected column headers not found in output: {result.stdout}"

    def test_cli_error_with_invalid_file(self):
        """Test CLI exits with non-zero code for invalid file paths."""
        # Test with non-existent file
        result = subprocess.run(
            [sys.executable, "cli.py", "--file", "nonexistent.csv", "--once"],
            capture_output=True,
            text=True,
        )

        # Should exit with error code
        assert result.returncode != 0, "CLI should fail with invalid file"

        # Should contain helpful error message in stderr
        assert (
            "error" in result.stderr.lower() or "not found" in result.stderr.lower()
        ), f"Expected error message in stderr: {result.stderr}"

    def test_cli_error_with_invalid_extension(self):
        """Test CLI exits with error for unsupported file extensions."""
        # Create a temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"some content")
            temp_path = temp_file.name

        try:
            result = subprocess.run(
                [sys.executable, "cli.py", "--file", temp_path, "--once"],
                capture_output=True,
                text=True,
            )

            # Should exit with error code
            assert result.returncode != 0, "CLI should fail with unsupported file type"

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_cli_help_option(self):
        """Test CLI --help option works."""
        result = subprocess.run(
            [sys.executable, "cli.py", "--help"],
            capture_output=True,
            text=True,
        )

        # Should exit successfully
        assert result.returncode == 0, f"CLI help failed: {result.stderr}"

        # Should contain usage information
        assert "--file" in result.stdout, "Help should mention --file option"
        assert "--once" in result.stdout, "Help should mention --once option"
        assert "--watch" in result.stdout, "Help should mention --watch option"

    def test_cli_requires_file_option(self):
        """Test CLI fails when --file option is not provided."""
        result = subprocess.run(
            [sys.executable, "cli.py", "--once"],
            capture_output=True,
            text=True,
        )

        # Should exit with error code
        assert result.returncode != 0, "CLI should require --file option"

        # Should contain helpful error message about missing file option
        assert (
            "file" in result.stderr.lower() or "required" in result.stderr.lower()
        ), f"Expected missing file error in stderr: {result.stderr}"

    def test_cli_dataframe_formatting(self):
        """Test that CLI output is properly formatted for DataFrame display."""
        result = subprocess.run(
            [sys.executable, "cli.py", "--file", "samples/data.csv", "--once"],
            capture_output=True,
            text=True,
        )

        # Should exit successfully
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        # Should have readable DataFrame output (not just raw data)
        output = result.stdout
        assert len(output.strip()) > 0, "Output should not be empty"

        # Should look like a formatted DataFrame (contains spaces or table structure)
        assert (
            "  " in output or "|" in output or "-" in output
        ), f"Output doesn't appear to be formatted DataFrame: {output}"
