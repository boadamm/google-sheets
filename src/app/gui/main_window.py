"""Main window module for sheets-bot GUI application.

This module contains the MainWindow class that serves as the primary interface
for the sheets-bot desktop application, including menu bar, tab layout,
and integrated logging panel.
"""

import sys
import logging
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QTextEdit,
    QDockWidget,
)
from PySide6.QtGui import QAction

from .manual_tab import ManualSyncTab
from .watcher_tab import WatcherTab


class GuiLogHandler(logging.Handler):
    """Custom logging handler that redirects log messages to GUI text widget.

    This handler captures log messages and displays them in the QTextEdit
    log panel, enabling real-time log viewing within the GUI.
    """

    def __init__(self, log_panel: QTextEdit):
        """Initialize the GUI log handler.

        Args:
            log_panel: QTextEdit widget to display log messages
        """
        super().__init__()
        self.log_panel = log_panel

        # Set a formatter for consistent log message format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.setFormatter(formatter)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to the GUI log panel.

        Args:
            record: The log record to emit
        """
        try:
            msg = self.format(record)
            # Append to the text edit (thread-safe via Qt's signal system)
            self.log_panel.append(msg)
        except Exception:
            # Avoid recursive logging issues
            pass


class MainWindow(QMainWindow):
    """Main window for the sheets-bot desktop application.

    This window provides the primary interface with menu bar, tabbed content,
    and a dockable log panel for real-time logging display.
    """

    # Signals for inter-component communication
    file_selected = Signal(str)  # Emitted when a file is selected
    sync_requested = Signal()  # Emitted when sync is requested
    watch_started = Signal()  # Emitted when file watching starts
    watch_stopped = Signal()  # Emitted when file watching stops

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the main window.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self._setup_window()
        self._setup_menu_bar()
        self._setup_central_widget()
        self._setup_log_panel()
        self._setup_logging()
        self._connect_signals()

    def _setup_window(self) -> None:
        """Set up basic window properties."""
        self.setWindowTitle("Sheets Bot")
        self.setMinimumSize(800, 600)

        # Center the window on screen
        self.resize(1024, 768)

    def _setup_menu_bar(self) -> None:
        """Set up the menu bar with File menu and Exit action."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)

        file_menu.addAction(exit_action)

    def _setup_central_widget(self) -> None:
        """Set up the central widget with tab layout."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Create and add tabs
        self.manual_sync_tab = ManualSyncTab()
        self.watcher_tab = WatcherTab()

        self.tab_widget.addTab(self.manual_sync_tab, "Manual Sync")
        self.tab_widget.addTab(self.watcher_tab, "Watcher")

        # Add tab widget to layout
        layout.addWidget(self.tab_widget)

    def _setup_log_panel(self) -> None:
        """Set up the dockable log panel."""
        # Create dock widget for log panel
        log_dock = QDockWidget("Log Panel", self)
        log_dock.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        # Create log text edit
        self.log_panel = QTextEdit()
        self.log_panel.setReadOnly(True)
        # Note: QTextEdit doesn't have setMaximumBlockCount, we'll manage log size in the handler

        # Style the log panel
        self.log_panel.setStyleSheet(
            """
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                border: 1px solid #555;
            }
        """
        )

        # Set dock widget content
        log_dock.setWidget(self.log_panel)

        # Add dock to main window
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, log_dock)

    def _setup_logging(self) -> None:
        """Set up logging integration with the GUI log panel."""
        # Create and configure the GUI log handler
        self.gui_log_handler = GuiLogHandler(self.log_panel)
        self.gui_log_handler.setLevel(logging.INFO)

        # Get the sheets-bot logger and add our handler
        logger = logging.getLogger("sheets-bot")
        logger.setLevel(logging.INFO)
        logger.addHandler(self.gui_log_handler)

        # Also set up root logger to catch other messages
        root_logger = logging.getLogger()
        if not any(isinstance(h, GuiLogHandler) for h in root_logger.handlers):
            root_logger.addHandler(self.gui_log_handler)

        # Log startup message
        logger.info("Sheets Bot GUI initialized successfully")

    def _connect_signals(self) -> None:
        """Connect internal signals and slots for inter-component communication."""
        # Tab change signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # Connect custom signals (placeholder for future functionality)
        self.file_selected.connect(self._on_file_selected)
        self.sync_requested.connect(self._on_sync_requested)
        self.watch_started.connect(self._on_watch_started)
        self.watch_stopped.connect(self._on_watch_stopped)

    def _on_tab_changed(self, index: int) -> None:
        """Handle tab change events.

        Args:
            index: Index of the newly selected tab
        """
        tab_names = ["Manual Sync", "Watcher"]
        if 0 <= index < len(tab_names):
            logger = logging.getLogger("sheets-bot")
            logger.info(f"Switched to {tab_names[index]} tab")

    def _on_file_selected(self, file_path: str) -> None:
        """Handle file selection signal.

        Args:
            file_path: Path to the selected file
        """
        logger = logging.getLogger("sheets-bot")
        logger.info(f"File selected: {file_path}")

    def _on_sync_requested(self) -> None:
        """Handle sync request signal."""
        logger = logging.getLogger("sheets-bot")
        logger.info("Sync operation requested")

    def _on_watch_started(self) -> None:
        """Handle watch started signal."""
        logger = logging.getLogger("sheets-bot")
        logger.info("File watching started")

    def _on_watch_stopped(self) -> None:
        """Handle watch stopped signal."""
        logger = logging.getLogger("sheets-bot")
        logger.info("File watching stopped")

    def closeEvent(self, event) -> None:
        """Handle window close event with cleanup.

        Args:
            event: The close event
        """
        logger = logging.getLogger("sheets-bot")
        logger.info("Shutting down Sheets Bot GUI")

        # Clean up tab resources (stop any running threads)
        try:
            if hasattr(self.manual_sync_tab, "cleanup"):
                self.manual_sync_tab.cleanup()
            if hasattr(self.watcher_tab, "cleanup"):
                self.watcher_tab.cleanup()
        except Exception as e:
            logger.warning(f"Error during tab cleanup: {e}")

        # Clean up logging handler
        if hasattr(self, "gui_log_handler"):
            logger.removeHandler(self.gui_log_handler)
            root_logger = logging.getLogger()
            if self.gui_log_handler in root_logger.handlers:
                root_logger.removeHandler(self.gui_log_handler)

        # Accept the close event
        event.accept()


def run_gui() -> None:
    """Run the sheets-bot GUI application.

    This function creates the QApplication instance, shows the main window,
    and starts the event loop.
    """
    # Create QApplication instance
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Sheets Bot")
    app.setApplicationVersion("1.1.0")
    app.setOrganizationName("Sheets Bot Team")

    # Create and show main window
    main_window = MainWindow()
    main_window.show()

    # Start event loop
    sys.exit(app.exec())
