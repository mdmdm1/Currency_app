from PyQt5.QtWidgets import (
    QTableWidgetItem,
    QSizePolicy,
    QHeaderView,
    QPushButton,
)
from PyQt5.QtCore import Qt
from sqlalchemy.exc import SQLAlchemyError
from dialogs.add_deposit_dialog import AddDepositDialog
from database.models import Customer, Deposit
from database.database import SessionLocal
from dialogs.withdraw_deposit_dialog import WithdrawDepositDialog
from pages.base_page import BasePage


class DepositPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent, title="Gestion des dépôts")
        self.init_ui()

    def init_ui(self):
        # Set up table headers
        self.setup_table_headers(
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

        # Set fixed width for actions column
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 170)

        # Add deposit button
        add_button = QPushButton("Ajouter un dépôt")
        add_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        add_button.clicked.connect(self.add_deposit)
        self.layout.addWidget(add_button, alignment=Qt.AlignBottom | Qt.AlignRight)

        self.load_deposit_data()

    def load_deposit_data(self):
        session = SessionLocal()
        try:
            deposits = (
                session.query(Deposit)
                .join(Customer, Deposit.customer_id == Customer.id)
                .add_columns(
                    Customer.id,
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
                    customer_id,
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
                    self.format_french_number(amount),
                    self.format_french_number(released_deposit),
                    self.format_french_number(current_debt),
                ]

                for col_idx, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_idx, col_idx, item)

                # Configure buttons for this row
                buttons_config = [
                    {
                        "text": "Retirer",
                        "color": "#dc3545",
                        "callback": self.withdraw,
                        "width": 70,
                    },
                    {
                        "text": "Ajouter",
                        "color": "#28a745",
                        "callback": self.update_deposit,
                        "width": 70,
                    },
                ]
                self.add_action_buttons(row_idx, customer_id, buttons_config)

            self.update_total_label(total_deposited, "Total Déposé")

        except SQLAlchemyError as e:
            self.show_error_message("Erreur", f"Erreur lors du chargement: {str(e)}")
        finally:
            session.close()

    def add_deposit(self):
        dialog = AddDepositDialog()
        if dialog.exec_():
            self.load_deposit_data()

    def update_deposit(self, customer_id):
        dialog = AddDepositDialog(customer_id=customer_id)
        if dialog.exec_():
            self.load_deposit_data()

    def withdraw(self, identite):
        dialog = WithdrawDepositDialog(identite)
        if dialog.exec_():
            self.load_deposit_data()
