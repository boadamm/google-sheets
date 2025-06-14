"""Watcher tab module for sheets-bot GUI.

This module contains the WatcherTab widget that provides UI for file
watching operations, status monitoring, and live diff updates.
"""

import logging
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QFrame,
    QLineEdit,
    QMessageBox,
)
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QFont

# Robust import with fallback for distributed environments
try:
    from ..core.parser import parse_file, UnsupportedFileTypeError
    from ..integrations.sheets_client import SheetsClient, SheetsPushError
    from ..core.delta import DeltaTracker
    from ..integrations.notifier import SlackNotifier
    from ..core.watcher import Watcher
except ImportError:
    # Fallback for distributed environments
    from app.core.parser import parse_file, UnsupportedFileTypeError
    from app.integrations.sheets_client import SheetsClient, SheetsPushError
    from app.core.delta import DeltaTracker
    from app.integrations.notifier import SlackNotifier
    from app.core.watcher import Watcher


class WatcherWorker(QThread):
    """Background worker thread for file watching operations.

    This worker manages the Watcher instance and processes detected files
    through the complete sheets-bot workflow.
    """

    # Signals for communicating with main thread
    file_processed = Signal(dict, str, bool)  # diff_result, sheet_url, slack_success
    processing_error = Signal(str)  # error_message
    watcher_started = Signal()
    watcher_stopped = Signal()

    def __init__(self, watch_folder: str):
        """Initialize the worker thread.

        Args:
            watch_folder: Folder path to watch for file changes
        """
        super().__init__()
        self.watch_folder = Path(watch_folder)
        self.logger = logging.getLogger("sheets-bot")
        self.watcher: Optional[Watcher] = None
        self._should_stop = False

    def run(self) -> None:
        """Run the watcher in background thread."""
        try:
            self.logger.info(f"Starting watcher for folder: {self.watch_folder}")

            # Initialize watcher
            self.watcher = Watcher(folder=self.watch_folder)

            # Start watching with our callback
            self.watcher.start(self._on_file_detected)
            self.watcher_started.emit()

            # Keep thread alive while watcher is running
            # Check every 100ms for stop signal to be more responsive
            while not self._should_stop:
                if not (
                    self.watcher
                    and hasattr(self.watcher, "_is_running")
                    and self.watcher._is_running
                ):
                    break
                self.msleep(100)  # Check every 100ms

        except Exception as e:
            error_msg = f"Watcher error: {str(e)}"
            self.logger.error(error_msg)
            self.processing_error.emit(error_msg)
        finally:
            # Ensure watcher is stopped
            if self.watcher:
                try:
                    self.watcher.stop()
                except Exception:
                    pass  # Ignore errors during cleanup

    def stop_watcher(self) -> None:
        """Stop the watcher and exit thread."""
        self._should_stop = True
        if self.watcher:
            try:
                self.watcher.stop()
                self.watcher_stopped.emit()
                self.logger.info("Watcher stopped successfully")
            except Exception as e:
                self.logger.error(f"Error stopping watcher: {e}")

    def _on_file_detected(self, file_path: Path) -> None:
        """Handle detected file through complete workflow.

        Args:
            file_path: Path to the detected file
        """
        try:
            self.logger.info(f"Processing detected file: {file_path}")

            # Step 1: Parse the file
            df = parse_file(file_path)
            self.logger.info(f"Parsed file with {len(df)} rows")

            # Step 2: Push to Google Sheets
            sheets_client = SheetsClient()
            sheet_url = sheets_client.push_dataframe(df)
            self.logger.info(f"Pushed to Google Sheets: {sheet_url}")

            # Step 3: Compute diff
            delta_tracker = DeltaTracker()
            diff_result = delta_tracker.compute_diff(df)
            self.logger.info(
                f"Diff computed: +{diff_result['added']} / {diff_result['updated']} / {diff_result['deleted']}"
            )

            # Step 4: Send Slack notification
            slack_success = False
            try:
                notifier = SlackNotifier.from_settings()
                slack_success = notifier.post_summary(diff_result, sheet_url)
                if slack_success:
                    self.logger.info("Slack notification sent successfully")
                else:
                    self.logger.warning("Slack notification failed")
            except Exception as e:
                self.logger.warning(f"Slack notification error: {e}")

            # Emit success signal
            self.file_processed.emit(diff_result, sheet_url, slack_success)

        except (UnsupportedFileTypeError, FileNotFoundError) as e:
            error_msg = f"File processing error: {str(e)}"
            self.logger.error(error_msg)
            self.processing_error.emit(error_msg)

        except SheetsPushError as e:
            error_msg = f"Sheets push error: {str(e)}"
            self.logger.error(error_msg)
            self.processing_error.emit(error_msg)

        except Exception as e:
            error_msg = f"Unexpected processing error: {str(e)}"
            self.logger.error(error_msg)
            self.processing_error.emit(error_msg)


