"""Configuration tab for managing Google Sheets API credentials and app settings.

This module provides a user-friendly interface for setting up Google Sheets API
credentials and configuring application settings without requiring users to
manually edit JSON or TOML files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import tomli

# Try to import tomli_w, fall back gracefully if not available
try:
    import tomli_w
    TOMLI_W_AVAILABLE = True
except ImportError:
    TOMLI_W_AVAILABLE = False
    print("⚠️  tomli_w not available - configuration saving may be limited")

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QGroupBox,
    QScrollArea,
    QMessageBox,
    QProgressBar,
    QFrame,
    QSizePolicy,
)
from PySide6.QtGui import QFont, QPixmap, QIcon

from ..integrations.sheets_client import SheetsClient, SheetsPushError


class CredentialsTestWorker(QThread):
    """Worker thread for testing Google Sheets API credentials."""
    
    test_completed = Signal(bool, str)  # success, message
    
    def __init__(self, creds_data: Dict[str, Any], spreadsheet_id: str, worksheet_name: str):
        """Initialize the credentials test worker.
        
        Args:
            creds_data: Dictionary containing Google Sheets credentials
            spreadsheet_id: ID of the Google Sheets spreadsheet to test
            worksheet_name: Name of the worksheet to test
        """
        super().__init__()
        self.creds_data = creds_data
        self.spreadsheet_id = spreadsheet_id
        self.worksheet_name = worksheet_name
        self.logger = logging.getLogger("sheets-bot.config")
    
    def run(self) -> None:
        """Run the credentials test in background thread."""
        try:
            # Create temporary credentials file
            temp_creds_path = Path("config/temp_creds.json")
            temp_settings_path = Path("config/temp_settings.toml")
            
            # Write temporary credentials
            with open(temp_creds_path, 'w') as f:
                json.dump(self.creds_data, f, indent=2)
            
            # Write temporary settings
            temp_settings = {
                "sheets": {
                    "spreadsheet_id": self.spreadsheet_id,
                    "worksheet_name": self.worksheet_name
                }
            }
            if TOMLI_W_AVAILABLE:
                with open(temp_settings_path, 'wb') as f:
                    tomli_w.dump(temp_settings, f)
            else:
                # Simple fallback for testing
                toml_content = f"""[sheets]
                spreadsheet_id = "{self.spreadsheet_id}"
                worksheet_name = "{self.worksheet_name}"
                """
                with open(temp_settings_path, 'w') as f:
                    f.write(toml_content)
            
            # Test the connection
            client = SheetsClient(
                creds_path=temp_creds_path,
                settings_path=temp_settings_path
            )
            
            # Try to access the spreadsheet (without writing data)
            import gspread
            gc = gspread.service_account(filename=temp_creds_path)
            spreadsheet = gc.open_by_key(self.spreadsheet_id)
            worksheet = spreadsheet.worksheet(self.worksheet_name)
            
            # Clean up temporary files
            temp_creds_path.unlink(missing_ok=True)
            temp_settings_path.unlink(missing_ok=True)
            
            self.test_completed.emit(True, f"✅ Successfully connected to '{worksheet.title}' in spreadsheet!")
            
        except Exception as e:
            # Clean up temporary files on error
            Path("config/temp_creds.json").unlink(missing_ok=True)
            Path("config/temp_settings.toml").unlink(missing_ok=True)
            
            error_msg = f"❌ Connection failed: {str(e)}"
            self.logger.error(error_msg)
            self.test_completed.emit(False, error_msg)


class ConfigTab(QWidget):
    """Configuration tab for managing API credentials and app settings."""
    
    credentials_saved = Signal(bool)  # Emitted when credentials are saved successfully
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the configuration tab.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.logger = logging.getLogger("sheets-bot.config")
        self._setup_ui()
        self._load_existing_config()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Main layout with scroll area for better organization
        main_layout = QVBoxLayout(self)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Header section
        self._create_header_section(content_layout)
        
        # Google Sheets API section
        self._create_api_credentials_section(content_layout)
        
        # Spreadsheet configuration section
        self._create_spreadsheet_config_section(content_layout)
        
        # Test connection section
        self._create_test_section(content_layout)
        
        # Action buttons section
        self._create_action_buttons_section(content_layout)
        
        # Status section
        self._create_status_section(content_layout)
        
        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def _create_header_section(self, layout: QVBoxLayout) -> None:
        """Create the header section with instructions."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.Box)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f8ff;
                border: 2px solid #4a90e2;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        
        # Title
        title_label = QLabel("🔧 Google Sheets API Configuration")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Instructions
        instructions = QLabel(
            "📋 <b>Setup Instructions:</b><br>"
            "1. Go to <a href='https://console.cloud.google.com/'>Google Cloud Console</a><br>"
            "2. Create a new project or select existing one<br>"
            "3. Enable Google Sheets API<br>"
            "4. Create service account credentials<br>"
            "5. Download the JSON key file and copy the values below<br>"
            "6. Share your Google Sheet with the service account email"
        )
        instructions.setWordWrap(True)
        instructions.setOpenExternalLinks(True)
        instructions.setStyleSheet("color: #2c3e50; padding: 10px;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(instructions)
        layout.addWidget(header_frame)
    
    def _create_api_credentials_section(self, layout: QVBoxLayout) -> None:
        """Create the Google Sheets API credentials section."""
        # API Credentials Group
        api_group = QGroupBox("🔑 Google Sheets API Credentials")
        api_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0px 5px 0px 5px;
            }
        """)
        
        api_layout = QFormLayout(api_group)
        api_layout.setSpacing(10)
        
        # Project ID
        self.project_id_input = QLineEdit()
        self.project_id_input.setPlaceholderText("your-project-id")
        self.project_id_input.setStyleSheet("padding: 8px; font-size: 10pt;")
        api_layout.addRow("Project ID:", self.project_id_input)
        
        # Service Account Email
        self.service_email_input = QLineEdit()
        self.service_email_input.setPlaceholderText("your-service-account@your-project-id.iam.gserviceaccount.com")
        self.service_email_input.setStyleSheet("padding: 8px; font-size: 10pt;")
        api_layout.addRow("Service Account Email:", self.service_email_input)
        
        # Private Key ID
        self.private_key_id_input = QLineEdit()
        self.private_key_id_input.setPlaceholderText("your-private-key-id")
        self.private_key_id_input.setStyleSheet("padding: 8px; font-size: 10pt;")
        api_layout.addRow("Private Key ID:", self.private_key_id_input)
        
        # Private Key (multi-line)
        self.private_key_input = QTextEdit()
        self.private_key_input.setPlaceholderText("-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_CONTENT_HERE\n-----END PRIVATE KEY-----")
        self.private_key_input.setMaximumHeight(120)
        self.private_key_input.setStyleSheet("padding: 8px; font-size: 9pt; font-family: 'Courier New', monospace;")
        api_layout.addRow("Private Key:", self.private_key_input)
        
        # Client ID
        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText("your-client-id")
        self.client_id_input.setStyleSheet("padding: 8px; font-size: 10pt;")
        api_layout.addRow("Client ID:", self.client_id_input)
        
        layout.addWidget(api_group)
    
    def _create_spreadsheet_config_section(self, layout: QVBoxLayout) -> None:
        """Create the spreadsheet configuration section."""
        # Spreadsheet Config Group
        sheet_group = QGroupBox("📊 Spreadsheet Configuration")
        sheet_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0px 5px 0px 5px;
            }
        """)
        
        sheet_layout = QFormLayout(sheet_group)
        sheet_layout.setSpacing(10)
        
        # Spreadsheet ID
        self.spreadsheet_id_input = QLineEdit()
        self.spreadsheet_id_input.setPlaceholderText("Extract from: https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit")
        self.spreadsheet_id_input.setStyleSheet("padding: 8px; font-size: 10pt;")
        sheet_layout.addRow("Spreadsheet ID:", self.spreadsheet_id_input)
        
        # Worksheet Name
        self.worksheet_name_input = QLineEdit()
        self.worksheet_name_input.setPlaceholderText("Sheet1")
        self.worksheet_name_input.setText("Sheet1")  # Default value
        self.worksheet_name_input.setStyleSheet("padding: 8px; font-size: 10pt;")
        sheet_layout.addRow("Worksheet Name:", self.worksheet_name_input)
        
        layout.addWidget(sheet_group)
    
    def _create_test_section(self, layout: QVBoxLayout) -> None:
        """Create the test connection section."""
        # Test Group
        test_group = QGroupBox("🧪 Test Connection")
        test_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0px 5px 0px 5px;
            }
        """)
        
        test_layout = QVBoxLayout(test_group)
        
        # Test button
        self.test_button = QPushButton("🔍 Test Google Sheets Connection")
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.test_button.clicked.connect(self._test_connection)
        
        # Progress bar (hidden by default)
        self.test_progress = QProgressBar()
        self.test_progress.setVisible(False)
        self.test_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
        """)
        
        # Test result label
        self.test_result_label = QLabel("")
        self.test_result_label.setWordWrap(True)
        self.test_result_label.setStyleSheet("padding: 10px; font-size: 10pt;")
        
        test_layout.addWidget(self.test_button)
        test_layout.addWidget(self.test_progress)
        test_layout.addWidget(self.test_result_label)
        
        layout.addWidget(test_group)
    
    def _create_action_buttons_section(self, layout: QVBoxLayout) -> None:
        """Create the action buttons section."""
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Save button
        self.save_button = QPushButton("💾 Save Configuration")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.save_button.clicked.connect(self._save_configuration)
        
        # Reset button
        self.reset_button = QPushButton("🔄 Reset Fields")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.reset_button.clicked.connect(self._reset_fields)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addStretch()  # Push buttons to the left
        
        layout.addLayout(buttons_layout)
    
    def _create_status_section(self, layout: QVBoxLayout) -> None:
        """Create the status section."""
        # Status label
        self.status_label = QLabel("📝 Ready to configure Google Sheets API credentials")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 10px;
                font-size: 10pt;
                color: #2c3e50;
            }
        """)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
    
    def _load_existing_config(self) -> None:
        """Load existing configuration from files."""
        try:
            # Load credentials
            creds_path = Path("config/creds.json")
            if creds_path.exists():
                with open(creds_path, 'r') as f:
                    creds_data = json.load(f)
                    
                self.project_id_input.setText(creds_data.get("project_id", ""))
                self.service_email_input.setText(creds_data.get("client_email", ""))
                self.private_key_id_input.setText(creds_data.get("private_key_id", ""))
                self.private_key_input.setPlainText(creds_data.get("private_key", ""))
                self.client_id_input.setText(creds_data.get("client_id", ""))
                
                self.status_label.setText("✅ Loaded existing credentials from config/creds.json")
            
            # Load settings
            settings_path = Path("config/settings.toml")
            if settings_path.exists():
                with open(settings_path, 'rb') as f:
                    settings_data = tomli.load(f)
                    
                sheets_config = settings_data.get("sheets", {})
                self.spreadsheet_id_input.setText(sheets_config.get("spreadsheet_id", ""))
                self.worksheet_name_input.setText(sheets_config.get("worksheet_name", "Sheet1"))
                
        except Exception as e:
            self.logger.warning(f"Could not load existing configuration: {e}")
            self.status_label.setText(f"⚠️ Could not load existing configuration: {e}")
    
    def _test_connection(self) -> None:
        """Test the Google Sheets API connection."""
        # Validate inputs
        if not self._validate_inputs():
            return
        
        # Prepare credentials data
        creds_data = {
            "type": "service_account",
            "project_id": self.project_id_input.text().strip(),
            "private_key_id": self.private_key_id_input.text().strip(),
            "private_key": self.private_key_input.toPlainText().strip(),
            "client_email": self.service_email_input.text().strip(),
            "client_id": self.client_id_input.text().strip(),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{self.service_email_input.text().strip()}"
        }
        
        # Show progress
        self.test_button.setEnabled(False)
        self.test_button.setText("🔄 Testing Connection...")
        self.test_progress.setVisible(True)
        self.test_progress.setRange(0, 0)  # Indeterminate progress
        self.test_result_label.setText("Testing connection to Google Sheets...")
        
        # Start test worker
        self.test_worker = CredentialsTestWorker(
            creds_data,
            self.spreadsheet_id_input.text().strip(),
            self.worksheet_name_input.text().strip()
        )
        self.test_worker.test_completed.connect(self._on_test_completed)
        self.test_worker.start()
    
    def _on_test_completed(self, success: bool, message: str) -> None:
        """Handle test completion.
        
        Args:
            success: Whether the test was successful
            message: Result message to display
        """
        # Hide progress
        self.test_progress.setVisible(False)
        self.test_button.setEnabled(True)
        self.test_button.setText("🔍 Test Google Sheets Connection")
        
        # Show result
        self.test_result_label.setText(message)
        
        if success:
            self.test_result_label.setStyleSheet("""
                QLabel {
                    background-color: #d5f4e6;
                    border: 2px solid #27ae60;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 10pt;
                    color: #1e8449;
                    font-weight: bold;
                }
            """)
        else:
            self.test_result_label.setStyleSheet("""
                QLabel {
                    background-color: #fadbd8;
                    border: 2px solid #e74c3c;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 10pt;
                    color: #c0392b;
                    font-weight: bold;
                }
            """)
    
    def _save_configuration(self) -> None:
        """Save the configuration to files."""
        try:
            # Validate inputs
            if not self._validate_inputs():
                return
            
            # Ensure config directory exists
            config_dir = Path("config")
            config_dir.mkdir(exist_ok=True)
            
            # Prepare credentials data
            creds_data = {
                "type": "service_account",
                "project_id": self.project_id_input.text().strip(),
                "private_key_id": self.private_key_id_input.text().strip(),
                "private_key": self.private_key_input.toPlainText().strip(),
                "client_email": self.service_email_input.text().strip(),
                "client_id": self.client_id_input.text().strip(),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{self.service_email_input.text().strip()}"
            }
            
            # Save credentials
            creds_path = Path("config/creds.json")
            with open(creds_path, 'w') as f:
                json.dump(creds_data, f, indent=2)
            
            # Prepare settings data
            settings_data = {
                "sheets": {
                    "spreadsheet_id": self.spreadsheet_id_input.text().strip(),
                    "worksheet_name": self.worksheet_name_input.text().strip()
                },
                "slack": {
                    "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                    "channel": "#general",
                    "username": "Sheets-Bot",
                    "icon_emoji": ":robot_face:"
                },
                "watcher": {
                    "folder": "./watch",
                    "patterns": ["*.csv", "*.xlsx"],
                    "poll_interval": 5
                }
            }
            
            # Save settings
            settings_path = Path("config/settings.toml")
            if TOMLI_W_AVAILABLE:
                with open(settings_path, 'wb') as f:
                    tomli_w.dump(settings_data, f)
            else:
                # Fallback: create a basic TOML manually if tomli_w is not available
                toml_content = self._create_basic_toml(settings_data)
                with open(settings_path, 'w') as f:
                    f.write(toml_content)
            
            # Update status
            self.status_label.setText("✅ Configuration saved successfully! You can now use the other tabs to sync your data.")
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #d5f4e6;
                    border: 2px solid #27ae60;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 10pt;
                    color: #1e8449;
                    font-weight: bold;
                }
            """)
            
            # Emit signal
            self.credentials_saved.emit(True)
            
            self.logger.info("Configuration saved successfully")
            
            # Show success message
            QMessageBox.information(
                self,
                "Configuration Saved",
                "✅ Google Sheets API configuration has been saved successfully!\n\n"
                "You can now:\n"
                "• Use the Manual Sync tab to upload files\n"
                "• Set up file watching in the Watcher tab\n"
                "• Test your configuration anytime"
            )
            
        except Exception as e:
            error_msg = f"❌ Failed to save configuration: {str(e)}"
            self.status_label.setText(error_msg)
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #fadbd8;
                    border: 2px solid #e74c3c;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 10pt;
                    color: #c0392b;
                    font-weight: bold;
                }
            """)
            
            self.logger.error(error_msg)
            
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save configuration:\n\n{str(e)}"
            )
    
    def _reset_fields(self) -> None:
        """Reset all input fields."""
        reply = QMessageBox.question(
            self,
            "Reset Fields",
            "Are you sure you want to reset all fields?\n\nThis will clear all entered data.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.project_id_input.clear()
            self.service_email_input.clear()
            self.private_key_id_input.clear()
            self.private_key_input.clear()
            self.client_id_input.clear()
            self.spreadsheet_id_input.clear()
            self.worksheet_name_input.setText("Sheet1")
            
            self.test_result_label.clear()
            self.status_label.setText("📝 Fields reset - ready to configure Google Sheets API credentials")
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 10pt;
                    color: #2c3e50;
                }
            """)
    
    def _validate_inputs(self) -> bool:
        """Validate user inputs.
        
        Returns:
            bool: True if all inputs are valid, False otherwise
        """
        # Check required fields
        required_fields = [
            (self.project_id_input, "Project ID"),
            (self.service_email_input, "Service Account Email"),
            (self.private_key_id_input, "Private Key ID"),
            (self.private_key_input, "Private Key"),
            (self.client_id_input, "Client ID"),
            (self.spreadsheet_id_input, "Spreadsheet ID"),
            (self.worksheet_name_input, "Worksheet Name"),
        ]
        
        for field, name in required_fields:
            if isinstance(field, QLineEdit):
                value = field.text().strip()
            else:  # QTextEdit
                value = field.toPlainText().strip()
                
            if not value:
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    f"Please fill in the {name} field."
                )
                field.setFocus()
                return False
        
        # Validate email format
        email = self.service_email_input.text().strip()
        if "@" not in email or not email.endswith(".gserviceaccount.com"):
            QMessageBox.warning(
                self,
                "Invalid Email",
                "Service Account Email should be in format:\nyour-service-account@your-project-id.iam.gserviceaccount.com"
            )
            self.service_email_input.setFocus()
            return False
        
        # Validate private key format
        private_key = self.private_key_input.toPlainText().strip()
        if not private_key.startswith("-----BEGIN PRIVATE KEY-----"):
            QMessageBox.warning(
                self,
                "Invalid Private Key",
                "Private Key should start with:\n-----BEGIN PRIVATE KEY-----"
            )
            self.private_key_input.setFocus()
            return False
        
        return True
    
    def _create_basic_toml(self, settings_data: Dict[str, Any]) -> str:
        """Create basic TOML content manually if tomli_w is not available.
        
        Args:
            settings_data: Dictionary containing settings to convert to TOML
            
        Returns:
            str: TOML formatted string
        """
        toml_lines = []
        
        for section_name, section_data in settings_data.items():
            toml_lines.append(f"[{section_name}]")
            for key, value in section_data.items():
                if isinstance(value, str):
                    toml_lines.append(f'{key} = "{value}"')
                elif isinstance(value, list):
                    value_str = ", ".join(f'"{item}"' for item in value)
                    toml_lines.append(f'{key} = [{value_str}]')
                else:
                    toml_lines.append(f'{key} = {value}')
            toml_lines.append("")  # Empty line between sections
        
        return "\n".join(toml_lines)