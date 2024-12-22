from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QSizePolicy,
    QHeaderView,
    QMessageBox,
)
from PyQt5.QtCore import Qt
import cx_Oracle


def connect_to_db():
    dsn = cx_Oracle.makedsn("localhost", "1521", service_name="MANAGEMENT3")
    return cx_Oracle.connect(user="admin", password="2024", dsn=dsn)


class DepositPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des dépôts")
        # self.setLayoutDirection(Qt.RightToLeft)  # For RTL layout if needed
        self.setStyleSheet(self.style_sheet())  # Apply custom stylesheet

        self.init_ui(parent)
        self.parent_window = parent

    def style_sheet(self):
        return """
            QWidget {
                font-family: Arial, sans-serif;
                font-size: 12px;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                min-width: 80px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton#addButton {
                background-color: #28a745;
            }
            QPushButton#deleteButton {
                background-color: #dc3545;
            }
            QPushButton#returnButton {
                background-color: #17a2b8;
            }
            QTableWidget {
                border: 1px solid #ddd;
                background-color: #ffffff;
                alternate-background-color: #f5f5f5;
                font-size: 12px;
            }
            QTableWidget QHeaderView::section {
                background-color: #007BFF;
                color: white;
                padding: 8px;
                font-size: 14px;
                border: 1px solid #007BFF;
                font-weight: bold;
                text-align: center;
            }
            QTableWidget::item {
                padding: 1px;
                border: 1px solid #ddd;
            }
            QTableWidget::item:selected {
                background-color: #007BFF;
                color: white;
            }
        """

    def init_ui(self, parent):
        # Main layout for the deposit page
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        # Button definitions
        self.add_button = QPushButton("Ajouter un dépôt")
        self.delete_button = QPushButton("Supprimer")
        self.ret_button = QPushButton("Retour")

        # Assign unique styles
        self.add_button.setObjectName("addButton")
        self.delete_button.setObjectName("deleteButton")
        self.ret_button.setObjectName("returnButton")

        # Connect buttons to actions
        self.add_button.clicked.connect(self.add_deposit)
        self.delete_button.clicked.connect(self.delete_deposit)
        self.ret_button.clicked.connect(self.return_to_previous)

        # Add buttons to layout
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.ret_button)
        button_layout.addStretch()

        # Add button layout to main layout
        main_layout.addWidget(QWidget().setLayout(button_layout))

        # Table setup
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Nom", "Montant", "Date du dépôt", "Dépôt libéré", "Dépôt actuel"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Add table to layout
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

        # Load deposit data
        self.load_deposit_data()

    def load_deposit_data(self):
        # Load data from database into the table
        with connect_to_db() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT ID, PERSON_NAME, AMOUNT, TO_CHAR(DEPOSIT_DATE, 'YYYY-MM-DD') AS DEPOSIT_DATE,
                       RELEASED_DEPOSIT, CURRENT_DEBT 
                FROM DEPOSITS ORDER BY ID DESC
            """
            )
            rows = cursor.fetchall()
            self.table.setRowCount(len(rows))

            self.deposit_ids = {}
            for row_idx, row in enumerate(rows):
                self.deposit_ids[row_idx] = row[0]  # Save ID for deletion
                for col_idx, item in enumerate(row[1:]):
                    table_item = QTableWidgetItem(str(item) if item is not None else "")
                    table_item.setTextAlignment(Qt.AlignCenter)
                    if col_idx in [0, 1, 2, 4]:  # Make certain columns non-editable
                        table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row_idx, col_idx, table_item)

    def add_deposit(self):
        # Implementation for adding a deposit (to be implemented)
        pass

    def delete_deposit(self):
        # Deleting selected deposit
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(
                self, "Alerte", "Veuillez sélectionner une ligne à supprimer."
            )
            return

        deposit_id = self.deposit_ids[selected_row]
        with connect_to_db() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM DEPOSITS WHERE ID = :id", id=deposit_id)
            connection.commit()

        self.load_deposit_data()
        QMessageBox.information(self, "Information", "Dépôt supprimé avec succès.")

    def return_to_previous(self):
        # Go back to previous window
        self.parent_window.setCurrentIndex(0)
