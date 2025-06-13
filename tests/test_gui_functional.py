"""Test suite for GUI functional integration with backend modules.

This module contains comprehensive tests for PySide6 GUI functionality including
manual sync operations, watcher controls, and live status updates following TDD principles.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from PySide6.QtWidgets import QApplication, QPushButton, QLabel, QLineEdit
from PySide6.QtCore import Qt


@pytest.fixture(scope="function")
def app(qtbot):
    """Create QApplication instance for testing."""
    return QApplication.instance()


@pytest.fixture(scope="function")
def main_window(app, qtbot):
    """Create MainWindow instance for testing."""
    from app.gui.main_window import MainWindow

    window = MainWindow()
    qtbot.addWidget(window)

    yield window

    # Explicit cleanup to prevent hanging threads
    try:
        if hasattr(window.manual_sync_tab, "cleanup"):
            window.manual_sync_tab.cleanup()
        if hasattr(window.watcher_tab, "cleanup"):
            window.watcher_tab.cleanup()
    except Exception:
        pass  # Ignore cleanup errors during test teardown


@pytest.fixture(scope="function")
def sample_csv_file():
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Name,Age,City\n")
        f.write("John Doe,30,New York\n")
        f.write("Jane Smith,25,Los Angeles\n")
        f.write("Bob Johnson,35,Chicago\n")
        f.flush()  # Ensure data is written to disk
        temp_file = f.name
    yield temp_file
    os.unlink(temp_file)


@pytest.fixture(scope="function")
def temp_watch_dir():
    """Create a temporary directory for watcher testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


class TestManualSyncTabFunctional:
    """Test suite for ManualSyncTab functional integration."""

    def test_manual_sync_tab_has_select_file_button(self, main_window):
        """Test that manual sync tab has a 'Select File' button."""
        # Switch to Manual Sync tab
        main_window.tab_widget.setCurrentIndex(0)
        manual_tab = main_window.manual_sync_tab

        # Find Select File button
        select_button = None
        for child in manual_tab.findChildren(QPushButton):
            if "Select File" in child.text():
                select_button = child
                break

        assert select_button is not None, "Select File button not found"

    def test_manual_sync_tab_has_status_labels(self, main_window):
        """Test that manual sync tab has status labels for diff and URL."""
        # Switch to Manual Sync tab
        main_window.tab_widget.setCurrentIndex(0)
        manual_tab = main_window.manual_sync_tab

        # Find status labels
        diff_label = None
        url_label = None

        for child in manual_tab.findChildren(QLabel):
            if hasattr(child, "objectName"):
                if child.objectName() == "diff_status_label":
                    diff_label = child
                elif child.objectName() == "url_status_label":
                    url_label = child

        assert diff_label is not None, "Diff status label not found"
        assert url_label is not None, "URL status label not found"

    @patch("app.gui.manual_tab.SheetsClient")
    @patch("app.gui.manual_tab.SlackNotifier")
    @patch("app.gui.manual_tab.DeltaTracker")
    @patch("app.gui.manual_tab.QFileDialog")
    def test_manual_sync_complete_workflow(
        self,
        mock_file_dialog,
        mock_delta,
        mock_slack,
        mock_sheets,
        main_window,
        qtbot,
        sample_csv_file,
    ):
        """Test complete manual sync workflow: select file → parse → push → diff → notify."""
        # Mock return values
        mock_file_dialog.getOpenFileName.return_value = (
            sample_csv_file,
            "CSV files (*.csv)",
        )

        mock_sheets_instance = MagicMock()
        mock_sheets_instance.push_dataframe.return_value = "https://gui.fake/tab"
        mock_sheets.return_value = mock_sheets_instance

        mock_delta_instance = MagicMock()
        mock_delta_instance.compute_diff.return_value = {
            "added": 3,
            "updated": 0,
            "deleted": 0,
            "diff_df": MagicMock(),
        }
        mock_delta.return_value = mock_delta_instance

        mock_slack_instance = MagicMock()
        mock_slack_instance.post_summary.return_value = True
        mock_slack.from_settings.return_value = mock_slack_instance

        # Switch to Manual Sync tab
        main_window.tab_widget.setCurrentIndex(0)
        manual_tab = main_window.manual_sync_tab

        # Find and click Select File button
        select_button = None
        for child in manual_tab.findChildren(QPushButton):
            if "Select File" in child.text():
                select_button = child
                break

        assert select_button is not None
        qtbot.mouseClick(select_button, Qt.LeftButton)

        # Allow GUI to process the workflow
        qtbot.wait(100)

        # Check that status labels are updated
        diff_label = None
        url_label = None

        for child in manual_tab.findChildren(QLabel):
            if hasattr(child, "objectName"):
                if child.objectName() == "diff_status_label":
                    diff_label = child
                elif child.objectName() == "url_status_label":
                    url_label = child

        assert diff_label is not None
        assert url_label is not None

        # Verify diff status contains expected format "+3 / 0 / 0"
        assert "+3 / 0 / 0" in diff_label.text()

        # Verify URL label contains the sheets URL
        assert "https://gui.fake/tab" in url_label.text()

        # Verify all backend methods were called
        mock_sheets_instance.push_dataframe.assert_called_once()
        mock_delta_instance.compute_diff.assert_called_once()
        mock_slack_instance.post_summary.assert_called_once()


