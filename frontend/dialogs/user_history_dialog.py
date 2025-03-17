from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QHeaderView,
)
import requests
import json
from datetime import datetime  # Import datetime for timestamp conversion

from utils.translation_manager import TranslationManager
from config import API_BASE_URL


class UserHistoryDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle(TranslationManager.tr("Historique d'utilisateur"))
        self.setGeometry(300, 200, 900, 400)  # Increased width for better layout
        self.api_base_url = API_BASE_URL
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            [
                TranslationManager.tr("Action"),
                TranslationManager.tr("Table"),
                TranslationManager.tr("ID de l'enregistrement"),
                TranslationManager.tr("Détails"),
                TranslationManager.tr("Horodatage"),
            ]
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        # Adjust column widths
        self.table.setColumnWidth(0, 100)  # Action
        self.table.setColumnWidth(1, 100)  # Table
        self.table.setColumnWidth(2, 120)  # Record ID
        self.table.setColumnWidth(3, 350)  # Details
        self.table.setColumnWidth(4, 150)  # Timestamp

        # Make rows taller
        self.table.verticalHeader().setDefaultSectionSize(
            80
        )  # Set default row height to 80 pixels

        # Allow text wrapping in cells
        self.table.setWordWrap(True)

        # Make the table resize rows to content
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_user_history()

    def load_user_history(self):
        try:
            audit_response = requests.get(
                f"{self.api_base_url}/audit_logs/by-user/{self.user_id}"
            )

            # Check if the user has no logs (FastAPI returns 404 in this case)
            if audit_response.status_code == 404:
                self.table.setRowCount(0)  # Ensure the table is cleared
                no_logs_label = QLabel(
                    TranslationManager.tr("Pas d'historique pour cet utilisateur.")
                )
                no_logs_label.setStyleSheet("color: gray; font-style: italic;")
                self.layout().addWidget(no_logs_label)
                return  # Stop execution here

            audit_response.raise_for_status()  # Raise an exception for other errors (e.g., 500)

            logs = audit_response.json()

            self.table.setRowCount(len(logs))
            for row, log in enumerate(logs):
                self.table.setItem(row, 0, QTableWidgetItem(log["operation"]))
                self.table.setItem(row, 1, QTableWidgetItem(log["table_name"]))
                self.table.setItem(row, 2, QTableWidgetItem(str(log["record_id"])))

                # Parse changes or details
                try:
                    details = (
                        json.loads(log["changes"])
                        if log["changes"]
                        else TranslationManager.tr("Pas de détails")
                    )
                    details_str = (
                        json.dumps(details, indent=2)
                        if isinstance(details, dict)
                        else str(details)
                    )
                except json.JSONDecodeError:
                    details_str = str(
                        log["changes"] or TranslationManager.tr("Pas de détails")
                    )

                details_item = QTableWidgetItem(details_str)
                details_item.setToolTip(details_str)  # Show full details on hover
                self.table.setItem(row, 3, details_item)

                # Convert timestamp string to datetime object
                timestamp_str = log["timestamp"]
                formatted_timestamp = timestamp_str  # Default raw string

                try:
                    from datetime import datetime

                    timestamp_dt = datetime.fromisoformat(timestamp_str)
                    formatted_timestamp = timestamp_dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    formatted_timestamp = TranslationManager.tr("Format invalide")

                self.table.setItem(row, 4, QTableWidgetItem(formatted_timestamp))

        except requests.exceptions.RequestException as e:
            print(f"{TranslationManager.tr('Error loading history:')} {e}")
            error_label = QLabel(
                f"{TranslationManager.tr('Erreur lors du chargement de l historique:')} {e}"
            )
            error_label.setStyleSheet("color: red;")
            self.layout().addWidget(error_label)
