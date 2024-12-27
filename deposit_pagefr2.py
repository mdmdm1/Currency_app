from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QSizePolicy,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QLabel,
)
from PyQt5.QtCore import Qt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from dialogs.add_deposit_dialog import AddDepositDialog
from database.models import (
    Customer,
    Deposit,
)
from database.database import SessionLocal
from dialogs.withdraw_deposit_dialog import WithdrawDepositDialog


class DepositPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Gestion des dépôts")
        self.setStyleSheet(self.load_stylesheet())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                "Nom",
                "NNI",
                "Date de dépôt",
                "Montant initial",
                "Dépôt libéré",
                "Dette actuelle",
                "Actions",
            ]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)

        # Total Deposited Amount
        self.total_amount_label = QLabel("Total Déposé: 0")
        self.total_amount_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.total_amount_label, alignment=Qt.AlignLeft)

        # Add "Add Deposit" Button
        add_button = QPushButton("Ajouter un dépôt")
        add_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        add_button.clicked.connect(self.add_deposit)
        layout.addWidget(add_button, alignment=Qt.AlignBottom | Qt.AlignRight)

        self.setLayout(layout)
        self.load_deposit_data()

    def load_stylesheet(self):
        return """
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 15px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QTableWidget {
                border: 1px solid #ddd;
                background-color: #ffffff;
                alternate-background-color: #f5f5f5;
            }
            QTableWidget QHeaderView::section {
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                text-align: center;
            }
        """

    def load_deposit_data(self):
        # print("Loading deposit data from database...")
        session = SessionLocal()
        try:
            deposits = (
                session.query(Deposit)
                .join(Customer, Deposit.customer_id == Customer.id)
                .add_columns(
                    Customer.name,
                    Customer.identite,
                    Deposit.deposit_date,
                    Deposit.amount,
                    Deposit.released_deposit,
                    Deposit.current_debt,
                )
                .filter(Deposit.current_debt > 0)
                .all()
            )
            self.table.setRowCount(len(deposits))
            total_deposited = 0

            for row_idx, row in enumerate(deposits):
                (
                    customer_name,
                    identite,
                    deposit_date,
                    amount,
                    released_deposit,
                    current_debt,
                ) = row[1:]
                total_deposited += amount

                row_data = [
                    customer_name,
                    identite,
                    deposit_date.strftime("%Y-%m-%d"),
                    amount,
                    released_deposit,
                    current_debt,
                ]
                for col_idx, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_idx, col_idx, item)

                # Add action buttons
                self.add_action_buttons(row_idx, identite)

            self.total_amount_label.setText(f"Total Déposé: {total_deposited}")

        except SQLAlchemyError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement: {str(e)}")
        finally:
            session.close()

    def add_action_buttons(self, row, identite):
        layout = QVBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)  # Remove margins to fit the cell properly
        layout.setAlignment(Qt.AlignCenter)  # Align the button to the center

        # Withdraw button
        withdraw_button = QPushButton("Retirer")
        withdraw_button.setFixedSize(65, 30)
        withdraw_button.clicked.connect(lambda: self.withdraw(identite))
        layout.addWidget(withdraw_button)

        button_widget = QWidget()
        button_widget.setLayout(layout)
        self.table.setCellWidget(row, 6, button_widget)

    def add_deposit(self):
        dialog = AddDepositDialog()
        if dialog.exec_():

            self.load_deposit_data()  # Reload data after adding
            # self.save_ids_to_file()  # Save IDs to file

    def withdraw(self, identite):

        dialog = WithdrawDepositDialog(identite)
        if dialog.exec_():
            self.load_deposit_data()