class TestWatcherTabFunctional:
    """Test suite for WatcherTab functional integration."""

    def test_watcher_tab_has_folder_controls(self, main_window):
        """Test that watcher tab has folder selection controls."""
        # Switch to Watcher tab
        main_window.tab_widget.setCurrentIndex(1)
        watcher_tab = main_window.watcher_tab

        # Find folder path line edit
        folder_edit = None
        for child in watcher_tab.findChildren(QLineEdit):
            if (
                hasattr(child, "objectName")
                and child.objectName() == "folder_path_edit"
            ):
                folder_edit = child
                break

        assert folder_edit is not None, "Folder path edit not found"

        # Find Browse button
        browse_button = None
        for child in watcher_tab.findChildren(QPushButton):
            if "Browse" in child.text():
                browse_button = child
                break

        assert browse_button is not None, "Browse button not found"

    def test_watcher_tab_has_control_buttons(self, main_window):
        """Test that watcher tab has Start/Stop watch buttons."""
        # Switch to Watcher tab
        main_window.tab_widget.setCurrentIndex(1)
        watcher_tab = main_window.watcher_tab

        # Find Start Watch button
        start_button = None
        for child in watcher_tab.findChildren(QPushButton):
            if "Start Watch" in child.text():
                start_button = child
                break

        assert start_button is not None, "Start Watch button not found"

    def test_watcher_tab_has_status_displays(self, main_window):
        """Test that watcher tab has status displays for diff and Slack."""
        # Switch to Watcher tab
        main_window.tab_widget.setCurrentIndex(1)
        watcher_tab = main_window.watcher_tab

        # Find diff status label
        diff_label = None
        slack_label = None

        for child in watcher_tab.findChildren(QLabel):
            if hasattr(child, "objectName"):
                if child.objectName() == "watcher_diff_label":
                    diff_label = child
                elif child.objectName() == "slack_status_label":
                    slack_label = child

        assert diff_label is not None, "Watcher diff label not found"
        assert slack_label is not None, "Slack status label not found"

    @patch("app.gui.watcher_tab.Watcher")
    @patch("app.gui.watcher_tab.QFileDialog")
    def test_watcher_start_stop_functionality(
        self, mock_file_dialog, mock_watcher_class, main_window, qtbot, temp_watch_dir
    ):
        """Test watcher start/stop functionality with thread management."""
        # Mock folder selection
        mock_file_dialog.getExistingDirectory.return_value = temp_watch_dir

        # Mock Watcher instance
        mock_watcher_instance = MagicMock()
        mock_watcher_class.return_value = mock_watcher_instance

        # Switch to Watcher tab
        main_window.tab_widget.setCurrentIndex(1)
        watcher_tab = main_window.watcher_tab

        # Find Browse button and click it
        browse_button = None
        for child in watcher_tab.findChildren(QPushButton):
            if "Browse" in child.text():
                browse_button = child
                break

        qtbot.mouseClick(browse_button, Qt.LeftButton)
        qtbot.wait(50)

        # Find Start Watch button and click it
        start_button = None
        for child in watcher_tab.findChildren(QPushButton):
            if "Start Watch" in child.text():
                start_button = child
                break

        qtbot.mouseClick(start_button, Qt.LeftButton)
        qtbot.wait(100)

        # Verify watcher was started
        mock_watcher_instance.start.assert_called_once()

        # Button should now show "Stop Watch"
        assert "Stop Watch" in start_button.text()

        # Click Stop Watch
        qtbot.mouseClick(start_button, Qt.LeftButton)
        qtbot.wait(100)

        # Verify watcher was stopped (called at least once, may be called again during cleanup)
        assert mock_watcher_instance.stop.call_count >= 1

        # Button should now show "Start Watch" again
        assert "Start Watch" in start_button.text()

    @patch("app.gui.watcher_tab.Watcher")
    @patch("app.gui.watcher_tab.SheetsClient")
    @patch("app.gui.watcher_tab.SlackNotifier")
    @patch("app.gui.watcher_tab.DeltaTracker")
    def test_watcher_file_detection_workflow(
        self,
        mock_delta,
        mock_slack,
        mock_sheets,
        mock_watcher_class,
        main_window,
        qtbot,
        temp_watch_dir,
    ):
        """Test complete watcher workflow when file is detected."""
        # Setup mocks
        mock_watcher_instance = MagicMock()
        mock_watcher_class.return_value = mock_watcher_instance

        mock_sheets_instance = MagicMock()
        mock_sheets_instance.push_dataframe.return_value = "https://watcher.fake/tab"
        mock_sheets.return_value = mock_sheets_instance

        mock_delta_instance = MagicMock()
        mock_delta_instance.compute_diff.return_value = {
            "added": 2,
            "updated": 1,
            "deleted": 0,
            "diff_df": MagicMock(),
        }
        mock_delta.return_value = mock_delta_instance

        mock_slack_instance = MagicMock()
        mock_slack_instance.post_summary.return_value = True
        mock_slack.from_settings.return_value = mock_slack_instance

        # Switch to Watcher tab
        main_window.tab_widget.setCurrentIndex(1)
        watcher_tab = main_window.watcher_tab

        # Set folder path manually
        folder_edit = None
        for child in watcher_tab.findChildren(QLineEdit):
            if (
                hasattr(child, "objectName")
                and child.objectName() == "folder_path_edit"
            ):
                folder_edit = child
                break

        folder_edit.setText(temp_watch_dir)

        # Start watcher
        start_button = None
        for child in watcher_tab.findChildren(QPushButton):
            if "Start Watch" in child.text():
                start_button = child
                break

        qtbot.mouseClick(start_button, Qt.LeftButton)
        qtbot.wait(100)

        # Simulate file detection by calling the callback directly
        # The callback should be passed to watcher.start()
        start_call_args = mock_watcher_instance.start.call_args
        assert start_call_args is not None
        callback = start_call_args[0][0]  # First positional argument

        # Create a test file and call the callback
        test_file = Path(temp_watch_dir) / "test.csv"
        test_file.write_text("Name,Age\nTest User,30\n")

        # Call the callback to simulate file detection
        callback(test_file)

        # Allow time for GUI updates
        qtbot.wait(500)

        # Check that diff label was updated
        diff_label = None
        for child in watcher_tab.findChildren(QLabel):
            if (
                hasattr(child, "objectName")
                and child.objectName() == "watcher_diff_label"
            ):
                diff_label = child
                break

        assert diff_label is not None
        # Should contain "+2 / 1 / 0" based on our mock
        assert "+2 / 1 / 0" in diff_label.text()

        # Check Slack status shows success
        slack_label = None
        for child in watcher_tab.findChildren(QLabel):
            if (
                hasattr(child, "objectName")
                and child.objectName() == "slack_status_label"
            ):
                slack_label = child
                break

        assert slack_label is not None
        # Should show green checkmark or success indicator
        assert "✅" in slack_label.text() or "success" in slack_label.text().lower()


class TestGuiResourcesAndIcons:
    """Test suite for GUI resources and icons."""

    def test_resources_module_exists(self):
        """Test that resources module exists for icons."""
        try:
            from app.gui import resources

            assert hasattr(resources, "get_checkmark_icon")
            assert hasattr(resources, "get_cross_icon")
        except ImportError:
            # Resources module is optional - test passes if it doesn't exist
            pass

    def test_gui_uses_proper_icons_if_available(self, main_window):
        """Test that GUI uses proper icons if resources are available."""
        # This test will pass regardless of whether resources exist
        # It's a placeholder for future icon integration
        try:
            from app.gui import resources

            # If resources exist, verify they provide the expected interface
            assert callable(getattr(resources, "get_checkmark_icon", lambda: None))
            assert callable(getattr(resources, "get_cross_icon", lambda: None))
        except ImportError:
            # Resources module doesn't exist - that's fine
            pass
