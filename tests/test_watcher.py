"""Test module for file watcher functionality.

This module contains tests for the Watcher class that monitors file changes
using the watchdog library.
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from app.core.watcher import Watcher


class TestWatcher:
    """Test cases for the Watcher class."""

    def test_watcher_initialization(self):
        """Test that Watcher initializes correctly with default parameters."""
        folder = Path("/tmp/test")
        patterns = ["*.csv", "*.xlsx"]

        watcher = Watcher(folder=folder, patterns=patterns)

        assert watcher.folder == folder
        assert watcher.patterns == patterns
        assert watcher.poll_interval == 5  # default value
        assert watcher._observer is None
        assert watcher._event_handler is None
        assert not watcher._is_running

    def test_watcher_initialization_with_custom_poll_interval(self):
        """Test that Watcher initializes with custom poll interval."""
        folder = Path("/tmp/test")
        patterns = ["*.csv"]
        poll_interval = 10

        watcher = Watcher(folder=folder, patterns=patterns, poll_interval=poll_interval)

        assert watcher.poll_interval == poll_interval

    @patch("app.core.watcher.tomli.load")
    def test_watcher_reads_config_defaults(self, mock_tomli_load):
        """Test that Watcher reads default values from settings.toml."""
        # Mock the tomli.load to return expected config
        mock_config = {
            "watcher": {
                "folder": "./watch",
                "patterns": ["*.csv", "*.xlsx"],
                "poll_interval": 3,
            }
        }
        mock_tomli_load.return_value = mock_config

        watcher = Watcher()

        assert watcher.folder == Path("./watch")
        assert watcher.patterns == ["*.csv", "*.xlsx"]
        assert watcher.poll_interval == 3

    @pytest.mark.slow
    def test_watcher_detects_new_csv_file(self):
        """Test that watcher detects new CSV files and calls callback."""
        with tempfile.TemporaryDirectory() as tmpdir:
            folder = Path(tmpdir)
            patterns = ["*.csv"]
            callback = Mock()

            watcher = Watcher(folder=folder, patterns=patterns, poll_interval=1)
            watcher.start(callback)

            try:
                # Give the watcher a moment to start
                time.sleep(0.1)

                # Create a new CSV file
                test_file = folder / "test.csv"
                test_file.write_text("col1,col2\n1,2\n")

                # Wait for the callback to be triggered (reduced timeout)
                start_time = time.time()
                while time.time() - start_time < 1:  # Reduced from 2 to 1 second
                    if callback.called:
                        break
                    time.sleep(0.05)  # Reduced sleep time

                # Assert callback was called with the file path
                assert callback.called
                callback.assert_called_with(test_file.resolve())

            finally:
                watcher.stop()

    @pytest.mark.slow
    def test_watcher_detects_new_xlsx_file(self):
        """Test that watcher detects new XLSX files and calls callback."""
        with tempfile.TemporaryDirectory() as tmpdir:
            folder = Path(tmpdir)
            patterns = ["*.xlsx"]
            callback = Mock()

            watcher = Watcher(folder=folder, patterns=patterns, poll_interval=1)
            watcher.start(callback)

            try:
                # Give the watcher a moment to start
                time.sleep(0.1)

                # Create a new XLSX file (just a dummy file with xlsx extension)
                test_file = folder / "test.xlsx"
                test_file.write_bytes(b"dummy xlsx content")

                # Wait for the callback to be triggered (reduced timeout)
                start_time = time.time()
                while time.time() - start_time < 1:  # Reduced from 2 to 1 second
                    if callback.called:
                        break
                    time.sleep(0.05)  # Reduced sleep time

                # Assert callback was called with the file path
                assert callback.called
                callback.assert_called_with(test_file.resolve())

            finally:
                watcher.stop()

    @pytest.mark.slow
    def test_watcher_detects_modified_file(self):
        """Test that watcher detects modified files and calls callback."""
        with tempfile.TemporaryDirectory() as tmpdir:
            folder = Path(tmpdir)
            patterns = ["*.csv"]
            callback = Mock()

            # Create a file before starting the watcher
            test_file = folder / "existing.csv"
            test_file.write_text("col1,col2\n1,2\n")

            watcher = Watcher(folder=folder, patterns=patterns, poll_interval=1)
            watcher.start(callback)

            try:
                # Give the watcher a moment to start
                time.sleep(0.1)

                # Modify the existing file
                test_file.write_text("col1,col2\n1,2\n3,4\n")

                # Wait for the callback to be triggered (reduced timeout)
                start_time = time.time()
                while time.time() - start_time < 1:  # Reduced from 2 to 1 second
                    if callback.called:
                        break
                    time.sleep(0.05)  # Reduced sleep time

                # Assert callback was called with the file path
                assert callback.called
                callback.assert_called_with(test_file.resolve())

            finally:
                watcher.stop()

    @pytest.mark.slow
    def test_watcher_respects_patterns(self):
        """Test that watcher only responds to files matching specified patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            folder = Path(tmpdir)
            patterns = ["*.csv"]  # Only CSV files
            callback = Mock()

            watcher = Watcher(folder=folder, patterns=patterns, poll_interval=1)
            watcher.start(callback)

            try:
                # Give the watcher a moment to start
                time.sleep(0.1)

                # Create a non-matching file
                txt_file = folder / "test.txt"
                txt_file.write_text("This is not a CSV file")

                # Wait a bit to see if callback is called (it shouldn't be)
                time.sleep(0.3)  # Reduced wait time

                # Assert callback was NOT called
                assert not callback.called

                # Now create a matching file
                csv_file = folder / "test.csv"
                csv_file.write_text("col1,col2\n1,2\n")

                # Wait for the callback to be triggered (reduced timeout)
                start_time = time.time()
                while time.time() - start_time < 1:  # Reduced from 2 to 1 second
                    if callback.called:
                        break
                    time.sleep(0.05)  # Reduced sleep time

                # Assert callback was called with the CSV file path
                assert callback.called
                callback.assert_called_with(csv_file.resolve())

            finally:
                watcher.stop()

    @pytest.mark.slow
    def test_watcher_debounces_duplicate_events(self):
        """Test that watcher debounces duplicate events within 1 second."""
        with tempfile.TemporaryDirectory() as tmpdir:
            folder = Path(tmpdir)
            patterns = ["*.csv"]
            callback = Mock()

            watcher = Watcher(folder=folder, patterns=patterns, poll_interval=1)
            watcher.start(callback)

            try:
                # Give the watcher a moment to start
                time.sleep(0.1)

                # Create a file
                test_file = folder / "test.csv"
                test_file.write_text("col1,col2\n1,2\n")

                # Modify the file multiple times quickly
                for i in range(3):
                    test_file.write_text(f"col1,col2\n1,2\n{i},{i+1}\n")
                    time.sleep(0.05)  # Reduced sleep time

                # Wait a bit longer to ensure all events are processed
                time.sleep(1.0)  # Reduced from 1.5 to 1.0 second

                # Should only be called once due to debouncing
                assert callback.call_count == 1

            finally:
                watcher.stop()

    def test_watcher_stop_cleanly_ends_observer(self):
        """Test that stopping the watcher cleanly ends the observer thread."""
        with tempfile.TemporaryDirectory() as tmpdir:
            folder = Path(tmpdir)
            patterns = ["*.csv"]
            callback = Mock()

            watcher = Watcher(folder=folder, patterns=patterns, poll_interval=1)
            watcher.start(callback)

            # Check that watcher is running
            assert watcher._is_running
            assert watcher._observer is not None
            assert watcher._observer.is_alive()

            # Stop the watcher
            watcher.stop()

            # Check that watcher is stopped
            assert not watcher._is_running
            assert watcher._observer is not None
            assert not watcher._observer.is_alive()

    def test_watcher_start_non_blocking(self):
        """Test that watcher.start() is non-blocking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            folder = Path(tmpdir)
            patterns = ["*.csv"]
            callback = Mock()

            watcher = Watcher(folder=folder, patterns=patterns, poll_interval=1)

            # start() should return immediately (non-blocking)
            start_time = time.time()
            watcher.start(callback)
            end_time = time.time()

            try:
                # Should complete very quickly (< 0.1 seconds)
                assert end_time - start_time < 0.1
                assert watcher._is_running

            finally:
                watcher.stop()

    def test_watcher_cannot_start_twice(self):
        """Test that watcher cannot be started twice."""
        with tempfile.TemporaryDirectory() as tmpdir:
            folder = Path(tmpdir)
            patterns = ["*.csv"]
            callback = Mock()

            watcher = Watcher(folder=folder, patterns=patterns, poll_interval=1)
            watcher.start(callback)

            try:
                # Starting again should raise an exception
                with pytest.raises(RuntimeError, match="Watcher is already running"):
                    watcher.start(callback)

            finally:
                watcher.stop()

    def test_watcher_stop_when_not_running(self):
        """Test that stopping a non-running watcher doesn't raise an error."""
        folder = Path("/tmp/test")
        patterns = ["*.csv"]

        watcher = Watcher(folder=folder, patterns=patterns)

        # This shouldn't raise an error
        watcher.stop()
        assert not watcher._is_running