class WatcherTab(QWidget):
    """Watcher tab widget for file monitoring operations.

    This widget provides controls for starting/stopping file watching,
    selecting watch folders, and displaying live status updates.
    """

    def __init__(self, parent=None):
        """Initialize the watcher tab.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.logger = logging.getLogger("sheets-bot")
        self.worker_thread: Optional[WatcherWorker] = None
        self.is_watching = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface for the watcher tab."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title section
        title_label = QLabel("File Watcher")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Folder selection section
        folder_section = self._create_folder_selection_section()
        layout.addWidget(folder_section)

        # Control section
        control_section = self._create_control_section()
        layout.addWidget(control_section)

        # Status section
        status_section = self._create_status_section()
        layout.addWidget(status_section)

        # Add stretch to push content to top
        layout.addStretch()

    def _create_folder_selection_section(self) -> QFrame:
        """Create the folder selection section.

        Returns:
            QFrame containing folder selection controls
        """
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        frame.setLineWidth(1)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)

        # Section title
        section_label = QLabel("Watch Folder")
        section_font = QFont()
        section_font.setPointSize(12)
        section_font.setBold(True)
        section_label.setFont(section_font)
        layout.addWidget(section_label)

        # Folder path input
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Folder:"))

        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setObjectName("folder_path_edit")
        self.folder_path_edit.setPlaceholderText("Select folder to watch...")
        self.folder_path_edit.setText("./watch")  # Default value
        path_layout.addWidget(self.folder_path_edit)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self._on_browse_folder)
        path_layout.addWidget(self.browse_button)

        layout.addLayout(path_layout)

        return frame

    def _create_control_section(self) -> QFrame:
        """Create the watcher control section.

        Returns:
            QFrame containing control buttons
        """
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        frame.setLineWidth(1)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)

        # Section title
        section_label = QLabel("Watcher Control")
        section_font = QFont()
        section_font.setPointSize(12)
        section_font.setBold(True)
        section_label.setFont(section_font)
        layout.addWidget(section_label)

        # Control buttons
        button_layout = QHBoxLayout()

        self.start_stop_button = QPushButton("Start Watch")
        self.start_stop_button.setMinimumHeight(40)
        self.start_stop_button.clicked.connect(self._on_start_stop_watch)
        button_layout.addWidget(self.start_stop_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Status indicator
        self.watcher_status_label = QLabel("Watcher stopped")
        self.watcher_status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.watcher_status_label)

        return frame

    def _create_status_section(self) -> QFrame:
        """Create the status display section.

        Returns:
            QFrame containing live status displays
        """
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        frame.setLineWidth(1)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)

        # Section title
        section_label = QLabel("Live Status")
        section_font = QFont()
        section_font.setPointSize(12)
        section_font.setBold(True)
        section_label.setFont(section_font)
        layout.addWidget(section_label)

        # Diff status
        diff_layout = QHBoxLayout()
        diff_layout.addWidget(QLabel("Last Changes:"))
        self.watcher_diff_label = QLabel("No files processed")
        self.watcher_diff_label.setObjectName("watcher_diff_label")
        self.watcher_diff_label.setStyleSheet("font-weight: bold;")
        diff_layout.addWidget(self.watcher_diff_label)
        diff_layout.addStretch()
        layout.addLayout(diff_layout)

        # Slack status
        slack_layout = QHBoxLayout()
        slack_layout.addWidget(QLabel("Slack Status:"))
        self.slack_status_label = QLabel("⚪ Not connected")
        self.slack_status_label.setObjectName("slack_status_label")
        self.slack_status_label.setStyleSheet("font-weight: bold;")
        slack_layout.addWidget(self.slack_status_label)
        slack_layout.addStretch()
        layout.addLayout(slack_layout)

        return frame

    def _on_browse_folder(self) -> None:
        """Handle browse folder button click."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Watch",
            self.folder_path_edit.text() or str(Path.home()),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        if folder_path:
            self.folder_path_edit.setText(folder_path)

    def _on_start_stop_watch(self) -> None:
        """Handle start/stop watch button click."""
        if not self.is_watching:
            self._start_watching()
        else:
            self._stop_watching()

    def _start_watching(self) -> None:
        """Start the file watcher."""
        folder_path = self.folder_path_edit.text().strip()
        if not folder_path:
            QMessageBox.warning(self, "No Folder", "Please select a folder to watch.")
            return

        folder = Path(folder_path)
        if not folder.exists():
            # Create the folder if it doesn't exist
            try:
                folder.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created watch folder: {folder}")
            except Exception as e:
                QMessageBox.critical(
                    self, "Folder Error", f"Cannot create folder: {str(e)}"
                )
                return

        # Update UI
        self.start_stop_button.setText("Stop Watch")
        self.start_stop_button.setStyleSheet("background-color: #ff6b6b;")
        self.watcher_status_label.setText("Starting watcher...")
        self.watcher_status_label.setStyleSheet("color: orange; font-weight: bold;")
        self.browse_button.setEnabled(False)
        self.folder_path_edit.setEnabled(False)

        # Start worker thread
        self.worker_thread = WatcherWorker(folder_path)
        self.worker_thread.file_processed.connect(self._on_file_processed)
        self.worker_thread.processing_error.connect(self._on_processing_error)
        self.worker_thread.watcher_started.connect(self._on_watcher_started)
        self.worker_thread.watcher_stopped.connect(self._on_watcher_stopped)
        self.worker_thread.finished.connect(self._on_thread_finished)
        self.worker_thread.start()

    def _stop_watching(self) -> None:
        """Stop the file watcher."""
        if self.worker_thread:
            self.worker_thread.stop_watcher()

        # Update UI immediately
        self.watcher_status_label.setText("Stopping watcher...")
        self.watcher_status_label.setStyleSheet("color: orange; font-weight: bold;")

    def _on_watcher_started(self) -> None:
        """Handle watcher started signal."""
        self.is_watching = True
        self.watcher_status_label.setText("Watcher running")
        self.watcher_status_label.setStyleSheet("color: green; font-weight: bold;")
        self.logger.info("File watcher started successfully")

    def _on_watcher_stopped(self) -> None:
        """Handle watcher stopped signal."""
        self.is_watching = False
        self.start_stop_button.setText("Start Watch")
        self.start_stop_button.setStyleSheet("")
        self.watcher_status_label.setText("Watcher stopped")
        self.watcher_status_label.setStyleSheet("color: red; font-weight: bold;")
        self.browse_button.setEnabled(True)
        self.folder_path_edit.setEnabled(True)
        self.logger.info("File watcher stopped")

    def _on_file_processed(
        self, diff_result: dict, sheet_url: str, slack_success: bool
    ) -> None:
        """Handle successful file processing.

        Args:
            diff_result: Dictionary with diff counts
            sheet_url: URL of the updated Google Sheet
            slack_success: Whether Slack notification was successful
        """
        # Update diff status
        diff_text = f"+{diff_result['added']} / {diff_result['updated']} / {diff_result['deleted']}"
        self.watcher_diff_label.setText(diff_text)
        self.watcher_diff_label.setStyleSheet("color: green; font-weight: bold;")

        # Update Slack status
        if slack_success:
            self.slack_status_label.setText("✅ Success")
            self.slack_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.slack_status_label.setText("❌ Failed")
            self.slack_status_label.setStyleSheet("color: red; font-weight: bold;")

        self.logger.info(f"File processed: {diff_text}, Slack: {slack_success}")

    def _on_processing_error(self, error_message: str) -> None:
        """Handle file processing error.

        Args:
            error_message: Error message to display
        """
        # Update status
        self.watcher_diff_label.setText("Processing error")
        self.watcher_diff_label.setStyleSheet("color: red; font-weight: bold;")
        self.slack_status_label.setText("❌ Error")
        self.slack_status_label.setStyleSheet("color: red; font-weight: bold;")

        self.logger.error(f"File processing error: {error_message}")

    def _on_thread_finished(self) -> None:
        """Handle worker thread completion (cleanup)."""
        # Clean up thread reference
        if self.worker_thread:
            self.worker_thread.deleteLater()
            self.worker_thread = None

        # Ensure UI is updated to stopped state
        if self.is_watching:
            self._on_watcher_stopped()

    def cleanup(self) -> None:
        """Clean up resources when widget is being destroyed."""
        # Stop watcher if running
        if self.is_watching and self.worker_thread:
            self.worker_thread.stop_watcher()
            # Wait for thread to finish
            if self.worker_thread.isRunning():
                self.worker_thread.wait(2000)  # Wait up to 2 seconds
                if self.worker_thread.isRunning():
                    # Force terminate if still running
                    self.worker_thread.terminate()
                    self.worker_thread.wait(1000)

    def closeEvent(self, event) -> None:
        """Handle widget close event."""
        self.cleanup()
        super().closeEvent(event)
