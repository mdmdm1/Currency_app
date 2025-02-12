from PyQt5.QtWidgets import (
    QTableWidgetItem,
    QSizePolicy,
    QHeaderView,
    QPushButton,
)
from PyQt5.QtCore import Qt
import requests
from sqlalchemy.exc import SQLAlchemyError
from dialogs.add_deposit_dialog import AddDepositDialog
from database.models import Customer, Deposit
from database.database import SessionLocal
from dialogs.withdraw_deposit_dialog import WithdrawDepositDialog
from pages.base_page import BasePage
from utils.translation_manager import TranslationManager


class DepositPage(BasePage):

    def __init__(self, parent):
        super().__init__(parent, title=TranslationManager.tr("Gestion des dépôts"))
        self.user_id = parent.user_id
        self.init_ui()

    def init_ui(self):
        # Set up table headers
        self.setup_table_headers(
            [
                TranslationManager.tr("Nom"),
                TranslationManager.tr("NNI"),
                TranslationManager.tr("Date de dépôt"),
                TranslationManager.tr("Montant initial"),
                TranslationManager.tr("Dépôt libéré"),
                TranslationManager.tr("Dette actuelle"),
                TranslationManager.tr("Actions"),
            ]
        )

        # Set fixed width for actions column
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 170)

        # Add deposit button
        self.add_button = QPushButton(TranslationManager.tr("Ajouter un dépôt"))
        self.add_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.add_button.clicked.connect(self.add_deposit)
        self.layout.addWidget(self.add_button, alignment=Qt.AlignBottom | Qt.AlignRight)

        self.load_deposit_data()

    def load_deposit_data(self):
        try:

            response = requests.get("http://127.0.0.1:8000/deposits")
            response.raise_for_status()  # Raise an error for bad status codes
            deposits = response.json()

            self.table.setRowCount(len(deposits))
            total_deposited = 0

            for row_idx, deposit in enumerate(deposits):
                customer_response = requests.get(
                    f"http://127.0.0.1:8000/customers/{deposit["customer_id"]}"
                )
                customer_response.raise_for_status()
                customer = customer_response.json()
                customer_name = customer["name"]
                identite = customer["identite"]
                deposit_date = deposit["deposit_date"]
                amount = deposit["amount"]
                released_deposit = deposit["released_deposit"]
                current_debt = deposit["current_debt"]

                total_deposited += current_debt

                row_data = [
                    customer_name,
                    identite,
                    deposit_date,
                    self.format_french_number(amount),
                    self.format_french_number(released_deposit),
                    self.format_french_number(current_debt),
                ]

                for col_idx, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)

                    # Disable editing for the item
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                    self.table.setItem(row_idx, col_idx, item)

                # Configure buttons for this row
                buttons_config = [
                    {
                        "text": TranslationManager.tr("Retirer"),
                        "color": "#dc3545",
                        "callback": self.withdraw,
                        "width": 70,
                    },
                    {
                        "text": TranslationManager.tr("Ajouter"),
                        "color": "#28a745",
                        "callback": self.update_deposit,
                        "width": 70,
                    },
                ]
                self.add_action_buttons(row_idx, deposit["customer_id"], buttons_config)

            self.total_prefix = TranslationManager.tr("Total Déposé")
            self.update_total_label(total_deposited, self.total_prefix)

        except requests.exceptions.RequestException as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                f"{TranslationManager.tr('Erreur lors du chargement')}: {str(e)}",
            )

    def add_deposit(self):
        dialog = AddDepositDialog(self)
        if dialog.exec_():
            self.load_deposit_data()

    def update_deposit(self, customer_id, row):
        dialog = AddDepositDialog(self, customer_id=customer_id)
        if dialog.exec_():
            self.load_deposit_data()

    def withdraw(self, identite, row):
        dialog = WithdrawDepositDialog(self, identite)
        if dialog.exec_():
            self.load_deposit_data()

    def retranslate_ui(self):

        # Update page title
        self.setWindowTitle(TranslationManager.tr("Gestion des dépôts"))

        # Update table headers
        self.setup_table_headers(
            [
                TranslationManager.tr("Nom"),
                TranslationManager.tr("NNI"),
                TranslationManager.tr("Date de dépôt"),
                TranslationManager.tr("Montant initial"),
                TranslationManager.tr("Dépôt libéré"),
                TranslationManager.tr("Dette actuelle"),
                TranslationManager.tr("Actions"),
            ]
        )

        self.add_button.setText(TranslationManager.tr("Ajouter un dépôt"))

        self.total_prefix = TranslationManager.tr("Total Déposé")
        self.load_deposit_data()
