"""Test suite for CLI push functionality.

Following TDD principles, these tests define the expected behavior
of the command-line interface push feature before implementation.
"""

import subprocess
import sys
import os
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock


class TestCLIPush:
    """Test cases for the CLI push functionality."""

    @pytest.mark.parametrize(
        "sample_file",
        [
            "samples/data.csv",
            "samples/data.xlsx",
        ],
    )
    def test_cli_push_success_with_valid_files(self, sample_file):
        """Test CLI exits with code 0 and prints push URL for valid files with --push flag."""
        # Set environment variable to enable testing mode
        test_env = os.environ.copy()
        test_env["PYTEST_CURRENT_TEST"] = "test_cli_push_success"

        with patch("cli.SheetsClient") as mock_client_class:
            # Mock the SheetsClient class and its push_dataframe method
            mock_client = MagicMock()
            mock_client.push_dataframe.return_value = "https://fake.url/tab"
            mock_client_class.return_value = mock_client

            # Create test script that includes the mock
            test_script = f"""
import sys
sys.path.insert(0, '.')
from unittest.mock import patch, MagicMock
import cli

# Mock SheetsClient
with patch('cli.SheetsClient') as mock_client_class:
    mock_client = MagicMock()
    mock_client.push_dataframe.return_value = "https://fake.url/tab"
    mock_client_class.return_value = mock_client
    
    # Call the CLI function directly with args
    sys.argv = ['cli.py', '--file', '{sample_file}', '--push']
    cli.main()
"""

            # Write test script to temporary file
            with open("/tmp/test_cli_push.py", "w") as f:
                f.write(test_script)

            # Run the test script
            result = subprocess.run(
                [sys.executable, "/tmp/test_cli_push.py"],
                capture_output=True,
                text=True,
                env=test_env,
            )

            # Clean up
            Path("/tmp/test_cli_push.py").unlink(missing_ok=True)

            # Should exit successfully
            assert result.returncode == 0, f"CLI failed with stderr: {result.stderr}"

            # Should contain push success message in stdout
            assert (
                "Data pushed to:" in result.stdout
            ), f"Expected push message not found in: {result.stdout}"
            assert (
                "https://fake.url/tab" in result.stdout
            ), f"Expected URL not found in: {result.stdout}"

    @pytest.mark.parametrize(
        "sample_file",
        [
            "samples/data.csv",
            "samples/data.xlsx",
        ],
    )
    def test_cli_push_calls_sheets_client_with_dataframe(self, sample_file):
        """Test that CLI calls SheetsClient.push_dataframe exactly once with a DataFrame."""
        # Set environment variable to enable testing mode
        test_env = os.environ.copy()
        test_env["PYTEST_CURRENT_TEST"] = "test_cli_push_calls"

        # Create test script that includes the mock and verification
        test_script = f"""
import sys
sys.path.insert(0, '.')
from unittest.mock import patch, MagicMock
import pandas as pd
import cli

# Mock SheetsClient
with patch('cli.SheetsClient') as mock_client_class:
    mock_client = MagicMock()
    mock_client.push_dataframe.return_value = "https://fake.url/tab"
    mock_client_class.return_value = mock_client
    
    # Call the CLI function directly with args
    sys.argv = ['cli.py', '--file', '{sample_file}', '--push']
    try:
        cli.main()
    except SystemExit:
        pass
    
    # Verify that push_dataframe was called exactly once
    assert mock_client.push_dataframe.call_count == 1, f"Expected push_dataframe to be called once, but was called {{mock_client.push_dataframe.call_count}} times"
    
    # Verify the argument passed was a DataFrame
    args, kwargs = mock_client.push_dataframe.call_args
    assert len(args) == 1, "Expected exactly one argument to push_dataframe"
    assert isinstance(args[0], pd.DataFrame), f"Expected DataFrame argument, got {{type(args[0])}}"
    
    # Verify DataFrame has expected structure
    df = args[0]
    expected_columns = ["Name", "Age", "City"]
    assert list(df.columns) == expected_columns, f"Expected columns {{expected_columns}}, got {{list(df.columns)}}"
    assert len(df) == 3, f"Expected 3 rows, got {{len(df)}}"
    
    print("All assertions passed")
"""

        # Write test script to temporary file
        with open("/tmp/test_cli_push_verify.py", "w") as f:
            f.write(test_script)

        # Run the test script
        result = subprocess.run(
            [sys.executable, "/tmp/test_cli_push_verify.py"],
            capture_output=True,
            text=True,
            env=test_env,
        )

        # Clean up
        Path("/tmp/test_cli_push_verify.py").unlink(missing_ok=True)

        # Should exit successfully
        assert result.returncode == 0, f"CLI failed with stderr: {result.stderr}"

        # Should contain verification message
        assert (
            "All assertions passed" in result.stdout
        ), f"Expected verification message not found in: {result.stdout}"

    def test_cli_no_push_preserves_current_behavior(self):
        """Test that CLI without --push flag preserves current behavior (no push operation)."""
        # Run the CLI without push flag (default behavior)
        result = subprocess.run(
            [sys.executable, "cli.py", "--file", "samples/data.csv", "--once"],
            capture_output=True,
            text=True,
        )

        # Should exit successfully
        assert result.returncode == 0, f"CLI failed with stderr: {result.stderr}"

        # Should contain DataFrame in stdout (current behavior)
        assert "Name" in result.stdout, "Expected DataFrame output"
        assert "John Doe" in result.stdout, "Expected data from DataFrame"

        # Should NOT contain push message
        assert (
            "Data pushed to:" not in result.stdout
        ), "Should not contain push message without --push flag"

    def test_cli_push_handles_sheets_push_error(self):
        """Test CLI exits with code 1 and prints error when SheetsPushError occurs."""
        # Create test script that raises SheetsPushError
        test_script = """
import sys
sys.path.insert(0, '.')
from unittest.mock import patch, MagicMock
from app.sheets_client import SheetsPushError
import cli

# Mock SheetsClient to raise error
with patch('cli.SheetsClient') as mock_client_class:
    mock_client = MagicMock()
    mock_client.push_dataframe.side_effect = SheetsPushError("Failed to authenticate with Google Sheets")
    mock_client_class.return_value = mock_client
    
    # Call the CLI function directly with args
    sys.argv = ['cli.py', '--file', 'samples/data.csv', '--push']
    cli.main()
"""

        # Write test script to temporary file
        with open("/tmp/test_cli_push_error.py", "w") as f:
            f.write(test_script)

        # Run the test script
        result = subprocess.run(
            [sys.executable, "/tmp/test_cli_push_error.py"],
            capture_output=True,
            text=True,
        )

        # Clean up
        Path("/tmp/test_cli_push_error.py").unlink(missing_ok=True)

        # Should exit with error code
        assert result.returncode == 1, f"Expected exit code 1, got {result.returncode}"

        # Should contain SheetsPushError in stderr
        assert (
            "SheetsPushError" in result.stderr
        ), f"Expected SheetsPushError in stderr: {result.stderr}"

    def test_cli_push_handles_invalid_credentials_file(self):
        """Test CLI exits with non-zero code when credentials file is invalid."""
        # Create test script that raises FileNotFoundError
        test_script = """
import sys
sys.path.insert(0, '.')
from unittest.mock import patch
import cli

# Mock SheetsClient initialization to raise FileNotFoundError
with patch('cli.SheetsClient') as mock_client_class:
    mock_client_class.side_effect = FileNotFoundError("Credentials file not found: config/creds.json")
    
    # Call the CLI function directly with args
    sys.argv = ['cli.py', '--file', 'samples/data.csv', '--push']
    cli.main()
"""

        # Write test script to temporary file
        with open("/tmp/test_cli_push_creds.py", "w") as f:
            f.write(test_script)

        # Run the test script
        result = subprocess.run(
            [sys.executable, "/tmp/test_cli_push_creds.py"],
            capture_output=True,
            text=True,
        )

        # Clean up
        Path("/tmp/test_cli_push_creds.py").unlink(missing_ok=True)

        # Should exit with error code
        assert (
            result.returncode != 0
        ), f"Expected non-zero exit code, got {result.returncode}"

        # Should contain error message in stderr
        assert (
            "SheetsPushError" in result.stderr
        ), f"Expected SheetsPushError in stderr: {result.stderr}"

    def test_cli_push_flag_in_help(self):
        """Test that --push flag appears in help output."""
        result = subprocess.run(
            [sys.executable, "cli.py", "--help"],
            capture_output=True,
            text=True,
        )

        # Should exit successfully
        assert result.returncode == 0, f"CLI help failed: {result.stderr}"

        # Should mention push option in help
        assert "--push" in result.stdout, "Help should mention --push option"
        assert "--no-push" in result.stdout, "Help should mention --no-push option"

    def test_cli_push_with_file_parse_error(self):
        """Test CLI exits with code 1 when file parsing fails with --push flag."""
        import tempfile

        # Create a temporary file with invalid content
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            temp_file.write(b"invalid,csv,content\nwith,malformed\ndata")
            temp_path = temp_file.name

        try:
            result = subprocess.run(
                [sys.executable, "cli.py", "--file", temp_path, "--push"],
                capture_output=True,
                text=True,
            )

            # Should exit with error code
            assert (
                result.returncode == 1
            ), f"Expected exit code 1, got {result.returncode}"

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_cli_watch_mode_with_test_flag(self):
        """Test CLI watch mode with --test-mode flag exits quickly."""
        result = subprocess.run(
            [sys.executable, "cli.py", "--watch", "--test-mode"],
            capture_output=True,
            text=True,
        )

        # Should exit successfully in test mode
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"

        # Should contain expected output
        assert (
            "Watching folder:" in result.stdout
            or "No files found to process" in result.stdout
        ), f"Expected watch mode output in stdout: {result.stdout}"

    def test_cli_handles_unsupported_file_type_error(self):
        """Test CLI exits with code 1 and prints error for unsupported file types."""
        import tempfile

        # Create a temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"some text content")
            temp_path = temp_file.name

        try:
            result = subprocess.run(
                [sys.executable, "cli.py", "--file", temp_path, "--once"],
                capture_output=True,
                text=True,
            )

            # Should exit with error code
            assert (
                result.returncode == 1
            ), f"Expected exit code 1, got {result.returncode}"

            # Should contain error message in stderr
            assert (
                "Error:" in result.stderr
            ), f"Expected error message in stderr: {result.stderr}"

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_cli_handles_value_error_in_non_push_mode(self):
        """Test CLI handles ValueError in non-push mode."""
        # Create test script that raises ValueError during parsing
        test_script = """
import sys
sys.path.insert(0, '.')
from unittest.mock import patch
from app.parser import UnsupportedFileTypeError
import cli

# Mock parse_file to raise ValueError
with patch('cli.parse_file') as mock_parse:
    mock_parse.side_effect = ValueError("Test ValueError")
    
    # Call the CLI function directly with args (no push flag)
    sys.argv = ['cli.py', '--file', 'samples/data.csv', '--once']
    cli.main()
"""

        # Write test script to temporary file
        with open("/tmp/test_cli_value_error.py", "w") as f:
            f.write(test_script)

        # Run the test script
        result = subprocess.run(
            [sys.executable, "/tmp/test_cli_value_error.py"],
            capture_output=True,
            text=True,
        )

        # Clean up
        Path("/tmp/test_cli_value_error.py").unlink(missing_ok=True)

        # Should exit with error code
        assert result.returncode == 1, f"Expected exit code 1, got {result.returncode}"

        # Should contain error message in stderr
        assert (
            "Error: Test ValueError" in result.stderr
        ), f"Expected ValueError in stderr: {result.stderr}"

    def test_cli_handles_unexpected_exception(self):
        """Test CLI handles unexpected exceptions."""
        # Create test script that raises unexpected exception
        test_script = """
import sys
sys.path.insert(0, '.')
from unittest.mock import patch
import cli

# Mock parse_file to raise unexpected exception
with patch('cli.parse_file') as mock_parse:
    mock_parse.side_effect = RuntimeError("Test unexpected error")
    
    # Call the CLI function directly with args
    sys.argv = ['cli.py', '--file', 'samples/data.csv', '--once']
    cli.main()
"""

        # Write test script to temporary file
        with open("/tmp/test_cli_unexpected_error.py", "w") as f:
            f.write(test_script)

        # Run the test script
        result = subprocess.run(
            [sys.executable, "/tmp/test_cli_unexpected_error.py"],
            capture_output=True,
            text=True,
        )

        # Clean up
        Path("/tmp/test_cli_unexpected_error.py").unlink(missing_ok=True)

        # Should exit with error code
        assert result.returncode == 1, f"Expected exit code 1, got {result.returncode}"

        # Should contain error message in stderr
        assert (
            "Unexpected error: Test unexpected error" in result.stderr
        ), f"Expected unexpected error in stderr: {result.stderr}"
