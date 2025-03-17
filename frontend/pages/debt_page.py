import json
from PyQt5.QtWidgets import (
    QTableWidgetItem,
    QPushButton,
    QSizePolicy,
    QHeaderView,
    QMessageBox,
)
from PyQt5.QtCore import Qt
import requests
from dialogs.add_debt_dialog import AddDebtDialog
from dialogs.pay_debt_dialog import PayDebtDialog
from pages.base_page import BasePage
from utils.translation_manager import TranslationManager
from config import API_BASE_URL


class DebtPage(BasePage):
    def __init__(self, parent):
        super().__init__(parent, title=TranslationManager.tr("Gestion des Dettes"))
        self.user_id = parent.user_id
        self.api_base_url = API_BASE_URL
        self.init_ui()

    def init_ui(self):
        # Set up table headers
        self.setup_table_headers(
            [
                TranslationManager.tr("Nom"),
                TranslationManager.tr("NNI"),
                TranslationManager.tr("Date de création"),
                TranslationManager.tr("Montant total"),
                TranslationManager.tr("Montant payé"),
                TranslationManager.tr("Dette actuelle"),
                TranslationManager.tr("Actions"),
            ]
        )

        # Set fixed width for actions column
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 170)

        # Add debt button
        self.add_button = QPushButton(TranslationManager.tr("Ajouter une dette"))
        self.add_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.add_button.clicked.connect(self.add_debt)
        self.layout.addWidget(self.add_button, alignment=Qt.AlignBottom | Qt.AlignRight)

        self.load_debt_data()

    def load_debt_data(self):
        try:
            response = requests.get(f"{self.api_base_url}/debts")
            response.raise_for_status()  # Raise an error for bad status codes
            debts = response.json()

            self.table.setRowCount(len(debts))
            total_debt = 0

            for row_idx, debt in enumerate(debts):
                customer_response = requests.get(
                    f"{self.api_base_url}/customers/{debt["customer_id"]}"
                )
                customer_response.raise_for_status()
                customer = customer_response.json()
                customer_name = customer["name"]
                identite = customer["identite"]
                debt_id = debt["id"]
                created_at = debt["created_at"]
                total_amount = debt["amount"]
                paid_debt = debt["paid_debt"]
                current_debt = debt["current_debt"]

                total_debt += current_debt

                row_data = [
                    customer_name,
                    identite,
                    created_at,
                    self.format_french_number(total_amount),
                    self.format_french_number(paid_debt),
                    self.format_french_number(current_debt),
                ]

                for col_idx, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)

                    # Disable editing for the item
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                    self.table.setItem(row_idx, col_idx, item)
                # Configure action buttons for this row
                buttons_config = [
                    {
                        "text": TranslationManager.tr("Payer"),
                        "color": "#ffc107",
                        "callback": self.pay_debt,
                        "width": 70,
                    },
                    {
                        "text": TranslationManager.tr("Supprimer"),
                        "color": "#dc3545",
                        "callback": self.delete_debt,
                        "width": 76,
                    },
                ]
                self.add_action_buttons(row_idx, debt_id, buttons_config)

            self.total_prefix = TranslationManager.tr("Total Dette")
            self.update_total_label(total_debt, TranslationManager.tr("Total Dette"))

        except requests.exceptions.RequestException as e:
            self.show_error_message(
                TranslationManager.tr("Erreur"),
                f"{TranslationManager.tr('Erreur lors du chargement')}: {str(e)}",
            )

    def add_debt(self):
        dialog = AddDebtDialog(self)
        if dialog.exec_():
            self.load_debt_data()

    def pay_debt(self, debt_id, row):
        dialog = PayDebtDialog(self, debt_id=debt_id)
        if dialog.exec_():
            self.load_debt_data()

    def delete_debt(self, debt_id, row):
        confirmation = QMessageBox(self)
        confirmation.setIcon(QMessageBox.Question)
        confirmation.setWindowTitle(TranslationManager.tr("Confirmer la suppression"))
        confirmation.setText(
            TranslationManager.tr("Êtes-vous sûr de vouloir supprimer cette dette ?")
        )

        # Add buttons with translated text
        yes_button = confirmation.addButton(
            TranslationManager.tr("Oui"), QMessageBox.YesRole
        )
        no_button = confirmation.addButton(
            TranslationManager.tr("Non"), QMessageBox.NoRole
        )

        confirmation.setDefaultButton(no_button)
        confirmation.exec_()

        if confirmation.clickedButton() == yes_button:
            try:

                debt_response = requests.get(f"{self.api_base_url}/debts/{debt_id}")
                debt_response.raise_for_status()
                debt = debt_response.json()

                customer_response = requests.get(
                    f"{self.api_base_url}/customers/{debt["customer_id"]}"
                )
                customer_response.raise_for_status()
                customer = customer_response.json()
                # Proceed with deletion
                response = requests.delete(f"{self.api_base_url}/debts/{debt_id}")
                response.raise_for_status()

                audit_response = requests.post(
                    f"{self.api_base_url}/audit_logs/",
                    json={
                        "table_name": TranslationManager.tr("Dette"),
                        "operation": TranslationManager.tr("SUPPRESSION"),
                        "record_id": debt_id,
                        "user_id": self.user_id,
                        "changes": json.dumps(
                            {
                                TranslationManager.tr("name"): customer["name"],
                                TranslationManager.tr("montant"): debt["amount"],
                                TranslationManager.tr("date du dette"): debt[
                                    "debt_date"
                                ],
                                TranslationManager.tr("dette actuelle"): debt[
                                    "current_debt"
                                ],
                                TranslationManager.tr("dette payée"): debt["paid_debt"],
                                TranslationManager.tr("date de création"): debt[
                                    "created_at"
                                ],
                            }
                        ),
                    },
                )
                audit_response.raise_for_status()

                self.load_debt_data()  # Refresh table after deletion

            except requests.exceptions.RequestException as e:
                self.show_error_message(
                    TranslationManager.tr("Erreur"),
                    f"{TranslationManager.tr('Erreur lors de la suppression')}: {str(e)}",
                )

    def retranslate_ui(self):
        # Update the window title
        self.setWindowTitle(TranslationManager.tr("Gestion des Dettes"))

        # Update table headers
        self.setup_table_headers(
            [
                TranslationManager.tr("Nom"),
                TranslationManager.tr("NNI"),
                TranslationManager.tr("Date de création"),
                TranslationManager.tr("Montant total"),
                TranslationManager.tr("Montant payé"),
                TranslationManager.tr("Dette actuelle"),
                TranslationManager.tr("Actions"),
            ]
        )

        # Update the Add Debt button text
        for widget in self.layout.children():
            if isinstance(widget, QPushButton) and widget.text() != "":
                widget.setText(TranslationManager.tr("buttons.Update Debt"))

        self.add_button.setText(TranslationManager.tr("Ajouter une dette"))

        # Update the AddDebtDialog if it's open
        # if hasattr(self, "add_debt_dialog"):
        #    self.add_debt_dialog.retranslate_ui()

        self.load_debt_data()
