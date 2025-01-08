from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem
from database.database import SessionLocal
from database.models import AuditLog


class UserHistoryDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Historique de l'utilisateur")
        self.setGeometry(300, 200, 600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Action", "Détails", "Horodatage"])
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

            self.table.setRowCount(len(logs))
            for row, log in enumerate(logs):
                self.table.setItem(row, 0, QTableWidgetItem(log.action))
                self.table.setItem(row, 1, QTableWidgetItem(log.details or ""))
                self.table.setItem(
                    row,
                    2,
                    QTableWidgetItem(log.timestamp.strftime("%Y-%m-%d %H:%M:%S")),
                )
        except Exception as e:
            print(f"Failed to load user history: {e}")
        finally:
            session.close()
