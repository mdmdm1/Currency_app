from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
from database.database import SessionLocal
from database.models import AuditLog
import json

from utils.translation_manager import TranslationManager


class UserHistoryDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle(TranslationManager.tr("Historique d'utilisateur"))
        self.setGeometry(300, 200, 800, 400)  # Adjusted for more columns
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget(self)
        self.table.setColumnCount(5)  # Adjusted to show more details
        self.table.setHorizontalHeaderLabels(
            [
                TranslationManager.tr("Action"),
                TranslationManager.tr("Table"),
                TranslationManager.tr("ID de l'enregistrement"),
                TranslationManager.tr("Details"),
                TranslationManager.tr("Horodatage"),
            ]
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_user_history()

    def load_user_history(self):
        session = SessionLocal()
        try:
            logs = (
                session.query(AuditLog)
                .filter(AuditLog.user_id == self.user_id)
                .order_by(AuditLog.timestamp.desc())
                .all()
            )

            if not logs:
                self.table.setRowCount(0)
                no_logs_label = QLabel(
                    TranslationManager.tr("Pas d'historique pour cet utilisateur.")
                )
                no_logs_label.setStyleSheet("color: gray; font-style: italic;")
                self.layout().addWidget(no_logs_label)
                return

            self.table.setRowCount(len(logs))
            for row, log in enumerate(logs):
                self.table.setItem(row, 0, QTableWidgetItem(log.operation))
                self.table.setItem(row, 1, QTableWidgetItem(log.table_name))
                self.table.setItem(row, 2, QTableWidgetItem(str(log.record_id)))

                # Parse changes or details
                try:
                    details = (
                        json.loads(log.changes)
                        if log.changes
                        else TranslationManager.tr("Pas de details")
                    )
                    details_str = (
                        json.dumps(details, indent=2)
                        if isinstance(details, dict)
                        else str(details)
                    )
                except json.JSONDecodeError:
                    details_str = str(
                        log.changes or TranslationManager.tr("Pas de details")
                    )

                self.table.setItem(row, 3, QTableWidgetItem(details_str))
                self.table.setItem(
                    row,
                    4,
                    QTableWidgetItem(log.timestamp.strftime("%Y-%m-%d %H:%M:%S")),
                )
        except Exception as e:
            print(f"{TranslationManager.tr('Error loading history:')} {e}")
            error_label = QLabel(
                TranslationManager.tr("Erreur lors du chargement de l'historique.")
            )
            error_label.setStyleSheet("color: red;")
            self.layout().addWidget(error_label)
        finally:
            session.close()
