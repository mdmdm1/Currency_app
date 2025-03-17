from datetime import datetime
import json
from PyQt5.QtWidgets import QLineEdit, QLabel, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QDate
import requests
from database.models import Customer, Debt
from dialogs.base_dialog import BaseDialog
from database.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError

from utils.translation_manager import TranslationManager
from utils.audit_logger import log_audit_entry
from config import API_BASE_URL


class PayDebtDialog(BaseDialog):
    def __init__(self, parent, debt_id):
        super().__init__(TranslationManager.tr("Payer la dette"), parent)
        self.debt_id = debt_id
        self.user_id = parent.user_id
        self.api_base_url = API_BASE_URL
        self.setGeometry(200, 200, 500, 400)
        self.populate_form_fields()

    def create_form_fields(self):
        self.current_debt_label = QLabel("0.00")
        self.pay_amount_input = QLineEdit()

        fields = [
            (TranslationManager.tr("Dette actuelle:"), self.current_debt_label),
            (TranslationManager.tr("Montant à payer:"), self.pay_amount_input),
        ]

        for label, widget in fields:
            self.create_input_row(label, widget)

    def populate_form_fields(self):

        try:
            response = requests.get(f"{self.api_base_url}/debts/{self.debt_id}")

            if response.status_code == 404:
                QMessageBox.critical(
                    self,
                    TranslationManager.tr("Erreur"),
                    TranslationManager.tr("Dette non trouvée."),
                )
                self.reject()
                return
            response.raise_for_status()
            debt = response.json()

            # Display the current debt amount
            self.current_debt_label.setText(
                self.format_french_number(debt["current_debt"])
            )

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(
                self,
                TranslationManager.tr("Erreur"),
                TranslationManager.tr("Erreur lors du chargement des données:")
                + f" {str(e)}",
            )
            self.reject()

    def on_submit(self):
        pay_amount_str = self.pay_amount_input.text().strip()

        is_valid_amount, pay_amount = self.validate_amount(pay_amount_str)

        if not is_valid_amount:
            return

        try:
            response = requests.get(f"{self.api_base_url}/debts/{self.debt_id}")
            response.raise_for_status()
            debt = response.json()

            if response.status_code == 404:
                QMessageBox.critical(
                    self,
                    TranslationManager.tr("Erreur"),
                    TranslationManager.tr("Dette non trouvée."),
                )
                return

            response = requests.get(
                f"{self.api_base_url}/customers/{debt["customer_id"]}"
            )
            if response.status_code == 404:
                customer = None
            else:
                response.raise_for_status()
                customer = response.json()

            if pay_amount > debt["current_debt"]:
                QMessageBox.warning(
                    self,
                    TranslationManager.tr("Erreur"),
                    TranslationManager.tr(
                        "Le montant payé ne peut pas dépasser la dette actuelle."
                    ),
                )
                return

            old_data = {
                "name": customer["name"],
                "Dette payee": debt["paid_debt"],
                "Dette actuelle": debt["amount"],
            }
            # Update debt fields
            """debt.paid_debt = (debt.paid_debt or 0) + pay_amount
            debt.current_debt = debt.amount - debt.paid_debt
            debt.updated_at = datetime.now()
            """
            updated_data = {
                "paid_debt": (debt["paid_debt"] or 0) + pay_amount,
                "current_debt": debt["current_debt"] - pay_amount,
                "updated_at": datetime.now().date().isoformat(),
            }

            updated_debt_response = requests.put(
                f"{self.api_base_url}/debts/{debt["id"]}", json=updated_data
            )

            updated_debt_response.raise_for_status()
            updated_debt = updated_debt_response.json()
            audit_response = requests.post(
                f"{self.api_base_url}/audit_logs/",
                json={
                    "table_name": TranslationManager.tr("Dette"),
                    "operation": TranslationManager.tr("PAYER"),
                    "record_id": updated_debt["id"],
                    "user_id": self.user_id,
                    "changes": json.dumps(
                        {
                            "old": old_data,
                            "new": {
                                TranslationManager.tr("nom"): customer["name"],
                                TranslationManager.tr("Dette payee"): updated_data[
                                    "paid_debt"
                                ],
                                TranslationManager.tr("dette actuelle"): updated_data[
                                    "current_debt"
                                ],
                            },
                        }
                    ),
                },
            )
            audit_response.raise_for_status()

            if updated_data["current_debt"] == 0:
                # Proceed with deletion
                delete_response = requests.delete(
                    f"{self.api_base_url}/debts/{self.debt_id}"
                )
                delete_response.raise_for_status()
            QMessageBox.information(
                self,
                TranslationManager.tr("Succès"),
                TranslationManager.tr("La dette a été mise à jour avec succès:")
                + "\n"
                + TranslationManager.tr("Dette actuelle:")
                + f" {debt["current_debt"]:.2f}\n"
                + TranslationManager.tr("Montant payé:")
                + f" {debt["paid_debt"]:.2f}",
            )
            self.accept()

        except requests.exceptions.RequestException as e:

            QMessageBox.critical(
                self,
                TranslationManager.tr("Erreur"),
                TranslationManager.tr("Erreur:") + f" {str(e)}",
            )

    @staticmethod
    def validate_amount(amount_str):
        try:
            amount = float(amount_str)
            if amount < 0:
                raise ValueError
            return True, amount
        except ValueError:
            QMessageBox.warning(
                None,
                TranslationManager.tr("Erreur"),
                TranslationManager.tr("Veuillez entrer un montant valide."),
            )
            return False, 0.0

    def retranslate_ui(self):

        fields = [
            (TranslationManager.tr("Dette actuelle:"), self.current_debt_label),
            (TranslationManager.tr("Montant à payer:"), self.pay_amount_input),
        ]

        for label, widget in fields:
            self.create_input_row(label, widget)
