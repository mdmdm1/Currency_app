import json
from PyQt5.QtWidgets import (
    QLineEdit,
    QDateEdit,
    QMessageBox,
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QDoubleValidator
import requests
from dialogs.base_dialog import BaseDialog


from utils.translation_manager import TranslationManager
from config import API_BASE_URL


class WithdrawDepositDialog(BaseDialog):
    def __init__(self, parent, customer_id):
        super().__init__(TranslationManager.tr("Retrait"), parent)
        self.setGeometry(250, 250, 300, 400)
        self.user_id = parent.user_id
        self.customer_id = customer_id
        self.api_base_url = API_BASE_URL

    def create_form_fields(self):
        # Input for withdrawal amount
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText(TranslationManager.tr("Montant à retirer"))
        self.amount_input.setValidator(
            QDoubleValidator(0, 1e9, 2)
        )  # Allow only valid numeric input
        self.create_input_row(TranslationManager.tr("Montant:"), self.amount_input)

        # Input for withdrawal date
        self.withdraw_date_input = QDateEdit(QDate.currentDate())
        self.withdraw_date_input.setCalendarPopup(True)
        self.create_input_row(
            TranslationManager.tr("Date de retrait:"), self.withdraw_date_input
        )

    def on_submit(self):
        # Validate withdrawal amount
        amount_valid, amount = self.validate_amount(self.amount_input.text())
        if not amount_valid:
            return

        # Validate if an amount is specified
        if amount <= 0:
            self.show_error(
                TranslationManager.tr("Le montant doit être supérieur à zéro.")
            )
            return

        try:
            deposit_response = requests.get(
                f"{self.api_base_url}/deposits/by-customer-id/{self.customer_id}"
            )
            deposit_response.raise_for_status()
            deposit = deposit_response.json()
            if deposit_response.status_code == 404:
                QMessageBox.critical(
                    self,
                    TranslationManager.tr("Erreur"),
                    TranslationManager.tr("Depot non trouvée."),
                )
                return

            customer_response = requests.get(
                f"{self.api_base_url}/customers/{deposit["customer_id"]}"
            )
            customer_response.raise_for_status()
            customer = customer_response.json()

            # Check if the customer has sufficient balance
            if deposit["current_debt"] < amount:
                self.show_error(
                    TranslationManager.tr("Solde insuffisant pour le retrait.")
                )
                return

            old_data = {
                TranslationManager.tr("Nom"): customer["name"],
                TranslationManager.tr("Depot libere"): deposit["released_deposit"],
                TranslationManager.tr("Depot actuelle"): deposit["current_debt"],
            }

            updated_data = {
                "current_debt": deposit["current_debt"] - amount,
                "released_deposit": deposit["released_deposit"] + amount,
            }

            """            
            deposit.current_debt -= amount
            deposit.released_deposit += amount
            """
            updated_deposit_response = requests.put(
                f"{self.api_base_url}/deposits/{deposit["id"]}", json=updated_data
            )

            updated_deposit_response.raise_for_status()
            updated_deposit = updated_deposit_response.json()
            audit_response = requests.post(
                f"{self.api_base_url}/audit_logs/",
                json={
                    "table_name": TranslationManager.tr("Depot"),
                    "operation": TranslationManager.tr("RETRAIT"),
                    "record_id": updated_deposit["id"],
                    "user_id": self.user_id,
                    "changes": json.dumps(
                        {
                            "old": old_data,
                            "new": {
                                TranslationManager.tr("nom"): customer["name"],
                                TranslationManager.tr("depot libere"): updated_data[
                                    "released_deposit"
                                ],
                                TranslationManager.tr("depot actuelle"): updated_data[
                                    "current_debt"
                                ],
                            },
                        }
                    ),
                },
            )
            audit_response.raise_for_status()

            # if current_debt is 0, delete the deposit
            if deposit["current_debt"] == 0:
                delete_response = requests.delete(
                    f"{self.api_base_url}/deposits/{deposit["id"]}"
                )
                delete_response.raise_for_status()

            # Inform the user of success
            QMessageBox.information(
                self,
                TranslationManager.tr("Succès"),
                TranslationManager.tr("Retrait effectué avec succès."),
            )

            self.accept()

        except requests.exceptions.RequestException as e:

            self.show_error(
                f"{TranslationManager.tr('Erreur lors de l\'accès à la base de données:')} {str(e)}"
            )
