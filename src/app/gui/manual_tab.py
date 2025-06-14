"""Manual sync tab module for sheets-bot GUI.

This module contains the ManualSyncTab widget that provides UI for manual
file synchronization operations with complete backend integration.
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
    QMessageBox,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from ..core.parser import parse_file, UnsupportedFileTypeError
from ..integrations.sheets_client import SheetsClient, SheetsPushError
from ..core.delta import DeltaTracker
from ..integrations.notifier import SlackNotifier


class ManualSyncWorker(QThread):
    """Background worker thread for manual sync operations.

    This worker handles the complete sync workflow in a separate thread
    to prevent GUI freezing during file processing operations.
    """

    # Signals for communicating with main thread
    sync_completed = Signal(dict, str)  # diff_result, sheet_url
    sync_failed = Signal(str)  # error_message

    def __init__(self, file_path: str):
        """Initialize the worker thread.

        Args:
            file_path: Path to the file to process
        """
        super().__init__()
        self.file_path = file_path
        self.logger = logging.getLogger("sheets-bot")

    def run(self) -> None:
        """Run the complete sync workflow in background thread."""
        try:
            self.logger.info(f"Starting manual sync for file: {self.file_path}")

            # Step 1: Parse the file
            df = parse_file(self.file_path)
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
            self.sync_completed.emit(diff_result, sheet_url)

        except (UnsupportedFileTypeError, FileNotFoundError) as e:
            error_msg = f"File error: {str(e)}"
            self.logger.error(error_msg)
            self.sync_failed.emit(error_msg)

        except SheetsPushError as e:
            error_msg = f"Sheets push error: {str(e)}"
            self.logger.error(error_msg)
            self.sync_failed.emit(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg)
            self.sync_failed.emit(error_msg)


class ManualSyncTab(QWidget):
    """Manual sync tab widget for manual file operations.

    This widget provides a complete interface for selecting files,
    processing them through the sheets-bot workflow, and displaying results.
    """

    def __init__(self, parent=None):
        """Initialize the manual sync tab.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.logger = logging.getLogger("sheets-bot")
        self.worker_thread: Optional[ManualSyncWorker] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface for the manual sync tab."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title section
        title_label = QLabel("Manual File Sync")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # File selection section
        file_section = self._create_file_selection_section()
        layout.addWidget(file_section)

        # Status section
        status_section = self._create_status_section()
        layout.addWidget(status_section)

        # Add stretch to push content to top
        layout.addStretch()

    def _create_file_selection_section(self) -> QFrame:
        """Create the file selection section.

        Returns:
            QFrame containing file selection controls
        """
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        frame.setLineWidth(1)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)

        # Section title
        section_label = QLabel("File Selection")
        section_font = QFont()
        section_font.setPointSize(12)
        section_font.setBold(True)
        section_label.setFont(section_font)
        layout.addWidget(section_label)

        # File selection button
        button_layout = QHBoxLayout()
        self.select_button = QPushButton("Select File")
        self.select_button.setMinimumHeight(40)
        self.select_button.clicked.connect(self._on_select_file)
        button_layout.addWidget(self.select_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Selected file display
        self.selected_file_label = QLabel("No file selected")
        self.selected_file_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.selected_file_label)

        return frame

    def _create_status_section(self) -> QFrame:
        """Create the status display section.

        Returns:
            QFrame containing status displays
        """
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        frame.setLineWidth(1)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)

        # Section title
        section_label = QLabel("Sync Status")
        section_font = QFont()
        section_font.setPointSize(12)
        section_font.setBold(True)
        section_label.setFont(section_font)
        layout.addWidget(section_label)

        # Diff status
        diff_layout = QHBoxLayout()
        diff_layout.addWidget(QLabel("Changes:"))
        self.diff_status_label = QLabel("No sync performed")
        self.diff_status_label.setObjectName("diff_status_label")
        self.diff_status_label.setStyleSheet("font-weight: bold;")
        diff_layout.addWidget(self.diff_status_label)
        diff_layout.addStretch()
        layout.addLayout(diff_layout)

        # URL status
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Sheet URL:"))
        self.url_status_label = QLabel("No sheet URL available")
        self.url_status_label.setObjectName("url_status_label")
        self.url_status_label.setOpenExternalLinks(True)
        self.url_status_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        url_layout.addWidget(self.url_status_label)
        url_layout.addStretch()
        layout.addLayout(url_layout)

        return frame

    def _on_select_file(self) -> None:
        """Handle file selection button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File to Sync",
            str(Path.home()),
            "Spreadsheet files (*.csv *.xlsx *.xls);;CSV files (*.csv);;Excel files (*.xlsx *.xls);;All files (*)",
        )

        if file_path:
            self.selected_file_label.setText(f"Selected: {Path(file_path).name}")
            self.selected_file_label.setStyleSheet("color: blue;")
            self._start_sync(file_path)

    def _start_sync(self, file_path: str) -> None:
        """Start the sync process in background thread.

        Args:
            file_path: Path to the file to sync
        """
        # Disable button during processing
        self.select_button.setEnabled(False)
        self.select_button.setText("Processing...")

        # Update status
        self.diff_status_label.setText("Processing file...")
        self.url_status_label.setText("Pushing to Google Sheets...")

        # Start worker thread
        self.worker_thread = ManualSyncWorker(file_path)
        self.worker_thread.sync_completed.connect(self._on_sync_completed)
        self.worker_thread.sync_failed.connect(self._on_sync_failed)
        self.worker_thread.finished.connect(self._on_thread_finished)
        self.worker_thread.start()

    def _on_sync_completed(self, diff_result: dict, sheet_url: str) -> None:
        """Handle successful sync completion.

        Args:
            diff_result: Dictionary with diff counts
            sheet_url: URL of the updated Google Sheet
        """
        # Update diff status
        diff_text = f"+{diff_result['added']} / {diff_result['updated']} / {diff_result['deleted']}"
        self.diff_status_label.setText(diff_text)
        self.diff_status_label.setStyleSheet("color: green; font-weight: bold;")

        # Update URL status with clickable link
        url_html = f'<a href="{sheet_url}" style="color: blue;">{sheet_url}</a>'
        self.url_status_label.setText(url_html)

        self.logger.info("Manual sync completed successfully")

    def _on_sync_failed(self, error_message: str) -> None:
        """Handle sync failure.

        Args:
            error_message: Error message to display
        """
        # Update status to show error
        self.diff_status_label.setText("Sync failed")
        self.diff_status_label.setStyleSheet("color: red; font-weight: bold;")
        self.url_status_label.setText("No URL available")

        # Show error dialog
        QMessageBox.critical(self, "Sync Error", error_message)

        self.logger.error(f"Manual sync failed: {error_message}")

    def _on_thread_finished(self) -> None:
        """Handle worker thread completion (cleanup)."""
        # Re-enable button
        self.select_button.setEnabled(True)
        self.select_button.setText("Select File")

        # Clean up thread reference
        if self.worker_thread:
            self.worker_thread.deleteLater()
            self.worker_thread = None

    def cleanup(self) -> None:
        """Clean up resources when widget is being destroyed."""
        if self.worker_thread and self.worker_thread.isRunning():
            # Terminate the thread if it's still running
            self.worker_thread.terminate()
            self.worker_thread.wait(1000)  # Wait up to 1 second
            if self.worker_thread.isRunning():
                # Force kill if still running
                self.worker_thread.quit()
                self.worker_thread.wait()

    def closeEvent(self, event) -> None:
        """Handle widget close event."""
        self.cleanup()
        super().closeEvent(event)
