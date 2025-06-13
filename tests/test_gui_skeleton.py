"""Test suite for GUI skeleton implementation.

This module contains comprehensive tests for the PySide6 desktop application
skeleton following TDD principles. Tests verify MainWindow functionality,
tab layout, menu actions, and log panel integration.
"""

from unittest.mock import patch, MagicMock
import pytest
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QTextEdit
from PySide6.QtGui import QAction
import logging


# Test fixtures for pytest-qt
@pytest.fixture(scope="function")
def app(qtbot):
    """Create QApplication instance for testing."""
    # qtbot fixture provides proper Qt application management
    return QApplication.instance()


@pytest.fixture(scope="function")
def main_window(app, qtbot):
    """Create MainWindow instance for testing."""
    from app.gui.main_window import MainWindow

    window = MainWindow()
    qtbot.addWidget(window)  # Ensure proper cleanup
    return window


class TestMainWindow:
    """Test suite for MainWindow functionality."""

    def test_window_title(self, main_window):
        """Test that window title is set to 'Sheets Bot'."""
        assert main_window.windowTitle() == "Sheets Bot"

    def test_window_is_main_window(self, main_window):
        """Test that MainWindow inherits from QMainWindow."""
        assert isinstance(main_window, QMainWindow)

    def test_menu_bar_exists(self, main_window):
        """Test that menu bar is present."""
        menu_bar = main_window.menuBar()
        assert menu_bar is not None

    def test_file_menu_exists(self, main_window):
        """Test that File menu exists in menu bar."""
        menu_bar = main_window.menuBar()
        file_menu = None

        for action in menu_bar.actions():
            if action.text() == "File":
                file_menu = action.menu()
                break

        assert file_menu is not None

    def test_exit_action_exists(self, main_window):
        """Test that Exit action exists in File menu."""
        menu_bar = main_window.menuBar()
        file_menu = None

        for action in menu_bar.actions():
            if action.text() == "File":
                file_menu = action.menu()
                break

        assert file_menu is not None

        exit_action = None
        for action in file_menu.actions():
            if action.text() == "Exit":
                exit_action = action
                break

        assert exit_action is not None
        assert isinstance(exit_action, QAction)

    def test_tab_widget_exists(self, main_window):
        """Test that main window contains a QTabWidget."""
        # Find QTabWidget in the main window
        tab_widget = None
        for child in main_window.findChildren(QTabWidget):
            tab_widget = child
            break

        assert tab_widget is not None
        assert isinstance(tab_widget, QTabWidget)

    def test_manual_sync_tab_exists(self, main_window):
        """Test that 'Manual Sync' tab exists."""
        tab_widget = None
        for child in main_window.findChildren(QTabWidget):
            tab_widget = child
            break

        assert tab_widget is not None

        # Check for Manual Sync tab
        manual_sync_found = False
        for i in range(tab_widget.count()):
            if tab_widget.tabText(i) == "Manual Sync":
                manual_sync_found = True
                break

        assert manual_sync_found, "Manual Sync tab not found"

    def test_watcher_tab_exists(self, main_window):
        """Test that 'Watcher' tab exists."""
        tab_widget = None
        for child in main_window.findChildren(QTabWidget):
            tab_widget = child
            break

        assert tab_widget is not None

        # Check for Watcher tab
        watcher_found = False
        for i in range(tab_widget.count()):
            if tab_widget.tabText(i) == "Watcher":
                watcher_found = True
                break

        assert watcher_found, "Watcher tab not found"

    def test_log_panel_exists(self, main_window):
        """Test that log panel (QTextEdit) exists and is read-only."""
        # Find QTextEdit in the main window
        log_panel = None
        for child in main_window.findChildren(QTextEdit):
            log_panel = child
            break

        assert log_panel is not None
        assert isinstance(log_panel, QTextEdit)
        assert log_panel.isReadOnly() is True

    def test_log_panel_connected_to_logging(self, main_window):
        """Test that log panel is connected to Python logging system."""
        # Find the log panel
        log_panel = None
        for child in main_window.findChildren(QTextEdit):
            log_panel = child
            break

        assert log_panel is not None

        # Test that logging handler is properly configured
        # This will be implemented with a custom logging handler
        logger = logging.getLogger("sheets-bot")

        # Check if our custom handler is attached
        gui_handler_found = False
        for handler in logger.handlers:
            if hasattr(handler, "log_panel"):
                gui_handler_found = True
                break

        assert gui_handler_found, "GUI logging handler not found"


class TestRunGuiFunction:
    """Test suite for run_gui() function."""

    @patch("app.gui.main_window.sys.exit")
    @patch("app.gui.main_window.QApplication")
    @patch("app.gui.main_window.MainWindow")
    def test_run_gui_function_exists(self, mock_main_window, mock_qapp, mock_exit):
        """Test that run_gui function exists and can be imported."""
        from app.gui.main_window import run_gui

        # Mock the QApplication and MainWindow
        mock_app_instance = MagicMock()
        mock_qapp.return_value = mock_app_instance
        mock_window_instance = MagicMock()
        mock_main_window.return_value = mock_window_instance

        # Call run_gui - it should not raise any exceptions
        run_gui()

        # Verify QApplication was created and exec was called
        mock_qapp.assert_called_once()
        mock_app_instance.exec.assert_called_once()
        mock_window_instance.show.assert_called_once()
        mock_exit.assert_called_once()


class TestTabStubs:
    """Test suite for tab stub classes."""

    def test_manual_sync_tab_class_exists(self):
        """Test that ManualSyncTab class exists."""
        from app.gui.manual_tab import ManualSyncTab
        from PySide6.QtWidgets import QWidget

        tab = ManualSyncTab()
        assert isinstance(tab, QWidget)

    def test_watcher_tab_class_exists(self):
        """Test that WatcherTab class exists."""
        from app.gui.watcher_tab import WatcherTab
        from PySide6.QtWidgets import QWidget

        tab = WatcherTab()
        assert isinstance(tab, QWidget)
